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

import mdpproblog.engine as eng
from mdpproblog.fluent import Fluent, StateSpace, ActionSpace

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
		""" Prepare the mdp-problog knowledge database to accept queries. """

		# add dummy current state fluents probabilistic facts
		for term in self.state_fluents():
			self._engine.add_fact(Fluent.create_fluent(term, 0), 0.5)

		# add dummy actions annotated disjunction
		actions = self.actions()
		self._engine.add_annotated_disjunction(actions, [1.0/len(actions)]*len(actions))

		# ground the mdp-problog program
		self.__utilities = self._engine.assignments('utility')
		next_state_fluents = self.next_state_fluents()
		queries = list(set(self.__utilities) | set(next_state_fluents) | set(actions))
		self._engine.relevant_ground(queries)

		# compile query database
		self.__next_state_queries = self._engine.compile(next_state_fluents)
		self.__reward_queries = self._engine.compile(self.__utilities)

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
		:rtype: list of pairs (problog.logic.Term, float)
		"""
		evidence = state.copy()
		evidence.update(action)
		return self._engine.evaluate(self.__next_state_queries, evidence)

	def transition_model(self):
		"""
		Return the transition model of all valid transitions.

		:rtype: dict of ((state,action), list of probabilities)
		"""
		transitions = {}
		states  = StateSpace(self.current_state_fluents())
		actions = ActionSpace(self.actions())
		for state in states:
			for action in actions:
				probabilities = self.transition(state, action)
				transitions[(tuple(state.values()), tuple(action.values()))] = probabilities
		return transitions

	def reward(self, state, action):
		"""
		Return the immediate reward value of the transition
		induced by applying `action` to the given `state`.

		:param state: state vector representation of current state fluents
		:type state: list of 0/1 according to state fluents order
		:param action: action vector representation
		:type action: one-hot vector encoding of action as a list of 0/1
		:rtype: float
		"""
		evidence = state.copy()
		evidence.update(action)
		total = 0
		for term, prob in self._engine.evaluate(self.__reward_queries, evidence):
			total += prob * self.__utilities[term].value
		return total

	def reward_model(self):
		"""
		Return the reward model of all valid transitions.

		:rtype: dict of ((state,action), float)
		"""
		rewards = {}
		states  = StateSpace(self.current_state_fluents())
		actions = ActionSpace(self.actions())
		for state in states:
			for action in actions:
				reward = self.reward(state, action)
				rewards[(tuple(state.values()), tuple(action.values()))] = reward
		return rewards
