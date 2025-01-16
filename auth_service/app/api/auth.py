from app.controller import AuthController
from app.database import get_db
from app.schemas import ChangePassword, UserCreate
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login")
def login(creds: UserCreate, response: Response,
          db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    return auth_controller.login(creds, response)


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    auth_controller = AuthController(db)
    return auth_controller.register(user)


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user_service = AuthController(db)
    return user_service.get_user(user_id)


@router.patch("/users/{user_id}/balance")
def update_balance(
        user_id: int, amount: int, db: Session = Depends(get_db)
):
    auth_controller = AuthController(db)
    return auth_controller.update_balance(user_id, amount)


@router.patch("/users/{user_id}/password")
def change_password(
        user_id: int,
        data: ChangePassword,
        db: Session = Depends(get_db),
):
    auth_controller = AuthController(db)
    return auth_controller.change_password(user_id, data)
