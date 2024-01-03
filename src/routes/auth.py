from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import *
from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Create new user in database and send confirmation email to user

    :param body: UserSchema: Body with user data
    :param bt: BackgroundTasks: BackgroundTasks for sending email
    :param request: Request: Request with base url
    :param db: AsyncSession: AsyncSession for database connection
    :return: User: Created user in database with token and refresh token
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ACCOUNT_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Login user and return access and refresh token for user

    :param body: OAuth2PasswordRequestForm: Body with username and password
    :param db: AsyncSession: AsyncSession for database connection
    :return: TokenSchema: Access and refresh token
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_PASSWORD)
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "test"})
    refresh_token2 = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token2, db)
    return {"access_token": access_token, "refresh_token": refresh_token2, "token_type": "bearer"}


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Refresh token for user and return access and refresh token for user

    :param credentials: HTTPAuthorizationCredentials: Credentials with refresh token
    :param db: AsyncSession: AsyncSession for database connection
    :return: TokenSchema: Access and refresh token
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token3 = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token3, db)
    return {"access_token": access_token, "refresh_token": refresh_token3, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm email for user and return message with email confirmed

    :param token: str: Token with email
    :param db: AsyncSession: AsyncSession for database connection
    :return: str: Message with email confirmed
    """

    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Request email for user and send confirmation email to user

    :param body: RequestEmail: Body with email
    :param background_tasks: BackgroundTasks: BackgroundTasks for sending email
    :param request: Request: Request with base url
    :param db: AsyncSession: AsyncSession for database connection
    :return: str: Message with email sent
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}