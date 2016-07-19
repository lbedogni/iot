#!/usr/bin/env python
# -*- coding: utf-8 -*-

# With this script we save all the data coming from SparkFun.

import sys, os
from urllib import urlopen
import requests
import json
from requests.exceptions import ChunkedEncodingError

logging = True
database = False

meta = None
data = None

# Open files and set logging and DB
def init(log, db):
	logging = log
	database = db
	if database:
		from database import metadati
		from database import test_set
	if logging:
		global meta
		global data
		meta = open('metaFromSF.csv', 'a+')
		data = open('dataFromSF.csv', 'a+')

# Just close the log CSV file
def finish():
	if logging:
		meta.close()
		data.close()	

# We save all the stream IDs in a macro list, ready to be processed
# maxPages : number of pages to fetch in total
# threshold : number of pages after which start to parse along
def get_all_streams(maxPages, threshold):
	pageArray = [] # List of HTML pages (a pool)
	list_stream = [] # List of stream IDs
	
	# Start from the streams you already collected
	#list_stream += get_all_streams_local()

	# Fetch all the pages in the desired range
	# We get first HTML code and, once in a while, we parse them, empty the pool, and save the stream IDs
	counter = 0
	for i in range(0, maxPages):
		try:
			print "Getting page " + str(i) + "..."
			pageArray.append(urlopen("https://data.sparkfun.com/streams/?page=" + str(i)))
			
			# Start to parse from the pool (along one by one)
			if (i >= threshold) or (i >= maxPages - 1):
				html = pageArray.pop()
				list_stream += get_streams_from_html(html, list_stream)
		except:
			print (sys.exc_info()[0])
			continue
	# Empty the pool and parse the remainder
	for y in range(len(pageArray)):
		html = pageArray.pop()
		list_stream += get_streams_from_html(html, list_stream)
	print ("All in all we have " + str(len(list_stream)) + " streams to compute.")
	return list_stream

def get_all_streams_local():
	list_stream = [] # List of stream IDs
	
	with open("streamsFromSF.csv", 'r') as SFstreams:
		for line in SFstreams.readlines():
			list_stream.append(line.strip())
	return list_stream
			
# Returns a list of stream URLs got from the HTML page
def get_streams_from_html(html, list_stream):
	list_stream_return = []
	for l in html.readlines():
		line = l.decode('utf-8').strip()  # All the lines tof the HTML document
		if "stream-title" in line:
			# Take the stream ID
			stream = line.split("\"")[3]
			if stream not in list_stream:
				list_stream_return.append(stream)
				with open("streamsFromSF.csv", 'a+') as SFstreams:
					SFstreams.write(stream + "\n")
	return list_stream_return

# Get measurements from all the streams in the list (list of URLs for which we already got the metadata) XXX
def get_data_stream(list_stream): 
	for stream in list_stream:
		try:
			
			# get the stream ID from the end of the URL
			stream_id = stream.split("/")[2]
			print "Getting data stream " + stream_id + "..." 
			response = requests.get('https://data.sparkfun.com/output/' + stream_id + '.json') # get the relative measurements JSON
			print "and the jason"
			data_stream = json.loads(response.content)
			
			# Avoid bad surprises
			if type(data_stream) == dict and data_stream[data_stream.keys()[0]] == 'no data has been pushed to this stream':
				continue
			
			# List of updates
			l = []
			last_update = get_last_update(stream)
			
			print "here"
			
			# Check if we have something to update
			if last_update < data_stream[0]['timestamp']:  # ultimo update tra i dati
				print "here2", last_update, data_stream[0]['timestamp']
			
				# Get the index of the last update we have in local in what we just downloaded (if it is -1 then we never extracted data)
				index_last_update = len(data_stream)
				for update in data_stream:
					if update['timestamp'] is last_update:
						index_last_update = list.index(update)
						break
						
				print "Checking stream " + stream_id #DEBUG		
				# From the last update till the end let's collect the data (reverse order)
				for i in range(0, index_last_update):
					update = data_stream[i]
					l.append(update)
					print "\t" + str(update) #DEBUG
					
			# add the list of measurements in the database #FIXME to be done in SQL	
			# post_id = dati.insert_one(doc).inserted_id

			# Aggiorna last_updati in metadati #FIXME to do in MySQL
			# metadati.find_one_and_update({"stream_id": stream}, {'$set': {'last_update': jj[0]['timestamp']}})
		
		except ChunkedEncodingError:
			print "this is very bad"
			pass
		
		except TypeError:
			print "Unexpected error:", sys.exc_info()[0]
			

