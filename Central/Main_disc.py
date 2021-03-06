import gym
import numpy as np
import tensorflow as tf
import random
import retro

import A3C
import DQN
import PG

import gym_cmd
parser = gym_cmd.build_parser()
options = parser.parse_args()

if __name__ == '__main__':

	# Assume command line param will be 'CartPole-v1' or 'MountainCar-v1', etc.
	algorithm = options.algorithm
	domain = options.domain

	env = retro.make(domain)

	if(algorithm == "DQN"):
		agent = DQN.DQN(act_dim=env.action_space.n, obs_dim=env.observation_space.shape[0],
					lr_q_value=0.02, gamma=options.gamma, epsilon=options.epsilon)
	elif(algorithm == "A3C"):
		agent = A3C.ActorCritic(act_dim=env.action_space.n, obs_dim=env.observation_space.shape[0],
					lr_actor=0.01, lr_value=0.02, gamma=options.gamma)
	elif(algorithm == "PG"):
		agent = PG.PolicyGradient(act_dim=env.action_space.n, obs_dim=env.observation_space.shape[0], 
					lr=0.02, gamma=options.gamma)

	else:
		print("Invalid algorithm specified. Only A3C, DQN, and PG currently supported")
		quit()
				
	nepisode = options.nepisode
	batch_size = 128
	iteration = 0
	
	# Necessary for DQN
	epsilon_step = options.epsilon_step
	epsilon_decay = options.epsilon_decay
	epsilon_min = options.epsilon_min
	
	for i_episode in range(nepisode):
		obs0 = env.reset()
		ep_rwd = 0

		# Discrete domains
		while True:

			if i_episode % 10 == 0: env.render()
			act, _ = agent.step(obs0)
	
			obs1, rwd, done, info = env.step(act)

			agent.memory.store_transition(obs0, act, rwd, obs1, done)

			obs0 = obs1
			ep_rwd += rwd

			# The following code can probably be cleaned up in a more general way
			if(algorithm == "DQN"):
				if iteration >= batch_size * 3:
					agent.learn() 
					if iteration % epsilon_step == 0:
						agent.epsilon = max([agent.epsilon * epsilon_decay, epsilon_min])
	
			if done:
				# Try to find a cleaner way of doing this
				if(algorithm == "A3C"):
					_, last_value = agent.step(obs1)
					agent.learn(last_value, done)
				elif(algorithm == "PG"):
					agent.learn()

				print('Ep: %i' % i_episode, "|Ep_r: %i" % ep_rwd)
				break

			iteration += 1