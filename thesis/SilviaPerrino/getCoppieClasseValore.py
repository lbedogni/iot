#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Silvia'

from database import metadati
import csv

"""
Estraggo i nomi campi già classificati manualmente (il primo training set)
"""

# file = open('coppieInputClasse.csv', 'a+')
#
# for doc in metadati.find({"$and": [{"campi.nome_campo": {"$exists": "true", "$ne": "null"}},
#                                    {"campi.classe": {"$exists": "true", "$ne": "null"}}]},
#                          {"campi.nome_campo": 1, "campi.classe": 1, "_id": 0}):
#     for campo in doc['campi']:
#         if campo['classe'] == 'CLASSE':
#             continue
#         else:
#             print campo['nome_campo'].encode('utf8'), campo['classe']
#             w = campo['nome_campo'].encode('utf8')
#             classe = campo['classe'].encode('utf8')
#             file.write(str(w) + ',' + str(classe) + '\n')
#
# file.close()

"""
Amplio il training test
"""

# file2 = open('campiDaClassificare.csv', 'a+')
#
# for doc in metadati.find({"campi.classe": "CLASSE"}, {"campi.nome_campo": 1, "campi.classe": 1, "_id": 0}):
#     for campo in doc['campi']:
#         if campo['classe'] == "CLASSE":
#             print campo['nome_campo'].encode('utf8'),',',campo['classe'].encode('utf8')
#             c = campo['nome_campo'].encode('utf8')
#             file2.write(str(c) + ', CLASSE' + '\n')

"""
Dopo aver classificato manualmente i campi nel csv, li prendo nuovamente e salvo le modifiche nel db
"""

with open('campiDaClassificare.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        campo = row[0].strip()
        classe = row[1].strip()
        print campo, ',', classe
        # query -> cerco il campo nel db, applico a tale campo la classe scelta
        metadati.update({"campi.nome_campo": campo}, {"$set":{"campi.$.classe": classe}}, multi=True)




