import os
from bs4 import BeautifulSoup
import json



def get_team_name_str(row):
    return row[3].get_text(strip=True)


def get_team_name(name):
    for i in range(len(name) - 1, -1, -1):
        if name[i] == '(':
            return name[:i - 1]
    return name


def getorganization(row):
    return row[1].get_text(strip=True)


def getproblemlist(row):
    return row[6:]


def calc2seconds(timestr: str):
    hour, mins, seconds = map(int, timestr.split(':'))
    return hour * 3600 + mins * 60 + seconds


def getacinfo(problemstr: str):
    # if problemstr.find('(') != -1:
    #     actime, times = problemstr.split('(')
    #     actime = calc2seconds(actime)
    #     times = -int(times[:-1]) + 1
    # else:
    #     actime = calc2seconds(problemstr)
    #     times = 1
    # return times, actime
    times, actime = map(int, problemstr.split('/'))
    return times, actime * 60


def getwainfo(problemstr: str):
    # times = int(problemstr[1:-1])
    # return -int(times)
    # times = int(problemstr.split('/')[0])
    times = int(problemstr)
    return times


def isofficalteam(name: str):
    return name[-1] == '*'


def teamparser(board_content: str, contest_name: str):
    dom = BeautifulSoup(board_content, 'lxml').html.table
    rows = [x for x in dom.contents if x != '\n'][1:]
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
    if "ac" in problem['class'] or "firstac" in problem['class']:
        times, actime = getacinfo(problem.get_text(strip=True))
        for delta in range(times):
            run = {'team_id': team_id, 'problem_id': problem_id, 'timestamp': actime - delta,
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
    dom = BeautifulSoup(board_content, 'lxml').html.table
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


if __name__ == '__main__':
    WORK_DIR = input('work path:\n')
    OUTPUT_DIR = input('output path:\n')
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
            if not os.path.isdir(OUTPUT_DIR + contest_name):
                os.mkdir(OUTPUT_DIR + contest_name)
            teamparser(board_content, OUTPUT_DIR + contest_name + "\\")
            solutionparser(board_content, OUTPUT_DIR + contest_name + "\\")
