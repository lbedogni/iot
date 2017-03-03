#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlopen
import json
import sys
from urllib2 import HTTPError

from clustering import training_set_db, sensquare_db
from pyxdameraulevenshtein import damerau_levenshtein_distance

from datetime import datetime, timedelta
import requests

keyArray = ['description', 'elevation', 'name', 'created_at', 'updated_at', 'longitude', 'latitude', 'last_entry_id', 'id', 'tags', 'metadata', 'url']

training_db = training_set_db.MyDB()
sensquare = sensquare_db.MyDB()


training_set = training_db.get_training_set_relevant_streams()

dictionary = {'Temperature': [], 'Dust_Level': [], 'Gas_Level': [],'Brightness': [], 'Power': [], 'UV': [],'Heat_Index': [],
              'Pressure': [], 'Rain_Index': [], 'Radiation': [],'Humidity': [], 'Wind_Direction': [], 'Wind_Speed': []}

classes_to_id = {
	'Temperature' : 'TEMP',
	'Dust_Level': 'DUST',
	'Gas_Level': 'GASL',
	'Brightness': 'BRTH',
	'Power':'POWR',
	'UV':'UV',
	'Heat_Index':'HTIX',
	'Pressure': 'PRES' ,
	'Rain_Index': 'RAIN',
	'Radiation': 'RADI',
	'Humidity': 'HUMY',
	'Wind_Direction': 'WIDR',
	'Wind_Speed': 'WISP'
}


# Here we fill the dictionary with the training set plus preprocessing (lowercase and whitespaces)
def fill_dictionary():    
    for stream in training_set:
        classe = stream["field_class"]
        field = stream["field_name"]
        dictionary[classe].append(field.strip().replace(' ', '_'))

def trim_string(string):
	string = string.replace('"','')
	string = string.replace("'","")
	return string


def classificate(stream,x,y):
    
    # res è un dict che conterrà (per ogni parola da testare) tutte le classi
    # e ad ognuna corrisponderà la distanza minima trovata (con le parole che la 'compongono')
    res = {}
    # **************** PRIMA CLASSIFICAZIONE *****************
    # Per ogni classe calcolo la diumbstanza tra le parole di cui è composta e la parola da testare
    for classe in dictionary.keys():

        # For each term in the dictionary for each class i save the DL distance, then i pick the minimum per class
        dam = [(damerau_levenshtein_distance(stream, campo_misurato)) for campo_misurato in
            dictionary[classe]]  # array di distanze per classe

        if len(dam) > 0:
            res[classe] = min(dam) # I pick the minimum distance for each class

        #else:
            #res[classe] = 50 #Da modificare, ma per ora serve per evitare problemi con le classi senza parole
        distanza_minima = res[min(res, key=res.get)]
        classi_con_stessa_distanza_minima = []  # riempio una lista per vedere se la distanza minima trovata è duplicata
        for key, value in res.iteritems():  # TODO casi in cui ci sono distanze uguali !!
            if value == distanza_minima:
                # print 'distanza minima =', key
                classi_con_stessa_distanza_minima.append(key)

        if distanza_minima is 0:
        	# TODO non so se riclassificare -> può venir fuori lo stesso risultato
        	if len(classi_con_stessa_distanza_minima) > 1:  # è stata trovata più di una classe con distanza 0 -> riclassifico per quelle classi
        		#XXX res = riclassifica_per_tag(p, tags, classi_con_stessa_distanza_minima)
        		res = res #toglilo
        else:
        	"""
        	A questo punto, verifico due condizioni:
        	- se la distanza minima trovata tra tutte le classi è maggiore del x% di len(strea,)
        	- se ci sono due distanze molto simili che hanno differenza y% sulla lunghezza
        	"""
        	percent_lunghezza = (len(stream) * x) / 100
            #se non rispetta la condizione la assumo come buona
        	if distanza_minima > percent_lunghezza:
        		# riclassifico solo per alcune classi !?
        		# TODO cerco le classi con distanze simili alla distanza minima
        		# aggiungo alla lista di distanza minima simile, le classi con distanze diverse ma simili
        		for classe, dist in res.iteritems():
        			diff = (abs((distanza_minima - dist)) * y) / 100
        			if diff < percent_lunghezza and (dist != distanza_minima):
        				classi_con_stessa_distanza_minima.append(classe)
        				
        			#XXX res = riclassifica_per_tag(p, tags, classi_con_stessa_distanza_minima)

        # We decide finally the class and check whether is right or wrong
    
	
    classe_attribuita = min(res, key=res.get)
    return classe_attribuita

def get_and_classificate(beg,fin):
	print "-----------------------------INIZIO----------------------------------"
	
	for i in range(beg,fin):
		print i	
		print "Evaluating channel " + str(i) + "..."
		ff = "https://thingspeak.com/channels/" + str(i) + "/feed.json"
		f = ""
		jj = ""
		
		try:
			# Parse the JSON from the page and get the root element
			f = urlopen('https://thingspeak.com/channels/' + str(i) + '/feed.json').read().decode("utf-8")
			jj = json.loads(f)  # string to json

			#If the cannel is valid we get all the fields then we try to classificate
			chan = jj['channel']  # metadata
			#print chan

			channel_lat = trim_string(str(chan['latitude'])).decode("utf-8")
			channel_lng = trim_string(str(chan['longitude'])).decode("utf-8")

			if 35 <= float(channel_lat) <= 48 and 6 <= float(channel_lng) <= 18.5:

				channel_id = trim_string(str(chan['id'])).decode("utf-8")
				channel_name = trim_string(str(chan['name'])).decode("utf-8")
				channel_description = trim_string(str(chan['description'])).decode("utf-8")
				#we only classificate italian's channels
				print "Italia"
				print 'https://thingspeak.com/channels/' + str(i) + '/feed.json'
				
				channel = {
					'name':channel_name,
					'description': channel_description,
					'latitude':channel_lat,
					'longitude':channel_lng,
					'url':'https://thingspeak.com/channels/' + str(i)
				}

				#print channel
				streams = []
				measurements = jj['feeds']
				for item in chan.keys():
					if item.startswith('field'):  # we found a field
						stream_name = str(chan[item]).replace('"','').decode('utf-8')
						classe = classificate(stream_name,50,60)
						stream_measurements = []

						for measure in measurements:
							stream_measurements.append({
								'value': measure[item],
								'timestamp': measure['created_at']
							})

						stream = {
							'stream_name': stream_name,
							'stream_class': classes_to_id[classe],
							'measurements': stream_measurements	
						}

						streams.append(stream)

				sensquare.store_channel_and_streams(channel,streams)

		except KeyError:
			print "HTTP 404 Response"
			
		# We pass those 'cause we might have some private channels	
		except HTTPError:
			pass
		
		except TypeError:
			print "This is a Private Channel..."
			
		except UnicodeEncodeError:
			pass

		# What else?
		except:
			print(sys.exc_info()[0])

if __name__ == "__main__":
	
	
	beg = int(sys.argv[1])
	fin = int(sys.argv[2])
	
	'''
	#Cosi prendo solo gli stream pubblici (anche se non vengono dati proprio tutti)
	jj = ""
	public_channels = []
	for i in range(2,626):
		print i
		f = urlopen('https://thingspeak.com/channels/public.json?page=' + str(i)).read().decode("utf-8")
		jj = json.loads(f)
		channels = jj["channels"]
		for channel in channels:
			public_channels.append(channel['id'])

	print "Inizio"
	'''
	
	fill_dictionary()
	get_and_classificate(beg,fin)
	

	