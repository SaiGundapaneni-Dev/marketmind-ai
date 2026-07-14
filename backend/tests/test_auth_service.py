from types import SimpleNamespace
from unittest.mock import patch

from app.services.auth_service import AuthService


def test_register_rejects_duplicate_email():
    with patch(
        "app.services.auth_service."
        "UserRepository.get_by_email"
    ) as mock_get:
        mock_get.return_value = SimpleNamespace(id=1)

        result = AuthService.register(
            db=None,
            name="Sai",
            email="sai@example.com",
            password="password123",
        )

        assert result is None


def test_register_returns_token():
    user = SimpleNamespace(
        id=7,
        name="Sai",
        email="sai@example.com",
        is_active=True,
    )

    with patch(
        "app.services.auth_service."
        "UserRepository.get_by_email",
        return_value=None,
    ), patch(
        "app.services.auth_service."
        "UserRepository.create",
        return_value=user,
    ), patch(
        "app.services.auth_service."
        "hash_password",
        return_value="hashed",
    ), patch(
        "app.services.auth_service."
        "create_access_token",
        return_value="token",
    ):
        result = AuthService.register(
            db=None,
            name="Sai",
            email="sai@example.com",
            password="password123",
        )

        assert result["access_token"] == "token"
        assert result["user"].id == 7


def test_login_rejects_wrong_password():
    user = SimpleNamespace(
        id=7,
        is_active=True,
        password_hash="hashed",
    )

    with patch(
        "app.services.auth_service."
        "UserRepository.get_by_email",
        return_value=user,
    ), patch(
        "app.services.auth_service."
        "verify_password",
        return_value=False,
    ):
        result = AuthService.login(
            db=None,
            email="sai@example.com",
            password="wrong",
        )

        assert result is None


def test_login_returns_token():
    user = SimpleNamespace(
        id=7,
        is_active=True,
        password_hash="hashed",
    )

    with patch(
        "app.services.auth_service."
        "UserRepository.get_by_email",
        return_value=user,
    ), patch(
        "app.services.auth_service."
        "verify_password",
        return_value=True,
    ), patch(
        "app.services.auth_service."
        "create_access_token",
        return_value="token",
    ):
        result = AuthService.login(
            db=None,
            email="sai@example.com",
            password="password123",
        )

        assert result["access_token"] == "token"
