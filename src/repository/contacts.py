from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.sql.operators import and_

from src.entity.models import Contact, User
from src.repository import users
from src.schemas import user
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, skip: int, db: AsyncSession, current_user: User, offset=None):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param skip: int: Skip the number of contacts returned
    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :param offset: int: Skip the number of contacts returned
    :return: a list of contacts
    """
    stmt = select(Contact).filter(Contact.user_id == current_user.id).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    The get_contact function returns a contact by id.

    :param contact_id: int: Get the contact by id
    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :return: A contact object
    """
    stmt = select(Contact).filter(Contact.user_id == current_user.id).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, current_user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :return: A contact object
    """
    contact = Contact(first_name=body.first_name, second_name=body.second_name, email=body.email,
                      birthday=body.birthday, add_info=body.add_info, user_id=current_user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, current_user: User):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Get the contact id
    :param body: ContactUpdateSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :return: A contact object
    """
    stmt = select(Contact).filter(Contact.user_id == current_user.id).filter_by(id=contact_id)
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


async def delete_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Get the contact id
    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :return: A contact object
    """
    stmt = select(Contact).filter(Contact.user_id == current_user.id).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(first_name: str, second_name: str, email: str, db: AsyncSession, current_user: User):
    """
    The search_contacts function searches for contacts in the database.

    :param first_name: str: Search for contacts by first name
    :param second_name: str: Search for contacts by second name
    :param email: str: Search for contacts by email
    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :return: A list of contacts
    """
    stmt = select(Contact).filter(Contact.user_id == current_user.id)

    if first_name:
        stmt = stmt.filter(Contact.first_name == first_name)
    if second_name:
        stmt = stmt.filter(Contact.second_name == second_name)
    if email:
        stmt = stmt.filter(Contact.email == email)

    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_birthday(db: AsyncSession, current_user: User):
    """
    The get_contacts_birthday function returns a list of contacts who have their birthday today.

    :param db: AsyncSession: Pass the database session
    :param current_user: User: Get the current user
    :return: A list of contacts
    """
    today = datetime.today()
    week_from_now = today + timedelta(days=7)

    stmt = select(Contact).filter(Contact.user_id == current_user.id).filter(
        func.date_part('month', Contact.birthday) == today.month,
        func.date_part('day', Contact.birthday) >= today.day,
        func.date_part('day', Contact.birthday) <= week_from_now.day,

    )

    contacts = await db.execute(stmt)
    return contacts.scalars().all()
