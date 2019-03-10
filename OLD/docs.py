"""
    This is a quick demo of the request currently supported by this server_id

    SERVER SIDE:
        # {"TYPE": "CONNECTED", "SERVER_ID": $server_id}
            - a new client is connected.

        # {"TYPE": "GET_PLAYER_INFO", "MSG": "..."}
            - sent when there's a timeout until the client responde by his full info

        # {"TYPE":"ROOM_CLOCK", "CLOCK":self.clock}
            - room clock. for the craps game

        # {"TYPE":"ROOM_JOINED", "ROOM_NAME":"DUMMY DATA"}
            - when a player enter a new room

        # {"TYPE":"ROOM_PLAYER_JOIN", "NAME":str(self._player_name) ,"SERVER_ID":str(self._server_id) ,"MONEY":"50000"}
            - when a new player enter the room

        # {"TYPE":"ROOM_PLAYER_LEFT", "NAME":str(self._player_name) ,"SERVER_ID":str(self._server_id) ,"MONEY":"50000"}
            - when a player leaves the room

        #


    CLIENT SIDE:
        # {"TYPE": "PLAYER_INFO", ... }

        # {"TYPE": "ECHO", ... }

        # {"TYPE": "JOIN_ROOM", ... }

        # {"TYPE": "ROOMS_FULL_INFO", ... }

        # {"TYPE": "ROOMS_ACTIVITY_INFO", ... }

        # 

"""
