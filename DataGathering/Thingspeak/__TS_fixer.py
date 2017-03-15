#!/usr/bin/env python
# -*- coding: utf-8 -*-

# With this script we save all the metadata coming from ThingSpeak.

# TODO:
# Integrate with the MySQL database
# Rename database fields (obviously...)

from urllib import urlopen
import json
import sys
from urllib2 import HTTPError

from datetime import datetime, timedelta
import requests

from gathering import dbcalls

# Standard ThingSpeak parameters
keyArray = ['description', 'elevation', 'name', 'created_at', 'updated_at', 'longitude', 'latitude', 'last_entry_id', 'id', 'tags', 'metadata', 'url']

THINGSPEAK_PARTICIPANT_NAME = "THINGSPEAK"
THINGSPEAK_PREFIX = "THINGSPEAK_"
THINGSPEAK_PARTICIPANT_ID = "4"
THINGSPEAK_DEVICE_TYPE = "UNRELIAB"

db = None
cur = None

logging = False
database = True

f_meta = None
f_data = None
f_erro = None
f_keys = None

AllDevices = []

# Open files and set logging and DB
def init():
	global db
	global cur
	global f_meta
	global f_data
	global f_erro
	global f_keys
	
	dbcalls.init()
		
		#FIXME
		#~ db = MySQLdb.connect(host="localhost",    # your host, usually localhost
			#~ user="SenSquare",         # your username
			#~ passwd="mgrs32TPQ",  # your password
			#~ db="SenSquare")        # name of the data base

	if logging:
		f_meta = open('metaFromTS.csv', 'a+') # File with all the metadata
		f_data = open('dataFromTS.csv', 'a+') # File with all the data
		f_erro = open('erroFromTS.csv', 'a+') # File with all the errors (log)
		f_keys = open('keysFromTS.csv', 'a+') # File collecting all the metadata keys.

def finish():
	
	dbcalls.finish()
	
	if logging:
		f_meta.close()
		f_data.close()
		f_erro.close()
		f_keys.close()
		
# Fill the list of all the devices from our DB
def fillAllDevices ():
	global AllDevices
	AllDevices = dbcalls.findAllDevices(THINGSPEAK_PARTICIPANT_ID)
	

if __name__ == "__main__":
	
	init()
	fillAllDevices()

	for dev in AllDevices:
		# Get the last update from a device (from one of its streams)	

		dbcalls.cur.execute("SELECT `creation_timestamp` FROM `DataStreams` WHERE (`device_ID` = '" + THINGSPEAK_PREFIX + str(dev['id']) + "')")
		results = dbcalls.cur.fetchall()
		print results
		if len(results) > 0:
			timestamp = results[0][0]
			dbcalls.cur.execute("UPDATE `DataStreams` SET `last_update_timestamp` = '" + str(timestamp) + "' WHERE (`device_ID` = '" + THINGSPEAK_PREFIX + str(dev['id']) + "')")
			dbcalls.db.commit()
	
	finish()
