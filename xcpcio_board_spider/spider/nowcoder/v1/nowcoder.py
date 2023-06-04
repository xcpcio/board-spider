from xcpcio_board_spider.core import utils
from xcpcio_board_spider.type import Contest, Team, Teams, Submission, Submissions, constants

import json
import requests
import concurrent.futures


class NowCoder:
    def __init__(self, contest: Contest, contest_id: int, fetch_uri: str = None):
        self.contest = contest
        self.contest_id = contest_id

        if fetch_uri is None:
            self.fetch_uri = "https://ac.nowcoder.com/acm-heavy/acm/contest/real-time-rank-data"
        else:
            self.fetch_uri = fetch_uri

        self.fetch_res_list = []

        self.teams = Teams()
        self.submissions = Submissions()

    def get_time_diff(self, l, r):
        return int((r - l) // 1000)

    def fetch(self):
        total = 0
        headers = {}

        params = (
            ('token', ''),
            ('id', self.contest_id),
            ('limit', '0'),
            ('_', utils.get_now_timestamp_second()),
        )

        resp = requests.get(
            self.fetch_uri, headers=headers, params=params)
        if resp.status_code != 200:
            raise RuntimeError(
                "fetch rank failed. [status_code={}]".format(resp.status_code))

        res = json.loads(resp.content)
        if res["code"] != 0:
            raise RuntimeError(
                "fetch rank failed. [code={}]".format(res["code"]))

        total = res['data']['basicInfo']['pageCount']

        res_list = []
        for i in range(1, total + 1):
            params = (
                ('token', ''),
                ('id', self.contest_id),
                ('limit', '0'),
                ('_', utils.get_now_timestamp_second()),
                ('page', str(i)),
            )

            resp = requests.get(self.fetch_uri, headers=headers, params=params)
            if resp.status_code != 200:
                raise RuntimeError(
                    "fetch rank failed. [status_code={}]".format(resp.status_code))

            res = json.loads(resp.content)
            if res["code"] != 0:
                raise RuntimeError(
                    "fetch rank failed. [code={}]".format(res["code"]))

            res_list.append(res)

        self.fetch_res_list = res_list

        return self

    def parse_teams(self):
        teams = Teams()

        for res in self.fetch_res_list:
            item = res['data']

            for raw_team in item['rankData']:
                team_id = raw_team['uid']
                team_name = raw_team['userName'].strip()
                team_organization = '---'

                if 'school' in raw_team.keys():
                    team_organization = raw_team['school']

                team = Team()
                team.team_id = team_id
                team.name = team_name
                team.organization = team_organization

                teams[team_id] = team

        self.teams = teams
        return self

    def parse_runs(self):
        runs = Submissions()

        for res in self.fetch_res_list:
            item = res['data']

            for raw_team in item['rankData']:
                team_id = raw_team['uid']
                i = -1
                for problem in raw_team['scoreList']:
                    i += 1

                    status = constants.RESULT_INCORRECT
                    timestamp = self.get_time_diff(
                        self.contest.start_time, min(self.contest.end_time, utils.get_now_timestamp_second()))

                    if problem['accepted']:
                        status = constants.RESULT_CORRECT
                        timestamp = self.get_time_diff(
                            self.contest.start_time, int(problem['acceptedTime']))

                    for j in range(0, problem['failedCount']):
                        run = Submission()
                        run.team_id = team_id
                        run.timestamp = timestamp
                        run.problem_id = i
                        run.status = constants.RESULT_INCORRECT

                        runs.append(run)

                    for j in range(0, problem['waitingJudgeCount']):
                        run = Submission()
                        run.team_id = team_id
                        run.timestamp = timestamp
                        run.problem_id = i
                        run.status = constants.RESULT_PENDING

                        runs.append(run)

                    if status == 'correct':
                        run = Submission()
                        run.team_id = team_id
                        run.timestamp = timestamp
                        run.problem_id = i
                        run.status = constants.RESULT_CORRECT

                        runs.append(run)

        self.runs = runs
        return self