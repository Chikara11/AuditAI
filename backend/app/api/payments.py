# File: backend/app/api/payments.py
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.payment_behavior_analyzer import PaymentBehaviorAnalyzer

router = APIRouter(prefix='/api/payments')
analyzer = PaymentBehaviorAnalyzer(history_path='app/data/payments_history.csv')

class PaymentRequest(BaseModel):
    employee_id: str
    amount: float
    timestamp: str
    vendor: str = None
    method: str = None
    category: str = None
    accept_card: bool
    session_timeout_secs: int
    success_link: str
    fail_link: str
    developer_tracking_id: str
    enforce_detection: bool = True  # new flag

@router.post('/pay')
async def pay(req: PaymentRequest):
    # 1) Optionally perform anomaly check
    if req.enforce_detection:
        anomaly = analyzer.detect_unusual(req.dict())
        if anomaly:
            raise HTTPException(status_code=403, detail=anomaly)

    # 2) Build Flouci payload
    fl_payload = {
        "app_token": "7c03ae2b-cbf8-44b2-8702-901b5c246162",
        "app_secret": "91c49207-5263-44dd-bfb8-5df9ef96ef97",
        "amount": str(int(req.amount)),                             # string
        "accept_card": str(req.accept_card).lower(),                # "true"/"false"
        "session_timeout_secs": req.session_timeout_secs,
        "success_link": req.success_link,
        "fail_link": req.fail_link,
        "developer_tracking_id": req.developer_tracking_id
    }

    # 3) Call Flouci
    async with httpx.AsyncClient() as client:
        fl_resp = await client.post(
            "https://developers.flouci.com/api/generate_payment",
            json=fl_payload,
            timeout=10.0
        )

    if fl_resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Flouci error: {fl_resp.status_code} {fl_resp.text}")

    # 4) Parse Flouci response
    data = fl_resp.json()
    result = data.get('result', {}) if isinstance(data, dict) else {}
    payment_url = (
        result.get("link")
        or result.get("payment_url")
        or result.get("checkout_url")
        or result.get("redirect_url")
        or result.get("url")
        or data.get("payment_url")
        or data.get("checkout_url")
        or data.get("redirect_url")
    )
    if not payment_url:
        keys = list(result.keys()) if result else list(data.keys())
        raise HTTPException(
            status_code=502,
            detail=f"Malformed Flouci response, result keys: {keys}"
        )

    # 5) Return URL for frontend to redirect
    return JSONResponse({"payment_url": payment_url})
