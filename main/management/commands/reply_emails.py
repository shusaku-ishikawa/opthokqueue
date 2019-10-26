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
        hostname = "stoneriver.info"
        user = 'contact'
        passwd = '332191-Aa'
        myaddress = '{}@{}'.format(user, hostname)
        i = imaplib.IMAP4(hostname, 143)
        i.login(user, passwd)
        i.select("INBOX")
        (ret, data) = i.search(None, 'UNDELETED')
        if ret != 'OK':
            print('Error occurs')
            exit(0)
        datas = data[0].split()
        
        smtpserver = get_smtp_server(hostname, user, passwd)
        for num in datas:
            _, data = i.fetch(num,'(RFC822)')
            msg = email.message_from_string(data[0][1].decode('utf8'))
            fromaddr = msg.get('From') #print(data)
            m = re.search(r'(?<=\<).+\@.+(?=\>)', fromaddr)
            fromaddr = m.group(0)
            subject = msg.get('Subject')
            m = re.search(r'(?<=clinicId=).+', subject)
            if m == None:
                print('clinic id not identified:{}'.format(num))
                continue
        
            clinic_id = m.group(0)
            print(clinic_id)
            body = '以下のURLから希望の日時を登録してください。\n'
            body += '{base}?email={email}&clinic={clinic}'.format(base = baseurl, email = fromaddr, clinic = clinic_id)
            sendmail(smtpserver, fromaddr, myaddress, '希望日時入力', body)
        quit_smtp_serevr(smtpserver)