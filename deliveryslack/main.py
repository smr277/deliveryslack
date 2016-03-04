import time
import argparse
import re
from slacker import Slacker

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from . import package
from . import email_grabber
from package import Package
from email_grabber import EmailGrabber
from deliveryslack import DB_PKGS, DB
import deliveryslack as ds
from tinydb import TinyDB, Query

class PackageHolder():
    def __init__(self, db_dict=None):
        self.packages = [] #list of package objects
        self.delivered = [] #list of packages that have been delivered
        if db_dict:
            print("Stuff in database...reading in")
            for itm in db_dict:
                pkg = Package(itm['tracking_num'], itm['sender'])
                pkg.status = itm['status']
                pkg.est_delivery = itm['est_delivery']
                self.need_to_print = False
                self.packages.append(pkg)

    '''
    email is a tuple (from, body)
    return a key,value pair unique to the package (key is the tracking number) 
    '''
    def extractor(self, email):
        #check if forwarded email:
        sender = re.findall('From: ([^~]+?)\n', email[1])
        if sender:
            email = (sender[0].strip(), email[1])
        #UPS
        match = re.findall("(1Z[0-9A-Z]{16})", email[1])
        if match:
            pkg = Package(match[0], email[0])
            self.packages.append(pkg)
            DB_PKGS.insert({'status':pkg.status, 'est_delivery':pkg.est_delivery, 'tracking_num':pkg.tracking_num, 'sender':pkg.sender})
            return pkg
        #TODO: Add the rest of them
        return None

    '''
    Check on all of the packages in the list of self.packages
    '''
    def update_packages(self):
        q_package = Query()
        for itm in self.packages:
            itm.check()
            DB_PKGS.update({'status': itm.status, 'est_delivery':itm.est_delivery}, q_package.tracking_num==itm.tracking_num)
            
        #Todo: if itm has been delivered, move to delivered

    '''
    Returns a string of the package updates
    '''
    def string_package_updates(self):
        string = ''
        for itm in self.packages:
            temp_string = itm.print_changed_status()
            if temp_string:
                string +=  temp_string
        return string


def main():
    while True:
        parser = argparse.ArgumentParser(description='Read from an email account and update a slack channel')
        parser.add_argument('--username', '-u', type=str, help='The username for the email server', nargs=1, required=True)
        parser.add_argument('--password', '-p', type=str, help='The password for the email server', nargs=1, required=True)
        parser.add_argument('--server', '-s', type=str, help='The server', nargs=1, required=False)
        parser.add_argument('--noslack', '-nps', help="Don't print to slack", action="store_false")
        parser.add_argument('--wait', '-w', help="Wait time before checking again, in minutes", nargs=1, type=int, default=10)
        parser.add_argument('--erase', '-e', help="Erase the database", action="store_true", default=False)
        parser.add_argument('--erase_tables', '-et', help="Erase just the pacakges in the database", action="store_true", default=False)
        parser.add_argument('--slack_channel', '-sc', help="The slack channel to post to", nargs=1, type=str, default='shipments')
        args = parser.parse_args()
        if args.erase:
            token_table = DB.table('token')
            token_table.purge()
            DB_PKGS.purge()
        if args.erase_tables:
            DB_PKGS.purge()

        q_token = Query()
        token_table = DB.table('token')
        grab = token_table.get(q_token.token_type == 'BOXOH_TOKEN')
        if grab:
            ds.BOXOH_TOKEN = grab.get('token')
        grab = token_table.get(q_token.token_type == 'SLACK_TOKEN')
        if grab:
            ds.SLACK_TOKEN = grab.get('token')

        if not ds.BOXOH_TOKEN:
            token = raw_input("Please enter your Boxoh Token. You only need to do this once: ")
            token_table.insert({'token_type':'BOXOH_TOKEN', 'token':token})
        if not ds.SLACK_TOKEN:
            token = raw_input("Please enter your Slack Token. You only need to do this once: ")
            token_table.insert({'token_type':'SLACK_TOKEN', 'token':token})
        print("Loaded tokens")

        if args.server:
            EG = EmailGrabber(args.username[0], args.password[0], server=args.server)
        else:
            EG = EmailGrabber(args.username[0], args.password[0])
        PH = PackageHolder(db_dict=DB_PKGS.all())
        slack = Slacker(ds.SLACK_TOKEN)
        slack.chat.post_message("#"+args.slack_channel[0], "Hi, I'm here to help with deliveries!", username="Fred, your delivery guy")

        emails = EG.pull_emails()
        for itm in emails:
            PH.extractor(itm)
        PH.update_packages()
        string = PH.string_package_updates()
        if string:
            try:
                slack.chat.post_message("#"+args.slack_channel[0], string, username="Fred, your delivery guy")
            except Exception as e:
                print("Slack failed: {}".format(e))
            print(string)
        time.sleep(args.wait*60)


if __name__ == '__main__':
    main()
