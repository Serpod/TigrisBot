import db
import os
import sqlite3
from log import *
from settings import *

def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        return

    queries = []
    queries.append("CREATE TABLE {} (creator_id INTEGER, owner_id INTEGER, name TEXT, description TEXT, item_id INTEGER, creation_date TEXT)".format(ITEM_TABLE))
    queries.append("CREATE TABLE {} (seller_id INTEGER, item_id INTEGER, price INTEGER, buyer_id INTEGER)".format(FOR_SALE_TABLE))
    for q in queries:
        conn.execute(q)

    conn.commit()
    conn.close()

class Marketplace():
    """
    Interface with the database
    """
    def __init__(self, db_name=DB_NAME_MARKETPLACE):
        if not os.path.isfile(db_name):
            init_db(db_name)

        self.db = db.connect_db(db_name)
        if self.db is not None:
            log_info("DB {} succesfully loaded".format(db_name))
        else:
            log_error("Error opening marketplace DB")


    def get_inventory(self, user_id):
        query_inventory = "SELECT creator_id, name, description, item_id, creation_date FROM {} WHERE owner_id = ?".format(ITEM_TABLE)
        cur = self.db.cursor()
        cur.execute(query_inventory, (user_id, ))
        inventory = cur.fetchall()

        if inventory is None:
            log_error("(get_inventory) No item for user_id {}".format(user_id))

        return inventory


    def create_item(self, user_id, name, description):
        # Only one item each day per user
        today = "strftime('%Y-%m-%d', 'now')"
        query_created_today = "SELECT * FROM {} WHERE creation_time = {} and creator_id = ?".format(ITEM_TABLE, today)
        cur = self.db.cursor()
        cur.execute(query_created_today, (user_id, ))
        obj = cur.fetchone()
        if obj is not None:
            log_error("(create_item) {} is trying to create a second item today".format(user_id))
            return False

        # Compute new item_id
        query_max_item_id = "SELECT MAX(item_id) FROM {}".format(ITEM_TABLE)
        cur = self.db.cursor()
        cur.execute(query_max_item_id, (user_id,))
        max_item_id = cur.fetchone()[0]
        if max_job_id is None:
            # First item
            item_id = 0
        else:
            item_id = max_item_id + 1

        query_create = "INSERT INTO {} (creator_id, owner_id, name, description, item_id, creation_date) VALUES (?, ?, ?, ?, ?, {})".format(ITEM_TABLE, today)
        cur = self.db.cursor()
        cur.execute(query_create, (user_id, user_id, name, description, item_id))
        self.db.commit()
        return True

    
    def is_owner(self, user_id, item_id):
        query_isowner = "SELECT * FROM {} WHERE owner_id = ? AND item_id = ?".format(ITEM_TABLE)
        cur = self.db.cursor()
        cur.execute(query_isowner, (user_id, item_id))
        obj = cur.fetchone()
        if obj is None:
            log_error("(is_owner) The user_id {} is not the owner of {}".format(user_id, item_id))
            return False
        return True


    def delete_item(self, user_id, item_id):
        if not self.is_owner(user_id, item_id):
            return False

        query_delete = "DELETE FROM {} WHERE owner_id = ? AND item_id = ?"
        cur = self.db.cursor()
        cur.execute(query_delete, (user_id, item_id))
        self.db.commit()
        return True


    def is_for_sale(self, item_id):
        query_is_for_sale = "SELECT * FROM {} WHERE item_id = ?".format(FOR_SALE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_is_for_sale, (item_id, ))
        obj = cur.fetchone()
        if obj is None:
            return False
        return True


    def sell(self, seller_id, item_id, price, buyer_id=None):
        # Check if the user has the item he's trying to sell
        if not self.is_owner(seller_id, item_id):
            return 1

        # Check that the item is not currently being sold
        if is_for_sale(item_id):
            log_error("(sell) {} is already for sale".format(item_id))
            return 2

        query_sell = "INSERT INTO {} (seller_id, item_id, price, buyer_id) VALUES (?, ?, ?, ?)".format(FOR_SALE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_sell, seller_id, item_id, price, buyer_id)
        self.db.commit()
        return 0


    def cancel_sale(self, user_id, item_id):
        None

    
    def buy(self, from_id, item_id, to_id, token):
        # Check if the token is right
        # Check if from_id and to_id are right
        # Change item owner
        # Send money
        None
