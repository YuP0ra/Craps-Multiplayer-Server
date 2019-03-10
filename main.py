from CrapsServer import Player
import socket

HOSTNAME, PORT = "0.0.0.0", 4466
if __name__ == '__main__':
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((HOSTNAME, PORT))
    SERVER.listen(5)

    print("Server started on main thread")
    while True:
        client_socket, client_address = SERVER.accept()
        print("New IP: %s" % client_address[0])
        Player(client_socket).start()
