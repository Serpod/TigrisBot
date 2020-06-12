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
    queries.append("CREATE TABLE {} (seller_id INTEGER, buyer_id INTEGER, price INTEGER, name TEXT, date TEXT)".format(TRADE_TABLE))
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


    def get_item_by_id(self, item_id):
        query_fetch = "SELECT creator_id, owner_id, name, description, creation_date FROM {} WHERE item_id = ?".format(ITEM_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch, (item_id,))
        return cur.fetchone()

    def get_inventory(self, user_id):
        query_inventory = "SELECT creator_id, name, description, item_id, creation_date FROM {} WHERE owner_id = ?".format(ITEM_TABLE)
        cur = self.db.cursor()
        cur.execute(query_inventory, (user_id, ))
        inventory = cur.fetchall()

        if not inventory:
            log_error("(get_inventory) No item for user_id {}".format(user_id))

        return inventory


    def create_item(self, user_id, name, description):
        # Only one item each day per user
        self.db.execute("BEGIN")
        try:

            today = "strftime('%Y-%m-%d', 'now')"
            query_created_today = "SELECT * FROM {} WHERE creation_date = {} and creator_id = ?".format(ITEM_TABLE, today)
            cur = self.db.cursor()
            cur.execute(query_created_today, (user_id, ))
            obj = cur.fetchone()
            if obj is not None:
                log_error("(create_item) {} is trying to create a second item today".format(user_id))
                self.db.rollback()
                return False

            # Compute new item_id
            query_max_item_id = "SELECT MAX(item_id) FROM {}".format(ITEM_TABLE)
            cur = self.db.cursor()
            cur.execute(query_max_item_id)
            max_item_id = cur.fetchone()[0]
            if max_item_id is None:
                # First item
                item_id = 0
            else:
                item_id = max_item_id + 1

            query_create = "INSERT INTO {} (creator_id, owner_id, name, description, item_id, creation_date) VALUES (?, ?, ?, ?, ?, {})".format(ITEM_TABLE, today)
            cur = self.db.cursor()
            cur.execute(query_create, (user_id, user_id, name, description, item_id))

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            log_error("(send) Unknown exception in database transaction")
            log_error(e)
            return False

    
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

        query_delete = "DELETE FROM {} WHERE owner_id = ? AND item_id = ?".format(ITEM_TABLE)
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
        assert price >= 0
        self.db.execute("BEGIN")

        try:
            # Check if the user has the item he's trying to sell
            if not self.is_owner(seller_id, item_id):
                self.db.rollback()
                return 1

            # Check that the item is not currently being sold
            if self.is_for_sale(item_id):
                self.db.rollback()
                log_error("(sell) {} is already for sale".format(item_id))
                return 2

            query_sell = "INSERT INTO {} (seller_id, item_id, price, buyer_id) VALUES (?, ?, ?, ?)".format(FOR_SALE_TABLE)
            cur = self.db.cursor()
            cur.execute(query_sell, (seller_id, item_id, price, buyer_id))

            self.db.commit()
            return 0
        except Exception as e:
            self.db.rollback()
            log_error("(send) Unknown exception in database transaction")
            log_error(e)
            return -1


    def cancel_sale(self, seller_id, item_id):
        if not self.is_owner(seller_id, item_id):
            return 1
        if not self.is_for_sale(item_id):
            return 2

        query_cancel = "DELETE FROM {} WHERE seller_id = ? AND item_id = ?".format(FOR_SALE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_cancel, (seller_id, item_id))
        self.db.commit()
        return 0


    def give(self, from_id, to_id, item_id):
        self.db.execute("BEGIN")
        try:
            if not self.is_owner(from_id, item_id):
                self.db.rollback()
                return 1
            if self.is_for_sale(item_id):
                self.db.rollback()
                return 2
            query_transfer_ownership = "UPDATE {} SET owner_id = ? WHERE item_id = ?".format(ITEM_TABLE)
            cur = self.db.cursor()
            cur.execute(query_transfer_ownership, (to_id, item_id))
            self.db.commit()
            return 0
        except:
            self.db.rollback()
            return -1


    def get_for_sale_items(self):
        query_fetch = "SELECT {1}.name, {0}.item_id, {0}.price, {0}.seller_id, {0}.buyer_id FROM {0} JOIN {1} ON {0}.item_id = {1}.item_id".format(FOR_SALE_TABLE, ITEM_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        return cur.fetchall()


    def get_all_trades(self):
        query_fetch = "SELECT seller_id, buyer_id, price, name, date FROM {}".format(TRADE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_fetch)
        trades = cur.fetchall()
        return trades


    def buy(self, buyer_id, item_id, bank):
        # Remove concurrency vulns ?
        self.db.execute("BEGIN")

        try:
            # Check item is for sale, and for the right buyer
            query_getsale = "SELECT buyer_id, seller_id, price FROM {} WHERE item_id = ?".format(FOR_SALE_TABLE)
            cur = self.db.cursor()
            cur.execute(query_getsale, (item_id, ))
            data = cur.fetchone()
            if data is None:
                self.db.rollback()
                return 6
            if data[0] is not None and data[0] != buyer_id:
                self.db.rollback()
                return 7

            item = self.get_item_by_id(item_id)
            item_name = item[2]

            # Send money
            ret_val = bank.send(buyer_id, data[1], data[2], "Buy: {} ({})".format(item_name, item_id))
            if ret_val:
                self.db.rollback()
                return ret_val

            self.cancel_sale(data[1], item_id)
            # Change item owner
            query_transfer_ownership = "UPDATE {} SET owner_id = ? WHERE item_id = ?".format(ITEM_TABLE)
            cur = self.db.cursor()
            cur.execute(query_transfer_ownership, (buyer_id, item_id))

            item_name = self.get_item_by_id(item_id)[2]

            query_add_trade = "INSERT INTO {} (seller_id, buyer_id, price, name, date) VALUES (?, ?, ?, ?, datetime('now'))".format(TRADE_TABLE)
            cur = self.db.cursor()
            cur.execute(query_add_trade, (data[1], buyer_id, data[2], item_name))

            self.db.commit()
            return 0
        except Exception as e:
            self.db.rollback()
            log_error("(send) Unknown exception in database transaction")
            log_error(e)
            return -1
