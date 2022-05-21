import time
import os
from os import path
import json
import requests
import grequests
import gevent.monkey
gevent.monkey.patch_all()


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def output(filename, data):
    with open(path.join(data_dir, filename), 'w') as f:
        f.write(json_output(data))


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


def get_now():
    return int(round(time.time() * 1000))


def get_timestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return int(round(timestamp * 1000))


def get_time_diff(l, r):
    return int((r - l) // 1000)


def ensure_dir(s):
    if not os.path.exists(s):
        os.makedirs(s)


_params = json_input('params.json')

# headers = _params['headers']
headers = {}
data_dir = _params['data_dir']
board_url = _params['board_url']
start_time = get_timestamp(_params['start_time'])
end_time = get_timestamp(_params['end_time'])
contest_id = _params['contest_id']

unofficial_organization = []
unofficial_team_name = []
if 'unofficial_organization' in _params.keys():
    unofficial_organization = _params['unofficial_organization']
if 'unofficial_team_name' in _params.keys():
    unofficial_team_name = _params['unofficial_team_name']

print(start_time)
print(end_time)

ensure_dir(data_dir)


def fetch():
    total = 0
    while True:
        params = (
            ('token', ''),
            ('id', contest_id),
            ('limit', '0'),
            ('_', get_now()),
        )
        response = requests.get(board_url, headers=headers, params=params)
        res = json.loads(response.text)
        if res['code'] == 0:
            total = res['data']['basicInfo']['pageCount']
            break

    print(total)

    req_list = []

    for i in range(1, total + 1):
        params = (
            ('token', ''),
            ('id', contest_id),
            ('limit', '0'),
            ('_', get_now()),
            ('page', str(i)),
        )
        req_list.append(grequests.get(
            board_url, headers=headers, params=params))

    res_list = grequests.map(req_list)
    return res_list


def team_output(res_list):
    teams = {}
    for item in res_list:
        item = json.loads(item.text)
        item = item['data']
        for team in item['rankData']:
            team_id = team['uid']
            team_name = team['userName'].strip()
            team_organization = '---'

            if 'school' in team.keys():
                team_organization = team['school']

            _team = {}
            _team['name'] = team_name
            _team['organization'] = team_organization

            if len(_team['name']) >= 3 and _team['name'][:3] == '***':
                _team['unofficial'] = 1
                _team['name'] = team_name[3:]
            else:
                _team['official'] = 1

            if team_organization in unofficial_organization or team_name in unofficial_team_name:
                _team['unofficial'] = 1
                if 'official' in _team.keys():
                    del _team['official']

            teams[team_id] = _team

    if len(teams.keys()) > 0:
        output("team.json", teams)


def run_output(res_list):
    run = []
    for item in res_list:
        item = json.loads(item.text)
        item = item['data']
        for team in item['rankData']:
            team_id = team['uid']
            i = -1
            for problem in team['scoreList']:
                timestamp = get_time_diff(start_time, min(end_time, get_now()))
                i += 1
                status = 'incorrect'
                if problem['accepted']:
                    status = 'correct'
                    timestamp = get_time_diff(
                        start_time, int(problem['acceptedTime']))

                for j in range(0, problem['failedCount']):
                    run_ = {
                        'team_id': team_id,
                        'timestamp': timestamp,
                        'problem_id': i,
                        'status': 'incorrect'
                    }
                    run.append(run_)

                for j in range(0, problem['waitingJudgeCount']):
                    run_ = {
                        'team_id': team_id,
                        'timestamp': timestamp,
                        'problem_id': i,
                        'status': 'pending'
                    }
                    run.append(run_)

                if status == 'correct':
                    run_ = {
                        'team_id': team_id,
                        'timestamp': timestamp,
                        'problem_id': i,
                        'status': 'correct'
                    }
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
        time.sleep(10)


sync()
