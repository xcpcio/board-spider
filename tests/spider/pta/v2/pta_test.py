from datetime import datetime, timezone

from xcpcio_board_spider import constants
from xcpcio_board_spider.spider.pta.v2.pta import PTA
from xcpcio_board_spider.type import Color, Contest, Submissions, Team


def test_parse_groups():
    test_data = {
        "total": 1,
        "groups": [
            {"id": "1833442550973878272", "fid": "1", "name": "正式"}
        ]
    }

    contest = Contest()
    pta = PTA(contest, "1222")
    pta._parse_groups(test_data)
    group = contest.group
    assert len(group) == 1
    assert group["1"] == "正式"


def test_parse_contest():
    contest = Contest()
    pta = PTA(contest, "1222")
    test_data = {
        "total": 1,
        "xcpcRankings": {
            "rankings": [
                {
                    "rank": 1,
                    "totalScore": 0,
                    "penaltyTime": 180,
                    "solvingTime": 1319,
                    "solvedCount": 10,
                    "schoolRank": 1,
                    "problemSubmissionDetailsByProblemSetProblemId": {
                        "1834757673898389504": {
                            "score": 300,
                            "validSubmitCount": 2,
                            "acceptTime": 47,
                            "submitCountSnapshot": 2
                        },
                        "1834757673898389505": {
                            "score": 300,
                            "validSubmitCount": 2,
                            "acceptTime": 216,
                            "submitCountSnapshot": 2
                        },
                        "1834757673898389506": {
                            "score": 300,
                            "validSubmitCount": 1,
                            "acceptTime": 25,
                            "submitCountSnapshot": 1
                        },
                        "1834757673898389507": {
                            "score": 0,
                            "validSubmitCount": 1,
                            "acceptTime": -1,
                            "submitCountSnapshot": 1
                        },
                    },
                    "updateAt": "2024-09-15T10:04:28Z",
                    "competitionId": "1831362571373408256",
                    "teamInfo": {
                        "memberNames": [
                            "程思元",
                            "戚朗瑞",
                            "魏佳泽"
                        ],
                        "teamName": "击中月亮",
                        "schoolName": "清华大学",
                        "groupFids": [
                            "1"
                        ],
                        "excluded": False,
                        "girlMajor": False
                    },
                    "teamFid": "1290"
                }
            ],
            "problemInfoByProblemSetProblemId": {
                "1834757673898389504": {
                    "label": "A",
                    "acceptCount": 1940,
                    "submitCount": 12371,
                    "balloonRgb": "#ff3b30",
                    "firstAcceptTeamFid": "1994"
                },
                "1834757673898389505": {
                    "label": "B",
                    "acceptCount": 23,
                    "submitCount": 192,
                    "balloonRgb": "#ee7528",
                    "firstAcceptTeamFid": "1283"
                },
                "1834757673898389506": {
                    "label": "C",
                    "acceptCount": 308,
                    "submitCount": 6078,
                    "balloonRgb": "#fde047",
                    "firstAcceptTeamFid": "1285"
                },
                "1834757673898389507": {
                    "label": "D",
                    "acceptCount": 1,
                    "submitCount": 53,
                    "balloonRgb": "#00aa00",
                    "firstAcceptTeamFid": "1284"
                },
            }
        },
        "competitionBasicInfo": {
            "name": "2024 ICPC Asia EC网络预选赛（第二场）",
            "startAt": "2024-09-21T05:00:00Z",
            "endAt": "2024-09-21T10:00:00Z",
            "logo": "70dd0346-f101-423f-895b-a0b11d2afcdf.png",
        }
    }

    pta._parse_contest(test_data)

    expected_start = int(datetime(2024, 9, 21, 5, 0, 0,
                         tzinfo=timezone.utc).timestamp())
    expected_end = int(datetime(2024, 9, 21, 10, 0, 0,
                       tzinfo=timezone.utc).timestamp())
    assert pta._contest.start_time == expected_start
    assert pta._contest.end_time == expected_end
    assert pta._contest.problem_quantity == 4
    assert pta._contest.problem_id == ["A", "B", "C", "D"]
    assert pta._contest.balloon_color == [
        Color(background_color="#ff3b30", color="#000"),
        Color(background_color="#ee7528", color="#000"),
        Color(background_color="#fde047", color="#000"),
        Color(background_color="#00aa00", color="#000"),
    ]

    assert pta._problem_ids == {
        "1834757673898389504": 0,
        "1834757673898389505": 1,
        "1834757673898389506": 2,
        "1834757673898389507": 3,
    }

    pta._parse_teams(test_data)

    team = pta.teams["1290"]
    assert team.team_id == "1290"
    assert team.name == "击中月亮"
    assert team.organization == "清华大学"
    assert team.members == ["程思元", "戚朗瑞", "魏佳泽"]
    assert team.group == ["1"]
    assert team.girl == False


def test_parse_team_runs():
    contest = Contest()
    contest.start_time = 1726376400
    pta = PTA(contest, "1222")
    pta._problem_ids = {
        "1001": 0,
        "1002": 1,
    }

    test_data = {
        "submissions": [
            {
                "status": "ACCEPTED",
                "problemSetProblemId": "1001",
                "submitAt":  "2024-09-15T05:17:30Z",
                "submissionId": "sub001"
            },
            {
                "status": "WRONG_ANSWER",
                "problemSetProblemId": "1002",
                "submitAt": "2024-09-15T05:20:12Z",
                "submissionId": "sub002"
            }
        ]
    }
    team_id = "team001"
    result = pta._parse_team_runs(test_data, team_id)

    assert isinstance(result, Submissions)
    assert len(result) == 2

    assert result[0].team_id == team_id
    assert result[0].status == constants.RESULT_ACCEPTED
    assert result[0].problem_id == 0
    assert result[0].timestamp == 1050
    assert result[0].submission_id == "sub001"

    assert result[1].team_id == team_id
    assert result[1].status == constants.RESULT_WRONG_ANSWER
    assert result[1].problem_id == 1
    assert result[1].timestamp == 1212
    assert result[1].submission_id == "sub002"
