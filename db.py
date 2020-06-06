import sqlite3
from settings import *
import os
from log import *

def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        return

    queries = []
    queries.append("CREATE TABLE {} (user_id INTEGER, balance REAL)".format(BALANCE_TABLE))
    queries.append("CREATE TABLE {} (from_id INTEGER, to_id INTEGER, amount INTEGER, comment TEXT, date TXT)".format(TRANSACTION_TABLE))
    queries.append("CREATE TABLE {} (user_id INTEGER, name TEXT)".format(NAME_TABLE))
    for q in queries:
        conn.execute(q)

    # Account that will hold all the money
    query_init = "INSERT INTO {}(user_id, balance) VALUES (?, ?)".format(BALANCE_TABLE)
    conn.execute(query_init, (ADMIN[0], INIT_MONEY))
    conn.commit()
    query_init = "INSERT INTO {}(user_id, name) VALUES (?, ?)".format(NAME_TABLE)
    conn.execute(query_init, (ADMIN[0], ADMIN_NAME[0]))
    conn.commit()

def connect_db(filename):
    if not os.path.isfile(filename):
        init_db(filename)

    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        conn = None
    return conn

def close_db(conn):
    if conn is not None:
        conn.close()
