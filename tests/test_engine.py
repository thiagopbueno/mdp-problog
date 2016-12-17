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
import random

from problog.logic import Term, Constant

import mdpproblog.engine as eng
from mdpproblog.fluent import Fluent

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
				utility(running(C,1),  1.00) :- computer(C).
				utility(reboot(C), -0.75) :- computer(C).
				utility(reboot(none), 0.00).
				""",
			'viral_marketing':
				"""
				person(ann). person(bob).
				state_fluent(marketed(P)) :- person(P).
				state_fluent(buys(P)) :- person(P).
				action(market(P)) :- person(P).
				action(market(none)).
				utility(buys(P,1), 5) :- person(P).
				utility(market(P), -1) :- person(P).
				"""
		}

	def setUp(self):
		self.engines = {
			'sysadmin': eng.Engine(self.models['sysadmin']),
			'viral_marketing': eng.Engine(self.models['viral_marketing'])
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
			engine = self.engines[domain]
			for declaration_type in types:
				terms = engine.declarations(declaration_type)
				actual_declarations = sorted([str(t) for t in terms])
				expected_declarations = types[declaration_type]
				self.assertEqual(actual_declarations, expected_declarations)

	def test_assignments(self):
		assignments = {
			'sysadmin': {
				'utility': {
					'running(c1,1)': 1.00, 'running(c2,1)': 1.00, 'running(c3,1)': 1.00,
					'reboot(c1)': -0.75, 'reboot(c2)': -0.75, 'reboot(c3)': -0.75,
					'reboot(none)': 0.00
				}
			},
			'viral_marketing': {
				'utility': {
					'buys(ann,1)': 5, 'buys(bob,1)': 5,
					'market(ann)': -1, 'market(bob)': -1
				}
			}
		}

		for domain, types in assignments.items():
			engine = self.engines[domain]
			for assignment_type in types:
				expected_assignments = types[assignment_type]
				actual_assignments = engine.assignments(assignment_type)
				self.assertEqual(len(actual_assignments), len(expected_assignments))
				for term, value in actual_assignments.items():
					self.assertTrue(str(term) in expected_assignments)
					self.assertEqual(value, expected_assignments[str(term)])

	def test_add_fact(self):
		engine = self.engines['sysadmin']
		terms = engine.declarations('state_fluent')
		terms = [Fluent.create_fluent(term, 0) for term in terms]
		for term in terms:
			term = Fluent.create_fluent(term, 0)
			p = random.choice([random.random(), None])
			n = engine.add_fact(term, p)
			fact = engine.get_fact(n)
			self.assertEqual(fact.functor, term.functor)
			self.assertEqual(fact.args, term.args)
			self.assertEqual(fact.probability, p)

	def test_get_fact(self):
		engine = self.engines['sysadmin']
		instructions = engine.get_instructions_table()
		facts = instructions['fact']
		for node,fact in facts:
			self.assertTrue(engine.get_fact(node), fact)
		for instruction_type in instructions:
			if instruction_type != 'fact':
				for node,instruction in instructions[instruction_type]:
					with self.assertRaises(IndexError):
						engine.get_fact(node)

	def test_add_rule(self):
		engine = self.engines['sysadmin']

		running = Term('running')
		c1 = Constant('c1')
		c2 = Constant('c2')
		c3 = Constant('c3')
		r1 = Fluent.create_fluent(running(c1), 1)
		r2 = Fluent.create_fluent(running(c2), 1)
		r3 = Fluent.create_fluent(running(c3), 1)

		head = Term('__s0__')
		body = ~r1 & ~r2 & ~r3
		rule = head << body
		node = engine.add_rule(head, [~r1, ~r2, ~r3])
		self.assertTrue(engine.get_rule(node), rule)

		head = Term('__s3__')
		body = r1 & r2 & ~r3
		node = engine.add_rule(head, [r1, r2, ~r3])
		rule = engine.get_rule(node)
		self.assertTrue(rule, head << body)

		head = Term('__s7__')
		body = r1 & r2 & r3
		rule = head << body
		node = engine.add_rule(head, [r1, r2, r3])
		self.assertTrue(engine.get_rule(node), rule)

	def test_get_rule(self):
		engine = self.engines['sysadmin']
		instructions = engine.get_instructions_table()
		rules = instructions['clause']
		for node,rule in rules:
			self.assertTrue(engine.get_rule(node), rule)
		for instruction_type in instructions:
			if instruction_type != 'clause':
				for node,instruction in instructions[instruction_type]:
					with self.assertRaises(IndexError):
						engine.get_rule(node)


if __name__ == '__main__':
	unittest.main(verbosity=2)
