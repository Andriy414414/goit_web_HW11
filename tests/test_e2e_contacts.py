from unittest.mock import Mock, patch
import pytest
from src.services.auth import auth_service


def test_get_contacts(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        response = client.get("api/contacts", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0


