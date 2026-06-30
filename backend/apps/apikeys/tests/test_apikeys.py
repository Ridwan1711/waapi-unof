import pytest
from rest_framework.test import APIClient

from apps.accounts.services import register_user

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ngPass!23"


def _jwt_client() -> APIClient:
    register_user(email="dev@example.com", password=PASSWORD, full_name="Dev")
    api = APIClient()
    login = api.post(
        "/v1/auth/login",
        {"email": "dev@example.com", "password": PASSWORD},
        format="json",
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    return api


def test_create_use_and_revoke_api_key() -> None:
    api = _jwt_client()

    created = api.post("/v1/api-keys/", {"name": "CI key"}, format="json")
    assert created.status_code == 201
    raw_key = created.data["key"]
    assert "." in raw_key
    key_id = created.data["id"]

    # Use the raw key on an endpoint that accepts API-key auth.
    key_client = APIClient()
    key_client.credentials(HTTP_AUTHORIZATION=f"Api-Key {raw_key}")
    who = key_client.get("/v1/auth/whoami")
    assert who.status_code == 200
    assert who.data["auth_method"] == "api_key"
    assert who.data["workspace"] is not None

    # Revoke via the dashboard (JWT) client.
    assert api.post(f"/v1/api-keys/{key_id}/revoke", format="json").status_code == 200

    # The revoked key is now rejected.
    assert key_client.get("/v1/auth/whoami").status_code == 401


def test_list_keys_never_exposes_secret() -> None:
    api = _jwt_client()
    api.post("/v1/api-keys/", {"name": "k1"}, format="json")

    listing = api.get("/v1/api-keys/")
    assert listing.status_code == 200
    assert len(listing.data) == 1
    assert "key" not in listing.data[0]
    assert "hashed_key" not in listing.data[0]


def test_invalid_api_key_rejected() -> None:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Api-Key bogus.nonsense")
    assert client.get("/v1/auth/whoami").status_code == 401
