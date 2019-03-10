import time
import json
from threading import Thread

class Room(Thread):
    ROOM_ID = 100
    def __init__(self, name, capacity, min_bet, max_bet):
        Thread.__init__(self)
        Room.ROOM_ID        += 1
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
            player.send_data({"TYPE":"ROOM_JOINED", "INFO":"DUMMY DATA"})
            self.broadcast_event(player, {"TYPE":"ROOM_PLAYER_JOIN"} + player.player_info)
