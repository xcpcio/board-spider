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

        return resp_obj

    def fetch(self):
        raw_team_data = []
        raw_run_data = []

        for team_uri in self.team_uris:
            resp_obj = self.fetch_resp_obj(team_uri)
            raw_team_data.extend(resp_obj)

        for run_uri in self.run_uris:
            resp_obj = self.fetch_resp_obj(run_uri)
            raw_run_data.extend(resp_obj)

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
            coach = str(raw_team["coach"])
            kind = int(raw_team["tkind"])
            room = str(raw_team["room"])

            team.team_id = team_id
            team.name = name
            team.organization = school
            team.members = members
            team.coach = coach

            if len(room) > 0:
                team.location = room

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

    def parse_result(self, result: int):
        """
        4    => 'Accepted',
        5    => 'Presentation Error',
        6    => 'Wrong Answer',
        7    => 'Time Limit Exceed',
        8    => 'Memory Limit Exceed',
        9    => 'Output Limit Exceed',
        10   => 'Runtime Error',
        11   => 'Compile Error',
        13   => 'Tested',
        100  => 'Unknown',
        0    => 'Pending',
        1    => 'Pending Rejudging',
        2    => 'Compiling',
        3    => 'Running&Judging',
        -1   => 'Frozen',

        CE 不罚时, PE 罚时
        """

        if result == 4:
            return constants.RESULT_ACCEPTED

        if result == 5:
            return constants.RESULT_PRESENTATION_ERROR

        if result == 6:
            return constants.RESULT_WRONG_ANSWER

        if result == 7:
            return constants.RESULT_TIME_LIMIT_EXCEEDED

        if result == 8:
            return constants.RESULT_MEMORY_LIMIT_EXCEEDED

        if result == 9:
            return constants.RESULT_OUTPUT_LIMIT_EXCEEDED

        if result == 10:
            return constants.RESULT_RUNTIME_ERROR

        if result == 11:
            return constants.RESULT_COMPILATION_ERROR

        if result == 13:
            return constants.RESULT_UNDEFINED

        if result == 100:
            return constants.RESULT_UNKNOWN

        if result == 0:
            return constants.RESULT_PENDING

        if result == 1:
            return constants.RESULT_JUDGING

        if result == 2:
            return constants.RESULT_COMPILING

        if result == 3:
            return constants.RESULT_JUDGING

        if result == -1:
            return constants.RESULT_FROZEN

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
        """

        for raw_run in self.raw_run_data:
            run = Submission()

            submission_id = str(raw_run["solution_id"])
            problem_id = int(raw_run["problem_id"])
            team_id = str(raw_run["user_id"]).split("_")[-1]
            result = int(raw_run["result"])
            in_date = str(raw_run["in_date"]).replace("T", " ")
            timestamp = utils.get_timestamp_second(
                in_date) - self.contest.start_time

            run.submission_id = str(submission_id)
            run.team_id = str(team_id)
            run.problem_id = problem_id
            run.timestamp = timestamp

            run.status = self.parse_result(result)

            runs.append(run)

        self.runs = runs

        return self
