from fastapi import FastAPI
from fastapi import Request, Response
from app.models import LoginRequest
import uuid

app = FastAPI()

current_sessions = {}



@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/login")
async def login(payload:LoginRequest, response:Response):
    username=payload.username.strip()
    password=payload.password.strip()

    if username=="admin" and password=="tempPassword":
        session_id = str(uuid.uuid4())
        current_sessions[session_id] = {"username": username}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return {"message": "Login successful"}
    else:
        return {"message": "Username or password is incorrect"}
    
@app.post("/logout")
async def logout(request:Request, response:Response):
    session_id = request.cookies.get("session_id")
    if session_id in current_sessions:
        del current_sessions[session_id]
        response.delete_cookie(key="session_id")
        return {"message": "Logout successful"}
    else:
        return {"message": "No active session"}
        
@app.get("/greet")
async def greet(request:Request, response:Response):
    session_id = request.cookies.get("session_id")
    if session_id in current_sessions:
        return {"message": f"Hello, {current_sessions[session_id]['username']}"}
    else:
        return {"message": "Unauthorized"}
