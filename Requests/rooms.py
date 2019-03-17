import json
import time
import random

from Kernel.database import get, set


""" ############### Loading the rooms json config file ############### """
token2player, room2token = {}, {}
roomsInfo, ROOM_CAPACITY = None, 5
with open('Statics/roomsInfo.json') as json_file:
    roomsInfo = json.load(json_file)

for room_name in roomsInfo['rooms_name']:
    room2token[room_name] = []

def getRoomsFullInfo():
    return {
            "TYPE"  : "FULL_ROOMS_INFO",
            "NAMES" : roomsInfo['rooms_name'],
            "MINBET": roomsInfo['rooms_min_bet'],
            "MAXBET": roomsInfo['rooms_max_bet'],
            "ACTIVE": roomsInfo['active_players']
            }

def getRoomsActivePlayers():
    return {
            "TYPE"  : "ACTIVIY_ROOMS_INFO",
            "ACTIVE": roomsInfo['active_players']
            }


""" ######################## players Runtime ######################## """
def run():
    ROUND_TIME = 15
    while True:
        initTime = time.time()
        ############################################ CODE START HERE


        ############################################ CODE END HERE
        initTime = sleepExatcly(initTime, ROUND_TIME)

def sleepExatcly(initTime, amount):
    deltaTime = time.time() - initTime
    if deltaTime < amount:
        time.sleep(amount - deltaTime)
    return time.time()


""" ####################### Requests Handling ####################### """
def onConnectionEnded(client):
    room_name = token2player.pop(client.TOKEN, None)
    if room_name is not None:
        room2token[client.DATA['LAST_JOINED_ROOM_NAME']].remove(client.TOKEN)

def ROOMS_FULL_INFO(player, request):
    player.send_data(getRoomsFullInfo())


def ROOMS_ACTIVITY_INFO(player, request):
    player.send_data(getRoomsActivePlayers())


def JOIN_ROOM_REQUEST(player, request):
    roomsActivity = roomsInfo['active_players']
    roomIndex = roomsInfo['rooms_name'].index(request['ROOM_NAME'])

    if not player.TOKEN in token2player:           # The player is not in a room
        if roomsActivity[roomIndex] < ROOM_CAPACITY:
            roomsActivity[roomIndex] += 1
            token2player[player.TOKEN] = player
            room2token[request['ROOM_NAME']].append(player.TOKEN)
            player.DATA['LAST_JOINED_ROOM_NAME'] = request['ROOM_NAME']
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "ROOM_NAME":str(request['ROOM_NAME'])})
            return
    player.send_data({"TYPE":"ROOM_JOIN_FAILD", "ERROR_MSG":"Room is at full capacity."})


def LEAVE_ROOM_REQUEST(player, request):
    if player.TOKEN in token2player:                 #The player is in a room
        roomsActivity = roomsInfo['active_players']
        roomName = player.DATA['LAST_JOINED_ROOM_NAME']
        roomIndex = roomsInfo['rooms_name'].index(roomName)

        roomsActivity[roomIndex] -= 1
        token2player.pop(player.TOKEN, None)
        room2token[roomName].remove(player.TOKEN)
        player.send_data({"TYPE":"ROOM_LEAVE_SUCCESS"})
    else:
        player.send_data({"TYPE":"ROOM_LEAVE_FAILD"})


def CRAPS_BET(client, request):
    pass
