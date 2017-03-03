import numpy as np  # from numpy package
import sklearn.cluster  # from sklearn package
import distance  # from distance package
import jaro
from pyxdameraulevenshtein import damerau_levenshtein_distance
import sys

from bozza import words     # TODO togliere
#words = []

# words = np.asarray(words)  # So that indexing with a list will work
words = np.asarray(words)  # So that indexing with a list will work

dam = np.array([[(damerau_levenshtein_distance(w1,w2)) for w1 in words] for w2 in words]) #damerau-levenshtein 

distance_matrix = dam  # matrice con le distanze
affinity_matrix = 1 - distance_matrix

## AFFINITY PROPAGATION CLUSTERING ##
mymat = -1 * distance_matrix
print mymat
# Perform Affinity Propagation Clustering of data
affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
# Create affinity matrix from negative euclidean distances, then apply affinity propagation clustering.
affprop.fit(mymat)
for cluster_id in np.unique(affprop.labels_):
    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
    cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
    cluster_str = ", ".join(cluster)
    #print(" - *%s:* %s" % (exemplar, cluster_str))  # (exemplar, cluster_str))
    print exemplar + "-----------"
    for w in cluster:
		print "\t " + w + " " + str(damerau_levenshtein_distance(exemplar,w))

print len(np.unique(affprop.labels_))
