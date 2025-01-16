import logging

import httpx
from app.models import Transactions
from app.schemas import TransactionCreate, TransactionQueryParams
from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


class TransactionController:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service_url = "http://auth_service:8000"

    def check_user_exists(self, user_id: int):
        response = httpx.get(f"{self.auth_service_url}/users/{user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=400,
                                detail=f"User with ID {user_id} does not exist")
        return response.json()

    def check_user_balance(self, user_id: int):
        user_data = self.check_user_exists(user_id)
        return user_data['balance']

    def create_transaction(self, transaction_data: TransactionCreate):
        if transaction_data.amount <= 0:
            raise HTTPException(status_code=400,
                                detail="Amount must be greater than 0")

        transaction = Transactions(
            amount=transaction_data.amount,
            sender_id=transaction_data.sender_id,
            recipient_id=transaction_data.recipient_id,
            status=False
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        try:
            self.update_user_balance(transaction_data.sender_id,
                                     -transaction_data.amount)
            self.update_user_balance(transaction_data.recipient_id,
                                     transaction_data.amount)
            transaction.status = True
        except HTTPException as e:
            self.db.rollback()
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        self.db.commit()
        logger.info(f"User{transaction_data.sender_id} sent "
                    f"{transaction_data.amount} to "
                    f"user{transaction_data.recipient_id}")

        return {"transaction_id": transaction.id, "status": transaction.status}

    def update_user_balance(self, user_id: int, amount: int):
        user_data = self.check_user_exists(user_id)

        user_balance = user_data['balance']
        user_balance += amount

        response = httpx.patch(
            f"{self.auth_service_url}/users/{user_id}/balance?amount={user_balance}",
            json={"amount": user_balance}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400,
                                detail="Failed to update user balance")

    def get_user_transactions(self, user_id: int,
                              query_params: TransactionQueryParams):
        query = self.db.query(Transactions).filter(
            (Transactions.sender_id == user_id) | (
                    Transactions.recipient_id == user_id)
        )

        if query_params.start_date:
            query = query.filter(
                Transactions.timestamp >= query_params.start_date)
        if query_params.end_date:
            query = query.filter(
                Transactions.timestamp <= query_params.end_date)
        if query_params.status:
            query = query.filter(Transactions.status == query_params.status)

        user_transactions = query.offset(query_params.offset).limit(
            query_params.limit).all()

        transactions = [
            {
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "status": transaction.status,
                "timestamp": transaction.timestamp,
                "sender_id": transaction.sender_id,
                "recipient_id": transaction.recipient_id
            }
            for transaction in user_transactions
        ]

        return transactions
