import json
import os
import typing
from pathlib import Path

import requests

from xcpcio_board_spider import (
    Contest,
    Submission,
    Submissions,
    Team,
    Teams,
    constants,
    utils,
)


class CF():
    kTimeoutSecs = 10

    def __init__(self, contest: Contest, fetch_uri: str = None):
        self._contest = contest
        self._fetch_uri = fetch_uri

        self._teams = Teams()
        self._runs = Submissions()
