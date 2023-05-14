import grequests
import requests
import urllib3
import json
import gevent.monkey
import copy

from xcpcio_board_spider import Contest, Submission, Submissions, Team, Teams, constants, utils

gevent.monkey.patch_all(ssl=False)
urllib3.disable_warnings()


class PTA:
    AC_SCORE = 300

    def __init__(self, contest: Contest, fetch_uri: str, cookies_str: str, headers: str = None):
        self.contest = contest
        self.fetch_uri = fetch_uri
        self.cookies = utils.get_cookies(cookies_str)

        if headers is None:
            self.headers = self.get_default_headers()
        else:
            self.headers = headers

        self.fetch_list = []
        self.team_info_list = {}

        self.teams = Teams()
        self.runs = Submissions()

    def get_default_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "Accept": "application/json;charset=UTF-8",
            "Accept-Language": "zh-CN",
            "X-Lollipop": "",
            "X-Marshmallow": "2061554085%0",
            "Content-Type": "application/json;charset=UTF-8",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }

    def fetch(self):
        params = {
            'page': '0',
            'limit': '50',
        }

        response = requests.get(self.fetch_uri, headers=self.headers,
                                params=params, cookies=self.cookies)

        total = json.loads(response.text)['total']

        req_list = []

        for i in range(((total + 49) // 50)):
            params = (
                ('page', str(i)),
                ('limit', '50'),
            )

            req_list.append(grequests.get(
                self.fetch_uri,
                headers=self.headers,
                params=params,
                cookies=self.cookies
            ))

        fetch_list = []
        resp_list = grequests.map(req_list)

        for resp in resp_list:
            res = json.loads(resp.text)
            fetch_list.append(res)

        self.fetch_list = fetch_list

        return self

    def parse_teams(self):
        teams = Teams()

        for fetch_res in self.fetch_list:
            for raw_team in fetch_res['commonRankings']['commonRankings']:
                if 'studentUser' in raw_team['user'].keys():
                    team_id = raw_team['user']['studentUser']['studentNumber']
                    team_key = raw_team['user']['studentUser']['name'].strip()

                    team = Team()
                    team.team_id = team_id
                    team.name = team_key
                    team.official = True

                    teams[team_id] = team

        self.teams = teams
        return self

    def parse_runs(self):
        runs = Submissions()

        for fetch_res in self.fetch_list:
            # problem_id = fetch_res['commonRankings']['labels']
            problem_id = fetch_res["commonRankings"]["labelByIndexTuple"]

            problem_ix = 0
            for k in problem_id.keys():
                problem_id[k] = problem_ix
                problem_ix += 1

            for team in fetch_res['commonRankings']['commonRankings']:
                if 'studentUser' in team['user'].keys():
                    team_id = team['user']['studentUser']['studentNumber']

                    total_time = team['solvingTime']
                    penalty_num = 0
                    for key in team['problemScores']:
                        _run = team['problemScores'][key]
                        if int(_run['score']) == self.AC_SCORE:
                            total_time -= int(_run['acceptTime'])

                    penalty_num = total_time // (self.contest.penalty // 60)

                    for key in team['problemScores']:
                        # p_id = key
                        p_id = problem_id[key]

                        _run = team['problemScores'][key]
                        timestamp = int(_run['acceptTime']) * 60

                        cnt = int(_run['submitCountSnapshot'])

                        pending_cnt = int(
                            _run['validSubmitCount']) - int(_run['submitCountSnapshot'])

                        submission = Submission()
                        submission.team_id = team_id
                        submission.timestamp = timestamp
                        submission.problem_id = p_id
                        submission.status = constants.RESULT_INCORRECT

                        if cnt > 0:
                            incorrect_num = cnt - 1

                            if int(_run['score']) == self.AC_SCORE:
                                if penalty_num > incorrect_num:
                                    penalty_num -= incorrect_num
                                else:
                                    incorrect_num = penalty_num
                                    penalty_num = 0

                            for i in range(0, incorrect_num):
                                submission.status = constants.RESULT_INCORRECT
                                runs.append(copy.deepcopy(submission))

                            if int(_run['score']) == self.AC_SCORE:
                                submission.status = constants.RESULT_CORRECT

                            runs.append(copy.deepcopy(submission))

                        for i in range(pending_cnt):
                            submission.status = constants.RESULT_PENDING
                            runs.append(copy.deepcopy(submission))

        self.runs = runs
        return self
