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
    queries.append("CREATE TABLE {} (user_id INTEGER, balance INTEGER, step INTEGER)".format(BALANCE_TABLE))
    queries.append("CREATE TABLE {} (from_id INTEGER, to_id INTEGER, amount INTEGER, comment TEXT, date TEXT)".format(TRANSACTION_TABLE))
    queries.append("CREATE TABLE {} (user_id INTEGER, name TEXT)".format(NAME_TABLE))
    for q in queries:
        conn.execute(q)

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

    def new_account(self, user_id, balance=0):
        if self.get_balance(user_id) >= 0:
            log_error("(new_account) user_id {} already in database".format(user_id))
            return False

        log_info("(new_account) Creating a new account for {}".format(user_id))
        query_insert = "INSERT INTO {}(user_id, balance, step) VALUES(?,?,?)".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_insert, (user_id, balance, 0))
        self.db.commit()

        return True


    def send(self, from_id, to_id, amount, message='', tax_free=False):
        assert amount >= 0
        amount = int(amount)
        if from_id == to_id:
            return 5
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

        # Tax
        if not tax_free and to_id != TAX_TARGET and from_id != TAX_TARGET and to_id not in TAX_FREE_USERS and from_id not in TAX_FREE_USERS:
            tax = int(amount * 0.1)
            amount -= tax
            ret_val = self.send(from_id, TAX_TARGET, tax, message="Tax")
            if ret_val != 0:
                return 4

        # Remove concurrency vulns ?
        self.db.execute("BEGIN")

        try:
            # Verify sufficient funds
            if balanceFrom < amount:
                log_error("(send) insufficiant funds from {}".format(from_id))
                self.db.rollback()
                return 3

            # Update balance
            query_update = "UPDATE {} SET balance = balance - ? WHERE user_id = ?".format(BALANCE_TABLE)
            cur = self.db.cursor()
            cur.execute(query_update, (amount, from_id))

            # Update balance
            query_update = "UPDATE {} SET balance = balance + ? WHERE user_id = ?".format(BALANCE_TABLE)
            cur = self.db.cursor()
            cur.execute(query_update, (amount, to_id))

            # Add transaction
            query_transac = "INSERT INTO {}(from_id, to_id, amount, comment, date) VALUES(?, ?, ?, ?, datetime('now', 'localtime'))".format(TRANSACTION_TABLE)
            cur = self.db.cursor()
            cur.execute(query_transac, (from_id, to_id, amount, message))

            self.db.commit()

            return 0
        except Exception as e:
            self.db.rollback()
            log_error("(send) Unknown exception in database transaction")
            log_error(e)
            return -1


    def get_history(self, user_id):
        balance = self.get_balance(user_id)
        if balance < 0:
            log_error("(get_history) user_id {} doesn't exist".format(user_id))
            return None

        query_fetch = "SELECT * FROM {} WHERE to_id = ? or from_id = ?".format(TRANSACTION_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id, user_id))
        return cur.fetchall()

    #def get_monthly_taxes(self, month=None):
    #    cur = self.db.cursor()
    #    query_tax = "SELECT SUM(amount) FROM {} WHERE comment = 'Tax'".format(TRANSACTION_TABLE)
    #    if month is None:
    #        query_filter = "AND date LIKE strftime('%Y-%m', 'now') || '%'"
    #        cur.execute(query_tax + query_filter)
    #    else:
    #        query_filter = " AND date LIKE ? || '%'"
    #        cur.execute(query_tax + query_filter, (month, ))
    #    sum_tax = cur.fetchone()[0]
    #    if sum_tax is None:
    #        log_error("(get_monthly_tax) No tax for the month {}".format(month))
    #    return sum_tax


    def get_citizens(self):
        query_citizens = "SELECT user_id FROM {}".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_citizens)
        citizens = cur.fetchall()
        return [i[0] for i in citizens]


    def get_income_step(self, user_id):
        query_fetch = "SELECT step FROM {} WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id,))
        step = cur.fetchone()
        if step is None:
            return None
        else:
            return step[0]

    def set_income_step(self, user_id, step):
        if self.get_balance(user_id) == -1:
            log_error("(set_income_step) User {} doesn't exist".format(user_id))
            return 1

        query = "UPDATE {} SET step = ? WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query, (step, user_id))
        return 0

    def get_all_steps(self):
        query_fetch = "SELECT user_id, step FROM {}".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        steps = cur.fetchall()

        return steps 


    def credit_income(self, to_id):
        step = self.get_income_step(to_id)

        income = INCOME_BASE + step * INCOME_STEP_VALUE
        # Finally, credit income
        log_info("(credit_income) Credit income, step {} ({}ŧ) to {}".format(step, income*100, to_id))

        self.credit(to_id, income*100, "Revenu universel palier {}".format(step))


    def credit(self, to_id, amount, message):
        # Update balance
        query_update = "UPDATE {} SET balance = balance + ? WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_update, (amount, to_id))

        # Add transaction
        query_transac = "INSERT INTO {}(from_id, to_id, amount, comment, date) VALUES(0, ?, ?, ?, datetime('now', 'localtime'))".format(TRANSACTION_TABLE)
        cur = self.db.cursor()
        cur.execute(query_transac, (to_id, amount, message))

    def payroll(self):
        citizens = self.get_citizens()
        ret_values = []
        log_info(citizens)
        for user_id in citizens:
            self.credit_income(user_id)
            ret_values.append(user_id)
        return ret_values

