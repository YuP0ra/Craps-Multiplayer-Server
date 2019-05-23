import time
from Kernel.database import get, set



def onConnectionStarted(client):
    client.send_data({  "TYPE"      : "CONNECTED",
                        "SERVER_ID" : str(client.clientID)})

    client.DATA['CURRENT_ROOM'] = None
    client.DATA['INFO'] = ["Guest", 1, 50000, '']
    client.send_data({"TYPE": "GET_PLAYER_INFO"})

    print("Connection Started: ", client.address)


def onConnectionTimeout(client):
    client.send_data({"TYPE": "GET_PLAYER_INFO"})


def onConnectionEnded(client):
    print("Connection Terminated: ", client.address)


def PING(client, request):
    client.send_data(request)


def SET_TOKEN(client, request):
    client.TOKEN = request['TOKEN']
    client.send_data({"TYPE": "TOKEN_SET_SUCCESS", "TOKEN": client.TOKEN})


def PLAYER_INFO(client, request):
    client.DATA['INFO'] = [request.get('NAME', 'Guest'), request.get('LEVEL', 1), request.get('MONEY', 50000), request.get('IMGURL', '')]
