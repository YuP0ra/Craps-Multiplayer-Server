import json
import time
import random

from Kernel.database import get, set


""" ############### Loading the rooms json config file ############### """
rommsToPlayerTokenDict = {}
configFile, ROOM_CAPACITY = None, 5
with open('Statics/roomsInfo.json') as json_file:
    configFile = json.load(json_file)

for room_name in configFile['rooms_name']:
    rommsToPlayerTokenDict[room_name] = []

def getRoomsFullInfo():
    return {
            "TYPE"  : "FULL_ROOMS_INFO",
            "NAMES" : configFile['rooms_name'],
            "MINBET": configFile['rooms_min_bet'],
            "MAXBET": configFile['rooms_max_bet'],
            "ACTIVE": configFile['active_players']
            }

def getRoomsActivePlayers():
    return {
            "TYPE"  : "ACTIVIY_ROOMS_INFO",
            "ACTIVE": configFile['active_players']
            }


""" ######################## players Runtime ######################## """
playersTokensDict = {}                   #"{TOKEN}: (socket, room, active)
def run():
    ROUND_TIME = 15
    while True:
        initTime = time.time()

        for socket, room, status in playersTokensDict:
            if active:
                socket.send_data({"TYPE":"NEW_ROUND_STARTED"})

        initTime = sleepExatcly(initTime, ROUND_TIME)

        for socket, room, status in playersTokensDict:
            if active:
                socket.send_data({"TYPE":"DICE_ROLLED", "DICE1":str(random.randint(1, 6)), "DICE2":str(random.randint(1, 6))})

        initTime = sleepExatcly(initTime, 5)

def sleepExatcly(initTime, amount):
    deltaTime = time.time() - initTime
    if deltaTime < amount:
        time.sleep(amount - deltaTime)
    return time.time()

""" ####################### Requests Handling ####################### """
def onConnectionEnded(client):
    if client.TOKEN in playersTokensDict:
        playersTokensDict[client.TOKEN][2] = False


def ROOMS_FULL_INFO(player, request):
    player.send_data(getRoomsFullInfo())


def ROOMS_ACTIVITY_INFO(player, request):
    player.send_data(getRoomsActivePlayers())


def JOIN_ROOM_REQUEST(player, request):
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


def LEAVE_ROOM_REQUEST(player, request):
    if player.TOKEN in playersTokensDict:                 #The player is in a room
        roomsActivity = configFile['active_players']
        roomIndex = configFile['rooms_name'].index(playersTokensDict[player.TOKEN][1])
        del playersTokensDict[player.TOKEN]
        roomsActivity[roomIndex] -= 1
        player.send_data({"TYPE":"ROOM_LEAVE_SUCCESS"})
    else:
        player.send_data({"TYPE":"ROOM_LEAVE_FAILD"})


def CRAPS_BET(client, request):
    pass
