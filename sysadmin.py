#! /usr/bin/env python3

from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString

objects = """computer(c1).
computer(c3).
computer(c2)."""

decision_facts = """
?::reboot(X) :- computer(X)."""

utility_attributes = """
utility(reboot(X), -0.75) :- computer(X).
utility(running(X), 1.00) :- computer(X)."""

background_knowledge = """
1.00::running(X) :- reboot(X), computer(X).
0.10::running(X) :- not(reboot(X)), not(was_running(X)), computer(X).
1.00::running(X) :- not(reboot(X)), was_running(X), was_running(Y), was_running(Z), Y \== Z, computer(X), computer(Y), computer(Z).
0.83::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), was_running(Z), Y \== Z, computer(X), computer(Y), computer(Z).
0.56::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), not(was_running(Z)), Y \== Z, computer(X), computer(Y), computer(Z).
"""

model = objects + decision_facts + utility_attributes + background_knowledge

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
    if sum(valuation) == 0:
        state = "was_running(fake). "
    else:
        state = ""
        for j in range(n):
            if valuation[j] == 1:
                state += "was_running(c{id}). ".format(id=j+1)
    return state

def state_rule(s, valuation):
    head = "state(s{s})".format(s=s)
    body = []
    for j in range(len(valuation)):
        if valuation[j] == 1:
            body.append("was_running(c{id})".format(id=j+1))
        else:
            body.append("not(was_running(c{id}))".format(id=j+1))
    body = ','.join(body)
    state_rule = "{head} :- {body}. ".format(head=head, body=body)
    return state_rule

def future_utility_attribute(s, value, gamma):
    utility_attribute = "utility(state(s{s}), {value}). ".format(s=s, gamma=gamma, value=gamma*value)
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
epsilon = 0.1
i = 0
while True:
    finished = True
    value_function = '\n'.join(future_utility_attributes) + '\n'
    m = model + value_function
    i += 1
    print("iteration #{0}".format(i))
    for s in range(2**n):
        state = states[s]
        score, decisions = solve_problog(m + state)
        print("state=s{s} | score={score:5.2f} | predicates={{ {state} }}".format(s=s, score=score, state=state))
        if abs(future_utilities[s] - score) > epsilon *(1-gamma)/(2*gamma):
            finished = False
        future_utilities[s] = score
        future_utility_attributes[s] = future_utility_attribute(s, score, gamma)
    print()
    if finished:
        for s in range(2**n):
            state = states[s]
            score, decisions = solve_problog(m + state)
            print("state=s{s} | predicates={{ {state} }} :".format(s=s, state=state))
            for name, value in decisions.items():
                print ("\t%s: %s" % (name, value))
            print()
        break
