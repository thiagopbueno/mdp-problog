#! /usr/bin/env python3

import sys

from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString

objects = """computer(c1).
computer(c2).
computer(c3)."""

decision_facts = """
?::a1.
?::a2.
reboot(c1) :- a1, not(a2).
reboot(c2) :- not(a1), a2.
reboot(c3) :- a1, a2."""

utility_attributes = """
utility(reboot(C), -0.75) :- computer(C).
utility(running(C,1), 1.00) :- computer(C)."""

# topology
background_knowledge = """
connected(c1,[c2,c3]).
connected(c2,[c1]).
connected(c3,[c1]).
accTotal([],A,A).
accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
total(L,T) :- accTotal(L,0,T).
accAlive([],A,A).
accAlive([H|T],A,X) :- running(H,0), B is A+1, accAlive(T,B,X).
accAlive([H|T],A,X) :- not(running(H,0)), B is A, accAlive(T,B,X).
alive(L,A) :- accAlive(L,0,A).
total_connected(C,T) :- connected(C,L), total(L,T).
total_running(C,R)   :- connected(C,L), alive(L,R).
1.00::running(C,1) :- reboot(C).
0.10::running(C,1) :- not(reboot(C)), not(running(C,0)).
P::running(C,1) :- not(reboot(C)), running(C,0), total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.
"""

# states
states_vars="""
state(running(C)) :- computer(C)."""

model = objects + states_vars + decision_facts + utility_attributes + background_knowledge
print(">> Model:")
print(model)

def initial_valuation(n):
    return [0]*n

def next_valuation(valuation):
    for j in range(n):
        if valuation[j] == 1:
            valuation[j] = 0
        else:
            valuation[j] = 1
            break
    return valuation

def state_predicates(valuation):
    state = ""
    for j in range(n):
        if valuation[j] == 1:
            state += "1.0::running(c{id},0). ".format(id=j+1)
        else:
            state += "0.0::running(c{id},0). ".format(id=j+1)
    return state

def state_rule(s, valuation):
    head = "s{s}".format(s=s)
    body = []
    for j in range(len(valuation)):
        if valuation[j] == 1:
            body.append("running(c{id},1)".format(id=j+1))
        else:
            body.append("not(running(c{id},1))".format(id=j+1))
    body = ','.join(body)
    state_rule = "{head} :- {body}. ".format(head=head, body=body)
    return state_rule

def future_utility_attribute(s, value, gamma):
    utility_attribute = "utility(s{s}, {value}). ".format(s=s, gamma=gamma, value=gamma*value)
    return utility_attribute

def solve_problog(model, debug=False):
    program = PrologString(model)
    decisions, score, statistics = dtproblog(program)
    if debug:
        print('score: %s' % score)
        for name, value in decisions.items():
            print('%s: %s' % (name, value))
    return (score, decisions)

def initialization(n, states, state_rules, future_utility_attributes, gamma):
    valuation = initial_valuation(n)
    for i in range(2**n):
        states.append(state_predicates(valuation))
        state_rules.append(state_rule(i, valuation))
        future_utility_attributes.append(future_utility_attribute(i, 0.0, gamma))
        valuation = next_valuation(valuation)

import time

# initialization
n = len(objects.split())
states = []
state_rules = []
future_utilities = [0.0]*(2**n)
future_utility_attributes = []
gamma = 0.9
initialization(n, states, state_rules, future_utility_attributes, gamma)
state_rules = '\n'.join(state_rules) + '\n'
model += state_rules

# value iteration
epsilon = 0.01

i = 0
while True:
    start = time.clock()
    print(">> iteration #{0} ...".format(i))

    finished = True
    value_function = '\n'.join(future_utility_attributes) + '\n'
    m = model + value_function

    i += 1
    for s in range(2**n):
        state = states[s]
        # print(m+state)
        # break

        score, decisions = solve_problog(m + state)
        error = abs(future_utilities[s] - score)

        print("state=s{s:<12.0f} | score={score:<12.6f} | error={err:<.6f}".format(s=s, score=score, err=error))

        if error > epsilon *(1-gamma)/(2*gamma):
            finished = False

        future_utilities[s] = score
        future_utility_attributes[s] = future_utility_attribute(s, score, gamma)

    end = time.clock()
    print("<< executed in {time:.3f} sec.\n".format(time=end-start))

    # break

    if finished:
        # print policy
        for s in range(2**n):
            state = states[s]
            score, decisions = solve_problog(m + state)
            state = state.split('. ')
            state = filter(lambda x: x.startswith("1.0"), state)
            state = map(lambda x: x[5:], state)
            state = ', '.join(state)
            print("state=s{s} | predicates={{{state}}} ->".format(s=s, state=state))
            for name, value in decisions.items():
                print ("\t%s: %s" % (name, value))
            print()
        break
