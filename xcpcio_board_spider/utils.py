import json
import time
import os
from typing import List


def hello_world():
    return "hello world"


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def output(target_path, data, if_not_exists=False):
    if if_not_exists and os.path.exists(target_path):
        return

    with open(target_path, 'w') as f:
        f.write(json_output(data))


def mkdir(_path):
    if not os.path.exists(_path):
        os.makedirs(_path)


def url_to_base64(url):
    import base64
    import requests as req
    from io import BytesIO

    if os.path.isfile(url):
        f = open(url, 'rb')
        img_data_b64 = base64.b64encode(f.read())
        f.close()
    else:
        response = req.get(url)
        img_data_b64 = base64.b64encode(BytesIO(response.content).read())

    return bytes.decode(img_data_b64)


def get_cookies(raw_cookies: str):
    from http.cookies import SimpleCookie
    cookie = SimpleCookie()
    cookie.load(raw_cookies)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {k: v.value for k, v in cookie.items()}

    return cookies


def read_xls(xls_file_path: str):
    import xlrd
    data = xlrd.open_workbook(xls_file_path)
    table = data.sheets()[0]
    nrows = table.nrows

    for i in range(1, nrows):
        yield table.row_values(i)


def frozen_fallback(runs, frozen_start_timestamp):
    for r in runs:
        if r['timestamp'] >= frozen_start_timestamp:
            r['status'] = 'pending'

    return runs


def get_timestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return int(timestamp)


def generate_problem_label(problem_nums: int) -> List[str]:
    return [chr(ord('A') + i) for i in range(problem_nums)]


def generate_balloon_color(problem_nums: int):
    default_balloon_color = [
        {'background_color': 'rgba(189, 14, 14, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(255, 144, 228, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(255, 255, 255, 0.7)', 'color': '#000'},
        {'background_color': 'rgba(38, 185, 60, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(239, 217, 9, 0.7)', 'color': '#000'},
        {'background_color': 'rgba(243, 88, 20, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(12, 76, 138, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(156, 155, 155, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(4, 154, 115, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(159, 19, 236, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(42, 197, 202, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(142, 56, 54, 0.7)', 'color': '#fff'},
        {'background_color': 'rgba(0, 0, 0, 0.7)', 'color': '#fff'},
    ]

    return default_balloon_color[:problem_nums]
