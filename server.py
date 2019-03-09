import time
import json
import socket
import threading
from CrapsGame import main_request_handler


def request(mode, msg):
    return {"MODE":mode, "MSG":msg}


def send_data(client_socket, data_dict):
    """ Convert the dict into json and append the EndOfFile mark """
    json_form = json.dumps(data_dict)
    valid_socket_form = "{0}<EOF>".format(json_form)
    valid_socket_form_bytes = valid_socket_form.encode('ascii')
    try:
        return client_socket.send(valid_socket_form_bytes)
    except Exception as e:
        return None

def recv_data(client_socket):
    """ This function will return a list of valid socket segments transmitted over the network """

    frame, eof = bytes('', 'ascii'), '<EOF>'
    try:
        while not frame.endswith(bytes(eof, 'ascii')):
            frame += client_socket.recv(256)
    except Exception as e:
        return None

    string_frames = [json.loads(f) for f in frame.decode('ascii').split(eof) if len(f) > 0]
    return string_frames


def main_thread(main_socket, data_base):
    while True:
        client_socket, client_address = main_socket.accept()
        threading.Thread(target=handle_client_recieve, args=(client_socket, client_address)).start()
        threading.Thread(target=handle_client_send, args=(client_socket, client_address)).start()


def handle_client_recieve(client_socket, address):
    print("Client has connected. IP: ", address)
    while True:
        data = recv_data(client_socket)
        if data is None:                        # Connection is lost.
            break
        main_request_handler(main_socket, data)
    print("Client has disconnected. IP: ", address)


def handle_client_send(client_socket, address):
    ''' welcome msg is sent to inform the client that he has been connected successfully '''
    if not send_data(client_socket, request("LOGIN", "success")) is None:
        while not send_data(client_socket, request("TIME", time.time())) is None:
            time.sleep(5);
