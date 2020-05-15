#!/usr/bin/python3
import time
import serial
import datetime
import logging

logging.basicConfig(filename='/var/log/co2mon.log', level=logging.INFO)

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
		weight_avg = sum(wlist) / len(wlist)
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
			logging.log(msg="{}:  {{'Timestamp':{}, '10 Minute Average':{}, '10 Minute Change':{}}}".format(dt, ts, weight_avg_display, weight_change_display), level=logging.INFO)
			walist = []
