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
    def get_dict(self):
        obj = {}

        obj["team_id"] = self.team_id
        obj["problem_id"] = self.problem_id
        obj["timestamp"] = self.timestamp
        obj["status"] = self.status

        if self.submission_id is not None:
            obj["submission_id"] = self.submission_id

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)


ISubmissions = typing.List[Submission]


class Submissions(ISubmissions):
    def __init__(self):
        return

    @property
    def get_dict(self):
        return [item.get_dict for item in self]

    @property
    def get_json(self):
        return json.dumps(self.get_dict)
