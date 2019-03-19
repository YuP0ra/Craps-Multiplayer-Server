import os, json, time, socket, secrets, importlib, inspect
from threading import Thread
from socket import timeout

from . import database


class GameServer(Thread):
    def __init__(self, HOSTNAME, PORT, requestHandlerPath='./Requests/'):
        Thread.__init__(self,)
        database.init()

        self.__moudles = {}
        self.__methods = {}
        self.__loops = []
        self.__inits = []

        self.PATH = requestHandlerPath
        self.HOSTNAME = HOSTNAME
        self.PORT = PORT

    def run(self,):
        self.__loadScripts()

        SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SERVER.bind((self.HOSTNAME, self.PORT))
        SERVER.listen(5)

        print("Server started on main thread")

        for loop in self.__loops:
            Thread(target=loop).start()

        for init in self.__inits:
            init()

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
            methods = [func for func in dir(objectModule) if inspect.isfunction(getattr(objectModule, func))]
            for method in methods:
                if method == 'run':
                    self.__loops.append(getattr(objectModule, method))
                elif method == 'init':
                    self.__inits.append(getattr(objectModule, method))
                else:
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



class RemoteClient():
    def __init__(self, socket, address, kernel):
        self._stack = []
        self._sendThrd = Thread(target=self.rceving_thread)
        self._rcevThrd = Thread(target=self.sending_thread)

        self.TOKEN      = str(secrets.token_hex(16))

        self._socket    = socket
        self._kernel    = kernel

        self.DATA       = {}
        self.address    = address

    def __eq__(self, other):
        return self.TOKEN == other.TOKEN

    def __hash__(self):
        return hash(self.TOKEN)

    def start(self,):
        self.on_client_connect()
        self._socket.settimeout(5)

        self._rcevThrd.start()
        self._sendThrd.start()

    def on_client_connect(self,):
        self._kernel.processClientEvents(self, "onConnectionStarted")

    def on_client_timeout(self,):
        self._kernel.processClientEvents(self, "onConnectionTimeout")

    def on_client_disconnect(self,):
        self._kernel.processClientEvents(self, "onConnectionEnded")
        quit()

    def rceving_thread(self,):
        while True:
            requests = self.recv_data()

            if requests is "TIMEOUT":
                continue

            for request in requests:
                self.process_request(request)
        self.on_client_disconnect()

    def sending_thread(self,):
        while True:
            try:
                if len(self._stack) == 0:
                    time.sleep(0.02)
                else:
                    data_dict = self._stack.pop(0)
                    json_form = json.dumps(data_dict) + "<EOF>"
                    valid_socket_form = json_form.encode('ascii')
                    self._socket.sendall(valid_socket_form)
            except Exception as e:
                self.on_client_disconnect()
                return None

    def send_data(self, data_dict):
        self._stack.append(data_dict)

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
