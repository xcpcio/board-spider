import json
import logging
import os
import time
from pathlib import Path
from typing import Dict

import requests

from xcpcio_board_spider import Contest, Submissions, Teams, constants

logger = logging.getLogger(__name__)


def json_input(path: str) -> None:
    with open(path, 'r') as f:
        return json.load(f)


def json_output(data):
    return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def output(target_path: Path, data: str, if_not_exists=False):
    if if_not_exists and os.path.exists(target_path):
        return

    with open(target_path, 'w') as f:
        f.write(json_output(data))


def ensure_makedirs(_path: Path):
    if not os.path.exists(_path):
        os.makedirs(_path)


def url_to_base64(url):
    import base64
    from io import BytesIO

    import requests as req

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


def get_timestamp_from_iso8601(dt):
    from datetime import datetime
    datetime_obj = datetime.fromisoformat(dt)
    timestamp = datetime_obj.timestamp()
    return int(timestamp)


def get_now_timestamp_second():
    return int(time.time())


def upload_to_xcpcio(token: str, files: Dict[str, str], url: str = "https://board-admin.xcpcio.com/upload-board-data"):
    payload = {
        "token": token,
        "extra_files": files,
    }
    headers = {
        "content-type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers)
    total_size = len(json.dumps(payload))

    if resp.status_code == 200:
        logger.info("upload successful. [resp={}] [size={}]".format(
            resp.content, total_size))
    else:
        logger.error("upload failed. [status_code={}] [resp={}] [size={}]".format(
            resp.status_code, resp.text, total_size))

    return resp


def save_to_disk(data_dir: Path, c: Contest, teams: Teams, runs: Submissions, if_not_exists=False):
    logger.info("save to disk. [data_dir={}]".format(data_dir))

    ensure_makedirs(data_dir)
    output(data_dir / "config.json", c.get_dict)
    output(data_dir / "team.json", teams.get_dict, if_not_exists=if_not_exists)
    output(data_dir / "run.json", runs.get_dict, if_not_exists=if_not_exists)
