#!/usr/bin/python2.7
#from numpy import genfromtxt
import pandas as pd
import numpy as np
import sys


def create_dictionary_from_dataframe(dat):
	dictionary = {}
	game_dictionary = {}

	df1 = dat.replace(np.nan,'#', regex=True)
	
	for play in df1.iterrows():
		p = dict(play[1])
		play = {k.lower(): v for k, v in p.items()}	
		
		offensive_team = str(play['offenseteam'])
		defensive_team = str(play['defenseteam'])
			
		game_id = play['gameid']
			
		if ( game_id not in game_dictionary ):
			game_dictionary[game_id] = {}
			game_dictionary[game_id]['awayteam'] = defensive_team
			game_dictionary[game_id]['awaytimeouts'] = [0,0,0,0,0,0]
			game_dictionary[game_id]['hometimeouts'] = [0,0,0,0,0,0]
		
		
		if(offensive_team != "#" and defensive_team != "#"):
			game_date = play['gamedate']
			
			game_dictionary[game_id]['teamone'] = offensive_team
			game_dictionary[game_id]['teamtwo'] = defensive_team
			if ( defensive_team not in dictionary ):
				dictionary[defensive_team] = {}
		
			if ( offensive_team not in dictionary ):
				dictionary[offensive_team] = {}
			
			if ( game_date not in dictionary[defensive_team] ):
				dictionary[defensive_team][game_date] = []
		
			if ( game_date not in dictionary[offensive_team] ):
				dictionary[offensive_team][game_date] = []
		
			dictionary[defensive_team][game_date].append(play)
			dictionary[offensive_team][game_date].append(play)
		elif( offensive_team == "#" ):
			game_dictionary[game_id]['awayteam'] = defensive_team
#
#			elif(play['playtype'] == 'TIMEOUT'):
#				splitter = play['description'].split(' ')
#				timeout = splitter[1][1]
#				index = int(timeout) - 1
#				print index
#				team = splitter[3]
#				if(team == game_dictionary[game_id]['awayteam']):
#				 	game_dictionary[game_id]['awaytimeouts'][index] = play['quarter']
#				else:
#					game_dictionary[game_id]['hometimeouts'][index] = play['quarter']
				
			
			
	return dictionary, game_dictionary

def output_stats( dictionary ):
	for team, game_date_dictionary in dictionary.iteritems():
		print team
		for game_date, sets in game_date_dictionary.iteritems():
			print "\t"+game_date
			for play in sets:
				print play				

def get_total_game_yards( team, game_plays ):
	team_one_points = 0
	team_two_points = 0
	team_one_game_yards = 0
	team_two_game_yards = 0
	team_one_passing_yards = 0
	team_two_passing_yards = 0
	team_one_rushing_yards = 0
	team_two_rushing_yards = 0
	team_one_penalty_yards = 0
	team_two_penalty_yards = 0
	
	for play in game_plays:
		if (str(play['isnoplay']) == '0'):
			yards = play['yards']
			if(str(play['offenseteam']) == team):
				if( play['isinterception'] == 0):
					team_one_game_yards += yards
					if( play['ispass'] == 1 ):
						team_one_passing_yards += yards
					elif( play['isrush'] == 1):
						team_one_rushing_yards += yards
					if( play['playtype'] == 'EXTRA POINT'):
						if( is_good(play)):
							team_one_points += 1
					elif( play['playtype'] == 'FIELD GOAL'):
						if( play['istouchdown'] == 1):
							team_two_points += 6
						elif( is_good(play)):
							team_one_points += 3
					elif( play['istouchdown'] == 1):
						if( play['isfumble'] == 1):
							print 'hey'
							if( defense_TD(play)):
								print 'ho'
								team_two_points += 6
							else:
								team_one_points += 6
						else:
							team_one_points += 6				
					elif( play['istwopointconversion'] == 1):
						if( play['istwopointconversionsuccessful'] == 1):
							team_one_points += 2
					elif( play['yards'] <= 0):
						if( is_safety(play)):
							team_two_points += 2
				else:
					team_two_game_yards += yards
					
			else:
				if( play['isinterception'] == 0):
					team_two_game_yards += yards
					if( play['ispass'] == 1 ):
						team_two_passing_yards += yards
					elif( play['isrush'] == 1):
						team_two_rushing_yards += yards
					if( play['playtype'] == 'EXTRA POINT'):
						if( is_good(play)):
							team_two_points += 1
					elif( play['playtype'] == 'FIELD GOAL'):
						if( play['istouchdown'] == 1):
							team_one_points += 6
						elif( is_good(play)):
							team_two_points += 3
					elif( play['istouchdown'] == 1):
						if( play['isfumble'] == 1):
							if( defense_TD(play)):
								team_one_points += 6
							else:
								team_two_points += 6
						else:
							team_two_points += 6				
					elif( play['istwopointconversion'] == 1):
						if( play['istwopointconversionsuccessful'] == 1):
							team_two_points += 2
					elif( play['yards'] <= 0):
						if( is_safety(play)):
							team_one_points += 2
				else:
					team_one_game_yards += yards
		else:
			if( is_safety(play)):
				if( play['offenseteam'] == team):
					team_two_points += 2
				else:
					team_one_points += 2
		if(play['ispenaltyaccepted'] == 1):
			if(str(play['penaltyteam']) == team):
				team_one_penalty_yards += play['penaltyyards']
			else:
				team_two_penalty_yards += play['penaltyyards']
					

	print "\t\tteam one yards = " + str(team_one_game_yards) + "\t\tteam two yards = " + str(team_two_game_yards)
	print "\t\tteam one passing yards = " + str(team_one_passing_yards) + "\tteam two passing yards = " + str(team_two_passing_yards)
	print "\t\tteam one rushing yards = " + str(team_one_rushing_yards) + "\tteam two rushing yards = " + str(team_two_rushing_yards)
	print "\t\tteam one penalty yards = " + str(team_one_penalty_yards) + "\tteam two penalty yards = " + str(team_two_penalty_yards)
	print "\t\tteam one points = " + str(team_one_points) + "\tteam two points = " + str(team_two_points)
	return [str(team_one_game_yards), str(team_two_game_yards),
	str(team_one_rushing_yards), str(team_two_rushing_yards),
	str(team_one_passing_yards), str(team_two_passing_yards),
	str(team_one_penalty_yards), str(team_two_penalty_yards),
	str(team_one_points), str(team_two_points)]
			

