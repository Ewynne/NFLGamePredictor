#!/usr/bin/python2.7
#from numpy import genfromtxt
import pandas as pd
import numpy as np
import math
import random
import sys

def create_dictionary_from_dataframe(dat):
	dictionary = {}
	data_set_dictionary = {}		
	
	for play in dat.iterrows():
		play1 = dict(play[1])
		play2 = dict(play[1])
		
		offensive_team = str(play1['hometeam'])
		defensive_team = str(play1['awayteam'])
		game_date = play1['gamedate']
		game_id = play1['gameid']
		
		if ( game_id not in data_set_dictionary ):
			data_set_dictionary[game_id] = {}
		
		data_set_dictionary[game_id]['gamedate'] = game_date
		data_set_dictionary[game_id]['home'] = offensive_team
		data_set_dictionary[game_id]['away'] = defensive_team
		data_set_dictionary[game_id]['winner'] = play1['winner']

	
		if ( defensive_team not in dictionary ):
			dictionary[defensive_team] = {}
		
		if ( offensive_team not in dictionary ):
			dictionary[offensive_team] = {}
			
	
		dictionary[defensive_team][game_date] = play1
		dictionary[defensive_team][game_date]['home'] = 0
		dictionary[offensive_team][game_date] = play2
		dictionary[offensive_team][game_date]['home'] = 1
	return dictionary, data_set_dictionary	

if __name__ == '__main__':
	dat = pd.read_csv('aggregate-pbp-2015.csv',delimiter=',', header=0, na_values="#")
	dictionary, data_set_dictionary = create_dictionary_from_dataframe(dat)
	
	for game, info in data_set_dictionary.iteritems():
		print "\t" + str(game)
		for key, value in info.items():
			print "\t\t" + str(key)+"="+str(value)
	
	keys = random.sample(list(data_set_dictionary), int(math.ceil(len(data_set_dictionary)/5)))
	train_dictionary = {}
	test_dictionary = {}
	
	for game, info in data_set_dictionary.iteritems():	
		if(game in keys):
			test_dictionary[game] = info
		else:
			train_dictionary[game] = info

	output_train = sys.argv[1]
	output_test = sys.argv[2]	
	f = open(output_test, "w")
	f.write("gameid,gamedate,home,away,winner")
	for game, info in test_dictionary.iteritems():
		f.write("\n"+str(game)+","+ str(info['gamedate'])+","+str(info['home'])+","+str(info['away'])+","+str(info['winner']))
	f.close()

	f = open(output_train, "w")
	f.write("gameid,gamedate,home,away,winner")
	for game, info in train_dictionary.iteritems():
		f.write("\n"+str(game)+","+ str(info['gamedate'])+","+str(info['home'])+","+str(info['away'])+","+str(info['winner']))
	f.close()
