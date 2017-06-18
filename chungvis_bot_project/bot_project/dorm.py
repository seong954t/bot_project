# 학생생활관 홈페이지

import requests
from bs4 import BeautifulSoup
import mysql.connector

# 은행사 공지사항 URL page number 제외
DORM = "https://dorm.cnu.ac.kr/_prog/_board/?code=sub05_0501&site_dvs_cd=kr&menu_dvs_cd=0501&skey=&sval=&site_dvs=&GotoPage="
CONCAT_URL = "https://dorm.cnu.ac.kr/_prog/_board"
# 학생생활관 식단 URL
DORM_MENU = "http://dorm.cnu.ac.kr/html/kr/sub03/sub03_0304.html"

DORM_menu = []
DORM_info = []

def inputData(list,list2):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()
    print(list[0])
    stmt = "INSERT INTO dorm_menu (menu, d_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE d_date=VALUES(d_date)"
    stmt2 = "INSERT INTO dorm_info (title, link, writer, d_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    cursor.executemany(stmt, list)
    cursor.executemany(stmt2, list2)
    cnx.commit()
    cnx.close()


def main():
    for i in range(1, 6):  # 5 페이지 가져옴
        '''은행사 공지사항'''
        URL = DORM + str(i)  # 기본 URL에 페이지 번호를 붙여줌
        soup = getURL(URL)
        crawlling(soup, DORM_info)

    '''학생생활관 식단'''
    soup = getURL(DORM_MENU)
    crawlling_MENU(soup, DORM_menu)
    inputData(DORM_menu, DORM_info)


# 해당 URL에서 페이지 소스를 받아옴
def getURL(URL):
    r = requests.get(URL)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    return soup


# 학생생활관 은행사 공지 크롤링
def crawlling(soup, data_list):
    table = soup.find('div', {'class': "board_list"})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    for tr in tr_list:
        c_title = tr.find('td', {'class': 'title'})
        c_href = tr.find('td', {'class': 'title'}).a.get('href')
        c_center = tr.find('td', {'class': 'center'})
        c_date = tr.find('td', {'class': 'date'})

        title = c_title.a.get_text()  # 제목
        link = CONCAT_URL + c_href[1:]  # 링크
        writer = c_center.get_text()  # 작성자
        date = c_date.get_text()  # 작성일

        query_data = (title, link, writer, date)  # 제목,링크,작성자,작성일 로 구성된 데이터
        data_list.append(query_data)  # 데이터를 리스트에 추가


# 학생생활관 식단 크롤링
def crawlling_MENU(soup, data_list):
    table = soup.find('table', {'class': 'default_view diet_table'})

    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')  # 요일별 메뉴 (0~6: 월~일)

    for tr in tr_list:
        td_date = tr.find('td')
        bal = tr.find_all('td', {'class': 'left'})  # 아침(0) & 점심(1)
        dinner = tr.find('td', {'class': 'left last'})  # 저녁

        date = td_date.get_text()
        menu = '아침\n' + bal[0].get_text() + '점심\n' + bal[1].get_text() + '저녁\n' + dinner.get_text()

        query_data = (date, menu)  # 날짜, 메뉴로 구성된 데이터
        data_list.append(query_data)  # 데이터를 리스트에 추가


if __name__ == "__main__":
    main()