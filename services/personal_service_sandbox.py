from flask import Flask
import json
from random import random, gauss
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
		if stream['data_class'] == 'TEMP':
			stream['value'] = gauss(14.0,1.4)
		else:
			stream['value'] = random() * 100
		stream['last_update_timestamp'] = str(datetime.datetime.fromtimestamp(notnow).isoformat())
	
	return json.dumps(jason, separators=(',',':'))

if __name__ == "__main__":
		
	app.run(host='130.136.37.15', port=10014)
