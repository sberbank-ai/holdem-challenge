import subprocess
import json

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
        game_info['uuid'] = self.uuid
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
