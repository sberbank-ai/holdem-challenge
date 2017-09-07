import sys
import json

from pypokerengine.players import BasePokerPlayer


class MyPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


if __name__ == '__main__':

    player = MyPlayer()

    while True:
        line = sys.stdin.readline().rstrip()
        if not line:
           break
        event_type, data = line.split('\t', 1)
        data = json.loads(data)

        if event_type == 'declare_action':
            action, amount = player.declare_action(
                data['valid_actions'], data['hole_card'], data['round_state'], data.get('bot_state'))
            sys.stdout.write('{}\t{}\n'.format(action, amount))
            sys.stdout.flush()
        elif event_type == 'game_start':
            player.set_uuid(data.get('uuid'))
            player.receive_game_start_message(data)
        elif event_type == 'round_start':
            player.receive_round_start_message(data['round_count'], data['hole_card'], data['seats'])
        elif event_type == 'street_start':
            player.receive_street_start_message(data['street'], data['round_state'])
        elif event_type == 'game_update':
            player.receive_game_update_message(data['new_action'], data['round_state'])
        elif event_type == 'round_result':
            player.receive_round_result_message(data['winners'], data['hand_info'], data['round_state'])
        else:
            raise RuntimeError('Bad event type "{}"'.format(event_type))

