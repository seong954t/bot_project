import time
import mysql.connector  #   MYSQL 커넥터
import telepot          #   텔레그램 봇과 통신하기 위한 API
import sys
import re

CNU = ['새소식', '학사공지', '구인구직', '교육정보']       #   충남대학교 홈페이지
CNU_news = CNU[0]
CNU_h_info = CNU[1]
CNU_job = CNU[2]
CNU_e_info = CNU[3]

E = ['자료실', '이러닝공지사항', '과제']                            #   이러닝 홈페이지
E_ref = E[0]
E_info = E[1]
E_hw = E[2]

CSE = ['컴공공지사항', '일반소식', '사업단소식']                  #   컴퓨터공학과 홈페이지
CSE_info = CSE[0]
CSE_g_info = CSE[1]
CSE_s_info = CSE[2]

MENU = ['2학', '3학']                                      #   급식 메뉴
MENU_2 = MENU[0]
MENU_3 = MENU[1]

DORM = ['급식', '기숙사공지사항']                                #   기숙사 홈페이지
DORM_menu = DORM[0]
DORM_info = DORM[1]

#   data를 db에 저장
def inputData(list):
    # DEFAULT SETTING : host='127.0.0.1', port='3306',charset='utf8'
    #cnx = mysql.connector.connect(user='root', password='1234qwer', database='cnu_bachelor_info')
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()
    print(list[0])
    stmt = "INSERT INTO info_db (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    #stmt2 = "INSERT INTO info_db2 (title, link, writer, publish_date) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title)"
    cursor.executemany(stmt, list)  #   한 번에 복수 개를 저장
    #cursor.executemany(stmt2, list)  # 한 번에 복수 개를 저장
    cnx.commit()
    cnx.close()

#   텔레그램 봇에 메세지를 전달
def send_message(id, msg):
    try:
        bot.sendMessage(id, msg)
    except:
        print("error!")


#   최초 명령어 알림 함수
def help(id):
    send_message(id,
u'''안녕? 난 충비서! 무엇을 도와줄까?

명령어 사용법:
/list  : 최근 등록게시물 10개 조회
/sub   : 게시판 구독하기
/unsub : 게시판 구독취소
/CNU   : 충남대학교 홈페이지 정보
/E     : 충남대학교 이러닝 홈페이지
/CSE   : 충남대학교 컴퓨터공학과 홈페이지
/MENU  : 충남대학교 학생 식당 정보
/DORM  : 충남대학교 학생생활관(기숙사) 정보
''')
    buttons = {'keyboard': [['/search', '/sub'], ['/unsub', '/CNU'], ['/E', '/CSE'], ['/MENU', '/DORM']]}
    bot.sendMessage(id, '어떤 정보를 원하니?', reply_markup=buttons)

#   구독 신청 명령어 알림 함수
def subscribe_help(id):
    send_message(id,
                 u''' 게시판 구독신청은 여기서 해요!

명령어 사용법:
&CNU   : 충남대학교 홈페이지 정보 구독
&E     : 충남대학교 이러닝 홈페이지 구독
&CSE   : 충남대학교 컴퓨터공학과 홈페이지 구독
&MENU  : 충남대학교 학생 식당 정보 구독
&DORM  : 충남대학교 학생생활관(기숙사) 정보
                 ''')
    buttons = {'keyboard': [['빈 버튼', '&CNU'], ['&E', '&CSE'], ['&MENU', '&DORM']]}
    bot.sendMessage(id, '어떤 정보를 원하니?', reply_markup=buttons)

#   구독된 정보가 없을 때
def before_subscribe(id, text):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',
                                  database='cnu_bachelor_info')
    cursor = cnx.cursor()
    sql_msg = ["INSERT INTO subscribe_board (user_name, cnu) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)",
               "INSERT INTO subscribe_board (user_name, elearn) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)",
               "INSERT INTO subscribe_board (user_name, cse) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)"
               "INSERT INTO subscribe_board (user_name, menu) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)",
               "INSERT INTO subscribe_board (user_name, dorm) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)"]

    stmt = ''
    if text == '&CNU':
        stmt = sql_msg[0]
    elif text == '&E':
        stmt = sql_msg[1]
    elif text == '&CSE':
        stmt = sql_msg[2]
    elif text == '&MENU':
        stmt = sql_msg[3]
    elif text == '&DORM':
        stmt = sql_msg[4]
    else:
        help(id)

    try:
        insert_text = []
        query_data = (id, 'Y')
        insert_text.append(query_data)
        cursor.execute(stmt, insert_text[0])
        send_message(id, " '%s' 구독이 완료되었습니다. " %(text))
    finally:
        cnx.commit()
        cnx.close()
        time.sleep(2)
        help(id)

