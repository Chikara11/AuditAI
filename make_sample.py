# make_sample.py
import os
import pandas as pd
from backend.app.core.anomaly_detector import InvoiceAnomalyDetector

# 1. Compute path to your big CSV
base_dir = os.path.dirname(__file__)                  # C:\AuditAI
csv_path = os.path.join(base_dir, "backend","app", "data", "invoices.csv")
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"Cannot find dataset at {csv_path}")

# 2. Load it, parsing the real date fields
df = pd.read_csv(csv_path, parse_dates=["issuedDate", "dueDate"])

# 3. Fit your anomaly detector on the full dataset
detector = InvoiceAnomalyDetector(data_path=csv_path)
detector.fit()

# 4. Identify anomalies in the full dataset
anoms = detector.detect_anomalies(df.copy())  # returns only anomaly rows with 'anomaly_type'

# 5. Split anomalies by type
iso_df = anoms[anoms['anomaly_type'] == 'IsolationForest']  # financial outliers
dup_df = anoms[anoms['anomaly_type'] == 'DBSCAN']           # duplicate‐style anomalies

# 6. Build a mixed sample of size N
N = 10
half = N // 2

# sample from each anomaly type
sample_iso = iso_df.sample(n=min(len(iso_df), half), random_state=42)
sample_dup = dup_df.sample(n=min(len(dup_df), half), random_state=42)

# fill the rest with normal invoices
selected_ids = pd.concat([sample_iso, sample_dup])['id_invoice']
normal_df = df[~df['id_invoice'].isin(selected_ids)]
remaining = N - len(sample_iso) - len(sample_dup)
sample_norm = normal_df.sample(n=min(len(normal_df), remaining), random_state=42)

# concatenate and shuffle to mix them up
sample = pd.concat([sample_iso, sample_dup, sample_norm]) \
           .sample(frac=1, random_state=42) \
           .reset_index(drop=True)

# 7. Write out as a new CSV
out_path = os.path.join(base_dir, "backend","app", "data", "sample_invoices.csv")
sample.to_csv(out_path, index=False)

print(
    f"✅ Wrote {len(sample)} sample invoices "
    f"({len(sample_iso)} outliers, {len(sample_dup)} duplicates, {len(sample_norm)} normal) "
    f"to {out_path}"
)
