from fastapi import FastAPI
from app.db.init_db import init_db
from app.apis import auth

app = FastAPI()
init_db()

current_sessions = {}
app.include_router(auth.router)



@app.get("/health")
async def health_check():
    return {"status": "ok"}

