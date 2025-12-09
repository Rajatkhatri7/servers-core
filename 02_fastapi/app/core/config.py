import os
from dotenv import load_dotenv

load_dotenv()



class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    REDIS_HOST: str = os.getenv("REDIS_HOST","localhost")
    REDIS_DB: int = int(os.getenv("REDIS_DB"))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT",6379))
    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


settings = Settings()
