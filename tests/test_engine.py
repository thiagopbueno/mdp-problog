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

from problog.logic import Term, Constant, AnnotatedDisjunction
from problog.program import PrologString

import mdpproblog.engine as eng
from mdpproblog.fluent import Fluent

class TestEngine(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
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

				action(reboot(C)) :- computer(C).
				action(reboot(none)).

				1.00::running(C,1) :- reboot(C).
				0.05::running(C,1) :- not(reboot(C)), not(running(C,0)).
				P::running(C,1)    :- not(reboot(C)), running(C,0),
				                      total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

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

	def test_add_assignment(self):
		engine = self.engines['sysadmin']
		fluents = engine.declarations('state_fluent')
		for i in range(2**len(fluents)):
			state = Term('__s%d__' % i)
			value = (-1)**(i % 2) * 10.0*i
			node = engine.add_assignment(state, value)
			fact = engine.get_fact(node)
			self.assertEqual(fact.functor, 'utility')
			self.assertEqual(fact.args, (state, Constant(value)))

	def test_get_assignment(self):
		engine = self.engines['sysadmin']
		assignments = engine.assignments('utility')
		instructions = engine.get_instructions_table()
		facts = instructions['fact']
		for node, fact in facts:
			if fact.functor == 'utility':
				assignment = engine.get_assignment(node)
				self.assertEqual(assignment[0], fact.args[0])
				self.assertEqual(assignment[1], fact.args[1])
			else:
				with self.assertRaises(IndexError):
					not_an_assignment = engine.get_assignment(node)

	def test_add_fact(self):
		engine = self.engines['sysadmin']
		terms = engine.declarations('state_fluent')
		terms = [Fluent.create_fluent(term, 0) for term in terms]
		for term in terms:
			term = Fluent.create_fluent(term, 0)
			p = random.choice([random.random(), None])
			node = engine.add_fact(term, p)
			fact = engine.get_fact(node)
			self.assertEqual(fact.functor, term.functor)
			self.assertEqual(fact.args, term.args)
			if p is None:
				self.assertEqual(str(fact.probability), 'None')
			else:
				self.assertAlmostEqual(float(str(fact.probability)), p)

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
						not_a_fact = engine.get_fact(node)

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
						not_a_rule = engine.get_rule(node)

	def test_add_and_get_annotated_disjunction(self):
		engine = self.engines['sysadmin']
		actions = engine.declarations('action')
		nodes = engine.add_annotated_disjunction(actions, [1.0/len(actions)]*len(actions))
		choices = engine.get_annotated_disjunction(nodes)

		engine.relevant_ground(actions)
		engine.compile()

		queries = { action: engine._knowledge.get_node_by_name(action) for action in actions }

		result = dict(engine.evaluate(queries, None))
		for action, choice in zip(actions, choices):
			probability = 1.0/len(actions)
			self.assertAlmostEqual(result[action], probability)
			self.assertAlmostEqual(choice.probability, probability)
			self.assertTrue(action in choice.functor.args)

	def test_evaluate(self):
		engine = self.engines['sysadmin']

		actions = engine.declarations('action')
		action2term = { str(term): term for term in actions }
		engine.add_annotated_disjunction(actions, [1.0/len(actions)]*len(actions))

		fluents = [Fluent.create_fluent(term, 0) for term in engine.declarations('state_fluent')]
		fluent2term = { str(term): term for term in fluents }
		for fluent in fluents:
			engine.add_fact(fluent, 0.5)

		queries = list(engine.assignments('utility'))
		engine.relevant_ground(queries)

		engine.compile()

		state_evidence  = { 'running(c1,0)': 1, 'running(c2,0)': 0, 'running(c3,0)': 0 }
		action_evidence = { 'reboot(c1)': 0, 'reboot(c2)': 1, 'reboot(c3)': 0, 'reboot(none)': 0 }

		evidence = {}
		for name, value in state_evidence.items():
			evidence[fluent2term[name]] = value
		for name, value in action_evidence.items():
			evidence[action2term[name]] = value

		kb_queries = dict(engine._knowledge.queries())
		queries = {}
		for q, node in kb_queries.items():
			query = str(q)
			if query in ['running(c1,1)', 'running(c2,1)', 'running(c3,1)']:
				queries[query] = node

		result = engine.evaluate(queries, evidence)

if __name__ == '__main__':
	unittest.main(verbosity=2)
