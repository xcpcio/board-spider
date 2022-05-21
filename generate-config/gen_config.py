import os
import json
import time


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


def get_timestamp(dt):
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return int(timestamp)


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


def generate_problem_label(num):
    return [chr(ord('A') + i) for i in range(num)]


def generate_balloon_color(num):
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

    return default_balloon_color[:num]


data_dir = "./data"

problem_num = 13

group = {
    'official': '正式队伍',
    'unofficial': '打星队伍',
}

status_time_display = {
    'correct': 1,
    'incorrect': 1,
    'pending': 1,
}

medal = {
    "official": {
        'gold': 30,
        'silver': 60,
        'bronze': 90,
    }
}

config = {
    'contest_name': '',
    'start_time': get_timestamp("2021-4-17 12:00:00"),
    'end_time': get_timestamp("2021-4-17 17:00:00"),
    'frozen_time': 60 * 60,
    'problem_id': generate_problem_label(problem_num),
    'group': group,
    'organization': 'School',
    'status_time_display': status_time_display,
    'penalty': 20 * 60,
    'medal': medal,
    'balloon_color': generate_balloon_color(problem_num),
}


mkdir(data_dir)
output(os.path.join(data_dir, "config.json"), config)
output(os.path.join(data_dir, "team.json"), {}, True)
output(os.path.join(data_dir, "run.json"), [], True)
