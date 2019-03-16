class Room():
    def __init__(self, name, capacity, min_bet, max_bet):
        self._players       = {}

        self.name           = name
        self.min_bet        = min_bet
        self.max_bet        = max_bet
        self.capacity       = capacity


    def broadcast_event(self, sender, json_frame):
        for player in self._players:
            if not sender == player:
                player.send_data(json_frame)


    def add_player(self, player):
        if len(self._players) < self.capacity and player.TOKEN not in self._players:
            self._players[player.TOKEN] = [player, True]
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "ROOM_NAME":str(self.name)})
            return True
        else:
            player.send_data({"TYPE":"ROOM_JOIN_FAILD", "ERROR_MSG":"Room is at full capacity."})

        roomsActivity = configFile['active_players']
        roomIndex = configFile['rooms_name'].index(request['ROOM_NAME'])

        if not player.TOKEN in playersTokensDict:           # The player is not in a room
            if roomsActivity[roomIndex] < ROOM_CAPACITY:
                """ Here we assign a player a room. socket,    room_name,      isActive """
                playersTokensDict[player.TOKEN] = [player, request['ROOM_NAME'], True]
                roomsActivity[roomIndex] += 1
                player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "ROOM_NAME":str(request['ROOM_NAME'])})
                return
        player.send_data({"TYPE":"ROOM_JOIN_FAILD", "ERROR_MSG":"Room is at full capacity."})

    def activate_player(self, player):
        pass


    def suspend_player(self, player):
        pass


    def remove_player(self, player):
        self._players.remove(player)
        database.set_room_active_players(self.name, len(self._players))
        self.broadcast_event(player, {"TYPE":"ROOM_PLAYER_LEFT", "PLAYER_ID": player._server_id})
