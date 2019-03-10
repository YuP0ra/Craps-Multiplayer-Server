from socket import timeout
from threading import Thread
import time, json, database


class Matcher:
    def __init__(self,):
        self._room_id_dict = {}
        self._room_name_dict = {}

    def add_room(room_name, room_id, room_instance):
        self._room_id_dict[room_id] = room_instance
        self._room_name_dict[room_name] = room_instance


    def match_by_room_id(self, room_id, player):
        self._room_id_dict[room_id].add_player(player)

    def match_by_room_name(self, room_name, player):
        self._room_name_dict[room_name].add_player(player)



class Room(Thread):
    ROOM_ID = 100
    def __init__(self, server_id, name, capacity, min_bet, max_bet):
        Thread.__init__(self)
        Room.ROOM_ID        += 1
        Room.SERVER_ID      = server_id

        self._counter       = -1
        self._plaers        = []

        self.name           = name
        self.min_bet        = min_bet
        self.max_bet        = max_bet
        self.capacity       = capacity


    def run(self,):
        while True:
            time.sleep(1)
            if len(self._plaers) == 0: continue

            self.broadcast_event({"TYPE":"ROOM_CLOCK", "CLOCK":self.clock})
            print("EVENT SENT TO ALL PLAYERS")


    @property
    def clock(self):
        self._counter = self._counter + 1
        return str(self._counter % 14)


    def broadcast_event(self, sender, json_frame):
        for player in self._plaers:
            if not sender == player:
                player.send_data(json_frame)


    def add_player(self, player):
        if len(self._plaers) < self.capacity:
            self._plaers.append(player)
            player.send_data({"TYPE":"ROOM_JOINED", "ROOM_NAME":"DUMMY DATA"})
            self.broadcast_event(player, {"TYPE":"ROOM_PLAYER_JOIN"} + player.player_info)



class Player(Thread):
    PLAYER_ID = 0
    def __init__(self, socket):
        Thread.__init__(self)

        Player.PLAYER_ID += 1
        socket.settimeout(5)

        self._server_id     = Player.PLAYER_ID
        self._player_id     = None
        self._socket        = socket
        self.request_queue  = []

        self._player_name   = None


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
        self.send_data({"TYPE": "CONNECTED", "SERVER_ID": self._server_id})


    def on_client_timeout(self,):
        if self._player_name is None:
            self.send_data({"TYPE": "GET_PLAYER_INFO", "MSG": "Server is asking you to send your info. username, userID and accessToken"})


    def on_client_disconnect(self,):
        print("CLIENT ID:%s HAS DISCONNECTED" % (self._server_id))
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
            print("Player ", request['NAME'], "is now in the lobby")
            self._player_name = request['NAME']
            return

        if request['TYPE'] == "ECHO":
            request['SERVER_EXTRA'] = time.ctime()
            self.send_data(request)
            return

        if request['TYPE'] == "JOIN_ROOM":
            pass

        if request['TYPE'] == "ROOMS_FULL_INFO":
            self.send_data(database.get_rooms_full_info())
            return

        if request['TYPE'] == "ROOMS_ACTIVITY_INFO":
            self.send_data(database.get_rooms_active_players_info())
            return
