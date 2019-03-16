import time
newPlayersList, playersInfoDict = [], {}


def onConnectionStarted(client):
    print("Connection Started: ", client.address)

    newPlayersList.append(client)
    client.send_data({"TYPE": "CONNECTED", "TOKEN":client.TOKEN})


def onConnectionTimeout(client):
    if client.TOKEN not in playersInfoDict:
        client.send_data({"TYPE": "GET_PLAYER_INFO"})


def onConnectionEnded(client):
    print("Connection Terminated: ", client.address)


def PLAYER_INFO(client, request):
    client.TOKEN = request['TOKEN']

    if client.TOKEN not in playersInfoDict:
        playersInfoDict[client.TOKEN] = [request['TOKEN'], request['NAME'], request['LEVEL'], request['MONEY']]

    print("PLAYER INFO: ", playersInfoDict[client.TOKEN])


def DEFAULT(client, request):
    print(request)
