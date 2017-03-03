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
		
# Go query ThingSpeak from index 'begin' to index 'end'
def get_metadata_stream(begin, end):
	
	pointer = beg
	#list_valid_streams = []

	for i in range(begin, end):
		
		# Search for the channel (device ID) on the DB
		device_ID = THINGSPEAK_PREFIX + str(i)
		
		# If the channel is new we should insert all its metadata
		if dbcalls.IsDevice(device_ID) > 0:
			print "Channel " + str(i) + " has already been stored."
		else:
			print "Evaluating channel " + str(i) + "..."
			url = "https://thingspeak.com/channels/" + str(i) + "/feed.json"
			
			try:
				# Parse the JSON from the page and get the root element
				f = unicode(urlopen("https://thingspeak.com/channels/" + str(i) + "/feed.json").read().decode("utf-8"))				
				jj = json.loads(f)  # string to json
				chan = jj['channel']  # metadata

				# Add an empty value whether the record does not have the field
				# We pass whenever the channel is not geolocated
				for item in keyArray:
					if item not in chan.keys():
						chan[item] = ""
				if (chan['latitude'] == "0.0") or (chan['latitude'] == "") or (chan['longitude'] == "0.0") or (chan['longitude'] == ""):
					print "Channel " + str(i) + " not geolocated."
					continue
					
				# Get the data fields (the STREAMS)
				fields = []
				for item in chan.keys():
					if item.startswith('field'):  # we found a field
						fields.append({'field': chan[item], "class": "", "field_num": item})
				
				# Add the tags, scraping them directly from the HTML page (whether they are useful is still a mystery)
				page = urlopen("https://thingspeak.com/channels/" + str(i))
				tags = []
				fields_list = []
				for line in page.readlines():
					if "channel-tags" in line:
						tags.append(line.split(">")[1].split("<")[0])
						
				# Generate the device record from the channel
				device_name = chan["name"][0:32]
				lat = str(chan["latitude"])
				lon = str(chan["longitude"])
				dbcalls.insertDevice(device_ID, device_name, THINGSPEAK_DEVICE_TYPE, THINGSPEAK_PARTICIPANT_ID)
				
				# Generate each stream record
				for field in fields:
					stream_name = field['field'][0:32]
					stream_class = field['class']
					creation_timestamp = dbcalls.TSToDatetime(chan['created_at'])
					last_update_timestamp = dbcalls.TSToDatetime(chan['updated_at'])
					description = chan['description'][0:64]
					elevation = chan['elevation']
					url = chan['url'][0:150]	
					stream_id = dbcalls.insertStream(stream_name, stream_class, creation_timestamp, description, elevation, url, device_ID)	# DB insert stream
					stream_num = field['field_num']
					
					# insert each measurement till now
					for meas in jj['feeds']:
						value = meas[stream_num]
						timestamp = dbcalls.TSToDatetime(meas['created_at'])
						dbcalls.insertMeasurement(stream_id, lat, lon, value, timestamp)
					
					# update the "last entry id field" 
					dbcalls.refreshStream(stream_id)
				
				# Write onto the CSV files
				if logging:
					tags_to_str = str(doc["tags"]).replace("[","").replace("]","").replace(",","|")
					for f in fields:
						fields_list.append(f['nome_campo'])
					fields_to_str = str(fields_list).replace("[","").replace("]","").replace(",","|")
					f_meta.write(",".join([str(i), chan["name"].replace(",", ";").replace("\n", ""), chan["description"].replace(",", ";").replace("\n", ""), chan["created_at"], chan["updated_at"], chan["longitude"], chan["latitude"], chan["elevation"], str(chan["last_entry_id"]), tags_to_str, fields_to_str]))
					f_meta.write('\n')
				#list_valid_streams.append(i)
			
				pointer = i+1 # Set the hypothetically next one to be checked
				
			# "channel" field not found
			except KeyError:
				print "HTTP 404 Response"

			# We pass those 'cause we might have some private streams	
			except HTTPError:
				pass
				
			except TypeError:
				print "This is a Private Channel..."
			
			# What else?
			#~ except:
				#~ print(sys.exc_info()[0])
	
	return pointer

# Go query ThingSpeak and get data streams for all the streams in the list
def get_data_stream(list_streams):
	for i in list_streams:
		stream = i		
		# Here we have a stream which has no measurements in the database, therefore we add all of them without further checking
		try:
			f = requests.get("https://thingspeak.com/channels/" + str(stream) + "/feed.json")
			data_stream = json.loads(f.content)
			
			# List of updates
			l = []
			last_update = get_last_update(stream)
			
			# Check if we have something to update
			if last_update < data_stream['channel']['updated_at']:  # ultimo update tra i dati
				
				# Get the index of the last update we have in local in what we just downloaded (if it is -1 then we never extracted data)
				index_last_update = -1
				for update in data_stream['feeds']:
					if update['created_at'] is last_update:
						index_last_update = list.index(update)
						break
				
				print "Checking stream " + str(stream) #DEBUG
				
				# From the last update till the end let's collect the data	
				for i in range(index_last_update + 1, len(data_stream['feeds'])):
					update = data_stream['feeds'][i]
					update['timestamp'] = update['created_at']
					del update['created_at']
					for k in update.keys():
						if 'field' in k:
							campo_misurato = data_stream['channel'][k]
							update[campo_misurato] = update[k]
							del update[k]
						
					l.append(update)
					print "\t" + str(update) #DEBUG
			
			doc = { "stream_id": stream, "update": l }
		
		except:
			print "Unexpected error:", sys.exc_info()[0]
	

# return last update of a stream from the database (-1 if never updated or no data is saved)
def get_last_update(streamId):
	return -1

if __name__ == "__main__":
	
	init()
	
	start, limit = dbcalls.getNextChannel(THINGSPEAK_PARTICIPANT_NAME)
	
	beg = start
	fin = start + limit	
	print beg, fin
	pointer = get_metadata_stream(beg, fin)
	
	dbcalls.setNextChannel(THINGSPEAK_PARTICIPANT_NAME, pointer)
	
	finish()
