# Lifecycle stage 3 — Data Understanding
 
import pandas as pd
 
def load_data(path):
    df = pd.read_csv(path, encoding="cp1252")

    if {"v1", "v2"}.issubset(df.columns):
        df = df.rename(columns={"v1": "label", "v2": "text"})
        df = df.loc[:, ["label", "text"]]

    return df
