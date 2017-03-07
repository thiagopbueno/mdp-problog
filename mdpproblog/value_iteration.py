# This file is part of MDP-ProbLog.

# MDP-ProbLog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MDP-ProbLog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MDP-ProbLog.  If not, see <http://www.gnu.org/licenses/>.

import sys

from mdpproblog.fluent import StateSpace, ActionSpace

class ValueIteration(object):
	"""
	Implementation of the enumerative Value Iteration algorithm.
	It performs successive, synchronous Bellman backups until
	convergence is achieved for the given error epsilon for the
	infinite-horizon MDP with discount factor gamma.

	:param mdp: MDP representation
	:type mdp: mdpproblog.MDP
	"""

	def __init__(self, mdp):
		self._mdp = mdp
		self.__transition_cache = {}
		self.__reward_cache = {}

	def run(self, gamma=0.9, epsilon=0.1):
		"""
		Execute value iteration until convergence.
		Return optimal value function, greedy policy and number
		of iterations.

		:param gamma: discount factor
		:type gamma: float
		:param epsilon: maximum error
		:type epsilon: float
		:rtype: triple (dict(state, value), dict(policy, action), float)
		"""
		V = {}
		policy = {}

		actions = ActionSpace(self._mdp.actions())
		states  = StateSpace(self._mdp.current_state_fluents())

		iteration = 0
		while True:
			iteration += 1
			max_residual = -sys.maxsize
			for (i, state) in enumerate(states):
				max_value = -sys.maxsize
				greedy_action = None
				for (j, action) in enumerate(actions):
					transition = self.__transition_cache.get((i, j), None)
					if transition is None:
						transition = self._mdp.transition(state, action)
						self.__transition_cache[(i,j)] = transition

					reward = self.__reward_cache.get((i,j), None)
					if reward is None:
						reward = self._mdp.reward(state, action)
						self.__reward_cache[(i,j)] = reward

					Q = reward + gamma * self.__expected_value(transition, V)
					if Q >= max_value:
						max_value = Q
						greedy_action = actions[j]

				residual = abs(V.get(i, 0) - max_value)
				max_residual = max(max_residual, residual)
				V[i] = max_value
				policy[i] = greedy_action

			if max_residual <= 2 * epsilon * (1-gamma) / gamma:
				break

		V = { states[i]: value for i, value in V.items() }
		policy = { states[i]: action for i, action in policy.items() }

		return V, policy, iteration

	def __expected_value(self, transition, V, k=0, index=0, joint=1.0):
		"""
		Compute the expected future value for the given `transition` with
		state value given by `V`.

		:param transition: transition probabilities
		:type transition: list of pairs (fluent, float)
		:param V: current value function
		:type V: dict(int,float)
		:rtype: float
		"""
		if len(transition) == 0:
			return joint * V.get(index, 0.0)

		probability = transition[0][1]
		if abs(probability - 1.0) <= 1e-06:
			ret1 = self.__expected_value(transition[1:], V, k+1, index + 2**k, joint)
			ret2 = 0.0
		elif abs(probability - 0.0) <=1e-06:
			ret1 = 0.0
			ret2 = self.__expected_value(transition[1:], V, k+1, index, joint)
		else:
			ret1 = self.__expected_value(transition[1:], V, k+1, index + 2**k, joint * probability)
			ret2 = self.__expected_value(transition[1:], V, k+1, index, joint * (1 - probability))
		return ret1 + ret2
