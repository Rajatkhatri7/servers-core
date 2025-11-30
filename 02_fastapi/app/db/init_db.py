from app.db.config import Base,engine,SessionLocal
from app.models.users import User


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()