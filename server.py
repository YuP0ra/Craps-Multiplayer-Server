import time
import json
import socket
import threading


def request(mode, msg):
    return {"MODE":mode, "MSG":msg}


def send_data(client_socket, data_dict):
    """ Convert the dict into json and append the EndOfFile mark """
    return client_socket.send("{0}<EOF>".format(json.dumps(data_dict)).encode('utf-8'))


def recv_data(client_socket):
    """ Basiclly keep recieving until you reach the end of the orginial msg """
    message = ''
    while not message.endswith('<EOF>'):
        message += client_socket.recv(256)
        if len(message) == 0:
            return None
    return message.rstrip()[:-5]


def main_thread(main_socket, data_base):
    while True:
        client_socket, client_address = main_socket.accept()
        threading.Thread(target=handle_client_recieve, args=(client_socket, client_address)).start()
        threading.Thread(target=handle_client_send, args=(client_socket, client_address)).start()
    print("Exiting Server")


def handle_client_recieve(client_socket, address):
    print("Client has connected. IP: ", address)
    while True:
        try:
            data = recv_data(client_socket)
            print(data)
        except Exception as e:
            break
    print("Client has been disconnected. IP: ", address)


def handle_client_send(client_socket, address):
    ''' welcome msg is sent to inform the client that he has been connected successfully '''
    send_data(client_socket, request("LOGIN", "success"))

    while True:
        try:
            send_data(client_socket, {"time": time.time()})
            time.sleep(5);
        except Exception as e:
            break
