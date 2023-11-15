#!/usr/bin/env python3
# -*- coding: utf-8

import datetime
import sys
import os
#Import config file
import configparser
config = configparser.ConfigParser()
debug = 'XYMONCLIENTHOME' not in os.environ
if debug:
	config.read('xymon-home_sensors.ini')
else:
	config.read(os.environ['XYMONCLIENTHOME']+'/etc/xymon-home_sensors.ini')
class Variable():
	def __init__(self, name):
		self.name = name
		self.value = float('NaN')
		self.thresholds = {
			"warning": (-sys.maxsize, sys.maxsize),
			"alarm": (-sys.maxsize, sys.maxsize)
		}
	
	@property
	def color(self):
		if self.value < self.thresholds['alarm'][0] or self.value > self.thresholds['alarm'][1]:
			return "red"
		elif self.value < self.thresholds['warning'][0] or self.value > self.thresholds['warning'][1]:
			return "yellow"
		else:
			return "green"

class Sensor:
	def __init__(self, name):
		self.name = name
		self.variables = {
			"temperature": Variable("temp"),
			"humidity": Variable("humidity")
		}

	def read_thresholds(self):
		for k in self.variables:
			v = self.variables[k]
			# Read thresholds as tuples
			self.variables[k].thresholds['warning'] = (float(config[k][self.name + "_" + v.name + "_warn_min"]), float(config[k][self.name + "_" + v.name + "_warn_max"]))
			self.variables[k].thresholds['alarm'] = (float(config[k][self.name + "_" + v.name + "_alarm_min"]), float(config[k][self.name + "_" + v.name + "_alarm_max"]))

	def __str__(self):
		return "\n".join(["&%s%s_%s: %.1f" % (v.color, self.name.capitalize(), v.name, v.value) for v in self.variables.values()])

sensors = {
	"ground": Sensor('ground'),
	"floor": Sensor('floor'),
	"veranda": Sensor('veranda'),
	"garage": Sensor('garage')
}

#Define variables from config file
#Adapt for debug
_Source_File = "/tmp/home_sensors"
_status = "green"
_test = "home_sensors"
now=datetime.datetime.now()
_date=now.strftime("%a %d %b %Y %H:%M:%S %Z")

for sensor in sensors.values():
	sensor.read_thresholds()

#get_values
with open(_Source_File, 'r') as f:
	for row in f:
		if row == "No data received from WeatherStation":
			sys.exit(1)
		values = [float(x) for x in row.split(",")]
		sensors['ground'].variables['temperature'].value = values[0]
		sensors['ground'].variables['humidity'].value = values[1]
		sensors['floor'].variables['temperature'].value = values[2]
		sensors['floor'].variables['humidity'].value = values[3]
		sensors['veranda'].variables['temperature'].value = values[4]
		sensors['veranda'].variables['humidity'].value = values[5]
		sensors['garage'].variables['temperature'].value = values[6]
		sensors['garage'].variables['humidity'].value = values[7]

# Check for colors
for sensor in sensors.values():
	for variable in sensor.variables.values():
		if variable.color == "red":
			_status = "red"
		elif variable.color == "yellow" and _status != "red":
			_status = "yellow"

if debug:
	_msg_line="\n".join([str(sensor) for sensor in sensors.values()])
	print(_msg_line)
else:
	_msg_line="&%sIndoor_temp: %s\n&%sIndoor_humidity: %s\n&%sFloor_temp: %s\n&%sFloor_humidity: %s\n&%sVeranda_temp: %s\n&%sVeranda_humidity: %s\nOutdoor_temp: %s\nOutdoor_humidity: %s\n" % (ground_temp_color, ground_temp, ground_humidity_color, ground_humidity, floor_temp_color, floor_temp, floor_humidity_color, floor_humidity, veranda_temp_color, veranda_temp, veranda_humidity_color, veranda_humidity, outdoor_temp, outdoor_humidity)
	_cmd_line="%s %s \"status %s.%s %s %s\n\n%s\"" %(os.environ['XYMON'], os.environ['XYMSRV'], os.environ['MACHINE'], _test, _status, _date, _msg_line)
	#Lancement commande 
	os.system(_cmd_line)