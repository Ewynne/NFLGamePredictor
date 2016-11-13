import numpy as np
import pandas as pd
import sys
import math

AVG_STATS = ['pointsfor','pointsopp','totalyardsfor','totalyardsopp','passyardsfor','passyardsopp','rushyardsfor','rushyardsopp','penaltyyardsfor','penaltyyardsopp','sacksfor','sacksopp','interceptionsfor','interceptionsopp','fumblesfor','fumblesopp']



## Regression tools ############################

def lin_reg(games,y):
    y = np.array(y)
    x = np.array(games)
    x = np.insert(x,0,1,axis=1)
    xdot = np.dot(np.transpose(x),x)
    h = np.dot(x,np.linalg.inv(xdot))
    w = np.dot(y,h)
    yhat = np.sign(np.dot(x,w))
    print 'hi'
    print accuracy(y,yhat)
    return w

def SGD(games,y,kernelType,eps,eta):
    x = np.array(games)
    size = x.shape
    w = np.random.rand(size[1])
    order = np.arange(size[0])
    while(1):
	wprev = w
	np.random.shuffle(order)
	for i in order:
	    z = -1*y[i]*np.dot(w,x[i])
	    grad = 1/(1+np.exp(-1*z))*y[i]*x[i]
	    w = w + eta*grad
	if np.linalg.norm(w-wprev) <= eps:
	    break 
    yhat = predict_gd(w,x,size[0])
 #   print accuracy(yhat,y)
    return w

def predict_lr(w,x):
    y = np.zeros(len(x))
    for i in range(0,len(x)):
	f = np.dot(x[i],w)
	if f < 0:
	    y[i] = -1
	else:
	    y[i] = 1
    return y

def predict_gd(w,x,size):
    y = np.zeros(size)
    for i in range(0,size):
	f = np.dot(w,x[i])
	if f < 0.5:
	    y[i] = -1
	else:
	    y[i] = 1
    return y

def accuracy(y,yj):
    cor = 0
    for i in range(len(y)):
	if y[i] == yj[i]:
	    cor += 1
    return float(cor)/len(y)

## Game prediction Data Compilation ############

def combine_team_data(home,away,home_hist,away_hist):
    home.pop('win%away')
    home.pop('team')
    away.pop('win%home')
    away.pop('team')
    hkeys = home.keys()
    akeys = away.keys()
    hkeys.sort()
    akeys.sort()
    game = []
    for i in range(0,len(hkeys),2):
	if 'win%' in hkeys[i]:
	    if away[akeys[i]] == 0:
		game.append(home[hkeys[i]]*100)
	    else:
		game.append(home[hkeys[i]]/away[akeys[i]])
	    if away[akeys[i+1]] == 0:
		game.append(home[hkeys[i+1]]*100)
	    else:	
		game.append(home[hkeys[i+1]]/away[akeys[i+1]])
	else:
	    if away[akeys[i+1]] == 0:
		game.append(home[hkeys[i]]*100)
	    else:
		game.append(home[hkeys[i]]/away[akeys[i+1]])
	    if away[akeys[i]] == 0:
		game.append(home[hkeys[i+1]]*100)
	    else:
		game.append(home[hkeys[i+1]]/away[akeys[i]])
    home_games_adv = 0
    away_games_adv = 0
    for team,home_record in home_hist.iteritems():
        if(team in away_hist):
	    away_record = int(away_hist[team])
	    if( home_record == 1 and away_record != 1):
		home_games_adv += 1
	    elif( away_record == 1 and home_record != 1):
		away_games_adv += 1				

    if( away_games_adv == 0 ):
	game.append(float(home_games_adv))
    else:
	game.append(float(home_games_adv/away_games_adv))
   
    return game

def get_average(date,stat,history):
    total = 0
    n = 0
    for d in history.keys():
	if d < date:
	    home = history[d]['home']
	    if home == 1:
		s = 'home'+stat[0:-3]
		total += history[d][s]
	    else:
		s = 'away'+stat[0:-3]
		total += history[d][s]
	    n += 1
    if n==0:
	return 0
    return float(total)/n

def get_win_percentage(date,stat,history):
    # stat=0 -> overall
    # stat=1 -> home
    # stat=-1 -> away
    wins = 0
    n = 0
    for d in history.keys():
	if d < date:
	    if stat == history[d]['home']:
		n += 1
		if stat == history[d]['winner']:
		    wins += 1
	    elif stat == 0:
		n += 1
		if history[d]['winner'] == history[d]['home']:
		    wins += 1
    if n == 0:
	return 0
    return float(wins)/n
		

def get_team_stats(team,date,data,season):
    stats = {'team':team}
    for stat in AVG_STATS:
	stats[stat] = get_average(date,stat,data[season][team])
    stats['win%'] = get_win_percentage(date,0,data[season][team])
    stats['win%home'] = get_win_percentage(date,1,data[season][team])
    stats['win%away'] = get_win_percentage(date,-1,data[season][team])
    return stats
	 
