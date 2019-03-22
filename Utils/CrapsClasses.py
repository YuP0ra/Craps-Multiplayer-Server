import copy
import random

class CrapsTable:
    def __init__(self,):
        self.marker = 0
        self.ridBets = {}
        self.isComeOutRoll = True

        self.roundResultsWIN = []
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
        roundWinLosePushResults = {}

        for rid in self.ridBets:
            self.CheckStatusBig6(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckStatusBig8(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckStatusBig6(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckStatusBig8(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckStatusLay(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckStatusBuy(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

            self.CheckPassLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)
            self.CheckDontPassLine(rid, tmpIsComeOutRoll, tmpMarker, totalDices)

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

        if firstRoll:
            if totalDices in [7, 11]:
                self.WIN(rid, 'passline')
            elif totalDices in [2, 3, 12]:
                self.LOSE(rid, 'passline')
        else:
            if totalDices == targetPoint:
                self.WIN(rid, 'passline')
            elif totalDices == 7:
                self.LOSE(rid, 'passline')

    def CheckDontPassLine(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'dontpassline') <= 0:
            return

        if firstRoll:
            if totalDices in [2, 3]:
                self.WIN(rid, 'dontpassline')
            elif totalDices in [7, 11]:
                self.LOSE(rid, 'dontpassline')
            elif totalDices in [12]:
                self.PUSH(rid, 'dontpassline')
        else:
            if totalDices == targetPoint:
                self.LOSE(rid, 'dontpassline')
            elif totalDices == 7:
                self.WIN(rid, 'dontpassline')

    def CheckStatusBig6(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'big6') <= 0:
            return
        else:
            if totalDices in [6]: self.WIN(rid, 'big6')
            if totalDices in [7]: self.LOSE(rid, 'big6')

    def CheckStatusBig8(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'big8') <= 0:
            return
        else:
            if totalDices in [8]: self.WIN(rid, 'big8')
            if totalDices in [7]: self.LOSE(rid, 'big8')

    def CheckStatusLay(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            if self.BetValue(rid,'lay' + str(totalDices)) > 0:
                self.LOSE(rid, 'lay' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                if self.BetValue(rid,'lay' + str(odd)) > 0:
                    self.WIN(rid, 'lay' + str(odd))

    def CheckStatusBuy(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            if self.BetValue(rid,'buy' + str(totalDices)) > 0:
                self.WIN(rid, 'buy' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                if self.BetValue(rid,'buy' + str(odd)) > 0:
                    self.LOSE(rid, 'buy' + str(odd))

    def CheckStatusFieldLine(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'field') <= 0:
            return
        else:
            if totalDices in [2, 3, 4, 9, 10, 11, 12]:
                self.WIN(rid, 'field')
            else:
                self.LOSE(rid, 'field')

    def CheckPropositionBets(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'prop0') > 0:
            if totalDices == 2 or totalDices == 3 or totalDices == 12:
                self.WIN(rid, 'prop0');
            else:
                self.LOSE(rid, 'prop0');

        if self.BetValue(rid, 'prop2') > 0:
            if totalDices == 2:
                self.WIN(rid, 'prop2');
            else:
                self.LOSE(rid, 'prop2');

        if self.BetValue(rid, 'prop3') > 0:
            if totalDices == 3:
                self.WIN(rid, 'prop3');
            else:
                self.LOSE(rid, 'prop3');

        if self.BetValue(rid, 'prop7') > 0:
            if totalDices == 7:
                self.WIN(rid, 'prop7');
            else:
                self.LOSE(rid, 'prop7');

        if self.BetValue(rid, 'prop11') > 0:
            if totalDices == 11:
                self.WIN(rid, 'prop11');
            else:
                self.LOSE(rid, 'prop11');

        if self.BetValue(rid, 'prop12') > 0:
            if totalDices == 12:
                self.WIN(rid, 'prop12');
            else:
                self.LOSE(rid, 'prop12');

    def CheckStatusHardway(self, rid, firstRoll, targetPoint, dice1, dice2):
        for num in [4, 6, 8, 10]:
            hardline = 'hard' + str(num)
            if self.BetValue(rid, hardline) > 0:
                if (dice1 + dice2) == 7:
                    self.LOSE(rid, hardline)

                if (dice1 + dice2) == num:
                    if dice1 == dice2:
                        self.WIN(rid, hardline)
                    else:
                        self.LOSE(rid, hardline)

    def ClearRoundResults(self):
        self.roundResultsWIN = []
        self.roundResultsPUSH = []
        self.roundResultsLOSE = []

    def WIN(self, rid, line):
        self.roundResultsWIN.append([rid, line])
        self.ClearTableBet(rid, line)

    def PUSH(self, rid, line):
        self.roundResultsPUSH.append([rid, line])
        self.ClearTableBet(rid, line)

    def LOSE(self, rid, line):
        self.roundResultsLOSE.append(line)
        self.roundResultsLOSE.append([rid, line])
        self.ClearTableBet(rid, line)

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
                "LIST_DICT" : [str(self.ridBets[rid]) for rid in self.ridBets]
                }

    def MarkerInfo(self):
        return {"TYPE"      : "MARKER_INFO",
                "COMEROLL"  : str(self.isComeOutRoll),
                "MARKER"    : str(self.marker)}


# t = CrapsTable()
#
# for i in range(10):
#     d1, d2 = random.randint(1, 6), random.randint(1, 6)
#     t.UpdateTableBet('123', 'big6', 10)
#     t.UpdateTableBet('123', 'big8', 30)
#     t.UpdateTableBet('123', 'passline', 10)
#     t.UpdateTableBet('123', 'dontpassline', 30)
#     t.UpdateTableBet('123', 'field', 10)
#     t.UpdateTableBet('123', 'prop2', 30)
#     t.UpdateTableBet('123', 'prop3', 30)
#     t.UpdateTableBet('123', 'prop7', 30)
#     t.UpdateTableBet('123', 'prop11', 30)
#
#     t.UpdateTableBet('13', 'big6', 10)
#     t.UpdateTableBet('13', 'big8', 30)
#     t.UpdateTableBet('13', 'passline', 10)
#     t.UpdateTableBet('13', 'dontpassline', 30)
#     t.UpdateTableBet('13', 'field', 10)
#     t.UpdateTableBet('13', 'prop2', 30)
#     t.UpdateTableBet('13', 'prop3', 30)
#     t.UpdateTableBet('13', 'prop7', 30)
#     t.UpdateTableBet('13', 'prop11', 30)
#
#     t.Roll(d1, d2)
#     print(d1+ d2, t.roundResultsWIN)
