import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import numpy as np

class InvoiceAnomalyDetector:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.data = pd.read_csv(self.data_path)
        self.model_isolation = IsolationForest(contamination=0.01, random_state=42)
        self.model_dbscan = DBSCAN(eps=0.5, min_samples=3)

    def preprocess(self, df):
        df_processed = df[['total', 'discount', 'tax', 'balance']]
        df_processed = df_processed.fillna(0)
        return df_processed

    def fit(self):
        X = self.preprocess(self.data)
        self.model_isolation.fit(X)

    def detect_anomalies(self, new_data: pd.DataFrame):
        X_new = self.preprocess(new_data)

        # Isolation Forest
        iso_preds = self.model_isolation.predict(X_new)
        new_data['isolation_anomaly'] = iso_preds == -1

        # DBSCAN
        dbscan_preds = self.model_dbscan.fit_predict(X_new)
        new_data['dbscan_anomaly'] = dbscan_preds == -1

        anomalies = new_data[
            (new_data['isolation_anomaly']) | (new_data['dbscan_anomaly'])
        ].copy()

        anomalies['anomaly_type'] = anomalies.apply(
            lambda row: 'IsolationForest' if row['isolation_anomaly'] else 'DBSCAN',
            axis=1
        )

        return anomalies.drop(columns=['isolation_anomaly', 'dbscan_anomaly'])
