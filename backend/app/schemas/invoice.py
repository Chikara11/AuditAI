from pydantic import BaseModel
from typing import Optional
from datetime import date

class Invoice(BaseModel):
    id_invoice: str
    issuedDate: date
    country: str
    service: str
    total: float
    discount: float
    tax: float
    invoiceStatus: str
    balance: float
    dueDate: date
    client: Optional[str]

class InvoiceAnomaly(Invoice):
    anomaly_type: Optional[str]