# TODO gonna be significant when we have the Database
# return last update of a stream from the database (-1 if never updated or no data is saved)
def get_last_update(streamId):
	return -1

# Cycle for metadata parsing
def get_metadata_stream(list_stream):
	
	ctr = 0
	for stream in list_stream:
		# Get the stream name
		stream_id = stream.split("/")[2]
				
		# Cerca stream su db <--------------------------------------------------------FIXME
		if database:
			metadataStream = metadati.find_one({"stream_id": stream})
			# metadatiStream = test_set.find_one({"stream_id": stream})
		else:
			metadataStream = None

		if metadataStream is not None:
			print "Stream " + stream_id + "has already been processed."
			# TODO vary just "last update" field
			continue
		else:
			print "Processing new stream " + str(ctr) + " ID:" + stream_id
			try:
				# Get metadata JSON file and save it onto a dict 
				response = requests.get("https://data.sparkfun.com/streams/" + stream_id + ".json")  
				metadata_stream = json.loads(response.content)  
								   
				# Get the geolocaliazation (if present)
				geolocalization = {"latitude": "", "longitude": ""}
				if 'location' in metadata_stream['stream']['_doc'].keys() and len(metadata_stream['stream']['_doc']['location']) != 0:
						geolocalization["latitude"] = metadata_stream['stream']['_doc']['location']['lat']
						geolocalization["longitude"] = metadata_stream['stream']['_doc']['location']['lng']

				# Get the measurement fields' names
				fields = []
				for nome_campo in metadata_stream['stream']["_doc"]["fields"]:
					fields.append({"nome_campo": nome_campo, "classe": "CLASS"})

				# Generate the JSON metadata record
				doc = {"stream_id": stream,
					   "nome": metadata_stream['stream']["_doc"]["title"],
					   "descrizione": metadata_stream['stream']["_doc"]["description"],
					   "tags": metadata_stream['stream']["_doc"]["tags"],  # array di stringhe
					   "campi": fields,
					   "geolocalization": geolocalization,
					   "last_update": metadata_stream['stream']["_doc"]["last_push"]
					   }
				tags_to_str = str(doc["tags"]).replace("[","").replace("]","").replace(",","|")
				fields_list = []
				for f in fields:
					fields_list.append(f['nome_campo'])
				fields_to_str = str(fields_list).replace("[","").replace("]","").replace(",","|")
				
				# Insert the new metadata record onto the DB
				if database:
					post_id = metadati.insert_one(doc).inserted_id
				
				# Insert the new metadata record in the CSV file	
				if logging:
					meta.write(",".join([stream_id, doc["nome"].replace(",", ";").replace("\n", ""),
					doc["descrizione"].replace(",", ";").replace("\n", ""), "",
					doc["last_update"], doc["geolocalization"]["longitude"], doc["geolocalization"]["latitude"], "",
					"", tags_to_str, fields_to_str]))
					meta.write('\n')
				ctr += 1
			except UnicodeEncodeError:
				pass # Questo è da fixare assolutamente
		
			except ConnectionError:
				pass # Questo è da fixare assolutamente pure
		break#XXX tohglilo cazzo!!!!
		
		
if __name__ == "__main__":
	
	maxP = int(sys.argv[1])
	thresh = int(sys.argv[2])
	
	init(True, False)
	myStreams = get_all_streams(maxP, thresh)
	#~ myStreams = get_all_streams_local()
	
	get_metadata_stream(myStreams)
	get_data_stream(myStreams)
	
	finish()

	
