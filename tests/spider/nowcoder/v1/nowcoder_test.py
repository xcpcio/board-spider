import os

from xcpcio_board_spider import Contest, utils
from xcpcio_board_spider.spider.nowcoder.v1 import NowCoder

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def test_spider_nowcoder_v1_2023_gxcpc_warmup(snapshot):
    c = Contest()
    c.start_time = utils.get_timestamp_second("2023-06-03 15:00:00")
    c.end_time = utils.get_timestamp_second("2023-06-03 17:00:00")

    if os.getenv("ENABLE_REMOTE_TEST") != "true":
        return

    n = NowCoder(c, 59039)

    n.fetch().parse_teams().parse_runs()

    assert len(n.teams) == 150
    assert len(n.runs) == 1019

    snapshot.assert_match(n.teams.get_json, "teams")
    snapshot.assert_match(n.runs.get_json, "runs")