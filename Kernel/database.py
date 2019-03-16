import json
import sqlite3


_db_memory      = {}
_db_connection  = sqlite3.connect('Statics/kyServerDB.db')


def init():
    """ ########################## Loading Database ######################### """
    cursor = _db_connection.execute('''SELECT * FROM sqlite_master WHERE type='table' and name='Token2JSON';''')
    for row in cursor:
        if 'Token2JSON' in row:
            break
    else:
        _db_connection.execute('''CREATE TABLE Token2JSON
                     (
                     TOKEN          CHAR(32)    NOT NULL    PRIMARY KEY,
                     JSON           TEXT        NOT NULL
                     );'''
                     )
        print("DATABASE CREATED SUCCESSFULLY")
        _db_connection.close()


def addJsonDB(token, playerJson):
    try:
        _db_connection.execute('''INSERT INTO Token2JSON(TOKEN, JSON) VALUES(?,?)''', (token, playerJson))
        _db_connection.commit()
        return True
    except Exception as e:
        return False


def getDJsonDB(token):
    try:
        return [str(row[0]) for row in _db_connection.execute('''SELECT JSON FROM Token2JSON WHERE token="%s";''' % token).fetchall()]
    except Exception as e:
        print(e)
        return None


def get(var):
    if var in _db_memory:
        return _db_memory[var]
    return None


def set(var, value):
    _db_memory[var] = value
