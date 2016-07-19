#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from urllib.request import urlopen  # version 3
from urllib import urlopen  # version 2.7
import json
import sys
# from urllib.error import HTTPError  # version 3
from urllib2 import HTTPError  # version 2.7
from database import metadati

# Prende tutti i dati da ThingSpeak e li salva su 2 file CSV: uno per i metadati e l'altro per i dati

# f_meta = open('metaFromTS.csv', 'a+')
# f_data = open('dataFromTS.csv', 'a+')
# f_erro = open('erroFromTS.csv', 'a+')
# f_keys = open('keysFromTS.csv', 'a+')

# Parametri che possono essere estratti dagli stream
keyArray = ['description', 'elevation', 'name', 'created_at', 'updated_at', 'longitude', 'latitude', 'last_entry_id',
            'id']

# for i in range(0, 101000):
for i in range(800, 900):
    # Cerca stream su db <--------------------------------------------------------
    metadatiStream = metadati.find_one({"stream_id": i})

    if metadatiStream is not None:
        print 'Lo stream', i, 'è gia salvato'.decode('utf-8')
        continue
    else:
        print 'Lo stream', i, 'non è ancora stato salvato'.decode('utf-8')  # Salva metadati !!!!!!
        ff = "https://thingspeak.com/channels/" + str(i) + "/feed.json"
        print(ff)
        f = ""
        jj = ""
        try:
            f = urlopen("https://thingspeak.com/channels/" + str(i) + "/feed.json").read().decode("utf-8")
            jj = json.loads(f)  # string to json

            # Questi json hanno 2 campi -> "channel" e "feeds" (feeds e' una lista)
            chan = jj['channel']  # metadati
            campi = []
            for item in chan.keys():
                if item.startswith('field'):  # questo e' un campo misurato dallo stream
                    campi.append({'nome_campo': chan[item], "classe": "CLASSE"})
                    # f_data.write(str(i) + ',' + str(item) + ',' + str(chan[item]) + '\n')
                # elif item not in keyArray:  # questo e' un nuovo parametro non ancora preso in considerazione
                    # f_keys.write(str(i) + ',' + str(item) + ',' + str(chan[item]) + '\n')
            for item in keyArray:
                if item not in chan.keys():
                    chan[item] = ""  # aggiunge campo vuoto

            # Metadati
            # f_meta.write(",".join([str(i), chan['name'].replace(",", ";").replace("\n", ""),
            #                        chan['description'].replace(",", ";").replace("\n", ""), chan['created_at'],
            #                        chan['updated_at'], chan['longitude'], chan['latitude'], chan['elevation'],
            #                        str(chan['last_entry_id'])]))
            # f_meta.write('\n')

            page = urlopen("https://thingspeak.com/channels/" + str(i) + "")
            tags = []
            for line in page.readlines():
                if "channel-tags" in line:
                    tags.append(line.split(">")[1].split("<")[0])

            doc = {"stream_id": i,
                   "nome": chan["name"],
                   "descrizione": chan["description"],
                   "tags": tags,
                   "campi": campi,
                   "geolocalization": {"longitude": chan["longitude"],
                                       "latitude": chan["latitude"]},
                   "last_update": chan["updated_at"],
                   "last_entry_id": chan["last_entry_id"]
                   }
            post_id = metadati.insert_one(doc).inserted_id
            print 'Documento inserito'

        except KeyError:
            print 'key error'
        except HTTPError:
            pass
        except:
            print(sys.exc_info()[0])

# f_meta.close()
# f_data.close()
# f_erro.close()
# f_keys.close()
