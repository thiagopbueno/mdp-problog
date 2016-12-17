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
from mdpproblog.fluent import Fluent

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
