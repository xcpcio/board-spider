import requests
import json
from os import path
import time

def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)

_params = json_input('params.json')
data_dir = _params['data_dir']
penalty = 20

def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)

def output(filename, data):
    with open(path.join(data_dir, filename), 'w') as f:
        f.write(json_output(data))

def get_timestamp(dt):
    #转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    #转换成时间戳
    timestamp = time.mktime(timeArray)
    return int(timestamp)

def get_now():
    return int(round(time.time() * 1000))

def fetch():
    if 'board_url' in _params.keys():
        board_url = _params['board_url']
        params = (
            ('t', get_now()),
        )   
        response = requests.get(board_url, params=params)
        return json.loads(response.text)
    else:
        board_file = _params['board_file']
        return json_input(board_file)

def team_output(res):
    team = {}
    for item in res['rows']:
        item = item['user']
        _item = {}
        _item['team_id'] = item['id']
        _item['name'] = item['name']
        _item['organization'] = item['organization']
        _item['coach'] = item['teamMembers'][0]['name'].replace('(教练)', '')
        members = [item['teamMembers'][i]['name'] for i in range(1, 4)]
        members.sort()
        _item['members'] = members
        if item['official'] == True:
            _item['official'] = 1
        else:
            _item['unofficial'] = 1
        if 'marker' in item.keys():
            if item['marker'] == 'female':
                _item['girl'] = 1
        team[_item['team_id']] = _item
    if len(team.keys()) > 0:
        output("team.json", team)

def Accepted(result):
    return result == 'AC' or result == 'FB'

def run_output(res):
    run = []
    for item in res['rows']:

        team_id = item['user']['id']
        total_time = item['score']['time'][0]
        penalty_num = 0
        for problem in item['statuses']:
            if Accepted(problem['result']):
                total_time -= int(problem['time'][0])
        penalty_num = total_time // penalty

        problem_id = -1
        for problem in item['statuses']:
            problem_id += 1
            _run = {}
            _run['problem_id'] = problem_id
            _run['team_id'] = team_id
            for __run in problem['solutions']:
                status = 'incorrect'
                if Accepted(__run['result']):
                    status = 'correct'
                timestamp = int(__run['time'][0])
                if __run['time'][1] == 'min':
                    timestamp *= 60;
                elif __run['time'][1] == 's':
                    timestamp = timestamp // 60 * 60
                _run['status'] = status
                _run['timestamp'] = timestamp
                run.append(_run.copy())
    if len(run) > 0:
        output('run.json', run)

def sync():
    while True:
        print("fetching...")
        try:
            res = fetch()
            team_output(res)
            run_output(res)
            print("fetch successfully")
        except Exception as e:
            print("fetch failed...")
            print(e)
        print("sleeping...")
        time.sleep(20)

sync()
