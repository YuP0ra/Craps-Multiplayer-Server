import os
import json
import time
import socket
import secrets
import inspect
import asyncore
import importlib

from socket import timeout
from threading import Thread


class GameServer(asyncore.dispatcher):
    def __init__(self, HOSTNAME, PORT, requestHandlerPath='./Requests/'):
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((HOSTNAME, PORT))
        self.listen(5)

        self.__moudles  = {}
        self.__methods  = {}
        self.__loops    = []
        self.__inits    = []

        self.PATH       = requestHandlerPath
        self.HOSTNAME   = HOSTNAME
        self.PORT       = PORT
        self.CLIENTID   = 0

    def run_server(self,):
        self._loadScripts()

        for init in self.__inits:
            init()

        for loop in self.__loops:
            Thread(target=loop).start()

        print("Server started on main thread")
        asyncore.loop(timeout=0.5, use_poll=True)


    def _loadScripts(self,):
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

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sockt, address = pair
            RemoteClient(sockt, address, self.processClientEvents, self.processClientRequest).handle_connect()

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



class RemoteClient(asyncore.dispatcher_with_send):
    def __init__(self, socket, address, on_event, on_request):
        asyncore.dispatcher_with_send.__init__(self, sock=socket)

        self.DATA           = {}
        self.address        = address
        self._on_event      = on_event
        self._on_request    = on_request
        self._recv_buffer   = bytes('', 'ascii')
        self._send_buffer   = bytes('', 'ascii')
        self.TOKEN          = str(secrets.token_hex(16))

    def __eq__(self, other):
        return self.TOKEN == other.TOKEN

    def writable(self):
        return len(self._send_buffer) > 0

    def handle_write(self):
        sent = self.send(self._send_buffer)

        if sent is None:
            self._send_buffer = bytes('', 'ascii')
        else:
            self._send_buffer = self._send_buffer[sent:]

    def handle_read(self):
        data = self.recv(4096)

        if not data: return
        self._recv_buffer += data
        if not data.endswith(bytes('<EOF>', 'ascii')): return

        for request in self._recv_buffer.decode('ascii').split('<EOF>'):
            if len(request) > 0:
                request = json.loads(request)
                if 'TYPE' in request: self._on_request(self, request)
        self._recv_buffer = bytes('', 'ascii')

    def send_data(self, request_dict):
        marked_request      = json.dumps(request_dict) + "<EOF>"
        request_bytes       = marked_request.encode('ascii')
        self._send_buffer   = self._send_buffer + request_bytes

    def handle_connect(self,):
        self._on_event(self, "onConnectionStarted")

    def handle_close(self,):
        self._on_event(self, "onConnectionEnded")
        self.close()
