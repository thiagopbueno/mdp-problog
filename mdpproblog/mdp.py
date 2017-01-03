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
		return sorted(self._engine.declarations('action'), key=lambda action: str(action))
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