def after_subscribe(id, text):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',
                                  database='cnu_bachelor_info')
    cursor = cnx.cursor()
    stmt = ''

    try:
        if text == '&CNU':
            cursor.execute("UPDATE subscribe_board set cnu = 'Y' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 완료되었습니다. " % (text))
        elif text == '&E':
            cursor.execute("UPDATE subscribe_board set elearn = 'Y' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 완료되었습니다. " % (text))
        elif text == '&CSE':
            cursor.execute("UPDATE subscribe_board set cse = 'Y' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 완료되었습니다. " % (text))
        elif text == '&MENU':
            cursor.execute("UPDATE subscribe_board set menu = 'Y' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 완료되었습니다. " % (text))
        elif text == '&DORM':
            cursor.execute("UPDATE subscribe_board set dorm = 'Y' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 완료되었습니다. " % (text))
        else:
            send_message(id, " '%s' 구독에 실패하셨습니다. " % (text))
            help(id)
    finally:
        cnx.commit()
        cnx.close()
        time.sleep(2)
        help(id)

#   게시판 구독 함수
def subscribe_board(id,text):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',
                                  database='cnu_bachelor_info')
    cursor = cnx.cursor()
    insert_text = []

    # 구독자 리스트 가져오기
    subscribe_user_list = []
    cursor.execute("SELECT user_name FROM subscribe_board")
    for data in cursor.fetchall():
        subscribe_user_list.append(data[0])

    #send_message(id, text)
    if text == '&CNU':
        #send_message(id, "진입2")
        if id in subscribe_user_list:
            cursor.execute("UPDATE subscribe_board set cnu = 'Y' WHERE user_name = '%s' " % (id))
            cnx.commit()
            cnx.close()
            send_message(id, "충남대 홈페이지 정보 구독이 완료되었습니다.")
            help(id)
        else:
            before_subscribe(id, text)
    elif text == "&E":
        if id in subscribe_user_list:
            query_data = (id)
            insert_text.append(query_data)
            # stmt = "UPDATE subscribe_board SET id=%s cnu=%s"
            # cursor.execute(stmt, insert_text[0])
            send_message(id,subscribe_user_list[0])
            cursor.execute("UPDATE subscribe_board set elearn = 'Y' WHERE user_name = '%s' " % (id))
            cnx.commit()
            cnx.close()
            send_message(id, "이러닝 홈페이지 정보 구독이 완료되었습니다. ")
            help(id)
        else:
            # query_data = (id, 'Y')
            # insert_text.append(query_data)
            # stmt = "INSERT INTO subscribe (user_name, elearn) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_name=VALUES(user_name)"
            # cursor.execute(stmt, insert_text[0])
            # send_message(id, "이러닝 홈페이지 정보 구독이 완료되었습니다. ")
            # help(id)
            before_subscribe(id, text)
    elif text == "&CSE":
        if id in subscribe_user_list:
            after_subscribe(id, text)
        else:
            before_subscribe(id, text)
    elif text == "&MENU":
        if id in subscribe_user_list:
            query_data = (id)
            insert_text.append(query_data)
            cursor.execute("UPDATE subscribe_board set menu = 'Y' WHERE user_name = '%s' " % (id))
            cnx.commit()
            cnx.close()
            send_message(id, "급식 정보 구독이 완료되었습니다. ")
            help(id)
        else:
            before_subscribe(id, text)
    elif text == "&DORM":
        if id in subscribe_user_list:
            query_data = (id)
            insert_text.append(query_data)
            cursor.execute("UPDATE subscribe_board set dorm = 'Y' WHERE user_name = '%s' " % (id))
            cnx.commit()
            cnx.close()
            send_message(id, "기숙사  정보 구독이 완료되었습니다.")
            help(id)
        else:
            before_subscribe(id, text)

