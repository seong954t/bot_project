import requests
from bs4 import BeautifulSoup
import mysql.connector

def inputData(list):
    # DEFAULT SETTING : host='127.0.0.1', port='3306',charset='utf8'
    cnx = mysql.connector.connect(user='root', password='1234qwer', database='cnu_bachelor_info')
    #cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()
    print(list[0])
    stmt = "INSERT INTO info_db (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    stmt2 = "INSERT INTO info_db2 (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    # ON DUPLICATE KEY UPDATE title = VALUES(title)
    cursor.executemany(stmt, list)
    cursor.executemany(stmt2, list)  # 한 번에 복수 개를 저장
    # cursor.executemany(stmt, list)
    cnx.commit()
    cnx.close()

# 학사정보 크롤링
URI = "http://plus.cnu.ac.kr/_prog/_board/?code=sub07_0702&site_dvs_cd=kr&menu_dvs_cd=0702"
CONCAT_URI = "http://plus.cnu.ac.kr/_prog/_board"
#
r = requests.get(URI)
r.encoding = "utf-8"
soup = BeautifulSoup(r.text, "html.parser")
table = soup.find('div', {'class': "board_list"})
tbody = table.find('tbody')
tr_list = tbody.find_all('tr')

insert_list = []

print("시작")

for tr in tr_list:
    c_title = tr.find('td', {'class': 'title'}).a.get_text()
    c_href = tr.find('td', {'class': 'title'}).a.get('href')
    original_uri = CONCAT_URI + c_href[1:]
    c_center = tr.find('td', {'class': 'center'}).get_text()
    c_date = tr.find('td', {'class': 'date'}).get_text()
    # print("제목: " + c_title)
    # print("url: " + original_uri)  # href는 앞에 .붙어서 .빼줘야함
    # print("작성자: " + c_center)
    # print("날짜: " + c_date)
    query_data = (
        c_title, original_uri, c_center, c_date
    )
    insert_list.append(query_data)

inputData(insert_list)  # Connect to the database