def get_game_sif( team, game_plays ):
	team_one_sacks = 0
	team_two_sacks = 0
	team_one_interceptions = 0
	team_two_interceptions = 0
	team_one_fumbles = 0
	team_two_fumbles = 0
	
	for play in game_plays:
		if(str(play['offenseteam']) == team):
			if( play['issack'] == 1):
				team_two_sacks += 1
			if( play['isinterception'] == 1):
				team_one_interceptions += 1
			if( play['isfumble'] == 1 ):
				team_one_fumbles += 1
		else:		
			if( play['issack'] == 1):
				team_one_sacks += 1
			if( play['isinterception'] == 1):
				team_two_interceptions += 1
			if( play['isfumble'] == 1 ):
				team_two_fumbles += 1
					

	print "\t\tteam one sacks = " + str(team_one_sacks) + "\t\tteam two sacks = " + str(team_two_sacks)
	print "\t\tteam one interceptions = " + str(team_one_interceptions) + "\tteam two interceptions = " + str(team_two_interceptions)
	print "\t\tteam one fumbles = " + str(team_one_fumbles) + "\t\tteam two fumbles = " + str(team_two_fumbles)
	return [str(team_one_sacks), str(team_two_sacks),
	str(team_one_interceptions), str(team_two_interceptions),
	str(team_one_fumbles), str(team_two_fumbles)]


def get_general_game_info(game_dictionary, game_id):
	game = game_dictionary[game_id]
	away_team = str(game['awayteam'])
	team_one = str(game['teamone'])
	team_two = str(game['teamtwo'])
	if( away_team == team_one):
		home_team = team_two
	else:
		home_team = team_one
	
	print "\t\thome team = " + home_team + "\t\taway team = " + away_team
#	print "\t\thome timeout 1 Q.= " + str(game['hometimeouts'][0])\
#	+ "\thome timeout 2 Q.= " + str(game['hometimeouts'][1])\
#	+ "\thome timeout 3 Q.= " + str(game['hometimeouts'][2])
	
#	print "\t\taway timeout 1 Q.= " + str(game['awaytimeouts'][0])\
#	+ "\taway timeout 2 Q.= " + str(game['awaytimeouts'][1])\
#	+ "\taway timeout 3 Q.= " + str(game['awaytimeouts'][2])
	return home_team, away_team

	
