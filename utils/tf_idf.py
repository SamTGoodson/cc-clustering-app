import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

tfidf = TfidfVectorizer()

def run_tfidf(df):
    grouped_df = df.groupby('prime_sponsor')['joined_text'].apply(' '.join).reset_index()
    tfidf_matrix = tfidf.fit_transform(grouped_df['joined_text'])
    feature_names = tfidf.get_feature_names_out()
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names, index=grouped_df['prime_sponsor'])
    return tfidf_df

def top_terms_for_member(member, df, n=5):
    tfidf_df = run_tfidf(df)
    if member in tfidf_df.index:
        member_tfidf = tfidf_df.loc[member]
        top_terms = member_tfidf.nlargest(n)
        # Join the top terms into a string, handling NaN and converting to string
        top_terms_str = ', '.join(top_terms.index.astype(str))
        return f"Top {n} terms for {member}: {top_terms_str}"
    else:
        return f"No data for individual: {member}"

