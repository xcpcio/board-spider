class Image:
    def __init__(self, url: str, base64: str):
        self.url = url
        self.base64 = base64


class Color:
    def __init__(self, color: str, background_color: str):
        self.color = color
        self.background_color = background_color
