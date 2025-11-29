
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
}

def handle_request(request):
    parsed_request = request.decode("utf-8")
    request_dict = {}
    header_text, _, body = parsed_request.partition("\r\n\r\n")
    request_lines = header_text.split("\r\n")

    request_dict["method"], request_dict["path"], request_dict["protocol"] = request_lines[0].split(" ")
    request_dict["headers"] = {}
    for line in request_lines[1:]:
        if line=="":
            break
        key, value = line.split(": ")
        request_dict["headers"][key] = value

    

    if body.strip():
        try:
            request_dict["body"] = json.loads(body)
        except (ValueError, SyntaxError):
            return None, "400 Bad Request"

    print(f"Request received from {request_dict['headers'].get('Host', '')}")

    return request_dict,None

def verify_credentials(credentials):
    username = credentials.get("username", "").strip()
    password = credentials.get("password", "").strip()
    if username=="admin" and password=="tempPassword":
        session_id = str(uuid.uuid4())
        current_sessions[session_id] = {"username": username}
        return session_id
    else:
        return False

def handle_route(parsed_request):
    path = parsed_request.get("path", "")
    method = parsed_request.get("method", "")
    body = parsed_request.get("body", {})
    cookie = parsed_request.get("headers", {}).get("Cookie", "")

    query_params = {}
    if "?" in path:
        path, query_string = path.split("?")
        query_params = dict(param.split("=") for param in query_string.split("&"))

    if path=="/login":
        if method!="POST":
            return 405, {"message": "405 Method Not Allowed"}, {"Content-Type": "application/json"}
        
        authenticate = verify_credentials(body)
        if authenticate:
            return 200, {"message": "Login successful"}, {"Content-Type": "application/json", "Set-Cookie": f"session_id={authenticate}"}
        else:
            return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json"}
        
    elif path=="/greet" and method=="GET":
        session_id = cookie.split("=")[1]
        if session_id not in current_sessions:
            return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json"}
        
        username = current_sessions[session_id]["username"]
        return 200, {"message": f"Hello, {username}!"}, {"Content-Type": "application/json"}
    
    elif path=="/logout" and method=="POST":
        session_id = cookie.split("=")[1]
        if session_id not in current_sessions:
            return 401, {"message": "401 Unauthorized"}, {"Content-Type": "application/json"}
        del current_sessions[session_id]
        return 200, {"message": "Logout successful"}, {"Content-Type": "application/json"}


def build_respone(status, body, headers):
    
    if body:
        body = json.dumps(body)
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