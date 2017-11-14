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

def updateMeasurementsFromJson(ID):
	f = requests.get("https://thingspeak.com/channels/" + str(ID) + "/feed.json?results=8000&start=2017-01-01 00:00:00")
	page = json.loads(f.content)
	channel = page['channel']
	stream_ids = {}
	
	# Name conversion for fields
	for k in channel.keys():
		if "field" in k:
			stream_id = dbcalls.getDataStream(THINGSPEAK_PREFIX + str(ID), channel[k])
			if stream_id == None:
				return
			stream_ids[k] = stream_id
	print stream_ids
	
	giga_string = ""
	for feed in page['feeds']:
		timestamp = feed['created_at']
		
		# Insert measurement for each stream
		for k in feed.keys():
			if "field" in k:
				try:
					value = float(feed[k])
				except:
					continue
				stream = stream_ids[k]
				giga_string += "(" + ",".join(["'"+str(stream)+"'", "'"+str(value)+"'", "'"+dbcalls.TSToDatetime(timestamp)+"'"]) + "),"
	giga_string = giga_string[:-1]
		
	dbcalls.insertMultipleMeasurements(giga_string)
	print "Insertion done"

# return last update of a stream from the database (-1 if never updated or no data is saved)
def get_last_update(streamId):
	return -1
	
def updateMeasurements(ID):
	new_daycount = 0
	
	#try:
	print "Executing for ID " + str(ID)
	# Get the old last update (from database)
	OldUpdate = dbcalls.getLastUpdate(THINGSPEAK_PREFIX + str(ID))
	if OldUpdate == None:
		return 365 # Meaning that the channel has no streams
		
	# Get the JSON for the whole data channel (1 second after our last update)
	print "fetching " + str(ID)
	f = requests.get("https://thingspeak.com/channels/" + str(ID) + "/feed.json?results=8000&start=" + datetime.strftime((OldUpdate + timedelta(0,1)), "%Y-%m-%d %H:%M:%S"))
	page = json.loads(f.content)
    try:    
	    channel = page['channel']
    except:
        print "This channel has gone"
        return

	stream_ids = {}
	
	# Name conversion for fields
	for k in channel.keys():
		if "field" in k:
			stream_id = dbcalls.getDataStream(THINGSPEAK_PREFIX + str(ID), channel[k])
			if stream_id == None:
				return
			stream_ids[k] = stream_id
	print stream_ids		
	
	insert_string = ""
	first = True
	first_timestamp = None
	for feed in page['feeds']:
		timestamp = feed['created_at']
		
		# Save the first timestamp to calculate new daycount
		if first:
			first = False
			first_timestamp = dbcalls.TSToDatetime(timestamp)
				
		# Insert measurement for each stream
		for k in feed.keys():
			if "field" in k:
				try:
					value = float(feed[k])
				except:
					continue
				stream = stream_ids[k]
				insert_string += "(" + ",".join(["'"+str(stream)+"'", "'"+str(channel["latitude"])+"'", "'"+str(channel["longitude"])+"'", "'-1'", "'"+str(value)+"'", "'"+dbcalls.TSToDatetime(timestamp)+"'"]) + "),"
				#insert_string += "(" + ",".join(["'"+str(stream)+"'", "'"+str(value)+"'", "'"+dbcalls.TSToDatetime(timestamp)+"'"]) + ")," # Reduced version
				#dbcalls.insertMeasurement(str(stream), str(channel["latitude"]), str(channel["longitude"]), str(value), dbcalls.TSToDatetime(timestamp))
	insert_string = insert_string[:-1]
	print "Inserting..."
	if len(insert_string) > 5: # 5 is just a tolerance interval 		
		dbcalls.insertMultipleMeasurements(insert_string)
		#dbcalls.insertMultipleMeasurementsReduced(insert_string)
	print "Insertion done"
	
	# Update last timestamp
	last_timestamp = dbcalls.TSToDatetime(channel['updated_at'])
	for k in stream_ids:
		dbcalls.refreshStreamSimple(str(stream_ids[k]), last_timestamp)
	
	if len(page['feeds']) > 0:
		new_daycount = dbcalls.calculateDaycount(first_timestamp, datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
	else:
		new_daycount = dbcalls.calculateDaycount(last_timestamp, datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
	
	#except:
	#	print "Unexpected error:", sys.exc_info()[0]
		
	return new_daycount
	

if __name__ == "__main__":
	
	init()
	fillAllDevices()
	
	#~ updateMeasurementsFromJson(49728) TESTING STUFF

	for dev in AllDevices:
		# Decrease daycount
		if dev['daycount'] > 0:
			dbcalls.setDayCount(THINGSPEAK_PREFIX + str(dev['id']), dev['daycount'] - 1)
		# Time to load measurements and reset the daycount
		else:
			newDayCount = updateMeasurements(dev['id'])
			dbcalls.setDayCount(THINGSPEAK_PREFIX + str(dev['id']), newDayCount)
	
	finish()
