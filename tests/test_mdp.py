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
from mdpproblog.fluent import StateSpace, ActionSpace

class TestMDP(unittest.TestCase):

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

	def test_fluent_states(self):
		expected_state_fluents = ['running(c1)', 'running(c2)', 'running(c3)']
		actual_state_fluents = [str(f) for f in self.mdp.state_fluents()]
		self.assertEqual(actual_state_fluents, expected_state_fluents)

	def test_current_state_fluents(self):
		expected_current_state_fluents = ['running(c1,0)', 'running(c2,0)', 'running(c3,0)']
		actual_current_state_fluents = [str(f) for f in self.mdp.current_state_fluents()]
		self.assertEqual(actual_current_state_fluents, expected_current_state_fluents)

	def test_next_state_fluents(self):
		expected_next_state_fluents = ['running(c1,1)', 'running(c2,1)', 'running(c3,1)']
		actual_next_state_fluents = [str(f) for f in self.mdp.next_state_fluents()]
		self.assertEqual(actual_next_state_fluents, expected_next_state_fluents)

	def test_actions(self):
		expected_actions = ['reboot(c1)', 'reboot(c2)', 'reboot(c3)', 'reboot(none)']
		actual_actions = [str(a) for a in self.mdp.actions()]
		self.assertEqual(actual_actions, expected_actions)

	def test_transition(self):
		states  = StateSpace(self.mdp.current_state_fluents())
		actions = ActionSpace(self.mdp.actions())
		for state in states:
			for j, action in enumerate(actions):
				probabilities = self.mdp.transition(state, action)

				for k, (term,prob) in enumerate(probabilities):
					if k == j:
						self.assertAlmostEqual(prob, 1.0)
					elif list(state.values())[k] == 0:
						self.assertAlmostEqual(prob, 0.05)
					else:
						connected = [[1,2], [0], [0]]
						alive = sum([x for i, x in enumerate(state.values()) if i in connected[k]])
						total = len(connected[k])
						self.assertAlmostEqual(prob, 0.45 + 0.50*alive/total)

	def test_transition_model(self):
		actions = self.mdp.actions()
		current_state_fluents = self.mdp.current_state_fluents()

		model = self.mdp.transition_model()
		self.assertEqual(len(model), len(actions) * 2**len(current_state_fluents))
		for (state, action) in model:
			probabilities = tuple(prob for term, prob in model[(state, action)])
			self.assertEqual(len(probabilities), len(current_state_fluents))
			self.assertTrue(all([p >= 0.0 and p <= 1.0 for p in probabilities]))

	def test_reward(self):
		states  = StateSpace(self.mdp.current_state_fluents())
		actions = ActionSpace(self.mdp.actions())
		for state in states:
			state_reward = 0
			for (fluent, value) in state.items():
				if value:
					state_reward += 1.0
			for action in actions:
				action_cost = 0
				for (a, value) in action.items():
					if value and a.__str__() != 'reboot(none)':
						action_cost += 0.75
				reward = self.mdp.reward(state, action)
				self.assertAlmostEqual(reward, state_reward - action_cost)

	def test_reward_model(self):
		rewards = self.mdp.reward_model()
		states  = StateSpace(self.mdp.current_state_fluents())
		actions = ActionSpace(self.mdp.actions())
		self.assertEqual(len(rewards), len(states) * len(actions))

if __name__ == '__main__':
	unittest.main(verbosity=2)
