#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np  # from numpy package
import sklearn.cluster  # from sklearn package
import distance  # from distance package
import jaro
from pyxdameraulevenshtein import damerau_levenshtein_distance
import csv


dictionary = {'Dust_Level': [], 'CPU_Usage': [], 'Distance': [], 'Energy': [], 'Capacity': [], 'Gas_Level': [],
              'Price': [], 'Geolocalization': [],
              'Brightness': [], 'Memory': [], 'Motion': [], 'Time': [], 'Power': [], 'Pressure': [], 'PH': [],
              'Rain_Index': [], 'Radiation': ['radiation'], 'Temperature': [],
              'Voltage': [], 'Current': [], 'Humidity': [], 'UV': [], 'Wind': [], 'Speed': [], 'Height': [], 'Rate': [],
              'Battery_Level': [], 'Heat_Index': [], 'Count': [], 'RSSI': [], 'LQI': [], 'Colour': []}


def riempi_dizionario(file):
    with open(file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            campo = row[0].strip().lower().replace(' ', '_')
            classe = row[1].strip()
            dictionary[classe].append(campo)


"""
Riempio un array con la lista di parole da clusterizzare con le relative classi
"""
parole = []  # parole da classificare / clusterizzare
parole_classe = []
# with open('coppieCampoDescrNomeTagClasse.csv', 'rb') as csvfile:
with open('test_set_1.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        nome_classe = []
        campo = row[0].strip().lower().replace(' ', '_')
        classe = row[1].strip()
        nome_classe.append(campo)
        nome_classe.append(classe)
        parole.append(campo)
        parole_classe.append(nome_classe)

"""
Per ogni elemento nel cluster, verifico la classe (con dictionary ?)
e tengo il conto di quante classi ho trovato e qual e' in % quella con + occorrenze
"""

count_metriche = {}
for classe in dictionary.keys():
    count_metriche[classe] = {'classificate': 0,
                              'effettive': 0,
                              'classificate_esatte': 0}


def classe_reale(parola):
    for p in parole_classe:
        if p[0] == parola:
            classe = p[1]
            return classe


def calcola_precisione_dizionario(lista_cluster):
    totale_campi = len(lista_cluster)
    classi_attribuite = {}
    # riempi_dizionario('coppieCampoClasse.csv')
    riempi_dizionario('training_set_1.csv')
    for elem in lista_cluster:
        res = {}
        for classe in dictionary.keys():
            dam = [(damerau_levenshtein_distance(elem, campo_misurato)) for campo_misurato in dictionary[classe]]
            res[classe] = min(dam)

        classe_attribuita = min(res, key=res.get)

        if classi_attribuite.get(classe_attribuita) is None:
            classi_attribuite[classe_attribuita] = 1
        else:
            classi_attribuite[classe_attribuita] += 1

    classe_piu_frequente = max(classi_attribuite, key=classi_attribuite.get)
    # 100 : totale_campi = x : classi_attribuite[classe_piu_frequente]
    percentuale = (100 * classi_attribuite[classe_piu_frequente])/totale_campi

    return classe_piu_frequente, percentuale


def calcola_precisione_classe(lista_cluster):
    totale_campi = len(lista_cluster)
    classi_attribuite = {}
    for elem in lista_cluster:
        # Aggiungo la classe vera di questa parola tra le classi effettive
        count_metriche[classe_reale(elem)]['effettive'] += 1  # TODO la classe effettiva si riferisce al cluster o al campo ?!!
        res = {}
        for classe in dictionary.keys():
            dam = (damerau_levenshtein_distance(elem, classe))
            res[classe] = dam

        classe_attribuita = min(res, key=res.get)
        count_metriche[classe_attribuita]['classificate'] += 1

        if classe_reale(elem) == classe_attribuita:
            count_metriche[classe_reale(elem)]['classificate_esatte'] += 1

        if classi_attribuite.get(classe_attribuita) is None:
            classi_attribuite[classe_attribuita] = 1
        else:
            classi_attribuite[classe_attribuita] += 1

    classe_piu_frequente = max(classi_attribuite, key=classi_attribuite.get)
    # 100 : totale_campi = x : classi_attribuite[classe_piu_frequente]
    percentuale = (100 * classi_attribuite[classe_piu_frequente])/totale_campi

    return classe_piu_frequente, percentuale

# Affinity propagation
words = np.asarray(parole)  # So that indexing with a list will work

dam = np.array([[(damerau_levenshtein_distance(w1, w2)) for w1 in words] for w2 in words])

distance_matrix = dam  # matrice con le distanze
affinity_matrix = 1 - distance_matrix

# AFFINITY PROPAGATION CLUSTERING #
mymat = -1 * distance_matrix
print mymat
# Perform Affinity Propagation Clustering of data
affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
# Create affinity matrix from negative euclidean distances, then apply affinity propagation clustering.
affprop.fit(mymat)

percentuali = 0
for cluster_id in np.unique(affprop.labels_):
    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
    cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
    print calcola_precisione_classe(cluster)
    percentuali += calcola_precisione_classe(cluster)[1]
    cluster_str = ", ".join(cluster)
    print(" - * %s: * %s" % (exemplar, cluster_str))  # (exemplar, cluster_str))

print len(np.unique(affprop.labels_)), 'cluster'
num_cluster = len(np.unique(affprop.labels_))

print percentuali/num_cluster, '%'
print count_metriche


def verifica_metriche(count_metriche):
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

    return metriche
metriche = verifica_metriche(count_metriche)
print 'metriche', metriche


def tot_metriche(metriche):
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
    print '***** recall *****  **** precision ****  **** f-measure ****'
    return sum_recall/classi_considerate, sum_precision/classi_considerate, sum_f_measure/classi_considerate
print '->', tot_metriche(metriche)