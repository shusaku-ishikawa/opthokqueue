import json
import logging
import os
from datetime import datetime, timedelta
import time
from django.core.management.base import BaseCommand
from django.template.loader import get_template

import imaplib
import smtplib
import email
import re
import time
def get_smtp_server(host, user, passwd):
    server = smtplib.SMTP(host, 587)
    server.login(user, passwd)
    return server
def quit_smtp_serevr(server):
    server.quit()
def sendmail(server, mailto, mailfrom, subject, body):
    import smtplib  
    from email.mime.text import MIMEText
    
    # MIMETextを作成
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["To"] = mailto
    msg["From"] = mailfrom
    
    server.send_message(msg)

class Command(BaseCommand):
    help = 'メールチェック'
    def handle(self, *args, **options):
        #baseurl = 'http://stoneriver.info'
        baseurl = 'http://localhost:8000/queue/userentry'
        hostname = "opthok-navi.com"
        user = 'noreply'
        passwd = 'P@ssw0rd'
        myaddress = '{}@{}'.format(user, hostname)
        i = imaplib.IMAP4(hostname, 143)
        i.login(user, passwd)
        
        smtpserver = get_smtp_server(hostname, user, passwd)
        i.select("INBOX")

        time_started = time.time()
        while True:
            time_elapsed = time.time() - time_started
            if time_elapsed > 55.0:
                break;
            (ret, data) = i.search(None, 'UNDELETED')
            if ret != 'OK':
                continue
            datas = data[0].split()
            
            for num in datas:
                _, data = i.fetch(num,'(RFC822)')
                msg = email.message_from_string(data[0][1].decode('utf8'))
                fromaddr = msg.get('From') #print(data)
                print(fromaddr)
                m = re.search(r'(?<=\<).+\@.+(?=\>)', fromaddr)
                if not m:
                    i.store(num, '+FLAGS', '\\Deleted')
                    continue
                fromaddr = m.group(0)
                subject = msg.get('Subject')
                m = re.search(r'(?<=clinicId_).+', subject)
                if not m:
                    i.store(num, '+FLAGS', '\\Deleted')
                    continue
            
                clinic_id = m.group(0)
                body = '以下のURLから希望の日時を登録してください。\n'
                body += '{base}?email={email}&clinic={clinic}'.format(base = baseurl, email = fromaddr, clinic = clinic_id)
                sendmail(smtpserver, fromaddr, myaddress, '希望日時入力', body)
                i.store(num, '+FLAGS', '\\Deleted')
                time.sleep(3)
        i.expunge()
        quit_smtp_serevr(smtpserver)