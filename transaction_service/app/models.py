from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.now())
    sender_id = Column(Integer, nullable=False)
    recipient_id = Column(Integer, nullable=False)
