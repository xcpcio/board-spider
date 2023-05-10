import os

from xcpcio_board_spider.spider.domjudge.v2 import DOMjudge

current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


def test_spider_domjudge_v2_2023_hbcpc(snapshot):
    test_prefix = "2023_hbcpc"

    d = DOMjudge()

    d.fetch_uri = os.path.join(
        current_dir_path, "test_data", test_prefix, "Scoreboard HBCPC_2023 - DOMjudge.html")

    d.start_time = "2023-04-30 10:00:00"
    d.end_time = "2023-04-30 15:00:00"

    d.fetch().parse_teams().parse_runs()

    assert len(d.teams) == 197
    assert len(d.runs) == 2759

    snapshot.assert_match(d.teams.get_json, "teams")
    snapshot.assert_match(d.runs.get_json, "runs")


def test_spider_domjudge_v2_47th_ec_final(snapshot):
    test_prefix = "47th_ec_final"

    d = DOMjudge()

    d.fetch_uri = os.path.join(
        current_dir_path, "test_data", test_prefix, "Scoreboard EC-Final - DOMjudge.html")

    d.start_time = "2023-03-25 10:00:00"
    d.end_time = "2023-03-25 15:00:00"

    d.fetch().parse_teams().handle_default_observers_team().parse_runs()

    assert len(d.teams) == 314
    assert len(d.runs) == 4788

    unofficial_cnt = sum(1 for team in d.teams.values() if team.unofficial)
    assert unofficial_cnt == 34

    snapshot.assert_match(d.teams.get_json, "teams")
    snapshot.assert_match(d.runs.get_json, "runs")
