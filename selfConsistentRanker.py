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
outputPrecision = 8

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
        gamesPlayed[winner] = gamesPlayed[winner] + 1
        gamesPlayed[loser]  = gamesPlayed[loser]  + 1
    elif int(game[0]) <= maxWeekRemaining:
        remainingSchedule[winner][loser].append(1)
        remainingSchedule[loser][winner].append(1)
        gamesRemaining[winner] = gamesRemaining[winner] + 1
        gamesRemaining[loser]  = gamesRemaining[loser]  + 1

strength = np.ones(nTeam+1)
newStrength = np.ones(nTeam)
for j in range(maxIts):
    strength[nTeam] = min(newStrength) - 1
    strengthScale = max(np.abs(newStrength))
    for i in range(nTeam):
        newStrength[i] = 0
        for k in range(nTeam+1):
            for l in range(len(winLossMatrix[i][k])):
                newStrength[i] = newStrength[i] + winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*strength[k]/strengthScale)
    maxDiff = np.amax(np.abs(newStrength-strength[0:nTeam]))
    strength[:-1] = np.copy(newStrength)
    iterations = j + 1
    if maxDiff < tol:
        break

sos = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(winLossMatrix[i][k])):
            sos[i] = sos[i] + np.exp(strength[k]/strengthScale)

strengthScale = max(np.abs(newStrength))
power = strength / np.amax([gamesPlayed,np.ones(nTeam+1)],axis=0)
srs = np.zeros(nTeam)
prs = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(remainingSchedule[i][k])):
            srs[i] = srs[i] + remainingSchedule[i][k][l]*np.exp(strength[k]/strengthScale)
            prs[i] = prs[i] + remainingSchedule[i][k][l]*power[k]
prs = prs / np.amax([gamesRemaining[:-1],np.ones(nTeam)],axis=0)

ranks = list(reversed(np.argsort(strength)))
sosranks = list(reversed(np.argsort(sos)))

print()
if nTeamDetails == 0:
    print(f'Ranks to week {maxWeek} after {iterations} iterations:')
    print()
    print(f'| Rank |{"Team":{maxNameLength}}| Strength |{"   Power  |    SOS   |    SRS   |    PRS   |" if extendedPrint else ""}')
    print(f'|------|{"-"*maxNameLength}|----------|{"----------|----------|----------|----------|" if extendedPrint else ""}')
    for i in range(nTeam):
        print(f'|{i+1:6}|{teams[ranks[i]]:{maxNameLength}}|{strength[ranks[i]]:.{outputPrecision}f}|{f"{power[ranks[i]]:.{outputPrecision}f}|{sos[ranks[i]]:.{outputPrecision}f}|{srs[ranks[i]]:.{outputPrecision}f}|{prs[ranks[i]]:.{outputPrecision}f}|" if extendedPrint else ""}')
else:
    for team in teamDetails:
        if team in teams:
            i = teams.index(team)
            if gamesPlayed[i] > 0:
                print(f'{team}')
                print(f'Ranked {ranks.index(i)+1} with strength {strength[i]:.{outputPrecision}f}')
                print(f'Strength of schedule ranked {sosranks.index(i)+1} with {sos[i]:.{outputPrecision}f}')
                print(f'|{" Played":{maxNameLength+5}}| Outcome    | Change     |')
                print(f'|{"-"*(maxNameLength+5)}|------------|------------|')
                for k in range(nTeam+1):
                    for l in range(len(winLossMatrix[i][k])):
                        print(f'|{ranks.index(k)+1:4} {teams[k]:{maxNameLength}}|{" Win        " if winLossMatrix[i][k][l]==1 else " Loss       "}| {"+" if winLossMatrix[i][k][l]==1 else ""}{winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*strength[k]/strengthScale):.{outputPrecision}f}|')
                print()
            if gamesRemaining[i] > 0:
                print(f'|{" Remaining":{maxNameLength+5}}| If Win     | If Loss    |')
                print(f'|{"-"*(maxNameLength+5)}|------------|------------|')
                for k in range(nTeam+1):
                    for l in range(len(remainingSchedule[i][k])):
                        print(f'|{ranks.index(k)+1:4} {teams[k]:{maxNameLength}}| +{np.exp(strength[k]/strengthScale):.{outputPrecision}f}| {-np.exp(-strength[k]/strengthScale):.{outputPrecision}f}|')
                print()
