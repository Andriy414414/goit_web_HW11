import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    """
    Class for authentication

    :param pwd_context: CryptContext: CryptContext for password hashing
    :param SECRET_KEY: str: Secret key for JWT
    :param ALGORITHM: str: Algorithm for JWT
    :param cache: redis.Redis: Redis for caching
    :param oauth2_scheme: OAuth2PasswordBearer: OAuth2PasswordBearer for authentication
    :param verify_password: verify_password: Function for password verification
    :param get_password_hash: get_password_hash: Function for password hashing
    :param create_access_token: create_access_token: Function for creating access token
    :param create_refresh_token: create_refresh_token: Function for creating refresh token
    :param get_current_user: get_current_user: Function for getting current user
    :param get_current_active_user: get_current_active_user: Function for getting current active user
    :param get_user_by_email: get_user_by_email: Function for getting user by email
    :param get_user_by_token: get_user_by_token: Function for getting user by token
    :param get_user_by_refresh_token: get_user_by_refresh_token: Function for getting user by refresh token
    :param get_user_by_username: get_user_by_username: Function for getting user by username
    :param update_token: update_token: Function for updating token
    :param delete_token: delete_token: Function for deleting token
    :param delete_refresh_token: delete_refresh_token: Function for deleting refresh token
    :param delete_all_tokens: delete_all_tokens: Function for deleting all tokens
    :param delete_all_refresh_tokens: delete_all_refresh_tokens: Function for deleting all refresh tokens
    :param delete_user: delete_user: Function for deleting user
    :param delete_all_users: delete_all_users: Function for deleting all users
    :param send_email: send_email: Function for sending email
    :param create_superuser: create_superuser: Function for creating superuser
    :param create_user: create_user: Function for creating user
    :param get_current_superuser: get_current_superuser: Function for getting current superuser
    :param get_user_by_id: get_user_by_id: Function for getting user by id
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, db=0)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:

            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)
        user = self.cache.get(user_hash)

        if user is None:
            print('User BD')
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print('User hash')
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
