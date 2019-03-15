import time
import sqlite3


def onConnectionStarted(client):
    print("New Connection: ", client.address)


def onConnectionTimeout(client):
    pass


def onConnectionEnded(client):
    print("Connection Terminated: ", client.address)


def PLAYER_INFO(client, request):
    print("FROM DEF PLAYER INFO: ", request)


def DEFAULT(client, request):
    print(request)
