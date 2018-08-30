import sqlite3
import datetime
import time
cursor = object

def init():
    global cursor
    connection = sqlite3.connect("db.sqlite")
    cur = connection.cursor()
    cur.execute("""CREATE TABLE if not exists history
                      (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, from_id, message text,
                       to_id text, date int)
                   """)
    cur.execute("""CREATE TABLE if not exists client
                      (wallet varchar, public_key varchar, private_key varchar)
                   """)
    cursor = cur

def add_event(string):
    data = string.split(":")
    sql = """INSERT INTO history(from_id,message,to_id,date) VALUES(?,?,?,?)"""
    print(sql)
    cursor.execute(sql, [data[0],data[1],data[2],str(int(time.time()))])

def get_last_transaction():
    sql = "SELECT * FROM history ORDER BY ID LIMIT 1"
    cursor.execute(sql)
    last_tx = cursor.fetchone()
    print(last_tx)


if __name__ == '__main__':
   init()
   add_event("Я:привет:Вадим")
   get_last_transaction()
