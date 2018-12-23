import os
import random
import numpy as np

def get_info(state, a1, a2, agent_num):
	if state[-1] == 'B':
		str3 = ' Consider both agent suggestions for the best outcome.'
	else:
		str3 = ' Consider my suggestions alone for the best outcome.'

	if (state[-2] == 'F') and (a1>a2):
		str2 =  ' My competence is higher.' + str3
	elif (state[-2] == 'F') and (a1<a2):
		str2 =  ' My competence is lower.' + str3
	elif (state[-2] == 'NF') and (a1>a2):
		str2 =  ' My competence is higher.' + str3
	elif (state[-2] == 'NF') and (a1<a2):
		str2 =  ' My competence is higher.' + str3

	if (state[-3] == 'H'):
		str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,a1) + str2
	elif (state[-3] == 'NH') and (state[-2] == 'F'):
		str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,int(a1+((a2-a1)*0.9))) + str2
	elif (state[-3] == 'NH') and (state[-2] == 'NF'):
		str1 = 'I am agent {} with ELO rating {}.'.format(agent_num,int(a2+((a2-a1)*0.9))) + str2

	return str1

def main():
	user_elo = 3200
	# Build Agent dictionary
	engines = ['stockfish_1','stockfish_2','stockfish_3','stockfish_5','stockfish_6','stockfish_7','stockfish_8','stockfish_9']
	elo_ratings = [3113,3079,3097,3194,3226,3246,3301,3369]
	engine_path = ['/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish-191-32-ja',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_2/Linux/stockfish-231-64-ja',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish-3-64-ja',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish_14053109_x64',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish_6_x64',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish7x64',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish_8_x64',
				   '/home/adi/Documents/Michigan_courses/EECS598_HCI/Final_project/Chess_stockfish/stockfish_1/Linux/stockfish_9_64']
   	idx = (np.abs(np.asarray(elo_ratings)-user_elo)).argmin()
   	m_agent_path = engine_path[idx]
   	elo_ratings_new = elo_ratings
   	del elo_ratings_new[idx]
   	idx_n = (np.abs(np.asarray(elo_ratings_new)-user_elo)).argmin()
	idx = elo_ratings.index(elo_ratings_new[idx_n])
	agent1_path = engine_path[idx]	
	a1_rating = elo_ratings[idx]

   	del elo_ratings_new[idx]
   	idx_n = (np.abs(np.asarray(elo_ratings_new)-user_elo)).argmin()
	idx = elo_ratings.index(elo_ratings_new[idx_n])
	agent2_path = engine_path[idx]
	a2_rating = elo_ratings[idx]

	Trust_options = [['H','F','B'],['H','F','NB'],['H','NF','B'],['H','NF','NB'],['NH','F','B'],['NH','F','NB'],['NH','NF','B'],['NH','NF','NB']]
	agent1_state = random.choice(Trust_options)
	agent2_state = random.choice(Trust_options)

	#Agent 1 information
	agent1_info = get_info(agent1_state,a1_rating,a2_rating,1)
	agent2_info = get_info(agent2_state,a2_rating,a1_rating,2)

	print(agent1_state)
	print(a1_rating)
	print(agent1_info)
	print(agent2_state)
	print(a2_rating)
	print(agent2_info)

if __name__ == '__main__': 
	main()