import datetime

from pypokerengine.players import RandomPlayer
from pypokerengine.players.docker_container import DockerContainerPlayer
from pypokerengine.api.game import setup_config, start_poker


if __name__ == '__main__':
    start_time = datetime.datetime.now()

    # choose here your strategy
    player = DockerContainerPlayer(
        source_dir='examples/python-bot',
        #image='sberbank/python',
        #entry_point='python bot.py',
        time_limit_action=0.2,
        time_limit_bank=10,
        cpu_limit=2,
        mem_limit='1g',
    )

    config = setup_config(max_round=50, initial_stack=1500, small_blind_amount=15)

    config.register_player(name='Participant', algorithm=player)
    for i in range(8):
        config.register_player(name='Random {}'.format(i), algorithm=RandomPlayer())

    num_games = 3
    game_scores = []

    for game_no in range(num_games):
        config.summary_file = 'example_game_replay_{}.json'.format(game_no)
        game_result = start_poker(config, verbose=0)
        participant_result = game_result['players'][0]
        game_scores.append(participant_result['stack'])
        print('Game #{}: stack={}, time_bank={}'.format(
            game_no,
            participant_result['stack'],
            player.time_available_bank,
        ))

        if player.failed:
            print('Bot failed: {}, {}'.format(player.fail_reason, player.fail_message))
            print(player.fail_stderr)

    print('Elapsed time: {}'.format(datetime.datetime.now() - start_time))
    print('Score: {}'.format(sum(game_scores) / num_games))
