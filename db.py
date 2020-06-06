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

    query_create1 = "CREATE TABLE {} (user_id INTEGER, balance REAL)".format(BALANCE_TABLE)
    query_create2 = "CREATE TABLE {} (from_id INTEGER, to_id INTEGER, amount INTEGER, comment TEXT, date TXT)".format(TRANSACTION_TABLE)
    conn.execute(query_create1)
    conn.execute(query_create2)

    query_init = "INSERT INTO {} VALUES (?, ?)".format(BALANCE_TABLE)
    conn.execute(query_init, (ADMIN[0], INIT_MONEY))
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
