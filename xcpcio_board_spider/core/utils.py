import json
import time
import os

from xcpcio_board_spider import constants, Contest, Submissions


def json_input(path: str) -> None:
    with open(path, 'r') as f:
        return json.load(f)


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def output(target_path, data, if_not_exists=False):
    if if_not_exists and os.path.exists(target_path):
        return

    with open(target_path, 'w') as f:
        f.write(json_output(data))


def ensure_makedirs(_path):
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


def get_cookies(cookies_str: str):
    from http.cookies import SimpleCookie
    cookie = SimpleCookie()
    cookie.load(cookies_str)

    # Even though SimpleCookie is dictionary-like, it internally uses a Morsel object
    # which is incompatible with requests. Manually construct a dictionary instead.
    cookies = {k: v.value for k, v in cookie.items()}

    return cookies


def xls_iterator_per_row(xls_file_path: str):
    import xlrd
    data = xlrd.open_workbook(xls_file_path)
    table = data.sheets()[0]
    nrows = table.nrows

    for i in range(1, nrows):
        yield table.row_values(i)


def frozen_fallback(contest: Contest, submissions: Submissions):
    for s in submissions:
        if s.timestamp >= contest.end_time - contest.start_time - contest.frozen_time:
            s.status = constants.RESULT_PENDING

    return submissions


def get_timestamp_second(dt):
    if str(dt).isdigit():
        return dt

    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)

    return int(timestamp)


def get_now_timestamp_second():
    return int(time.time())
