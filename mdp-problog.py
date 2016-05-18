#! /usr/bin/env python3

from problog.program import PrologString
from problog.engine  import DefaultEngine
from problog.logic   import Constant,Term,And,Clause
from problog         import get_evaluatable

import time
import math
import inspect

class MDPProbLog():
	_eng = DefaultEngine(label_all=True)

	def __init__(self, model, gamma, epsilon):
		self._model = model
		self._gamma = gamma
		self._epsilon = epsilon

		print("  >> Preparing program ...", end=" ")
		start = time.clock()
		self._db = self._eng.prepare(PrologString(model))
		end = time.clock()
		uptime = end-start
		print("Done in {0:.3f}sec.".format(uptime))

		self._build_state_atoms()
		self._get_action_atoms()
		self._build_action_rules()
		self._build_value_function_rules()
		self._utilities = dict(self._eng.query(self._db, Term('utility', None, None)))

		print("  >> Relevant grounding ...", end=" ")
		start = time.clock()
		self._gp = self._eng.ground_all(self._db, target=None, queries=self._utilities.keys())
		end = time.clock()
		uptime = end-start
		print("Done in {0:.3f}sec.".format(uptime))

		print("  >> Compilation ...", end=" ")
		start = time.clock()
		self._knowledge = get_evaluatable(None).create_from(self._gp)
		end = time.clock()
		uptime = end-start
		print("Done in {0:.3f}sec.".format(uptime))

		self._queries = dict(self._knowledge.queries())
		self._get_decision_facts()

	@property
	def model(self):
		return self._model

	@property
	def actions(self):
		return self._action_atoms

	def _build_state_atoms(self):
		state_vars = [p[0] for p in self._eng.query(self._db, Term('state_fluent', None))]
		self._state_functors = set()
		self._next_state_atoms = []
		self._current_state_atoms = []
		for t in state_vars:
			self._state_functors.add(t.functor)

			args = t.args + (Constant(1),)
			self._next_state_atoms.append(t.with_args(*args))

			args = t.args + (Constant(0),)
			curr_state_atom = t.with_args(*args)
			self._current_state_atoms.append(curr_state_atom)
			self._db.add_fact(curr_state_atom.with_probability(Term('?')))

	def _get_action_atoms(self):
		self._action_atoms = [p[0] for p in self._eng.query(self._db, Term('action', None))]

	def _build_action_rules(self):
		self._action_decision_facts = []
		self._action_rules = []

		n = math.ceil(math.log2(len(self._action_atoms)))
		for i in range(1, n+1):
			f = Term('a{}'.format(i), p=Term('?'))
			self._action_decision_facts.append(f)
			self._db.add_fact(f)

		valuation = [0]*n
		for i in range(len(self._action_atoms)):
			body_atoms = []
			for pos in range(n):
				if valuation[pos] == 1:
					body_atoms.append(self._action_decision_facts[pos])
				else:
					body_atoms.append(~self._action_decision_facts[pos])

			body = And.from_list(body_atoms)
			head = self._action_atoms[i]
			r = head << body
			self._action_rules.append(r)
			self._db.add_clause(r)

			MDPProbLog.next_valuation(valuation)

	def _get_decision_facts(self):
		self._action_decision_facts = []
		self._state_decision_facts = []
		for i, n, t in self._gp:
			if t == 'atom' and n.probability == Term('?'):
				functor = n.name.functor
				if functor in self._state_functors:
					self._state_decision_facts.append(n.name)
				else:
					self._action_decision_facts.append(n.name)
		self._state_decision_facts = sorted(self._state_decision_facts, key=Term.__repr__)

	def _build_value_function_rules(self):
		self._value_function_atoms = []
		n = len(self._next_state_atoms)
		valuation = [0]*n
		for i in range(2**n):
			body_atoms = []
			for pos in range(n):
				if valuation[pos] == 1:
					body_atoms.append(self._next_state_atoms[pos])
				else:
					body_atoms.append(~self._next_state_atoms[pos])
			body = And.from_list(body_atoms)
			head = Term('__s{}__'.format(i))
			self._value_function_atoms.append(head)
			rule = head << body
			self._db.add_clause(rule)

			value = Term('utility', head.with_probability(None), Constant(0.0))
			self._db.add_fact(value)

			MDPProbLog.next_valuation(valuation)

	def value_iteration(self, verbose):
		self._verbose = verbose
		value_function, policy = self.update()

		if self._verbose == 3:
			states = [int(k[3:-2]) for k in value_function.keys()]
			output = ["Iteration", "Error", "Time"]
			output += ["V(s{0})".format(s) for s in sorted(states)]
			print(','.join(output))

		iteration = 0
		max_error = None
		while True:
			start = time.clock()
			new_value_function, policy = self.update()
			error = [ abs(new_value_function[s] - value_function[s]) for s in value_function.keys() ]
			max_error = max(error)
			value_function = new_value_function.copy()
			if max_error <= 2*epsilon*(1-gamma)/(gamma):
				break
			end = time.clock()
			uptime = end-start

			if self._verbose in [1,2]:
				print("@ Iteration #{} ...".format(iteration))
				print(">> Done in {0:.3f}sec.".format(uptime))
				print(">> Max error={0:.5f}".format(max_error))
				print()

			if self._verbose == 3:
				output = [str(iteration)]
				output.append("{0:.5f}".format(max_error))
				output.append("{time:.3f}".format(time=uptime))
				values = []
				for s in sorted(states):
					k = "__s{}__".format(s)
					val = value_function[k]
					values.append("{0:3.4f}".format(val))
				output += values
				print(','.join(output))

			iteration += 1

		value_function, policy = self.update(True)
		value_function, policy = self._translate_function_repr(value_function, policy)

		return value_function, policy, iteration, max_error

	def update(self, actions=False):
		value, policy = self._search_exhaustive(actions)
		for u,v in self._utilities.items():
			if u.__repr__() in value.keys():
				self._utilities[u] = self._gamma * value[u.__repr__()]
		return value, policy

	def _search_exhaustive(self, actions):
		value = {}
		policy = {}

		n_actions = len(self._action_atoms)
		n_action_facts = math.ceil(math.log2(len(self._action_atoms)))
		n_states = 2**len(self._state_decision_facts)

		state_valuation = [0]*n_states
		for i in range(n_states):

			if self._verbose == 2:
				start_st = time.clock()
				print(">> state #{0}".format(i))

			state_evidence = dict(zip(self._state_decision_facts, state_valuation))

			best_score = None
			best_choice = None

			action_valuation = [0]*n_action_facts
			for j in range(n_actions):
				if self._verbose == 2:
					start_act = time.clock()
					print("\taction #{0}".format(j), end="\t:\t")

				action_evidence = dict(zip(self._action_decision_facts, action_valuation))

				evidence = state_evidence.copy()
				evidence.update(action_evidence)

				score = self._evaluate(evidence, i, j)
				if best_score is None or score > best_score:
					best_score = score
					best_choice = dict(evidence)

				MDPProbLog.next_valuation(action_valuation)

				if self._verbose == 2:
					end_act = time.clock()
					print("\t@ uptime per action = {0:.3f}sec.".format(end_act-start_act))

			s = "__s{}__".format(i)
			value[s] = best_score
			s = ', '.join(["{0}={1}".format(k,state_evidence[k]) for k in sorted(state_evidence.keys(), key=Term.__repr__)])
			policy[s] = { k:v for (k,v) in best_choice.items() if k in self._action_decision_facts }

			MDPProbLog.next_valuation(state_valuation)
			if self._verbose == 2:
				end_st = time.clock()
				print("@ uptime per state = {0:.3f}sec.".format(end_st-start_st))
				print()

		return value, policy

	def _evaluate(self, evidence, state_id, action_id):
		# queries = dict(self._knowledge.queries())
		evaluator = self._knowledge.get_evaluator(None, None, evidence)

		nodes = []
		if (state_id, action_id) in self._evaluate.reachable_nodes:
			nodes = self._evaluate.reachable_nodes[(state_id, action_id)]
		else:
			# action nodes
			for name in self._action_atoms:
				nodes.append(self._queries[name])

			# state variable nodes
			reachable_states = set()
			for name in self._value_function_atoms:
				node = self._queries[name]
				reachable_states.add(node)

			# value function prunning
			for i in range(len(self._next_state_atoms)):
				name = self._next_state_atoms[i]
				node = self._queries[name]
				nodes.append(node)
				p = evaluator.evaluate(node)

				states = set()
				if abs(p - 1.0) <= 0.0001:
					for j in range(2**i, len(self._value_function_atoms), 2**(i+1)):
						for k in range(2**i):
							n = j+k
							states.add(self._queries[self._value_function_atoms[n]])
					reachable_states = reachable_states & states

			# value function nodes
			for node in reachable_states:
				nodes.append(node)

			# memoization
			self._evaluate.reachable_nodes[(state_id, action_id)] = nodes

		result = {}
		score = 0.0
		for node in nodes:
			name = self._knowledge.get_name(node)
			result[name] = evaluator.evaluate(node)
			score += result[name] * float(self._utilities[name])

		if self._verbose == 2:
			print("WMC = {}".format(len(result)), end="\t:  ")

		return score

		# result = self._knowledge.evaluate(weights=evidence)
		# print("WMC = {}".format(len(result)))
		# score = 0.0
		# for r in result:
		# 	score += result[r] * float(self._utilities[r])
		# return score

	_evaluate.reachable_nodes = {}

	def _translate_function_repr(self, value_function, policy):
		# actions in policy function
		for state, strategy in policy.items():
			decision_facts = sorted(strategy.keys(), key=Term.__repr__)
			index = 0
			b = 1
			for a in decision_facts:
				index += b*strategy[a]
				b *= 2
			action = self._action_atoms[index]
			policy[state] = action

		# states in value function
		state_labels = {}
		n_states = 2**len(self._state_decision_facts)
		state_valuation = [0]*n_states
		for i in range(n_states):
			state_evidence = dict(zip(self._state_decision_facts, state_valuation))
			lbl = "__s{}__".format(i)
			st_repr = ', '.join(["{0}={1}".format(k,state_evidence[k]) for k in sorted(state_evidence.keys(), key=Term.__repr__)])
			state_labels[lbl] = st_repr
			MDPProbLog.next_valuation(state_valuation)
		new_value_function = {}
		for state, value in value_function.items():
			new_value_function[state_labels[state]] = value

		return new_value_function, policy

	@staticmethod
	def next_valuation(valuation):
		for pos in range(len(valuation)):
			if valuation[pos] == 1:
				valuation[pos] = 0
			else:
				valuation[pos] = 1
				break

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("domain", help="path to MDP domain file")
	parser.add_argument("instance", help="path to MDP instance file")
	parser.add_argument("-g", "--gamma",   type=float, default=0.9, help="discount factor (default=0.9)")
	parser.add_argument("-e", "--eps",     type=float, default=0.1, help="relative error  (default=0.1)")
	parser.add_argument("-v", "--verbose", type=int,   default=0,   help="verbose mode    (default=0)")
	args = parser.parse_args()

	model = ""
	with open(args.domain, 'r') as domain:
		if args.verbose in [1,2]:
			print(">> Reading file {}...".format(args.domain))
		start = time.clock()
		model += domain.read()
		end = time.clock()
		if args.verbose in [1,2]:
			print(">> Done in {0:.5f}sec.".format(end-start))
			print()
	with open(args.instance, 'r') as instance:
		if args.verbose in [1,2]:
			print(">> Reading file {}...".format(args.instance))
		start = time.clock()
		model += instance.read()
		end = time.clock()
		if args.verbose in [1,2]:
			print(">> Done in {0:.5f}sec.".format(end-start))
			print()

	if args.verbose in [1, 2]:
		print(">> Building MDPProbLog program ...")
	gamma = args.gamma
	epsilon = args.eps
	start = time.clock()
	program = MDPProbLog(model, gamma, epsilon)
	end = time.clock()
	if args.verbose in [1, 2]:
		print(">> Done in {0:.5f}sec.".format(end-start))
		print()

	if args.verbose in [1, 2]:
		print(">> Running value iteration ...")
		print()
	start = time.clock()
	value_function, policy, iterations, error = program.value_iteration(args.verbose)
	end = time.clock()
	uptime = end-start

	states = sorted(policy.keys())
	print()
	print(">> Policy:")
	for s in states:
		print("Pi({0}) = {1}".format(s, policy[s]))
	print()

	print(">> Value:")
	for s in states:
		print("V({0}) = {1:.4f}".format(s, value_function[s]))
	print()

	print(">> Value iteration converged in {time:.3f}sec after {it} iterations.".format(time=uptime, it=iterations))
	print("@ Average time per iteration = {0:.3f}sec.".format(uptime/iterations))
	print("@ Max error = {0:.5f}".format(error))
	print()
