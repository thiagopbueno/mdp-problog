#! /usr/bin/env python3

from problog.program import PrologString
from problog.engine  import DefaultEngine
from problog.logic   import Constant,Term,And,Clause

import inspect

def usage(progname):
	print("Usage: {} /path/to/input.pl".format(progname))

def init(filename):

	with open(filename, 'r') as f:

		# read problog model from string
		model = PrologString(f.read())

		# prepare grounding engine
		eng = DefaultEngine(label_all=True)
		db = eng.prepare(model)

		# find state variables and build state atoms
		state_functors, current_state_atoms, next_state_atoms = build_state_atoms(eng, db)
		print(">> State functors:", end="")
		print(state_functors)
		print(">> Current state atoms: ", end="")
		print(current_state_atoms)
		print(">> Next state atoms:    ", end="")
		print(next_state_atoms)
		print()

		# add state decision facts
		for t in current_state_atoms:
			state_decision_fact = t.with_probability(Term('?'))
			db.add_fact(state_decision_fact)

		# build state rules and initial values
		state_rules, state_values = build_next_state_rules(next_state_atoms)

		print(">> Next state rules:")
		for r in state_rules:
			db.add_clause(r)
			print(r)
		print()

		print(">> Next state future values:")
		for u in state_values:
			db.add_fact(u)
			print(u)
		print()

		# get utility attributes
		print(">> Utility attributes:")
		utilities = dict(eng.query(db, Term('utility', None, None)))
		print(utilities)
		print()

		# perform relevant grounding w.r.t. utility nodes
		gp = eng.ground_all(db, target=None, queries=utilities.keys())

		# get all decision facts
		print(">> Decision facts:")
		actions_decision_facts = []
		states_decision_facts = []
		for i, n, t in gp:
			if t == 'atom' and n.probability == Term('?'):
				functor = n.name.functor
				if functor in state_functors:
					states_decision_facts.append((i,n.name))
				else:
					actions_decision_facts.append((i, n.name))
		print(actions_decision_facts)
		print(states_decision_facts)
		print()

		return gp


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
		for pos in valuation:
			if pos == 1:
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


if __name__ == '__main__':
	import sys

	if len(sys.argv) < 2:
		usage(sys.argv[0])
		exit(1)

	filename = sys.argv[1]
	gp = init(filename)
	print(">> Ground program:")
	print(gp)
