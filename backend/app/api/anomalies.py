from fastapi import APIRouter, UploadFile, File
from typing import List
import pandas as pd
from app.schemas.invoice import InvoiceAnomaly
from app.core.anomaly_detector import InvoiceAnomalyDetector
import tempfile

router = APIRouter(prefix="/api/anomalies")

detector = InvoiceAnomalyDetector(data_path='app/data/invoices.csv')
detector.fit()

@router.post("/detect", response_model=List[InvoiceAnomaly])
async def detect_anomalies(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    user_df = pd.read_csv(tmp_path)
    anomalies_df = detector.detect_anomalies(user_df)

    anomalies_df['id_invoice'] = anomalies_df['id_invoice'].astype(str)


    return anomalies_df.to_dict(orient='records')
    