#! /usr/bin/python3.9
import numpy as np
import csv
import sys

nTeamDetails = len(sys.argv) - 1
if nTeamDetails > 0:
    teamDetails = sys.argv[1:nTeamDetails+1]


seasonFile = 'data/2021season.csv'
teamsFile  = 'data/2021fbs.csv'
extendedPrint = True

maxIts = 10000
tol = 1e-14
maxWeek = 13
maxWeekRemaining = 15
outputPrecision = 7

rankstrings = [('(' + str(i+1) + ') ') for i in range(25)]
nameSwaps = [['Central Florida','UCF'],['Pittsburgh','Pitt'],['Alabama-Birmingham','UAB'],['Texas-San Antonio','UTSA'],
             ['Texas-El Paso','UTEP'],['Southern Methodist','SMU'],['Brigham Young','BYU'],['Mississippi','Ole Miss'],
             ['Louisiana State','LSU'],['Southern California','USC']]
season = []
with open(seasonFile, newline='') as csvfile:
    gameData = csv.reader(csvfile, delimiter=',')
    header = next(gameData, None)  # skip the header
    wIndex = header.index('Winner')
    lIndex = header.index('Loser')
    for game in gameData:
        name1 = game[wIndex]
        name2 = game[lIndex]
        for rank in rankstrings:
            name1 = name1.replace(rank,'')
            name2 = name2.replace(rank,'')
        for swap in nameSwaps:
            if name1 == swap[0]:
                name1 = swap[1]
            if name2 == swap[0]:
                name2 = swap[1]
        season.append([int(game[1]),name1,name2])

teams = []
with open(teamsFile, newline='') as csvfile:
    teamData = csv.reader(csvfile, delimiter=',')
    next(teamData, None)  # skip the header
    next(teamData, None)  # skip the header
    for team in teamData:
        teams.append(team[1])
maxNameLength = max([len(team) for team in teams])

nTeam = len(teams)
winLossMatrix = [[ [] for i in range(nTeam+1)] for j in range(nTeam+1)]
remainingSchedule = [[ [] for i in range(nTeam+1)] for j in range(nTeam+1)]
teams.append('Non-FBS')

gamesPlayed = np.zeros(nTeam+1)
gamesRemaining = np.zeros(nTeam+1)
ws = np.zeros(nTeam+1)
ls = np.zeros(nTeam+1)
for game in season:
    try:
        winner = teams.index(game[1])
    except ValueError:
        winner = nTeam
    try:
        loser  = teams.index(game[2])
    except ValueError:
        loser = nTeam
    if int(game[0]) <= maxWeek:
        winLossMatrix[winner][loser].append(1)
        winLossMatrix[loser][winner].append(-1)
        gamesPlayed[winner] += 1
        gamesPlayed[loser]  += 1
        ws[winner] += 1
        ls[loser]  += 1
    elif int(game[0]) <= maxWeekRemaining:
        remainingSchedule[winner][loser].append(1)
        remainingSchedule[loser][winner].append(1)
        gamesRemaining[winner] += 1
        gamesRemaining[loser]  += 1

naw = np.ones(nTeam+1)
newNAW = np.ones(nTeam)
for j in range(maxIts):
    naw[nTeam] = min(newNAW) - 1
    nawScale = max(np.abs(newNAW))
    for i in range(nTeam):
        newNAW[i] = 0
        for k in range(nTeam+1):
            for l in range(len(winLossMatrix[i][k])):
                newNAW[i] = newNAW[i] + winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale)
    maxDiff = np.amax(np.abs(newNAW-naw[0:nTeam]))
    naw[:-1] = np.copy(newNAW)
    iterations = j + 1
    if maxDiff < tol:
        break

ncs = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(winLossMatrix[i][k])):
            ncs[i] = ncs[i] + np.exp(naw[k]/nawScale)

nawScale = max(np.abs(newNAW))
awe = naw / np.amax([gamesPlayed,np.ones(nTeam+1)],axis=0)
nrs = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(remainingSchedule[i][k])):
            nrs[i] = nrs[i] + remainingSchedule[i][k][l]*np.exp(naw[k]/nawScale)

ranks    = list(reversed(np.argsort(naw)))
aweranks = list(reversed(np.argsort(awe)))
ncsranks = list(reversed(np.argsort(ncs)))
nrsranks = list(reversed(np.argsort(nrs)))

print()
if nTeamDetails == 0:
    print(f'Ranks to week {maxWeek} after {iterations} iterations:')
    print()
    print(f'| Rank | {"Team":{maxNameLength}} |     NAW     |{"     AWE     |     NCS     |     NRS     | Record  |" if extendedPrint else ""}')
    print(f'|------|{"-"*(maxNameLength+2)}|-------------|{"-------------|-------------|-------------|---------|" if extendedPrint else ""}')
    for i in range(nTeam):
        print(f'| {i+1:4} | {teams[ranks[i]]:{maxNameLength}} | {naw[ranks[i]]:11.{outputPrecision}f} | {f"{awe[ranks[i]]:11.{outputPrecision}f} | {ncs[ranks[i]]:11.{outputPrecision}f} | {nrs[ranks[i]]:11.{outputPrecision}f} | {int(ws[ranks[i]]):2d} - {int(ls[ranks[i]]):2d} |" if extendedPrint else ""}')
else:
    for team in teamDetails:
        if team in teams:
            i = teams.index(team)
            if gamesPlayed[i] > 0:
                print(f'{team} ({int(ws[i])} - {int(ls[i])})')
                print(f'|       |     NAW     |     AWE     |     NCS     |     NRS     |')
                print(f'|-------|-------------|-------------|-------------|-------------|')
                print(f'| Value | {naw[i]:11.{outputPrecision}f} | {awe[i]:11.{outputPrecision}f} | {ncs[i]:11.{outputPrecision}f} | {nrs[i]:11.{outputPrecision}f} |')
                print(f'| Rank  | {ranks.index(i)+1:11d} | {aweranks.index(i)+1:11d} | {ncsranks.index(i)+1:11d} | {nrsranks.index(i)+1:11d} |')
                print()
                print(f'|{" Played":{maxNameLength+5}}| Outcome    | Change     |')
                print(f'|{"-"*(maxNameLength+5)}|------------|------------|')
                for k in range(nTeam+1):
                    for l in range(len(winLossMatrix[i][k])):
                        print(f'|{ranks.index(k)+1:4} {teams[k]:{maxNameLength}}|{" Win        " if winLossMatrix[i][k][l]==1 else " Loss       "}| {"+" if winLossMatrix[i][k][l]==1 else ""}{winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale):.{outputPrecision}f} |')
                print()
            if gamesRemaining[i] > 0:
                print(f'|{" Remaining":{maxNameLength+5}}| If Win     | If Loss    |')
                print(f'|{"-"*(maxNameLength+5)}|------------|------------|')
                for k in range(nTeam+1):
                    for l in range(len(remainingSchedule[i][k])):
                        print(f'|{ranks.index(k)+1:4} {teams[k]:{maxNameLength}}| +{np.exp(naw[k]/nawScale):.{outputPrecision}f} | {-np.exp(-naw[k]/nawScale):.{outputPrecision}f} |')
                print()
