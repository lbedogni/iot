#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
__author__ = 'Silvia'


#from database import metadati
import csv, sys
from pyxdameraulevenshtein import damerau_levenshtein_distance
from itertools import *


# Here we define the 30 classes for our dictionary
dictionary = {'Dust_Level': [], 'CPU_Usage': [], 'Distance': [], 'Energy': [], 'Capacity': [], 'Gas_Level': [],
              'Price': [], 'Geolocalization': [],
              'Brightness': [], 'Memory': [], 'Motion': [], 'Time': [], 'Power': [], 'Pressure': [], 'PH': [],
              'Rain_Index': [], 'Radiation': [], 'Temperature': [],
              'Voltage': [], 'Current': [], 'Humidity': [], 'UV': [], 'Wind': [], 'Speed': [], 'Height': [], 'Rate': [],
              'Battery_Level': [], 'Heat_Index': [], 'Count': [], 'RSSI': [], 'LQI': [], 'Colour': []}
              
# Prepare our evaluation structure
count_metriche = {}
for classe in dictionary.keys():
	count_metriche[classe] = {'classificate': 0,
							  'effettive': 0,
							  'classificate_esatte': 0}

# Here we fill the dictionary with the training set plus preprocessing (lowercase and whitespaces)
def riempi_dizionario(f):
    with open(f, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            campo = row[0].strip().lower().replace(' ', '_')
            classe = row[1].strip()
            dictionary[classe].append(campo)

# fill the test set with every field, all of them encoded in arrays (name, class, stream name, description, tag, tag, tag,....)
def get_words(f):
    parole = []
    with open(f, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            lista_campo = []
            campo = row[0].strip().lower().replace(' ', '_')
            classe = row[1].strip()
            nome = row[2].strip().lower()
            descrizione = row[3].strip().lower()
            lista_campo.append(campo)
            lista_campo.append(classe)
            if (nome is not '') and (descrizione is not ''):
                lista_campo.append(nome)
                lista_campo.append(descrizione)
            for i in range(4, len(row)):
                if row[i] is not '':
                    tag = row[i].strip()
                    lista_campo.append(tag)

            parole.append(lista_campo)
    return parole

def riclassifica_per_tag(p, tags, classi_da_riclassificare):
    parola = p[0]
    tags.append(parola)
    res = {}
    if len(classi_da_riclassificare) > 0:
        print 'riclassifica per tag solo per alcune classi'
        for classe in classi_da_riclassificare:  # solo le classi con distanza simile o uguale
            dam = []
            for campo_misurato in dictionary[classe]:
                for tag in tags:
                    dam.append(damerau_levenshtein_distance(tag,campo_misurato))

            res[classe] = min(dam)
            # print 'dam', classe, '(', min(dam), ')-->', dam
        return res
    else:
        print 'riclassifica per tag per tutte le classi'
        for classe in dictionary.keys():  # tutte le classi
            dam = [[(damerau_levenshtein_distance(tag, campo_misurato)) for tag in tags] for campo_misurato in dictionary[classe]]
            res[classe] = min(dam)
            # print 'dam', classe, '----->', dam  # TODO !?!?!??!

        return res


def classificazione(x, y):
	parole = get_words('test_set_1.csv')
	for p in parole:
		
		# Extract parts of the record
		parola = p[0]
		classe_effettiva = p[1]
		if len(p) > 4:
			tags = []
			for i in range(4, len(p)):
				tags.append(p[i])

		# res è un dict che conterrà (per ogni parola da testare) tutte le classi
		# e ad ognuna corrisponderà la distanza minima trovata (con le parole che la 'compongono')
		res = {}
		# **************** PRIMA CLASSIFICAZIONE *****************
		# Per ogni classe calcolo la distanza tra le parole di cui è composta e la parola da testare
		for classe in dictionary.keys():
			if classe == classe_effettiva:
				count_metriche[classe]['effettive'] += 1  # di ogni classe nel diz. so quante ce ne sono davvero

			# For each term in the dictionary for each class i save the DL distance, then i pick the minimum per class
			dam = [(damerau_levenshtein_distance(p[0], campo_misurato)) for campo_misurato in
				dictionary[classe]]  # array di distanze per classe
			res[classe] = min(dam) # I pick the minimum distance for each class
			
		distanza_minima = res[min(res, key=res.get)]
		classi_con_stessa_distanza_minima = []  # riempio una lista per vedere se la distanza minima trovata è duplicata
		print 'PAROLA', parola, 'CLASSE', classe_effettiva, '-', x, '%', (len(parola) * x) / 100, 'distanza minima:', distanza_minima
		for key, value in res.iteritems():  # TODO casi in cui ci sono distanze uguali !!
			if value == distanza_minima:
				# print 'distanza minima =', key
				classi_con_stessa_distanza_minima.append(key)
		lista_distanze = []
		
		for c in res.keys():
			lista_distanze.append(res[c])

		if distanza_minima is 0:
			# print 'LA DISTANZA MINIMA è 0'
			# TODO non so se riclassificare -> può venir fuori lo stesso risultato
			if lista_distanze.count(0) > 1:  # è stata trovata più di una classe con distanza 0 -> riclassifico per quelle classi
				#XXX res = riclassifica_per_tag(p, tags, classi_con_stessa_distanza_minima)
				res = res #toglilo
		else:
			# print 'LA DISTANZA MINIMA NON è 0'
			"""
			A questo punto, verifico due condizioni:
			- se la distanza minima trovata tra tutte le classi è maggiore del x% di len(parola)
			- se ci sono due distanze molto simili che hanno differenza y% sulla lunghezza
			"""
			percent_lunghezza = (len(parola) * x) / 100

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
		count_metriche[classe_attribuita]['classificate'] += 1
		if classe_effettiva == classe_attribuita:
			count_metriche[classe_attribuita]['classificate_esatte'] += 1
		print 'CLASSE ATTRIBUITA', classe_attribuita, 'distanza', res[classe_attribuita]
		
	return count_metriche

# FIXME la metrica totale è sbagliata
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
    with open("risultati.csv", 'a') as reslt:
		reslt.write(",".join([sys.argv[1], sys.argv[2], str(sum_precision/classi_considerate), str(sum_recall/classi_considerate), str(sum_f_measure/classi_considerate)]) + "\n")
		
    return sum_recall/classi_considerate, sum_precision/classi_considerate, sum_f_measure/classi_considerate

if __name__ == "__main__":
	riempi_dizionario('training_set_1.csv')

	# count_metriche = classificazione(60, 50)
	count_metriche = classificazione(int(sys.argv[1]), int(sys.argv[2]))
	print count_metriche
	# classificazione(15, 15)
	metriche = verifica_metriche(count_metriche)
	print metriche
	print '->', tot_metriche(metriche)
