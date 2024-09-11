#!/usr/bin/python
# coding=UTF-8
# check_soon2expireAccount.py                                              #
# check AD account and send an email alert which will expire after 10 days #
# Create by 2022.09.02                                                     #
# Author : James Hsiao                                                     #
############################################################################
from datetime import datetime
import smtplib
import json
from ldap3 import Server, Connection, ALL, NTLM
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from datetime import datetime as DT

PWDLIFEDAYS = 180
PWDEXPIREDAYS = 10

#AD CONFIG
SERVERIP = '192.168.2.253'
QUERYACCOUNT = 'ADQSrvc'
QUERYPASSWORD = 'W96j02219N0z/8028U6fu4*'
QUERYBASEDN = 'ou=mitutoyo,dc=mitutoyo-tap,dc=co'

#MAIL CONFIG
MAILSERVER = 'mitumail.mitutoyo.com.tw'
SENDER = 'MIS.notify@mitutoyo.com.tw'
CC = ['jameshsiao@mitutoyo.com.tw']
#CC = 'yuyin.kuo@mitutoyo.com.tw'

def send_mail(send_from, send_to, send_cc, subject, text, files=None):
    #assert isinstance(mailreceiver, list)
    print(send_to)
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Cc'] = ', '.join(send_cc)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    result = 0
    try:
        smtp = smtplib.SMTP(MAILSERVER)
        recipients = [send_to]
        recipients.extend(send_cc)
        smtp.sendmail(send_from, recipients, msg.as_string())
        smtp.close()
        print('Send email to :' + send_to + 'msg' + msg.as_string() + '\n')
    except Exception as e:
        print('Send email error :'+ str(e) +'\n')
        result = 1
    return result

def conn_ldap():
    server = Server(SERVERIP, get_info=ALL)
    conn = Connection(server, user=QUERYACCOUNT, password=QUERYPASSWORD, auto_bind=True)
    print(conn)
    return conn

def get_enableUsers():
    with conn_ldap() as c:
        c.search(search_base=QUERYBASEDN,
                 search_filter='(&(objectClass=person)(userAccountControl=512))',
                 attributes=[
                     'name',
                     'mail',
                     'title',
                     'pwdLastSet'
                 ])
    return c.entries

def check_expiration(pwd_date):
    today = datetime.today()
    chgday = datetime.strptime(pwd_date, '%Y-%m-%d')
    diffday = today - chgday
    if diffday.days == PWDLIFEDAYS - PWDEXPIREDAYS:
        return diffday
    return 0

if True:
    enUser = []
    for entry in get_enableUsers():
        enUser.append(json.loads(entry.entry_to_json()))

    print(enUser)
    for infos in enUser:
        chkexpir = check_expiration(infos['attributes']['pwdLastSet'][0].split()[0])
        if chkexpir:
            if infos['attributes']['mail']:
                #print(infos['attributes']['name'][0])
                #print(infos['attributes']['pwdLastSet'][0])
                #print(chkexpir)
                nametext = infos['attributes']['name'][0]
                titletext = infos['attributes']['title'][0]
                mailtotext = infos['attributes']['mail'][0]
                msgtext = ''
                if titletext == '一般':
                    msgtext = nametext + ' ' + '您好 : ' + '\n\n您的開機密碼即將於10日後到期.\n\n請於到期日前, 在電腦畫面上按下 ctrl + alt + del , 並按下變更密碼.\n\n進行密碼變更, 變更完成後, \n\n' \
                                                             '無線網路以及Outlook, OneDrive等Office365服務也需要重新輸入新密碼進行驗證.\n\n因遠距可能無法正常修改密碼, 若有遇到密碼修改或設定問題, 請再與MIS聯繫.' \
                                                             '謝謝您.\n\n\n\n管理部 MIS\n\n\n\n此為系統通知信箱,請勿直接回信,謝謝.'
                else:
                    msgtext = nametext + ' ' + titletext + ' 您好 : ' + '\n\n您的開機密碼即將於10日後到期.\n\n請於到期日前, 在電腦畫面上按下 ctrl + alt + del , 並按下變更密碼.\n\n進行密碼變更, 變更完成後, \n\n' \
                                                             '無線網路以及Outlook, OneDrive等Office365服務也需要重新輸入新密碼進行驗證.\n\n因遠距可能無法正常修改密碼, 若有遇到密碼修改或設定問題, 請再與MIS聯繫.' \
                                                             '謝謝您.\n\n\n\n管理部 MIS\n\n\n\n此為系統通知信箱,請勿直接回信,謝謝.'
                #send_mail('MIS.notification@mitutoyo.com.tw', mailtotext, '[MIS通知]您的開機密碼即將到期, 請於到期日前更換', msgtext)
                mailtotext = 'yuyin.kuo@mitutoyo.com.tw'
                send_mail(SENDER, mailtotext, CC, '[MIS通知]您的開機密碼即將於10日後到期, 請於到期日前更換', msgtext)