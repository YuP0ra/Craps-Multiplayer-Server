import time
import random
import secrets
from threading import Thread
from Kernel.database import get, set
from Utils.CrapsClasses import CrapsTable, CrapsBot

################################################################################
tokensDB, crapsRooms, crapsRoomsTable, roomAllowedBets = {}, {}, {}, {}


################################################################################
def init():
    for i, roomName in enumerate(get('roomsInfo')['ROOMS_NAME']):
        crapsRooms[roomName] = []
        crapsRoomsTable[roomName] = CrapsTable(get('roomsInfo')['ROOMS_CHIPS'][i])
        roomAllowedBets[roomName] = get('roomsInfo')['ROOMS_CHIPS'][i]
        Thread(target=runRoom,
               args=(roomName, crapsRooms[roomName], crapsRoomsTable[roomName])
               ).start()
    set('crapsRooms', crapsRooms)

def runRoom(roomName, roomPlayers, table):
    ROUND_TIME, CALCULATIONS_TIME = 15, 1

    bot = CrapsBot(table.validChips)
    bot.joinRoom(roomName, JOIN_ROOM_REQUEST)

    while True:
        initTime = time.time()
        ############ Betiing Starts
        if len(roomPlayers) == 1:
            table.ClearTableBets()
            bot.fireupNewBot()
            table.Reset()
            time.sleep(3)
            continue

        for player in roomPlayers:
            player.send_data({
                                "TYPE"      :"ROUND_STARTED",
                                "COMEROLL"  : str(table.isComeOutRoll),
                                "MARKER"    : str(table.marker),
                                "ROUND_ID"  : str(table.roundID)
                             })

        ############ Betiing Ends
        for i in range(ROUND_TIME):
            if i in [5, 9]:
                bot.placeBet(table.isComeOutRoll, CRAPS_BET)

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
                                "TYPE"  : "DICE_ROLLED",
                                "DICE1" : str(dice1),
                                "DICE2" : str(dice2)
                             })

        table.roundID += 1

        finalResult = {     "TYPE"      : "ROUND_RESULT",
                            "TOTAL"     : str(table.roundResultsTotalWins),
                            "TOTALBETS" : str(table.TableTotalBetsList()),
                            "WIN"       : str(table.roundResultsWIN),
                            "PUSH"      : str(table.roundResultsPUSH),
                            "LOSE"      : str(table.roundResultsLOSE),
                            "MOVE"      : str(table.roundResultsMOVE),
                            "COMEROLL"  : str(table.isComeOutRoll),
                            "MARKER"    : str(table.marker)
                         }

        for player in roomPlayers:
            player.send_data(finalResult)

        CALCULATIONS_TIME = 5 + len(table.roundResultsWIN) * .25
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


################################################################################
def onConnectionEnded(client):
    roomName = client.DATA.get('CURRENT_ROOM', None)
    if roomName is not None:
        if client in crapsRooms[roomName]:
            crapsRooms[roomName].remove(client)
        crapsRoomsTable[roomName].RemovePlayer(client.DATA['RID'])
        broadcastRequest(client, {  "TYPE"  : "NEW_PLAYER_LEFT",
                                    "TOKEN" : str(client.DATA['RID'])})


def JOIN_ROOM_REQUEST(player, request):
    if request['ROOM_NAME'] not in crapsRooms:
        player.send_data({"TYPE":"ROOM_JOIN_FAILD"})
        return

    if 'SERVERID' not in request:
        player.send_data({"TYPE":"ROOM_JOIN_FAILD"})
        return

    if request['SERVERID'] == "" or request['SERVERID'] == "0":
        player.send_data({"TYPE":"ROOM_JOIN_FAILD"})
        return

    LEAVE_ROOM_REQUEST(player, None)

    if player in crapsRooms[request['ROOM_NAME']]:
        player.send_data({"TYPE":"ROOM_JOIN_FAILD"})
        return


    player.DATA['INFO'][3] = request.get('FACEID', '')
    if player.DATA.get('CURRENT_ROOM', None) is None:
        if len(crapsRooms[request['ROOM_NAME']]) < 4:
            player.DATA['RID'] = secrets.token_hex(10)
            player.DATA['CURRENT_ROOM'] = request['ROOM_NAME']
            crapsRooms[request['ROOM_NAME']].append(player)

            player.send_data({  "TYPE":"ROOM_JOIN_SUCCESS",
                                "TOKEN"     : str(player.DATA['RID']),
                                "ROOM_NAME" : str(request['ROOM_NAME']),
                                "CHIPS_ARR" : str(roomAllowedBets[request['ROOM_NAME']]),
                                "ROUND_ID"  : str(crapsRoomsTable[request['ROOM_NAME']].roundID)
                              })

            player.send_data(crapsRoomsTable[request['ROOM_NAME']].MarkerInfo())
            tokensDB[player.TOKEN] = request['ROOM_NAME']

            broadcastRequest(player, {  "TYPE"  : "NEW_PLAYER_JOINED",
                                        "TOKEN" : str(player.DATA['RID']),
                                        "NAME"  : str(player.DATA['INFO'][0]),
                                        "LEVEL" : str(player.DATA['INFO'][1]),
                                        "MONEY" : str(player.DATA['INFO'][2]),
                                        "IMAGE" : str(player.DATA['INFO'][3])})
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
            broadcastRequest(player, {  "TYPE"  : "NEW_PLAYER_LEFT",
                                        "TOKEN" : str(player.DATA['RID'])})
            player.DATA['CURRENT_ROOM'] = None
            tokensDB.pop(player.TOKEN, None)
        except Exception as e:
            pass


