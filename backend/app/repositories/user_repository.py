from sqlalchemy.orm import Session
from app.models.models import User

class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def create(db: Session, name: str, email: str, password_hash: str):
        user = User(
            name=name.strip(),
            email=email.lower(),
            password_hash=password_hash,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_password(db: Session, user: User, password_hash: str):
        user.password_hash = password_hash
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_profile(db: Session, user: User, name: str, email: str):
        user.name = name.strip()
        user.email = email.lower()
        db.commit()
        db.refresh(user)
        return user
