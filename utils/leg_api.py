import pandas as pd
import numpy as np
import requests
from datetime import datetime
import re
from matplotlib import pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fcluster

from config import cc_api_key

import folium

TODAY = datetime.today()
SESS_BEGIN = TODAY.replace(year=TODAY.year - ((TODAY.year % 4) - 2), month=1, day=1).strftime("%Y-%m-%d") if (TODAY.year % 4) >= 2 else TODAY.replace(year=TODAY.year - ((TODAY.year % 4) + 2), month=1, day=1).strftime("%Y-%m-%d")
SESS_END = "{}-{}-{}".format(int(SESS_BEGIN.split("-")[0]) + 3, 12, 31)

def process_cm_info(df):
    CM_RAW = df.json()

    for CM in CM_RAW:
        PERSON_DATA = requests.get(url="https://webapi.legistar.com/v1/nyc/Persons/{}/?&token={}".format(CM["OfficeRecordPersonId"], cc_api_key))
        CM_PERSONAL_DATA = PERSON_DATA.json()


        if CM_PERSONAL_DATA['PersonWWW']:
            district_numbers = re.findall('[0-9]+', CM_PERSONAL_DATA['PersonWWW'])
            if district_numbers:
                CM["District"] = int(district_numbers[0])
            else:
                if CM_PERSONAL_DATA['PersonEmail']:
                    district_numbers = re.findall('[0-9]+', CM_PERSONAL_DATA['PersonEmail'])
                    CM["District"] = int(district_numbers[0]) if district_numbers else np.nan
                else:
                    CM["District"] = np.nan
        else:
            CM["District"] = np.nan

        CM['Address'] = CM_PERSONAL_DATA['PersonAddress1']
        CM["City"] = CM_PERSONAL_DATA['PersonCity1']
        CM['Zip'] = CM_PERSONAL_DATA['PersonZip1']

    CM_DATA = sorted(CM_RAW, key=lambda i: i['District'] if not np.isnan(i['District']) else float('inf'))

    return pd.DataFrame(CM_DATA)

def generate_cc_df():
    CM_RAW = requests.get(url="https://webapi.legistar.com/v1/nyc/Bodies/1/OfficeRecords/?$filter=OfficeRecordStartDate+eq+datetime'{}'&token={}".format(SESS_BEGIN, cc_api_key))

    CM_DATA = process_cm_info(CM_RAW)

    CM_DATA.loc[CM_DATA['OfficeRecordFullName'] == 'Joseph C. Borelli', 'District'] = 51
    CM_DATA.loc[CM_DATA['OfficeRecordFullName'] == 'Justin L. Brannan', 'District'] = 43
    CM_DATA = CM_DATA[CM_DATA['OfficeRecordFullName'] != 'Public Advocate Jumaane Williams']
    CM_DATA['District'] = CM_DATA['District'].astype('Int64')

    return CM_DATA

def get_votes():
    all_votes = []

    CM_RAW = requests.get(url="https://webapi.legistar.com/v1/nyc/Bodies/1/OfficeRecords/?$filter=OfficeRecordStartDate+eq+datetime'{}'&token={}".format(SESS_BEGIN, cc_api_key))
    CM_RAW = CM_RAW.json()
    for CM in CM_RAW:
        PERSON_DATA = requests.get(url="https://webapi.legistar.com/v1/nyc/Persons/{}/?&token={}".format(CM["OfficeRecordPersonId"], cc_api_key))
        CM_PERSONAL_DATA = PERSON_DATA.json()
    
        VOTES = requests.get(url="https://webapi.legistar.com/v1/nyc/Persons/{}/votes/?$filter=VoteLastModifiedUtc+gt+datetime'{}'&token={}".format(CM_PERSONAL_DATA["PersonId"], SESS_BEGIN, cc_api_key))
        VOTES_JSON = VOTES.json()
    
        all_votes.extend(VOTES_JSON)

    VOTER = pd.DataFrame(all_votes)
    return VOTER

def find_close_votes():
    df = get_votes()
    vote_counts = df.groupby(['VoteEventItemId', 'VoteValueName']).size()
    pivot_table = vote_counts.unstack(fill_value=0)
    pivot_table = pivot_table.reset_index()

    pivot_table['anti'] = pivot_table['Negative'] + pivot_table['Abstain']
    pivot_table['total'] = pivot_table['Affirmative'] + pivot_table['anti']
    pivot_table['ratio'] = pivot_table['anti'] / pivot_table['Affirmative']

    pivot_table = pivot_table[pivot_table['ratio'].notna()]
    pivot_table.replace([np.inf, -np.inf], np.nan, inplace=True)

    full = pivot_table[pivot_table['total'] > 45]
    top_ratio = full.sort_values('ratio', ascending=False).head(100)

    ratio_ids = top_ratio['VoteEventItemId'].tolist()
    full_ratio = df[df['VoteEventItemId'].isin(ratio_ids)]

    fr_pivot = full_ratio.pivot_table(index='VotePersonName', columns='VoteEventItemId', values='VoteValueId')
    fr_pivot.dropna(axis=1, how='any', inplace=True)

    return fr_pivot
    
def scale_and_standardize(df):
    one_hot = pd.get_dummies(df, columns=df.columns)
    scaler = StandardScaler()
    scaled_df = scaler.fit_transform(one_hot)
    return scaled_df

def kmeans_cluster(df,n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(df)
    df['cluster'] = kmeans.labels_
    return kmeans

def hierarchical_cluster(df):
    Z = linkage(df, 'ward')
    return Z

def plot_denogram(Z,df):
    plt.figure(figsize=(25, 10))
    dendrogram(Z, labels=df.index, leaf_rotation=90)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(Z, leaf_rotation=90., leaf_font_size=8.)
    plt.show()

def cluster(Z,df,threshold):
    df = df.copy()
    distance_threshold = threshold
    clusters = fcluster(Z, distance_threshold, criterion='distance')
    df['h_cluster'] = clusters
    return df

def merge_with_cluster(cm_df,cluster_df):
    master = pd.merge(cm_df, cluster_df, left_on='OfficeRecordFullName', right_on='VotePersonName', how='left')
    return master

def run_kmeans_on_click(df, n_clusters):
    close_votes = find_close_votes(df)
    scaled_df = scale_and_standardize(close_votes)
    kmeans = kmeans_cluster(scaled_df,n_clusters)
    return kmeans

def start_hierarchical(close_votes):
    scaled_df = scale_and_standardize(close_votes)
    Z = hierarchical_cluster(scaled_df)
    return Z

def make_base_map(df,CM_DATA,gdf):
    gdfe = gdf.to_crs(epsg=4326)
    df = df.reset_index()
    master = pd.merge(CM_DATA, df, left_on='OfficeRecordFullName', right_on='VotePersonName', how='left')
    master = master[['OfficeRecordFullName', 'District', 'h_cluster']].copy() 
    master_map = pd.merge(gdfe, master, left_on='CounDist', right_on='District', how='left')

    return master_map

def generate_colorscale(num_clusters, geojson_data):
    cmap = plt.get_cmap('tab20')
    colorscale = [
        "rgba({},{},{},{})".format(int(r * 255), int(g * 255), int(b * 255), a)
        for r, g, b, a in (cmap(i / num_clusters) for i in range(num_clusters))
    ]
    return colorscale
