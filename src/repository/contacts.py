from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, skip: int, db: AsyncSession, offset=None):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.second_name = body.second_name
        contact.email = body.email
        contact.birthday = body.birthday
        contact.add_info = body.add_info
        await db.commit()
        await db.refresh(contact)

    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
