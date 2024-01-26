import pandas as pd
import numpy as np

from sklearn.cluster import KMeans

def cluster(df, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(df)
    return kmeans.labels_

def add_clusters(df, n_clusters):
    df['cluster'] = cluster(df, n_clusters)
    return df