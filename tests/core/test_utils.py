from xcpcio_board_spider import core


def test_get_timestamp_from_iso8601():
    assert core.utils.get_timestamp_from_iso8601(
        "2024-09-15T05:00:00Z") == 1726376400
    assert core.utils.get_timestamp_from_iso8601(
        "2024-09-15T05:00:00+08:00") == 1726347600
