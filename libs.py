class TCPClient:
    def __init__(self, client_socket, address):
        self.socket = client_socket
        self.address = address


    def hook_client(self,):
        while True:
            threading.Thread(target=self.data_revicer, args=()).start()

    def request_handler(self,):
        pass
