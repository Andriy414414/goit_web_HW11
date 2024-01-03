import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.entity.models import Contact, User
from src.repository.contacts import get_contacts, get_contact, create_contact, update_contact, delete_contact, \
    search_contacts, get_contacts_birthday


class TestAsyncContactRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(
            id=1, username="test", password="test", email="test", confirmed=True
        )
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name="test", second_name="test", email="test", birthday="test"),
            Contact(id=2, first_name="test", second_name="test", email="test", birthday="test")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)  # assert that result is equal to contacts

    async def test_get_contact(self):
        contact_id = 1
        contact = [
            Contact(id=1, first_name="test", second_name="test", email="test", birthday="test"),
        ]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)  # assert that result is equal to contact

    async def test_create_contact(self):
        body = ContactSchema(first_name="test", second_name="test", email="test",
                             birthday=date(2000, 1, 1),
                             add_info="test", user_id=1)

        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.second_name, body.second_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.add_info, body.add_info)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact(self):
        contact_id = 1
        body = ContactUpdateSchema(first_name="test", second_name="test", email="test",
                                   birthday=date(2000, 1, 1),
                                   add_info="test", user_id=1, completed=True)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name="test", second_name="test",
                                                                 email="test", birthday=date(2000, 1, 1),
                                                                 add_info="test", user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(contact_id, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.second_name, body.second_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.add_info, body.add_info)
        self.assertEqual(result.birthday, body.birthday)

    async def test_delete_contact(self):
        contact_id = 1
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name="test", second_name="test",
                                                                 email="test", birthday=date(2000, 1, 1),
                                                                 add_info="test", user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id, self.session, self.user)
        self.assertIsInstance(result, Contact)

    async def test_search_contact(self):
        search_text = "test"

        contact1 = Contact(id=1, first_name="test", second_name="test", email="test", birthday="test")
        contact2 = Contact(id=2, first_name="testaaa", second_name="test", email="test", birthday="test")

        matchting_contacts = [contact1]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = matchting_contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts(search_text, search_text, search_text, self.session, self.user)
        self.assertEqual(result, matchting_contacts)

    async def test_get_contacts_birthday(self):

        today = date.today()
        yesterday = today - timedelta(days=1)
        next_day_1 = today + timedelta(days=2)
        next_day_2 = today + timedelta(days=3)

        contact1 = Contact(id=1, first_name="test", second_name="test", birthday=yesterday.isoformat())
        contact2 = Contact(id=2, first_name="test2", second_name="test2", birthday=next_day_1.isoformat())
        contact3 = Contact(id=3, first_name="test3", second_name="test3", birthday=next_day_2.isoformat()),

        matchting_contacts = [contact2, contact3]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = matchting_contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts_birthday(self.session, self.user)
        self.assertEqual(result, matchting_contacts)
