import json
import os
import re
import typing

import requests

from xcpcio_board_spider import (
    Contest,
    Submission,
    Submissions,
    Team,
    Teams,
    constants,
    utils,
)


class CSG_CPC():
    def __init__(self, contest: Contest,
                 fetch_uri: str = None):
        self.contest = contest
        self.fetch_uri = fetch_uri

        self.raw_problem_data = []
        self.raw_problem_map = {}
        self.raw_contest_data = {}
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

            if resp.status_code != 200:
                raise RuntimeError(
                    "fetch failed. [status_code=%s]" % resp.status_code)

            resp_obj = json.loads(resp.text)

        return resp_obj

    def fetch(self):
        raw_problem_data = []
        raw_team_data = []
        raw_run_data = []

        resp_obj = self.fetch_resp_obj(self.fetch_uri + "/contest.json")
        self.raw_contest_data = resp_obj

        resp_obj = self.fetch_resp_obj(self.fetch_uri + "/problem.json")
        raw_problem_data.extend(resp_obj)

        resp_obj = self.fetch_resp_obj(self.fetch_uri + "/team.json")
        raw_team_data.extend(resp_obj)

        resp_obj = self.fetch_resp_obj(self.fetch_uri + "/solution.json")
        raw_run_data.extend(resp_obj)

        self.raw_problem_data = raw_problem_data
        self.raw_team_data = raw_team_data
        self.raw_run_data = raw_run_data

        for p in self.raw_problem_data:
            self.raw_problem_map[p["problem_id"]] = p

        for r in self.raw_run_data:
            problem_id = r["problem_id"]
            r["problem_id"] = self.raw_problem_map[problem_id]["num"]

        return self

    def get_timestamp_from_date(self, dt):
        return utils.get_timestamp_from_iso8601(dt.replace(" ", "T") + "+08:00")

    def parse_teams(self):
        teams = Teams()

        for raw_team in self.raw_team_data:
            team = Team()

            team_id = raw_team["team_id"]

            if team_id in ["admin", "balloon", "printer"] or team_id.startswith("test"):
                continue

            name = raw_team["name"]
            school = raw_team["school"]

            members = re.split(r'[,、\s]+', raw_team["tmember"])
            members = [member.strip() for member in members]

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
        for raw_run in self.raw_run_data:
            run = Submission()

            submission_id = str(raw_run["solution_id"])
            problem_id = int(raw_run["problem_id"])
            team_id = str(raw_run["user_id"]).split("_")[-1]
            result = int(raw_run["result"])
            in_date = str(raw_run["in_date"]).replace("T", " ")
            timestamp = self.get_timestamp_from_date(
                in_date) - self.contest.start_time

            run.submission_id = str(submission_id)
            run.team_id = str(team_id)
            run.problem_id = problem_id
            run.timestamp = timestamp

            run.status = self.parse_result(result)

            runs.append(run)

        self.runs = runs

        return self

    def update_contest(self):
        start_time = self.raw_contest_data["start_time"]
        end_time = self.raw_contest_data["end_time"]
        frozen_minute = self.raw_contest_data["frozen_minute"]

        self.contest.start_time = self.get_timestamp_from_date(start_time)
        self.contest.end_time = self.get_timestamp_from_date(end_time)
        self.contest.frozen_time = int(frozen_minute) * 60
        self.contest.problem_quantity = len(self.raw_problem_data)
        self.contest.fill_problem_id().fill_balloon_color()

        return self
