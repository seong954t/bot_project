import requests
from bs4 import BeautifulSoup
import json
import mysql.connector
import os

def parse_config(filename):
    f = open(filename, 'r')
    js = json.loads(f.read())
    f.close()
    return js


def get_config(config):
    global URI
    global PAGE_SPT
    global DB_NAME
    URI = config['uri']['clien']
    PAGE_SPT = config['uri']['page_spt']
    DB_NAME = config['db']['name']


def crawl(uri):
    r = requests.get(uri)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find('table', {'class': "tb_lst_normal"})
    tbody = table.find('tbody')
    tr_list = tbody.find_all('tr')

    db_insert_list = []

    for tr in tr_list:
        wrap_div = tr.td.div
        wrap_span = tr.td.div.span
        if not wrap_span is None:
                if not wrap_span.img is None:
                    continue
        else:
            title = wrap_div.find('span', {"class": "lst_tit"}).get_text()
            href = uri[:-14] + wrap_div['onclick'][15:-1] + PAGE_SPT
            data = (title, href)
            db_insert_list.append(data)

    inputData(db_insert_list)


def inputData(list):
    # DEFAULT SETTING : host='127.0.0.1', port='3306',charset='utf8'
    cnx = mysql.connector.connect(user='root', password='1234qwer', database='cnu_bachelor_info')
    cursor = cnx.cursor()
    print(list[0])
    stmt = "INSERT INTO info_db (title, link, writer, publish_date) VALUES (%s, %s, %s, %s)"
    # ON DUPLICATE KEY UPDATE title = VALUES(title)
    cursor.execute(stmt, list)
    # cursor.executemany(stmt, list)
    cnx.commit()
    cnx.close()


CONFIG_FILE = os.path.abspath("settings.json")
config = parse_config(CONFIG_FILE)
if not bool(config):
    print("Err: Setting file is not found")
exit()
get_config(config)
crawl(URI)