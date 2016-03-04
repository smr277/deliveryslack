from tinydb import TinyDB
import os

direct = os.path.expanduser("~/.deliveryslack/")
try:
    DB = TinyDB(os.path.join(direct,"db.json"))
except:
    os.mkdir(direct)
    DB = TinyDB(os.path.join(direct,"db.json"))
DB_PKGS = DB.table('packages')
BOXOH_TOKEN = None
SLACK_TOKEN = None
__version__ = '0.5.0'