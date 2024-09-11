#!/usr/bin/python3
import Adafruit_DHT
from datetime import datetime
import time
import logging
import smtplib

pin = 4
fromaddr = 'ks-rpi3@mitutoyo.com.tw'
toaddrs = 'mitutoyo.sysalert@mitutoyo.com.tw'
sensor = Adafruit_DHT.DHT22
ALERTHumidity = 70
ALERTTemperature = 30
NOTIFYTIME = '09'
humidity = -1
temperature = -1

def set_log(date):
    logging.basicConfig(filename='/home/mis/workspace/TmpHmyLog{0}.log'.format(date), filemode='a', level=logging.INFO)


def get_humidity() :
    hum, tmp = Adafruit_DHT.read_retry(sensor, pin)
    if hum is not None and tmp is not None:
        return '{0:0.1f}'.format(tmp), '{0:0.1f}'.format(hum)
    else :
        ruturn -1, -1


def sent_mail_notify(data):
    subject = '[Notify] KS Control Room Temperature&Humidity'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
           % (fromaddr, toaddrs, subject))
    msg = msg + data
    print(msg)
    server = smtplib.SMTP('smtp.mitutoyo.com.tw')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


def send_mail_alert(data):
    subject = '[ALERT] KS Control Room Temperature&Humidity'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
           % (fromaddr, toaddrs, subject))
    msg = msg + data
    print(msg)
    server = smtplib.SMTP('smtp.mitutoyo.com.tw')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
    

if __name__ == '__main__':
    now = datetime.now()
    set_log(now.date())
    temperature,humidity = get_humidity()
    if  float(humidity) > ALERTHumidity or float(temperature) > ALERTTemperature:
        data = "{0} : Temperature={1}*C , Humidity={2}%".format(now, temperature, humidity)
        print(data)
        nowhour = int(now.strftime('%H'))
        weekday = now.strftime('%a')
        if nowhour > 8 and nowhour < 18 and not weekday == 'Sat' and not weekday == 'Sun':
             send_mail_alert(data)
    while not humidity == -1 or not temperature == -1:
        data = "{0} : Temperature={1}*C , Humidity={2}%".format(now, temperature, humidity)
        print(data)
        logging.info(data)
        if now.strftime('%H') == NOTIFYTIME:
            sent_mail_notify(data)
        break
    else:
        logging.info("{0} : failed to get reading. Retry...".format(now))
