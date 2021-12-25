from os import path
import os
import json
import time
import requests
# PyExecJS
import execjs


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


def mkdir(_path):
    if not path.exists(_path):
        os.makedirs(_path)


def get_timestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return int(timestamp)


def output(filename, data):
    with open(path.join(data_dir, filename), 'w') as f:
        f.write(json_output(data))


def get_now():
    return int(round(time.time() * 1000))


def get_js_object(js_code, key):
    text = js_code
    text = text[text.find("=") + 1:]
    text = text[:text.rfind(";")]
    text = "JSON.stringify(" + text + ")"
    text = execjs.eval(text)
    return json.loads(text)


_params = json_input('params.json')
data_dir = _params['data_dir']


def fetch(key):
    key_url = key + "_url"
    key_file = key + "_file"
    if key_url in _params.keys():
        url = _params[key_url]
        params = (
            ('t', get_now()),
        )
        response = requests.get(url, params=params)

        return get_js_object(response.text, key)
    elif key_file in _params.keys():
        board_file = _params[key_file]

        with open(board_file, 'r') as f:
            return get_js_object(f.read(), key)
    else:
        return ""


def fetch_all():
    return fetch("teams"), fetch("runs")


def team_output(teams):
    print(teams)

    team_dic = teams
    team = {}

    for key in team_dic:
        item = team_dic[key]
        team[key] = {}
        new_item = team[key]
        new_item['organization'] = item['school']
        new_item['name'] = item['team']

        members = item['members'].split('、')
        members.sort()
        new_item['members'] = members

        type = item['type'].split(" ")
        if 'unofficial' in type:
            new_item['unofficial'] = 1
        else:
            new_item['official'] = 1

        if 'girls' in type:
            new_item['girl'] = 1

    if len(team) > 0:
        output("team.json", team)


def run_output(runs):
    print(runs)

    run_list = runs
    run = []

    for item in run_list:
        if item[2] < 0:
            continue

        new_item = {}
        new_item['team_id'] = item[0]
        new_item['problem_id'] = ord(item[1]) - ord('A')
        new_item['timestamp'] = (int(item[2] // 1000) // 60) * 60

        status = item[3]
        if status == 'AC':
            new_item['status'] = 'correct'
        elif status == 'NO':
            new_item['status'] = 'incorrect'
        elif status == 'NEW':
            new_item['status'] = 'pending'

        run.append(new_item)

    if len(run) > 0:
        output("run.json", run)


def sync():
    while True:
        print("fetching...")

        try:
            teams, runs = fetch_all()
            team_output(teams)
            run_output(runs)

            print("fetch successfully")
        except Exception as e:
            print("fetch failed...")
            print(e)

        print("sleeping...")
        time.sleep(10)


sync()
