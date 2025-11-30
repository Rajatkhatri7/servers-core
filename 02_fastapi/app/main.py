from fastapi import FastAPI
from app.db.init_db import init_db
from app.db.init_cache import cache
from app.apis import auth,user

app = FastAPI()
# init_db()



current_sessions = {}
app.include_router(auth.router)
app.include_router(user.router)



@app.get("/health")
async def health_check():
    return {"status": "ok"}

