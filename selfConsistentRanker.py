#! /usr/bin/python3.9
import numpy as np
import csv

seasonFile = '2021season-week4.csv'
teamsFile  = '2021fbs.csv'

maxIts = 1000
tol = 1e-15
maxWeek = 100 # set to 17 for pre-bowl games

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

nTeam = len(teams)
winLossMatrix = [[ [] for i in range(nTeam+1)] for j in range(nTeam+1)]
teams.append('Non-FBS')

for game in season:
    if int(game[0]) > maxWeek:
        break
    try:
        winner = teams.index(game[1])
    except ValueError:
        winner = nTeam
    try:
        loser  = teams.index(game[2])
    except ValueError:
        loser = nTeam
    winLossMatrix[winner][loser].append(1)
    winLossMatrix[loser][winner].append(-1)

strength = np.ones(nTeam+1)
newStrength = np.ones(nTeam)
for j in range(maxIts):
    strength[nTeam] = min(strength[:nTeam-1]-1)
    strengthSum = sum(np.abs(strength))
    for i in range(nTeam):
        newStrength[i] = 0
        for k in range(nTeam):
            for l in range(len(winLossMatrix[i][k])):
                newStrength[i] = newStrength[i] + winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*strength[k]/strengthSum)
    maxDiff = np.amax(np.abs(newStrength-strength[:-1]))
    strength[:-1] = np.copy(newStrength)
    iterations = j
    if maxDiff < tol:
        break

ranks = list(reversed(np.argsort(strength)))
print(f'Ranks after {iterations} iterations:')
for i in range(nTeam):
    print(f'{i+1} {teams[ranks[i]]} {strength[ranks[i]]}')
