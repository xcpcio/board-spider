import os

from xcpcio_board_spider import Contest, utils
from xcpcio_board_spider.spider.domjudge.v3 import DOMjudge

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def test_spider_domjudge_v3_9th_ccpc_guilin(snapshot):
    test_prefix = "9th_ccpc_guilin"

    c = Contest()
    c.start_time = utils.get_timestamp_second("2023-10-29 09:00:00")
    c.end_time = utils.get_timestamp_second("2023-10-29 14:00:00")

    fetch_uri = os.path.join(current_dir_path, "test_data", test_prefix)

    d = DOMjudge(c, fetch_uri)
    d.fetch().parse_teams().parse_runs().update_contest()

    assert len(d.teams) == 270
    assert len(d.runs) == 3360

    snapshot.assert_match(d.contest.get_json, "contest")
    snapshot.assert_match(d.teams.get_json, "teams")
    snapshot.assert_match(d.runs.get_json, "runs")
