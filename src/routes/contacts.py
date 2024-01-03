from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500),
                       offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Get list of contacts with pagination and filtering by limit and offset parameters
    :param limit: int: Limit of contacts
    :param offset: int: Offset of contacts
    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: list[ContactResponse]: List of contacts
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, current_user)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Get contact by id

    :param contact_id: int: Id of contact
    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: ContactResponse: Contact
    """
    contact = await repositories_contacts.get_contact(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT Found contact')
    return contact


@router.post('/', response_model=ContactResponse, status_code=201)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Create new contact in database

    :param body: ContactSchema: Body with contact data
    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: ContactResponse: Created contact
    """
    contact = await repositories_contacts.create_contact(body, db, current_user)
    return contact


@router.put('/{contact_id}')
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Update contact by id

    :param body: ContactUpdateSchema: Body with contact data
    :param contact_id: int: Id of contact
    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: ContactResponse: Updated contact
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT Found contact')
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Delete contact by id

    :param contact_id: int: Id of contact
    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: None
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, current_user)
    return contact


@router.get('/search/')
async def search(
        first_name: str = Query(None, description='Search by first_name'),
        second_name: str = Query(None, description='Search by second_name'),
        email: str = Query(None, description='Search by email'),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    Search contacts by first_name, second_name and email

    :param first_name: str: Search by first_name
    :param second_name: str: Search by second_name
    :param email: str: Search by email
    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: list[ContactResponse]: List of contacts
    """
    contacts = await repositories_contacts.search_contacts(first_name, second_name, email, db, current_user)
    if contacts is [None]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT Found contact')
    return contacts


@router.get('/birthday/')
async def get_birthday(db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Get contacts with birthday in current month

    :param db: AsyncSession: AsyncSession for database connection
    :param current_user: User: Current user
    :return: list[ContactResponse]: List of contacts
    """
    contacts = await repositories_contacts.get_contacts_birthday(db, current_user)
    return {"contacts": contacts}
