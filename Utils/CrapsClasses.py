import copy
import random
import secrets


class CrapsBot():
    def __init__(self, allowedBets):
        self.TOKEN      = str(secrets.token_hex(16))
        self.DATA       = {}

        self._stck      = []
        self._money     = {}
        self._roundID   = "0"
        self.validChips = allowedBets

    def __eq__(self, other):
        return self.TOKEN == other.TOKEN

    def __hash__(self):
        return hash(self.TOKEN)

    def joinRoom(self, roomName, func):
        self.DATA['CURRENT_ROOM'] = None
        self.DATA['INFO'] = ['bot', 10, 500000, '']
        request = { 'TYPE'      :'JOIN_ROOM_REQUEST',
                    'SERVERID'  :'123456',
                    'ROOM_NAME' :roomName
                   }
        func(self, request)

    def fireupNewBot(self):
        index = random.randint(0, 14)
        names = ['b@t1', 'b@t2', 'b@t3', 'b@t4', 'b@t4', 'b@t5', 'b@t6', 'b@t7', 'b@t8', 'b@t9', 'b@t10', 'b@t11', 'b@t12', 'b@t13', 'b@t14', 'b@t15']
        leves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        money = [1000000, 2000000, 300000, 400000, 500000, 6000000, 7000000, 8000000, 9000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000,]

        self._money = money[index]
        self.DATA['INFO'] = [names[index], leves[index], money[index], '']

    def placeBet(self, firstRoll, func):
        if firstRoll:
            validBets = ['passline', 'passline', 'passline', 'passline', 'dontpassline',
                         'big6', 'big8',
                         'prop0', 'prop7',
                         'lay4', 'lay5', 'lay6', 'lay8', 'lay9', 'lay10',
                         'field', 'field', 'field']
        else:
            validBets = ['come', 'come', 'come', 'dontcome',
                         'big6', 'big8',
                         'prop0', 'prop7',
                         'lay4', 'lay5', 'lay6', 'lay8', 'lay9', 'lay10',
                         'field', 'field', 'field']

        validBets = [x for x in validBets if x not in self._stck]
        val = random.choice(self.validChips[:-2])
        bet = random.choice(validBets)
        self._stck.append(bet)

        bet_request = { 'TYPE'      :'CRAPS_BET',
                        'TOKEN'     :self.TOKEN,
                        'ROUND_ID'  :self._roundID,
                        'BETTING_ON':str(bet),
                        'AMOUNT'    :str(val)
                       }

        if self._money > val:
            self._money -= val
            func(self, bet_request)
            self.DATA['INFO'][2] = self._money


    def send_data(self, request):
        if 'TYPE' in request:
            if request['TYPE'] == 'ROUND_STARTED':
                self._roundID = request['ROUND_ID']
                self.DATA['INFO'][2] = self._money
                self._stck = []

            if request['TYPE'] == 'CLOCK_UPDATE':
                self.DATA['INFO'][2] = self._money


