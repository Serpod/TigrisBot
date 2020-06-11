import sqlite3
from settings import *
import os
from log import *



def connect_db(filename):
    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        conn = None
    return conn

def close_db(conn):
    if conn is not None:
        conn.close()
