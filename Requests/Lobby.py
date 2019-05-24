import json
from Kernel.database import get, set


################################################################################
roomsInfo = None



################################################################################
def GET_LOBBY_ROOMS(player, request):
    crapsRooms = get('crapsRooms')
    roomsInfo['active_players'] = [len(crapsRooms[room]) for room in crapsRooms]
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
