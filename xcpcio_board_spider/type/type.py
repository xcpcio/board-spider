import json
import typing
from typing import Optional


class Image:
    def __init__(self, url: str = None, base64: str = None, preset: str = None):
        self.url = url
        self.base64 = base64
        self.preset = preset

    @property
    def get_dict(self):
        obj = {}

        if self.url is not None:
            obj["url"] = self.url

        if self.base64 is not None:
            obj["base64"] = self.base64

        if self.preset is not None:
            obj["preset"] = self.preset

        return obj

    def from_dict(self, d: typing.Any):
        if "url" in d.keys():
            self.url = d["url"]

        if "base64" in d.keys():
            self.base64 = d["base64"]

        if "preset" in d.keys():
            self.preset = d["preset"]

    @property
    def get_json(self):
        return json.dumps(self.get_dict)

    def from_json(self, json_string: str):
        self.from_dict(json.loads(json_string))


class Color:
    def __init__(self, color: str, background_color: str):
        self.color = color
        self.background_color = background_color

    def __eq__(self, other):
        return (
            self.color == other.color
            and self.background_color == other.background_color
        )

    @property
    def get_dict(self):
        obj = {}

        obj["color"] = self.color
        obj["background_color"] = self.background_color

        return obj

    def from_dict(self, d: typing.Any):
        if "color" in d.keys():
            self.color = d["color"]

        if "background_color" in d.keys():
            self.background_color = d["background_color"]

    @property
    def get_json(self):
        return json.dumps(self.get_dict)

    def from_json(self, json_string: str):
        self.from_dict(json.loads(json_string))


class ContestOptions:
    def __init__(
        self,
        calculation_of_penalty: Optional[str] = None,
        submission_timestamp_unit: Optional[str] = None,
        has_reaction_videos: Optional[bool] = None,
        reaction_video_url_template: Optional[str] = None,
    ):
        self.calculation_of_penalty = calculation_of_penalty
        self.submission_timestamp_unit = submission_timestamp_unit
        self.has_reaction_videos = has_reaction_videos
        self.reaction_video_url_template = reaction_video_url_template

    @property
    def get_dict(self):
        obj = {}

        if self.calculation_of_penalty is not None:
            obj["calculation_of_penalty"] = self.calculation_of_penalty

        if self.submission_timestamp_unit is not None:
            obj["submission_timestamp_unit"] = self.submission_timestamp_unit

        if self.has_reaction_videos is not None:
            obj["has_reaction_videos"] = self.has_reaction_videos

        if self.reaction_video_url_template is not None:
            obj["reaction_video_url_template"] = self.reaction_video_url_template

        return obj

    def from_dict(self, d: typing.Any):
        if "calculation_of_penalty" in d.keys():
            self.color = d["calculation_of_penalty"]

        if "submission_timestamp_unit" in d.keys():
            self.submission_timestamp_unit = d["submission_timestamp_unit"]

        if "has_reaction_videos" in d.keys():
            self.has_reaction_videos = d["has_reaction_videos"]

        if "reaction_video_url_template" in d.keys():
            self.reaction_video_url_template = d["reaction_video_url_template"]

    @property
    def get_json(self):
        return json.dumps(self.get_dict)

    def from_json(self, json_string: str):
        self.from_dict(json.loads(json_string))


class Reaction:
    def __init__(self, url: typing.Optional[str] = None):
        self.url = url

    @property
    def get_dict(self):
        obj = {}

        if self.url is not None:
            obj["url"] = self.url

        return obj

    def from_dict(self, d: typing.Dict):
        if "url" in d.keys():
            self.url = d["url"]

    @property
    def get_json(self):
        return json.dumps(self.get_dict)

    def from_json(self, json_string: str):
        self.from_dict(json.loads(json_string))
