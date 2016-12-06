#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
__author__ = 'Davide'


#from database import metadati
import dbClustering
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from pyxdameraulevenshtein import damerau_levenshtein_distance
from itertools import *
import time
import datetime
import sys

#Vettore delle classi corrette
y_real = []

#Vettore delle classi attribuite
y_assigned = []

# Prepare our evaluation structure
count_metriche = {}


# Here we define the 30 classes for our dictionary
dictionary = {'Temperature': [], 'Dust_Level': [], 'Gas_Level': [],'Brightness': [], 'Power': [], 'UV': [],'Heat_Index': [],
              'Pressure': [], 'Rain_Index': [], 'Radiation': [],'Humidity': [], 'Wind_Direction': [], 'Wind_Speed': []}

#Classi rilevanti
relevant_labels = ['Temperature','Dust_Level','Gas_Level','Brightness','Power','UV','Heat_Index','Pressure', 'Rain_Index', 'Radiation',
                'Humidity', 'Wind_Direction', 'Wind_Speed']

db = dbClustering.MyDB()

"""
Call in a loop to create terminal progress bar
@params:
    iteration   - Required  : current iteration (Int)
    total       - Required  : total iterations (Int)
    prefix      - Optional  : prefix string (Str)
    suffix      - Optional  : suffix string (Str)
    decimals    - Optional  : positive number of decimals in percent complete (Int)
    barLength   - Optional  : character length of bar (Int)
"""
# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    #bar             = '█' * filledLength + '-' * (barLength - filledLength)
    bar = '=' * filledLength + '>' +' ' * (barLength - filledLength -1)  
    sys.stdout.write('\r%s [%s] %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def azzera_metriche():
    for classe in dictionary.keys():
	   count_metriche[classe] = {'classificate': 0,
                                 'effettive': 0,
                                 'classificate_esatte': 0}

def svuota_dizionario():
    for classe in dictionary:
        dictionary[classe] = []

# Here we fill the dictionary with the training set plus preprocessing (lowercase and whitespaces)
def riempi_dizionario(training_set):	
    svuota_dizionario()
    for stream in training_set:
        classe = stream["field_class"]
        field = stream["field_name"]
        dictionary[classe].append(field.strip().replace(' ', '_'))
	
# fill the test set with every field, all of them encoded in struct 
# {'field_id','field_name','field_class','channel_description','channel_name','channel_id','tag'}
def get_fields():
    fields = db.get_test_set()
    for field in fields:
        tags = db.getFieldTags(field["channel_id"])
        field["tags"] = tags

    return fields

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


def classificazione(test_set,x, y,number,current_prefix):
    l = len(test_set) - 1
    progress=0
    for stream in test_set:
        printProgress(progress, l, prefix = current_prefix, suffix = 'Complete', barLength = 50)
        field = stream["field_name"].strip().replace(' ', '_')
        #print "Classifico field: " + field

        # res è un dict che conterrà (per ogni parola da testare) tutte le classi
        # e ad ognuna corrisponderà la distanza minima trovata (con le parole che la 'compongono')
        res = {}
        # **************** PRIMA CLASSIFICAZIONE *****************
        # Per ogni classe calcolo la distanza tra le parole di cui è composta e la parola da testare
        for classe in dictionary.keys():
            if classe == stream["field_class"]:
                count_metriche[classe]['effettive'] += 1  # di ogni classe nel diz. so quante ce ne sono davvero

            # For each term in the dictionary for each class i save the DL distance, then i pick the minimum per class
            dam = [(damerau_levenshtein_distance(field, campo_misurato)) for campo_misurato in
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
        '''
        lista_distanze = []
        for c in res.keys():
            lista_distanze.append(res[c])
        print "lista_distanze",lista_distanze
        '''
        if distanza_minima is 0:
        	# TODO non so se riclassificare -> può venir fuori lo stesso risultato
        	if len(classi_con_stessa_distanza_minima) > 1:  # è stata trovata più di una classe con distanza 0 -> riclassifico per quelle classi
        		#XXX res = riclassifica_per_tag(p, tags, classi_con_stessa_distanza_minima)
        		res = res #toglilo
        else:
        	"""
        	A questo punto, verifico due condizioni:
        	- se la distanza minima trovata tra tutte le classi è maggiore del x% di len(field)
        	- se ci sono due distanze molto simili che hanno differenza y% sulla lunghezza
        	"""
        	percent_lunghezza = (len(field) * x) / 100

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
        count_metriche[classe_attribuita]['classificate'] += 1
        if stream["field_class"] == classe_attribuita:
        	count_metriche[classe_attribuita]['classificate_esatte'] += 1
        
        y_real.append(stream["field_class"])
        y_assigned.append(classe_attribuita)
        #print 'CLASSE ATTRIBUITA', classe_attribuita, 'distanza', res[classe_attribuita]
        db.store_classification(stream,classe_attribuita,res[classe_attribuita],number,"ClassificationRelevant")
        progress = progress + 1

    


#Calcolo le metriche
def verifica_metriche():
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
                if (count_metriche[classe]['classificate_esatte'] is not 0) and (count_metriche[classe]['effettive'] is not 0):
                    precision = float(count_metriche[classe]['classificate_esatte']) / float(count_metriche[classe]['effettive'])
                    metriche[classe]['precision'] = precision
                else:
                    precision = 0.0
                    metriche[classe]['precision'] = precision

                if (count_metriche[classe]['classificate_esatte'] is not 0) and (count_metriche[classe]['classificate'] is not 0):
                    recall = float(count_metriche[classe]['classificate_esatte']) / float(count_metriche[classe]['classificate'])
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

#Calcolo la media delle metriche
def tot_metrics(metriche,ts,number):
    sum_recall = 0.0
    sum_precision = 0.0
    sum_f_measure = 0.0
    classi_considerate = 0
    # Fare le medie di questi valori
    for classe in metriche.keys():
        # print classe, metriche[classe]
        classi_considerate += count_metriche[classe]["effettive"]
        sum_recall += metriche[classe]['recall'] * count_metriche[classe]["effettive"]
        sum_precision += metriche[classe]['precision'] * count_metriche[classe]["effettive"]
        sum_f_measure += metriche[classe]['f_measure']  * count_metriche[classe]["effettive"]

    metrica = {'precision': sum_precision/classi_considerate, 'recall': sum_recall/classi_considerate,'f_measure': sum_f_measure/classi_considerate}
    db.store_metric(metrica,"Totale",ts,number,"MetricRelevant")

def store_metrics(metriche,ts,number):
    for classe in metriche:
        db.store_metric(metriche[classe],classe,ts,number,"MetricRelevant")

#Creo la riga da passare alla query per l'inserimento
def create_row_to_store(values,number):
    row = ""
    for i in range(0,len(values)):
        row += str(values[i]) + ", "

    row += str(number)

    return row

def store_confusion_matrix(cm,labels,number,table):
    for i in range(0,len(cm)):
        db.store_matrix(labels[i], create_row_to_store(cm[i],number),table)


def print_dictionary():
    print "--------------------------------------------------------------------"
    for classe in dictionary:
        print classe,dictionary[classe]

if __name__ == "__main__":
    db.delete_classification("ClassificationRelevant") #Cancello l'ultima calssificazione
    db.delete_matrix("ConfusionMatrixRelevant")
    db.delete_metrics("MetricRelevant")
    all_streams = db.get_relevant_streams() 

    #k-fold validation
    for i in range(0,10):
        y_real = []
        y_assigned = []
        azzera_metriche()
        min_index = (i*96)
        max_index = ((i+1)*96)
        riempi_dizionario(all_streams[min_index:max_index])
        test_set = all_streams[:min_index] + all_streams[max_index:]    
        current_prefix = str(i+1) + "° classificazione"
        classificazione(test_set,60, 50,i,current_prefix)
        
    
        st = time.time()
        ts = datetime.datetime.fromtimestamp(st).strftime('%Y-%m-%d %H:%M:%S')
        
        metriche = verifica_metriche()
        store_metrics(metriche,ts,i)
        tot_metrics(metriche,ts,i)


        #Due confusion matrix: una per le calssi rilevanti, l'altra per tutte le classi
        cm_relevant = confusion_matrix(y_real,y_assigned,labels=relevant_labels)
store_confusion_matrix(cm_relevant,relevant_labels,i,"ConfusionMatrixRelevant")
