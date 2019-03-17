import time
from Kernel.database import get, set


def onConnectionStarted(client):
    client.send_data({"TYPE": "CONNECTED"})
    client.DATA['Info'] = ["Guest", 1, 50000]
    print("Connection Started: ", client.address)
    client.send_data({"TYPE": "GET_PLAYER_INFO"})


def onConnectionTimeout(client):
    client.send_data({"TYPE": "GET_PLAYER_INFO"})


def onConnectionEnded(client):
    print("Connection Terminated: ", client.address)


def SET_TOKEN(client, request):
    client.TOKEN = request['TOKEN']


def PLAYER_INFO(client, request):
    client.DATA['INFO'] = [request['NAME'], request['LEVEL'], request['MONEY']]
