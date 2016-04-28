#! /usr/bin/env python3

from problog.program import PrologString
from problog.engine  import DefaultEngine
from problog.logic   import Constant,Term,And,Clause
from problog         import get_evaluatable

import time
import math

def read_input(domain, instance):
	model = ""
	with open(domain, 'r') as f:
		model += f.read()
	with open(instance, 'r') as f:
		model += f.read()
	return PrologString(model)

def init(model):
	# prepare grounding engine
	eng = DefaultEngine(label_all=True)
	db = eng.prepare(model)

	# find state variables and build state atoms
	state_functors, current_state_atoms, next_state_atoms = build_state_atoms(eng, db)

	# find action atoms
	action_atoms = build_action_atoms(eng, db)
	action_decision_facts, action_rules = build_action_rules(action_atoms)
	for f in action_decision_facts:
		db.add_fact(f)
	for r in action_rules:
		db.add_clause(r)

	# add state decision facts
	for t in current_state_atoms:
		state_decision_fact = t.with_probability(Term('?'))
		db.add_fact(state_decision_fact)

	# build state rules and initial values
	state_rules, state_values = build_next_state_rules(next_state_atoms)
	for r in state_rules:
		db.add_clause(r)
	for u in state_values:
		db.add_fact(u)

	# get utility attributes
	utilities = dict(eng.query(db, Term('utility', None, None)))

	# perform relevant grounding w.r.t. utility nodes
	gp = eng.ground_all(db, target=None, queries=utilities.keys())

	# get decision facts for action and state variables
	action_facts, state_facts = get_decision_facts(gp, state_functors)

	return gp, action_atoms, action_facts, state_facts, utilities

def value_iteration(epsilon, gamma, gp, action_facts, state_facts, utilities):

	i = 0
	start = time.clock()
	print(">> iteration #{0} ...".format(i))
	value_function, policy, utilities, stats = update(gp, gamma, action_facts, state_facts, utilities)
	states = [int(k[1:]) for k in value_function.keys()]
	for s in sorted(states):
		k = "s{}".format(s)
		print("V(s{0})\t= {1:<12.6f}".format(s, value_function[k]))
	end = time.clock()
	print("<< executed in {time:.3f} sec.\n".format(time=end-start))

	while True:
		start = time.clock()
		print(">> iteration #{0} ...".format(i))

		new_value_function, policy, utilities, stats = update(gp, gamma, action_facts, state_facts, utilities)
		error = [ abs(new_value_function[s] - value_function[s]) for s in value_function.keys() ]

		states = [int(k[1:]) for k in new_value_function.keys()]
		for s in sorted(states):
			k = "s{}".format(s)
			print("V(s{0})\t= {1:<12.6f}".format(s, new_value_function[k]))
		print("@ error = {0:.5f}".format(max(error)))

		end = time.clock()
		print("<< executed in {time:.3f} sec.\n".format(time=end-start))

		if max(error) <= epsilon*(1-gamma)/(gamma):
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
		state_evidence = dict(zip(state_decision_names, map(int, state_choices)))

		best_score = None
		best_choice = None

		for j in range(0, 1 << len(actions)):
			action_choices = num2bits(j, len(actions))
			action_evidence = dict(zip(action_decision_names, map(int, action_choices)))

			evidence = state_evidence.copy()
			evidence.update(action_evidence)

			score = evaluate(formula, evidence, utilities)
			stats['eval'] += 1
			if best_score is None or score > best_score:
				best_score = score
				best_choice = dict(evidence)

		s = "s{}".format(i)
		value[s] = best_score
		s = ', '.join(["{0}={1}".format(k,state_evidence[k]) for k in sorted(state_evidence.keys(), key=Term.__repr__)])
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

def build_action_atoms(eng, db):
	action_atoms = [p[0] for p in eng.query(db, Term('action', None))]
	return action_atoms

def build_action_rules(action_atoms):
	facts = []
	rules = []

	n = math.ceil(math.log2(len(action_atoms)))
	for i in range(1, n+1):
		facts.append(Term('a{}'.format(i), p=Term('?')))

	# initialize valuation
	valuation = [0]*n

	# build state rules
	for i in range(len(action_atoms)):
		body_atoms = []
		for pos in range(n):
			if valuation[pos] == 1:
				body_atoms.append(facts[pos])
			else:
				body_atoms.append(~facts[pos])

		body = And.from_list(body_atoms)
		head = action_atoms[i]
		rules.append(head << body)

		# update valuation
		for pos in range(n):
			if valuation[pos] == 1:
				valuation[pos] = 0
			else:
				valuation[pos] = 1
				break

	return facts, rules

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
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("domain", help="path to MDP domain file")
	parser.add_argument("instance", help="path to MDP instance file")
	args = parser.parse_args()

	model = read_input(args.domain, args.instance)
	gp, action_atoms, action_facts, state_facts, utilities = init(model)

	gamma = 0.9
	epsilon = 0.1

	start = time.clock()
	value_function, policy, iterations = value_iteration(epsilon, gamma, gp, action_facts, state_facts, utilities)
	end = time.clock()
	print("@ Value iteration converged in {time:.3f}sec after {it} iterations.\n".format(time=end-start, it=iterations))

	print(">> Policy:")
	for s in sorted(policy.keys()):
		strategy = policy[s]
		decision_facts = sorted(strategy.keys(), key=Term.__repr__)
		index = 0
		b = 1
		for a in decision_facts:
			index += b*strategy[a]
			b *= 2
		action = ""
		if index >= len(action_atoms):
			action = None
		else:
			action = action_atoms[index]
		print("Pi({0}) = {1}".format(s,action))
	print()
