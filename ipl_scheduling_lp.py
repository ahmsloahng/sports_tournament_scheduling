# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 19:39:04 2021

@author: amlan.ghosh
"""

from pulp import *
import pandas as pd

'''MODEL'''
model = LpProblem('IPL_Scheduling', sense = LpMinimize)


'''PARAMETERS'''
''' 1) Team names and their home ground '''
team_ground = {
                'PBKS': 'Mohali',
                'DC': 'Delhi',
                'RR': 'Jaipur',
                'KKR': 'Kolkata',
                'MI': 'Mumbai',
                'SRH': 'Hyderabad',
                'RCB': 'Bengaluru',
                'CSK': 'Chennai'
              }

''' 2) List of grounds '''
grounds = ['Mohali', 'Delhi', 'Jaipur', 'Kolkata', 'Mumbai', 'Hyderabad', 'Bengaluru', 'Chennai']

''' 3) Distance matrix: Distance between two grounds. Distances are not actual and crazy!!! '''
distance_matrix = {
                    'Mohali': {'Delhi':232, 'Jaipur':428, 'Kolkata':1466, 'Mumbai':1347, 'Hyderabad':1489, 'Bengaluru':1971, 'Chennai':1990},
                    'Delhi': {'Mohali':232, 'Jaipur':269, 'Kolkata':1472, 'Mumbai':1447, 'Hyderabad':1552, 'Bengaluru':2150, 'Chennai':2180},
                    'Jaipur': {'Mohali':428, 'Delhi':269, 'Kolkata':1518, 'Mumbai':1175, 'Hyderabad':1548, 'Bengaluru':2138, 'Chennai':2169},
                    'Kolkata': {'Mohali':1466, 'Delhi':1472, 'Jaipur':1518, 'Mumbai':2014, 'Hyderabad':1460, 'Bengaluru':1871, 'Chennai':1659},
                    'Mumbai': {'Mohali':1347, 'Delhi':1447, 'Jaipur':1175, 'Kolkata':2014, 'Hyderabad':701, 'Bengaluru':981, 'Chennai':1338},
                    'Hyderabad': {'Mohali':1489, 'Delhi':1552, 'Jaipur':1548, 'Kolkata':1460, 'Mumbai':701, 'Bengaluru':566, 'Chennai':629},
                    'Bengaluru': {'Mohali':1971, 'Delhi':2150, 'Jaipur':2138, 'Kolkata':1871, 'Mumbai':981, 'Hyderabad':566, 'Chennai':350},
                    'Chennai': {'Mohali':1990, 'Delhi':2180, 'Jaipur':2169, 'Kolkata':1659, 'Mumbai':1338, 'Hyderabad':629, 'Bengaluru':350}    
                 }

''' 5) Total no. of matches in a round robin league '''
total_matches = int(len(team_ground)*(len(team_ground) - 1))

''' 6) Total no. of rounds in a round robin league '''
total_rounds = int(2*(len(team_ground) - 1))

''' 7) No. of matches in a given round '''
total_matches_in_round = int(len(team_ground)/2)

''' 8) Rounds and match number in a given round '''
round_match = {i:[j for j in range(i*total_matches_in_round,(i+1)*total_matches_in_round)] for i in range(total_rounds)}

''' 9) Match no and their respective rounds '''
match_round = {i:i//total_matches_in_round for i in range(total_matches)}


'''VARIABLES'''
''' 1) Match variable: home team, away tem, ground, match, round '''
var_match = LpVariable.dicts('match', ((home_team,away_team,team_ground[home_team],match,round) 
                                       for home_team in team_ground 
                                       for away_team in team_ground if home_team != away_team 
                                       for round in range(total_rounds) 
                                       for match in round_match[round]), 
                             cat = LpBinary)

''' 2) Trval variable: if any team is travelling from ground 1 to ground 2 in a paritcular round '''
var_travel = LpVariable.dicts('travel', ((team,ground_1,ground_2,round)
                                         for team in team_ground
                                         for ground_1 in grounds
                                         for ground_2 in grounds if ground_1 != ground_2
                                         for round in range(total_rounds - 1)),
                              cat = LpBinary)


'''CONSTRAINTS'''
''' 1) A match of home team and away team can be played only once. '''
for home_team in team_ground:
    for away_team in team_ground:
        if away_team != home_team:
            model += lpSum([var_match[home_team,away_team,team_ground[home_team],match,match_round[match]] 
                            for match in range(total_matches)]) == 1

''' 2) In a given match day, only one match must happen '''
for match in range(total_matches):
    model += lpSum([var_match[home_team,away_team,team_ground[home_team],match,match_round[match]]
                    for home_team in team_ground
                    for away_team in team_ground if home_team != away_team]) == 1

''' 3) A team play one match in a round '''
for team in team_ground:
    for round in range(total_rounds):
        model += lpSum([(var_match[team,opp_team,team_ground[team],match,round]
                          + var_match[opp_team,team,team_ground[opp_team],match,round])
                        for opp_team in team_ground if opp_team != team 
                        for match in round_match[round]]) == 1

''' 4) A team cannot play in two consecutive match days '''
for team in team_ground:
    for match in range(total_matches - 1):
        model += lpSum([(var_match[team,opp_team,team_ground[team],match,match_round[match]]
                        + var_match[team,opp_team,team_ground[team],match+1,match_round[match+1]]
                        + var_match[opp_team,team,team_ground[opp_team],match,match_round[match]]
                        + var_match[opp_team,team,team_ground[opp_team],match+1,match_round[match+1]])
                        for opp_team in team_ground if opp_team != team]) <= 1

''' 5) A team cannot play 3 consecutive home games and away games '''
for team in team_ground:
    for round in range(total_rounds - 2):
        model += lpSum([var_match[team,away_team,team_ground[team],match,r] 
                        for away_team in team_ground if away_team != team
                        for r in range(round,round+3)
                        for match in round_match[r]]) <= 2 #Home

        model += lpSum([var_match[home_team,team,team_ground[home_team],match,r] 
                        for home_team in team_ground if home_team != team
                        for r in range(round,round+3)
                        for match in round_match[r]]) <= 2 #Away

''' 6) First match: MI vs DC'''
#model += var_match['MI','DC','Mumbai',0,0] == 1

''' 7) If a team is playing 
        1) Home game i_th round, Away game (i+1)_th round
        2) Away game i_th round, Home game (i+1)_th round
        3) Away game i_th round, Away game (i+1)_th round
    Then the team is travelling from grond_1 to ground_2 in i_th round 

     Constraint is AND gate formulation '''   
for team in team_ground:
    for round in range(total_rounds - 1):
        for opp_team in team_ground:
            if opp_team != team :
                model += var_travel[team,team_ground[team],team_ground[opp_team],round] <= lpSum([var_match[team,team_1,team_ground[team],match,round] for team_1 in team_ground if team_1 != team for match in round_match[round]]) #playing home match in current round
                model += var_travel[team,team_ground[team],team_ground[opp_team],round] <= lpSum([var_match[opp_team,team,team_ground[opp_team],match_1,round+1] for match_1 in round_match[round+1]]) #playing away match in next round
                model += var_travel[team,team_ground[team],team_ground[opp_team],round] >= lpSum([var_match[team,team_1,team_ground[team],match,round] for team_1 in team_ground if team_1 != team for match in round_match[round]]) + lpSum([var_match[opp_team,team,team_ground[opp_team],match_1,round+1] for match_1 in round_match[round+1]]) - 1
                
                model += var_travel[team,team_ground[opp_team],team_ground[team],round] <= lpSum([var_match[opp_team,team,team_ground[opp_team],match,round] for match in round_match[round]]) #playing away match in current round
                model += var_travel[team,team_ground[opp_team],team_ground[team],round] <= lpSum([var_match[team,team_1,team_ground[team],match_1,round+1] for team_1 in team_ground if team_1!= team for match_1 in round_match[round+1]]) #playing home game in next round
                model += var_travel[team,team_ground[opp_team],team_ground[team],round] >= lpSum([var_match[opp_team,team,team_ground[opp_team],match,round] for match in round_match[round]]) + lpSum([var_match[team,team_1,team_ground[team],match_1,round+1] for team_1 in team_ground if team_1 != team for match_1 in round_match[round+1]]) - 1

for team in team_ground:
    for roun in range(total_rounds - 1):
        for away_team_1 in team_ground:
            if away_team_1 != team :
                for away_team_2 in team_ground:
                    if away_team_2 != team and away_team_2 != away_team_1 :
                        model += var_travel[team,team_ground[away_team_1],team_ground[away_team_2],round] <= lpSum([var_match[away_team_1,team,team_ground[away_team_1],match,round] for match in round_match[round]]) #playing away game in current round
                        model += var_travel[team,team_ground[away_team_1],team_ground[away_team_2],round] <= lpSum([var_match[away_team_2,team,team_ground[away_team_2],match_1,round+1] for match_1 in round_match[round+1]]) #playing away game in next round
                        model += var_travel[team,team_ground[away_team_1],team_ground[away_team_2],round] >= lpSum([var_match[away_team_1,team,team_ground[away_team_1],match,round] for match in round_match[round]]) + lpSum([var_match[away_team_2,team,team_ground[away_team_2],match_1,round+1] for match_1 in round_match[round+1]]) - 1  

'''OBJECTIVE'''
model += (lpSum([var_travel[team,ground_1,ground_2,round]*distance_matrix[ground_1][ground_2] 
               for ground_1 in grounds 
               for ground_2 in grounds if ground_1 != ground_2 
               for team in team_ground
               for round in range(total_rounds - 1)]) 
          + lpSum([var_match[home_team,away_team,team_ground[home_team],match,0]*distance_matrix[team_ground[home_team]][team_ground[away_team]]
                   for home_team in team_ground
                   for away_team in team_ground if home_team != away_team
                   for match in round_match[0]]))

''' PRINITING THE LP FILE '''
model.writeLP('ipl_scheduling_lp.lp', writeSOS = 1, mip = 1)

''' SOLVING THE MODEL AND PRINTING THE LOG '''
model.solve(PULP_CBC_CMD(msg = 1, logPath = 'status.log'))

''' PRINTING THE STATUS '''
print("Status",LpStatus[model.status])

'''PRINITING THE SCHEDULE '''

list_round = []
list_match = []
list_home_team = []
list_away_team = []
list_ground = []

for round in range(total_rounds):
    for match in round_match[round]:
        for home_team in team_ground:
            for away_team in team_ground:
                if home_team != away_team:
                    if var_match[home_team,away_team,team_ground[home_team],match,round].varValue == 1:
                        list_round.append(round + 1)
                        list_match.append('Match '+str(match + 1))
                        list_home_team.append(home_team)
                        list_away_team.append(away_team)
                        list_ground.append(team_ground[home_team])

schedule_dict = {
                    'Round': list_round,
                    'Match': list_match,
                    'Team (Home)': list_home_team,
                    'Team (Away)': list_away_team,
                    'Venue': list_ground
                }

df = pd.DataFrame(schedule_dict, columns = ['Round','Match','Team (Home)','Team (Away)','Venue'])

df.to_excel('IPL Schedule.xlsx', sheet_name = 'Schedule', index = False)





 


