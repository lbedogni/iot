#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib import urlopen  # <-------------
import requests
import json
from googlemaps import Client
from database import collection


# maxPages = int(sys.argv[1])  # numero di pagine da prendere
pageArray = []
gmaps = Client(key='AIzaSyDGGQRjUKv2HkqPzotZx9isbz-xXVDR0NQ')


# def metaSparkfunParse():
#     print 'get metadata sparkfun'

# for i in range(maxPages):
# for i in range(100, 105):
#     page = i
#     print(i)
#     try:
#         # pageArray.append(urllib.request.urlopen("https://data.sparkfun.com/streams/?page=" + str(page)))
#         pageArray.append(urlopen("https://data.sparkfun.com/streams/?page=" + str(page)))
#     except:
#         print (sys.exc_info()[0])
#         continue

pageArray.append(urlopen("https://data.sparkfun.com/streams/?page=105"))
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

    # num = 1
    # file = open('titoliSparkfun.csv', 'a+')

    for l in html.readlines():
        line = l.decode('utf-8').strip()  # tutte le righe della pagina
        if 'class="pager"' in line:  # per capire che si tratta dell'ultimo stream
            # fw = open('metaSparkfun.csv', 'a+')
            # fw.write(", ".join(record[:4]).encode('utf-8') + ", " + str(", ".join(record[4])) + '\n')

            # doc = {"messagge": "Ho inserito un nuovo documento!!"}
            #
            # post_id = collection.insert_one(doc).inserted_id  # <--------------- insert_one

            print 'Salva metadati stream'
            # fw.close()

        if "stream-title" in line:

            if record[0] != "" or record[1] != "" or record[2] != "" or record[3] != "" or len(record[4]) != 0 or city[
                0] != "" or city[1] != "" or city[2] != "":
                # fw = open('metaSparkfun.csv', 'a+')
                # fw.write(", ".join(record[:4]).encode('utf-8') + ", " + str(", ".join(record[4])) + '\n')

                # doc = {"stream_id": "",
                #        "nome": "",
                #        "descrizione": "",
                #        "tags": [],  # array di stringhe
                #        "campi": [{}, {}],  # array di json
                #        "geolocalization": {"longitude": "", "latitude": ""}}
                #
                # post_id = collection.insert_one(doc).inserted_id  # <--------------- insert_one

                print 'Salva metadati stream'
                # fw.close()

            # Azzerare
            record = ["", "", "", "", []]
            city = ["", "", ""]

            # Prendi lo stream e il nome
            stream = line.split("\"")[3]
            record[0] = stream
            list_stream.append(stream)

            stream_id = stream.split("/")[2]
            response = requests.get("https://data.sparkfun.com/streams/"+stream_id+".json")
            metadata_stream = json.loads(response.content)  # dict 
            # print metadata_stream['stream']["_doc"]["description"]

            # Cerca stream su db <--------------------------------------------------------
            metadatiStream = collection.find_one({"stream_id": stream})

            # if metadatiStream is not None:
            #     print 'Lo stream', stream, 'è gia salvato'.decode('utf-8')
            #     break
            # else:
            #     print 'Lo stream', stream, 'non è ancora stato salvato'.decode('utf-8')  # Salva metadati !!!!!!
                # doc = {"messagge": "Ho inserito un nuovo documento!!"}
                #
                # post_id = collection.insert_one(doc).inserted_id  # <--------------- insert_one

            name = line.split(">")[2].split("<")[0]
            record[1] = name

            # file.write(str(num) + ': ' + str(line.encode('utf-8').split('<')[2].split('>')[1]) + '\n')
            # num += 1

        if "/streams/city" in line:
            city[0] = line.split("/streams/city/")[1].split("\"")[0]
        elif "/streams/state" in line:
            city[1] = line.split("/streams/state/")[1].split("\"")[0]
        elif "/streams/country" in line:
            city[2] = line.split("/streams/country/")[1].split("\"")[0]

            address = ", ".join(city)
            # print 'address',address.encode('utf-8')
            # file.write('address:'+str(address.encode('utf-8')) + '\n')
            # sys.exit()
            if not address == ", , ":  # se l'indirizzo c'e' -> trova le coordinate
                geocoord = gmaps.geocode(address)[0]['geometry']['location']
                lat = str(geocoord['lat'])
                lng = str(geocoord['lng'])
                record[2] = lat
                record[3] = lng

        if "/streams/tag" in line:
            record[4].append(line.split("/streams/tag/")[1].split("\"")[0])
            tags = ", ".join(record[4])


# file.close()


# get_data_stream(list_stream)
