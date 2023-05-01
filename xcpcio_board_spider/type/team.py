import typing


class Team:
    def __init__(self,
                 team_id: str,
                 name: str,
                 organization: str,
                 members: typing.List[str],
                 coach: str,
                 official: bool = False,
                 unofficial: bool = False,
                 girl: bool = False):
        self.team_id = team_id
        self.name = name
        self.organization = organization
        self.members = members
        self.coach = coach

        self.official = official
        self.unofficial = unofficial
        self.girl = girl


ITeams = typing.Dict[str, Team]


class Teams(ITeams):
    pass
