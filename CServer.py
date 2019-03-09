import time
import json
import socket
import threading


class Player:
    PLAYER_ID = 0
    def __init__(self, socket):
        Player.PLAYER_ID += 1

        self._id            = Player.PLAYER_ID
        self._socket        = socket




    def send_data(self, data_dict):
        """ Convert the dict into json and append the EndOfFile mark """
        json_form = json.dumps(data_dict)
        valid_socket_form = "{0}<EOF>".format(json_form)
        valid_socket_form_bytes = valid_socket_form.encode('ascii')
        try:
            return client_socket.send(valid_socket_form_bytes)
        except Exception as e:
            return None

    def recv_data(self, client_socket):
        """ This function will return a list of valid socket segments transmitted over the network """

        frame, eof = bytes('', 'ascii'), '<EOF>'
        try:
            while not frame.endswith(bytes(eof, 'ascii')):
                frame += client_socket.recv(256)
        except Exception as e:
            return None



x = dict()
x['plaer'] = "plaer name"
x['sore'] = 1236

j = json.dumps(x)



print(j == str(x).replace('\'', '"'))
