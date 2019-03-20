import json
from Kernel.database import get, set


################################################################################
roomsInfo = None


################################################################################
def activePlayersInRoom(roomName):
    return roomsInfo['active_players'][roomsInfo['rooms_name'].index(roomName)]

def incrementRoomActivity(roomName):
    roomIndex = roomsInfo['rooms_name'].index(roomName)
    roomsActivity = roomsInfo['active_players']
    if activePlayersInRoom(roomName) < 5:
        roomsActivity[roomIndex] += 1

def decrementRoomActivity(roomName):
    roomIndex = roomsInfo['rooms_name'].index(roomName)
    roomsActivity = roomsInfo['active_players']
    if activePlayersInRoom(roomName) > 0:
        roomsActivity[roomIndex] -= 1


################################################################################
def SET_TOKEN(client, request):
    if get('tokensDB').get(request['TOKEN'], None) is not None:
        client.send_data({
                            "TYPE":         "REJOIN_ROOM",
                            "ROOM_NAME":    get('tokensDB')[request['TOKEN']]
                         })


def GET_LOBBY_ROOMS(player, request):
    player.send_data({
                        "TYPE"  : "LOBBY_ROOMS",
                        "NAMES" : roomsInfo['rooms_name'],
                        "MINBET": roomsInfo['rooms_min_bet'],
                        "MAXBET": roomsInfo['rooms_max_bet'],
                        "ACTIVE": roomsInfo['active_players']
                    })


def GET_LOBBY_ACTIVIY(player, request):
    player.send_data({
                        "TYPE"  : "LOBBY_ROOMS_ACTIVITY",
                        "ACTIVE": roomsInfo['active_players']
                    })


################################################################################
with open('Statics/roomsInfo.json') as json_file:
    roomsInfo = json.load(json_file)

set('roomsInfo', roomsInfo)
set('activePlayersInRoom', activePlayersInRoom)
set('incrementRoomActivity', incrementRoomActivity)
set('decrementRoomActivity', decrementRoomActivity)
