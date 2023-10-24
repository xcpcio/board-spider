import os

from xcpcio_board_spider import Contest, utils
from xcpcio_board_spider.spider.domjudge.v4 import DOMjudge

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def test_spider_domjudge_v4_2021_ec_final(snapshot):
    test_prefix = "2021_ec_final"

    c = Contest()
    c.start_time = utils.get_timestamp_second("2022-07-20 09:00:00")
    c.end_time = utils.get_timestamp_second("2022-07-20 14:00:00")

    d = DOMjudge()
    d.contest = c
    d.fetch_uri = os.path.join(
        current_dir_path, "test_data", test_prefix, "events.xml")

    d.fetch()
    d.parse_teams()
    d.parse_runs()

    # snapshot.assert_match(d.xml_content, "xml_content")
    # snapshot.assert_match(json.dumps(d.json_dict), "json_content")

    assert len(d.teams) == 367
    assert len(d.runs) == 6785

    snapshot.assert_match(d.teams.get_json, "teams")
    snapshot.assert_match(d.runs.get_json, "runs")
