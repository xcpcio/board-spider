import typing
import json


class Team:
    def __init__(self,
                 team_id: str = "",
                 name: str = "",
                 organization: str = "",
                 members: typing.List[str] = None,
                 coach: str = None,
                 official: bool = False,
                 unofficial: bool = False,
                 girl: bool = False,
                 extra: typing.Dict[str, typing.Any] = {}):
        self.team_id = team_id
        self.name = name
        self.organization = organization

        self.members = members
        self.coach = coach

        self.official = official
        self.unofficial = unofficial
        self.girl = girl

        self.extra = extra

    @property
    def __json__(self):
        json_string = {}

        json_string["team_id"] = self.team_id
        json_string["name"] = self.name
        json_string["organization"] = self.organization

        if self.members is not None:
            json_string["members"] = self.members
        if self.coach is not None:
            json_string["coach"] = self.coach

        if self.official is not None:
            json_string["official"] = self.official
        if self.unofficial is not None:
            json_string["unofficial"] = self.unofficial
        if self.girl is not None:
            json_string["girl"] = self.girl

        return json_string


ITeams = typing.Dict[str, Team]


class Teams(ITeams):
    def __init__(self):
        pass

    @property
    def __json__(self):
        return json.dumps(self, default=lambda o: o.__json__)
