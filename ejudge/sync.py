import requests
import json
import time
import bs4
import os
import logging


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


_params = json_input('params.json')
data_dir = _params['data_dir']


def output(filename, data):
    with open(os.path.join(data_dir, filename), 'w') as f:
        f.write(json_output(data))


def mkdir(_path):
    if not os.path.exists(_path):
        os.makedirs(_path)


def get_now():
    return int(time.time())


def trim(s):
    def ltrim(s):
        while len(s) > 0:
            if s[0] == " " or s[0] == "\n":
                s = s[1:]
            else:
                break
        return s

    s = ltrim(s)
    s = s[::-1]
    s = ltrim(s)
    s = s[::-1]

    return s


def init_logging():
    global logger

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)


def fetch():
    if 'board_url' in _params.keys():
        board_url = _params['board_url']
        params = (
            ('t', get_now()),
        )
        response = requests.get(board_url, params=params, timeout=5)
        html = response.text

        return html

    elif 'board_file' in _params.keys():
        board_file = _params['board_file']
        with open(board_file, 'r') as f:
            return f.read()

    return ""


def team_out(html):
    team = {}
    soup = bs4.BeautifulSoup(html, 'html5lib')

    tbody = soup.select('tbody')[0]
    trs = tbody.select('tr')

    for tr in trs:
        if tr.get('class') is None:
            continue

        tds = tr.select('td')

        _team = {}
        team_name = trim(tds[1].text)
        team_id = team_name

        _team['name'] = team_name
        _team['team_id'] = team_id
        _team['official'] = 1

        team[team_id] = _team

    if len(team) > 0:
        output("team.json", team)


def run_out(html):
    run = []
    soup = bs4.BeautifulSoup(html, 'html5lib')

    tbody = soup.select('tbody')[0]
    trs = tbody.select('tr')

    for tr in trs:
        if tr.get('class') is None:
            continue

        tds = tr.select('td')

        team_id = trim(tds[1].text)

        _run = {}
        _run['team_id'] = team_id

        tds = tds[2:-4]

        problem_id = -1

        for td in tds:
            problem_id += 1

            res = td.select('center')
            res = str(res[0])
            res = res.replace('<center>', '')
            res = res.replace('</center>', '')
            res = res.replace('<font size="1">', '')
            res = res.replace('</font>', '')

            if res == '-':
                continue

            _run['problem_id'] = problem_id

            nums = res.split('<br/>')[0]
            times = res.split('<br/>')[1]
            times = times.split(':')
            timestamp = int(times[0]) * 3600 + int(times[1]) * 60

            tries = 0
            status = 'correct'

            if nums == '+':
                tries = 1
            else:
                tries = int(nums)
                if tries < 0:
                    status = 'incorrect'
                    tries = -tries
                else:
                    tries += 1

            if status == 'correct':
                tries -= 1

            _run['timestamp'] = timestamp

            _run['status'] = 'incorrect'
            run.extend([_run.copy()] * tries)

            if status == 'correct':
                _run['status'] = 'correct'
                run.append(_run.copy())

    if len(run) > 0:
        output('run.json', run)


def sync():
    init_logging()

    while True:
        logger.info("fetching...")
        try:
            html = fetch()

            team_out(html)
            run_out(html)

            logger.info("fetch successfully")
        except Exception as e:
            logger.error("fetch failed...", e)

        logger.info("sleeping...")

        time.sleep(20)


# sync()

html = fetch()
team_out(html)
run_out(html)
