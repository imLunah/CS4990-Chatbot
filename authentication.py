import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

from db import ChatDB
from models import UserInDB


class Auth:
    def __init__(
        self,
        secret_key: str = os.environ["JWT_SECRET"],
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
    ):
        self.SECRET_KEY = secret_key
        self.ALGORITHM = algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
    
    def get_user(self, db: ChatDB, user_id: str):
        try:
            hashed_password = db.get_user_hashed_password(user_id)
            return UserInDB(user_id=user_id, hashed_password=hashed_password)
        except Exception:
            return None
        
    def authenticate_user(self, db: ChatDB, user_id: str, password: str):
        user = self.get_user(db, user_id)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    