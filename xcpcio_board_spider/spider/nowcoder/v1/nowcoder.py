import json

import requests

from xcpcio_board_spider.core import logger, utils
from xcpcio_board_spider.type import (
    Contest,
    Submission,
    Submissions,
    Team,
    Teams,
    constants,
)


class NowCoder:
    CONSTANT_RANK_URL = "https://ac.nowcoder.com/acm-heavy/acm/contest/real-time-rank-data"
    CONSTANT_SUBMISSIONS_URL = "https://ac.nowcoder.com/acm-heavy/acm/contest/status-list"

    def __init__(self, contest: Contest, contest_id: int):
        self.contest = contest
        self.contest_id = contest_id

        self.fetch_res_list = []

        self.logger = logger.init_logger()

        self.teams = Teams()
        self.submissions = Submissions()

    def get_time_diff(self, l, r):
        return int(r - l)

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
            self.CONSTANT_RANK_URL, headers=headers, params=params)
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

            resp = requests.get(self.CONSTANT_RANK_URL,
                                headers=headers, params=params)
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

    def fetch_single_team_submissions(self, team: Team):
        runs = Submissions()

        page_ix = 1

        while True:
            params = (
                ('token', ''),
                ('id', self.contest_id),
                ('page', page_ix),
                ('pageSize', 50),
                ('searchUserName', team.name),
                ('_', utils.get_now_timestamp_second()),
            )
            headers = {}

            resp = requests.get(self.CONSTANT_SUBMISSIONS_URL,
                                headers=headers, params=params)
            if resp.status_code != 200:
                raise RuntimeError(
                    "fetch rank failed. [status_code={}]".format(resp.status_code))

            res = json.loads(resp.content)
            if res["code"] != 0:
                raise RuntimeError(
                    "fetch rank failed. [code={}]".format(res["code"]))

            res = res["data"]

            for r in res["data"]:
                run = Submission()

                team_name = r["userName"]
                if team_name != team.name:
                    continue

                timestamp = (int(r["submitTime"]) // 1000)
                if timestamp > self.contest.end_time:
                    continue

                status = r["statusMessage"]

                if status == "编译错误":
                    continue

                run.submission_id = str(r["submissionId"])
                run.timestamp = timestamp - self.contest.start_time
                run.team_id = str(r["userId"])
                run.problem_id = ord(str(r["index"])) - ord("A")

                if status == "答案正确":
                    run.status = constants.RESULT_CORRECT
                else:
                    run.status = constants.RESULT_INCORRECT

                runs.append(run)

            if page_ix == int(res["basicInfo"]["pageCount"]):
                break

            page_ix += 1

        return runs

    def fetch_submissions(self):
        runs = Submissions()
        for t in self.teams.values():
            self.logger.info("fetch submissions. [team={}]".format(t.name))

            r = self.fetch_single_team_submissions(t)
            runs.extend(r)

        self.runs = runs
        return self

    def parse_teams(self):
        teams = Teams()

        for res in self.fetch_res_list:
            item = res['data']

            for raw_team in item['rankData']:
                team_id = str(raw_team['uid'])
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
                            self.contest.start_time, int(problem['acceptedTime']) // 1000)

                    for j in range(0, problem['failedCount']):
                        run = Submission()
                        run.team_id = team_id
                        run.timestamp = max(0, timestamp - 1)
                        run.problem_id = i
                        run.status = constants.RESULT_INCORRECT

                        runs.append(run)

                    for j in range(0, problem['waitingJudgeCount']):
                        run = Submission()
                        run.team_id = team_id
                        run.timestamp = max(0, timestamp - 1)
                        run.problem_id = i
                        run.status = constants.RESULT_PENDING

                        runs.append(run)

                    if status == constants.RESULT_CORRECT:
                        run = Submission()
                        run.team_id = team_id
                        run.timestamp = timestamp
                        run.problem_id = i
                        run.status = constants.RESULT_CORRECT

                        runs.append(run)

        self.runs = runs
        return self
