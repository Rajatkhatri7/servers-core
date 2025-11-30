from pydantic import BaseModel,EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: str
    email: str
    access_token: str
    token_type: str = "bearer"

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

