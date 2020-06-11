import db
import os
from log import *
from settings import *

def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        return

    queries = []
    queries.append("CREATE TABLE {} (user_id INTEGER, balance INTEGER)".format(BALANCE_TABLE))
    queries.append("CREATE TABLE {} (from_id INTEGER, to_id INTEGER, amount INTEGER, comment TEXT, date TEXT)".format(TRANSACTION_TABLE))
    queries.append("CREATE TABLE {} (user_id INTEGER, job_id INTEGER, title TEXT, salary INTEGER)".format(JOB_TABLE))
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
    conn.close()

class TigrisBank():
    """
    Interface with the database
    """
    def __init__(self, db_name=DB_NAME_TIGRIS):
        if not os.path.isfile(db_name):
            init_db(db_name)

        self.db = db.connect_db(db_name)
        if self.db is not None:
            log_info("DB {} succesfully loaded".format(db_name))
        else:
            log_error("Error opening tigris DB")

    def get_name(self, user_id):
        query_fetch = "SELECT name FROM {} WHERE user_id = ?".format(NAME_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id, ))
        name = cur.fetchone()
        if name is None:
            log_error("(get_name) Unknown user_id {}".format(user_id))
            return None
        return name[0]


    def set_name(self, user_id, name):
        # Set name
        query_insert = "INSERT INTO {}(user_id, name) VALUES(?,?)".format(NAME_TABLE)
        cur = self.db.cursor()
        cur.execute(query_insert, (user_id, name))
        self.db.commit()


    def get_all_balance(self):
        query_fetch = "SELECT * FROM {} ORDER BY balance DESC".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        balance = cur.fetchall()
        for b in balance:
            log_info(b)
        return balance

    def get_balance(self, user_id=None):
        query_fetch = "SELECT balance FROM {} WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id,))
        balance = cur.fetchone()
        if balance is None:
            log_error("(get_balance) user_id {} is not in the database".format(user_id))
            return -1 

        return balance[0]

    def new_account(self, user_id, balance=0.):
        if self.get_balance(user_id) >= 0:
            log_error("(new_account) user_id {} already in database".format(user_id))
            return False

        query_insert = "INSERT INTO {}(user_id, balance) VALUES(?,?)".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_insert, (user_id, balance))
        self.db.commit()

        return True


    def send(self, from_id, to_id, amount, message=''):
        assert from_id != to_id
        # Verify from_id exists in db
        balanceFrom = self.get_balance(from_id)
        if balanceFrom < 0:
            log_error("(send) user_id {} doesn't exist".format(from_id))
            return 1

        # Verify to_id exists in db
        balanceTo = self.get_balance(to_id)
        if balanceTo < 0:
            log_error("(send) user_id {} doesn't exist".format(to_id))
            return 2

        # Verify sufficient funds
        if balanceFrom < amount:
            log_error("(send) insufficiant funds from {}".format(from_id))
            return 3

        # Tax
        if to_id != TAX_TARGET and from_id != TAX_TARGET:
            tax = round(amount * 0.1, 3)
            amount -= tax
            ret_val = self.send(from_id, TAX_TARGET, tax, message="Tax")
            if ret_val != 0:
                return 4
            balanceFrom = self.get_balance(from_id)

        # Update balance
        query_update = "UPDATE {} SET balance = ? WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_update, (round(balanceFrom - amount, 3), from_id))

        # Update balance
        cur = self.db.cursor()
        cur.execute(query_update, (round(balanceTo + amount, 3), to_id))

        # Add transaction
        query_transac = "INSERT INTO {}(from_id, to_id, amount, comment, date) VALUES(?, ?, ?, ?, datetime('now', 'localtime'))".format(TRANSACTION_TABLE)
        cur = self.db.cursor()
        cur.execute(query_transac, (from_id, to_id, amount, message))

        self.db.commit()

        return 0


    def get_history(self, user_id):
        balance = self.get_balance(user_id)
        if balance < 0:
            log_error("(get_history) user_id {} doesn't exist".format(user_id))
            return None

        query_fetch = "SELECT * FROM {} WHERE to_id = ? or from_id = ?".format(TRANSACTION_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id, user_id))
        return cur.fetchall()


    def new_job(self, user_id, salary, title):
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
        query_new_job = "INSERT INTO {}(user_id, job_id, title, salary) VALUES(?, ?, ?, ?)".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_new_job, (user_id, job_id, title, salary))
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
        query_fetch = "SELECT user_id, job_id, title, salary FROM {} WHERE user_id = ? ORDER BY job_id ASC".format(JOB_TABLE)
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


    def get_salary(self, user_id):
        query_fetch = "SELECT SUM(salary) FROM {} WHERE user_id = ?".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id,))
        salary = cur.fetchone()[0]
        if salary is None:
            log_error("(get_salary) The user_id {} has no job".format(user_id))
            return None

        return salary


    def get_all_salaries(self):
        query_fetch = "SELECT user_id, SUM(salary) FROM {} GROUP BY user_id ORDER BY SUM(salary) DESC".format(JOB_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        salaries = cur.fetchall()

        return salaries


    def pay_salary(self, from_id, to_id, salary=None):
        # Create account if necessary
        if salary is None:
            # Fetch salary
            salary = self.get_salary(to_id)

        if salary == 0:
            log_info("(pay_salary) 0 salary for to_id {}".format(to_id))
            return 2

        if self.get_balance(to_id) < 0:
            # Create account
            self.new_account(to_id, "")

        from_b = self.get_balance(from_id)
        if from_b < 0:
            log_error("(pay_salary) from_id {} doesn't exists".format(from_id))
            return 1

        if from_b < salary:
            log_error("(pay_salary) from_id {} hasn't got sufficient funds".format(from_id))
            return 3


        # Finally, pay salary
        return self.send(from_id, to_id, salary, "Salary")


    def pay_all_salaries(self, from_id):
        salaries = self.get_all_salaries()
        ret_values = []
        for user_id, salary in salaries:
            ret_values.append((user_id, self.pay_salary(from_id, user_id, salary), salary))

        return ret_values


    def get_monthly_taxes(self, month=None):
        cur = self.db.cursor()
        query_tax = "SELECT SUM(amount) FROM {} WHERE comment = 'Tax'".format(TRANSACTION_TABLE)
        if month is None:
            query_filter = "AND date LIKE strftime('%Y-%m', 'now') || '%'"
            cur.execute(query_tax + query_filter)
        else:
            query_filter = " AND date LIKE ? || '%'"
            cur.execute(query_tax + query_filter, (month, ))
        sum_tax = cur.fetchone()[0]
        if sum_tax is None:
            log_error("(get_monthly_tax) No tax for the month {}".format(month))
        return sum_tax
