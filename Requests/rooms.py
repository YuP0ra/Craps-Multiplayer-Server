import json


""" ############### Loading the settings json config file ############### """
config_file = None
with open('Statics/settings.json') as json_file:
    config_file = json.load(json_file)


""" ####################### Loading rooms info ########################## """
rooms_active_players = [0] * len(config_file['rooms_name'])

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
