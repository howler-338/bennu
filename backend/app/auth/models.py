import enum

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import BaseModel


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
