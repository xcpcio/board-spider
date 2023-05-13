import os

from xcpcio_board_spider import Contest
from xcpcio_board_spider.spider.zoj.v2 import ZOJ

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def test_spider_zoj_v2_8th_ccpc_final(snapshot):
    test_prefix = "8th_ccpc_final_warmup"
    fetch_uri_prefix = os.path.join(
        current_dir_path, "test_data", test_prefix)

    c = Contest()
    z = ZOJ(c, fetch_uri_prefix)

    z.fetch().parse_teams().parse_runs()

    assert len(z.teams) == 132
    assert len(z.runs) == 946

    snapshot.assert_match(z.teams.get_json, "teams")
    snapshot.assert_match(z.runs.get_json, "runs")
