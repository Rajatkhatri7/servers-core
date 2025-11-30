from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.users import User
from app.utilities.auth_utils import verify_user

router = APIRouter(prefix="/user")

@router.get("/details")
async def get_user_details(user: User = Depends(verify_user)):
        return {"id": str(user.id), "email": user.email, "username": user.username}