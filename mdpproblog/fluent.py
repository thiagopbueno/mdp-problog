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

from problog.logic import Term, Constant

from collections import OrderedDict

class Fluent(object):
	"""
	Factory class for building fluent terms. A fluent term is a
	problog.logic.Term with a problog.logic.Constant as last argument
	representing its timestep.
	"""

	@classmethod
	def create_fluent(cls, term, timestep):
		""""
		Return a new fluent made from `term` with given `timestep`.

		:param term: any problog term
		:type term: problog.logic.Term
		:param timestep: timestep numeric value
		:type timestep: int
		:rtype: problog.logic.Term
		"""
		args = term.args + (Constant(timestep),)
		return term.with_args(*args)


class StateSpace(object):
	"""
	Iterator class for looping over vector representations of
	states in a factored MDP defined by `state_fluents`. Each state
	is implemented by an OrderedDict of (problog.logic.Term, 0/1).

	:param state_fluents: predicates defining a state in a given timestep
	:type state_fluents: list of problog.logic.Term
	"""

	def __init__(self, state_fluents):
		self.__state_fluents = state_fluents
		self.__state_space_size = 2**len(self.__state_fluents)

	def __len__(self):
		""" Return the number of states of the state space. """
		return self.__state_space_size

	def __iter__(self):
		""" Return an iterator over the state space. """
		self.__state_number = 0
		self.__state = OrderedDict([ (fluent, 1) for fluent in self.__state_fluents ])
		return self

	def __next__(self):
		""" Return next state representation. """
		if self.__state_number == self.__state_space_size:
			raise StopIteration

		for fluent, value in self.__state.items():
			if value == 1:
				self.__state[fluent] = 0
			else:
				self.__state[fluent] = 1
				break

		self.__state_number += 1
		return self.__state

	def __getitem__(self, index):
		"""
		Return the state representation with given `index`.

		:param index: state index in state space
		:type index: int
		"""
		state = []
		for fluent in self.__state_fluents:
			value = index % 2
			index //= 2
			state.append((fluent, value))
		return tuple(state)


class ActionSpace(object):
	"""
	Iterator class for looping over vector representations of
	`actions` in a factored MDP. Each action is implemented by
	an OrderedDict of (problog.logic.Term, 0/1).

	:param actions: predicates listing possible actions
	:type actions: list of problog.logic.Term
	"""

	def __init__(self, actions):
		self.__actions = actions
		self.__action_space_size = len(self.__actions)

	def __len__(self):
		""" Return the number of actions of the action space. """
		return self.__action_space_size

	def __iter__(self):
		""" Return an iterator over the action space. """
		self.__action_number = 0
		self.__action = OrderedDict([ (action, 0) for action in self.__actions ])
		self.__action[self.__actions[-1]] = 1
		return self

	def __next__(self):
		""" Return next action representation. """
		if self.__action_number == self.__action_space_size:
			raise StopIteration

		self.__action[self.__actions[self.__action_number-1]] = 0
		self.__action[self.__actions[self.__action_number]] = 1

		self.__action_number += 1
		return self.__action

	def __getitem__(self, index):
		"""
		Return the action representation with given `index`.

		:param index: action index in action space
		:type index: int
		"""
		return self.__actions[index]
