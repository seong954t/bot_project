# CNU 크롤링 페이지

import requests
from bs4 import BeautifulSoup
import pymysql

def inputData(list,list2,list3,list4):
    cnx = pymysql.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()
    print(list[0])
    stmt = "INSERT INTO cnu_news (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    stmt2 = "INSERT INTO cnu_h_info (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    stmt3 = "INSERT INTO cnu_e_info (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    stmt4 = "INSERT INTO cnu_job(title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"

    cursor.executemany(stmt, list)
    cursor.executemany(stmt2, list2)
    cursor.executemany(stmt3, list3)
    cursor.executemany(stmt4, list4)

    cnx.commit()
    cnx.close()


# 각 게시판 URL page number 제외
NEWS = "http://plus.cnu.ac.kr/_prog/_board/?code=sub07_0701&site_dvs_cd=kr&menu_dvs_cd=0701&skey=&sval=&site_dvs=&ntt_tag=&GotoPage="
H_INFO = "http://plus.cnu.ac.kr/_prog/_board/?code=sub07_0702&site_dvs_cd=kr&menu_dvs_cd=0702&skey=&sval=&site_dvs=&ntt_tag=&GotoPage="
E_INFO = "http://plus.cnu.ac.kr/_prog/_board/?code=sub07_0704&site_dvs_cd=kr&menu_dvs_cd=0704&skey=&sval=&site_dvs=&ntt_tag=&GotoPage="
JOBS = "http://plus.cnu.ac.kr/_prog/recruit/?site_dvs_cd=kr&menu_dvs_cd=07080401&gubun=1&&GotoPage="

CONCAT_URI = "http://plus.cnu.ac.kr/_prog/_board"
CONCAT_JOBS = "http://plus.cnu.ac.kr"

CNU_news = []
CNU_h_info = []
CNU_e_info = []
CNU_job = []


def main():
    for i in range(1, 11):  # 10 페이지 가져옴
        URL = NEWS + str(i)  # 기본 URL에 페이지 번호를 붙여줌
        soup = getURL(URL)
        crawlling(soup, CNU_news)

        URL = H_INFO + str(i)
        soup = getURL(URL)
        crawlling(soup, CNU_h_info)

        URL = E_INFO + str(i)
        soup = getURL(URL)
        crawlling(soup, CNU_e_info)

        URL = JOBS + str(i)
        soup = getURL(URL)
        crawllingJobs(soup, CNU_job)

    inputData(CNU_news,CNU_h_info,CNU_e_info,CNU_job)
    print("ok")


# 해당 URL에서 페이지 소스를 받아옴
def getURL(URL):
    r = requests.get(URL)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    return soup


# 새소식, 학사 정보, 교육 정보 크롤링
def crawlling(soup, data_list):
    table = soup.find('div', {'class': "board_list"})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    for tr in tr_list:
        c_title = tr.find('td', {'class': 'title'})
        c_href = tr.find('td', {'class': 'title'}).a.get('href')
        c_center = tr.find('td', {'class': 'center'})
        c_date = tr.find('td', {'class': 'date'})

        title = c_title.a.get_text()
        link = CONCAT_URI + c_href[1:]
        writer = c_center.get_text()
        date = c_date.get_text()

        query_data = (title, link, writer, date)
        data_list.append(query_data)


# 구인구직 크롤링
def crawllingJobs(soup, data_list):
    table = soup.find('table', {'class': 'default_table'})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    for tr in tr_list:
        td_list = tr.find_all('td')
        td_title = td_list[1]
        td_url = td_list[1].a.get('href')
        td_write = td_list[2]
        td_date = td_list[3]

        title = td_title.a.get_text()  # 제목
        link = CONCAT_JOBS + td_url  # 링크
        writer = td_write.get_text()  # 작성자
        date = td_date.get_text()  # 작성일

        query_data = (title, link, writer, date)
        data_list.append(query_data)

if __name__ == "__main__":
    main()
