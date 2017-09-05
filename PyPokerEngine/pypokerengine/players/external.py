import subprocess
import json
import uuid
import shlex
import datetime
import _thread
from threading import Timer

from pypokerengine.players import BasePokerPlayer


class ExternalExecutablePlayer(BasePokerPlayer):
    def __init__(self, cmd):
        self.process = subprocess.Popen(
            cmd,
            shell=not isinstance(cmd, list),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.executable_input = self.process.stdin
        self.executable_output = self.process.stdout

    def _read_answer(self):
        answer_line = self.executable_output.readline().decode('utf8')
        answer_parts = answer_line.rstrip().split('\t')
        return answer_parts

    def _write_event(self, event_type, data):
        event_line = '{event_type}\t{data}\n'.format(
            event_type=event_type,
            data=json.dumps(data),
        )
        self.executable_input.write(event_line.encode('utf8'))
        self.executable_input.flush()

    def declare_action(self, valid_actions, hole_card, round_state):
        data = {
            'valid_actions': valid_actions,
            'hole_card': hole_card,
            'round_state': round_state,
        }
        self._write_event('declare_action', data)

        answer_parts = self._read_answer()
        if len(answer_parts) != 2:
            raise RuntimeError('Bad executable declare_action answer')

        action, amount = answer_parts
        amount = int(amount)

        return action, amount

    def receive_game_start_message(self, game_info):
        self._write_event('game_start', game_info)

    def receive_round_start_message(self, round_count, hole_card, seats):
        data = {
            'round_count': round_count,
            'hole_card': hole_card,
            'seats': seats,
        }
        self._write_event('round_start', data)

    def receive_street_start_message(self, street, round_state):
        data = {
            'street': street,
            'round_state': round_state,
        }
        self._write_event('street_start', data)

    def receive_game_update_message(self, new_action, round_state):
        data = {
            'new_action': new_action,
            'round_state': round_state,
        }
        self._write_event('game_update', data)

    def receive_round_result_message(self, winners, hand_info, round_state):
        data = {
            'winners': winners,
            'hand_info': hand_info,
            'round_state': round_state,
        }
        self._write_event('round_result', data)


class DockerContainerPlayer(ExternalExecutablePlayer):
    def __init__(self, source_dir, image, entry_point, time_limit):
        bot_id = uuid.uuid1().hex
        self.container_name = 'bot_{}'.format(bot_id)
        cmd = [
                  'docker',
                  'run',
                  '--rm',
                  '-i',
                  '-m', '4g',
                  '--cpus', '2',
                  '--network', 'none',
                  '--name', self.container_name,
                  '-v', '{}:/workspace'.format(os.path.abspath(source_dir)),
                  '-w', '/workspace',
                  image,
              ] + shlex.split(entry_point)

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        self.executable_input = self.process.stdin
        self.executable_output = self.process.stdout

        self.start_time = datetime.datetime.now()
        self.time_limit = time_limit

        self.failed = False
        self.failed_message = None

    def kill(self):
        try:
            subprocess.run([
                'docker',
                'kill',
                self.container_name,
            ], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        except Exception as e:
            pass

    def declare_action(self, valid_actions, hole_card, round_state):
        data = {
            'valid_actions': valid_actions,
            'hole_card': hole_card,
            'round_state': round_state,
        }
        self._write_event('declare_action', data)

        answer_parts = self._read_answer()
        if len(answer_parts) != 2:
            self.failed = True
            self.failed_message = 'crashed'
            raise RuntimeError()

        action, amount = answer_parts

        try:
            amount = int(amount)
        except ValueError:
            self.failed = True
            self.failed_message = 'crashed'
            raise RuntimeError()

        return action, amount

    def _read_answer(self):
        answer_line = None

        timeout = max(0, (self.time_limit - (datetime.datetime.now() - self.start_time)).total_seconds())
        try:
            timeout_timer = Timer(timeout, _thread.interrupt_main)
            timeout_timer.start()
            answer_line = self.executable_output.readline()
        except KeyboardInterrupt:
            self.failed = True
            self.failed_message = 'time limit exceeded'
            self.kill()
            raise RuntimeError()
        finally:
            timeout_timer.cancel()

        answer_parts = answer_line.decode('utf8').rstrip().split('\t')
        return answer_parts

    def _write_event(self, event_type, data):
        event_line = '{event_type}\t{data}\n'.format(
            event_type=event_type,
            data=json.dumps(data),
        )
        try:
            self.executable_input.write(event_line.encode('utf8'))
            self.executable_input.flush()
        except BrokenPipeError:
            self.failed = True
            self.failed_message = 'crashed'
            raise RuntimeError()
