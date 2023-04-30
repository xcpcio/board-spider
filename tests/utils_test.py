import xcpcio_board_spider.utils as utils


def test_hello_world():
    assert utils.hello_world() == "hello world"


def test_generate_problem_label():
    assert utils.generate_problem_label(1) == ["A"]
    assert utils.generate_problem_label(
        15) == ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
