import json


class Image:
    def __init__(self, url: str = None, base64: str = None):
        self.url = url
        self.base64 = base64

    @property
    def get_dict(self):
        obj = {}

        if self.url is not None:
            obj['url'] = self.url

        if self.base64 is not None:
            obj['base64'] = self.base64

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)


class Color:
    def __init__(self, color: str, background_color: str):
        self.color = color
        self.background_color = background_color

    @property
    def get_dict(self):
        obj = {}

        obj["color"] = self.color
        obj["background_color"] = self.background_color

        return obj

    @property
    def get_json(self):
        return json.dumps(self.get_dict)
