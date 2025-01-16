from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    sender_id: int
    recipient_id: int
    amount: int


class TransactionQueryParams(BaseModel):
    limit: int = Field(10, ge=1, le=100,
                       description="Количество записей на странице")
    offset: int = Field(0, ge=0, description="Количество записей для пропуска")
    start_date: Optional[date] = Field(
        None, description="Начало периода (YYYY-MM-DD)"
    )
    end_date: Optional[date] = Field(
        None, description="Конец периода (YYYY-MM-DD)"
    )
    status: Optional[str] = Field(
        None, description="Фильтр по статусу транзакции"
    )
