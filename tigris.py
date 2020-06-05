import db
from log import *
from settings import *

class TigrisBank():
    """
    Interface with the database
    """
    def __init__(self, db_name=DB_NAME):
        self.db = db.connect_db(db_name)
        if self.db is not None:
            log_info("DB succesfully loaded")
        else:
            log_error("Error opening DB")

    def get_all_balance(self):
        query_fetch = "SELECT * FROM {}".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        balance = cur.fetchall()
        for b in balance:
            log_info(b)

    def get_balance(self, user_id=None):
        query_fetch = "SELECT * FROM {} WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (user_id,))
        balance = cur.fetchone()
        if balance is None:
            log_error("(get_balance) user_id {} is not in the database".format(user_id))
            return -1 

        return balance[1]

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
        # Verify from_id exists in db
        balanceFrom= self.get_balance(from_id)
        if balanceFrom < 0:
            log_error("(send) user_id {} doesn't exist".format(from_id))
            return 1

        # Verify sufficient funds
        if balanceFrom < amount:
            log_error("(send) insufficiant funds from {}".format(from_id))
            return 3

        # Update balance
        query_update = "UPDATE {} SET balance = ? WHERE user_id = ?".format(BALANCE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_update, (balanceFrom - amount, from_id))

        # Verify to_id exists in db
        balanceTo = self.get_balance(to_id)
        if balanceTo < 0:
            log_error("(send) user_id {} doesn't exist".format(to_id))
            return 2

        # Update balance
        cur = self.db.cursor()
        cur.execute(query_update, (balanceTo + amount, to_id))

        # Add transaction
        query_transac = "INSERT INTO {}(from_id, to_id, amount, comment) VALUES(?, ?, ?, ?)".format(TRANSACTION_TABLE).format(TRANSACTION_TABLE)
        cur = self.db.cursor()
        cur.execute(query_transac, (from_id, to_id, amount, message))

        self.db.commit()

        return 0