def cancle_subscribe_help(id):
    send_message(id,
                 u''' 게시판 구독 취소 여기서 해요!

명령어 사용법:
초기목록: 처음으로 돌아가기
$CNU   : 충남대학교 홈페이지 정보 구독
$E     : 충남대학교 이러닝 홈페이지 구독
$CSE   : 충남대학교 컴퓨터공학과 홈페이지 구독
$MENU  : 충남대학교 학생 식당 정보 구독
$DORM  : 충남대학교 학생생활관(기숙사) 정보
                 ''')
    buttons = {'keyboard': [['초기목록', '$CNU'], ['$E', '$CSE'], ['$MENU', '$DORM']]}
    bot.sendMessage(id, '어떤 정보를 원하니?', reply_markup=buttons)


def cancle_subscribe(id,text):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',
                                  database='cnu_bachelor_info')
    cursor = cnx.cursor()
    insert_text = []

    # 구독자 리스트 가져오기
    subscribe_user_list = []
    cursor.execute("SELECT user_name FROM subscribe_board")
    for data in cursor.fetchall():
        subscribe_user_list.append(data[0])

    # send_message(id, text)
    if text == '$CNU':
        # send_message(id, "진입2")
        if id in subscribe_user_list:
            remove_subscribe_list(id, text)
            send_message(id, "충남대 홈페이지 정보 구독이 취소되었습니다.")
        else:
            send_message(id, "구독하지 않았습니다. ")
    elif text == "$E":
        if id in subscribe_user_list:
            remove_subscribe_list(id,text)
            send_message(id, "이러닝 홈페이지 정보 구독이 취소되었습니다. ")
        else:
            send_message(id, "구독하지 않았습니다. ")
    elif text == "$CSE":
        if id in subscribe_user_list:
            remove_subscribe_list(id, text)
            send_message(id, "컴공 홈페이지 정보 구독이 취소되었습니다. ")
        else:
            send_message(id, "구독하지 않았습니다. ")
    elif text == "$MENU":
        if id in subscribe_user_list:
            remove_subscribe_list(id, text)
            send_message(id, "급식 정보 구독이 취소되었습니다. ")
        else:
            send_message(id, "구독하지 않았습니다. ")
    elif text == "$DORM":
        if id in subscribe_user_list:
            remove_subscribe_list(id, text)
            send_message(id, "기숙사  정보 구독이 취소되었습니다.")
        else:
            send_message(id, "구독하지 않았습니다. ")
    time.sleep(2)
    help(id)

def remove_subscribe_list(id, text):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',
                                  database='cnu_bachelor_info')
    cursor = cnx.cursor()
    stmt = ''

    try:
        if text == '$CNU':
            cursor.execute("UPDATE subscribe_board set cnu = 'N' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 취소되었습니다. " % (text))
        elif text == '$E':
            cursor.execute("UPDATE subscribe_board set elearn = 'N' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 취소되었습니다. " % (text))
        elif text == '$CSE':
            cursor.execute("UPDATE subscribe_board set cse = 'N' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 취소되었습니다. " % (text))
        elif text == '$MENU':
            cursor.execute("UPDATE subscribe_board set menu = 'N' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 취소되었습니다. " % (text))
        elif text == '$DORM':
            cursor.execute("UPDATE subscribe_board set dorm = 'N' WHERE id = '%s'" % (id))
            send_message(id, " '%s' 구독이 취소되었습니다. " % (text))
        else:
            send_message(id, " '%s' 구독 취소에 실패하셨습니다. " % (text))
    finally:
        cnx.commit()
        cnx.close()




