# backend/app/schemas.py
from pydantic import BaseModel

class TradeApproval(BaseModel):
    instrument: str
    quantity: float
    entry_price: float
