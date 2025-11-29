
import json
import uuid
import ast

current_sessions = {}
STATUS_CODES = {
    200: "200 OK",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    500: "500 Internal Server Error"
}

def handle_request(request):
    parsed_request = request.decode("utf-8")
    request_dict = {}
    header_text, _, body = parsed_request.partition("\r\n\r\n")
    request_lines = header_text.split("\r\n")

    request_dict["method"], request_dict["path"], request_dict["protocol"] = request_lines[0].split(" ")

    #headers
    request_dict["headers"] = {}
    for line in request_lines[1:]:
        if line=="":
            break
        key, value = line.split(": ")
        request_dict["headers"][key] = value

    #query params
    if "?" in request_dict["path"]:
        request_dict["path"], query_string = request_dict["path"].split("?")
        query_params = dict(param.split("=") for param in query_string.split("&"))
        request_dict["query_params"] = query_params

    #body
    if body.strip():
        try:
            request_dict["body"] = json.loads(body)
        except (ValueError, SyntaxError):
            return None, "400 Bad Request"
    else:
        request_dict["body"] = {}

    #cookies
    if "Cookie" in request_dict["headers"]:
        request_dict["cookies"] = dict(cookie.split("=") for cookie in request_dict["headers"]["Cookie"].split(";"))
    else:
        request_dict["cookies"] = {}

    #unique request id
    request_dict["request_id"] = str(uuid.uuid4())

    print(f"Request received from {request_dict['headers'].get('Host', '')}")

    return request_dict,None


def handle_login(parsed_request):
    body = parsed_request.get("body", {})
    authenticated = verify_credentials(body)
    if authenticated:
        return 200, {"message": "Login successful"}, {"Content-Type": "application/json", "Set-Cookie": f"session_id={authenticated}", "X-Request-Id": parsed_request["request_id"]}
    else:
        return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}
def verify_credentials(credentials):
    username = credentials.get("username", "").strip()
    password = credentials.get("password", "").strip()
    if username=="admin" and password=="tempPassword":
        session_id = str(uuid.uuid4())
        current_sessions[session_id] = {"username": username}
        return session_id
    else:
        return False
    
def handle_greet(parsed_request):
    session_id = parsed_request.get("cookies", {}).get("session_id", "")
    if session_id:
        if session_id in current_sessions:
            username = current_sessions[session_id]["username"]
            return 200, {"message": f"Hello, {username}!"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}
        else:
            return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}
    else:
        return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}

def handle_logout(parsed_request):
    session_id = parsed_request.get("cookies", {}).get("session_id", "")
    if session_id:
        if session_id in current_sessions:
            del current_sessions[session_id]
            return 200, {"message": "Logout successful"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}
        else:
            return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}
    else:
        return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}


def handle_route(parsed_request):
    path = parsed_request.get("path", "")
    method = parsed_request.get("method", "")

    if path=="/login" and method=="POST":
        return handle_login(parsed_request)
        
    elif path=="/greet" and method=="GET":
        return handle_greet(parsed_request)
    elif path=="/logout" and method=="POST":
        return handle_logout(parsed_request)
    else:
        return 404, {"message": "404 Not Found"}, {"Content-Type": "application/json", "X-Request-Id": parsed_request["request_id"]}

def build_respone(status, body, headers):
    
    if body:
        body = json.dumps(body)
    else:
        body = {}
    default_headers = {
        "Content-Length": str(len(body))
    }
    headers.update(default_headers)
    response = (f"HTTP/1.1 {STATUS_CODES[status]}\r\n"
                + "\r\n".join([f"{key}: {value}" for key, value in headers.items()])
                + "\r\n\r\n"
                + body
                )
    return response