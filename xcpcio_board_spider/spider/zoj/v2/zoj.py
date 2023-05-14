import requests
import execjs
import json
import os

from xcpcio_board_spider import Contest, Team, Teams, Submission, Submissions, utils, constants


class ZOJ:
    CONSTANT_TEAM_TYPE = "type"

    def __init__(self, contest: Contest, fetch_uri_prefix: str):
        self.contest = contest
        self.fetch_uri_prefix = fetch_uri_prefix

        self.raw_teams_data = None
        self.raw_runs_data = None

        self.teams = Teams()
        self.runs = Submissions()

    @staticmethod
    def get_team_type(team: Team):
        if team.extra[ZOJ.CONSTANT_TEAM_TYPE] is None:
            team.extra[ZOJ.CONSTANT_TEAM_TYPE] = []

        return team.extra[ZOJ.CONSTANT_TEAM_TYPE]

    def get_js_object(self, js_code: str, key: str):
        text = js_code.lstrip("var {} =".format(key)).rstrip(";\n ")
        text = "JSON.stringify(" + text + ")"
        text = execjs.eval(text)

        return json.loads(text)

    def fetch(self):
        data = {}

        for key in ["teams", "runs"]:
            fetch_uri = "/".join([self.fetch_uri_prefix, key + ".js",])

            if os.path.exists(fetch_uri):
                with open(fetch_uri, "r") as f:
                    data[key] = self.get_js_object(f.read(), key)
            else:
                params = {
                    '__timestamp__': utils.get_now_timestamp_second(),
                }
                response = requests.get(fetch_uri, params=params)

                data[key] = self.get_js_object(response.text, key)

        self.raw_teams_data = data["teams"]
        self.raw_runs_data = data["runs"]

        return self

    def parse_teams(self):
        teams = Teams()
        for team_id, raw_team in self.raw_teams_data.items():
            if team_id == "et_number":
                continue

            team = Team()

            teams[team_id] = team

            team.team_id = team_id
            team.name = raw_team["team"]
            team.organization = raw_team["school"]
            team.members = raw_team["members"].split("、")
            team.members.sort()

            type = raw_team["type"].split(" ")
            team.extra[self.CONSTANT_TEAM_TYPE] = type

        self.teams = teams

        return self

    def parse_runs(self):
        runs = Submissions()

        for raw_run in self.raw_runs_data:
            run = Submission()

            run.team_id = raw_run[0]
            run.problem_id = ord(raw_run[1]) - ord('A')
            run.timestamp = (int(raw_run[2] // 1000) // 60) * 60

            status = raw_run[3]
            if status == "AC":
                run.status = constants.RESULT_CORRECT
            elif status == "NO":
                run.status = constants.RESULT_INCORRECT
            elif status == "NEW":
                run.status = constants.RESULT_PENDING

            runs.append(run)

        self.runs = runs

        return self
