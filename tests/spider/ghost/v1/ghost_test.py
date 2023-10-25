import os

from xcpcio_board_spider import Contest, utils
from xcpcio_board_spider.spider.ghost.v1 import Ghost

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def test_spider_ghost_v1_2022_ec_final(snapshot):
    test_prefix = "2022_ec_final"

    c = Contest()
    c.start_time = utils.get_timestamp_second("2023-03-25 09:00:00")
    c.end_time = utils.get_timestamp_second("2023-03-25 14:00:00")

    d = Ghost()
    d.contest = c
    d.fetch_uri = os.path.join(
        current_dir_path, "test_data", test_prefix, "contest.dat")

    d.fetch()
    d.parse_teams()
    d.parse_runs()

    assert len(d.teams) == 314
    assert len(d.runs) == 4842

    snapshot.assert_match(d.teams.get_json, "teams")
    snapshot.assert_match(d.runs.get_json, "runs")
