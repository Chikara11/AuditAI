from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.anomalies import router as invoice_router
from app.api.payments import router as payment_router

app = FastAPI()

# Allow your React front-end to talk to all these endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoice_router)
app.include_router(payment_router)
