import datetime

from pypokerengine.players import RandomPlayer, ExternalExecutablePlayer
from pypokerengine.api.game import setup_config, start_poker


if __name__ == '__main__':
    start_time = datetime.datetime.now()

    # choose here your strategy
    player = ExternalExecutablePlayer('python examples/python-bot/bot.py')

    config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15,
                          summary_file='example_game_replay.json')
    config.register_player(name='Participant', algorithm=player)
    for i in range(8):
        config.register_player(name='Random {}'.format(i), algorithm=RandomPlayer())

    num_games = 3
    game_scores = []

    for game_no in range(num_games):
        game_result = start_poker(config, verbose=0)
        participant_result = game_result['players'][0]
        game_scores.append(participant_result['stack'])
        print('Game #{}: stack={}, state={}'.format(
            game_no,
            participant_result['stack'],
            participant_result['state'],
        ))

    print('Elapsed time: {}'.format(datetime.datetime.now() - start_time))
    print('Score: {}'.format(sum(game_scores) / num_games))
