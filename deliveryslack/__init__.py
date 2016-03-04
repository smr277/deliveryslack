from tinydb import TinyDB

DB = TinyDB('./data/db.json')
DB_PKGS = DB.table('packages')
BOXOH_TOKEN = None
SLACK_TOKEN = None