def get_all_games_stats( dictionary, game_dictionary, input_file ):
	f = open("aggregate-all-seasons", "w")
	f.write("gameid,gamedate,hometeam,awayteam,hometotalyards,awaytotalyards,homerushyards,awayrushyards,")
	f.write("homepassyards,awaypassyards,homepenaltyyards,awaypenaltyyards,homesacks,awaysacks,homeinterceptions,")
	f.write("awayinterceptions,homefumbles,awayfumbles,homepoints,awaypoints,winner,seasonyear")

	for team, game_date_dictionary in dictionary.iteritems():
		print team
		for game_date, sets in game_date_dictionary.iteritems():
			print "\t"+game_date
	
			print
			home_team, away_team = get_general_game_info(game_dictionary, sets[0]['gameid'])
			if(team == away_team):
				continue			
			print
			team_game_yards, opponent_game_yards, team_rushing_yards,\
			opponent_rushing_yards,team_passing_yards, opponent_passing_yards,\
			team_penalty_yards, oppenent_penalty_yards, team_points, opponent_points \
			 =  get_total_game_yards(str(team),sets)
			if(team_points < opponent_points):
				winner = -1
			elif(team_points == opponent_points):
				winner = 0
			else:
				winner = 1			

			print
			team_sacks, opponent_sacks, team_interceptions, opponent_interceptions,\
			team_fumbles, opponent_fumbles = get_game_sif(str(team), sets)
			
			print
			f.write("\n"+str(sets[0]['gameid'])+","+str(game_date)+","+home_team +","+away_team+","\
			+team_game_yards+","+opponent_game_yards+","+team_rushing_yards+","\
			+opponent_rushing_yards+","+team_passing_yards+","+opponent_passing_yards+","\
			+team_penalty_yards+","+oppenent_penalty_yards+","+team_sacks+","+opponent_sacks+","\
			+team_interceptions+","+opponent_interceptions+","+team_fumbles+","+opponent_fumbles+","\
			+str(team_points)+","+str(opponent_points)+","+str(winner)+","+str(game_date_dictionary['seasonyear'])) 
	f.close()
			
def print_data_to_file( dictionary, game_dictionary, f):
	for team, game_date_dictionary in dictionary.iteritems():
		print team
		for game_date, sets in game_date_dictionary.iteritems():
			print "\t"+game_date
	
			print
			home_team, away_team = get_general_game_info(game_dictionary, sets[0]['gameid'])
			if(team == away_team):
				continue
			season = sets[0]['seasonyear']			
			print
			team_game_yards, opponent_game_yards, team_rushing_yards,\
			opponent_rushing_yards,team_passing_yards, opponent_passing_yards,\
			team_penalty_yards, oppenent_penalty_yards, team_points, opponent_points \
			 =  get_total_game_yards(str(team),sets)
			if(team_points < opponent_points):
				winner = -1
			elif(team_points == opponent_points):
				winner = 0
			else:
				winner = 1			

			print
			team_sacks, opponent_sacks, team_interceptions, opponent_interceptions,\
			team_fumbles, opponent_fumbles = get_game_sif(str(team), sets)
			
			print
			f.write("\n"+str(sets[0]['gameid'])+","+str(game_date)+","+home_team +","+away_team+","\
			+team_game_yards+","+opponent_game_yards+","+team_rushing_yards+","\
			+opponent_rushing_yards+","+team_passing_yards+","+opponent_passing_yards+","\
			+team_penalty_yards+","+oppenent_penalty_yards+","+team_sacks+","+opponent_sacks+","\
			+team_interceptions+","+opponent_interceptions+","+team_fumbles+","+opponent_fumbles+","\
			+str(team_points)+","+str(opponent_points)+","+str(winner)+","+str(season)) 
			
def is_good(play):
	info = play['description']
	if( 'NO GOOD' in info or 'BLOCKED' in info):
		return False
	return True

def defense_TD(play):
	yards = play['yards']
	if( yards <= 0):
	    return True
	return False			
			
def is_safety(play):
	info = play['description']
	if( 'SAFETY' in info):
	    return True
	return False

def merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z	

if __name__ == '__main__':
	input_files = [ "pbp-2014.csv","pbp-2015.csv","pbp-2016.csv"]
	dictionary = {}	
	game_dictionary = {}

	f = open("aggregate-all-seasons", "w")
	f.write("gameid,gamedate,hometeam,awayteam,hometotalyards,awaytotalyards,homerushyards,awayrushyards,")
	f.write("homepassyards,awaypassyards,homepenaltyyards,awaypenaltyyards,homesacks,awaysacks,homeinterceptions,")
	f.write("awayinterceptions,homefumbles,awayfumbles,homepoints,awaypoints,winner,seasonyear")
	for input_file in input_files:
		dat = pd.read_csv(input_file,delimiter=',', header=0, na_values="#")
		dictionary, game_dictionary = create_dictionary_from_dataframe(dat)
		print_data_to_file(dictionary, game_dictionary, f)

	f.close()
#	get_all_games_stats(dictionary, game_dictionary, input_file)	
	#output_stats(dictionary)
	








