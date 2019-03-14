import time, json, database, secrets
from threading import Thread
from socket import timeout


class Matcher:
    def __init__(self,):
        self._rooms_dict = {}

    def add_room(self, room):
        self._rooms_dict[room.name] = room

    def match_by_room_name(self, room_name, player):
        self._rooms_dict[room_name].add_player(player)



class Room(Thread):
    def __init__(self, name, capacity, min_bet, max_bet):
        Thread.__init__(self)
        self._counter       = -1
        self._players       = []

        self.name           = name
        self.min_bet        = min_bet
        self.max_bet        = max_bet
        self.capacity       = capacity


    def run(self,):
        while True:
            time.sleep(1)
            if len(self._players) == 0:
                continue
            else:
                database.rooms_active_players[database.rooms_name.index(self.name)] = len(self._players)

            for player in self._players:
                player.send_data({"TYPE":"ROOM_CLOCK", "CLOCK":self.clock})


    @property
    def clock(self):
        self._counter = self._counter + 1
        return str(self._counter % 14)


    def broadcast_event(self, sender, json_frame):
        for player in self._players:
            if not sender == player:
                player.send_data(json_frame)


    def add_player(self, player):
        if len(self._players) < self.capacity and player not in self._players:
            self._players.append(player)
            player._joined_room = self
            database.rooms_active_players[database.rooms_name.index(self.name)] += 1
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "ROOM_NAME":str(self.name)})
        else:
            player.send_data({"TYPE":"ROOM_JOIN_FAILD", "ERROR_MSG":"Room is at full capacity."})


    def remove_player(self, player):
        self._players.remove(player)
        self.broadcast_event(player, {"TYPE":"ROOM_PLAYER_LEFT"} + player.player_info)



class Player(Thread):
    PLAYER_ID = 0
    def __init__(self, socket, matcher):
        Thread.__init__(self)
        socket.settimeout(5)

        """ Server side data """
        Player.PLAYER_ID   += 1
        self._joined_room   = None
        self._server_id     = Player.PLAYER_ID

        self._matcher       = matcher
        self._socket        = socket
        self.request_queue  = []

        """ Player info data """
        self._token         = secrets.token_hex(32)
        self._player_name   = None
        self._money         = 50000


    def __eq__(self, other):
        return str(self._token) == str(other._token)


    def player_info(self, type="PLAYER_INFO"):
        return {"TYPE"      :str(type),
                "NAME"      :str(self._player_name) ,
                "SERVER_ID" :str(self._server_id),
                "TOKEN"     :str(self._token),
                "MONEY"     :str(self._money)
                }


    def run(self,):
        self.on_client_connect()
        while True:
            requests = self.recv_data()

            if requests is None: break
            if requests is "TIMEOUT": continue

            for request in requests:
                self.process_request(request)


    def on_client_connect(self,):
        self.send_data({"TYPE"      :"CONNECTED",
                        "SERVER_ID" :str(self._server_id),
                        "TOKEN"     :str(self._token),
                        })


    def on_client_timeout(self,):
        if self._player_name is None:
            self.send_data({"TYPE": "GET_PLAYER_INFO"})


    def on_client_disconnect(self,):
        print("CLIENT ID:%s HAS DISCONNECTED" % (self._server_id))
        if self._joined_room is not None:
            del self._joined_room._players[self._joined_room._players.index(self)]
            database.rooms_active_players[database.rooms_name.index(self._joined_room.name)] = len(self._joined_room._players)
        quit()


    def send_data(self, data_dict):
        """ Convert the dict into json and append the EndOfFile mark """

        json_form = json.dumps(data_dict) + "<EOF>"
        valid_socket_form = json_form.encode('ascii')
        try:
            return self._socket.send(valid_socket_form)
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
        if not 'TYPE' in request: return

        if request['TYPE'] == "PLAYER_INFO":
            self._player_name = request['NAME']
            self._token = request['TOKEN']
            self._money = request['MONEY']
            return

        if request['TYPE'] == "JOIN_ROOM_REQUEST":
            if self._joined_room is None:
                self._matcher.match_by_room_name(request['ROOM_NAME'], self)

        if request['TYPE'] == "LEAVE_ROOM_REQUEST":
            if not self._joined_room is None:
                del self._joined_room._players[self._joined_room._players.index(self)]
                database.rooms_active_players[database.rooms_name.index(self._joined_room.name)] = len(self._joined_room._players)
                self._joined_room = None

        if request['TYPE'] == "ROOMS_FULL_INFO":
            self.send_data(database.get_rooms_full_info())
            return

        if request['TYPE'] == "ROOMS_ACTIVITY_INFO":
            self.send_data(database.get_rooms_active_players_info())
            return
