from socket import timeout
from threading import Thread
import time, json, database


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
        self._players        = []

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
            database.rooms_active_players[database.rooms_name.index(self.name)] += 1
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "ROOM_NAME":"You've entered the room"})
        else:
            player.send_data({"TYPE":"ROOM_JOIN_FAILD", "ERROR_MSG":"Room is at full capacity."})



    def remove_player(self, player):
        self._players.remove(player)
        self.broadcast_event(player, {"TYPE":"ROOM_PLAYER_LEFT"} + player.player_info)



class Player(Thread):
    PLAYER_ID = -1
    def __init__(self, socket, matcher):
        Thread.__init__(self)

        Player.PLAYER_ID += 1
        socket.settimeout(5)

        self._server_id     = Player.PLAYER_ID
        self._matcher       = matcher
        self._socket        = socket
        self.request_queue  = []

        self._player_name   = None
        self._player_id     = None


    @property
    def player_info(self,):
        return {"NAME":str(self._player_name) ,"SERVER_ID":str(self._server_id) ,"MONEY":"50000"}


    def run(self,):
        self.on_client_connect()
        while True:
            requests = self.recv_data()

            if requests is None: break
            if requests is "TIMEOUT": continue

            for request in requests:
                self.process_request(request)


    def on_client_connect(self,):
        self.send_data({"TYPE": "CONNECTED", "SERVER_ID": str(self._server_id)})


    def on_client_timeout(self,):
        if self._player_name is None:
            self.send_data({"TYPE": "GET_PLAYER_INFO", "MSG": "Server is asking you to send your info. username, userID and accessToken"})


    def on_client_disconnect(self,):
        print("CLIENT ID:%s HAS DISCONNECTED" % (self._server_id))
        del this
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
            return

        if request['TYPE'] == "ECHO":
            request['SERVER_EXTRA'] = time.ctime()
            self.send_data(request)
            return

        if request['TYPE'] == "JOIN_ROOM_REQUEST":
            self._matcher.match_by_room_name(request['ROOM_NAME'], self)

        if request['TYPE'] == "ROOMS_FULL_INFO":
            self.send_data(database.get_rooms_full_info())
            return

        if request['TYPE'] == "ROOMS_ACTIVITY_INFO":
            self.send_data(database.get_rooms_active_players_info())
            return
