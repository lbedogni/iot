#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database import metadati, dati
from datetime import datetime, timedelta
import requests
import json
import sys

"""
    Per ogni stream/channel già salvato nel db -> prendere i dati e salvarli in un'altra collection solo per i dati.
    Per prima cosa vedo se i dati dello stream sono gia salvati nella collection 'dati':
        - se si, controllo update
        - se no, salvo tutti i dati (nuovo documento)

    Scorro i metadati, per ogni stream controllo l'ultimo update:
        - se l'ultimo update nei metadati è recente:
            - non faccio nulla.
        - se è passata piu di mezz'ora, cerco nuovi update:
            - se ci sono li salvo
            - se non ci sono nuovi update, non faccio nulla.

    Last update -> ultima volta in cui i dati sono stati caricati. 2016-05-09T15:22:48.820Z

    In TS potrei usare il last_entry_id per vedere se ci sono nuovi update. (ma anche no)

    PROBLEMI:
        - non riesce a salvare documenti troppo grandi (finora visto solo con SF)

"""


def passata_mezzora(timestamp):  # 2016-05-09T15:22:48.820Z
    # Confronta l'orario passato come parametro con l'ora corrente -> se è passata mezz'ora, ritorna TRUE
    now = datetime.utcnow()
    m = str(now - timedelta(minutes=30)).split('.')[0]
    if m > timestamp.replace('T', ' '):
        return True
    else:
        return False


# Analizza tutti gli stream nella collection dei metadati
for doc in metadati.find({}):
    stream = doc['stream_id']
    print 'stream', stream
    # Se lo stream è gia nella collection dei dati, li aggiorno se ci sono update recenti
    if dati.find_one({"stream_id": str(stream)}) is not None:
        last_update = doc['last_update']
        print 'Last update', doc['last_update']
        if not passata_mezzora(last_update):
            continue
        else:
            print 'Cerca ultimi update'
            # Vedo se si tratta di TS o SF
            if type(stream) is not int and 'streams' in stream:
                # Contro che ci siano update successivi all'ultimo update trovato nei metadati
                try:
                    response = requests.get('https://data.sparkfun.com/output/' + stream.split('/')[2] + '.json')
                    data_stream = json.loads(response.content)

                    if last_update < data_stream[0]['timestamp']:  # ultimo update tra i dati

                        for update in data_stream:
                            if update['timestamp'] is last_update:
                                index_last_update = list.index(update)

                                for i in range(0, index_last_update):
                                    dati.find_one_and_update({"stream_id": str(stream)}, {'$push': {'update': data_stream[i]}})

                                metadati.find_one_and_update({"stream_id": str(stream)},
                                                     {'$set': {'last_update': data_stream[0]['timestamp']}})

                                break  # TODO controllare questi break se vanno bene
                    else:
                        print 'non cè niente da aggiornare'
                        continue
                except:
                    print "Unexpected error:", sys.exc_info()[0]
            else:
                # Dovrei controllare che ci siano update successivi temporalmente all'ultimo update trovato nei metadati
                try:
                    response = requests.get('https://thingspeak.com/channels/' + str(stream) + '/feed.json')
                    data_stream = json.loads(response.content)

                    if last_update < data_stream['channel']['updated_at']:  # ultimo update tra i dati

                        for update in data_stream['feeds']:
                            if update['created_at'] is last_update:
                                index_last_update = list.index(update)

                                for i in range(index_last_update+1, len(data_stream['feeds'])):
                                    dati.find_one_and_update({"stream_id": str(stream)},
                                                             {'$push': {'update': data_stream['feeds'][i]}})

                                metadati.find_one_and_update({"stream_id": str(stream)},
                                                             {'$set': {'last_update': data_stream['channel']['updated_at']}})

                                break  # TODO controllare questi break se vanno bene
                    else:
                        print 'non cè niente da aggiornare'
                        continue
                except:
                    print "Unexpected error:", sys.exc_info()[0]
    else:
        print 'Salvo per la prima volta i dati dello stream . . .'
        # Eccezioni da gestire: document too large, connection broken, cursor not found
        if type(stream) is int:
            try:
                f = requests.get("https://thingspeak.com/channels/" + str(stream) + "/feed.json")
                jj = json.loads(f.content)

                l = []  # <----------------------------------
                # for update in jj['feeds']:
                #     update['timestamp'] = update['created_at']
                #     del update['created_at']
                #     l.append(update)

                for update in jj['feeds']:
                    update['timestamp'] = update['created_at']
                    del update['created_at']
                    for k in update.keys():
                        if 'field' in k:
                            campo_misurato = jj['channel'][k]
                            update[campo_misurato] = update[k]
                            del update[k]

                    l.append(update)

                doc = {
                    "stream_id": stream,
                    "update": l
                }
                post_id = dati.insert_one(doc).inserted_id

                # Aggiorna last_updati in metadati
                metadati.find_one_and_update({"stream_id": str(stream)},
                                             {'$set': {'last_update': jj['channel']['updated_at']}})

            except:
                print "Unexpected error:", sys.exc_info()[0]
        else:
            try:
                stream_id = stream.split('/')[2]
                f = requests.get("https://data.sparkfun.com/output/" + stream_id + ".json")
                jj = json.loads(f.content)

                doc = {
                    "stream_id": stream,
                    "update": jj
                }

                post_id = dati.insert_one(doc).inserted_id

                # Aggiorna last_updati in metadati
                metadati.find_one_and_update({"stream_id": stream}, {'$set': {'last_update': jj[0]['timestamp']}})

            except:
                print "Unexpected error:", sys.exc_info()[0]
