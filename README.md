# TigrisBot

## Warning
Be aware that this code was made quickly and is certainly really dirty. Do not hesitate to open some issues or pull requests if you want to contribute (refactor, implement new features, remove bugs or typos, ...).

## Quick description of the project
### main.py

Bot discord interface. Parse messages and prepare parameters for the database.

### db.py

Load the SQLite database.

### tigris.py

Contains a class (`TigrisBank`) which interacts with the database to implement actions (`get_balance`, `new_account`, `send`).

### utils.py

Simple utility functions to ease interactiosn.

### log.py

Some functions to manage logs.

### settings.py

Configuration constants. Not present in this repository for security purpose.
