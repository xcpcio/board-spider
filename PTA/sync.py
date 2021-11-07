import requests
import json
import grequests
from os import path
import time


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


_params = json_input('params.json')
cookies = _params['cookies']
headers = _params['headers']
data_dir = _params['data_dir']
board_url = _params['board_url']

penalty = 20
ac_score = 300


def json_output(data):
    return json.dumps(data, sort_keys=False, indent=4, separators=(',', ':'), ensure_ascii=False)


def output(filename, data):
    with open(path.join(data_dir, filename), 'w') as f:
        f.write(json_output(data))


def fetch():
    params = (
        ('page', '0'),
        ('limit', '50'),
    )

    response = requests.get(board_url, headers=headers,
                            params=params, cookies=cookies)
    total = json.loads(response.text)['total']

    print(total)

    req_list = []

    for i in range(((total + 49) // 50)):
        params = (
            ('page', str(i)),
            ('limit', '50'),
        )
        req_list.append(grequests.get(
            board_url, headers=headers, params=params, cookies=cookies))

    res_list = grequests.map(req_list)
    return res_list


def team_output(res_list):
    teams = {}
    for item in res_list:
        item = json.loads(item.text)
        for team in item['commonRankings']['commonRankings']:
            if 'studentUser' in team['user'].keys():
                team_id = team['user']['studentUser']['studentNumber']
                _name = team['user']['studentUser']['name']
                name = _name.split('_')[2]
                school = _name.split('_')[1]
                _id = _name.split('_')[0]
                _team = {}
                _team['name'] = name
                _team['organization'] = school
                _team['team_id'] = team_id
                if _id[0] == '*':
                    _team['unofficial'] = 1
                else:
                    _team['official'] = 1
                if _id[0] == 'F':
                    _team['girl'] = 1
                teams[team_id] = _team
    if len(teams.keys()) > 0:
        output("team.json", teams)


def run_output(res_list):
    run = []
    for item in res_list:
        item = json.loads(item.text)
        problem_id = item['commonRankings']['labels']
        for team in item['commonRankings']['commonRankings']:
            if 'studentUser' in team['user'].keys():
                team_id = team['user']['studentUser']['studentNumber']

                total_time = team['solvingTime']
                penalty_num = 0
                for key in team['problemScores']:
                    _run = team['problemScores'][key]
                    if int(_run['score']) == 300:
                        total_time -= int(_run['acceptTime'])

                penalty_num = total_time // penalty

                for key in team['problemScores']:
                    p_id = problem_id.index(key)
                    _run = team['problemScores'][key]
                    timestamp = int(_run['acceptTime']) * 60

                    cnt = int(_run['submitCountSnapshot'])
                    incorrect_num = cnt - 1
                    if int(_run['score']) == ac_score:
                        if penalty_num > incorrect_num:
                            penalty_num -= incorrect_num
                        else:
                            incorrect_num = penalty_num
                            penalty_num = 0

                    for i in range(0, incorrect_num):
                        run_ = {
                            'team_id': team_id,
                            'timestamp': timestamp,
                            'problem_id': p_id,
                            'status': 'incorrect'
                        }
                        run.append(run_)
                    run_ = {
                        'team_id': team_id,
                        'timestamp': timestamp,
                        'problem_id': p_id,
                        'status': 'incorrect'
                    }
                    if int(_run['score']) == ac_score:
                        run_['status'] = 'correct'
                    run.append(run_)
    if len(run) > 0:
        output('run.json', run)


def sync():
    while True:
        print("fetching...")
        try:
            res_list = fetch()
            team_output(res_list)
            run_output(res_list)
            print("fetch successfully")
        except Exception as e:
            print("fetch failed...")
            print(e)
        print("sleeping...")
        time.sleep(20)


sync()
