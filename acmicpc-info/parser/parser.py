import os
from bs4 import BeautifulSoup
import json
import re
import time

RE_SOLUTION_AC_TYPE1 = re.compile(r'\d+/\d+$')
RE_SOLUTION_AC_TYPE2 = re.compile(r'\d+:\d+:\d+ \(\d+\)$')
RE_SOLUTION_AC_TYPE3 = re.compile(r'\d+:\d+:\d+\(-*\d+\)$')
RE_SOLUTION_AC_TYPE4 = re.compile(r'\d+:\d+:\d+$')
RE_SOLUTION_AC_TYPE5 = re.compile(r'\d+\(\d+\)$')
RE_SOLUTION_AC_TYPE6 = re.compile(r'\d+\(-\d+\)$')
RE_SOLUTION_AC_TYPE7 = re.compile(r'\d+$')
RE_SOLUTION_AC_TYPE8 = re.compile(r'\d+:\d+:\d+\(\+*\d+\)$')

RE_SOLUTION_WA_TYPE1 = re.compile(r'\d+/[-]+$')
RE_SOLUTION_WA_TYPE2 = re.compile(r'\(\d+\)$')
RE_SOLUTION_WA_TYPE3 = re.compile(r'\d+$')
RE_SOLUTION_WA_TYPE4 = re.compile(r'\(-\d+\)$')
RE_SOLUTION_WA_TYPE5 = re.compile(r'-\d+/[-]+$')
RE_SOLUTION_WA_TYPE6 = re.compile(r'-\d+$')

# ---------------------modify here to adapt different board------------
col_name = 3
col_organization = 1
col_problem_start = 6
col_problem_end = -1


def get_team_name_str(row):
    global col_name
    # name = row[col_name].get_text(strip=True).split('(')[-1]
    # return name
    # name = row[col_name].get_text().split()[0]
    # return '-'.join(name.split('-')[1:])
    return row[col_name].get_text(strip=True)


def get_team_name(name):
    # for i in range(len(name) - 1, -1, -1):
    #     if name[i] == '(':
    #         return name[:i - 1]
    return name


def getorganization(row):
    global col_organization
    # name = row[col_name].get_text(strip=True).split('-')[0]
    # if isofficalteam(name):
    #     return name[3:]
    # return name
    # name = row[col_name].get_text().split()[1]
    # return name
    return row[col_organization].get_text(strip=True)


def getproblemlist(row):
    global col_problem_start, col_problem_end
    return row[col_problem_start:col_problem_end]


def calc2seconds(timestr: str):
    hour, mins, seconds = map(int, timestr.split(':'))
    return hour * 3600 + mins * 60 + seconds


def getacinfo(problemstr: str):
    # print(problemstr)
    if RE_SOLUTION_AC_TYPE1.match(problemstr):
        times, actime = map(int, problemstr.split('/'))
        actime *= 60
    elif RE_SOLUTION_AC_TYPE2.match(problemstr):
        # print('TYPE2')
        actime, times = problemstr.split()
        actime = calc2seconds(actime)
        times = int(times[1:-1]) + 1
    elif RE_SOLUTION_AC_TYPE3.match(problemstr):
        # print('TYPE2')
        actime, times = problemstr.split('(')
        actime = calc2seconds(actime)
        times = -int(times[:-1]) + 1
    elif RE_SOLUTION_AC_TYPE4.match(problemstr):
        # print('TYPE2')
        actime = calc2seconds(problemstr)
        times = 1
    elif RE_SOLUTION_AC_TYPE5.match(problemstr):
        actime, times = problemstr.split('(')
        actime = int(actime) * 60
        times = int(times[:-1]) + 1
    elif RE_SOLUTION_AC_TYPE6.match(problemstr):
        actime, times = problemstr.split('(')
        actime = int(actime) * 60
        times = -int(times[:-1]) + 1
    elif RE_SOLUTION_AC_TYPE7.match(problemstr):
        actime = int(problemstr) * 60
        times = 1
    elif RE_SOLUTION_AC_TYPE8.match(problemstr):
        actime, times = problemstr.split('(')
        actime = calc2seconds(actime)
        times = int(times[:-1]) + 1
    return times, actime


def getwainfo(problemstr: str):
    if RE_SOLUTION_WA_TYPE1.match(problemstr):
        times = int(problemstr.split('/')[0])
    elif RE_SOLUTION_WA_TYPE2.match(problemstr):
        times = int(problemstr[1:-1])
    elif RE_SOLUTION_WA_TYPE3.match(problemstr):
        times = int(problemstr)
    elif RE_SOLUTION_WA_TYPE4.match(problemstr):
        times = -int(problemstr[1:-1])
    elif RE_SOLUTION_WA_TYPE5.match(problemstr):
        times = -int(problemstr.split('/')[0])
    elif RE_SOLUTION_WA_TYPE6.match(problemstr):
        times = -int(problemstr)
    return times


