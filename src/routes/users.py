import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.services.auth import auth_service
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix='/users', tags=['users'])
cloudinary.config(cloud_name=config.CLD_NAME, api_key=config.CLD_API_KEY,
                  api_secret=config.CLD_API_SECRET, secure=True)


@router.get('/me', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    Get current user by token

    :param user: user: Current user
    :return: UserResponse: Current user
    """
    return user


@router.patch('/avatar', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=30))])
async def get_current_user(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    """
    Update user avatar url

    :param file: UploadFile: File with avatar
    :param user: user: Current user
    :param db: AsyncSession: AsyncSession for database connection
    :return: UserResponse: Updated user
    """
    public_id = f'Web16/{user.email}'
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerited=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop='fill', version=res.get('version'))
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    return user
