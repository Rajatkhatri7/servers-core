from fastapi import APIRouter,Request
from app.schema.auth import SignupRequest,LoginRequest,RefreshTokenRequest
from sqlalchemy.orm import Session
import uuid
from app.models.users import User
from app.db.init_db import get_db
from fastapi import Depends,HTTPException,status
from passlib.hash import pbkdf2_sha256
from app.utilities.auth_utils import create_token,verify_user,blacklist_access_token,verify_refresh_token,get_decoded_token
from app.core.config import settings
from app.db.init_cache import cache



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

    user = db.query(User).with_entities(User.email,User.password,User.id).filter(User.email == username).first()
    if not user or not pbkdf2_sha256.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token = await create_token(data={"sub": user.email},type="access",expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = await create_token(data={"sub": user.email},type="refresh",expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    cache.set(f"refresh_token_{str(user.id)}",refresh_token,settings.REFRESH_TOKEN_EXPIRE_MINUTES*60)

    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer","expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,"refresh_token": refresh_token,"refresh_token_expires_in": settings.REFRESH_TOKEN_EXPIRE_MINUTES}

@router.post("/logout")
async def logout(request: Request,user: User = Depends(verify_user)):

    cache.delete(f"refresh_token_{str(user.id)}")
    token = request.headers.get("Authorization").split(" ")[1]
    try:
        await blacklist_access_token(token)
    except HTTPException as e:
        print(f"Error blacklisting token : {e.detail}")
    return {"message": "Logout successful"}



@router.post("/token/refresh")
async def refresh_token(request: RefreshTokenRequest,user: User = Depends(verify_user),db: Session = Depends(get_db)):

    token = request.refresh_token.strip()
    token_verified = await verify_refresh_token(token,db)
     
    if token_verified is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
     
    access_token = await create_token(data={"sub": user.email},type="access",expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access_token, "token_type": "bearer","expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES}
     
    
@router.get("/token/decode")
async def decode_token(token: dict = Depends(get_decoded_token)):
    return token
