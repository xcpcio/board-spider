import typing
import json


class Submission:
    def __init__(self,
                 team_id: str = "",
                 problem_id: int = 0,
                 timestamp: int = 0,
                 status: str = "",
                 submission_id: str = None):
        self.team_id = team_id
        self.problem_id = problem_id
        self.timestamp = timestamp
        self.status = status

        self.submission_id = submission_id

    @property
    def __json__(self):
        json_obj = {}

        json_obj["team_id"] = self.team_id
        json_obj["problem_id"] = self.problem_id
        json_obj["timestamp"] = self.timestamp
        json_obj["status"] = self.status

        if self.submission_id is not None:
            json_obj["submission_id"] = self.submission_id

        return json_obj


ISubmissions = typing.List[Submission]


class Submissions(ISubmissions):
    def __init__(self):
        pass

    @property
    def __json__(self):
        return json.dumps(self, default=lambda o: o.__json__)
