from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    type: str
    amount: float
    category: str
    note: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_must_be_valid(cls, v):
        if v not in ("sale", "expense"):
            raise ValueError("type must be 'sale' or 'expense'")
        return v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    category: str
    note: Optional[str]
    date: str

class SummaryResponse(BaseModel):
    period: str
    total_sales: float
    total_expenses: float
    profit: float
    transaction_count: int

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    action_taken: Optional[str] = None
    data: Optional[dict] = None
