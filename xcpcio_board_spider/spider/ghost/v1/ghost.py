import os
import requests

from xcpcio_board_spider.core import utils
from xcpcio_board_spider.type import Contest, Team, Teams, Submission, Submissions, constants

'''
For CodeForces Ghost
'''


class Ghost:
    def __init__(self,
                 contest: Contest = None,
                 fetch_uri: str = None):
        self.contest = contest
        self.fetch_uri = fetch_uri

        self.ghost_content = ""

        self.teams = Teams()
        self.runs = Submissions()

    def fetch(self):
        ghost_content = ""

        if os.path.exists(self.fetch_uri):
            with open(self.fetch_uri, 'r') as f:
                ghost_content = f.read()
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
                    ghost_content = resp.content.decode(charset)
                else:
                    ghost_content = resp.content.decode()
            else:
                raise RuntimeError(
                    "fetch failed. [status_code=%s]" % resp.status_code)

        self.ghost_content = ghost_content.split("\n")

        return self

    def parse_result(self, result: str):
        if result == "OK":
            return constants.RESULT_ACCEPTED

        if result == "WA":
            return constants.RESULT_WRONG_ANSWER

        if result == "RJ":
            return constants.RESULT_REJECTED

        if result == "PE":
            return constants.RESULT_PRESENTATION_ERROR

        if result == "ML":
            return constants.RESULT_MEMORY_LIMIT_EXCEEDED

        if result == "OL":
            return constants.RESULT_OUTPUT_LIMIT_EXCEEDED

        if result == "RT":
            return constants.RESULT_RUNTIME_ERROR

        if result == "TL":
            return constants.RESULT_TIME_LIMIT_EXCEEDED

        if result == "CE":
            return constants.RESULT_COMPILATION_ERROR

        return constants.RESULT_UNKNOWN

    def parse_teams(self):
        self.teams = Teams()

        for line in self.ghost_content:
            if not line.startswith("@t "):
                continue

            team = Team()

            line = line[3:]
            line = line.split(',')

            team_id = str(line[0])
            name = str(line[-1][1:-1])

            team.team_id = team_id
            team.name = name

            self.teams[team_id] = team

        return self

    def parse_runs(self):
        self.runs = Submissions()

        index = 0
        for line in self.ghost_content:
            if not line.startswith("@s "):
                continue

            submission = Submission()

            index += 1

            line = line[3:]
            line = line.split(',')

            team_id = str(line[0])
            submission_id = str(index)
            problem_id = ord(str(line[1])) - ord('A')
            timestamp = int(line[3])
            result = str(line[4])

            submission.team_id = team_id
            submission.submission_id = submission_id
            submission.problem_id = problem_id
            submission.timestamp = timestamp
            submission.status = self.parse_result(result)

            self.runs.append(submission)

        return self
