def main_request_handler(user, request):
    if "MODE" in request:
        if request['MODE'] == "ECHO":
            user.send_data(request)
