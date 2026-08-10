from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

class AuthService:
    @staticmethod
    def register(db: Session, name: str, email: str, password: str):
        existing = UserRepository.get_by_email(db, email)
        if existing is not None:
            return None

        user = UserRepository.create(
            db=db,
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        token = create_access_token(str(user.id))
        return {"access_token": token, "token_type": "bearer", "user": user}

    @staticmethod
    def login(db: Session, email: str, password: str):
        user = UserRepository.get_by_email(db, email)
        if user is None or not user.is_active or not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None

        token = create_access_token(str(user.id))
        return {"access_token": token, "token_type": "bearer", "user": user}

    @staticmethod
    def request_password_reset(db: Session, email: str) -> dict:
        result = {
            "message": (
                "If an account exists for that email, "
                "password reset instructions have been prepared."
            ),
            "dev_reset_url": None,
        }

        user = UserRepository.get_by_email(db, email)
        if user is None or not user.is_active:
            return result

        token = create_password_reset_token(user.id)
        reset_url = (
            f"{settings.frontend_url.rstrip('/')}"
            f"/reset-password?token={token}"
        )

        sent = EmailService.send_password_reset(
            recipient=user.email,
            reset_url=reset_url,
        )

        if not settings.is_production and not sent:
            result["dev_reset_url"] = reset_url

        return result

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        user_id = decode_password_reset_token(token)
        if user_id is None:
            return False

        user = UserRepository.get_by_id(db, user_id)
        if user is None or not user.is_active:
            return False

        UserRepository.update_password(
            db,
            user,
            hash_password(new_password),
        )
        return True

    @staticmethod
    def update_profile(db: Session, user, name: str, email: str):
        normalized = email.lower()
        existing = UserRepository.get_by_email(db, normalized)

        if existing is not None and existing.id != user.id:
            return None

        return UserRepository.update_profile(
            db,
            user,
            name,
            normalized,
        )

    @staticmethod
    def change_password(
        db: Session,
        user,
        current_password: str,
        new_password: str,
    ) -> bool:
        if not user.password_hash:
            return False

        if not verify_password(current_password, user.password_hash):
            return False

        UserRepository.update_password(
            db,
            user,
            hash_password(new_password),
        )
        return True
