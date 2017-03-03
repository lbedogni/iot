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
import MySQLdb

from datetime import datetime, timedelta
import requests


# Standard ThingSpeak parameters
keyArray = ['description', 'elevation', 'name', 'created_at', 'updated_at', 'longitude', 'latitude', 'last_entry_id', 'id', 'tags', 'metadata', 'url']

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

# Open files and set logging and DB
def init():
	global db
	global cur
	global f_meta
	global f_data
	global f_erro
	global f_keys
	
	if database: #FIXME
		#~ db = MySQLdb.connect(host="localhost",    # your host, usually localhost
			#~ user="SenSquare",         # your username
			#~ passwd="mgrs32TPQ",  # your password
			#~ db="SenSquare")        # name of the data base
		db = MySQLdb.connect(host="localhost",    # your host, usually localhost
			user="davidek",         # your username
			passwd="tesiCRESTINI2016",  # your password
			db="sensquare")        # name of the data bas
		cur = db.cursor()
	if logging:
		f_meta = open('metaFromTS.csv', 'a+') # File with all the metadata
		f_data = open('dataFromTS.csv', 'a+') # File with all the data
		f_erro = open('erroFromTS.csv', 'a+') # File with all the errors (log)
		f_keys = open('keysFromTS.csv', 'a+') # File collecting all the metadata keys.

def finish():
	# Close the logging CSV files
	if logging:
		f_meta.close()
		f_data.close()
		f_erro.close()
		f_keys.close()
	
# Query the DB for all the ThingSpeak stream we already have
def all_streams_IDs():
	streams = []
	cur.execute("SELECT ID FROM `Devices` WHERE (ID LIKE 'THINGSPEAK_%')")
	for stream in cur.fetchall():
		streams.append(stream[0].replace("THINGSPEAK_",""))
	return streams

# Go query ThingSpeak and get data streams for all the streams in the list
def get_data_stream(list_streams):
	for stream in list_streams:	
		
		device_ID = THINGSPEAK_PREFIX + str(stream)
		print "Evaluating stream " + str(stream) + "..."
		url = "https://thingspeak.com/channels/" + str(stream) + "/feed.json"
		f = ""
		jj = ""
		
		try:
			# Parse the JSON from the page and get the root element
			f = urlopen("https://thingspeak.com/channels/" + str(stream) + "/feed.json").read().decode("utf-8")
			jj = json.loads(f)  # string to json
			chan = jj['channel']  # metadata
			
			# Get the data fields (database mode only)
			fields = []
			for item in chan.keys():
				if item.startswith('field'):  # we found a field
					fields.append({'field': chan[item], "class": "", "field_num": item})
				
			# Generate the device record
			device_name = chan["name"][0:32]
			lat = str(chan["latitude"])
			lon = str(chan["longitude"])
			last_update_TS = chan["updated_at"]

			# Insert the measurements
			for field in fields:
				
				# Get the assigned stream id
				stream_name = field['field'][0:32]
				cur.execute("SELECT `ID`,`last_update_timestamp` FROM `DataStreams` WHERE (name = '" + stream_name + "') AND (device_ID = '" + device_ID + "')")
				resp = cur.fetchall()
				stream_id = str(resp[0][0])
				last_update_db = str(resp[0][1])
				stream_num = field['field_num']
				
				# insert each measurement till now
				for meas in jj['feeds']:
					value = str(meas[stream_num])
					timestamp = str(meas['created_at'])
					sql = "INSERT INTO `Measurements`(`data_stream_ID`, `GPS_latitude`, `GPS_longitude`, `value`, `timestamp`) VALUES ('" + stream_id + "','" + lat + "','" + lon + "','" + value + "','" + timestamp + "')"
					cur.execute(sql)
				db.commit()
				
				# update the "last entry id field" 
				cur.execute("SELECT `ID` FROM `Measurements` WHERE (data_stream_ID = '" + stream_id + "') AND (timestamp = '" + timestamp + "')")
				meas_id = str(cur.fetchall()[0][0])
				cur.execute("UPDATE `DataStreams` SET `last_entry_ID`='" + meas_id + "' WHERE (ID = '" + stream_id + "')")
				db.commit()
			
			# Write onto the CSV files
			if logging:
				tags_to_str = str(doc["tags"]).replace("[","").replace("]","").replace(",","|")
				for f in fields:
					fields_list.append(f['nome_campo'])
				fields_to_str = str(fields_list).replace("[","").replace("]","").replace(",","|")
				f_meta.write(",".join([str(i), chan["name"].replace(",", ";").replace("\n", ""), chan["description"].replace(",", ";").replace("\n", ""), chan["created_at"], chan["updated_at"], chan["longitude"], chan["latitude"], chan["elevation"], str(chan["last_entry_id"]), tags_to_str, fields_to_str]))
				f_meta.write('\n')
			list_valid_streams.append(i)
	

# TODO gonna be significant when we have the Database
# return last update of a stream from the database (-1 if never updated or no data is saved)
def get_last_update(streamId):
	return -1

if __name__ == "__main__":
	
	beg = int(sys.argv[1])
	fin = int(sys.argv[2])
	
	init()
	
	streams = all_streams_IDs()
	get_data_stream(streams)
	
	finish()
