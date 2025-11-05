#! /usr/bin/python3
import numpy as np
import csv
import sys
import pandas as pd
import pickle
from functions import general as gen
import os
import re

nTeamDetails = 0
pickling = False
saveAllTeams = True
printTeam = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'pickle':
        pickling = True
    else:
        printTeam = True
        nTeamDetails = len(sys.argv) - 1
        if nTeamDetails > 0:
            teamDetails = sys.argv[1:nTeamDetails+1]

season = '2025'
seasonFile = f'data/{season}season.csv'
teamsFile  = f'data/{season}fbs.csv'
extendedPrint = True

maxIts = 10000
tol = 1e-14
maxWeek = 11
maxWeekRemaining = 16

rankstrings = [(f'({i+1}) ') for i in range(25)]
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

if saveAllTeams:
    nTeamDetails = nTeam
    teamDetails = teams

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

naw = ws - ls
newNAW = np.copy(naw[0:-1])
for j in range(maxIts):
    naw[nTeam] = min(newNAW) * 1.1
    nawScale = (max(newNAW)-min(newNAW))/2
    for i in range(nTeam):
        newNAW[i] = 0
        for k in range(nTeam+1):
            for l in range(len(winLossMatrix[i][k])):
                newNAW[i] += winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale)
    maxDiff = np.amax(np.abs(newNAW-naw[0:nTeam]))
    naw[:-1] = np.copy(newNAW)
    iterations = j + 1
    if maxDiff < tol:
        break

ncs = np.zeros(nTeam+1)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(winLossMatrix[i][k])):
            ncs[i] = ncs[i] + np.exp(naw[k]/nawScale)

nawScale = max(np.abs(newNAW))
aaw = naw / np.amax([gamesPlayed,np.ones(nTeam+1)],axis=0)
nrs = np.zeros(nTeam+1)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(remainingSchedule[i][k])):
            nrs[i] = nrs[i] + remainingSchedule[i][k][l]*np.exp(naw[k]/nawScale)

aaw[-1] = -np.inf
ncs[-1] = -np.inf
nrs[-1] = -np.inf

ranks    = list(reversed(np.argsort(naw)))
# use sort instead of argsort here to allow ties
naworder = list(reversed(np.sort(naw)))
aaworder = list(reversed(np.sort(aaw)))
ncsorder = list(reversed(np.sort(ncs)))
nrsorder = list(reversed(np.sort(nrs)))

# Formatting
fnd = 3         # float number of decimals (choose odd)
ffw = fnd + 4   # float full width, :{ffw}.{fnd}f
ifw = 4         # integer full width, :{ifw}d
tlp = ' '*int((fnd+3)/2)    # padding around 3-letter strings
tbs = '-'*int(ffw+2)        # table border segment

print()
if not printTeam:
    print(f'Ranks to week {maxWeek-1} after {iterations} iterations:')
    print()
    print(f'| Rank | {"Team":{maxNameLength}} |{tlp}NAW{tlp}|{f"{tlp}AAW{tlp}|{tlp}NCS{tlp}|{tlp}NRS{tlp}| Record  |" if extendedPrint else ""}')
    print(f'|------|{"-"*(maxNameLength+2)}|{tbs}|{f"{tbs}|{tbs}|{tbs}|---------|" if extendedPrint else ""}')
    for i in range(nTeam):
        print(f'| {naworder.index(naw[ranks[i]])+1:{ifw}} | [{teams[ranks[i]]:{maxNameLength}}](teams/{re.sub(r"[^a-zA-Z0-9]","",teams[ranks[i]])}.md) | {naw[ranks[i]]:{ffw}.{fnd}f} | {f"{aaw[ranks[i]]:{ffw}.{fnd}f} | {ncs[ranks[i]]:{ffw}.{fnd}f} | {nrs[ranks[i]]:{ffw}.{fnd}f} | {int(ws[ranks[i]]):2d} - {int(ls[ranks[i]]):2d} |" if extendedPrint else ""}')

for team in teamDetails:
    if team in teams:
        i = teams.index(team)
        teamOutput = []
        if gamesPlayed[i] > 0:
            teamOutput.append(f'{team} ({int(ws[i])} - {int(ls[i])})')
            teamOutput.append(f'|       |{tlp}NAW{tlp}|{tlp}AAW{tlp}|{tlp}NCS{tlp}|{tlp}NRS{tlp}|')
            teamOutput.append(f'|-------|{tbs}|{tbs}|{tbs}|{tbs}|')
            teamOutput.append(f'| Value | {naw[i]:{ffw}.{fnd}f} | {aaw[i]:{ffw}.{fnd}f} | {ncs[i]:{ffw}.{fnd}f} | {nrs[i]:{ffw}.{fnd}f} |')
            teamOutput.append(f'| Rank  | {naworder.index(naw[i])+1:{ffw}d} | {aaworder.index(aaw[i])+1:{ffw}d} | {ncsorder.index(ncs[i])+1:{ffw}d} | {nrsorder.index(nrs[i])+1:{ffw}d} |')
            teamOutput.append('')
            teamOutput.append(f'|{" Played":{maxNameLength+5}}| Outcome    |{tlp[1:]}Change{tlp[1:]}|')
            teamOutput.append(f'|{"-"*(maxNameLength+5)}|------------|-{tbs}|')
            for j in range(nTeam+1):
                k = ranks[j]
                for l in range(len(winLossMatrix[i][k])):
                    teamOutput.append(f'|{naworder.index(naw[k])+1:{ifw}} [{teams[k]:{maxNameLength}}]({re.sub(r"[^a-zA-Z0-9]","",teams[k])}.md)|{" Win        " if winLossMatrix[i][k][l]==1 else " Loss       "}| {"+" if winLossMatrix[i][k][l]==1 else "-"}{np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale):{ffw}.{fnd}f} |')
            teamOutput.append('')
        if gamesRemaining[i] > 0:
            teamOutput.append(f'|{" Remaining":{maxNameLength+5}}|{tlp[1:]}If Win{tlp[1:]}|{tlp[1:]}If Loss{tlp[2:]}|')
            teamOutput.append(f'|{"-"*(maxNameLength+5)}|-{tbs}|-{tbs}|')
            for j in range(nTeam+1):
                k = ranks[j]
                for l in range(len(remainingSchedule[i][k])):
                    teamOutput.append(f'|{naworder.index(naw[k])+1:{ifw}} [{teams[k]:{maxNameLength}}]({re.sub(r"[^a-zA-Z0-9]","",teams[k])}.md)| +{np.exp(naw[k]/nawScale):{ffw}.{fnd}f} | -{np.exp(-naw[k]/nawScale):{ffw}.{fnd}f} |')
            teamOutput.append('')
        if printTeam: [print(t) for t in teamOutput]
        with open(f'teams/{re.sub(r"[^a-zA-Z0-9]","",team)}.md', 'w') as file:
            for s in teamOutput:
                file.write(s + '\n')

