import json, time


""" ############### Loading the rooms json config file ############### """
configFile, ROOM_CAPACITY = None, 5
with open('Statics/roomsInfo.json') as json_file:
    configFile = json.load(json_file)


""" ####################### Initializing Rooms ####################### """
playersTokensDict = {}                  #"{TOKEN}: (socket, room, status)


def run():
    while True:
        initTime = time.time()


        """ Calculate deltaTime to make sure all rooms are clocked every exatly 1 second """
        deltaTime = time.time() - initTime
        if deltaTime < 1:
            time.sleep(1 - deltaTime)
        print(deltaTime)


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
            playersTokensDict[player.TOKEN] = (player, request['ROOM_NAME'], True)
            roomsActivity[roomIndex] += 1
            player.send_data({"TYPE":"ROOM_JOIN_SUCCESS", "ROOM_NAME":str(request['ROOM_NAME'])})
            return
    player.send_data({"TYPE":"ROOM_JOIN_FAILD", "ERROR_MSG":"Room is at full capacity."})


def LEAVE_ROOM_REQUEST(player, request):
    if player.TOKEN in playerTokenList:                 #The player is in a room
        roomsActivity = configFile['active_players']
        roomIndex = configFile['rooms_name'].index(playerTokenList[player.TOKEN][1])
        del playerTokenList[player.TOKEN]
        roomsActivity[roomIndex] -= 1
        player.send_data({"TYPE":"ROOM_LEAVE_SUCCESS"})
    else:
        player.send_data({"TYPE":"ROOM_LEAVE_FAILD"})
