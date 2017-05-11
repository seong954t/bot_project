import pymysql.cursors
import datetime

# Connect to the database
connection = pymysql.connect(host='localhost', port=3306, user='root', passwd='1234qwer', db='cnu_bachelor_info', charset='utf8')

try:
    with connection.cursor() as cursor:
        # Create a new record
        input_data = (
            "asd",
            "http://plus.cnu.ac.kr/_prog/_board/?mode=V&no=2276265&code=sub07_0702&site_dvs_cd=kr&menu_dvs_cd=0702&skey=&sval=&site_dvs=&ntt_tag=&GotoPage=",
            "ad",
            datetime.datetime.now().date()
        )
        cursor.execute("""INSERT INTO info_db (title, link, writer, publish_date) VALUES (%s, %s, %s, %s)""", input_data)
    connection.commit()

finally:
    connection.close()
