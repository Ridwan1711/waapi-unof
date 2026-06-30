import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.workspaces.models import Membership, Workspace

pytestmark = pytest.mark.django_db

PASSWORD = "Str0ngPass!23"


def test_register_creates_user_and_workspace() -> None:
    api = APIClient()
    response = api.post(
        "/v1/auth/register",
        {"email": "ann@example.com", "password": PASSWORD, "full_name": "Ann"},
        format="json",
    )
    assert response.status_code == 201

    user = User.objects.get(email="ann@example.com")
    assert Workspace.objects.filter(owner=user).count() == 1
    assert Membership.objects.filter(user=user, role=Membership.Role.OWNER).exists()


def test_login_and_me() -> None:
    api = APIClient()
    api.post("/v1/auth/register", {"email": "bob@example.com", "password": PASSWORD}, format="json")

    login = api.post(
        "/v1/auth/login",
        {"email": "bob@example.com", "password": PASSWORD},
        format="json",
    )
    assert login.status_code == 200
    assert "access" in login.data and "refresh" in login.data

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    me = api.get("/v1/auth/me")
    assert me.status_code == 200
    assert me.data["user"]["email"] == "bob@example.com"
    assert len(me.data["workspaces"]) == 1


def test_register_duplicate_email_rejected() -> None:
    api = APIClient()
    payload = {"email": "dup@example.com", "password": PASSWORD}
    assert api.post("/v1/auth/register", payload, format="json").status_code == 201
    assert api.post("/v1/auth/register", payload, format="json").status_code == 400


def test_me_requires_authentication() -> None:
    assert APIClient().get("/v1/auth/me").status_code == 401
