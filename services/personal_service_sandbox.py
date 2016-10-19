from flask import Flask
import json
from random import random
from time import time
import datetime
app = Flask(__name__)

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

@app.route("/sandy/<number>")
def sandbox(number=None):
	
	jason = readJson(number)
	now = time()
	notnow = now - (now % 1200)
	
	
	for stream in jason['streams']:
		stream['value'] = random() * 100
		stream['timestamp'] = str(datetime.datetime.fromtimestamp(notnow).isoformat())
	
	return json.dumps(jason, separators=(',',':'))

if __name__ == "__main__":
	
	jason = readJson("0")
	now = time()
	notnow = now - (now%1200)
	
	
	for stream in jason['streams']:
		stream['value'] = random() * 100
		stream['timestamp'] = str(notnow)
	
	app.run(host='130.136.37.231', port=10014)
