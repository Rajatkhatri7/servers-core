import socket
from helpers import handle_request, handle_route, build_respone
import subprocess
import time



print("Socket server is starting.....")
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# killing the process running on port 8080
try:
    p = subprocess.run(["sudo","lsof", "-ti", ":8080"], capture_output=True, check=True)
    pid = p.stdout.decode()
    if pid:
        print(f"Found process with PID {pid}")
        pid = pid.strip()
        p = subprocess.run(["sudo","kill", "-9", pid], capture_output=True, check=True)
        time.sleep(10)
        print(f"Killed process with PID {pid}")

except Exception as e:
    print(f"Exception when trying to kill process with PID: {e}")
    time.sleep(20) #waiting for os to release port is process is killed


socket_server.bind(("localhost", 8080))
socket_server.listen(1)
print("Socket server is listening on localhost:8080")


while True:
    client_socket, client_address = socket_server.accept()
    request = client_socket.recv(1024)

    parsed_request,error = handle_request(request)
    if error:
        response_body = {
            "message": error
        }
        response = build_respone(400, response_body,headers={"Content-Type": "application/json"})
        client_socket.send(response.encode())
        client_socket.close()
        continue
    status, body, headers = handle_route(parsed_request)
    response = build_respone(status, body, headers)

    client_socket.send(response.encode())
    client_socket.close()