def get_team_game_history(team, game_data,date):
	play_history_dict = {}
	
	for game, info in game_data.iteritems():
		if info['gamedate'] <= date:
		    continue
		home_team = info['home']
		away_team = info['away']
		winning = info['winner']
		if ( str(home_team) == team ):
			play_history_dict[away_team] = winning
		elif( str(away_team) == team ):
			if ( int(winning) == 1 ):
				winning == -1
			elif( int(winning) == -1):
				winning == 1
			play_history_dict[home_team] = winning

	return play_history_dict

## Parse tools #################################

def create_dictionary_from_dataframe(dat):
	dictionary = {}
	
	for play in dat.iterrows():
		play1 = dict(play[1])
		play2 = dict(play[1])		
	
		season = str(play1['seasonyear'])
		offensive_team = str(play1['hometeam'])
		defensive_team = str(play1['awayteam'])
		game_date = play1['gamedate']
		
		if( season not in dictionary ):
			dictionary[season] = {}
	
		if ( defensive_team not in dictionary[season] ):
			dictionary[season][defensive_team] = {}
		
		if ( offensive_team not in dictionary ):
			dictionary[season][offensive_team] = {}
			
		dictionary[season][defensive_team][game_date] = play1
		dictionary[season][defensive_team][game_date]['home'] =-1 
		dictionary[season][offensive_team][game_date] = play2
		dictionary[season][offensive_team][game_date]['home'] = 1
	return dictionary	
    
def get_data_sets(training_file, testing_file):
	training_data = pd.read_csv(training_file,delimiter=',',header=0, na_values='#')
	testing_data = pd.read_csv(testing_file,delimiter=',',header=0, na_values='#')
	training_dictionary = {}
	testing_dictionary = {}
	
	
	for play in training_data.iterrows():
		p = dict(play[1])
		game_id = p['gameid']	
	
		if ( game_id not in training_dictionary ):
			training_dictionary[game_id] = {}
		
		training_dictionary[game_id]['gamedate'] = p['gamedate']
		training_dictionary[game_id]['home'] = p['home']
		training_dictionary[game_id]['away'] = p['away']
		training_dictionary[game_id]['winner'] = p['winner']
		
	for play in testing_data.iterrows():
		p = dict(play[1])
		game_id = p['gameid']	
	
		if ( game_id not in testing_dictionary ):
			testing_dictionary[game_id] = {}
		
		testing_dictionary[game_id]['gamedate'] = p['gamedate']
		testing_dictionary[game_id]['home'] = p['home']
		testing_dictionary[game_id]['away'] = p['away']
		testing_dictionary[game_id]['winner'] = p['winner']

	return training_dictionary, testing_dictionary


if __name__ == '__main__':
    train, test = get_data_sets(sys.argv[1], sys.argv[2])
    data = pd.read_csv('aggregate-all-seasons',delimiter=',',header=0, na_values='#')
    dictionary = create_dictionary_from_dataframe(data)    
    
    games = []
    results = []
    for key, g in train.iteritems():
	date = g['gamedate']
	home = get_team_stats(g['home'],date,dictionary,g['gamedate'][0:4])
	away = get_team_stats(g['away'],date,dictionary,g['gamedate'][0:4])
	home_play_hist = get_team_game_history(g['home'], train,g['gamedate'])
	away_play_hist = get_team_game_history(g['away'], train,g['gamedate'])
	games.append(combine_team_data(home,away, home_play_hist, away_play_hist))
	results.append(g['winner'])

    games_test = []
    results_test = []
    for key, g in test.iteritems():
	date = g['gamedate']
	home = get_team_stats(g['home'],date,dictionary,g['gamedate'][0:4])
	away = get_team_stats(g['away'],date,dictionary,g['gamedate'][0:4])
	home_play_hist = get_team_game_history(g['home'], test,g['gamedate'])
	away_play_hist = get_team_game_history(g['away'], test,g['gamedate'])
	games_test.append(combine_team_data(home,away, home_play_hist, away_play_hist))
	results_test.append(g['winner'])

    ensemble = []
    for i in range(0,10):
	w = SGD(games,results,'linear',.5,0.0001)
	ensemble.append(w)
	y = predict_gd(w,games_test,len(games_test))
	print accuracy(y,results_test)
    yh = []
    for g in games_test:
	res = []
        for e in ensemble:
	    f = np.dot(e,g)
	    if f < 0.5:
		y = -1
	    else:
		y = 1
	    res.append(y)
	win = np.sign(sum(res)/float(len(res)))
	yh.append(win)
    print 'test'
    print accuracy(yh,results_test)

    hometeam = raw_input('home team(Abbreviation): ')
    awayteam = raw_input('away team: ')
    date = raw_input('game date(yyyy-mm-dd): ')

    hstats = get_team_stats(hometeam,date,dictionary,date[0:4])
    astats = get_team_stats(awayteam,date,dictionary,date[0:4])
    hplay_hist = get_team_game_history(hometeam,train,date)
    aplay_hist = get_team_game_history(awayteam,train,date)
    game =  combine_team_data(hstats,astats,hplay_hist,aplay_hist)

    res = []
    for e in ensemble:
	f = np.dot(e,g)
	if f < 0.5:
	    y = -1
	else:
	    y = 1
	res.append(y)
    print res
    win = (sum(res)/float(len(res)))
    print np.sign(win)
