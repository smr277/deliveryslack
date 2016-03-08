import json
from datetime import datetime
import re
import imaplib
import email
import html2text

class EmailGrabber():
    def __init__(self, usr, pswd, server='imap.gmail.com'):
        self.mail = imaplib.IMAP4_SSL(server)
        self.mail.login(usr, pswd)
    
    '''
    Grab emails and return a list of tuples (from, body). Tries to parse html emails as well.
    @return <List>(<str>,<str>): Returns a list of tuples, where each tuple is (from, email body)
    '''
    def pull_emails(self):
        self.mail.select("inbox")
        result, data = self.mail.uid('search', None, "UNSEEN")
        if len(data[0]) < 1:
            return []
        latest_email_uid = data[0].split()
        #repeat what's under here for each email that came in. Parse them all!
        parsed_emails = []
        for itm in latest_email_uid:
            result, data = self.mail.uid('fetch', itm, '(RFC822)')
            raw_email = data[0][1]
            msg = email.message_from_string(raw_email)
            h = html2text.HTML2Text()
            h.ignore_links = True
            from_person = msg['From']
            from_person = from_person.split('@')
            from_person = from_person[-1]

            body = ""
            if msg.is_multipart():
                for payload in msg.get_payload():
                    # if payload.is_multipart(): ...
                    if payload.get_content_type() == 'text/html':
                        # body+= 
                        string = str(payload.get_payload(decode=True))
                        body+= h.handle(string)
                        continue
                    else:
                        try:
                            body+=str(payload.get_payload(decode=True))
                        except:
                            continue
            else:
                body+=msg.get_payload(decode=True)
            parsed_emails.append((from_person, body))
        return parsed_emails
