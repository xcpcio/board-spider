import os
from bs4 import BeautifulSoup

if __name__ == '__main__':
    year = 2008
    base_pth = 'D:\\XCPCIO\\XCPCIO-Board-Data\\origin-data\\icpc\\'
    for _ in range(9):
        year += 1
        dir_pth = base_pth + str(year)
        if os.path.isdir(dir_pth):
            os.chdir(dir_pth)
        else:
            exit(-1)
        for file_name in os.listdir():
            if os.path.isdir(file_name):
                continue
            content_txt = ''
            with open(file_name, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    if line.find('if($haspara){') != -1:
                        continue
                    if line.find('for($i=0;$i') != -1:
                        continue
                    if line.find(');')!=-1:
                        continue
                    content_txt += line
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content_txt)
