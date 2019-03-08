import time
import json
import socket
import threading


def request(mode, header, msg):
    return {"MODE":mode, "HEADER":header, "MSG":msg}


def send_data(client_socket, data_dict):
    return client_socket.send(json.dumps(data_dict).encode('utf-8'))


def recv_data(client_socket):
    return json.loads(client_socket.recv(1024))


def main_thread(main_socket, data_base):
    while True:
        client_socket, client_address = main_socket.accept()
        threading.Thread(target=handle_client_recieve, args=(client_socket, client_address)).start()
        threading.Thread(target=handle_client_send, args=(client_socket, client_address)).start()


def handle_client_recieve(client_socket, address):
    print("Client has connected. IP: ", address)

    while True:
        try:
            data = recv_data(client_socket)
            print(data)
        except Exception as e:
            print("Client has been disconnected. IP: ", address)
            break


def handle_client_send(client_socket, address):
    ''' welcome msg is sent to inform the client that he has been connected successfully '''
    send_data(client_socket, request("POST", "LOGIN", "success"))

    while True:
        try:
            send_data(client_socket, {"time": time.time()})
            time.sleep(1);
        except Exception as e:
            break
