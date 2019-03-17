import time

from Kernel.database import get, set


playersDict, playersInfoDict = {}, {}
set('playersDict', playersDict)


def onConnectionStarted(client):
    print("Connection Started: ", client.address)
    client.send_data({"TYPE": "CONNECTED", "TOKEN":client.TOKEN})


def onConnectionTimeout(client):
    if client.TOKEN not in playersInfoDict:
        client.send_data({"TYPE": "GET_PLAYER_INFO"})


def onConnectionEnded(client):
    playersDict.pop(client.TOKEN, None)
    playersInfoDict.pop(client.TOKEN, None)
    print("Connection Terminated: ", client.address)


def PLAYER_INFO(client, request):
    client.TOKEN = request['TOKEN']

    if client.TOKEN not in playersInfoDict:
        playersDict[client.TOKEN] = client
        playersInfoDict[client.TOKEN] = [request['TOKEN'], request['NAME'], request['LEVEL'], request['MONEY']]

    print("PLAYER INFO: ", playersInfoDict[client.TOKEN])


def DEFAULT(client, request):
    print("DEFAULT: ", request)
