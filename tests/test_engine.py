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
import mdpproblog.engine as eng

class TestEngine(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.models = {
			'sysadmin':
				"""
				computer(c1). computer(c2). computer(c3).
				state_fluent(running(C)) :- computer(C).
				action(reboot(C)) :- computer(C).
				action(reboot(none)).
				""",
			'viral_marketing':
				"""
				person(ann). person(bob).
				state_fluent(marketed(P)) :- person(P).
				state_fluent(buys(P)) :- person(P).
				action(market(P)) :- person(P).
				action(market(none)).
				"""
		}

	def test_declarations(self):
		declarations = {
			'sysadmin': {
				'state_fluent': ['running(c1)', 'running(c2)', 'running(c3)'],
				'action': ['reboot(c1)', 'reboot(c2)', 'reboot(c3)', 'reboot(none)']
			},
			'viral_marketing': {
				'state_fluent': ['buys(ann)', 'buys(bob)', 'marketed(ann)', 'marketed(bob)'],
				'action': ['market(ann)', 'market(bob)', 'market(none)']
			}
		}

		for domain, types in declarations.items():
			engine = eng.Engine(self.models[domain])
			for declaration_type in types:
				terms = engine.declarations(declaration_type)
				terms = sorted([str(t) for t in terms])
				self.assertEqual(terms, types[declaration_type])


if __name__ == '__main__':
	unittest.main(verbosity=2)
