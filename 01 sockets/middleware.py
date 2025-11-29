
from helpers import handle_route

def middleware_wrapper(request):
    print("Middleware: Request received")
    try:
        response = handle_route(request)
        if response:
            return response
        else:
            return 404, {"message": "404 Not Found"}, {"Content-Type": "application/json"}
    except Exception as e:
        print(f"Middleware: Error - {e}")
        return 500, {"message": "500 Internal Server Error"}, {"Content-Type": "application/json"}