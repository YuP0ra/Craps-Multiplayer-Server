import json


""" ############### Loading the rooms json config file ############### """
configFile = None
with open('Statics/roomsInfo.json') as json_file:
    configFile = json.load(json_file)


""" ####################### Initializing Rooms ####################### """
crapsRooms, playersTokens = {}, {}
for room_name in configFile['rooms_name']:
    crapsRooms[room_name] = [], []


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


def ROOMS_FULL_INFO(client, request):
    client.send_data(getRoomsFullInfo())


def ROOMS_ACTIVITY_INFO(client, request):
    client.send_data(getRoomsActivePlayers())


def JOIN_ROOM_REQUEST(client, request):
    roomsActivity = configFile['active_players']
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
    roomsActivity = configFile['active_players']
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