def ROOM_PLAYERS_INFO(player, request):
    roomName = player.DATA.get('CURRENT_ROOM', None)
    if roomName in crapsRooms:
        players = [player] + [x for x in crapsRooms[roomName] if x != player]

        tokens  = [str(p.DATA['RID']) for p in players]
        names   = [str(p.DATA['INFO'][0]) for p in players]
        levels  = [str(p.DATA['INFO'][1]) for p in players]
        moneies = [str(p.DATA['INFO'][2]) for p in players]
        fbids   = [str(p.DATA['INFO'][3]) for p in players]

        player.send_data({"TYPE":   "ROOM_PLAYERS_INFO",
                                    "TOKEN"     : str(tokens),
                                    "NAME"      : str(names),
                                    "LEVEL"     : str(levels),
                                    "MONEY"     : str(moneies),
                                    "IMAGES"    : str(fbids),
                                    "MARKER"    : str(crapsRoomsTable[roomName].marker),
                                    "ROUND_ID"  : str(crapsRoomsTable[roomName].roundID),
                                    "COMEROLL"  : str(crapsRoomsTable[roomName].isComeOutRoll),
                                    "BETS"      : str(crapsRoomsTable[roomName].TableBetsList())
                        })


def ROOM_TABLE_INFO(player, request):
    roomName = player.DATA.get('CURRENT_ROOM', None)
    if roomName in crapsRooms:
        player.send_data(crapsRoomsTable[roomName].JsonTableInfo())


def PLAYER_BETS(player, request):
    roomName = player.DATA.get('CURRENT_ROOM', None)
    if roomName in crapsRoomsTable:
        player.send_data(crapsRoomsTable[roomName].JsonPlayerBets(request["TARGET_TOKEN"]))


def CRAPS_BET(client, request):
    request['TOKEN'] = client.DATA['RID']
    roomName = client.DATA.get('CURRENT_ROOM', None)

    if roomName in crapsRoomsTable:
        if crapsRoomsTable[roomName].updateTableBet(client.DATA['RID'], request):
            client.DATA['INFO'][2] = str(int(client.DATA['INFO'][2]) - int(request['AMOUNT']))
            client.send_data({"TYPE"       : "BET_SUCCESS",
                              "BETTING_ON" : str(request['BETTING_ON']),
                              "AMOUNT"     : str(request['AMOUNT'])
                              })
            broadcastRequest(client, request)
        else:
            client.send_data({"TYPE"       : "BET_ERROR",
                              "BETTING_ON" : str(request['BETTING_ON']),
                              "AMOUNT"     : str(request['AMOUNT'])
                              })


def CRAPS_CLEAR(client, request):
    request['TOKEN'] = client.DATA['RID']
    roomName = client.DATA.get('CURRENT_ROOM', None)
    if roomName in crapsRoomsTable:
        if crapsRoomsTable[roomName].clearTableBet(client.DATA['RID'], request):
            client.send_data({"TYPE"       : "CLEAR_SUCCESS",
                              "BETTING_ON" : str(request['BETTING_ON'])
                              })
            broadcastRequest(client, request)


def SWITCH_SCREEN_MODE(client, request):
    request['TOKEN'] = client.DATA['RID']
    roomName = client.DATA.get('CURRENT_ROOM', None)
    if roomName in crapsRoomsTable:
        crapsRoomsTable[roomName].ClearPlayerBets(client.DATA['RID'])
        broadcastRequest(client, request)


def SYNC(client, request):
    request['TOKEN'] = client.DATA['RID']
    broadcastRequest(client, request)


################################################################################
set('tokensDB', tokensDB)
