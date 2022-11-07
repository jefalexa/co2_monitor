#!/usr/bin/python3
import time
import serial
import datetime
import logging
import google.cloud.logging
import sys
from twilio.rest import Client
import json

# Imports the Google Cloud client library

# ------------------
# Setup Logging
# ------------------

file_name = ("CO2 Monitor")

logging.basicConfig(format="%(filename)s:%(lineno)s - %(funcName)s() %(message)s")

# ------------------
# Setup Stackdriver
# ------------------

auth_file = '/home/pi/co2_monitor/homelab-266121-2389cbbb58c3.json'

# Instantiates a client
client = google.cloud.logging.Client.from_service_account_json(auth_file)

# Connects the logger to the root logging handler; by default this captures
# all logs at INFO level and higher
client.setup_logging()

logging.log(msg="Test 1", level=logging.INFO)

# ------------------
# Setup Twilio
# ------------------

phone_num_from = '12052933447'
phone_num_to = '13038182403'
msg_empty_sent = False
msg_low_sent = False

key_file = '/home/pi/co2_monitor/twilio_keys.json'

with open(key_file, 'r') as file:
    key_file = json.load(file)
    twilio_sid = key_file['twilio_sid']
    twilio_auth_token = key_file['twilio_auth_token']

client_twilio = Client(twilio_sid, twilio_auth_token)


def send_empty_msg(weight_avg):
    global msg_empty_sent
    global msg_low_sent
    dt = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    if ((weight_avg <= 0.01) & (msg_empty_sent==False)):
        msg_body = f'{dt} - CO2 is empty!'
        message = client_twilio.messages.create(body=msg_body,from_=phone_num_from,to=phone_num_to)
        sleep_count = 0
        while ((message.fetch().status != 'delivered') & (sleep_count < 30)):
            time.sleep(3)
            sleep_count += 3
        if message.fetch().status == 'delivered':
            msg_empty_sent = True    
    elif ((weight_avg < 0.5) & (msg_low_sent==False) & (msg_empty_sent==False)):
        msg_body = f'{dt} - CO2 is getting low!'
        message = client_twilio.messages.create(body=msg_body,from_=phone_num_from,to=phone_num_to)
        sleep_count = 0
        while ((message.fetch().status != 'delivered') & (sleep_count < 30)):
            time.sleep(3)
            sleep_count += 3
        if message.fetch().status == 'delivered':
            msg_low_sent = True
    elif weight_avg > 1:
        msg_empty_sent = False
        msg_low_sent = False
    return


def send_change_msg(weight_change):
    dt = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    ts = datetime.datetime.now().timestamp()
    weight_change_display = round(weight_change, 2)
    if weight_change >= 1:
        logging.log(msg="{{'Timestamp':{}, WARNING Very High Weight Change '10 Minute Change':{}}}".format(ts, weight_change_display), level=logging.critical)
        msg_body = f'{dt} - WARNING Very High Weight Change - 10 Minute Change:{weight_change_display}'
        message = client_twilio.messages.create(body=msg_body,from_=phone_num_from,to=phone_num_to)
    elif weight_change >= 0.2:
        logging.log(msg="{{'Timestamp':{}, WARNING High Weight Change '10 Minute Change':{}}}".format(ts, weight_change_display), level=logging.error)
        msg_body = f'{dt} - WARNING High Weight Change - 10 Minute Change:{weight_change_display}'
        message = client_twilio.messages.create(body=msg_body,from_=phone_num_from,to=phone_num_to)
    elif weight_change >= 0.1:
        logging.log(msg="{{'Timestamp':{}, WARNING Above Average Weight Change '10 Minute Change':{}}}".format(ts, weight_change_display), level=logging.warning)
        msg_body = f'{dt} - WARNING Above Average Weight Change - 10 Minute Change:{weight_change_display}'
        message = client_twilio.messages.create(body=msg_body,from_=phone_num_from,to=phone_num_to)
    return



ser = serial.Serial(port='/dev/ttyUSB0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

wlist = []
walist = []
    
logging.log(msg="Test 2", level=logging.INFO)

while 1:
    x = ser.readline()
    y = str(x)
    z = y.split(",")[0]
    try:
        weight = float(z.split("b'")[1])
        wlist.append(weight)
    except:
        print(y)
    if len(wlist) >= 60:
        try:
            wlist.sort()
            weight_avg = (wlist[30] + wlist[29]) /2
        except:
            weight_avg = sum(wlist) / len(wlist)
            logging.log(msg="Error calculating median, reverting to mean", level=logging.INFO)
        walist.append(weight_avg)
        print(weight_avg)
        dt = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        print("{}:  1 Minute Average:  {}".format(dt, round(weight_avg, 2)))
        logging.log(msg="{}:  1 Minute Average:  {}".format(dt, round(weight_avg, 2)), level=logging.INFO)
        wlist = []
        if len(walist) >= 10:
            weight_avg = sum(walist) / len(walist)
            weight_change = walist[0] - walist[-1]
            weight_avg_display = round(weight_avg, 2)
            weight_change_display = round(weight_change, 2)
            now = datetime.datetime.now()
            dt = now.strftime("%Y-%m-%d_%H%M")
            ts = now.timestamp()
            print("{}:  10 Minute Average:  {}".format(dt, weight_avg_display))
            print("{}:  10 Minute Change:  {}".format(dt, weight_change_display))
            logging.log(msg="{{'Timestamp':{}, '10 Minute Average':{}, '10 Minute Change':{}}}".format(ts, weight_avg_display, weight_change_display), level=logging.INFO)
            send_empty_msg(weight_avg)
            send_change_msg(weight_change)
            walist = []


