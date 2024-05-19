import typing
import json

from . import constants


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
                 location: str = None,
                 group: typing.List[str] = None,
                 extra: typing.Dict[str, typing.Any] = None):
        self.team_id = team_id
        self.name = name
        self.organization = organization

        self.members = members
        self.coach = coach

        self.official = official
        self.unofficial = unofficial
        self.girl = girl

        self.location = location

        self.group = group if group is not None else []
        self.extra = extra if extra is not None else {}

    def enable_group(self, group: str):
        if group not in self.group:
            self.group.append(group)

    def disable_group(self, group: str):
        if group in self.group:
            self.group.remove(group)

    @property
    def get_dict(self):
        obj = {}

        obj["team_id"] = self.team_id
        obj["name"] = self.name
        obj["organization"] = self.organization

        if self.members is not None:
            obj["members"] = self.members
        if self.coach is not None:
            obj["coach"] = self.coach

        if self.official is not None and self.official is True:
            self.group.append(constants.TEAM_TYPE_OFFICIAL)
        if self.unofficial is not None and self.unofficial is True:
            self.group.append(constants.TEAM_TYPE_UNOFFICIAL)
        if self.girl is not None and self.girl is True:
            self.group.append(constants.TEAM_TYPE_GIRL)

        if self.location is not None:
            obj["location"] = self.location

        obj["group"] = list(set(self.group))

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)


ITeams = typing.Dict[str, Team]


class Teams(ITeams):
    def __init__(self):
        return

    @property
    def get_dict(self):
        obj = {}

        for k in self.keys():
            obj[k] = self[k].get_dict

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)
