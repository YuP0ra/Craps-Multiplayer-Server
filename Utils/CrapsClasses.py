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

    def CheckCome(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.WIN(rid, 'come' + totalDices)
            self.WIN(rid, 'come' + totalDices + 'odds')

        if (diceTotal == 7)
            for odd in [4, 5, 6, 8, 9, 10]:
                self.LOSE(rid, 'come' + odd)
                self.LOSE(rid, 'come' + odd + 'odds')

        if not firstRoll and self.BetValue(rid, 'come'):
            if diceTotal in [7, 11]:
                self.WIN(rid, 'come')
            elif diceTotal in [2, 3, 12]:
                self.LOSE(rid, 'come')

    def CheckDontCome(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.LOSE(rid, 'dontcome' + totalDices)
            self.LOSE(rid, 'dontcome' + totalDices + 'odds')

        if (diceTotal == 7)
            for odd in [4, 5, 6, 8, 9, 10]:
                self.WIN(rid, 'dontcome' + odd)
                self.WIN(rid, 'dontcome' + odd + 'odds')

        if not firstRoll and self.BetValue(rid, 'dontcome'):
            if diceTotal in [2, 3]:
                self.WIN(rid, 'dontcome')
            elif diceTotal in [7, 11]:
                self.LOSE(rid, 'dontcome')
            elif diceTotal in [12]:
                self.PUSH(rid, 'dontcome')

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
        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.LOSE(rid, 'lay' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                self.WIN(rid, 'lay' + str(odd))

    def CheckBuy(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            self.WIN(rid, 'buy' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                self.LOSE(rid, 'buy' + str(odd))

    def CheckFieldLine(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [2, 3, 4, 9, 10, 11, 12]:
            self.WIN(rid, 'field')
        else:
            self.LOSE(rid, 'field')

    def CheckPropositionBets(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices == 2 or totalDices == 3 or totalDices == 12:
            self.WIN(rid, 'prop0');
        else:
            self.LOSE(rid, 'prop0');

        if totalDices == 2:
            self.WIN(rid, 'prop2');
        else:
            self.LOSE(rid, 'prop2');

        if totalDices == 3:
            self.WIN(rid, 'prop3');
        else:
            self.LOSE(rid, 'prop3');

        if totalDices == 7:
            self.WIN(rid, 'prop7');
        else:
            self.LOSE(rid, 'prop7');

        if totalDices == 11:
            self.WIN(rid, 'prop11');
        else:
            self.LOSE(rid, 'prop11');

        if totalDices == 12:
            self.WIN(rid, 'prop12');
        else:
            self.LOSE(rid, 'prop12');

    def CheckStatusHardway(self, rid, firstRoll, targetPoint, dice1, dice2):
        for odd in [4, 6, 8, 10]:
            hardline = 'hard' + str(odd)
            if (dice1 + dice2) == 7:
                self.LOSE(rid, hardline)

            if (dice1 + dice2) == odd:
                if dice1 == dice2:
                    self.WIN(rid, hardline)
                else:
                    self.LOSE(rid, hardline)

    def ClearRoundResults(self):
        self.roundResultsWIN = []
        self.roundResultsPUSH = []
        self.roundResultsLOSE = []

    def WIN(self, rid, line):
        if self.BetValue(rid, line) > 0:
            self.roundResultsWIN.append(rid)
            self.roundResultsWIN.append(line)
        self.ClearTableBet(rid, line)

    def PUSH(self, rid, line):
        if self.BetValue(rid, line) > 0:
            self.roundResultsPUSH.append(rid)
            self.roundResultsPUSH.append(line)
        self.ClearTableBet(rid, line)

    def LOSE(self, rid, line):
        if self.BetValue(rid, line) > 0:
            self.roundResultsLOSE.append(rid)
            self.roundResultsLOSE.append(line)
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
