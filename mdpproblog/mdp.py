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
		return sorted(self._engine.declarations('state_fluent'), key=lambda fluent: str(fluent))

	def actions(self):
		"""
		Return an ordered list of action objects.

		:rtype: list of action objects sorted by string representation
		"""
		return sorted(self._engine.declarations('action'), key=lambda action: str(action))
