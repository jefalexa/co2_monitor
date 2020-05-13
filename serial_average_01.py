#!/usr/bin/python3
import time
import serial
import datetime
import logging

logging.basicConfig(filename='co2mon.log', level=logging.INFO)

ser = serial.Serial(port='/dev/ttyUSB0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

counter=0
weight_avg = 0
	
while 1:
	x = ser.readline()
	y = str(x)
	z = y.split(",")[0]
	try:
		weight = float(z.split("b'")[1])
		if weight_avg == 0:
			weight_avg = weight
		weight_avg = (weight_avg + weight) / 2
		#print(weight, round(weight_avg, 2))
		counter += 1
	except:
		print(y)
	if counter >= 60:
		dt = datetime.datetime.now()
		dt2 = dt.strftime("%Y-%m-%d_%H-%M")
		print("{}:  1 Minute Average:  {}".format(dt2, round(weight_avg, 2)))
		counter = 0
		weight_avg = 0
