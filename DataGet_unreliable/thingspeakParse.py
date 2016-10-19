#!/usr/bin/env python
# -*- coding: utf-8 -*-

# With this script we save all the data coming from ThingSpeak.

# TODO:
# Integrate with the MySQL database
# Rename database fields (obviously...)

from urllib import urlopen
import json
import sys
from urllib2 import HTTPError

from datetime import datetime, timedelta
import requests


# Standard ThingSpeak parameters
keyArray = ['description', 'elevation', 'name', 'created_at', 'updated_at', 'longitude', 'latitude', 'last_entry_id', 'id', 'tags', 'metadata', 'url']

logging = True
database = False

f_meta = None
f_data = None
f_erro = None

# Open files and set logging and DB
def init(log, db):
	logging = log
	database = db
	
	global f_meta
	global f_data
	global f_erro
	
	if database: #FIXME
		from database import metadati
		from database import test_set
	if logging:
		f_meta = open('metaFromTS.csv', 'a+') # File with all the metadata
		f_data = open('dataFromTS.csv', 'a+') # File with all the data
		f_erro = open('erroFromTS.csv', 'a+') # File with all the errors (log)
		# f_keys = open('keysFromTS.csv', 'a+') # File collecting all the metadata keys.

def finish():
	# Close the logging CSV files
	if logging:
		f_meta.close()
		f_data.close()
		f_erro.close()
		# f_keys.close()
		
# Go query ThingSpeak from index 'begin' to index 'end'
def get_metadata_stream(begin, end):
	
	list_valid_streams = []

	for i in range(begin, end):
		
		# Search for the stream on the DB FIXME
		if database:
			metadataStream = metadati.find_one({"stream_id": i})
		else:
			metadataStream = None

		if metadataStream is not None:
			print "Stream " + str(i) + " has already been stored."
			# TODO just update the "last update" field
		else:
			
			print "Evaluating stream " + str(i) + "..."
			ff = "https://thingspeak.com/channels/" + str(i) + "/feed.json"
			f = ""
			jj = ""
			
			try:
				# Parse the JSON from the page and get the root element
				f = urlopen("https://thingspeak.com/channels/" + str(i) + "/feed.json").read().decode("utf-8")
				jj = json.loads(f)  # string to json
				chan = jj['channel']  # metadata
				
				# Get the data fields (database mode only)
				fields = []
				for item in chan.keys():
					if item.startswith('field'):  # we found a field
						fields.append({'nome_campo': chan[item], "classe": "CLASS"})

				# Add an empty value whether the record does not have the field
				for item in keyArray:
					if item not in chan.keys():
						chan[item] = ""
				
				# Add the tags, parsing them directly from the HTML page
				page = urlopen("https://thingspeak.com/channels/" + str(i))
				tags = []
				fields_list = []
				for line in page.readlines():
					if "channel-tags" in line:
						tags.append(line.split(">")[1].split("<")[0])
				
				# Generate the JSON metadata record and insert it onto the DB
				doc = {
					"stream_id": i,
					"nome": chan["name"],
					"descrizione": chan["description"],
					"tags": tags,
					"campi": fields,
					"geolocalization": {"longitude": chan["longitude"], "latitude": chan["latitude"]},
					"last_update": chan["updated_at"],
					"last_entry_id": chan["last_entry_id"]
				}				
				if database:
					post_id = metadati.insert_one(doc).inserted_id # Insert the record onto the DB
					print "Document " + str(i) + "inserted onto the DB."
				
				# Write onto the CSV files
				if logging:
					tags_to_str = str(doc["tags"]).replace("[","").replace("]","").replace(",","|")
					for f in fields:
						fields_list.append(f['nome_campo'])
					fields_to_str = str(fields_list).replace("[","").replace("]","").replace(",","|")
					f_meta.write(",".join([str(i), chan["name"].replace(",", ";").replace("\n", ""), chan["description"].replace(",", ";").replace("\n", ""), chan["created_at"], chan["updated_at"], chan["longitude"], chan["latitude"], chan["elevation"], str(chan["last_entry_id"]), tags_to_str, fields_to_str]))
					f_meta.write('\n')
				
				list_valid_streams.append(i)
				
			# "channel" field not found
			except KeyError:
				print "HTTP 404 Response"
				
			# We pass those 'cause we might have some private streams	
			except HTTPError:
				pass
			
			except TypeError:
				print "This is a Private Channel..."

			# What else?
			except:
				print(sys.exc_info()[0])
	
	return list_valid_streams

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
			
			# add the list of measurements in the database #FIXME to be done in SQL	
			# post_id = dati.insert_one(doc).inserted_id

			# Aggiorna last_updati in metadati #FIXME to do in MySQL
			# metadati.find_one_and_update({"stream_id": str(stream)}, {'$set': {'last_update': data_stream['channel']['updated_at']}})
		
		except:
			print "Unexpected error:", sys.exc_info()[0]
	

# TODO gonna be significant when we have the Database
# return last update of a stream from the database (-1 if never updated or no data is saved)
def get_last_update(streamId):
	return -1

if __name__ == "__main__":
	beg = int(sys.argv[1])
	fin = int(sys.argv[2])
	
	init(True, False)
	streams = get_metadata_stream(beg, fin)
	print streams
	get_data_stream(streams)
	
	finish()