class CrapsTable:
    def __init__(self, allowedBets):
        self.marker = 0
        self.roundID = 0
        self.ridBets = {}
        self.canPlay = True
        self.isComeOutRoll = True
        self.validChips = allowedBets

        self.ridTotalWin = {}

        self.roundNextBets = []
        self.roundResultsWIN = []
        self.roundResultsMOVE = []
        self.roundResultsPUSH = []
        self.roundResultsLOSE = []
        self.roundResultsTotalWins = []


    def Reset(self,):
            self.marker = 0
            self.isComeOutRoll = True

    def Roll(self, dice1, dice2):
        totalDices = dice1 + dice2
        tmpMarker = copy.deepcopy(self.marker)
        tmpIsComeOutRoll = copy.deepcopy(self.isComeOutRoll)

        if self.isComeOutRoll and totalDices in [4, 5, 6, 8, 9, 10]:
            self.marker = totalDices
            self.isComeOutRoll = False
        elif totalDices == 7 or totalDices == self.marker:
            self.marker = 0
            self.isComeOutRoll = True

        self.ClearRoundResults()
        totalDices = dice1 + dice2

        for rid in self.ridBets:
            self.ridTotalWin[rid] = 0

            self.CheckLay(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckBig6(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckBig8(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckCome(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckPassLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckDontCome(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckFieldLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckDontPassLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckPropositionBets(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            if not tmpIsComeOutRoll:
                self.CheckBuy(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
                self.CheckStatusHardway(rid, tmpIsComeOutRoll, tmpMarker, dice1, dice2)

        for rid, total in self.ridTotalWin.items():
            total = 0 if total < 0 else total
            self.roundResultsTotalWins.append(str(rid))
            self.roundResultsTotalWins.append(str(total))


    def BetValue(self, rid, betName):
        """Takes Room ID and Line, returns the bets on it"""
        if rid not in self.ridBets:
            return 0
        elif betName not in self.ridBets[rid]:
            return 0
        else:
            return int(self.ridBets[rid][betName])


    def CheckPassLine(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'passline') <= 0:
            return

        payout = {4:2, 5:3/2, 6:6/5, 8:6/5, 9:3/2, 10:2}
        if firstRoll:
            if totalDices in [7, 11]:
                self.WIN(rid, 'passline')
            elif totalDices in [2, 3, 12]:
                self.LOSE(rid, 'passline')
        else:
            if totalDices == targetPoint:
                self.WIN(rid, 'passline')
                self.WIN(rid, 'passlineodds', payout[totalDices])
            elif totalDices == 7:
                self.LOSE(rid, 'passline')
                self.LOSE(rid, 'passlineodds')


    def CheckDontPassLine(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'dontpassline') <= 0:
            return

        payout = {4:1/2, 5:2/3, 6:5/6, 8:5/6, 9:2/3, 10:1/2}
        if firstRoll:
            if totalDices in [2, 3]:
                self.WIN(rid, 'dontpassline')
            elif totalDices in [7, 11]:
                self.LOSE(rid, 'dontpassline')
            elif totalDices in [12]:
                self.PUSH(rid, 'dontpassline')
        else:
            if totalDices == 7:
                self.WIN(rid, 'dontpassline')
                self.WIN(rid, 'dontpasslineodds', payout[targetPoint])
            elif totalDices == targetPoint:
                self.LOSE(rid, 'dontpassline')
                self.LOSE(rid, 'dontpasslineodds')


    def CheckCome(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            payout = {4:2, 5:3/2, 6:6/5, 8:6/5, 9:3/2, 10:2}
            self.WIN(rid, 'come' + str(totalDices))
            if firstRoll:
                self.PUSH(rid, 'comeodds' + str(totalDices))
            else:
                self.WIN(rid, 'comeodds' + str(totalDices), payout[totalDices])

        if (totalDices == 7):
            for odd in [4, 5, 6, 8, 9, 10]:
                self.LOSE(rid, 'come' + str(odd))
                if firstRoll:
                    self.PUSH(rid, 'comeodds' + str(odd))
                else:
                    self.LOSE(rid, 'comeodds' + str(odd))

        if not firstRoll and self.BetValue(rid, 'come') > 0:
            if totalDices in [7, 11]:
                self.WIN(rid, 'come')
            elif totalDices in [2, 3, 12]:
                self.LOSE(rid, 'come')
            else:
                self.MOVE(rid, 'come', 'come' + str(totalDices))


    def CheckDontCome(self, rid, firstRoll, targetPoint, totalDices):
        payout = {4:1/2, 5:2/3, 6:5/6, 8:5/6, 9:2/3, 10:1/2}
        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.LOSE(rid, 'dontcome' + str(totalDices))
            self.LOSE(rid, 'dontcomeodds' + str(totalDices))

        if (totalDices == 7):
            for odd in [4, 5, 6, 8, 9, 10]:
                self.WIN(rid, 'dontcome' + str(odd))
                self.WIN(rid, 'dontcomeodds' + str(odd), payout[odd])

        if not firstRoll and self.BetValue(rid, 'dontcome') > 0:
            if totalDices in [2, 3]:
                self.WIN(rid, 'dontcome')
            elif totalDices in [7, 11]:
                self.LOSE(rid, 'dontcome')
            elif totalDices in [12]:
                self.PUSH(rid, 'dontcome')
            else:
                self.MOVE(rid, 'dontcome', 'dontcome' + str(totalDices))


    def CheckBig6(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices == 6:
            self.WIN(rid, 'big6')
        if totalDices == 7:
            self.LOSE(rid, 'big6')


    def CheckBig8(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices == 8:
            self.WIN(rid, 'big8')
        if totalDices == 7:
            self.LOSE(rid, 'big8')


    def CheckLay(self, rid, firstRoll, targetPoint, totalDices):
        payout = {4: 19/41, 5: 19/31, 6: 19/25, 8: 19/25, 9: 19/31, 10: 19/41}

        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.LOSE(rid, 'lay' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                self.WIN(rid, 'lay' + str(odd), payout[odd])


    def CheckBuy(self, rid, firstRoll, targetPoint, totalDices):
        payout = {4: 39/20, 5: 7/5, 6: 7/6, 8: 7/6, 9: 7/5, 10: 39/20}

        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.WIN(rid, 'buy' + str(totalDices), payout[totalDices])

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                self.LOSE(rid, 'buy' + str(odd))


    def CheckFieldLine(self, rid, firstRoll, targetPoint, totalDices):
        payout = {2:2, 3:1, 4:1, 9:1, 10:1, 11:1, 12:3}

        if totalDices in [2, 3, 4, 9, 10, 11, 12]:
            self.WIN(rid, 'field', payout[totalDices])
        else:
            self.LOSE(rid, 'field')


    def CheckPropositionBets(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices == 2 or totalDices == 3 or totalDices == 12:
            self.WIN(rid, 'prop0', 7);
        else:
            self.LOSE(rid, 'prop0');

        if totalDices == 2:
            self.WIN(rid, 'prop2', 30);
        else:
            self.LOSE(rid, 'prop2');

        if totalDices == 3:
            self.WIN(rid, 'prop3', 15);
        else:
            self.LOSE(rid, 'prop3');

        if totalDices == 7:
            self.WIN(rid, 'prop7', 4);
        else:
            self.LOSE(rid, 'prop7');

        if totalDices == 11:
            self.WIN(rid, 'prop11', 15);
        else:
            self.LOSE(rid, 'prop11');

        if totalDices == 12:
            self.WIN(rid, 'prop12', 30);
        else:
            self.LOSE(rid, 'prop12');


    def CheckStatusHardway(self, rid, firstRoll, targetPoint, dice1, dice2):
        payout = {4:7, 6:9, 8:9, 10:7}

        for odd in [4, 6, 8, 10]:
            hardline = 'hard' + str(odd)
            if (dice1 + dice2) == 7:
                self.LOSE(rid, hardline)

            if (dice1 + dice2) == odd:
                if dice1 == dice2:
                    self.WIN(rid, hardline, payout[odd])
                else:
                    self.LOSE(rid, hardline)


    def ClearRoundResults(self):
        self.roundResultsWIN = []
        self.roundResultsPUSH = []
        self.roundResultsLOSE = []
        self.roundResultsMOVE = []
        self.roundResultsTotalWins = []


    def WIN(self, rid, line, factor=1):
        def ceil(a):
            if a > int(a) + 0.3:
                return int(a + 1)
            return int(a)
        moneyOnLine = int(ceil(self.BetValue(rid, line) * (1 + factor)))
        self.ridTotalWin[rid] += moneyOnLine
        if moneyOnLine > 0:
            self.roundResultsWIN.append(str(rid))
            self.roundResultsWIN.append(str(line))
            self.roundResultsWIN.append(str(int(moneyOnLine)))
            self.ClearTableBet(rid, line)


    def PUSH(self, rid, line):
        moneyOnLine = self.BetValue(rid, line)
        self.ridTotalWin[rid] += moneyOnLine
        if moneyOnLine > 0:
            self.roundResultsPUSH.append(str(rid))
            self.roundResultsPUSH.append(str(line))
            self.roundResultsPUSH.append(str(int(moneyOnLine)))
            self.ClearTableBet(rid, line)


    def LOSE(self, rid, line):
        moneyOnLine = self.BetValue(rid, line)
        self.ridTotalWin[rid] -= moneyOnLine
        if moneyOnLine > 0:
            self.roundResultsLOSE.append(str(rid))
            self.roundResultsLOSE.append(str(line))
            self.roundResultsLOSE.append(str(int(moneyOnLine)))
            self.ClearTableBet(rid, line)


    def MOVE(self, rid, oldLine, newLine):
        moneyOnOldLine = self.BetValue(rid, oldLine)
        moneyOnNewLine = self.BetValue(rid, newLine)
        if moneyOnOldLine > 0:
            self.appendTableBet(rid, newLine, moneyOnOldLine + moneyOnNewLine)
            self.roundResultsMOVE.append(str(rid))
            self.roundResultsMOVE.append(str(oldLine))
            self.roundResultsMOVE.append(str(newLine))
            self.ClearTableBet(rid, oldLine)



    def appendTableBet(self, rid, bet, amount):
        if rid not in self.ridBets:
            self.ridBets[rid] = {}
        if bet not in self.ridBets[rid]:
            self.ridBets[rid][bet] = 0
        self.ridBets[rid][bet] += amount


    def removeTableBet(self, rid, bet):
        if rid in self.ridBets:
            if bet in self.ridBets[rid]:
                self.ridBets[rid][bet] = 0


    def updateTableBet(self, rid, request):
        if 'ROUND_ID' in request:
            if self.canPlay:
                if request['ROUND_ID'] == str(self.roundID):

                    if request['BETTING_ON'] == 'passlineodds':
                        factor = {4:3, 5:4, 6:5, 8:5, 9:4, 10:3}
                        if self.BetValue(rid, 'passlineodds') >= self.BetValue(rid, 'passline') * factor[self.marker]:
                            return False
                    elif request['BETTING_ON'] == 'dontpasslineodds':
                        if self.BetValue(rid, 'dontpasslineodds') >= self.BetValue(rid, 'dontpassline') * 6:
                            return False
                    elif 'dontcomeodds' in request['BETTING_ON']:
                        if self.BetValue(rid, request['BETTING_ON']) >= self.BetValue(rid, request['BETTING_ON'].replace('odds', '')) * 6:
                            return False
                    elif 'comeodds' in request['BETTING_ON']:
                        factor = {4:3, 5:4, 6:5, 8:5, 9:4, 10:3}
                        if self.BetValue(rid, request['BETTING_ON']) >= self.BetValue(rid, request['BETTING_ON'].replace('odds', '')) * factor[int(request['BETTING_ON'][8:])]:
                            return False

                    self.appendTableBet(rid, request['BETTING_ON'], int(request['AMOUNT']))
                    return True
        return False

    def clearTableBet(self, rid, request):
        if 'ROUND_ID' in request:
            if self.canPlay:
                if request['ROUND_ID'] == str(self.roundID):
                    self.removeTableBet(rid, request['BETTING_ON'])
                    return True
        return False

    def ClearTableBet(self, rid, bet):
        if rid in self.ridBets:
            if bet in self.ridBets[rid]:
                self.ridBets[rid][bet] = 0


    def ClearTableBets(self,):
        for rid in self.ridBets:
            for bet in self.ridBets[rid]:
                self.ridBets[rid][bet] = 0


    def ClearPlayerBets(self, rid):
        if rid in self.ridBets:
            for bet in self.ridBets[rid]:
                self.ridBets[rid][bet] = 0


    def RemovePlayer(self, rid):
        if rid in self.ridBets:
            del self.ridBets[rid]


    def TableTotalBetsList(self):
        allTotalBets = []
        for rid in self.ridBets:
            total = 0
            for bet in self.ridBets[rid]:
                val = self.ridBets[rid][bet]
                if val > 0:
                    total += val
            allTotalBets.append(str(rid))
            allTotalBets.append(str(total))
        return allTotalBets

    def TableBetsList(self):
        allValidBets = []
        for rid in self.ridBets:
            for bet in self.ridBets[rid]:
                val = self.ridBets[rid][bet]
                if val > 0:
                    allValidBets.append(str(rid))
                    allValidBets.append(str(bet))
                    allValidBets.append(str(val))
        return allValidBets

    def JsonTableInfo(self):
        ridList = [str(rid) for rid in self.ridBets]
        return {"TYPE"      : "TABLE_INFO",
                "RIDS_LIST" : str(ridList),
                "MARKER"    : str(self.marker),
                "RID_COUNT" : str(len(ridList)),
                "ROUND_ID"  : str(self.roundID),
                "COMEROLL"  : str(self.isComeOutRoll),
                }


    def JsonPlayerBets(self, rid):
        betNames = []
        betValues = []
        if rid in self.ridBets:
            for key, value in self.ridBets[rid].items():
                betNames.append(key)
                betValues.append(value)

        return {"TYPE"      : "PLAYER_BETS",
                "TOKEN"     : rid,
                "BET_NAMES" : betNames,
                "BET_VALUES": betValues}


    def MarkerInfo(self):
        return {"TYPE"      : "MARKER_INFO",
                "COMEROLL"  : str(self.isComeOutRoll),
                "MARKER"    : str(self.marker)
               }
