from sqlalchemy import Column,Integer,String,Boolean,Index
from sqlalchemy.dialects.postgresql import UUID
from app.db.init_db import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    __table_args__ = (
       Index("idx_users_email", email),
       Index("idx_users_username", username),
    )
