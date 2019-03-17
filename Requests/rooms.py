import time
import random
from Kernel.database import get, set

################################################################################
ROOM_CAPACITY = 5
crapsRooms = {}


################################################################################
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

def broadcastRequest(roomName, sender, request):
    for player in crapsRooms[roomName]:
        if not sender.TOKEN == player.TOKEN:
            player.send_data(request)

################################################################################
def onConnectionEnded(client):
    roomName = client.DATA.get('CURRENT_ROOM', None)
    if roomName is not None:
        crapsRooms[roomName].remove(client)


def JOIN_ROOM_REQUEST(player, request):
    roomsActivity = roomsInfo['active_players']
    roomIndex = roomsInfo['rooms_name'].index(request['ROOM_NAME'])

    if not player.TOKEN in token2player:           # The player is not in a room
        if roomsActivity[roomIndex] < ROOM_CAPACITY:
            roomsActivity[roomIndex] += 1
            token2player[player.TOKEN] = player
            room2token[request['ROOM_NAME']].append(player.TOKEN)
            player.DATA['LAST_JOINED_ROOM_NAME'] = request['ROOM_NAME']

            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS"})
            broadcastRequest(request['ROOM_NAME'], player.TOKEN, {"TYPE":"NEW_PLAYER_JOINED"})
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
        broadcastRequest(roomName, player.TOKEN, {"TYPE":"NEW_PLAYER_LEFT"})
    else:
        player.send_data({"TYPE":"ROOM_LEAVE_FAILD"})


def CRAPS_BET(client, request):
    broadcastRequest(client.DATA['LAST_JOINED_ROOM_NAME'], client.TOKEN, request)
