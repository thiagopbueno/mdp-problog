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

from collections import namedtuple
RewardModel = namedtuple('RewardModel', ['actions', 'fluents'])

import mdpproblog.engine as eng
from mdpproblog.fluent import Fluent, State

class MDP(object):
	"""
	Representation of an MDP and its components. Implemented as a bridge
	class to the ProbLog programs specifying the MDP domain and problems.

	:param model: a valid MDP-ProbLog program
	:type model: str
	"""

	def __init__(self, model):
		self._model = model
		self._engine = eng.Engine(model)

		self.__prepare()

	def __prepare(self):
		engine = self._engine

		for term in engine.declarations('state_fluent'):
			engine.add_fact(Fluent.create_fluent(term, 0), 0.5)

		actions = engine.declarations('action')
		engine.add_annotated_disjunction(actions, [1.0/len(actions)]*len(actions))

		utilities = engine.assignments('utility')
		next_state_fluents = [Fluent.create_fluent(f, 1) for f in self.state_fluents()]
		queries = list(set(utilities) | set(next_state_fluents) | set(actions))

		engine.relevant_ground(queries)
		self.__queries = engine.compile(self.next_state_fluents())

	def state_fluents(self):
		"""
		Return an ordered list of state fluent objects.

		:rtype: list of state fluent objects sorted by string representation
		"""
		return sorted(self._engine.declarations('state_fluent'), key=str)

	def current_state_fluents(self):
		"""
		Return the ordered list of current state fluent objects.

		:rtype: list of current state fluent objects sorted by string representation
		"""
		return [Fluent.create_fluent(f, 0) for f in self.state_fluents()]

	def next_state_fluents(self):
		"""
		Return the ordered list of next state fluent objects.

		:rtype: list of next state fluent objects sorted by string representation
		"""
		return [Fluent.create_fluent(f, 1) for f in self.state_fluents()]

	def actions(self):
		"""
		Return an ordered list of action objects.

		:rtype: list of action objects sorted by string representation
		"""
		return sorted(self._engine.declarations('action'), key=str)

	def transition(self, state, action):
		"""
		Return the probabilities of next state fluents given current
		`state` and `action`.

		:param state: state vector representation of current state fluents
		:type state: list of 0/1 according to state fluents order
		:param action: action vector representation
		:type action: one-hot vector encoding of action as a list of 0/1
		"""
		evidence = dict(zip(self.current_state_fluents(), state))
		evidence.update(dict(zip(self.actions(), action)))
		return self._engine.evaluate(self.__queries, evidence)

	def transition_model(self):
		"""
		Return the transition model of all valid transitions.

		:rtype: dict of ((tuple(state),action), list of probabilities)
		"""
		transitions = {}

		current_state_fluents = self.current_state_fluents()
		actions = self.actions()

		state = State.create_state(len(current_state_fluents))
		action = [0]*len(actions)
		action[-1] = 1
		for i in range(2**len(current_state_fluents)):
			for j in range(len(actions)):
				action[j-1] = 0
				action[j] = 1
				probabilities = self.transition(state, action)
				transitions[(tuple(state), actions[j])] = probabilities
			state = State.next_state(state)

		return transitions

	def reward_model(self):
		"""
		Return the reward model mapping utility attributes
		to numeric values, separated by actions and fluents.

		:rtype: namedtuple RewardModel(actions, fluents) of
		        dicts of (problog.logic.Term, float)
		"""
		utilities = self._engine.assignments('utility')
		action_utilites = {}
		fluent_utilities = {}
		for term, value in utilities.items():
			if term in self.actions():
				action_utilites[term] = value
			else:
				fluent_utilities[term] = value
		return RewardModel(actions=action_utilites, fluents=fluent_utilities)
