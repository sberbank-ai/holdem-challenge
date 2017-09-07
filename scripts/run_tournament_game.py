import os
import json
import subprocess
import datetime
import urllib
import argparse
import copy

from pypokerengine.players import RandomPlayer
from pypokerengine.players.docker_container import DockerContainerPlayer
from pypokerengine.api.game import setup_config, start_poker


def run_game(game_id, participants, archives_path, workspaces_path, game_config, time_limit_action, time_limit_bank):
    players = []

    for participant in participants:
        submission_id = participant['submission_id']
        archive_filename = os.path.abspath(os.path.join(archives_path, 'submission_{}.zip'.format(submission_id)))
        workspace_path = os.path.abspath(os.path.join(workspaces_path, submission_id))

        if not os.path.exists(archive_filename):
            print('Downloading archive', participant['archive_url'])
            try:
                urllib.request.urlretrieve(participant['archive_url'], archive_filename)
            except urllib.error.HTTPError as e:
                print('HTTPError', e, participant['archive_url'])
                return {'error': 'http error when downloading', 'error_participant': participant}

        print('Extracting archive', workspace_path)
        if not os.path.exists(workspace_path):
            os.makedirs(workspace_path)
            unzip_proc = subprocess.run(['unzip', '-o', '-qq', '-d', workspace_path, archive_filename])
            if unzip_proc.returncode != 0:
                return {'error': 'bad zip file', 'error_participant': participant}

        try:
            with open(os.path.join(workspace_path, 'metadata.json')) as f_metadata:
                metadata = json.load(f_metadata)

            image = metadata['image']
            entry_point = metadata['entry_point']
        except FileNotFoundError:
            return {
                'success': False,
                'status': 'error: metadata not found',
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'status': 'error: invalid metadata',
            }
        except KeyError:
            return {
                'success': False,
                'status': 'error: invalid metadata',
            }

        # TODO: pull image

        player = DockerContainerPlayer(
            source_dir=os.path.abspath(workspace_path),
            image=image,
            entry_point=entry_point,
            time_limit_action=time_limit_action,
            time_limit_bank=time_limit_bank,

        )
        player.user_id = participant['user_id']
        players.append(player)

    start_time = datetime.datetime.now()

    config = copy.copy(game_config)
    for p in players:
        config.register_player(name=p.user_id, algorithm=p)

    game_result = None
    try:
        game_result = start_poker(config, verbose=1)
    except ValueError as e:
        print(e)
        pass
    except RuntimeError as e:
        print(e)
        pass

    for player in players:
        player.stop()

    elapsed_time = (datetime.datetime.now() - start_time).total_seconds()

    result = game_result
    if result is None:
        result = {'error': 'crashed'}
    result['elapsed_time'] = elapsed_time

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archives', default='archives')
    parser.add_argument('--workspaces', default='workspaces')
    parser.add_argument('--replays', default='replays')
    parser.add_argument('--results', default='results')
    parser.add_argument('--time-action', default=0.2, type=float)
    parser.add_argument('--time-bank', default=30, type=float)
    parser.add_argument('--game-index', default=None, type=int)
    parser.add_argument('games_file')
    args = parser.parse_args()

    with open(args.games_file) as fin:
        games = json.load(fin)

    if args.game_index:
        games = [games[args.game_index]]

    for game in games:
        game_id = game['game_id']

        result_filename = os.path.join(args.results, 'result_{}.json'.format(game_id))
        if os.path.exists(result_filename) and args.game_index is None:
            with open(result_filename) as fin:
                old_result = json.load(fin)
                if 'error' not in old_result:
                    print('!!! GOOD RESULT')
                    continue

        print('##### GAME {}'.format(game_id))
        participants = game['participants']

        config = setup_config(
            max_round=50,
            initial_stack=1500,
            small_blind_amount=15,
            summary_file=os.path.join(args.replays, 'game_{}.json'.format(game_id)),
        )
        result = run_game(
            game_id,
            participants,
            archives_path=args.archives,
            workspaces_path=args.workspaces,
            game_config=config,
            time_limit_action=args.time_action,
            time_limit_bank=args.time_bank,
        )

        with open(result_filename, 'wt') as fout:
            json.dump(result, fout, indent=4)



