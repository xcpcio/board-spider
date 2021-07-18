import requests
import json
from os import path
import time
import bs4
import os
import logging

def json_input(path):
	with open(path, 'r') as f:
		return json.load(f)

def json_output(data):
	return json.dumps(data, sort_keys=False, separators=(',', ':'), ensure_ascii=False)

__IMAGE_DOWNLOAD_HOST__ = "image_download_host"
__IMAGE_DIR__ = "image_dir"

# Required parameters
_params = json_input('params.json')
data_dir = _params['data_dir']
charset = _params['charset']
end_time = _params['end_time']
start_time = _params['start_time']

# Optional parameters
if "image_download_host" in _params.keys():
	image_download_host = _params[__IMAGE_DOWNLOAD_HOST__]

if "image_dir" in _params.keys():
	image_dir = _params[__IMAGE_DIR__]

def output(filename, data):
	with open(path.join(data_dir, filename), 'w') as f:
		f.write(json_output(data))

def get_timestamp(dt):
	# 转换成时间数组
	timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
	
	# 转换成时间戳
	timestamp = time.mktime(timeArray)
	return int(timestamp)

def get_now():
	return int(time.time())

def get_incorrect_timestamp():
	return min(get_now(), get_timestamp(end_time)) - get_timestamp(start_time)

def mkdir(_path):
	if not path.exists(_path):
		os.makedirs(_path)

def trim(s):
	def ltrim(s):
		while len(s) > 0:
			if s[0] == " " or s[0] == "\n":
				s = s[1:]
			else:
				break
		return s

	s = ltrim(s)
	s = s[::-1]
	s = ltrim(s)
	s = s[::-1]

	return s

def init_logging():
  global logger
  
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)

def urllib_download(img_url, dist):
	from urllib.request import urlretrieve
	mkdir(path.split(dist)[0])
	urlretrieve(img_url, dist)

def fetch():
	if 'board_url' in _params.keys():
		board_url = _params['board_url']
		params = (
			('t', get_now()),
		)   
		response = requests.get(board_url, params=params)
		html = response.text
		
		# print(html)
		# html = response.text.encode("latin1").decode(charset)
		
		return html
	
	elif 'board_file' in _params.keys():
		board_file = _params['board_file']
		with open(board_file, 'r') as f:
			return f.read()
	
	return ""

def image_download(html):
	soup = bs4.BeautifulSoup(html,'html5lib')
	img_elements = soup.select('img')
	srcs = set()
	imgs = soup.find_all('img')
	for img in imgs:
		srcs.add(img['src'])
	for src in srcs:
		img_url = path.join(image_download_host, src)
		dist = path.join(image_dir, src)
		if not path.isfile(dist):
			print("downloading... " + src)
			urllib_download(img_url, dist)
			print(src + " downloaded.")
		else:
			print(src + " existed.")

def team_out(html):
	team = {}
	soup = bs4.BeautifulSoup(html, 'html5lib')
	
	# 默认选择第0个 如果在榜单前出现其他 tbody 元素会出错
	tbody = soup.select('tbody')[0]
	trs = tbody.select('tr')
	
	for tr in trs:        
		if not tr.has_attr("id"):
			continue
			
		_team = {}
		team_id = tr['id'].split(':')[1]
		
		for item in tr.select('.forceWidth')[0].children:
			name = item
		
		for item in tr.select('.forceWidth')[1].children:
			organization = item
		
		name = trim(name)
		organization = trim(organization)

		if len(tr.select('.cl_ffcc33')) > 0:
			_team['unofficial'] = 1
		else:
			_team['official'] = 1
				
		_team['organization'] = organization
		_team['name'] = name
		
		_team['team_id'] = team_id
		team[team_id] = _team

	if get_now() >= get_timestamp(start_time) and len(team) > 0:
		output("team.json", team)

def run_out(html):
	run = []
	soup = bs4.BeautifulSoup(html,'html5lib')
	
	# 默认选择第0个 如果在榜单前出现其他 tbody 元素会出错
	tbody = soup.select('tbody')[0]
	trs = tbody.select('tr')
	
	for tr in trs:
		if not tr.has_attr("id"):
			continue
			
		team_id = tr['id'].split(':')[1]
		
		_run = {}
		_run['team_id'] = team_id
		
		score_cells = tr.select('.score_cell')
		index = -1
		for score_cell in score_cells:
			index += 1
			_run['problem_id'] = index
			
			score_correct = score_cell.select('.score_correct')
			score_incorrect = score_cell.select('.score_incorrect')
			score_pending = score_cell.select('.score_pending')

			if len(score_correct) > 0:
				timestamp = int(trim(score_correct[0].contents[0])) * 60
				cnt = int(trim(score_correct[0].select('span')[0].string).split(' ')[0])

				_run['timestamp'] = timestamp
				_run['status'] = 'incorrect'
				
				for i in range(1, cnt):
					run.append(_run.copy())
				
				_run['status'] = 'correct'
				run.append(_run.copy())

			if len(score_incorrect) > 0:
				cnt = int(trim(score_incorrect[0].select('span')[0].string).split(' ')[0])
				
				for i in range(cnt):
					_run['status'] = 'incorrect'
					_run['timestamp'] = get_incorrect_timestamp()
					run.append(_run.copy())
			
			if len(score_pending) > 0:
				pending_text = trim(score_pending[0].select('span')[0].string)
				pending_text = pending_text.replace(" tries", "")

				wa_cnt = int(pending_text.split(" + ")[0])
				pending_cnt = int(pending_text.split(" + ")[1])
 
				for i in range(wa_cnt):
					_run['status'] = 'incorrect'
					_run['timestamp'] = 1
					run.append(_run.copy())
				
				for i in range(pending_cnt):
					_run['status'] = 'pending'
					_run['timestamp'] = get_incorrect_timestamp()
					run.append(_run.copy())
			
	if get_now() >= get_timestamp(start_time) and len(run) > 0:
		output('run.json', run)

def sync():
	init_logging()

	while True:
		logger.info("fetching...")
		try:
			html = fetch()
			
			if __IMAGE_DOWNLOAD_HOST__ in dir() and __IMAGE_DIR__ in dir():
				image_download(html)
			
			team_out(html)
			run_out(html)

			logger.info("fetch successfully")
		except Exception as e:
			logger.error("fetch failed...", e)
		
		logger.info("sleeping...")
		
		time.sleep(20)

sync()
