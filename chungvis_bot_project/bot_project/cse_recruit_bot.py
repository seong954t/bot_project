# # -*- coding: utf-8 -*-
# # !/usr/bin/python
# import json
# import time
# import mysql.connector as mariadb
# import telepot
# import sys
# import os
# import logging
#
# LOG_PATH = os.path.abspath('log')
# logging.basicConfig(filename=os.path.join(LOG_PATH, "cse_recruit_bot.log"),
#                     format='%(asctime)s [%(levelname)s][%(filename)s:%(lineno)s] %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S',
#                     level=logging.DEBUG)
#
#
# def parse_config(filename):
#     f = open(filename, 'r')
#     js = json.loads(f.read())
#     f.close()
#     return js
#
#
# def get_config(config):
#     global CSE_RECRUIT_URI
#     global DB_HOST
#     global DB_PORT
#     global DB_USER
#     global DB_PASS
#     global DB_SCHEMA
#     CSE_RECRUIT_URI = config['crawling']['cse_recruit_uri']
#     DB_HOST = config['db']['db_host']
#     DB_PORT = config['db']['db_port']
#     DB_USER = config['db']['db_user']
#     DB_PASS = config['db']['db_pass']
#     DB_SCHEMA = config['db']['db_schema_telegram']
#
#
# def send_message(id, msg):
#     try:
#         bot.sendMessage(id, msg)
#     except:
#         print("error!")
#         logging.error("[message send error] chat_id : '%s'" % (id))
#
#
# def help(id):
#     send_message(id, u'''CSE 취업정보 게시판 알림 봇 입니다.
# 취업정보 게시판에 등록된 글을 텔레그램 메시지로 받을 수 있습니다^.^
#
# 명령어 사용법:
# /list : 최근 등록게시물 10개 조회
# /sub : 최신 글 등록 시 알람 받기
# /unsub : 알람 해제
# ''')
#
#
# def handle(msg):
#     mariadb_connection = mariadb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_SCHEMA,
#                                          charset='utf8')
#     cursor = mariadb_connection.cursor()
#     content_type, chat_type, chat_id = telepot.glance(msg)
#     logging.info("handle chat_id : '%s' / message : '%s' " % (chat_id, msg['text']))
#     if content_type != 'text':
#         send_message(chat_id, u'잘못된 입력입니다.')
#         return
#
#     text = msg['text']
#     res = ''
#     if text.startswith('/'):
#         if text.startswith('/list'):
#             try:
#                 cursor.execute("SELECT num,subject,href,name,date FROM cse_recruit ORDER BY id desc LIMIT 10")
#                 logging.info("[get list] chat_id : '%s'" % (chat_id))
#                 receive_list = []
#                 res = ''
#                 for num, subject, href, name, date in cursor:
#                     receive_list.append(u"글번호 : %s \n제목 : %s \n작성자 : %s \n작성일자 : %s\n%s\n\n" % (
#                         num, subject, name, date, href))
#                 for message in reversed(receive_list):
#                     res += message
#                 send_message(chat_id, res)
#             except mariadb.Error as error:
#                 logging.error("Error: {}".format(error))
#                 send_message(chat_id, u"리스트를 받아오던 중 문제가 발생했습니다. :<")
#             finally:
#                 mariadb_connection.close()
#                 return
#         elif text.startswith('/sub'):
#             try:
#                 cursor.execute("INSERT INTO cse_recruit_subscribe (user_id) VALUES ('%s')" % (chat_id))
#                 logging.info("[subscribe] chat_id : '%s'" % (chat_id))
#             except mariadb.Error as error:
#                 logging.error("Error: {}".format(error))
#                 send_message(chat_id, u"이미 알람 신청이 되어있습니다. :<")
#             else:
#                 mariadb_connection.commit()
#                 send_message(chat_id, u"알람 신청이 완료되었습니다. :D")
#             finally:
#                 mariadb_connection.close()
#                 return
#         elif text.startswith('/unsub'):
#             try:
#                 cursor.execute("DELETE FROM cse_recruit_subscribe WHERE user_id='%s'" % (chat_id))
#                 logging.info("[unsubscribe] chat_id : '%s'" % (chat_id))
#             except mariadb.Error as error:
#                 logging.error("Error: {}".format(error))
#                 send_message(chat_id, u"알람 해제가 실패했습니다. :<")
#             else:
#                 mariadb_connection.commit()
#                 send_message(chat_id, u"알람 해제가 완료되었습니다. :D")
#             finally:
#                 mariadb_connection.close()
#                 return
#         else:
#             mariadb_connection.close()
#             help(chat_id)
#     else:
#         mariadb_connection.close()
#         help(chat_id)
#
#
# def new_message():
#     mariadb_connection = mariadb.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_SCHEMA,
#                                          charset='utf8')
#     cursor = mariadb_connection.cursor()
#     subscribe_user_list = []
#     cursor.execute("SELECT user_id FROM cse_recruit_subscribe")
#     for data in cursor.fetchall():
#         subscribe_user_list.append(data[0])
#
#     cursor.execute("SELECT id,num,subject,href,name,date FROM cse_recruit WHERE new='Y'")
#
#     response = []
#     id_list = []
#     for id, num, subject, href, name, date in cursor:
# 	print num
# 	print subject
#
#         response.append(
#             u"글번호 : %s \n제목 : %s \n작성자 : %s \n작성일자 : %s\n%s\n\n" % (num, subject, name, date, href))
#         id_list.append(id)
#
#     for data in id_list:
#         cursor.execute("UPDATE cse_recruit set new = 'N' WHERE id = '%s'" % (data))
#
#     mariadb_connection.commit()
#     mariadb_connection.close()
#
#     for res in response:
#         for chat_id in subscribe_user_list:
#             send_message(chat_id, res)
#     return
#
#
# TOKEN = sys.argv[1]
# print('received token :', TOKEN
# logging.info("received token : '%s'" % (TOKEN))
#
# CONFIG_FILE = os.path.abspath("setting.json")
# config = parse_config(CONFIG_FILE)
# if not bool(config):
#     logging.error("Err: Setting file is not found")
#     print("Err: Setting file is not found")
#     exit()
# get_config(config)
#
# bot = telepot.Bot(TOKEN)
# bot.message_loop(handle)
# print 'Listening...'
#
# while 1:
#     new_message()
#     time.sleep(30)
