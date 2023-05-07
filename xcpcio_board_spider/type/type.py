import json


class Image:
    def __init__(self, url: str, base64: str):
        self.url = url
        self.base64 = base64

    @property
    def __dict__(self):
        obj = {}

        obj["url"] = self.url
        obj["base64"] = self.base64

        return obj

    @property
    def __json__(self):
        return json.dumps(self.__dict__)


class Color:
    def __init__(self, color: str, background_color: str):
        self.color = color
        self.background_color = background_color

    @property
    def __dict__(self):
        obj = {}

        obj["color"] = self.color
        obj["background_color"] = self.background_color

        return obj

    @property
    def __json__(self):
        return json.dumps(self.__dict__)
