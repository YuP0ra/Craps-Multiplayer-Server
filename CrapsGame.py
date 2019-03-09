from server import send_data

def main_request_handler(user, request):
    if "MODE" in request:
        if request['MODE'] == "ECHO":
            send_data(user, request)
