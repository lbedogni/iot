#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Silvia'

from database import dati
from time import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from pyxdameraulevenshtein import damerau_levenshtein_distance
import collections

from scipy.cluster.vq import vq, kmeans, whiten
import scipy

"""
QUESTO SOTTO E' UN ESEMPIO SEMPLICE CHE FUNZIONA

# d = [46.6000, 79.3400, 8, 46.7000, 79.3400, 7, 46.6000, 79.3400, 0, 46.5000, 79.5200, 7, 46.4000, 79.5200, 8]
# d_np = np.array(d)
#
# k_means = KMeans(init='k-means++', n_clusters=3, n_init=10, max_iter=10)
# k_means.fit(d_np.reshape(-1, 1))
# print k_means.cluster_centers_  # CLUSTER TROVATI
"""

# file = open('datiStream.csv', 'a+')
def get_data_from_db():
    dati_numerici = []
    for doc in dati.find({}):
        if len(doc['update']) is not 0:
            for update in doc['update']:
                for campo in update.keys():
                    if (campo != 'timestamp') and (campo != 'entry_id') and (update[campo] is not None) and (len(update[campo]) != 0):
                        dato = update[campo].encode('utf8')
                        try:
                            if len(dato) is not 0:
                                dati_numerici.append(float(dato))
                                # file.write(str(dato))
                                # file.write('\n')
                            else:
                                continue
                        except ValueError:
                            continue

    return dati_numerici



# dati_numerici = get_data_from_db()
# dati_numerici = list(set(dati_numerici))  # rimuove dati duplicati
# print dati_numerici  # 54503

# d_np = np.array(dati_numerici)
# k_means = KMeans(init='k-means++', n_clusters=30, n_init=10, max_iter=30)
# # k_means = KMeans(init='k-means++', n_clusters=10, n_init=10, max_iter=30)
# k_means.fit(d_np.reshape(-1, 1))  # scikit expects a 2D array with a samples and a features axis
# print k_means.cluster_centers_  # CLUSTER TROVATI


# dati_numerici = [0.0, 175.5, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0, 80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110]
# d_np = np.array(dati_numerici)
# varianza = np.var(dati_numerici)
# media = np.mean(dati_numerici)
# x, y = media, varianza

# ‘random’: generate k centroids from a Gaussian with mean and variance estimated from the data.
# k_means = scipy.cluster.vq.kmeans2(data=d_np.reshape(-1, 1), k=10, iter=10, minit='random', missing='warn')
# print k_means

parola = 'solarradiation'
percent_parola = (len(parola) * 15)/100
res = {'Battery_Level': 12, 'Capacity': 13, 'Temperature': 10, 'Time': 10, 'Radiation': 5, 'Rain_Index': 9, 'Current': 11, 'LQI': 12, 'Memory': 13, 'Power': 11, 'Price': 10, 'Pressure': 10, 'RSSI': 12, 'PH': 14, 'Heat_Index': 12, 'Count': 14, 'Distance': 12, 'CPU_Usage': 13, 'Gas_Level': 13, 'Brightness': 11, 'Colour': 11, 'Humidity': 10, 'Motion': 9, 'Geolocalization': 10, 'Wind': 10, 'Energy': 14, 'UV': 13, 'Height': 12, 'Rate': 10, 'Voltage': 11, 'Dust_Level': 12, 'Speed': 11}
distanza_minima = 5
for classe, dist in res.iteritems():
    diff = (abs((distanza_minima - dist)) * 15) / 100
    if diff < percent_parola and (classe is not 'Radiation'):
        print classe