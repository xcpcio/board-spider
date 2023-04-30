
import typing


class Image:
    def __init__(self, url: str, base64: str):
        self.url = url
        self.base64 = base64


class Color:
    def __init__(self, color: str, background_color: str):
        self.color = color
        self.background_color = background_color


class Contest:
    def __init__(self,
                 contest_name: str,
                 start_time,
                 end_time,
                 frozen_time,
                 penalty,
                 problem_id: typing.List[str],
                 group,
                 organization: str,
                 status_time_display,
                 medal,
                 balloon_color: typing.List[Color],
                 logo: Image):
        self.contest_name = contest_name
        self.start_time = start_time
        self.end_time = end_time
        self.frozen_time = frozen_time
        self.penalty = penalty
        self.problem_id = problem_id
        self.group = group
        self.organization = organization
        self.status_time_display = status_time_display
        self.medal = medal
        self.balloon_color = [Color(**item) for item in balloon_color]
        self.logo = Image(**logo)
