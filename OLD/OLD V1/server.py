import time
import json
import socket
import threading


def request(TYPE, msg):
    return {"TYPE":TYPE, "MSG":msg}


def send_data(client_socket, data_dict):
    """ Convert the dict into json and append the EndOfFile mark """
    json_form = json.dumps(data_dict) + "<EOF>"
    valid_socket_form = json_form.encode('ascii')
    try:
        return client_socket.sendall(valid_socket_form)
    except Exception as e:
        return None

def recv_data(client_socket):
    """ This function will return a list of valid socket segments transmitted over the network """

    frame, eof = bytes('', 'ascii'), '<EOF>'
    try:
        while not frame.endswith(bytes(eof, 'ascii')):
            tmp_frame = client_socket.recv(1024)
            if not tmp_frame: break
            frame += tmp_frame
    except Exception as e:
        return None

    string_frames = []
    for single_frame in frame.decode('ascii').split(eof):
        try:
            string_frames.append(json.loads(single_frame))
        except Exception as e:
            continue
    return string_frames


def main_thread(main_socket, data_base):
    while True:
        client_socket, client_address = main_socket.accept()
        threading.Thread(target=handle_client_recieve, args=(client_socket, client_address)).start()
        threading.Thread(target=handle_client_send, args=(client_socket, client_address)).start()


def handle_client_recieve(client_socket, address):
    print("Client has connected. IP: ", address)
    while True:
        data_segments = recv_data(client_socket)
        if data_segments is None:                        # Connection is lost.
            break

        for data in data_segments:
            main_request_handler(client_socket, data)

    print("Client has disconnected. IP: ", address)


def handle_client_send(client_socket, address):
    ''' welcome msg is sent to inform the client that he has been connected successfully '''
    if not send_data(client_socket, request("LOGIN", "success")) is None:
        while not send_data(client_socket, request("TIME", time.time())) is None:
            time.sleep(0.01);


def main_request_handler(client_socket, request):
    if not "TYPE" in request:
        return

    if request['TYPE'] == "ECHO":
        send_data(client_socket, request)

    if request['TYPE'] == "ROOMS":
        send_data(client_socket, request("ROOMS", [0, 0, 0, 0]))
