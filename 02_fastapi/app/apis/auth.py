from fastapi import APIRouter
from app.schema.auth import SignupRequest,LoginRequest
from sqlalchemy.orm import Session
import uuid
from app.models.users import User
from app.db.init_db import get_db
from fastapi import Depends,HTTPException,status
from passlib.hash import pbkdf2_sha256
from app.utilities.auth_utils import create_access_token,verify_user
from app.core.config import settings


router = APIRouter()

@router.post("/signup")
async def signup(request: SignupRequest,db: Session = Depends(get_db)):
    username = request.username.strip()
    email = request.email.strip()
    password = request.password.strip()

    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    elif db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    new_user = User(username=username, email=email, password=pbkdf2_sha256.hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "id": str(new_user.id), "email": new_user.email}

@router.post("/login")
async def login(request: LoginRequest,db: Session = Depends(get_db)):
    username = request.username.strip()
    password = request.password.strip()

    user = db.query(User).filter(User.email == username).first()
    if not user or not pbkdf2_sha256.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token = await create_access_token(data={"sub": user.email})
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer","expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES}

@router.get("/user/details")
async def get_user_details(user: User = Depends(verify_user)):
        return {"id": str(user.id), "email": user.email, "username": user.username}
