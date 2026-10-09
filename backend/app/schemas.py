from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["PENDING", "APPROVED", "PAID"]
Category = Literal["FOOD", "TRAVEL", "BILLS", "OTHER"]

class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    notes: str = ""
    amount: float = Field(default=0.0, ge=0)
    category: Category = "OTHER"
    status: Status = "PENDING"
    paid_by: str = "Self"

class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None
    amount: float | None = Field(default=None, ge=0)
    category: Category | None = None
    status: Status | None = None
    paid_by: str | None = None

class ExpenseOut(ExpenseCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StatsOut(BaseModel):
    total: int
    pending: int
    approved: int
    paid: int
    total_spend: float
