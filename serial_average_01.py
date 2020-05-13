#!/usr/bin/python3
import time
import serial
import datetime
import logging

logging.basicConfig(filename='co2mon.log', level=logging.INFO)

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
		logging.log(msg="{}:  1 Minute Average:  {}".format(dt, round(weight_avg, 2)), level=logging.INFO)
		wlist = []
		if len(walist) >= 10:
			weight_avg = sum(walist) / len(walist)
			dt = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
			print("{}:  10 Minute Average:  {}".format(dt, round(weight_avg, 2)))
			logging.log(msg="{}:  10 Minute Average:  {}".format(dt, round(weight_avg, 2)), level=logging.INFO)
			walist = []
