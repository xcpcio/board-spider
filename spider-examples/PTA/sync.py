import grequests
import requests
import urllib3
import os
import json
import time
import gevent.monkey
gevent.monkey.patch_all(ssl=False)
urllib3.disable_warnings()


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def output(target_path, data, if_not_exists=False):
    if if_not_exists and os.path.exists(target_path):
        return

    with open(target_path, 'w') as f:
        f.write(json_output(data))


def mkdir(_path):
    if not os.path.exists(_path):
        os.makedirs(_path)


def get_timestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return int(timestamp)


def get_cookies(raw_cookies: str):
    from http.cookies import SimpleCookie
    cookie = SimpleCookie()
    cookie.load(raw_cookies)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {k: v.value for k, v in cookie.items()}

    return cookies


_params = json_input('params.json')
cookies = _params['cookies']
headers = _params['headers']
data_dir = _params['data_dir']
board_url = _params['board_url']

run_frozen_fallback = False
if 'run_frozen_fallback' in _params.keys():
    run_frozen_fallback = _params['run_frozen_fallback']
    frozen_start_timestamp = _params['frozen_start_timestamp']

team_info_xls_path = ''
if 'team_info_xls_path' in _params.keys():
    team_info_xls_path = _params['team_info_xls_path']


headers["Referer"] = board_url


penalty = 20
ac_score = 300


def frozen_fallback(runs, frozen_start_timestamp):
    for r in runs:
        if r['timestamp'] >= frozen_start_timestamp:
            r['status'] = 'pending'

    return runs


def read_xls(xls_file_path: str):
    import xlrd
    data = xlrd.open_workbook(xls_file_path)
    table = data.sheets()[0]
    nrows = table.nrows

    for i in range(1, nrows):
        yield table.row_values(i)


def get_team_info(team_info_xls_path: str):
    team_info = {}

    for row in read_xls(team_info_xls_path):
        team_id = row[0]

        team_info[team_id] = {}
        cur_team = team_info[team_id]

        cur_team["organization"] = row[3]
        cur_team["team_name"] = row[6]
        cur_team["members"] = []

        for ix in [8, 11, 14]:
            if len(row[ix]) > 0:
                cur_team["members"].append(row[ix])

    return team_info


def fetch():
    params = (
        ('page', '0'),
        ('limit', '50'),
    )

    c = get_cookies(cookies)

    response = requests.get(board_url, headers=headers,
                            params=params, cookies=c)

    total = json.loads(response.text)['total']

    req_list = []

    for i in range(((total + 49) // 50)):
        params = (
            ('page', str(i)),
            ('limit', '50'),
        )

        req_list.append(grequests.get(
            board_url, headers=headers, params=params, cookies=c))

    res_list = grequests.map(req_list)

    return res_list


def team_output(res_list):
    if len(team_info_xls_path) > 0:
        team_info = get_team_info(team_info_xls_path)

    teams = {}
    for item in res_list:
        item = json.loads(item.text)

        for team in item['commonRankings']['commonRankings']:
            if 'studentUser' in team['user'].keys():
                team_id = team['user']['studentUser']['studentNumber']
                _team = {}
                _team['team_id'] = team_id

                # _name = team['user']['studentUser']['name']
                # name = _name
                # name = _name.split('_')[2]
                # school = _name.split('_')[1]
                # _id = _name.split('_')[0]
                # if _id[0] == '*':
                #     _team['unofficial'] = 1
                # else:
                #     _team['official'] = 1
                # if _id[0] == 'F':
                #     _team['girl'] = 1

                cur_team = team_info[team_id]

                if len(team_info_xls_path) > 0:
                    _team['name'] = cur_team['team_name']
                    _team['organization'] = cur_team['organization']
                    _team['members'] = cur_team['members']

                _team['official'] = 1
                teams[team_id] = _team

    if len(teams.keys()) > 0:
        output(os.path.join(data_dir, "team.json"), teams)


def run_output(res_list):
    run = []

    for item in res_list:
        item = json.loads(item.text)
        # problem_id = item['commonRankings']['labels']
        problem_id = item["commonRankings"]["labelByIndexTuple"]

        problem_ix = 0
        for k in problem_id.keys():
            problem_id[k] = problem_ix
            problem_ix += 1

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
                    # p_id = key
                    p_id = problem_id[key]

                    _run = team['problemScores'][key]
                    timestamp = int(_run['acceptTime']) * 60

                    cnt = int(_run['submitCountSnapshot'])

                    pending_cnt = int(
                        _run['validSubmitCount']) - int(_run['submitCountSnapshot'])

                    run_ = {
                        'team_id': team_id,
                        'timestamp': timestamp,
                        'problem_id': p_id,
                        'status': 'incorrect',
                    }

                    if cnt > 0:
                        incorrect_num = cnt - 1

                        if int(_run['score']) == ac_score:
                            if penalty_num > incorrect_num:
                                penalty_num -= incorrect_num
                            else:
                                incorrect_num = penalty_num
                                penalty_num = 0

                        for i in range(0, incorrect_num):
                            run_['status'] = 'incorrect'
                            run.append(run_.copy())

                        if int(_run['score']) == ac_score:
                            run_['status'] = 'correct'

                        run.append(run_.copy())

                    for i in range(pending_cnt):
                        run_['status'] = 'pending'
                        run.append(run_.copy())

    if run_frozen_fallback:
        run = frozen_fallback(run, frozen_start_timestamp)

    if len(run) > 0:
        output(os.path.join(data_dir, 'run.json'), run)


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
        time.sleep(15)


if __name__ == "__main__":
    sync()