def isofficalteam(name: str):
    return name.find('*') != -1


# -----------------------------------------------------------------------

def teamparser(dom, contest_name: str):
    # dom = BeautifulSoup(board_content, 'lxml').html.body.table
    rows = [x for x in dom.contents if x != '\n']
    # row = [x for x in rows[0].contents if x != '\n']
    # col_num = 0
    # for item in row:
    #     print('col -', col_num, item.get_text(strip=True))
    #     col_num += 1
    # op = input('default setting(Y/N):\n')
    # if op == 'Y' or op == 'y':
    #     pass
    # else:
    #     global col_name, col_problem_start, col_organization, col_problem_end
    #     col_organization, col_name, col_problem_start, col_problem_end = map(int, input('col_organization, col_name, '
    #                                                                                     'col_problem_start, '
    #                                                                                     'col_problem_end\n').split())
    rows = rows[1:]
    team_id = 0
    res = dict()
    global CONTEST_TYPE, CONTEST_NAME

    for row in rows:
        team_id += 1
        row = [x for x in row.contents if x != '\n']
        team = dict()
        name = get_team_name(get_team_name_str(row))
        if name == "":
            name = " "
        team["team_id"] = str(team_id)
        team["name"] = name
        team["organization"] = getorganization(row)
        if isofficalteam(name):
            team["unofficial"] = 1
        else:
            team["official"] = 1
        res[str(team_id)] = team
    with open(contest_name + "team.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False))


def parserproblem(problem, team_id: int, problem_id: int):
    res = list()
    if "ac" in problem['class'] or "firstac" in problem['class'] or "fb" in problem['class']:
        times, actime = getacinfo(problem.get_text(strip=True))
        for delta in range(times):
            run = {'team_id': str(team_id), 'problem_id': problem_id, 'timestamp': max(0, actime - delta),
                   'status': 'correct' if delta == 0 else 'incorrect'}
            res.append(run)
    else:
        times = getwainfo(problem.get_text(strip=True))
        for delta in range(times):
            run = {'team_id': str(team_id), 'problem_id': problem_id, 'timestamp': delta,
                   'status': 'incorrect'}
            res.append(run)
    return res


def solutionparser(dom, contest_name: str):
    # dom = BeautifulSoup(board_content, 'lxml').html.body.table
    rows = [x for x in dom.contents if x != '\n'][1:]
    team_id = 0
    res = []
    for row in rows:
        team_id += 1
        row = getproblemlist([x for x in row.contents if x != '\n'])
        problem_id = 0
        for problem in row:
            if problem.get('class') is None:
                continue
            res += parserproblem(problem, team_id, problem_id)
            problem_id += 1
    with open(contest_name + "run.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False))


siteinfo = dict()


def configparser(contest_dir: str, contest_name: str, default_name: str):
    problem_num = col_problem_end - col_problem_start

    global siteinfo
    site = contest_dir + '/' + default_name
    global CONTEST_TYPE, YEAR
    default_name = CONTEST_TYPE.upper() + ' ' + ' '.join(default_name.split('_'))

    # print(default_name, site)
    # return None

    def generate_problem_label(num):
        return [chr(ord('A') + i) for i in range(num)]

    def generate_balloon_color(num):
        return default_balloon_color[:num]

    def get_timestamp(dt):
        timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
        timestamp = time.mktime(timeArray)
        return int(timestamp)

    default_balloon_color = [
        {'background_color': 'rgba(189, 14, 14, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(255, 144, 228, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(255, 255, 255, 0.7)', 'color': '#000'},
        {'background_color': 'rgba(38, 185, 60, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(239, 217, 9, 0.7)', 'color': '#000'},
        {'background_color': 'rgba(243, 88, 20, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(12, 76, 138, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(156, 155, 155, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(4, 154, 115, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(159, 19, 236, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(42, 197, 202, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(142, 56, 54, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(0, 0, 0, 0.7)', 'color': '#fff'},
    ]

    group = {
        'official': '正式队伍',
        'unofficial': '打星队伍',
    }

    status_time_display = {
        'correct': 1,
    }
    if siteinfo.get(site):
        config = {
            'contest_name': siteinfo[site]['title'],
            'start_time': get_timestamp(siteinfo[site].get('start_time')),
            'end_time': get_timestamp(siteinfo[site].get('end_time')),
            'frozen_time': 60 * 60,
            'problem_id': generate_problem_label(problem_num),
            'group': group,
            'organization': 'School',
            'status_time_display': status_time_display,
            'penalty': 20 * 60,
            'balloon_color': generate_balloon_color(problem_num),
        }
    else:
        config = {
            'contest_name': default_name,
            'start_time': get_timestamp(YEAR + "-09-01 09:00:00"),
            'end_time': get_timestamp(YEAR + "-09-01 14:00:00"),
            'frozen_time': 60 * 60,
            'problem_id': generate_problem_label(problem_num),
            'group': group,
            'organization': 'School',
            'status_time_display': status_time_display,
            'penalty': 20 * 60,
            'balloon_color': generate_balloon_color(problem_num),
        }
    with open(contest_name + "config.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(config, sort_keys=False, separators=(',', ':'), ensure_ascii=False))
    return None


def showtopic(dom):
    row = [x for x in dom.contents if x != '\n'][0]
    topics = [x for x in row.contents if x != '\n']
    global col_problem_start, col_problem_end
    cur = 'A'
    index = 0
    for item in topics:
        if item.get_text(strip=True)[0] == 'A':
            col_problem_start = col_problem_end = index
        if item.get_text(strip=True)[0] == cur:
            cur = chr(ord(cur) + 1)
            col_problem_end += 1
        print(item.get_text(strip=True).ljust(15, ' '), end='')
        index += 1
    print('')
    # print(col_problem_start, col_problem_end)


def single_test(file_name: str, OUTPUT_DIR: str):
    with open(file_name, 'r', encoding='utf-8') as f:
        CONTEST_NAME = file_name.split('.')[-2]
        board_content = f.read()
        print(CONTEST_NAME)
        if not os.path.isdir(OUTPUT_DIR + CONTEST_NAME):
            os.mkdir(OUTPUT_DIR + CONTEST_NAME)
        dom = BeautifulSoup(board_content, 'lxml').html.body.table
        showtopic(dom)
        teamparser(dom, OUTPUT_DIR + CONTEST_NAME + "\\")
        solutionparser(dom, OUTPUT_DIR + CONTEST_NAME + "\\")


if __name__ == '__main__':
    # WORK_DIR = "D:\\XCPCIO\\XCPCIO-Board-Data\\origin-data\\icpc\\2009"
    # FILE_NAME = "whu_onsite.html"
    # OUTPUT_DIR = "D:\\XCPCIO\\XCPCIO-Board-Data\\data\\icpc\\2009\\"
    # os.chdir(WORK_DIR)
    # single_test(FILE_NAME, OUTPUT_DIR)
    # exit(0)
    with open('path.config', 'r', encoding='utf-8') as f:
        WORK_DIR = f.readline().strip()
        OUTPUT_DIR = f.readline().strip()
        CONTEST_TYPE = f.readline().strip()
        YEAR = f.readline().strip()
        CONFIG_DIR = f.readline().strip()
    WORK_DIR = WORK_DIR + CONTEST_TYPE + '/' + YEAR
    OUTPUT_DIR = OUTPUT_DIR + CONTEST_TYPE + '/' + YEAR
    print(WORK_DIR)
    print(OUTPUT_DIR)
    if os.path.isdir(WORK_DIR):
        os.chdir(WORK_DIR)
    else:
        exit(-1)
    # for file_name in os.listdir():
    #     if os.path.isdir(file_name):
    #         continue
    #     with open(file_name, 'r', encoding='utf-8') as f:
    #         board_content = f.read()
    #         dom = BeautifulSoup(board_content, 'lxml').html.body.table
    #         showtopic(dom)
    # exit(-1)
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    contest_dir = "/" + CONTEST_TYPE.lower() + "/" + YEAR
    with open(CONFIG_DIR, 'r', encoding='utf-8') as f:
        siteinfo = json.loads(f.read())
    print(contest_dir)
    # exit(0)
    OUTPUT_DIR += '\\'
    for file_name in os.listdir():
        if os.path.isdir(file_name):
            continue
        with open(file_name, 'r', encoding='utf-8') as f:
            CONTEST_NAME = file_name.split('.')[-2]
            board_content = f.read()
            print(CONTEST_NAME)
            if not os.path.isdir(OUTPUT_DIR + CONTEST_NAME):
                os.mkdir(OUTPUT_DIR + CONTEST_NAME)
            dom = BeautifulSoup(board_content, 'lxml').html.body.table
            showtopic(dom)
            # teamparser(dom, OUTPUT_DIR + CONTEST_NAME + "\\")
            solutionparser(dom, OUTPUT_DIR + CONTEST_NAME + "\\")
            # configparser(contest_dir, OUTPUT_DIR + contest_name + "\\", contest_name)
            # exit(0)
