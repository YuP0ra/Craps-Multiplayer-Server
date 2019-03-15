import threading
import database
import server
import socket
import time

HOSTNAME, PORT = "0.0.0.0", 4466      #35.198.95.100


if __name__ == '__main__':
    DATABASE = database.Database()

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((HOSTNAME, PORT))
    SERVER.listen(5)
    z
    ACCEPT_THREAD = threading.Thread(target=server.main_thread, args=(SERVER, DATABASE))
    ACCEPT_THREAD.start()
    print("Main thred is on.")
    ACCEPT_THREAD.join()
