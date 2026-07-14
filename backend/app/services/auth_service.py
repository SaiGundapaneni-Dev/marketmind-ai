from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository


class AuthService:

    @staticmethod
    def register(
        db: Session,
        name: str,
        email: str,
        password: str,
    ):
        existing = UserRepository.get_by_email(
            db,
            email,
        )

        if existing is not None:
            return None

        user = UserRepository.create(
            db=db,
            name=name,
            email=email,
            password_hash=hash_password(password),
        )

        token = create_access_token(str(user.id))

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):
        user = UserRepository.get_by_email(
            db,
            email,
        )

        if user is None:
            return None

        if not user.is_active:
            return None

        if not user.password_hash:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        token = create_access_token(str(user.id))

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }
