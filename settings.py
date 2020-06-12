BOT_TOKEN = "" # Token of the bot given by the Discord Developer Portal (must be changed)

DB_NAME_TIGRIS = "./tigris.db" # Name of the file containing the SQLite main database
BALANCE_TABLE = "balance" # Name of the table containing the balances
TRANSACTION_TABLE = "transac" # Name of the table containing the transactions
JOB_TABLE = "job" # Name of the table containing the job details
NAME_TABLE = "name" # Name of the table containing the name of the users

ALLOWED_CHAN = ["general"] # Name of the channels on which the bot is allowed

ADMIN = [0] # Discord User ID of the admins (must be changed)
ADMIN_NAME = [""] # Name of the ADMIN, only for initialisation
INIT_MONEY = 100000000 # Amount of tigris for the first user

DEBUG = True

TAX_RATE = 0.1 # Percentage of taxes on each transaction.
TAX_TARGET = ADMIN[0]

# INVENTORY
DB_NAME_MARKETPLACE = "./marketplace.db" # Name of the file containing the SQLite marketplace database
OBJECT_TABLE = "object" # Name of the table containing the objects
FOR_SALE_TABLE = "for_sale" # Name of the table containing items to be sold