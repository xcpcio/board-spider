import xcpcio_board_spider as board


def test_fill_problem_id():
    c = board.Contest()

    c.problem_quantity = 1
    c.fill_problem_id()
    assert len(c.problem_id) == c.problem_quantity
    assert c.problem_id == ["A"]

    c.problem_quantity = 15
    c.fill_problem_id()
    assert len(c.problem_id) == c.problem_quantity
    assert c.problem_id == ["A", "B", "C", "D", "E",
                            "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]


def test_fill_balloon_color():
    c = board.Contest()

    c.problem_quantity = 10
    c.fill_balloon_color()
    assert len(c.balloon_color) == c.problem_quantity
    assert c.balloon_color[0].color == "#fff"
    assert c.balloon_color[0].background_color == "rgba(189, 14, 14, 0.7)"


def test_contest_json(snapshot):
    c = board.Contest()

    c.contest_name = "test_name"

    snapshot.assert_match(c.get_json, "test_contest")


def test_contest_options(snapshot):
    c = board.Contest()

    o = board.ContestOptions()
    o.calculation_of_penalty = board.constants.CALCULATION_OF_PENALTY_ACCUMULATE_IN_SECONDS_AND_FINALLY_TO_THE_MINUTE

    c.options = o

    snapshot.assert_match(c.get_json, "test_contest_options")
