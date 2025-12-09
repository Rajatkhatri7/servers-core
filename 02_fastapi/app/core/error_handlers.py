
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Request
from app.core.exceptions import AppException
import traceback


def create_response_payload(code,message,status_code,details=None):

    payload = {
        'error':{
                    'code': code ,
                    'message': message,
                    'status_code':status_code
        }
    }
    if details:
        payload['error']['details'] = details

    return payload

async def app_exception_handler(request:Request,exc:AppException):
    request_id = request.state.request_id if hasattr(request.state,'request_id') else None
    payload = create_response_payload(exc.code,exc.message,exc.status_code,exc.details)

    return JSONResponse(content=payload,status_code=exc.status_code)

async def http_exception_handler(request:Request,exc:HTTPException):
    request_id = request.state.request_id if hasattr(request.state,'request_id') else None

    code="HTTP_ERROR"
    message = str(exc.detail) if exc.detail else exc.status_code
    payload = create_response_payload(code,message,exc.status_code)

    return JSONResponse(content=payload,status_code=exc.status_code)



async def validaton_exception_handler(request:Request,exc:RequestValidationError):
    request_id = request.state.request_id if hasattr(request.state,'request_id') else None

    payload = create_response_payload('VALIDATION_ERROR',"Invalid request data",422,exc.errors())

    return JSONResponse(content=payload,status_code=422)


async def generic_exception_handler(request:Request,exc:Exception):
    request_id = request.state.request_id if hasattr(request.state,'request_id') else None

    payload = create_response_payload("INTERNAL_SERVER_ERROR","Internal Server Error",500)

    return JSONResponse(content=payload,status_code=500)



def regiser_exception_hanlders(app):

    app.add_exception_handler(AppException,app_exception_handler)
    app.add_exception_handler(RequestValidationError,validaton_exception_handler)
    app.add_exception_handler(HTTPException,http_exception_handler)
    app.add_exception_handler(Exception,generic_exception_handler)



