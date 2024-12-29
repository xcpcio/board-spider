import json
import typing

from .constants import *
from .type import *


class Contest:
    def __init__(self,
                 contest_name: str = "",
                 start_time: int = 0,
                 end_time: int = 0,
                 frozen_time: int = 60 * 60,
                 unfrozen_time: int = 0x3f3f3f3f3f3f3f3f,
                 penalty: int = 20 * 60,
                 problem_quantity: int = 0,
                 problem_id: typing.List[str] = [],
                 group: typing.Any = None,
                 organization: str = "School",
                 status_time_display: typing.Any = None,
                 medal: typing.Any = {},
                 balloon_color: typing.List[Color] = None,
                 logo: Image = None,
                 banner: Image = None,
                 banner_mode: str = None,
                 options: ContestOptions = None,
                 ):
        self.contest_name = contest_name
        self.start_time = start_time
        self.end_time = end_time
        self.frozen_time = frozen_time
        self.unfrozen_time = unfrozen_time
        self.penalty = penalty
        self.problem_quantity = problem_quantity
        self.problem_id = problem_id
        self.group = group
        self.organization = organization
        self.status_time_display = status_time_display
        self.medal = medal
        self.options = options

        if self.group is None:
            self.group = {
                TEAM_TYPE_OFFICIAL: TEAM_TYPE_ZH_CN_OFFICIAL,
                TEAM_TYPE_UNOFFICIAL: TEAM_TYPE_ZH_CN_UNOFFICIAL,
            }

        if self.status_time_display is None:
            self.status_time_display = FULL_STATUS_TIME_DISPLAY

        if balloon_color is not None:
            self.balloon_color = [Color(**item) for item in balloon_color]
        else:
            self.balloon_color = None

        if logo is not None:
            self.logo = Image(**logo)
        else:
            self.logo = None

        if banner is not None:
            self.banner = Image(**banner)
        else:
            self.banner = None

        if banner_mode is not None:
            self.banner_mode = banner_mode
        else:
            self.banner_mode = None

        if options is not None:
            self.options = options
        else:
            self.options = ContestOptions()

    def append_balloon_color(self, color: Color):
        if self.balloon_color is None:
            self.balloon_color = []
        self.balloon_color.append(color)
        return self

    def fill_problem_id(self):
        self.problem_id = [chr(ord('A') + i)
                           for i in range(self.problem_quantity)]

        return self

    def fill_balloon_color(self):
        default_balloon_color_list = [
            Color(background_color='rgba(189, 14, 14, 0.7)', color='#fff'),
            Color(background_color='rgba(149, 31, 217, 0.7)', color='#fff'),
            Color(background_color='rgba(16, 32, 96, 0.7)', color='#fff'),
            Color(background_color='rgba(38, 185, 60, 0.7)', color='#000'),
            Color(background_color='rgba(239, 217, 9, 0.7)', color='#000'),
            Color(background_color='rgba(243, 88, 20, 0.7)', color='#fff'),
            Color(background_color='rgba(12, 76, 138, 0.7)', color='#fff'),
            Color(background_color='rgba(156, 155, 155, 0.7)', color='#000'),
            Color(background_color='rgba(4, 154, 115, 0.7)', color='#000'),
            Color(background_color='rgba(159, 19, 236, 0.7)', color='#fff'),
            Color(background_color='rgba(42, 197, 202, 0.7)', color='#000'),
            Color(background_color='rgba(142, 56, 54, 0.7)', color='#fff'),
            Color(background_color='rgba(144, 238, 144, 0.7)', color='#000'),
            Color(background_color='rgba(77, 57, 0, 0.7)', color='#fff'),
        ]

        self.balloon_color = default_balloon_color_list[:self.problem_quantity]

        return self

    @property
    def get_dict(self):
        obj = {}

        obj["contest_name"] = self.contest_name
        obj["start_time"] = self.start_time
        obj["end_time"] = self.end_time
        obj["frozen_time"] = self.frozen_time
        obj["penalty"] = self.penalty
        obj["problem_quantity"] = self.problem_quantity
        obj["problem_id"] = self.problem_id
        obj["group"] = self.group
        obj["organization"] = self.organization
        obj["status_time_display"] = self.status_time_display
        obj["medal"] = self.medal

        if self.balloon_color is not None:
            obj["balloon_color"] = [item.get_dict for item in self.balloon_color]

        if self.logo is not None:
            obj["logo"] = self.logo.get_dict

        if self.banner is not None:
            obj["banner"] = self.banner.get_dict

        if self.banner_mode is not None:
            obj["banner_mode"] = self.banner_mode

        obj["options"] = self.options.get_dict

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)
