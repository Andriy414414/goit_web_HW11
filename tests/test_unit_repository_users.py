import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import UserSchema, UserResponse, TokenSchema, RequestEmail
from src.entity.models import User
from src.repository.users import create_user, get_user_by_email, update_token, confirmed_email, update_avatar_url


class TestAsyncUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):

        self.session = AsyncMock(spec=AsyncSession)

    async def test_create_user(self):
        body = UserSchema(username="test", email="test", password="testtest")
        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_get_user_by_email(self):
        user = User(
            id=1, username="test2", password="testtest", email="test2", confirmed=True, avatar="test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(user.email, self.session)
        self.assertEqual(result.email, "test2")

    async def test_update_token(self):
        user = User(
            id=1, username="test2", password="testtest", email="test2", confirmed=True, avatar="test"
        )
        user.refresh_token = "token_test"

        await update_token(user, "token_test", self.session)
        self.assertEqual(user.refresh_token, "token_test")

    async def test_confirmed_email(self):
        user = User(
            id=1, username="test2", password="testtest", email="test2", confirmed=True, avatar="test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        user.confirmed = False
        await confirmed_email(user.email, self.session)

        self.assertEqual(user.confirmed, True)

    async def test_update_avatar_url(self):
        user = User(
            id=1, username="test2", password="testtest", email="test2", confirmed=True, avatar="avatar_test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await update_avatar_url(user.avatar, "avatar_test", self.session)
        self.assertEqual(user.avatar, "avatar_test")
