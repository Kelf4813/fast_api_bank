from app.controller import TransactionController
from app.database import get_db
from app.schemas import TransactionQueryParams, TransactionCreate
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/create_transaction")
def create_transaction(transaction_data: TransactionCreate,
                       db: Session = Depends(get_db)):
    transaction_controller = TransactionController(db)
    return transaction_controller.create_transaction(transaction_data)


@router.get("/transaction/{user_id}")
def get_user_transactions(
    user_id: int,
    query_params: TransactionQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    transaction_controller = TransactionController(db)
    return transaction_controller.get_user_transactions(
        user_id,
        query_params=query_params
    )
