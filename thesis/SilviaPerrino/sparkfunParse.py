#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib import urlopen
import requests
import json
from googlemaps import Client
from database import metadati
from database import test_set


# maxPages = int(sys.argv[1])  # numero di pagine da prendere
pageArray = []
gmaps = Client(key='AIzaSyDGGQRjUKv2HkqPzotZx9isbz-xXVDR0NQ')


# def metaSparkfunParse():
#     print 'get metadata sparkfun'

# for i in range(maxPages):
for i in range(0, 5):
    page = i
    print(i)
    try:
        # pageArray.append(urllib.request.urlopen("https://data.sparkfun.com/streams/?page=" + str(page)))
        pageArray.append(urlopen("https://data.sparkfun.com/streams/?page=" + str(page)))
    except:
        print (sys.exc_info()[0])
        continue

# pageArray.append(urlopen("https://data.sparkfun.com/streams/?page=0"))
print ("LENGTH = " + str(len(pageArray)))

# Lista di streams id #
list_stream = []


def get_data_stream(list_stream):  # Prendere i dati di tutti gli stream presi in considerazione e salvarli su csv #
    print 'Salva dati stream'
    data = open('dataSparkfun.csv', 'a+')
    for stream in list_stream:
        # for line in file('dataSparkfun.csv'):
        #     if stream in line:
        #         print 'trovato'
        #         # rimuovi duplicati
        stream_id = stream.split("/")[2]
        response = requests.get('https://data.sparkfun.com/output/' + stream_id + '.json')
        data_stream = json.loads(response.content)
        # Rimuovere i duplicati
        if type(data_stream) == dict and data_stream[data_stream.keys()[0]] == 'no data has been pushed to this stream':
            continue
        else:
            print 'Salva dati stream'
            data.write(str(stream) + '\n')
            for update in data_stream:  # per ogni update salva timestamp e valori misurati
                data.write(str(update['timestamp']) + ', ')
                for key in update.keys():
                    if len(update[key]) > 0 and key != 'timestamp':
                        data.write(str(update[key]).encode('utf-8') + ', ')

                data.write('\n')

            data.write('\n')

    data.close()


record = ["", "", "", "", []]
city = ["", "", ""]  # city - region - state
for html in pageArray:

    for l in html.readlines():
        line = l.decode('utf-8').strip()  # tutte le righe della pagina

        if "stream-title" in line:

            # # Azzerare
            # record = ["", "", "", "", []]
            # city = ["", "", ""]

            # Prendi l'id dello stream
            stream = line.split("\"")[3]
            # record[0] = stream
            list_stream.append(stream)

            # Cerca stream su db <--------------------------------------------------------
            metadatiStream = metadati.find_one({"stream_id": stream})
            # metadatiStream = test_set.find_one({"stream_id": stream})

            if metadatiStream is not None:
                print 'Lo stream', stream, 'è gia salvato'.decode('utf-8')
                continue
            else:
                print 'Lo stream', stream, 'non è ancora stato salvato'.decode('utf-8')  # Salva metadati !!!!!!
                stream_id = stream.split("/")[2]
                try:
                    response = requests.get("https://data.sparkfun.com/streams/" + stream_id + ".json")  # file contenente metadati
                    metadata_stream = json.loads(response.content)  # dict

                    geolocalization = {"latitude": "",
                                       "longitude": ""}
                    # Lo stream potrebbe non avere geolocalizzazione
                    if 'location' in metadata_stream['stream']['_doc'].keys() and len(metadata_stream['stream']['_doc']['location']) != 0:
                            geolocalization["latitude"] = metadata_stream['stream']['_doc']['location']['lat']
                            geolocalization["longitude"] = metadata_stream['stream']['_doc']['location']['lng']

                    campi = []
                    for nome_campo in metadata_stream['stream']["_doc"]["fields"]:
                        campi.append({"nome_campo": nome_campo, "classe": "CLASSE"})

                    doc = {"stream_id": stream,
                           "nome": metadata_stream['stream']["_doc"]["title"],
                           "descrizione": metadata_stream['stream']["_doc"]["description"],
                           "tags": metadata_stream['stream']["_doc"]["tags"],  # array di stringhe
                           # "campi": metadata_stream['stream']["_doc"]["fields"],  # array di dict
                           "campi": campi,
                           "geolocalization": geolocalization,
                           "last_update": metadata_stream['stream']["_doc"]["last_push"]
                           }

                    post_id = metadati.insert_one(doc).inserted_id
                    # post_id = test_set.insert_one(doc).inserted_id
                    print '---> Documento inserito <---'
                except:
                    print "Unexpected error:", sys.exc_info()[0]

# get_data_stream(list_stream)