def handle(msg):
    #cnx = mysql.connector.connect(user='root', password='1234qwer', database='cnu_bachelor_info')
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',database='cnu_bachelor_info')
    cursor = cnx.cursor()
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        send_message(chat_id, u'잘못된 입력입니다.')
        return

    text = msg['text']
    res = ''
    if text.startswith('/'):
        if text.startswith('/search'):
            # try:
            #     cursor.execute("SELECT id,title,link,writer,publish_date FROM info_db ORDER BY id desc LIMIT 10")
            #     receive_list = []
            #     res = ''
            #     for id, title, link, writer, publish_date in cursor:
            #         receive_list.append(u"글번호 : %s \n제목 : %s \n링크 : %s \n작성자 : %s\n작성일자 : %s\n\n" % (
            #             id, title, link, writer, publish_date))
            #     for message in reversed(receive_list):
            #         res += message
            #     send_message(chat_id, res)
            # finally:
            #     cnx.commit()
            #     cnx.close()
            #     help(chat_id)
            #     return
            print(chat_id)
            search_keyword_help(chat_id)
            #search_keyword(chat_id)
        elif text.startswith('/sub'):
            try:
                # cursor.execute("INSERT INTO subscribe (subscribe_id) VALUES (%d)" python bot.py 320460822:AAEX3Iu6cxClu4wG0GXyrosTvkK-Cr_5XIk% chat_id)
                # send_message(chat_id, "게시판 구독 신청이 완료되었습니다!.!")
                subscribe_help(chat_id)
            finally:
                cnx.commit()
                cnx.close()
                #help(chat_id)
                return
        elif text.startswith('/unsub'):
            try:
                # cursor.execute("DELETE FROM subscribe WHERE subscribe_id=(%d)" % chat_id)
                cancle_subscribe_help(chat_id)
            finally:
                cnx.commit()
                cnx.close()
                return
        elif text.startswith('/CNU'):
            try:
                send_message(chat_id, u'''
                안뇽^.^ 충남대학교 홈페이지의 정보를 가져오는 충비서야.

명령어 안내

학사정보 : 학사정보를 볼 수 있어
새소식  : 새소식을 볼 수 있어
교육정보 : 교육정보를 볼 수 있어
구인구직 : 구인구직정보를 볼 수 있어 ''')
                buttons = {'keyboard': [['새소식', '학사공지'], ['구인구직', '교육정보']]}
                bot.sendMessage(chat_id, '골라주세요 >.<', reply_markup=buttons)
            finally:
                cnx.commit()
                cnx.close()
                return
        elif text.startswith('/E'):
                send_message(chat_id, u'''
안뇽^.^ 이러닝 홈페이지의 정보를 가져오는 충비서야.
명령어 안내
자료실', '이러닝공지사항', '과제'  ''')
                buttons2 = {'keyboard': [['자료실', '이러닝공지사항'],['과제']]}
                bot.sendMessage(chat_id, '골라주세요 >.<', reply_markup=buttons2)
                return
        elif text.startswith('/CSE'):
            try:
                send_message(chat_id, u'''
안뇽^.^ 컴퓨터공학과 홈페이지의 정보를 가져오는 충비서야.
명령어 안내
'컴공공지사항', '일반소식', '사업단소식'  ''')
                buttons = {'keyboard': [['컴공공지사항', '일반소식'],['사업단소식']]}
                bot.sendMessage(chat_id, '골라주세요 >.<', reply_markup=buttons)
            finally:
                return
        elif text.startswith('/MENU'):
            try:
                send_message(chat_id, u'''
안뇽^.^ 충남대학교의 급식 메뉴 가져오는 충비서야.
명령어 안내
'2학', '3학'  ''')
                buttons = {'keyboard': [['2학', '3학']]}
                bot.sendMessage(chat_id, '골라주세요 >.<', reply_markup=buttons)
            finally:
                return
        elif text.startswith('/DORM'):
            try:
                send_message(chat_id, u'''
안뇽^.^ 충남대학교 기숙사 정보를 가져오는 충비서야.
명령어 안내
'급식', '공지사항'  ''')
                buttons = {'keyboard':[['급식', '기숙사공지사항']]}
                bot.sendMessage(chat_id, '골라주세요 >.<', reply_markup=buttons)
            finally:
                return
        else:
            cnx.commit()
            cnx.close()
            help(chat_id)
    elif text.startswith('&'):
        subscribe_board(chat_id, text)
    elif text.startswith('$'):
        cancle_subscribe(chat_id, text)
    elif text.startswith('2017'):
        search_keyword(chat_id)
    else:
        if text in CNU:
            if text == CNU_news:
                run_CNU("cnu_news")
            elif text == CNU_h_info:
                run_CNU("cnu_h_info")
            elif text == CNU_job:
                run_CNU("cnu_job")
            elif text == CNU_e_info:
                run_CNU("cnu_e_info")
        elif text in E:
            if text == E_ref:
                send_message(chat_id, ''' 이러닝 홈페이지 자료실 ''')
                run_E("e_ref")

            elif text == E_info:
                send_message(chat_id, ''' 이러닝 홈페이지 공지사항 ''')
                run_E("e_info")

            elif text == E_hw:
                send_message(chat_id, ''' 이러닝 홈페이지 과제실 ''')
                run_E_hw()

        elif text in CSE:
            if text == CSE_info:
                return
            elif text == CSE_g_info:
                return
            elif text == CSE_s_info:
                return
        elif text in MENU:
            if text == MENU_2:
                try:
                    send_message(chat_id, ''' 이번주 2학 메뉴 ''')
                    cursor.execute("SELECT id,menu,price,m_date FROM menu_2 ORDER BY id desc LIMIT 3")
                    receive_list = []
                    res = ''
                    for id,menu,price,m_date in cursor:
                        receive_list.append(u"글번호 : %s \n메뉴 : %s \n가격 : %s \n날짜 : %s \n \n\n" % (
                            id, menu, price, m_date))
                    for message in reversed(receive_list):
                        res += message
                    send_message(chat_id, res)
                finally:
                    cnx.commit()
                    cnx.close()
                    time.sleep(3)
                    help(chat_id)
                    return
            elif text == MENU_3:
                try:
                    send_message(chat_id, ''' 이번주 3학 메뉴''')
                    cursor.execute("SELECT id,menu,m_date FROM menu_3 ORDER BY id desc LIMIT 3")
                    receive_list = []
                    res = ''
                    for id, menu, m_date in cursor:
                        receive_list.append(u"글번호 : %s \n메뉴 : %s \n가격 : %s \n날짜 : %s \n \n\n" % (
                            id, menu,  m_date))
                    for message in reversed(receive_list):
                        res += message
                    send_message(chat_id, res)
                finally:
                    cnx.commit()
                    cnx.close()
                    time.sleep(3)
                    help(chat_id)
                    return
        elif text in DORM:
            if text == DORM_info:
                try:
                    send_message(chat_id, ''' 충남대 기숙사 공지사항 ''')
                    cursor.execute("SELECT id,title,link,writer,d_date FROM dorm_info ORDER BY id desc LIMIT 3")
                    receive_list = []
                    res = ''
                    for id,title,link,writer,d_date in cursor:
                        receive_list.append(u"글번호 : %s \n제목 : %s \n링크 : %s \n작성자 : %s\n작성일자 : %s\n\n" % (
                            id, title, link, writer, d_date))
                    for message in reversed(receive_list):
                        res += message
                    send_message(chat_id, res)
                finally:
                    cnx.commit()
                    cnx.close()
                    time.sleep(3)
                    help(chat_id)
                    return
            elif text == DORM_menu:
                try:
                    send_message(chat_id, ''' 충남대 기숙사 식사 메뉴 ''')
                    cursor.execute("SELECT id,menu,d_date FROM dorm_menu ORDER BY id desc LIMIT 3")
                    receive_list = []
                    res = ''
                    for id, menu, d_date in cursor:
                        receive_list.append(u"글번호 : %s \n메뉴 : %s \n날짜 : %s \n \n\n" % (
                            id, menu, d_date))
                    for message in reversed(receive_list):
                        res += message
                    send_message(chat_id, res)
                finally:
                    cnx.commit()
                    cnx.close()
                    time.sleep(3)
                    help(chat_id)
                    return
        else:
            cnx.commit()
            cnx.close()
            help(chat_id)

    # CNU_news, CNU_h_info, CNU_job, CNU_e_info
    def run_CNU(run_data):
        try:
            cursor.execute("SELECT id,title,link,writer,publish_date FROM ", run_data, " ORDER BY id desc LIMIT 10")
            receive_list = []
            res = ''
            for id, title, link, writer, publish_date in cursor:
                receive_list.append(u"글번호 : %s \n제목 : %s \n링크 : %s \n작성자 : %s\n작성일자 : %s\n\n" % (
                    id, title, link, writer, publish_date))
            for message in reversed(receive_list):
                res += message
            send_message(chat_id, res)
        finally:
            cnx.commit()
            cnx.close()
            help(chat_id)
            return

    # E_ref, E_info
    def run_E(run_data):
        try:
            cursor.execute("SELECT id,title,r_date FROM ", run_data," ORDER BY id desc LIMIT 10")
            receive_list = []
            res = ''
            for id, title, r_date in cursor:
                receive_list.append(u"글번호 : %s \n제목 : %s \n게시일자 : %s \n\n" % (
                    id, title, r_date))
            for message in reversed(receive_list):
                res += message
            send_message(chat_id, res)
        finally:
            cnx.commit()
            cnx.close()
            time.sleep(3)
            help(chat_id)
            return

    # E_hw
    def run_E_hw():
        try:
            cursor.execute("SELECT id,title,s_date,e_date,submit FROM e_hw ORDER BY id desc LIMIT 10")
            receive_list = []
            res = ''
            for id, title, s_date, e_date, submit in cursor:
                receive_list.append(u"글번호 : %s \n제목 : %s \n시작일 : %s \n종료일 : %s \n제출여부 : %s \n \n\n" % (
                    id, title, s_date, e_date, submit))
            for message in reversed(receive_list):
                res += message
            send_message(chat_id, res)
        finally:
            cnx.commit()
            cnx.close()
            time.sleep(3)
            help(chat_id)
            return


