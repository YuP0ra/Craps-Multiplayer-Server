import threading
import database
import server
import time

HOSTNAME, PORT = "127.0.0.1", 4466

if __name__ == '__main__':
    DATABASE = database.Database()

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((HOSTNAME, PORT))
    SERVER.listen(5)

    ACCEPT_THREAD = threading.Thread(target=main_thread, args=(SERVER, DATABASE))
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
