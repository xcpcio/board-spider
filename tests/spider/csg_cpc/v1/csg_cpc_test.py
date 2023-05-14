import os

from xcpcio_board_spider import Contest, utils
from xcpcio_board_spider.spider.csg_cpc.v1 import CSG_CPC

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)

team_uris = [
    os.path.join(current_dir_path, "test_data/2023_gdcpc/team_list_1004.json"),
    os.path.join(current_dir_path, "test_data/2023_gdcpc/team_list_1005.json"),
]

run_uris = [
    os.path.join(current_dir_path, "test_data/2023_gdcpc/run_list_1004.json"),
    os.path.join(current_dir_path, "test_data/2023_gdcpc/run_list_1005.json"),
]


def test_spider_csg_cpc_v1_2023_gdcpc(snapshot):
    c = Contest()
    c.start_time = utils.get_timestamp_second("2023-05-14 10:00:00")
    c.end_time = utils.get_timestamp_second("2023-05-14 15:00:00")

    csg_cpc = CSG_CPC(c, team_uris, run_uris)
    csg_cpc.fetch().parse_teams().parse_runs()

    assert len(csg_cpc.teams) == 302
    assert len(csg_cpc.runs) == 4381

    snapshot.assert_match(csg_cpc.teams.get_json, "teams")
    snapshot.assert_match(csg_cpc.runs.get_json, "runs")
