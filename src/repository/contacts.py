from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.sql.operators import and_

from src.entity.models import Contact, User
from src.repository import users
from src.schemas import user
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, skip: int, db: AsyncSession, offset=None):
    stmt = select(Contact).filter(Contact.user_id == User.id).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter(Contact.user_id == User.id).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):

    contact = Contact(**body.model_dump(exclude_unset=True), user_id=User.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    stmt = select(Contact).filter(Contact.user_id == User.id).filter_by(id=contact_id)
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
    stmt = select(Contact).filter(Contact.user_id == User.id).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(first_name: str, second_name: str, email: str, db: AsyncSession):
    stmt = select(Contact).filter(Contact.user_id == User.id)

    if first_name:
        stmt = stmt.filter(Contact.first_name == first_name)
    if second_name:
        stmt = stmt.filter(Contact.second_name == second_name)
    if email:
        stmt = stmt.filter(Contact.email == email)

    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_birthday(db: AsyncSession):
    today = datetime.today()
    week_from_now = today + timedelta(days=7)

    stmt = select(Contact).filter(Contact.user_id == User.id).filter(
        func.date_part('month', Contact.birthday) == today.month,
        func.date_part('day', Contact.birthday) >= today.day,
        func.date_part('day', Contact.birthday) <= week_from_now.day,

    )

    contacts = await db.execute(stmt)
    return [{"name": contact.first_name, "birthday": contact.birthday} for contact in contacts.scalars().all()]
