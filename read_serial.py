#!/usr/bin/python3
import time
import serial
import datetime
import logging
import google.cloud.logging
import sys

# Imports the Google Cloud client library

# ------------------
# Setup Logging
# ------------------

file_name = ("CO2 Monitor")

#logger = logging.getLogger(__name__)
#logging.basicConfig(format=FORMAT, filename="basic_logging.log")
logging.basicConfig(format="%(filename)s:%(lineno)s - %(funcName)s() %(message)s")
#logging.basicConfig(filename='/var/log/co2mon.log', level=logging.INFO)

#logger.setLevel(logging.INFO)

# ------------------
# Setup Stackdriver
# ------------------

auth_file = '/home/pi/co2_monitor/homelab-266121-2389cbbb58c3.json'

# Instantiates a client
client = google.cloud.logging.Client.from_service_account_json(auth_file)

# Connects the logger to the root logging handler; by default this captures
# all logs at INFO level and higher
client.setup_logging()




ser = serial.Serial(port='/dev/ttyUSB0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

wlist = []
walist = []
	
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
		dt = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
		print("{}:  1 Minute Average:  {}".format(dt, round(weight_avg, 2)))
		#logging.log(msg="{}:  1 Minute Average:  {}".format(dt, round(weight_avg, 2)), level=logging.INFO)
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
			if weight_change >= 1:
				logging.log(msg="{{'Timestamp':{}, WARNING Very High Weight Change '10 Minute Change':{}}}".format(ts, weight_change_display), level=logging.critical)
			elif weight_change >= 0.1:
				logging.log(msg="{{'Timestamp':{}, WARNING High Weight Change '10 Minute Change':{}}}".format(ts, weight_change_display), level=logging.error)
			elif weight_change >= 0.1:
				logging.log(msg="{{'Timestamp':{}, WARNING Above Average Weight Change '10 Minute Change':{}}}".format(ts, weight_change_display), level=logging.warning)
			walist = []
