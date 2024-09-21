from xcpcio_board_spider import core


def test_logger():
    l = core.logger.init_logger()
    assert (l is not None) == True
