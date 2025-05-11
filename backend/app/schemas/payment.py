from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union

class Payment(BaseModel):
    payment_id: str
    employee_id: str
    timestamp: datetime
    amount: float
    vendor: str
    method: str
    category: str
    status: str

class PaymentBehaviorAnomaly(Payment):
    anomaly_score: float
    anomaly_type: str  # e.g. "AmountOutlier", "FrequencySpike", etc.
