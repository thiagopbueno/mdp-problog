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

class State(object):

	@classmethod
	def create_state(cls, size):
		return [0]*size

	@classmethod
	def next_state(cls, state):
		new_state = state.copy()
		for i, val in enumerate(new_state):
			if val == 0:
				new_state[i] = 1
				break
			else:
				new_state[i] = 0
		return new_state
