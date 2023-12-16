from fastapi import APIRouter, HTTPException, Depends, status, Path, Query

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500),
                       offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT Found contact')
    return contact


@router.post('/', response_model=ContactResponse, status_code=201)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.create_contact(body, db)
    return contact


@router.put('/{contact_id}')
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT Found contact')
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.delete_contact(contact_id, db)
    return contact


@router.get('/search/')
async def search(
        first_name: str = Query(None, description='Search by first_name'),
        second_name: str = Query(None, description='Search by second_name'),
        email: str = Query(None, description='Search by email'),
        db: AsyncSession = Depends(get_db)
):
    contacts = await repositories_contacts.search_contacts(first_name, second_name, email, db)
    return contacts


@router.get('/birthday/')
async def get_birthday(db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts_birthday(db)
    return {"contacts": contacts}