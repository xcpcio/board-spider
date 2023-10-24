import os
import math
import requests
import xmltodict

from xcpcio_board_spider.core import utils
from xcpcio_board_spider.type import Contest, Team, Teams, Submission, Submissions, constants

'''
For DOMjudge 6.1.3 events.xml
'''


class DOMjudge:
    def __init__(self,
                 contest: Contest = None,
                 fetch_uri: str = None):
        self.contest = contest
        self.fetch_uri = fetch_uri

        self.xml_content = ""
        self.json_content = ""

        self.teams = Teams()
        self.runs = Submissions()

    def fetch(self):
        xml_content = ""

        if os.path.exists(self.fetch_uri):
            with open(self.fetch_uri, 'r') as f:
                xml_content = f.read()
        else:
            params = {
                '__timestamp__': utils.get_now_timestamp_second()
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }

            resp = requests.get(self.fetch_uri, params=params,
                                headers=headers, timeout=5)

            if resp.status_code == 200:
                content_type = resp.headers.get("Content-Type")

                if "charset" in content_type:
                    charset = content_type.split("charset=")[1]
                    xml_content = resp.content.decode(charset)
                else:
                    xml_content = resp.content.decode()
            else:
                raise RuntimeError(
                    "fetch failed. [status_code=%s]" % resp.status_code)

        self.xml_content = xml_content
        self.json_dict = xmltodict.parse(self.xml_content)

        return self

    def parse_result(self, result: str):
        if result == "AC":
            return constants.RESULT_ACCEPTED

        if result == "WA" or result == "NO":
            return constants.RESULT_WRONG_ANSWER

        if result == "CE":
            return constants.RESULT_COMPILATION_ERROR

        if result == "PE":
            return constants.RESULT_PRESENTATION_ERROR

        if result == "MLE":
            return constants.RESULT_MEMORY_LIMIT_EXCEEDED

        if result == "OLE":
            return constants.RESULT_OUTPUT_LIMIT_EXCEEDED

        if result == "RTE":
            return constants.RESULT_RUNTIME_ERROR

        if result == "TLE":
            return constants.RESULT_TIME_LIMIT_EXCEEDED

        return constants.RESULT_UNKNOWN

    def parse_teams(self):
        self.teams = Teams()

        for d_team in self.json_dict["contest"]["team"]:
            team = Team()

            team_id = str(d_team["id"])
            name = str(d_team["name"])
            organization = str(d_team["university"])

            team.team_id = team_id
            team.name = name
            team.organization = organization

            self.teams[team_id] = team

        return self

    def parse_runs(self):
        self.runs = Submissions()

        for s in self.json_dict["contest"]["run"]:
            submission = Submission()

            judged = bool(s["judged"])
            if judged == False:
                continue

            team_id = str(s["team"])
            submission_id = str(s["id"])
            problem_id = int(s["problem"]) - 1
            timestamp = int(math.floor(float(s["time"])))

            if timestamp < 0 or timestamp > self.contest.end_time - self.contest.start_time:
                continue

            result = str(s["result"])

            submission.team_id = team_id
            submission.submission_id = submission_id
            submission.problem_id = problem_id
            submission.timestamp = timestamp
            submission.status = self.parse_result(result)

            self.runs.append(submission)

        return self
