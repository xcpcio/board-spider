import typing
import requests
import json
import os

from xcpcio_board_spider import Contest, Team, Teams, Submission, Submissions, utils, constants


class CSG_CPC():
    def __init__(self, contest: Contest, team_uris: typing.List[str], run_uris: typing.List[str]):
        self.contest = contest

        self.team_uris = team_uris
        self.run_uris = run_uris

        self.raw_team_data = []
        self.raw_run_data = []

        self.teams = Teams()
        self.runs = Submissions()

    def fetch_resp_obj(self, uri: str):
        if os.path.exists(uri):
            with open(uri, 'r') as f:
                resp_obj = json.loads(f.read())
        else:
            resp = requests.get(uri, timeout=10)
            resp_obj = json.loads(resp.text)

        if int(resp_obj["code"]) != 200:
            raise RuntimeError("Invalid response")

        return resp_obj

    def fetch(self):
        raw_team_data = []
        raw_run_data = []

        for team_uri in self.team_uris:
            resp_obj = self.fetch_resp_obj(team_uri)
            raw_team_data.extend(resp_obj["data"])

        for run_uri in self.run_uris:
            resp_obj = self.fetch_resp_obj(run_uri)
            raw_run_data.extend(resp_obj["data"])

        self.raw_team_data = raw_team_data
        self.raw_run_data = raw_run_data

        return self

    def parse_teams(self):
        teams = Teams()

        for raw_team in self.raw_team_data:
            team = Team()

            team_id = raw_team["team_id"]

            if team_id in ["admin", "balloon", "printer"] or team_id.startswith("test"):
                continue

            name = raw_team["name"]
            school = raw_team["school"]
            members = raw_team["tmember"].split("、")
            coach = raw_team["coach"]
            kind = int(raw_team["tkind"])

            team.team_id = team_id
            team.name = name
            team.organization = school
            team.members = members
            team.coach = coach

            if kind == 0:
                team.official = True

            if kind == 1:
                team.official = True
                team.girl = True

            if kind == 2:
                team.unofficial = True

            teams[team_id] = team

        self.teams = teams

        return self

    def parse_runs(self):
        runs = Submissions()

        """

        [
            6,
            1001,
            1000,
            "team111",
            6,
            "2023-05-13T15:33:27"
        ],

solution_id
contest_id
problem_id
user_id
result
in_date

        4    =>   Accepted'],
        5    =>    'Presentation Error'],
        6    =>    'Wrong Answer'],
        7    =>   Time Limit Exceed'],
        8    =>   Memory Limit Exceed'],
        9    =>   Output Limit Exceed'],
        10    =>  Runtime Error'],
        11    =>  Compile Error'],
        13    =>  Tested'],
        100    => Unknown'],
        0    =>    'Pending'],
        1    =>    'Pending Rejudging'],
        2    =>    'Compiling'],
        3    =>    'Running&Judging'],
        -1 => 封榜后的未知结果

        CE不罚时，PE罚时
        """

        for raw_run in self.raw_run_data:
            run = Submission()

            submission_id = str(raw_run[0])
            problem_id = int(raw_run[2])
            team_id = str(raw_run[3])
            result = int(raw_run[4])
            in_date = str(raw_run[5]).replace("T", " ")
            timestamp = utils.get_timestamp_second(
                in_date) - self.contest.start_time

            run.submission_id = str(submission_id)
            run.team_id = str(team_id)
            run.problem_id = problem_id
            run.timestamp = timestamp

            if result == 4:
                run.status = constants.RESULT_CORRECT
            elif result in [0, 1, 2, 3, -1]:
                run.status = constants.RESULT_PENDING
            else:
                run.status = constants.RESULT_INCORRECT

            if result in [11, 13, 100]:
                continue

            runs.append(run)

        self.runs = runs

        return self
