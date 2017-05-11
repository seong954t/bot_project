from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import time
import mysql.connector

E_URL = "http://e-learn.cnu.ac.kr/"
C_URL = "http://e-learn.cnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet?course_id=201620UN0025154D0000002&class_no=02&term_year=2016&term_cd=10&subject_cd=25154D00000&user_no="
R_URL = "http://e-learn.cnu.ac.kr/lms/class/boardItem/doListView.dunet?mnid=20100863099&board_no=6"

username = '201502022'  # 아이디
password = 'k1d2e3135246'  # 패스워드

E_ref = []
E_info = []
E_hw = []

def inputData(list,list2,list3):
    # DEFAULT SETTING : host='127.0.0.1', port='3306',charset='utf8'
    #cnx = mysql.connector.connect(user='root', password='1234qwer', database='cnu_bachelor_info')
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()
    print(list[0])
    stmt = "INSERT INTO e_ref (title, r_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    stmt2 = "INSERT INTO e_info (title, i_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    stmt3 = "INSERT INTO e_hw (title, s_date, e_date, submit) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    cursor.executemany(stmt, list)
    cursor.executemany(stmt2, list2)
    cursor.executemany(stmt3, list3)

    cnx.commit()
    cnx.close()

def main():
    '''PhantomJS를 이용하여 이러닝 사이트에 접속'''
    driver = webdriver.PhantomJS("C:\\Users\\eunjeong\\Desktop\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe")
    driver.set_window_size(1124, 850)
    driver.get(E_URL)

    login_elearn(driver)  # 이러닝 사이트에 로그인
    c_source = classroom(driver)  # 강의홈 페이지소스
    r_source = referenceroom(driver)  # 자료실 페이지소스

    driver.quit()  # PhantomJs 종료

    crawlling_reference(r_source, E_ref)  # 자료실 크롤링
    crawlling_notice(c_source, E_info)  # 공지사항 크롤링
    crawlling_hw(c_source, E_hw)  # 과제목록 크롤링

    inputData(E_ref, E_info, E_hw)
    print("ok")


# 이러닝 사이트에 로그인
def login_elearn(driver):
    login = None
    while not login:  # NoSuchElementException 처리
        try:
            login = driver.find_element_by_xpath("//a[@ id = 'pop_login']")  # 로그인창
        except NoSuchElementException:
            time.sleep(.5)

    login.click()  # 로그인창 활성화
    time.sleep(.5)

    loginform = driver.find_elements_by_tag_name('form')  # 로그인 폼
    userid = loginform[1].find_element_by_class_name('input_id')  # 아이디
    userpass = loginform[1].find_element_by_class_name('input_pw')  # 패스워드

    userid.send_keys(username)  # 아이디 전송
    userpass.send_keys(password)  # 패스워드 전송

    login_button = loginform[1].find_element_by_id('btn-login')  # 로그인 버튼
    login_button.click()  # 로그인 버튼 클릭
    time.sleep(2)


# 강의실에 접속하여 페이지 소스 리턴
def classroom(driver):
    driver.get(C_URL)  # 강의실 접속 (시스템 프로그래밍)

    html_source = driver.page_source  # 웹페이지 소스 가져옴

    return html_source


# 자료실에 접속하여 페이지 소스 리턴
def referenceroom(driver):
    driver.get(R_URL)  # 자료실 접속

    html_source = driver.page_source  # 웹페이지 소스 가져옴

    return html_source


# 과제 목록 크롤링
def crawlling_hw(html_source, data_list):
    soup = BeautifulSoup(html_source, 'html.parser')
    table = soup.find('table', {'class': 'datatable mg_t15'})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    i = 0
    for tr in tr_list:
        hw = tr.find('td', {'class': 'ta_l'})
        date = tr.find_all('td', {'class': 'ta_c'})
        tr_submit = tr.find('td', {'class': 'bn_tc'})

        if (i == 0):
            i = 1
            title = hw.get_text()  # 과제 제목
            s_date = date[1].get_text()  # 시작일
            e_date = date[2].get_text()  # 종료일
            submit = tr_submit.get_text()  # 제출 여부
        else:
            title = hw.get_text()  # 과제 제목
            s_date = date[0].get_text()  # 시작일
            e_date = date[1].get_text()  # 종료일
            submit = tr_submit.get_text()  # 제출 여부

        query_data = (title, s_date, e_date, submit)
        data_list.append(query_data)


# 해당 테그의 텍스트에서 공백을 제거하여 리턴
def del_blank(tag):
    txt = tag.get_text()
    return ''.join(txt.split())


# 공지사항 크롤링
def crawlling_notice(html_source, data_list):
    soup = BeautifulSoup(html_source, 'html.parser')
    table = soup.find_all('table', {'class': 'datatable fs_s bo_lrn'}, limit=2)
    tbody = table[1].find('tbody')
    tr_list = tbody.find_all('tr')

    for tr in tr_list:
        notice = tr.find('td', {'class': "bo_lrn ft_b ta_l"})
        td_date = tr.find('td', {'class': 'bo_lrn ta_c'})

        title = del_blank(notice)  # 공지사항 제목
        date = td_date.get_text()  # 작성일

        query_data = (title, date)  # 제목, 작성일로 구성된 데이터
        data_list.append(query_data)  # 리스트에 데이터 추가


# 자료실 크롤링
def crawlling_reference(html_source, data_list):
    soup = BeautifulSoup(html_source, 'html.parser')
    table = soup.find('table', {'class': 'list'})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    for tr in tr_list:
        td_list = tr.find_all('td')

        title = del_blank(td_list[1].a)  # 제목
        date = td_list[4].get_text()  # 작성일

        query_data = (title, date)  # 제목, 작성일로 구성된 데이터
        data_list.append(query_data)  # 리스트에 데이터 추가


if __name__ == "__main__":
    main()