import time
import random
import secrets
from Kernel.database import get, set

################################################################################
tokensDB, crapsRooms, crapsRoomsTable = {}, {}, {}


################################################################################
def run():
    ROUND_TIME, CALCULATIONS_TIME = 15, 10

    while True:
        initTime = time.time()
        ############################################ CODE START HERE
        ############ Betiing Starts
        for roomName in crapsRooms:
            dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
            if len(crapsRooms[roomName]) == 0:
                clearRoomTable()
            else:
                for player in crapsRooms[roomName]:
                    player.send_data({"TYPE"  :"ROUND_STARTED"})
        ############ Betiing Ends

        initTime = sleepExatcly(initTime, ROUND_TIME)

        ############ Animation Starts
        for roomName in crapsRooms:
            for player in crapsRooms[roomName]:
                player.send_data({
                                    "TYPE"  :"DICE_ROLLED",
                                    "DICE1" :str(dice1),
                                    "DICE2" :str(dice2)
                                 })
        ############ Animation Ends
        ############################################ CODE END HERE
        initTime = sleepExatcly(initTime, CALCULATIONS_TIME)

def sleepExatcly(initTime, amount):
    deltaTime = time.time() - initTime
    if deltaTime < amount:
        time.sleep(amount - deltaTime)
    return time.time()

def broadcastRequest(sender, request):
    roomName = sender.DATA.get('CURRENT_ROOM', None)
    if roomName is not None:
        for player in crapsRooms[roomName]:
            if not sender.TOKEN == player.TOKEN:
                player.send_data(request)
        sender.send_data({"TYPE": "BROADCAST_SUCCESS", "BROADCAST_TYPE": request['TYPE']})

def clearRoomTable():
    crapsRoomsTable[roomNmae] = {}

def updateRoomTable(roomName, rid, betName, amount):
    if roomName not in crapsRoomsTable:
        crapsRoomsTable[roomName] = {}

    if betName not in crapsRoomsTable[roomName]:
        crapsRoomsTable[roomName][betName] = 0

    crapsRoomsTable[roomName][betName] += amount

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
        crapsRooms[request['ROOM_NAME']] = []

    if player.DATA.get('CURRENT_ROOM', None) is None:
        if len(crapsRooms[request['ROOM_NAME']]) < 4:

            player.DATA['RID'] = secrets.token_hex(10)
            player.DATA['CURRENT_ROOM'] = request['ROOM_NAME']
            get('incrementRoomActivity')(request['ROOM_NAME'])
            crapsRooms[request['ROOM_NAME']].append(player)
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS"})
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
        crapsRooms[player.DATA['CURRENT_ROOM']].remove(player)
        get('decrementRoomActivity')(player.DATA['CURRENT_ROOM'])
        broadcastRequest(player, {  "TYPE"  : "NEW_PLAYER_LEFT",
                                    "TOKEN" : player.DATA['RID']})
        player.DATA['CURRENT_ROOM'] = None
        tokensDB.pop(player.TOKEN, None)


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
    if roomNmae in crapsRooms:
        bets    = [bn for bn in crapsRoomsTable[roomName]]
        amount  = [crapsRoomsTable[roomName][bn] for bn in crapsRoomsTable[roomName]]

        player.send_data({"TYPE":   "ROOM_TABLE_INFO",
                                    "BETS"  : bets,
                                    "AMOUNT": amount })

def CRAPS_BET(client, request):
    client['TOKEN'] = client['RID']
    broadcastRequest(client, request)
    updateRoomTable(client['CURRENT_ROOM'], client['RID'], request['BETTING_ON'], request['AMOUNT'])

################################################################################
set('tokensDB', tokensDB)
