import os
from bs4 import BeautifulSoup
import json
import re

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

col_name = 3
col_organization = 1
col_problem_start = 6
col_problem_end = -1


def get_team_name_str(row):
    global col_name
    return row[col_name].get_text(strip=True)


def get_team_name(name):
    # for i in range(len(name) - 1, -1, -1):
    #     if name[i] == '(':
    #         return name[:i - 1]
    return name


def getorganization(row):
    global col_organization
    return row[col_organization].get_text(strip=True)


def getproblemlist(row):
    global col_problem_start, col_problem_end
    if col_problem_end == -1:
        return row[col_problem_start:col_problem_end]
    return row[col_problem_start:]


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


def teamparser(board_content: str, contest_name: str):
    dom = BeautifulSoup(board_content, 'lxml').html.body.table
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
    res = []
    for row in rows:
        team_id += 1
        row = [x for x in row.contents if x != '\n']
        team = dict()
        name = get_team_name(get_team_name_str(row))
        if name == "":
            name = " "
        team["team_id"] = team_id
        team["name"] = name
        team["organization"] = getorganization(row)
        if isofficalteam(name):
            team["unofficial"] = 1
        else:
            team["official"] = 1
        res.append(team)
    with open(contest_name + "team.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False))


def parserproblem(problem, team_id: int, problem_id: int):
    res = list()
    if "ac" in problem['class'] or "firstac" in problem['class'] or "fb" in problem['class']:
        times, actime = getacinfo(problem.get_text(strip=True))
        for delta in range(times):
            run = {'team_id': team_id, 'problem_id': problem_id, 'timestamp': max(0, actime - delta),
                   'status': 'correct' if delta == 0 else 'incorrect'}
            res.append(run)
    else:
        times = getwainfo(problem.get_text(strip=True))
        for delta in range(times):
            run = {'team_id': team_id, 'problem_id': problem_id, 'timestamp': delta,
                   'status': 'correct' if delta == 0 else 'incorrect'}
            res.append(run)
    return res


def solutionparser(board_content: str, contest_name: str):
    dom = BeautifulSoup(board_content, 'lxml').html.body.table
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


def single_test(file_name: str):
    with open(file_name, 'r', encoding='utf-8') as f:
        contest_name = re.split(r'[.\\]', file_name)[-2]
        board_content = f.read()
        print(contest_name)
        if not os.path.isdir(OUTPUT_DIR + contest_name):
            os.mkdir(OUTPUT_DIR + contest_name)
        teamparser(board_content, OUTPUT_DIR + contest_name + "\\")
        solutionparser(board_content, OUTPUT_DIR + contest_name + "\\")


if __name__ == '__main__':
    with open('path.config', 'r', encoding='utf-8') as f:
        WORK_DIR = f.readline().strip()
        OUTPUT_DIR = f.readline().strip()
    print(WORK_DIR)
    print(OUTPUT_DIR)
    # WORK_DIR = input('work path:\n')
    # OUTPUT_DIR = input('output path:\n')
    if os.path.isdir(WORK_DIR):
        os.chdir(WORK_DIR)
    else:
        exit(-1)
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    OUTPUT_DIR += '\\'
    for file_name in os.listdir():
        if os.path.isdir(file_name):
            continue
        with open(file_name, 'r', encoding='utf-8') as f:
            contest_name = file_name.split('.')[-2]
            board_content = f.read()
            print(contest_name)
            # global col_name, col_problem_start, col_organization, col_problem_end
            if contest_name.find('online') != -1:
                col_organization, col_name, col_problem_start, col_problem_end = 1, 3, 6, 0
            else:
                col_organization, col_name, col_problem_start, col_problem_end = 1, 3, 6, -1
            if not os.path.isdir(OUTPUT_DIR + contest_name):
                os.mkdir(OUTPUT_DIR + contest_name)
            teamparser(board_content, OUTPUT_DIR + contest_name + "\\")
            solutionparser(board_content, OUTPUT_DIR + contest_name + "\\")
