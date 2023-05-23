from xcpcio_board_spider.type import Contest, Team, Teams, Submission, Submissions, constants

from domjudge_utility import Dump, DumpConfig


class DOMjudge():
    CONSTANT_EXTRA_DOMJUDGE_TEAM = "domjudge_team"

    def __init__(self,
                 contest: Contest = None,
                 fetch_uri: str = None):
        self.contest = contest
        self.fetch_uri = fetch_uri

        self.dump_config = DumpConfig()
        self.dump_config.base_file_path = self.fetch_uri

        self.dump = Dump(self.dump_config)

        self.teams = Teams()
        self.submissions = Submissions()

    def fetch(self):
        self.dump.load_domjudge_api()

        return self

    def get_submission_timestamp_millisecond(self, time_str: str):
        from datetime import datetime

        time_obj = datetime.strptime(time_str, '%H:%M:%S.%f')

        hour = time_obj.hour
        minute = time_obj.minute
        second = time_obj.second
        millisecond = time_obj.microsecond // 1000

        return (hour * 3600 + minute * 60 + second) * 1000 + millisecond

    def parse_teams(self):
        self.teams = Teams()

        for d_team in self.dump.teams:
            team = Team()

            team_id = d_team["id"]
            name = d_team["display_name"]
            organization = d_team["affiliation"]

            team.team_id = team_id
            team.name = name
            team.organization = organization
            team.extra[DOMjudge.CONSTANT_EXTRA_DOMJUDGE_TEAM] = d_team

            self.teams[team_id] = team

        return self

    def parse_runs(self):
        self.runs = Submissions()

        for s in self.dump.submissions:
            submission = Submission()

            team_id = s["team_id"]
            submission_id = s["id"]
            problem_id = s["problem_id"]
            contest_time = s["contest_time"]

            # ignore submissions that are not submit after contest start
            if contest_time.startswith("-"):
                continue

            timestamp = self.get_submission_timestamp_millisecond(
                contest_time) // 1000 // 60 * 60

            if timestamp > self.contest.end_time - self.contest.start_time:
                continue

            verdict = s["verdict"]

            submission.team_id = team_id
            submission.submission_id = submission_id
            submission.timestamp = timestamp

            if verdict == "CE":
                continue

            if verdict == "AC":
                submission.status = constants.RESULT_CORRECT
            elif verdict == "PD":
                submission.status = constants.RESULT_PENDING
            else:
                submission.status = constants.RESULT_INCORRECT

            p = self.dump.problems_dict[problem_id]
            submission.problem_id = p["ordinal"]

            self.runs.append(submission)

        return self
