from os import path
import os
import json
import time


def json_output(data):
    return json.dumps(data, sort_keys=False, indent=0, separators=(',', ':'), ensure_ascii=False)


def json_input(path):
    with open(path, 'r') as f:
        return json.load(f)


def mkdir(_path):
    if not path.exists(_path):
        os.makedirs(_path)


def get_timestamp(dt):
    # 转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)
    return int(timestamp)


def output(filename, data):
    with open(path.join(data_dir, filename), 'w') as f:
        f.write(json_output(data))


raw_dir = "raw"
data_dir = "../../../../data/provincial-contest/2021/zjcpc"
team_data_filename = "team.json"
run_data_filename = "run.json"
problem_num = 13
problem_id = [chr(ord('A') + i) for i in range(problem_num)]
group = {
    'official': '正式队伍',
    'unofficial': '打星队伍',
    'undergraduate': '本科组',
    'junior': '专科组',
    'highschool': '高中组',
    'girl': '女队',
}
status_time_display = {
    'correct': 1,
    'incorrect': 1,
    'pending': 1,
}
medal = {
    "undergraduate": {
        'gold': 20,
        'silver': 60 - 20,
        'bronze': 118 - 60,
    },
    "junior": {
        'gold': 11,
        'silver': 30 - 11,
        'bronze': 66 - 30,
    }
}
balloon_color = [
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
config = {
    'contest_name': 'The 18th Zhejiang Provincial Collegiate Programming Contest Sponsored by TuSimple',
    'start_time': get_timestamp("2021-4-17 12:00:00"),
    'end_time': get_timestamp("2021-4-17 17:00:00"),
    'frozen_time': 60 * 60,
    'problem_id': problem_id,
    'group': group,
    'organization': 'School',
    'status_time_display': status_time_display,
    'penalty': 20 * 60,
    'medal': medal,
    'balloon_color': balloon_color,
}


def config_out():
    output("config.json", config)


def team_out():
    team_dic = json_input(path.join(raw_dir, team_data_filename))
    team = {}
    for key in team_dic:
        item = team_dic[key]
        team[key] = {}
        new_item = team[key]
        new_item['organization'] = item['school']
        new_item['name'] = item['team']
        members = item['members'].split('、')
        members.sort()
        new_item['members'] = members
        type = item['type'].split(" ")
        if 'unofficial' in type:
            new_item['unofficial'] = 1
        else:
            for tp in type:
                if tp == 'type1':
                    new_item['undergraduate'] = 1
                    new_item['official'] = 1
                elif tp == 'type2':
                    new_item['junior'] = 1
                    new_item['official'] = 1
                elif tp == 'type3':
                    new_item['highschool'] = 1
                elif tp == 'girls':
                    new_item['girl'] = 1
                else:
                    new_item[tp] = 1
    output("team.json", team)


def run_out():
    run_list = json_input(path.join(raw_dir, run_data_filename))
    run = []
    for item in run_list:
        new_item = {}
        new_item['team_id'] = item[0]
        new_item['problem_id'] = problem_id.index(item[1])
        new_item['timestamp'] = (int(item[2] // 1000) // 60) * 60
        status = item[3]
        if status == 'AC':
            new_item['status'] = 'correct'
        elif status == 'NO':
            new_item['status'] = 'incorrect'
        elif status == 'NEW':
            new_item['status'] = 'pending'
        run.append(new_item)
    output("run.json", run)


mkdir(data_dir)
config_out()
team_out()
run_out()
