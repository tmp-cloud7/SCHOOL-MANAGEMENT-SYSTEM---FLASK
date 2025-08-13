import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', db='flask_sms')
cursor = conn.cursor()
cursor.execute('SELECT 1')
print(cursor.fetchone())
conn.close()
