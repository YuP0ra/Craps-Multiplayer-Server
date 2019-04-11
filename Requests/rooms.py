import time
import random
import secrets
from threading import Thread
from Kernel.database import get, set
from Utils.CrapsClasses import CrapsTable

################################################################################
tokensDB, crapsRooms, crapsRoomsTable = {}, {}, {}


################################################################################
def init():
    for roomName in get('roomsInfo')['rooms_name']:
        crapsRooms[roomName] = []
        crapsRoomsTable[roomName] = CrapsTable()
        Thread(target=runRoom,
               args=(crapsRooms[roomName], crapsRoomsTable[roomName],)).start()


def runRoom(roomPlayers, table):
    ROUND_TIME, CALCULATIONS_TIME = 15, 10

    while True:
        initTime = time.time()
        ############ Betiing Starts
        if len(roomPlayers) == 0:
            table.Reset()
            time.sleep(3)
            continue
        else:
            table.roundID += 1
            for player in roomPlayers:
                player.send_data({
                                    "TYPE"      :"ROUND_STARTED",
                                    "ROUND_ID"  :str(table.roundID)
                                 })
        ############ Betiing Ends

        for i in range(ROUND_TIME):
            for player in roomPlayers:
                player.send_data({
                                    "TYPE"  :"CLOCK_UPDATE",
                                    "CLOCK" :str(ROUND_TIME - i - 1)
                                 })
                initTime = sleepExatcly(initTime, 1)

        ############ Animation Starts
        if len(roomPlayers) == 0:
            continue

        dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
        table.Roll(dice1, dice2)
        for player in roomPlayers:
            player.send_data({
                                "TYPE"  :"DICE_ROLLED",
                                "DICE1" :str(dice1),
                                "DICE2" :str(dice2)
                             })

            player.send_data({
                                "TYPE"  : "ROUND_RESULT",
                                "WIN"   : str(table.roundResultsWIN),
                                "PUSH"  : str(table.roundResultsPUSH),
                                "LOSE"  : str(table.roundResultsLOSE),
                                "MOVE"  : str(table.roundResultsMOVE),
                                "TOTAL" : str(table.roundResultsTotalWins),
                                "NEXT"  :str(table.roundNextBets)
                             })

            player.send_data(table.MarkerInfo())

        CALCULATIONS_TIME = 3 + len(table.roundResultsWIN) *.24 + len(table.roundResultsLOSE) * .24
        ############ Animation Ends

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


################################################################################
def onConnectionEnded(client):
    roomName = client.DATA.get('CURRENT_ROOM', None)
    if roomName is not None:
        if client in crapsRooms[roomName]:
            crapsRooms[roomName].remove(client)
        crapsRoomsTable[roomName].RemovePlayer(client.DATA['RID'])
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
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "TOKEN": player.DATA['RID'], "ROOM_NAME": request['ROOM_NAME']})
            player.send_data(crapsRoomsTable[request['ROOM_NAME']].MarkerInfo())
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
            if player in crapsRooms[player.DATA['CURRENT_ROOM']]:
                crapsRooms[player.DATA['CURRENT_ROOM']].remove(player)
            crapsRoomsTable[player.DATA['CURRENT_ROOM']].RemovePlayer(player.DATA['RID'])
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


def PLAYER_BETS(player, request):
    roomNmae = player.DATA.get('CURRENT_ROOM', None)
    if roomNmae in crapsRoomsTable:
        player.send_data(crapsRoomsTable[roomNmae].JsonPlayerBets(request["TARGET_TOKEN"]))


def CRAPS_BET(client, request):
    request['TOKEN'] = client.DATA['RID']
    roomNmae = client.DATA.get('CURRENT_ROOM', None)

    if roomNmae in crapsRoomsTable:
        if crapsRoomsTable[roomNmae].updateTableBet(client.DATA['RID'], request):
            broadcastRequest(client, request)
        else:
            client.send_data({"TYPE":   "BET_ERROR",
                                        "BETTING_ON" : request['BETTING_ON'],
                                        "AMOUNT"  : request['AMOUNT']
                              })



################################################################################
set('tokensDB', tokensDB)
