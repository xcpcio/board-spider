from bs4 import BeautifulSoup
import re
import os

RE_SOLUTION_AC_TYPE1 = re.compile(r'\d+/\d+')
RE_SOLUTION_AC_TYPE2 = re.compile(r'\d+:\d+:\d+ \(\d+\)')
RE_SOLUTION_AC_TYPE3 = re.compile(r'\d+:\d+:\d+\(-\d+\)')
RE_SOLUTION_AC_TYPE4 = re.compile(r'\d+:\d+:\d+')
RE_SOLUTION_AC_TYPE5 = re.compile(r'\d+\(\d+\)')
RE_SOLUTION_AC_TYPE6 = re.compile(r'\d+\(-\d+\)')
RE_SOLUTION_AC_TYPE7 = re.compile(r'\d+')

RE_SOLUTION_WA_TYPE1 = re.compile(r'\d+/[-]+')
RE_SOLUTION_WA_TYPE2 = re.compile(r'\(\d+\)')
RE_SOLUTION_WA_TYPE3 = re.compile(r'\d+')
RE_SOLUTION_WA_TYPE4 = re.compile(r'\(-\d+\)')
RE_SOLUTION_WA_TYPE5 = re.compile(r'-\d+/[-]+')
RE_SOLUTION_WA_TYPE6 = re.compile(r'-\d+')

if __name__ == '__main__':
    while True:
        WORK_DIR = input('input work dir:\n')
        if os.path.isdir(WORK_DIR):
            os.chdir(WORK_DIR)
        else:
            exit(-1)
        for file in os.listdir():
            if os.path.isdir(file):
                continue
            with open(file, 'r', encoding='utf-8') as f:
                html_content = f.read()
                dom = BeautifulSoup(html_content, 'lxml')
                # ac_solution = dom.find_all('td', class_='ac') + dom.find_all('td', class_='firstac')
                # for content in ac_solution:
                #     if RE_SOLUTION_AC_TYPE1.match(content.get_text(strip=True)):
                #         continue
                #     if RE_SOLUTION_AC_TYPE2.match(content.get_text(strip=True)):
                #         continue
                #     if RE_SOLUTION_AC_TYPE3.match(content.get_text(strip=True)):
                #         continue
                #     if RE_SOLUTION_AC_TYPE4.match(content.get_text(strip=True)):
                #         continue
                #     if RE_SOLUTION_AC_TYPE5.match(content.get_text(strip=True)):
                #         continue
                #     if RE_SOLUTION_AC_TYPE6.match(content.get_text(strip=True)):
                #         continue
                #     if RE_SOLUTION_AC_TYPE7.match(content.get_text(strip=True)):
                #         continue
                #     print(file, content.get_text(strip=True))
                wa_solution = dom.find_all('td', class_='fail') + dom.find_all('td', class_='try')
                for content in wa_solution:
                    if RE_SOLUTION_WA_TYPE1.match(content.get_text(strip=True)):
                        continue
                    if RE_SOLUTION_WA_TYPE2.match(content.get_text(strip=True)):
                        continue
                    if RE_SOLUTION_WA_TYPE3.match(content.get_text(strip=True)):
                        continue
                    if RE_SOLUTION_WA_TYPE4.match(content.get_text(strip=True)):
                        continue
                    if RE_SOLUTION_WA_TYPE5.match(content.get_text(strip=True)):
                        continue
                    if RE_SOLUTION_WA_TYPE6.match(content.get_text(strip=True)):
                        continue
                    print(file, content.get_text(strip=True))