def new_message():
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()

    subscribe_user_list = []
    cursor.execute("SELECT subscribe_id FROM subscribe")
    for data in cursor.fetchall():
        subscribe_user_list.append(data[0])
    response = []
    id_list = []

    cursor.execute("SELECT id,title,link,writer,publish_date FROM cnu_h_info ORDER BY id desc LIMIT 3 ")
    for id, title, link, writer, publish_date in cursor:
        response.append(
            u"글번호 : %s \n제목 : %s \n링크 : %s \n작성자 : %s\n작성일자 : %s\n\n" % (id, title, link, writer, publish_date))
        id_list.append(id)

    for data in id_list:
        cursor.execute("UPDATE info_db set updated = 'N' WHERE id = '%s'" % (data))

    cnx.commit()
    cnx.close()

    for res in response:
        for chat_id in subscribe_user_list:
            send_message(chat_id, res)
    return

def search_keyword_help(id):
    send_message(id, '찾기를 원하는 키워드를 입력해주세요.')


def search_keyword(id):
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306',
                                  database='cnu_bachelor_info')
    cursor = cnx.cursor()

    subscribe_user_list = []
    cursor.execute("SELECT subscribe_id FROM subscribe")
    for data in cursor.fetchall():
        subscribe_user_list.append(data[0])
    response = []
    id_list = []
    result = []
    res =''
    chat_id = id
    m = re.compile('2017')
    cursor.execute("SELECT id,title,link,writer,publish_date FROM cnu_h_info ORDER BY id LIMIT 10 ")
    for id, title, link, writer, publish_date in cursor:
        response.append(
            u"글번호 : %s \n제목 : %s \n링크 : %s \n작성자 : %s\n작성일자 : %s\n\n" % (id, title, link, writer, publish_date))
        id_list.append(id)

        if m.match(title):
            str = title
            print(title)
            result.append(
                u"글번호 : %s \n제목 : %s \n링크 : %s \n작성자 : %s\n작성일자 : %s\n\n" % (id, title, link, writer, publish_date))

    for message in reversed(result):
        res += message

    print(chat_id)
    send_message(chat_id, res)

    cnx.commit()
    cnx.close()



def start():
    cnx = mysql.connector.connect(user='root', password='1234qwer', host='110.35.41.233', port='13306', database='cnu_bachelor_info')
    cursor = cnx.cursor()

    subscribe_user_list = []
    cursor.execute("SELECT subscribe_id FROM subscribe")
    for data in cursor.fetchall():
        subscribe_user_list.append(data[0])

    cnx.commit()
    cnx.close()

    for chat_id in subscribe_user_list:
        print(chat_id)
        help(chat_id)

    return


#TOKEN = sys.argv[1]
TOKEN = "320460822:AAEX3Iu6cxClu4wG0GXyrosTvkK-Cr_5XIk"
print('received token :', TOKEN)

bot = telepot.Bot(TOKEN)
start()
bot.message_loop(handle)
print('Listening...')
# search_keyword_help(292404252)

while 1:
    new_message()
    time.sleep(30)


