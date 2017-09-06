import uuid
import os
import subprocess
import fcntl
import time
import json

import docker
import docker.errors

from pypokerengine.players import ExternalExecutablePlayer


class DockerContainerPlayer(ExternalExecutablePlayer):
    WAIT_ANSWER_TICK = 0.0001
    METADATA_FILE = 'metadata.json'

    def __init__(self, source_dir, image=None, entry_point=None, time_limit_action=0, time_limit_bank=60 * 5,
                 docker_client=None, **kwargs):

        self.docker_client = docker_client if docker_client is not None else docker.DockerClient()
        self.source_dir = os.path.abspath(source_dir)
        self.time_limit_action = time_limit_action
        self.time_limit_bank = time_limit_bank

        self.image = image
        self.entry_point = entry_point
        if image is None or entry_point is None:
            self._init_from_metadata()

        self.time_available_bank = time_limit_bank
        self.failed = False

        self.container = None
        self.attach_process = None

        self._run_container(kwargs)
        self._attach_container()

    def _init_from_metadata(self):
        metadata_file = os.path.join(self.source_dir, DockerContainerPlayer.METADATA_FILE)
        if not os.path.exists(metadata_file):
            raise RuntimeError('Neither metadata.json found nor image and entry_point specified')
        with open(metadata_file) as fin:
            metadata = json.load(fin)
        self.image = metadata['image']
        self.entry_point = metadata['entry_point']

    def _run_container(self, params):
        self.container_name = 'bot_{}'.format(uuid.uuid1().hex)

        self.docker_run_params = {
            'network': 'none',
            'network_disabled': True,
            'mem_limit': '2g',
            'cpu_period': 50000,
            'cpu_quota': 50000,
        }
        self.docker_run_params.update(params)

        self.container = self.docker_client.containers.run(
            self.image,
            entrypoint=self.entry_point,
            working_dir='/workspace',
            volumes={
                self.source_dir: {'bind': '/workspace', 'mode': 'rw'},
            },
            name=self.container_name,
            detach=True,
            stdin_open=True,
            auto_remove=True,
            **self.docker_run_params
        )

        # wait for container to get running
        while self.container.status in ('created',):
            self._update_container()

    def _attach_container(self):
        self.attach_process = subprocess.Popen(
            ['docker', 'attach', self.container.id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.executable_input = self.attach_process.stdin
        self.executable_output = self.attach_process.stdout

        attach_stdout_fd = self.attach_process.stdout.fileno()
        attach_stdout_flags = fcntl.fcntl(attach_stdout_fd, fcntl.F_GETFL)
        fcntl.fcntl(attach_stdout_fd, fcntl.F_SETFL, attach_stdout_flags | os.O_NONBLOCK)

    def _update_container(self):
        self.container = self.docker_client.containers.get(self.container.id)

    def stop(self):
        if self.container is not None:
            try:
                self.container.remove(force=True)
            except docker.errors.NotFound:
                pass
            except docker.errors.APIError:
                pass
        if self.attach_process is not None:
            self.attach_process.kill()

    def __del__(self):
        self.stop()

    def _set_fail(self, reason, message=None):
        self.failed = True
        self.fail_reason = reason
        self.fail_message = message

        self.fail_game = None
        self.fail_round = None

        self.stop()

    def _construct_answer(self, action='fold', amount=0, time_elapsed=0, **kwargs):
        info = {
            'failed': self.failed,
            'time_elapsed': time_elapsed,
            'time_bank': self.time_available_bank,
        }
        info.update(kwargs)
        return action, amount, info

    def _read_answer(self, data):
        if self.failed:
            return self._construct_answer()

        max_think_time = self.time_available_bank + self.time_limit_action
        think_time = 0.0
        new_think_time = 0.0
        start_time = time.time()

        attach_exit_code = None
        answer_line = self.executable_output.readline()

        while (not answer_line) and (new_think_time <= max_think_time) and (attach_exit_code is None):
            think_time = new_think_time
            time.sleep(DockerContainerPlayer.WAIT_ANSWER_TICK)
            attach_exit_code = self.attach_process.poll()
            answer_line = self.executable_output.readline()
            new_think_time = time.time() - start_time
        think_time = new_think_time

        spent_time_bank = max(0, think_time - self.time_limit_action)
        self.time_available_bank -= spent_time_bank

        if answer_line:
            try:
                answer_line = answer_line.decode('utf8').rstrip()
                answer_parts = answer_line.split('\t')
            except UnicodeDecodeError:
                self._set_fail('crash', 'bad characters in answer line')
                return self._construct_answer(time_elapsed=think_time)

            if len(answer_parts) != 2:
                self._set_fail('crash', 'invalid action format')
                return self._construct_answer(time_elapsed=think_time, line=answer_line)

            action, amount = answer_parts

            try:
                amount = int(amount)
            except ValueError:
                self._set_fail('crash', 'invalid action format: amount is not int')
                return self._construct_answer(time_elapsed=think_time)

            return self._construct_answer(action, amount, time_elapsed=think_time, line=answer_line, valid_actions=data['valid_actions'])

        elif attach_exit_code is not None:
            self._set_fail('crash', 'process exited during answering with code {}'.format(attach_exit_code))
            return self._construct_answer(time_elapsed=think_time)

        elif think_time > max_think_time:
            self._set_fail('time_limit_exceeded')
            return self._construct_answer(time_elapsed=think_time)

    def _write_event(self, event_type, data):
        if self.failed:
            return  # do not write to failed bots

        event_line = '{event_type}\t{data}\n'.format(
            event_type=event_type,
            data=json.dumps(data),
        )
        try:
            self.executable_input.write(event_line.encode('utf8'))
            self.executable_input.flush()
        except BrokenPipeError:
            attach_exit_code = self.attach_process.poll()
            if attach_exit_code is not None:
                self._set_fail('crash', 'process suddenly exited with code {}'.format(attach_exit_code))
            else:
                self._set_fail('crash', 'process suddenly closed stdin')

    def declare_action(self, valid_actions, hole_card, round_state):
        if self.failed:
            return self._construct_answer()

        bot_stack = None
        for seat in round_state['seats']:
            if seat['uuid'] == self.uuid:
                bot_stack = seat['stack']
        bot_state = {
            'uuid': self.uuid,
            'time_limit_action': self.time_limit_action,
            'time_limit_bank': self.time_available_bank,
            'stack': bot_stack,
        }

        data = {
            'valid_actions': valid_actions,
            'hole_card': hole_card,
            'round_state': round_state,
            'bot_state': bot_state,
        }
        self._write_event('declare_action', data)

        action, amount, info = self._read_answer(data)

        # check action validity
        valid_amounts = {
            record['action']: record['amount']
            for record in valid_actions
        }
        if action not in valid_amounts:
            self._set_fail('invalid_action', 'unknown action "{}"'.format(action))
            return self._construct_answer(time_elapsed=info['time_elapsed'])
        action_valid_amount = valid_amounts[action]
        if isinstance(action_valid_amount, dict):
            if amount < action_valid_amount['min'] or amount > action_valid_amount['max']:
                self._set_fail('invalid_action', 'invalid amount for action {}, allowed {}..{}, requested {}'.format(
                    action, action_valid_amount['min'], action_valid_amount['max'], amount,
                ))
                return self._construct_answer(time_elapsed=info['time_elapsed'])
        else:
            if amount != action_valid_amount:
                self._set_fail('invalid_action', 'invalid amount for action {}, allowed {}, requested {}'.format(
                    action, action_valid_amount, amount,
                ))
                return self._construct_answer(time_elapsed=info['time_elapsed'])

        return action, amount, info

