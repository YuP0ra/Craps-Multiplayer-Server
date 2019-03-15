import sqlite3, json



conn = sqlite3.connect('Statics/kyServerDB.db')

def init():
    """ ########################## Loading Database ######################### """
    cursor = conn.execute('''SELECT * FROM sqlite_master WHERE type='table' and name='CrapsPlayer';''')
    for row in cursor:
        if 'CrapsPlayer' in row:
            break
    else:
        conn.execute('''CREATE TABLE CrapsPlayer
                     (
                     TOKEN          CHAR(32)    NOT NULL    PRIMARY KEY,
                     JSON           TEXT        NOT NULL
                     );'''
                     )
        print("DATABASE CREATED SUCCESSFULLY")
        conn.close()


def addJsonPlayer(token, playerJson):
    try:
        conn.execute('''INSERT INTO CrapsPlayer(TOKEN, JSON) VALUES(?,?)''', (token, playerJson))
        conn.commit()
        return True
    except Exception as e:
        return False


def getJsonPlayer(token):
    try:
        return [str(row[0]) for row in conn.execute('''SELECT JSON FROM CrapsPlayer WHERE token="%s";''' % token).fetchall()]
    except Exception as e:
        print(e)
        return None
