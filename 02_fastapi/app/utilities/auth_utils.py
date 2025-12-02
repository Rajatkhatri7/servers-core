from jose import JWTError, jwt
from datetime import datetime, timedelta,time,timezone
from app.core.config import settings
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.init_db import get_db
from app.models.users import User
import uuid
from app.db.init_cache import cache


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_decoded_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def create_token(data: dict, type: str,expires_minutes: int):
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire,"type":type,"jti":jti})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def blacklist_access_token(token: str):
    try:

        token_payload = await get_decoded_token(token)
        if token_payload is None:
            return 
        jti = token_payload.get("jti")
        ttl = int(token_payload.get("exp")-datetime.now(timezone.utc).timestamp())
        if ttl>0:
            cache.set(f"blacklisted_token_{jti}",token,ttl)
    except Exception as e:
        print(f"Error blacklisting access token: {e} at line {e.__traceback__.tb_lineno}")

async def verify_refresh_token(token: str,db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await get_decoded_token(token)
        if payload is None:
            raise credentials_exception
        jti = payload.get("jti")
        if payload.get("type") != "refresh" or jti is None or payload.get("sub") is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    elif cache.get(f"refresh_token_{str(user.id)}") is None:
        raise credentials_exception
    
    return user
    
    
    
    
    
    
async def verify_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await get_decoded_token(token)
        if payload is None:
            raise credentials_exception

        if payload.get("type") != "access" or payload.get("jti") is None or payload.get("sub") is None:
            raise credentials_exception
        
        jti = payload.get("jti")
        blacklisted = cache.get(f"blacklisted_token_{jti}")
        if blacklisted:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


async def admin_required(user: User = Depends(verify_user)):
    if user.is_admin is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    return user