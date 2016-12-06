from flask import Flask
import json
from random import random
from time import time
import MySQLdb
import datetime
app = Flask(__name__)

db = None
cur = None

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
	user="davidek",         # your username
	passwd="tesiCRESTINI2016",  # your password
	db="sensquare")        # name of the data base
# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

def readJson(number):
	jason = ""	
	if number == "0":
		with open("sandbox0.json", 'r') as jay:
			jason = json.loads(jay.read().replace('\n', ''))
	elif number == "1":
		with open("sandbox1.json", 'r') as jay:
			jason = json.loads(jay.read().replace('\n', ''))
	else:
		jason = {}
	return jason
	
def extractService(number):
	jason = {}
	
	jason['device_id'] = number
	jason['streams'] = []
		
	cur.execute("SELECT * FROM `DataStreams` WHERE device_ID = '" + number + "'")
	results = cur.fetchall()
			
	for record in results:
		stream = {}
		
		stream_id = str(record[0])
		data_class = str(record[2])
		creation = str(record[3])
		last_update = str(record[4])
		
		cur.execute("SELECT unit_of_measure FROM `DataClasses` WHERE ID = '" + data_class + "'")
		dc = cur.fetchall()
		if len(dc) > 0:
			unit_of_measure = dc[0][0]
		else:
			unit_of_measure = ""
		
		cur.execute("SELECT * FROM `Measurements` WHERE (data_stream_ID = '" + stream_id + "') AND (timestamp = (SELECT MAX(timestamp) FROM `Measurements` WHERE (data_stream_ID = '" + stream_id + "')))")
		meas = cur.fetchall()
		if len(meas) > 0:
			lat = str(meas[0][2])
			lon = str(meas[0][3])
			value = str(meas[0][5])
			last_update = str(meas[0][6])
		else:
			return {}
		
		stream['data_class'] = str(data_class)
		stream['creation_timestamp'] = str(creation)
		stream['last_update_timestamp'] = str(last_update)
		stream['value'] = str(value)
		stream['unit_of_measure'] = str(unit_of_measure)
		jason['streams'].append(stream)
		jason['latitude'] = str(lat)
		jason['longitude'] = str(lon)
		
	return jason
	

@app.route("/extract/<number>")
def extract(number=None):
	
	#jason = readJson(number)
	jason = extractService(number)
	
	now = time()
	notnow = now - (now % 1200)
	
	
	for stream in jason['streams']:
		stream['value'] = random() * 100
		stream['last_update_timestamp'] = str(datetime.datetime.fromtimestamp(notnow).isoformat())

	return json.dumps(jason, separators=(',',':'))

if __name__ == "__main__":
	

		
	app.run(host='130.136.37.231', port=10016)
