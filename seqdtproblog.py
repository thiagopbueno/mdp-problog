#! /usr/bin/env python3

from problog.program import PrologString
from problog.engine  import DefaultEngine
from problog.logic   import Constant,Term,And,Clause
from problog         import get_evaluatable

import time

def usage(progname):
	print("Usage: {} /path/to/input.pl".format(progname))

def read_input(filename):
	with open(filename, 'r') as f:
		model = PrologString(f.read())
		return model

def init(model):
	# prepare grounding engine
	eng = DefaultEngine(label_all=True)
	db = eng.prepare(model)

	# find state variables and build state atoms
	state_functors, current_state_atoms, next_state_atoms = build_state_atoms(eng, db)
	# print(">> State functors:", end="")
	# print(state_functors)
	# print(">> Current state atoms: ", end="")
	# print(current_state_atoms)
	# print(">> Next state atoms:    ", end="")
	# print(next_state_atoms)
	# print()

	# add state decision facts
	for t in current_state_atoms:
		state_decision_fact = t.with_probability(Term('?'))
		db.add_fact(state_decision_fact)

	# build state rules and initial values
	state_rules, state_values = build_next_state_rules(next_state_atoms)

	# print(">> Next state rules:")
	for r in state_rules:
		db.add_clause(r)
		# print(r)
	# print()

	# print(">> Next state future values:")
	for u in state_values:
		db.add_fact(u)
		# print(u)
	# print()

	# get utility attributes
	# print(">> Utility attributes:")
	utilities = dict(eng.query(db, Term('utility', None, None)))
	# print(utilities)
	# print()

	# perform relevant grounding w.r.t. utility nodes
	gp = eng.ground_all(db, target=None, queries=utilities.keys())

	action_facts, state_facts = get_decision_facts(gp, state_functors)
	# print(action_facts)
	# print(state_facts)
	# print()

	return gp, action_facts, state_facts, utilities

def value_iteration(epsilon, gamma, gp, action_facts, state_facts, utilities):

	i = 0
	start = time.clock()
	print(">> iteration #{0} ...".format(i))
	value_function, policy, utilities, stats = update(gp, gamma, action_facts, state_facts, utilities)
	for s in sorted(value_function.keys()):
		print("V({0}) = {1:<12.6f}".format(s, value_function[s]))
	end = time.clock()
	print("<< executed in {time:.3f} sec.\n".format(time=end-start))

	while True:
		start = time.clock()
		print(">> iteration #{0} ...".format(i))

		new_value_function, policy, utilities, stats = update(gp, gamma, action_facts, state_facts, utilities)
		error = [ abs(new_value_function[s] - value_function[s]) for s in value_function.keys() ]

		print("error = {0:.5f}".format(max(error)))
		for s in sorted(new_value_function.keys()):
			print("V({0}) = {1:<12.6f}".format(s, new_value_function[s]))

		end = time.clock()
		print("<< executed in {time:.3f} sec.\n".format(time=end-start))

		if max(error) <= epsilon * (1-gamma) / (2*gamma):
			break

		value_function = new_value_function.copy()
		i += 1

	value_function, policy, utilities, stats = update(gp, gamma, action_facts, state_facts, utilities)
	return value_function, policy, i

def update(gp, gamma, action_facts, state_facts, utilities):
	knowledge = get_evaluatable(None).create_from(gp)
	value, policy, stats = search_exhaustive(knowledge, action_facts, state_facts, utilities)
	for u,v in utilities.items():
		if u.__repr__() in value.keys():
			utilities[u] = gamma * value[u.__repr__()]
	return value, policy, utilities, stats

def search_exhaustive(formula, actions, states, utilities):
	stats = {'eval': 0}

	state_decision_ids, state_decision_names = zip(*states)
	action_decision_ids, action_decision_names = zip(*actions)

	state_decision_names = tuple(sorted(state_decision_names, key=Term.__repr__, reverse=True))

	value = {}
	policy = {}

	for i in range(0, 1 << len(states)):
		state_choices = num2bits(i, len(states))
		# print(state_choices)
		state_evidence = dict(zip(state_decision_names, map(int, state_choices)))
		# print(state_evidence)

		best_score = None
		best_choice = None

		for j in range(0, 1 << len(actions)):
			action_choices = num2bits(j, len(actions))
			# print(action_choices)
			action_evidence = dict(zip(action_decision_names, map(int, action_choices)))
			# print(action_evidence)

			evidence = state_evidence.copy()
			evidence.update(action_evidence)

			# print(evidence)
			# print()

			score = evaluate(formula, evidence, utilities)
			stats['eval'] += 1
			if best_score is None or score > best_score:
				best_score = score
				best_choice = dict(evidence)

		s = "s{}".format(i)
		value[s] = best_score
		policy[s] = { k:v for (k,v) in best_choice.items() if k in action_decision_names }

	return value, policy, stats

def evaluate(formula, decisions, utilities):
	result = formula.evaluate(weights=decisions)
	score = 0.0
	for r in result:
		score += result[r] * float(utilities[r])
	return score

def num2bits(n, nbits):
	bits = [False] * nbits
	for i in range(1, nbits + 1):
		bits[nbits - i] = bool(n % 2)
		n >>= 1
	return bits

def build_state_atoms(eng, db):
	state_vars = [p[0] for p in eng.query(db, Term('state', None))]
	state_functors = set()
	current_state_atoms = []
	next_state_atoms = []
	for t in state_vars:
		state_functors.add(t.functor)
		args = t.args + (Constant(0),)
		current_state_atoms.append(t.with_args(*args))
		args = t.args + (Constant(1),)
		next_state_atoms.append(t.with_args(*args))
	return state_functors, current_state_atoms, next_state_atoms


def build_next_state_rules(next_state_atoms):
	state_rules = []
	value_utilities = []

	# initialize valuation
	n = len(next_state_atoms)
	valuation = [0]*n

	# build state rules
	for i in range(2**n):
		body_atoms = []
		for pos in range(n):
			if valuation[pos] == 1:
				body_atoms.append(next_state_atoms[pos])
			else:
				body_atoms.append(~next_state_atoms[pos])

		# build new rule
		body = And.from_list(body_atoms)
		head = Term('s{}'.format(i))
		rule = head << body

		value = Term('utility', head.with_probability(None), Constant(0.0))
		value_utilities.append(value)

		# store new rule
		state_rules.append(rule)

		# update valuation
		for pos in range(n):
			if valuation[pos] == 1:
				valuation[pos] = 0
			else:
				valuation[pos] = 1
				break

	return state_rules, value_utilities

def get_decision_facts(gp, state_functors):
	action_decision_facts = []
	state_decision_facts = []
	for i, n, t in gp:
		if t == 'atom' and n.probability == Term('?'):
			functor = n.name.functor
			if functor in state_functors:
				state_decision_facts.append((i,n.name))
			else:
				action_decision_facts.append((i, n.name))
	return action_decision_facts, state_decision_facts

if __name__ == '__main__':
	import sys

	if len(sys.argv) < 2:
		usage(sys.argv[0])
		exit(1)

	filename = sys.argv[1]
	model = read_input(filename)
	gp, action_facts, state_facts, utilities = init(model)

	gamma = 0.9
	epsilon = 0.01

	start = time.clock()
	value_function, policy, iterations = value_iteration(epsilon, gamma, gp, action_facts, state_facts, utilities)
	end = time.clock()
	print("@ Value iteration converged in {time:.3f}sec after {it} iterations.\n".format(time=end-start, it=iterations))

	print(">> Policy:")
	for s in sorted(policy.keys()):
		print("pi({0}) = {1}".format(s, policy[s]))
	print()
