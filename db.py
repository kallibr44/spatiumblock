import sqlite3
import datetime
import time
connection = object
def init():
    global connection
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE if not exists history
                      (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, from_id, message text,
                       to_id text, date int)
                   """)
    cur.execute("""CREATE TABLE if not exists client
                      (wallet varchar, public_key varchar, private_key varchar)
                   """)
    connection = conn

def add_event(string):
    data = string.split(":")
    cursor = connection.cursor()
    sql = """INSERT INTO history(from_id,message,to_id,date) VALUES(?,?,?,?)"""
    cursor.execute(sql, [data[0],data[1],data[2],str(int(time.time()))])
    connection.commit()

def get_last_transaction():
    cursor = connection.cursor()
    sql = "SELECT * FROM history ORDER BY ID DESC LIMIT 1"
    cursor.execute(sql)
    last_tx = cursor.fetchone()
    print(last_tx)

def create_user(public_key):
    cursor = connection.cursor()
    sql= """INSERT INTO client(public_key) VALUES(?,?)"""
    cursor.execute(sql, [public_key,private_key])
    connection.commit()

def get_key():
    cursor = connection.cursor()
    cursor.execute("SELECT public_key FROM client")
    data = cursor.fetchone()
    return data

if __name__ == '__main__':
   init()
   add_event("Я:пока:Вадим")
   get_last_transaction()
   time.sleep(1)
   add_event("Вадим:пока:Я")
   get_last_transaction()
