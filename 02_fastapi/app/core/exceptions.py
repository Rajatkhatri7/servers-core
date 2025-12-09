

from typing import Any

#global custom exception for whole app
class AppException(Exception):

    def __init__(self, code:str,message:str,status_code:int = 400,details:Any = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

    def to_dict(self):
        payload = {
            "code":self.code,
            "message":self.message,
        }
        if self.details:
            payload['details'] = self.details

        return payload