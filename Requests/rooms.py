import json


""" ############### Loading the rooms json config file ############### """
configFile = None
with open('Statics/roomsInfo.json') as json_file:
    config_file = json.load(json_file)


""" ####################### Initializing Rooms ####################### """
crapsRooms = {}
for room_name in config_file['rooms_name']:
    crapsRooms[room_name] = []


def getRoomsFullInfo():
    return {
            "TYPE"  : "FULL_ROOMS_INFO",
            "NAMES" : config_file['rooms_name'],
            "MINBET": config_file['rooms_min_bet'],
            "MAXBET": config_file['rooms_max_bet'],
            "ACTIVE": config_file['active_players']
            }

def getRoomsActivePlayers():
    return {
            "TYPE"  : "ACTIVIY_ROOMS_INFO",
            "ACTIVE": config_file['active_players']
            }


def ROOMS_FULL_INFO(client, request):
    client.send(getRoomsFullInfo())


def ROOMS_ACTIVITY_INFO(client, request):
    client.send(getRoomsActivePlayers())


def JOIN_ROOM_REQUEST(client, request):
    roomsActivity = config_file['active_players']
    roomIndex = configFile['rooms_name'].index(request['ROOM_NAME'])
    playerTokenList, playerActiveList = crapsRooms[request['ROOM_NAME']]

    if not client.TOKEN in playerTokenList:     #The player is not in the room
        if roomsActivity[roomIndex] < 5:
            playerTokenList.append(client.TOKEN)
            playerActiveList.append(True)
            roomsActivity[roomIndex] += 1
    else:
        index = playerTokenList.index(client.TOKEN)
        playerActiveList[index] = True


def LEAVE_ROOM_REQUEST(client, request):
    roomsActivity = config_file['active_players']
    roomIndex = configFile['rooms_name'].index(request['ROOM_NAME'])
    playerTokenList, playerActiveList = crapsRooms[request['ROOM_NAME']]

    if not client.TOKEN in playerTokenList:     #The player is not in the room
        if roomsActivity[roomIndex] < 5:
            playerTokenList.append(client.TOKEN)
            playerActiveList.append(True)
            roomsActivity[roomIndex] += 1
    else:
        index = playerTokenList.index(client.TOKEN)
        playerActiveList[index] = True
