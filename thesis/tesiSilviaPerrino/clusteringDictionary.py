#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

__author__ = 'Silvia'

# from database import metadati
import csv
from pyxdameraulevenshtein import damerau_levenshtein_distance

"""
Definire classi del dizionario (le 30 classi scelte)
"""
dictionary = {'Dust_Level': [], 'CPU_Usage': [], 'Distance': [], 'Energy': [], 'Capacity': [], 'Gas_Level': [],
              'Price': [], 'Geolocalization': [],
              'Brightness': [], 'Memory': [], 'Motion': [], 'Time': [], 'Power': [], 'Pressure': [], 'PH': [],
              'Rain_Index': [], 'Radiation': ['radiation'], 'Temperature': [],
              'Voltage': [], 'Current': [], 'Humidity': [], 'UV': [], 'Wind': [], 'Speed': [], 'Height': [], 'Rate': [],
              'Battery_Level': [], 'Heat_Index': [], 'Count': [], 'RSSI': [], 'LQI': [], 'Colour': []}

"""
Prendo una porzione di campi dal training set, e riempio il dizionario
"""
# Salvo su csv le coppie nome_campo - classe su cui effettuare il test

# file = open('campiDaTestare.csv', 'a+')
# file = open('coppieCampoClasse.csv', 'a+')
# n = 1
# for doc in metadati.find({"campi.classe": {"$exists": "true", "$ne": "null"}},
#                          {"campi.classe": 1, "campi.nome_campo": 1, "_id": 0}):
#     for stream in doc['campi']:
#         nome_campo = stream['nome_campo'].encode('utf8')
#         classe = stream['classe'].encode('utf8')
#         if classe != "CLASSE":
#             print n, nome_campo, classe
#             # file.write(str(nome_campo) + ',' + str(classe) + '\n')
#             if n > 500:
#                 file.write(str(nome_campo) + ',' + str(classe) + '\n')
#                 n += 1
#             else:
#                 n += 1


# Riempio il dizionario con i campi trovati
with open('coppieCampoClasse.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        campo = row[0].strip().lower().replace(' ', '_')
        classe = row[1].strip()
        # print campo, ',', classe
        dictionary[classe].append(campo)

# Salvo in una lista tutti i nomi_campo da testare
parole = []
with open('campiDaTestare.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        campo = row[0].strip().lower().replace(' ', '_')
        classe = row[1].strip()
        parole.append([campo, classe])

count_metriche = {}
for classe in dictionary.keys():
    count_metriche[classe] = {'classificate': 0,
                              'effettive': 0,
                              'classificate_esatte': 0}

file2 = open('risultatoDictionary.csv', 'a+')
# Per ogni parola da testare, calcolo la distanza che c'è tra tale parola ed ogni parola nella lista di nomi_campo salvate nel dizionario
for p in parole:
    classe_effettiva = p[1]
    # res è un dict che conterrà (per ogni parola da testare) tutte le classi e ad ognuna corrisponderà la distanza minima trovata (con le parole che la 'compongono')
    res = {}
    # Per ogni classe calcolo la distanza tra le parole di cui è composta e la parola da testare
    for classe in dictionary.keys():
        if classe == classe_effettiva:
            count_metriche[classe][
                'effettive'] += 1  # tra l'insieme di parole, quante sono effettivamente di tale classe

        dam = [(damerau_levenshtein_distance(p[0], campo_misurato)) for campo_misurato in
               dictionary[classe]]  # array di distanze per classe
        res[classe] = min(dam)
        # if len(dam) != 0:  #
        #     res[classe] = min(dam)

    # print res
    classe_attribuita = min(res, key=res.get)
    # print 'Classe attribuita -->', classe_attribuita, '\n'
    count_metriche[classe_attribuita]['classificate'] += 1  # quante volte attribuisco tale classe (giusta o sbagliata)
    # file2.write(str(p[0]) + ',' + ',' + str(p[1]) + ',' + str(min(res, key=res.get)) + '\n')
    if classe_effettiva == classe_attribuita:
        count_metriche[classe_attribuita]['classificate_esatte'] += 1


print count_metriche

"""
Metriche di riuscita per classe
"""
metriche = {}
for classe in count_metriche.keys():
    if (count_metriche[classe]['classificate_esatte'] is 0) and (count_metriche[classe]['classificate'] is 0) and (count_metriche[classe]['effettive'] is 0):
        count_metriche.pop(classe)
        continue
    else:

        metriche[classe] = {'precision': '',
                            'recall': '',
                            'f_measure': ''}
        try:
            if (count_metriche[classe]['classificate_esatte'] is not 0) and (count_metriche[classe]['classificate'] is not 0):
                precision = float(count_metriche[classe]['classificate_esatte']) / float(count_metriche[classe]['classificate'])
                metriche[classe]['precision'] = precision
            else:
                precision = 0.0
                metriche[classe]['precision'] = precision

            if (count_metriche[classe]['classificate_esatte'] is not 0) and (count_metriche[classe]['effettive'] is not 0):
                recall = float(count_metriche[classe]['classificate_esatte']) / float(count_metriche[classe]['effettive'])
                metriche[classe]['recall'] = recall
            else:
                recall = 0.0
                metriche[classe]['recall'] = recall

            if (precision is not 0.0) and (recall is not 0.0):
                pp = precision * recall
                pr = precision + recall
                # f_measure = 2*(float(precision*recall)/float(precision+recall))
                f_measure = 2 * (float(pp) / float(pr))
                metriche[classe]['f_measure'] = f_measure
            else:
                f_measure = 0.0
                metriche[classe]['f_measure'] = f_measure
        except ZeroDivisionError:
            print 'ZeroDivisionError', classe

print metriche

"""
Ci sono classi che non vengono classificate, perchè nel test set non sono presenti
"""
sum_recall = 0.0
sum_precision = 0.0
sum_f_measure = 0.0
classi_considerate = 0
# Fare le medie di questi valori
for classe in metriche.keys():
    # print classe, metriche[classe]
    classi_considerate += 1
    sum_recall += metriche[classe]['recall']
    sum_precision += metriche[classe]['precision']
    sum_f_measure += metriche[classe]['f_measure']  # ??

print 'classi considerate', classi_considerate
print sum_recall/classi_considerate, sum_precision/classi_considerate, sum_f_measure/classi_considerate


    # if (len(metriche[classe]['recall']) is 0) or (metriche[classe]['recall'] is 0) or (
    #     len(metriche[classe]['precision']) is 0) or (metriche[classe]['precision'] is 0) or (
    #                 len(metriche[classe]['f_measure']) is 0) or (metriche[classe]['f_measure'] is 0):
    #     print classe, metriche[classe]
