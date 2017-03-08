#! /usr/bin/env python3

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

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import unittest
from mdpproblog.fluent import Fluent, StateSpace, ActionSpace

from problog.logic import Term, Constant

class TestFluent(unittest.TestCase):

	def test_fluent(self):
		terms = [
			Term('t0'),
			Term('t1', args=(Constant('c1'),)),
			Term('t2', args=(Constant('c1'), Constant('c2')))
		]
		for term in terms:
			for timestep in range(2):
				fluent = Fluent.create_fluent(term, timestep)
				self.assertEqual(fluent.functor, term.functor)
				self.assertEqual(fluent.arity, term.arity+1)
				self.assertEqual(fluent.args[:-1], term.args)
				self.assertEqual(fluent.args[-1], Constant(timestep))

class TestStateSpace(unittest.TestCase):

	def test_state_space(self):
		running = Term('running')
		fluents = [ running.with_args(Constant('c%d' % i), Constant(0)) for i in range(1,4) ]
		states = StateSpace(fluents)
		for i, state in enumerate(states):
			self.assertEqual(len(state), 3)
			n = 0
			for j, (fluent, value) in enumerate(state.items()):
				self.assertEqual(fluent.functor, 'running')
				self.assertEqual(fluent.args[0], 'c%d' % (j+1))
				self.assertEqual(fluent.args[-1], 0)
				n += value * (2**j)
			self.assertEqual(n, i)

class TestActionSpace(unittest.TestCase):

	def test_action_space(self):
		reboot = Term('reboot')
		computers = [ Constant('c%i' % i) for i in range(1,4) ]
		fluents = [ reboot(c) for c in computers ]
		fluents.append(reboot(Constant('none')))
		actions = ActionSpace(fluents)
		for i, action in enumerate(actions):
			self.assertEqual(sum(action.values()), 1)
			for j, (fluent, value) in enumerate(action.items()):
				self.assertEqual(fluent, fluents[j])
				if j == i:
					self.assertEqual(value, 1)
				else:
					self.assertEqual(value, 0)


if __name__ == '__main__':
	unittest.main(verbosity=2)
