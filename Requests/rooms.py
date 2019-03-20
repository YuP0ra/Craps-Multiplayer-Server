import time
import random
import secrets
from threading import Thread
from Kernel.database import get, set

################################################################################
class CrapsTable:
    def __init__(self,):
        self.marker = 0
        self.ridBets = {}
        self.isComeOutRoll = True

    def Roll(self, dice1, dice2):
        totalDices = dice1 + dice2
        if self.isComeOutRoll and totalDices in [4, 5, 6, 8, 9, 10]:
            self.marker = totalDices
            self.isComeOutRoll = False
        elif totalDices == 7 or totalDices == self.marker:
            self.marker = 0
            self.isComeOutRoll = True

    def Reset(self,):
            self.marker = 0
            self.isComeOutRoll = True

    def UpdateTableBet(self, rid, bet, amount):
        if rid not in self.ridBets:         self.ridBets[rid] = {}
        if bet not in self.ridBets[rid]:    self.ridBets[rid][bet] = 0
        self.ridBets[rid][bet] +=           amount

    def JsonTableInfo(self):
        ridList = [str(rid) for rid in self.ridBets]
        return {"TYPE"      : "TABLE_INFO",
                "MARKER"    : str(self.marker),
                "RID_COUNT" : str(len(ridList)),
                "RIDS_LIST" : ridList,
                "LIST_DICT" : [str(self.ridBets[rid]) for rid in self.ridBets]
                }


################################################################################
tokensDB, crapsRooms, crapsRoomsTable = {}, {}, {}


################################################################################
def init():
    for roomName in get('roomsInfo')['rooms_name']:
        crapsRooms[roomName] = []
        crapsRoomsTable[roomName] = CrapsTable()
        Thread(target=runRoom, args=(roomName,)).start()


def runRoom(roomName):
    ROUND_TIME, CALCULATIONS_TIME = 15, 10

    while True:
        initTime = time.time()
        ############ Betiing Starts
        if len(crapsRooms[roomName]) == 0:
            crapsRoomsTable[roomName].Reset()
            time.sleep(1)
            continue
        else:
            for player in crapsRooms[roomName]:
                player.send_data({"TYPE"  :"ROUND_STARTED"})
        ############ Betiing Ends

        initTime = sleepExatcly(initTime, ROUND_TIME)

        ############ Animation Starts
        if len(crapsRooms[roomName]) == 0:
            continue

        dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
        crapsRoomsTable[roomName].Roll(dice1, dice2)
        for player in crapsRooms[roomName]:
            player.send_data({
                                "TYPE"  :"DICE_ROLLED",
                                "DICE1" :str(dice1),
                                "DICE2" :str(dice2)
                             })
        ############ Animation Ends
        initTime = sleepExatcly(initTime, CALCULATIONS_TIME)

def sleepExatcly(initTime, amount):
    deltaTime = time.time() - initTime
    if deltaTime < amount:
        time.sleep(amount - deltaTime)
    return time.time()

def broadcastRequest(sender, request):
    roomName = sender.DATA.get('CURRENT_ROOM', None)
    print("Broadcasting request ", request["TYPE"])
    if roomName is not None:
        for player in crapsRooms[roomName]:
            if not sender.TOKEN == player.TOKEN:
                player.send_data(request)
            elif request["TYPE"] == "CRAPS_BET":
                player.send_data(request)
        sender.send_data({"TYPE": "BROADCAST_SUCCESS", "BROADCAST_TYPE": request['TYPE']})


################################################################################
def onConnectionEnded(client):
    roomName = client.DATA.get('CURRENT_ROOM', None)
    if roomName is not None:
        crapsRooms[roomName].remove(client)
        get('decrementRoomActivity')(roomName)
        broadcastRequest(client, {  "TYPE"  : "NEW_PLAYER_LEFT",
                                    "TOKEN" : client.DATA['RID']})


def JOIN_ROOM_REQUEST(player, request):
    if request['ROOM_NAME'] not in crapsRooms:
        player.send_data({"TYPE":"ROOM_JOIN_FAILD"})
        return

    if player.DATA.get('CURRENT_ROOM', None) is None:
        if len(crapsRooms[request['ROOM_NAME']]) < 4:

            player.DATA['RID'] = secrets.token_hex(10)
            player.DATA['CURRENT_ROOM'] = request['ROOM_NAME']
            get('incrementRoomActivity')(request['ROOM_NAME'])
            crapsRooms[request['ROOM_NAME']].append(player)
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "TOKEN": player.DATA['RID']})
            tokensDB[player.TOKEN] = request['ROOM_NAME']

            broadcastRequest(player, {  "TYPE"  : "NEW_PLAYER_JOINED",
                                        "TOKEN" : player.DATA['RID'],
                                        "NAME"  : str(player.DATA['INFO'][0]),
                                        "LEVEL" : str(player.DATA['INFO'][1]),
                                        "MONEY" : str(player.DATA['INFO'][2])})
        else:
            player.send_data({"TYPE":"ROOM_JOIN_FAILD"})
    else:
        player.send_data({"TYPE":"ROOM_JOIN_FAILD"})


def LEAVE_ROOM_REQUEST(player, request):
    if player.DATA.get('CURRENT_ROOM', None) in crapsRooms:
        try:
            crapsRooms[player.DATA['CURRENT_ROOM']].remove(player)
            get('decrementRoomActivity')(player.DATA['CURRENT_ROOM'])
            broadcastRequest(player, {  "TYPE"  : "NEW_PLAYER_LEFT",
                                        "TOKEN" : player.DATA['RID']})
            player.DATA['CURRENT_ROOM'] = None
            tokensDB.pop(player.TOKEN, None)
        except Exception as e:
            pass


def ROOM_PLAYERS_INFO(player, request):
    roomNmae = player.DATA.get('CURRENT_ROOM', None)
    if roomNmae in crapsRooms:
        players = [x for x in crapsRooms[roomNmae] if x != player]

        tokens  = [p.DATA['RID'] for p in players]
        names   = [str(p.DATA['INFO'][0]) for p in players]
        levels  = [str(p.DATA['INFO'][1]) for p in players]
        moneies = [str(p.DATA['INFO'][2]) for p in players]

        player.send_data({"TYPE":   "ROOM_PLAYERS_INFO",
                                    "TOKEN" : tokens,
                                    "NAME"  : names,
                                    "LEVEL" : levels,
                                    "MONEY" : moneies })


def ROOM_TABLE_INFO(player, request):
    roomNmae = player.DATA.get('CURRENT_ROOM', None)
    if roomNmae in crapsRoomsTable:
        player.send_data(crapsRoomsTable[roomNmae].JsonTableInfo())


def CRAPS_BET(client, request):
    request['TOKEN'] = client.DATA['RID']
    broadcastRequest(client, request)

    roomNmae = client.DATA.get('CURRENT_ROOM', None)
    if roomNmae in crapsRoomsTable:
        crapsRoomsTable[roomNmae].UpdateTableBet(client.DATA['RID'], request['BETTING_ON'], int(request['AMOUNT']))


################################################################################
set('tokensDB', tokensDB)
