from fastapi import FastAPI,Request
from app.db.init_db import init_db
from app.db.init_cache import cache
from app.apis import auth,user
import time
import uuid
from fastapi.responses import JSONResponse
from app.utilities.auth_utils import get_decoded_token
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware



app = FastAPI()
# init_db()



current_sessions = {}
app.include_router(auth.router)
app.include_router(user.router)


#our middleware to log the request and response

RATE_LIMIT = 10
RATE_LIMIT_PERIOD = 60

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["my-api.com", "localhost"]
)


   
@app.middleware("http")
async def rate_limit_middleware(request:Request,call_next):

    try:
        access_token = request.headers.get("Authorization")
        if not access_token:
            user_id = "anonymous"
        else:
            decode_token  = await get_decoded_token(access_token.split(" ")[1])
            if not decode_token or decode_token.get("sub") is None:
                user_id = "anonymous"
            else:
                user_id = decode_token.get("sub")

        cache_key = f"rate_limit:{user_id}"
        current_count = cache.incr(cache_key,1)
        cache.expire(cache_key,RATE_LIMIT_PERIOD)

        if current_count > RATE_LIMIT:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        
        
        response = await call_next(request)
        return response
    
    except Exception as e:
        print(f"Error in rate_limit_middleware: {e} at line {e.__traceback__.tb_lineno}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    

@app.middleware("http")
async def log_middleware(request:Request,call_next):

    start_time = time.perf_counter()

    x_request_id = request.headers.get("X-Request-Id",str(uuid.uuid4()))
    try:
        response = await call_next(request)
    except Exception as e:
        print(f" ERROR HANDLING - Request ID: {x_request_id}, Method: {request.method}, Path: {request.url.path}, Status Code: {response.status_code}, Elapsed Time: {end_time - start_time}")
        raise e
    
    response.headers["X-Request-Id"] = x_request_id
    end_time = time.perf_counter()

    print(f"Request ID: {x_request_id}, Method: {request.method}, Path: {request.url.path}, Status Code: {response.status_code}, Elapsed Time: {end_time - start_time}")
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok"}

