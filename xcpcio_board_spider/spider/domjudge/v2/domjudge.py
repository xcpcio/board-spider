import requests
import bs4
import copy
import os

from xcpcio_board_spider.core import utils
from xcpcio_board_spider.type import Contest, Team, Teams, Submission, Submissions, constants


class DOMjudge():
    CONSTANT_IS_DEFAULT_OBSERVERS_TEAM = "is_default_observers_team"
    CONSTANT_CLASS_ATTR = "class_attr"

    def __init__(self,
                 contest: Contest = None,
                 fetch_uri: str = None):
        self.contest = contest
        self.fetch_uri = fetch_uri

        self.html = ""
        self.soup = None

        self.teams = Teams()
        self.submissions = Submissions()

    @staticmethod
    def is_default_observers_team(team: Team) -> bool:
        return DOMjudge.CONSTANT_IS_DEFAULT_OBSERVERS_TEAM in team.extra.keys() and team.extra[DOMjudge.CONSTANT_IS_DEFAULT_OBSERVERS_TEAM] == True

    @staticmethod
    def get_team_class_attr(team: Team):
        return team.extra[DOMjudge.CONSTANT_CLASS_ATTR]

    def get_incorrect_timestamp(self) -> int:
        return min(utils.get_now_timestamp_second(), utils.get_timestamp_second(self.contest.end_time)) - utils.get_timestamp_second(self.contest.start_time)

    def fetch(self):
        if os.path.exists(self.fetch_uri):
            with open(self.fetch_uri, 'r') as f:
                self.html = f.read()
        else:
            params = {
                '__timestamp__': utils.get_now_timestamp_second()
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }

            resp = requests.get(self.fetch_uri, params=params,
                                headers=headers, timeout=5)

            if resp.status_code == 200:
                content_type = resp.headers.get("Content-Type")

                if "charset" in content_type:
                    charset = content_type.split("charset=")[1]
                    html = resp.content.decode(charset)
                else:
                    html = resp.content.decode()
            else:
                raise RuntimeError(
                    "fetch failed. [status_code=%s]" % resp.status_code)

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

            team.official = True

            team.extra[DOMjudge.CONSTANT_CLASS_ATTR] = tr.select(".scoretn")[
                0].attrs["class"]

            # default Observers color
            if "cl_ffcc33" in team.extra[DOMjudge.CONSTANT_CLASS_ATTR]:
                team.extra[DOMjudge.CONSTANT_IS_DEFAULT_OBSERVERS_TEAM] = True

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

    def handle_default_observers_team(self):
        for team in self.teams.values():
            if DOMjudge.is_default_observers_team(team):
                team.official = False
                team.unofficial = True

        return self
