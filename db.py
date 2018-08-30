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

def check_event(data):
    string = data.split(":")
    cursor = connection.cursor()
    sql = "SELECT * FROM history WHERE id=?,from_id=?,message=?,date=?,to_id=?"
    cursor.execute(sql,[string[1],string[2],string[3],string[4],string[5]])
    result = cursor.fetchone()
    if result != None:
        print("Попытка взлома!")
    else:
        string = (str())
        add_event()
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
    return last_tx

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

def get_transactions(wallet):
    cursor = connection.cursor()
    sql = """SELECT * FROM history WHERE from_id=?"""
    cursor.execute(sql, [str(wallet)])
    result = cursor.fetchall()
    return result