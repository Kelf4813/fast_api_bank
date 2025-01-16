import logging

from app.models import User
from app.schemas import ChangePassword, UserCreate
from app.utils import hash_password, verify_password
from authx import AuthX, AuthXConfig
from databases import Database
from fastapi import HTTPException, Response

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)


class AuthController:
    def __init__(self, db: Database):
        self.db = db
        self.config = AuthXConfig()
        self.config.JWT_SECRET_KEY = "SECRET_KEY"
        self.config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
        self.config.JWT_TOKEN_LOCATION = ["cookies"]
        self.security = AuthX(config=self.config)

    def login(self, creds: UserCreate, response: Response):
        user = self.db.query(User).filter(
            User.username == creds.username).first()
        if verify_password(creds.password, user.hashed_password):
            token = self.security.create_access_token(uid=creds.username)
            response.set_cookie(self.config.JWT_ACCESS_COOKIE_NAME, token,
                                httponly=True)
            logger.info(f"User {User.username} login")
            return {"access_token": token}

        raise HTTPException(status_code=401, detail="Invalid credentials")

    def register(self, user_data: UserCreate):
        existing_user = self.db.query(User).filter(
            User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        existing_email = self.db.query(User).filter(
            User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        hashed_password = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        logger.info(f"User {User.username} register")
        return {"message": "User registered successfully"}

    def get_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "balance": user.balance,
        }

    def update_balance(self, user_id: int, amount: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.balance = amount
        self.db.commit()
        self.db.refresh(user)

        return {"id": user.id, "new_balance": user.balance}

    def change_password(self, user_id: int, data: ChangePassword):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(status_code=401,
                                detail="Invalid current password")

        user.hashed_password = hash_password(data.new_password)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User {User.username} change password")
        return {"message": "Password updated successfully"}
