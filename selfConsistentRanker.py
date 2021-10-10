#! /usr/bin/python3.9
import numpy as np
import csv

seasonFile = 'data/2021season.csv'
teamsFile  = 'data/2021fbs.csv'
extendedPrint = True

maxIts = 10000
tol = 1e-14
maxWeek = 7
maxWeekRemaining = 15
outputPrecision = 8

rankstrings = [('(' + str(i+1) + ') ') for i in range(25)]
nameSwaps = [['Central Florida','UCF'],['Pittsburgh','Pitt'],['Alabama-Birmingham','UAB'],['Texas-San Antonio','UTSA'],
             ['Texas-El Paso','UTEP'],['Southern Methodist','SMU'],['Brigham Young','BYU'],['Mississippi','Ole Miss'],
             ['Louisiana State','LSU'],['Southern California','USC']]
season = []
with open(seasonFile, newline='') as csvfile:
    gameData = csv.reader(csvfile, delimiter=',')
    next(gameData, None)  # skip the header
    for game in gameData:
        name1 = game[5]
        name2 = game[8]
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
        for k in range(nTeam):
            for l in range(len(winLossMatrix[i][k])):
                newStrength[i] = newStrength[i] + winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*strength[k]/strengthScale)
    maxDiff = np.amax(np.abs(newStrength-strength[0:nTeam]))
    strength[:-1] = np.copy(newStrength)
    iterations = j + 1
    if maxDiff < tol:
        break

strengthScale = max(np.abs(newStrength))
power = strength / np.amax([gamesPlayed,np.ones(nTeam+1)])
srs = np.zeros(nTeam)
prs = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam):
        for l in range(len(remainingSchedule[i][k])):
            srs[i] = srs[i] + remainingSchedule[i][k][l]*np.exp(strength[k]/strengthScale)
            prs[i] = prs[i] + remainingSchedule[i][k][l]*power[k]
prs = prs / np.amax([gamesRemaining[:-1],np.ones(nTeam)])

ranks = list(reversed(np.argsort(strength)))
print(f'Ranks after {iterations} iterations:')
print()
print(f'| Rank |{"Team":{maxNameLength}}| Strength |{"   Power  |    SRS   |    PRS   |" if extendedPrint else ""}')
print(f'|------|{"-"*maxNameLength}|----------|{"----------|----------|----------|" if extendedPrint else ""}')
for i in range(nTeam):
    print(f'|{i+1:6}|{teams[ranks[i]]:{maxNameLength}}|{strength[ranks[i]]:.{outputPrecision}f}|{f"{power[ranks[i]]:.{outputPrecision}f}|{srs[ranks[i]]:.{outputPrecision}f}|{prs[ranks[i]]:.{outputPrecision}f}|" if extendedPrint else ""}')
