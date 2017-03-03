import numpy as np  # from numpy package
import sklearn.cluster  # from sklearn package
import distance  # from distance package
import jaro
from database import metadati
from pyxdameraulevenshtein import damerau_levenshtein_distance
import sys

from bozza import words_per_stream     # TODO togliere
words = words_per_stream

words = np.asarray(words)  # So that indexing with a list will work

for stream in words:
    stream = np.asarray(stream)
    print stream
    # lev = np.array([[distance.nlevenshtein(w1, w2) for w1 in words] for w2 in words])  # levenshtein
    # dam = np.array([[damerau_levenshtein_distance(w1,w2) for w1 in words] for w2 in words]) #damerau-levenshtein TO NORMALIZE
    # ham = -1*np.array([[distance.hamming(w1,w2) for w1 in words] for w2 in words]) # hamming FIXME solo per stringhe della stessa lunghezza
    # jar = np.array(
    #     [[(1 - jaro.jaro_winkler_metric(unicode(w1), unicode(w2))) for w1 in words] for w2 in words])  # jaro-winkler
    # sor = np.array([[distance.sorensen(w1, w2) for w1 in words] for w2 in words])  # sorensen
    # jac = np.array([[distance.jaccard(w1, w2) for w1 in words] for w2 in words])  # jaccard
    jac = np.array([[distance.jaccard(w1, w2) for w1 in stream] for w2 in stream])  # jaccard

    # distance_matrix = lev
    distance_matrix = jac  # matrice con le distanze
    affinity_matrix = 1 - distance_matrix

    ## AFFINITY PROPAGATION CLUSTERING ##
    mymat = -1 * distance_matrix
    print mymat
    # Perform Affinity Propagation Clustering of data
    affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
    # Create affinity matrix from negative euclidean distances, then apply affinity propagation clustering.
    affprop.fit(mymat)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = stream[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(stream[np.nonzero(affprop.labels_ == cluster_id)])
        cluster_str = ", ".join(cluster)
        print(" - *%s:* %s" % ("cluster", cluster_str))  # (exemplar, cluster_str))
    print
