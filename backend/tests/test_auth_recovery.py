from types import SimpleNamespace
from unittest.mock import patch

from app.services.auth_service import AuthService

@patch("app.services.auth_service.EmailService.send_password_reset", return_value=False)
@patch("app.services.auth_service.create_password_reset_token", return_value="reset-token")
@patch("app.services.auth_service.UserRepository.get_by_email")
def test_password_reset_request_for_existing_user(mock_get, mock_token, mock_email):
    mock_get.return_value = SimpleNamespace(
        id=9,
        email="test@example.com",
        is_active=True,
    )

    result = AuthService.request_password_reset(
        db=object(),
        email="test@example.com",
    )

    assert "message" in result
    mock_token.assert_called_once_with(9)

@patch("app.services.auth_service.UserRepository.update_password")
@patch("app.services.auth_service.UserRepository.get_by_id")
@patch("app.services.auth_service.decode_password_reset_token", return_value=9)
def test_reset_password(mock_decode, mock_get, mock_update):
    mock_get.return_value = SimpleNamespace(id=9, is_active=True)

    result = AuthService.reset_password(
        db=object(),
        token="valid",
        new_password="newpassword123",
    )

    assert result is True
    mock_update.assert_called_once()

@patch("app.services.auth_service.decode_password_reset_token", return_value=None)
def test_reset_password_rejects_invalid_token(mock_decode):
    result = AuthService.reset_password(
        db=object(),
        token="invalid",
        new_password="newpassword123",
    )
    assert result is False
