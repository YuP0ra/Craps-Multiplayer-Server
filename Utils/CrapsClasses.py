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
                self.WIN('passline')
            elif totalDices in [2, 3, 12]:
                self.LOSE('passline')
        else:
            if totalDices == targetPoint:
                self.WIN('passline')
            elif totalDices == 7:
                self.LOSE('passline')

    def CheckDontPassLine(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'dontpassline') <= 0:
            return

        if firstRoll:
            if totalDices in [2, 3]:
                self.WIN('dontpassline')
            elif totalDices in [7, 11]:
                self.LOSE('dontpassline')
            elif totalDices in [12]:
                self.PUSH('dontpassline')
        else:
            if totalDices == targetPoint:
                self.LOSE('dontpassline')
            elif totalDices == 7:
                self.WIN('dontpassline')

    def CheckStatusBig6(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'big6') <= 0:
            return
        else:
            if totalDices in [6]: self.WIN('big6')
            if totalDices in [7]: self.LOSE('big6')

    def CheckStatusBig8(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'big8') <= 0:
            return
        else:
            if totalDices in [8]: self.WIN('big8')
            if totalDices in [7]: self.LOSE('big8')

    def CheckStatusLay(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            if self.BetValue('lay' + str(totalDices)) > 0:
                self.LOSE('lay' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                if self.BetValue('lay' + str(odd)) > 0:
                    self.WIN('lay' + str(odd))

    def CheckStatusBuy(self, rid, firstRoll, targetPoint, totalDices):
        if totalDices in [4, 5, 6, 8, 9, 10]:
            if self.BetValue('lay' + str(totalDices)) > 0:
                self.WIN('lay' + str(totalDices))

        if totalDices == 7:
            for odd in  [4, 5, 6, 8, 9, 10]:
                if self.BetValue('lay' + str(odd)) > 0:
                    self.LOSE('lay' + str(odd))

    def CheckStatusFieldLine(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'field') <= 0:
            return
        else:
            if totalDices in [2, 3, 4, 9, 10, 11, 12]:
                self.WIN('field')
            else:
                self.LOSE('field')

    def CheckPropositionBets(self, rid, firstRoll, targetPoint, totalDices):
        if self.BetValue(rid, 'prop0') > 0:
            if totalDices == 2 or totalDices == 3 or totalDices == 12:
                self.WIN('prop0');
            else:
                self.LOSE('prop0');

        if self.BetValue(rid, 'prop2') > 0:
            if totalDices == 2:
                self.WIN('prop2');
            else:
                self.LOSE('prop2');

        if self.BetValue(rid, 'prop3') > 0:
            if totalDices == 3:
                self.WIN('prop3');
            else:
                self.LOSE('prop3');

        if self.BetValue(rid, 'prop7') > 0:
            if totalDices == 7:
                self.WIN('prop7');
            else:
                self.LOSE('prop7');

        if self.BetValue(rid, 'prop11') > 0:
            if totalDices == 11:
                self.WIN('prop11');
            else:
                self.LOSE('prop11');

        if self.BetValue(rid, 'prop12') > 0:
            if totalDices == 12:
                self.WIN('prop12');
            else:
                self.LOSE('prop12');

    def CheckStatusHardway(self, rid, firstRoll, targetPoint, dice1, dice2):
        for num in [4, 6, 8, 10]:
            hardline = 'hard' + str(num)
            if self.BetValue(rid, hardline) > 0:
                if (dice1 + dice2) == 7:
                    self.LOSE(hardline)

                if (dice1 + dice2) == num:
                    if dice1 == dice2:
                        self.WIN(hardline)
                    else:
                        self.LOSE(hardline)


    def ClearRoundResults(self):
        self.roundResultsWIN = []
        self.roundResultsPUSH = []
        self.roundResultsLOSE = []

    def WIN(self, line):
        self.roundResultsWIN.append(line)
        self.ClearTableBet(rid, line)

    def PUSH(self, line):
        self.roundResultsPUSH.append(line)
        self.ClearTableBet(rid, line)

    def LOSE(self, line):
        self.roundResultsLOSE.append(line)
        self.ClearTableBet(rid, line)

    def UpdateTableBet(self, rid, bet, amount):
        if rid not in self.ridBets:
            self.ridBets[rid] = {}
        if bet not in self.ridBets[rid]:
            self.ridBets[rid][bet] = 0
        self.ridBets[rid][bet] += amount

    def ClearTableBet(self, rid, bet):
        if rid not in self.ridBets:
            self.ridBets[rid] = {}
        if bet not in self.ridBets[rid]:
            self.ridBets[rid][bet] = 0
        self.ridBets[rid][bet] = 0

    def RemovePlayer(self, rid):
        if rid in self.ridBets:
            self.ridBets.remove(rid)

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
