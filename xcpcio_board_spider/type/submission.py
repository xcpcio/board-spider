import json
from typing import List, Optional

from .type import Reaction


class Submission:
    def __init__(self,
                 status: str = "",
                 team_id: str = "",
                 problem_id: int = 0,
                 timestamp: int = 0,
                 time: Optional[int] = None,
                 language: Optional[str] = None,
                 submission_id: Optional[str] = None,
                 reaction: Optional[Reaction] = None):
        self.status = status
        self.team_id = team_id
        self.problem_id = problem_id
        self.timestamp = timestamp

        self.time = time
        self.language = language
        self.submission_id = submission_id
        self.reaction = reaction

    @property
    def get_dict(self):
        obj = {}

        obj["status"] = self.status
        obj["team_id"] = self.team_id
        obj["problem_id"] = self.problem_id
        obj["timestamp"] = self.timestamp

        if self.time is not None:
            obj["time"] = self.time

        if self.language is not None:
            obj["language"] = self.language

        if self.submission_id is not None:
            obj["submission_id"] = self.submission_id

        if self.reaction is not None:
            obj["reaction"] = self.reaction.get_dict

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)


ISubmissions = List[Submission]


class Submissions(ISubmissions):
    def __init__(self):
        return

    @property
    def get_dict(self):
        return [item.get_dict for item in self]

    @property
    def get_json(self):
        return json.dumps(self.get_dict)
