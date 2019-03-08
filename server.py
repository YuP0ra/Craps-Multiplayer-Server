import json
import socket
import threading


def request(mode, header, msg):
    return {"MODE":mode, "HEADER":header, "MSG":msg}


def send_data(client, data_dict):
    return client.send(json.dumps(data_dict))


def recv_data(client):
    return json.loads(client.recv(1024))


def main_thread(main_socket, data_base):
    while True:
        client_socket, client_address = main_socket.accept()
        send_data(client_socket, request("POST", "LOGIN", "success"))
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


def handle_client(client, address):
    while True:
        send_data(client, request("GET", "DATA", "please handover your name, id and pass"))
        dict = recv_data(client)