if pickling:
    pickleFile = 'ncaafb.p'
    try:
        d = pd.read_pickle(pickleFile)
    except FileNotFoundError:
        gen.dbInit(pickleFile)
        d = pd.read_pickle(pickleFile)
    ldf = []
    for i in range(nTeam):
        rank = f'{naworder.index(naw[ranks[i]])+1:{ifw}}'
        team = teams[ranks[i]]
        tNaw = f'{naw[ranks[i]]:{ffw}.{fnd}f}'
        tAaw = f'{aaw[ranks[i]]:{ffw}.{fnd}f}'
        tNcs = f'{ncs[ranks[i]]:{ffw}.{fnd}f}'
        tNrs = f'{nrs[ranks[i]]:{ffw}.{fnd}f}'
        record = f'{int(ws[ranks[i]])} - {int(ls[ranks[i]])}'
        ldf.append([rank,team,tNaw,tAaw,tNcs,tNrs,record])
    df = pd.DataFrame(ldf,columns=['Rank','Team','NAW','AAW','NCS','NRS','Record'])
    df.sort_values(['Rank'],inplace=True)
    d['analysis']['teamRankings'] = df
    pickle.dump(d, open(os.path.join(pickleFile), 'wb'))
    d['analysis']['byTeam'] = dict()

    for team in teams:
        i = teams.index(team)
        v = dict()
        v['team'] = f'{team} ({int(ws[i])} - {int(ls[i])})'
        d['analysis']['byTeam'][team] = v
        if gamesPlayed[i] > 0:
            # make stats summary table
            tNaw = f'{naw[i]:{ffw}.{fnd}f}'
            tAaw = f'{aaw[i]:{ffw}.{fnd}f}'
            tNcs = f'{ncs[i]:{ffw}.{fnd}f}'
            tNrs = f'{nrs[i]:{ffw}.{fnd}f}'
            rNaw = f'{naworder.index(naw[i])+1:{ffw}d}'
            rAaw = f'{aaworder.index(aaw[i])+1:{ffw}d}'
            rNcs = f'{ncsorder.index(ncs[i])+1:{ffw}d}'
            rNrs = f'{nrsorder.index(nrs[i])+1:{ffw}d}'
            ldf = [[tNaw,tAaw,tNcs,tNrs],[rNaw,rAaw,rNcs,rNrs]]
            df = pd.DataFrame(ldf,columns=['NAW','AAW','NCS','NRS'])
            d['analysis']['byTeam'][team]['stats'] = df
            pickle.dump(d, open(os.path.join(pickleFile), 'wb'))
            # make games played/results table
            ldf = []
            for j in range(nTeam+1):
                k = ranks[j]
                for l in range(len(winLossMatrix[i][k])):
                    opponent = f'{naworder.index(naw[k])+1:4} {teams[k]:{maxNameLength}}'
                    outcome = f'{"Win" if winLossMatrix[i][k][l]==1 else "Loss"}'
                    change = f'{"+" if winLossMatrix[i][k][l]==1 else "-"}{np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale):{ffw}.{fnd}f}'
                    ldf.append([opponent,outcome,change])
            df = pd.DataFrame(ldf,columns=['Played','Outcome','Change'])
            d['analysis']['byTeam'][team]['results'] = df
            pickle.dump(d, open(os.path.join(pickleFile), 'wb'))
        else:
            # dump empty if no games played
            d['analysis']['byTeam'][team]['stats'] = []
            d['analysis']['byTeam'][team]['results'] = []
        if gamesRemaining[i] > 0:
            # make games remaining table
            ldf = []
            for j in range(nTeam+1):
                k = ranks[j]
                for l in range(len(remainingSchedule[i][k])):
                    opponent = f'{naworder.index(naw[k])+1:{ifw}} {teams[k]:{maxNameLength}}'
                    cifw = f'+{np.exp(naw[k]/nawScale):{ffw}.{fnd}f}'
                    cifl = f'-{np.exp(-naw[k]/nawScale):{ffw}.{fnd}f}'
                    ldf.append([opponent,cifw,cifl])
            df = pd.DataFrame(ldf,columns=['Remaining','If Win','If Loss'])
            d['analysis']['byTeam'][team]['remaining'] = df
            pickle.dump(d, open(os.path.join(pickleFile), 'wb'))
        else:
            # dump empty if no games remaining
            d['analysis']['byTeam'][team]['remaining'] = []

    d['analysis']['week'] = str(maxWeek-1)
    teams.sort()
    d['data']['teams']= teams
    pickle.dump(d, open(os.path.join(pickleFile), 'wb'))
