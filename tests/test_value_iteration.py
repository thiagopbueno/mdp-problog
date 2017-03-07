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

import mdpproblog.mdp as mdp
import mdpproblog.value_iteration as vi

class TestValueIteration(unittest.TestCase):

	@classmethod
	def setUp(cls):
		cls.models = {
			'sysadmin':
				"""
				computer(c1). computer(c2). computer(c3).
				connected(c1,[c2,c3]). connected(c2,[c1]). connected(c3,[c1]).

				accTotal([],A,A).
				accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
				total(L,T) :- accTotal(L,0,T).
				total_connected(C,T) :- connected(C,L), total(L,T).

				accAlive([],A,A).
				accAlive([H|T],A,X) :- running(H,0), B is A+1, accAlive(T,B,X).
				accAlive([H|T],A,X) :- not(running(H,0)), B is A, accAlive(T,B,X).
				alive(L,A) :- accAlive(L,0,A).
				total_running(C,R) :- connected(C,L), alive(L,R).

				state_fluent(running(C)) :- computer(C).

				action(reboot(none)).
				action(reboot(C)) :- computer(C).

				1.00::running(C,1) :- reboot(C).
				0.05::running(C,1) :- not(reboot(C)), not(running(C,0)).
				P::running(C,1)    :- not(reboot(C)), running(C,0),
				                      total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

				utility(running(C,0),  1.00) :- computer(C).

				utility(reboot(C), -0.75) :- computer(C).
				utility(reboot(none), 0.00).
				"""
		}

		cls.mdp = mdp.MDP(cls.models['sysadmin'])
		cls.vi  = vi.ValueIteration(cls.mdp)

	def test_value_iteration(self):
		V, policy, iteration = self.vi.run()
		expected_policy = [
			'reboot(c1)',
			'reboot(c3)',
			'reboot(c1)',
			'reboot(c3)',
			'reboot(c1)',
			'reboot(c2)',
			'reboot(c1)',
			'reboot(none)'
		]
		self.assertEqual([a.__str__() for s,a in policy.items()], expected_policy)

if __name__ == '__main__':
	unittest.main(verbosity=2)
