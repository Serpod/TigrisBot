import db
import os
from log import *
from settings import *
import sqlite3

def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        return

    queries = []
    queries.append("CREATE TABLE {} (user_id INTEGER, job_id INTEGER, title TEXT)".format(JOB_TABLE))
    for q in queries:
        conn.execute(q)
    conn.close()

class JobsManager():
    def __init__(self, db_name=DB_NAME_JOBS):
        if not os.path.isfile(db_name):
            init_db(db_name)

        self.db = db.connect_db(db_name)
        if self.db is not None:
            log_info("DB {} succesfully loaded".format(db_name))
        else:
            log_error("Error opening jobs DB")

    def new_job(self, user_id, title):
        # Someone can have a job without an account. One will be created at pay time.

        # Compute new job_id
        query_max_job_id = "SELECT MAX(job_id) FROM {} WHERE user_id = ?".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_max_job_id, (user_id,))
        max_job_id = cur.fetchone()[0]
        if max_job_id is None:
            # First job
            job_id = 0
        else:
            job_id = max_job_id + 1

        # Insert new job
        query_new_job = "INSERT INTO {}(user_id, job_id, title) VALUES(?, ?, ?, ?)".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_new_job, (user_id, job_id, title))
        self.db.commit()

        return 0

    def get_job(self, user_id, job_id):
        query_fetch = "SELECT * FROM {} WHERE user_id = ? AND job_id = ?".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id, job_id))
        job = cur.fetchone()

        return job

    def remove_job(self, user_id, job_id):
        job = self.get_job(user_id, job_id)
        if job is None:
           log_error("(remove_job) The job ({}) for user_id {} doesn't exist".format(job_id, user_id))
           return None

        query_delete = "DELETE FROM {} WHERE user_id = ? AND job_id = ?".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_delete, (user_id, job_id))
        self.db.commit()

        return job


    def get_jobs(self, user_id):
        query_fetch = "SELECT user_id, job_id, title FROM {} WHERE user_id = ? ORDER BY job_id ASC".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id, ))
        jobs = cur.fetchall()

        return jobs


    def get_all_jobs(self):
        query_fetch = "SELECT * FROM {} ORDER BY  user_id ASC, job_id ASC".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        jobs = cur.fetchall()

        return jobs





