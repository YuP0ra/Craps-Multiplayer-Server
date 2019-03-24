import copy
import random

class CrapsTable:
    def __init__(self,):
        self.marker = 0
        self.ridBets = {}
        self.isComeOutRoll = True

        self.roundResultsWIN = []
        self.roundResultsMOVE = []
        self.roundResultsPUSH = []
        self.roundResultsLOSE = []

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
            self.CheckBig6(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckBig8(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckFieldLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckPropositionBets(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckLay(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckBuy(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckPassLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckDontPassLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckCome(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckDontCome(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckStatusHardway(rid, tmpIsComeOutRoll, tmpMarker, dice1, dice2)

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

        payout = {4:2, 5:3/2, 6:6/5, 8:6/5, 9:3/2, 10:2}
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
            self.WIN(rid, 'come' + str(totalDices), payout[totalDices])
            self.WIN(rid, 'come' + str(totalDices) + 'odds', payout[totalDices])

        if (totalDices == 7):
            for odd in [4, 5, 6, 8, 9, 10]:
                self.LOSE(rid, 'come' + str(odd))
                self.LOSE(rid, 'come' + str(odd) + 'odds')

        if not firstRoll and self.BetValue(rid, 'come'):
            if totalDices in [7, 11]:
                self.WIN(rid, 'come')
            elif totalDices in [2, 3, 12]:
                self.LOSE(rid, 'come')
            else:
                self.MOVE(rid, 'come', 'come' + str(totalDices))

    def CheckDontCome(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            payout = {4:2, 5:3/2, 6:6/5, 8:6/5, 9:3/2, 10:2}
            self.LOSE(rid, 'dontcome' + str(totalDices))
            self.LOSE(rid, 'dontcome' + str(totalDices) + 'odds')

        if (totalDices == 7):
            for odd in [4, 5, 6, 8, 9, 10]:
                self.WIN(rid, 'dontcome' + str(odd))
                self.WIN(rid, 'dontcome' + str(odd) + 'odds')

        if not firstRoll and self.BetValue(rid, 'dontcome'):
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

    def WIN(self, rid, line, factor=1):
        moneyOnLine = int(self.BetValue(rid, line) * (1 + factor))
        if moneyOnLine > 0:
            self.roundResultsWIN.append(rid)
            self.roundResultsWIN.append(line)
            self.roundResultsWIN.append(str(moneyOnLine))
            self.ClearTableBet(rid, line)

    def PUSH(self, rid, line):
        moneyOnLine = self.BetValue(rid, line)
        if moneyOnLine > 0:
            self.roundResultsPUSH.append(rid)
            self.roundResultsPUSH.append(line)
            self.roundResultsPUSH.append(str(moneyOnLine))
            self.ClearTableBet(rid, line)

    def LOSE(self, rid, line):
        moneyOnLine = self.BetValue(rid, line)
        if moneyOnLine > 0:
            self.roundResultsLOSE.append(rid)
            self.roundResultsLOSE.append(line)
            self.roundResultsLOSE.append(str(moneyOnLine))
            self.ClearTableBet(rid, line)

    def MOVE(self, rid, oldLine, newLine):
        moneyOnOldLine = self.BetValue(rid, oldLine)
        moneyOnNewLine = self.BetValue(rid, newLine)
        if moneyOnOldLine > 0:
            self.UpdateTableBet(rid, newLine, moneyOnOldLine + moneyOnNewLine)
            self.roundResultsMOVE.append(rid)
            self.roundResultsMOVE.append(oldLine)
            self.roundResultsMOVE.append(newLine)
            self.ClearTableBet(rid, oldLine)

    def UpdateTableBet(self, rid, bet, amount):
        if rid not in self.ridBets:
            self.ridBets[rid] = {}
        if bet not in self.ridBets[rid]:
            self.ridBets[rid][bet] = 0
        self.ridBets[rid][bet] += amount

    def ClearTableBet(self, rid, bet):
        if rid in self.ridBets:
            if bet in self.ridBets[rid]:
                self.ridBets[rid][bet] = 0

    def RemovePlayer(self, rid):
        if rid in self.ridBets:
            del self.ridBets[rid]

    def JsonTableInfo(self):
        ridList = [str(rid) for rid in self.ridBets]
        return {"TYPE"      : "TABLE_INFO",
                "MARKER"    : str(self.marker),
                "COMEROLL"  : str(self.isComeOutRoll),
                "RID_COUNT" : str(len(ridList)),
                "RIDS_LIST" : ridList,
                }

    def PlayerBets(self, rid):
        betNames = []
        betValues = []
        if len(self.ridBets) > 0:
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
                "MARKER"    : str(self.marker)}




# t = CrapsTable()
#
# for i in range(100):
#     d1, d2 = random.randint(1, 6), random.randint(1, 6)
#     t.UpdateTableBet('123', 'buy4', 10)
#     t.UpdateTableBet('123', 'buy8', 10)
#     t.UpdateTableBet('123', 'buy9', 10)
#     t.UpdateTableBet('123', 'lay6', 10)
#     t.UpdateTableBet('123', 'lay4', 10)
#     t.UpdateTableBet('123', 'lay10', 10)
#     t.UpdateTableBet('123', 'big6', 10)
#     t.UpdateTableBet('123', 'big8', 10)
#     t.UpdateTableBet('123', 'come', 10)
#     t.UpdateTableBet('123', 'field', 10)
#     t.UpdateTableBet('123', 'prop2', 10)
#     t.UpdateTableBet('123', 'prop3', 10)
#     t.UpdateTableBet('123', 'prop7', 10)
#     t.UpdateTableBet('123', 'prop11', 10)
#     t.UpdateTableBet('123', 'dontcome', 10)
#     t.UpdateTableBet('123', 'passline', 10)
#     t.UpdateTableBet('123', 'dontpassline', 10)
#     t.UpdateTableBet('123', 'passlineodds', 10)
#     t.UpdateTableBet('123', 'dontpasslineodds', 10)
#
#     t.Roll(d1, d2)
#     print(d1+ d2, t.roundResultsWIN)
