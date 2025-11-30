from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from app.models.users import User
from app.utilities.auth_utils import verify_user,admin_required
from app.db.init_db import get_db
import uuid


router = APIRouter(prefix="/user")

@router.get("/details")
async def get_user_details(user: User = Depends(verify_user)):
        return {"id": str(user.id), "email": user.email, "username": user.username}


@router.get("/all")
async def get_all_users(db: Session = Depends(get_db),user: User = Depends(verify_user)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    users = db.query(User).with_entities(User.id, User.email, User.username, User.is_admin).all()

    response = [{"id": str(user.id), "email": user.email, "username": user.username, "is_admin": user.is_admin} for user in users]
    return response
    

@router.patch("/update_role/{user_id}")
async def update_user_role(user_id: str, db: Session = Depends(get_db),user: User = Depends(admin_required)):
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    user_to_update = db.query(User).filter(User.id == user_uuid).first()
    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_to_update.is_admin = True
    db.commit()
    return {"message": "User updated successfully"}

@router.patch("/update/{user_id}")
async def update_user(request: Request,user_id: str, db: Session = Depends(get_db),user: User = Depends(verify_user)):
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID format")
    user_to_update = db.query(User).filter(User.id == user_uuid).first()
    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # get user details from request body
    user_details = await request.json()

    ALLOWED_FIELDS = {"username"}
    
    for field in user_details.keys():
        if field not in ALLOWED_FIELDS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid field: {field}")
        setattr(user_to_update, field, user_details[field])

    db.commit()
    return {"message": "User updated successfully"}