import requests
import bs4
import copy
import os

from xcpcio_board_spider.core import utils
from xcpcio_board_spider.type import Team, Teams, Submission, Submissions, constants


class DOMjudge():
    IS_DEFAULT_OBSERVERS_TEAM = "is_default_observers_team"

    def __init__(self,
                 start_time: int = None,
                 end_time: int = None,
                 fetch_uri: str = None,):
        self.start_time = start_time
        self.end_time = end_time
        self.fetch_uri = fetch_uri

        self.html = ""
        self.soup = None

        self.teams = Teams()
        self.submissions = Submissions()

    @staticmethod
    def is_default_observers_team(team: Team) -> bool:
        return team.extra[DOMjudge.IS_DEFAULT_OBSERVERS_TEAM] == True

    def get_incorrect_timestamp(self) -> int:
        return min(utils.get_now_timestamp_second(), utils.get_timestamp(self.end_time)) - utils.get_timestamp(self.start_time)

    def fetch(self):
        if os.path.exists(self.fetch_uri):
            with open(self.fetch_uri, 'r') as f:
                self.html = f.read()
        else:
            params = (
                ('t', utils.get_now_timestamp_second())
            )
            response = requests.get(self.fetch_uri, params=params, timeout=5)
            html = response.text

            # html = response.text.encode("latin1").decode(charset)
            self.html = html

        self.soup = bs4.BeautifulSoup(self.html, 'html5lib')

        return self

    def trs_iterator(self):
        # 默认选择第0个 如果在榜单前出现其他 tbody 元素会出错
        tbody = self.soup.select('tbody')[0]
        trs = tbody.select('tr')

        for tr in trs:
            if not tr.has_attr("id"):
                continue

            yield tr

    def parse_teams(self):
        self.teams = Teams()

        for tr in self.trs_iterator():
            team = Team()
            team_id = str(tr['id'].split(':')[1])

            for item in tr.select('.forceWidth')[0].children:
                name = item

            for item in tr.select('.forceWidth')[1].children:
                organization = item

            team.team_id = team_id
            team.name = name.strip()
            team.organization = organization.strip()

            # default Observers color
            if len(tr.select('.cl_ffcc33')) > 0:
                team.extra[DOMjudge.IS_DEFAULT_OBSERVERS_TEAM] = True

            self.teams[team_id] = team

        return self

    def parse_runs(self):
        self.runs = Submissions()

        for tr in self.trs_iterator():
            team_id = str(tr['id'].split(':')[1])

            submission = Submission()
            submission.team_id = team_id

            score_cells = tr.select('.score_cell')
            index = -1
            for score_cell in score_cells:
                index += 1
                submission.problem_id = index

                score_correct = score_cell.select('.score_correct')
                score_incorrect = score_cell.select('.score_incorrect')
                score_pending = score_cell.select('.score_pending')

                if len(score_correct) > 0:
                    timestamp = int(
                        str(score_correct[0].contents[0]).strip()) * 60
                    cnt = int(score_correct[0].select(
                        'span')[0].string.strip().split(' ')[0])

                    submission.timestamp = timestamp
                    submission.status = constants.RESULT_INCORRECT
                    self.runs += [copy.deepcopy(submission)
                                  for _ in range(1, cnt)]

                    submission.status = constants.RESULT_CORRECT
                    self.runs.append(copy.deepcopy(submission))

                if len(score_incorrect) > 0:
                    cnt = int(score_incorrect[0].select(
                        'span')[0].string.strip().split(' ')[0])

                    submission.status = constants.RESULT_INCORRECT
                    submission.timestamp = self.get_incorrect_timestamp()
                    self.runs += [copy.deepcopy(submission)
                                  for _ in range(cnt)]

                if len(score_pending) > 0:
                    pending_text = score_pending[0].select('span')[
                        0].string.strip()
                    pending_text = pending_text.replace(" tries", "")

                    incorrect_cnt = int(pending_text.split(" + ")[0])
                    pending_cnt = int(pending_text.split(" + ")[1])

                    pending_timestamp = self.get_incorrect_timestamp()
                    incorrect_timestamp = max(1, pending_timestamp - 1)

                    submission.status = constants.RESULT_INCORRECT
                    submission.timestamp = incorrect_timestamp
                    self.runs += [copy.deepcopy(submission)
                                  for _ in range(incorrect_cnt)]

                    submission.status = constants.RESULT_PENDING
                    submission.timestamp = pending_timestamp
                    self.runs += [copy.deepcopy(submission)
                                  for _ in range(pending_cnt)]

        return self
