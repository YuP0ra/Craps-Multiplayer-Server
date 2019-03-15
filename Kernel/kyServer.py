import os, json, socket, secrets, importlib
from threading import Thread
from socket import timeout

from . import database


class GameServer(Thread):
    def __init__(self, HOSTNAME, PORT, requestHandlerPath='./Requests/'):
        Thread.__init__(self,)
        database.init()

        self.__moudles = {}
        self.__methods = {}

        self.PATH = requestHandlerPath
        self.HOSTNAME = HOSTNAME
        self.PORT = PORT

    def run(self,):
        self.__loadScripts()

        SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SERVER.bind((self.HOSTNAME, self.PORT))
        SERVER.listen(5)

        print("Server started on main thread")
        while True:
            client_socket, client_address = SERVER.accept()
            RemoteClient(client_socket, client_address, self).start()

    def __loadScripts(self,):
        scripts = [x for x in os.listdir(self.PATH) if x[-3:] == '.py']

        for script in scripts:
            # Load the moudle into python then excute it
            loader = importlib.machinery.SourceFileLoader(script[:-3], self.PATH + script)
            objectModule = loader.load_module()

            # register the moudle
            self.__moudles[script] = objectModule

            # get requests method
            methods = [func for func in dir(objectModule) if callable(getattr(objectModule, func))]
            for method in methods:
                if not method in self.__methods:
                    self.__methods[method] = []
                self.__methods[method].append(getattr(objectModule, method))

    def processClientEvents(self, client, event):
        if event in self.__methods:
            for method in self.__methods[event]:
                method(client)

    def processClientRequest(self, client, request):
        if request['TYPE'] in self.__methods:
            for method in self.__methods[request['TYPE']]:
                method(client, request)
        else:
            if 'DEFAULT' in self.__methods:
                for method in self.__methods['DEFAULT']:
                    method(client, request)



class RemoteClient(Thread):
    RemoteClientID = 0
    def __init__(self, socket, address, kernel):
        Thread.__init__(self)
        socket.settimeout(5)
        RemoteClient.RemoteClientID += 1

        self._socket    = socket
        self._kernel    = kernel

        self.address    = address
        self.token      = RemoteClient.RemoteClientID

    def __eq__(self, other):
        pass

    def run(self,):
        self.on_client_connect()
        while True:
            requests = self.recv_data()

            if requests is "TIMEOUT":
                continue

            for request in requests:
                self.process_request(request)
        self.on_client_disconnect()

    def on_client_connect(self,):
        self._kernel.processClientEvents(self, "onConnectionStarted")

    def on_client_timeout(self,):
        self._kernel.processClientEvents(self, "onConnectionTimeout")

    def on_client_disconnect(self,):
        self._kernel.processClientEvents(self, "onConnectionEnded")
        quit()

    def send_data(self, data_dict):
        """ Convert the dict into json and append the EndOfFile mark """

        json_form = json.dumps(data_dict) + "<EOF>"
        valid_socket_form = json_form.encode('ascii')
        try:
            return self._socket.sendall(valid_socket_form)
        except Exception as e:
            self.on_client_disconnect()
            return None

    def recv_data(self,):
        """ This function will return a list of valid socket segments transmitted over the network """

        frame, eof = bytes('', 'ascii'), '<EOF>'
        try:
            while not frame.endswith(bytes(eof, 'ascii')):
                tmp_frame = self._socket.recv(1024)
                frame += tmp_frame

                if tmp_frame is None or len(tmp_frame) == 0:
                    if len(frame) > 0:
                        break
                    else:
                        raise Exception("CLIENT DISCONNECTED")

        except timeout as e:
            self.on_client_timeout()
            return "TIMEOUT"
        except Exception as e:
            self.on_client_disconnect()
            return None

        string_frames = []
        for single_frame in frame.decode('ascii').split(eof):
            try:
                string_frames.append(json.loads(single_frame))
            except Exception as e:
                continue
        return string_frames

    def process_request(self, request):
        if not 'TYPE' in request:
            return
        else:
            self._kernel.processClientRequest(self, request)
