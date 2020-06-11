import db
from log import *
from settings import *

def init_db(filename):
    try:
        conn = sqlite3.connect(filename)
    except Exception as e:
        log_error(e)
        return

    queries = []
    queries.append("CREATE TABLE {} (creator_id INTEGER, owner_id INTEGER, name TEXT, description TEXT, object_id INTEGER, creation_date TEXT)".format(OBJECT_TABLE))
    queries.append("CREATE TABLE {} (seller_id INTEGER, object_id INTEGER, price INTEGER, buyer_id INTEGER)".format(FOR_SALE_TABLE))
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
        query_inventory = "SELECT creator_id, name, description, object_id, creation_date FROM {} WHERE owner_id = ?".format(OBJECT_TABLE)
        cur = self.db.cursor()
        cur.execute(query_inventory, (user_id, ))
        inventory = cur.fetchall()

        if inventory is None:
            log_error("(get_inventory) No objects for user_id {}".format(user_id))

        return inventory


    def create_object(self, user_id, name, description):
        # Only one object each day
        today = "strftime('%Y-%m-%d', 'now')"
        query_created_today = "SELECT * FROM {} WHERE creation_time = {} and creator_id = ?".format(OBJECT_TABLE, today)
        cur = self.db.cursor()
        cur.execute(query_created_today, (user_id, ))
        obj = cur.fetchone()
        if obj is not None:
            log_error("(create_object) {} is trying to create a second object today".format(user_id))
            return False

        # Compute new object_id
        query_max_object_id = "SELECT MAX(object_id) FROM {}".format(OBJECT_TABLE)
        cur = self.db.cursor()
        cur.execute(query_max_object_id, (user_id,))
        max_object_id = cur.fetchone()[0]
        if max_job_id is None:
            # First object
            object_id = 0
        else:
            object_id = max_object_id + 1

        query_create = "INSERT INTO {} (creator_id, owner_id, name, description, object_id, creation_date) VALUES (?, ?, ?, ?, ?, {})".format(OBJECT_TABLE, today)
        cur = self.db.cursor()
        cur.execute(query_create, (user_id, user_id, name, description, object_id))
        self.db.commit()
        return True

    
    def is_owner(self, user_id, object_id):
        query_isowner = "SELECT * FROM {} WHERE owner_id = ? AND object_id = ?".format(OBJECT_TABLE)
        cur = self.db.cursor()
        cur.execute(query_isowner, (user_id, object_id))
        obj = cur.fetchone()
        if obj is None:
            log_error("(is_owner) The user_id {} is not the owner of {}".format(user_id, object_id))
            return False
        return True


    def delete_object(self, user_id, object_id):
        if not self.is_owner(user_id, object_id):
            return False

        query_delete = "DELETE FROM {} WHERE owner_id = ? AND object_id = ?"
        cur = self.db.cursor()
        cur.execute(query_delete, (user_id, object_id))
        self.db.commit()
        return True


    def is_for_sale(self, object_id):
        query_is_for_sale = "SELECT * FROM {} WHERE object_id = ?".format(FOR_SALE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_is_for_sale, (object_id, ))
        obj = cur.fetchone()
        if obj is None:
            return False
        return True


    def sell(self, seller_id, object_id, price, buyer_id=None):
        # Check if the user has the object he's trying to sell
        if not self.is_owner(seller_id, object_id):
            return 1

        # Check that the object is not currently being sold
        if is_for_sale(object_id):
            log_error("(sell) {} is already for sale".format(object_id))
            return 2

        query_sell = "INSERT INTO {} (seller_id, object_id, price, buyer_id) VALUES (?, ?, ?, ?)".format(FOR_SALE_TABLE)
        cur = self.db.cursor()
        cur.execute(query_sell, seller_id, object_id, price, buyer_id)
        self.db.commit()
        return 0


    def cancel_sale(self, user_id, object_id):
        None

    
    def buy(self, from_id, object_id, to_id, token):
        # Check if the token is right
        # Check if from_id and to_id are right
        # Change object owner
        # Send money
        None
