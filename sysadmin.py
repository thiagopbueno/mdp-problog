#! /usr/bin/env python3

from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString

objects = """
computer(c1).
computer(c3).
computer(c2).
"""

decision_facts = """
?::reboot(X) :- computer(X).
"""

utility_attributes = """
utility(reboot(X), -0.75) :- computer(X).
utility(running(X), 1.00) :- computer(X).
"""

background_knowledge = """
1.00::running(X) :- reboot(X).
0.10::running(X) :- not(reboot(X)), not(was_running(X)).
1.00::running(X) :- not(reboot(X)), was_running(X), was_running(Y), was_running(Z), Y \== Z.
0.83::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), was_running(Z), Y \== Z.
0.56::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), not(was_running(Z)), Y \== Z.
"""

initial_state = """
was_running(fake).
was_running(c1).
"""

model = objects + decision_facts + utility_attributes + background_knowledge + initial_state

program = PrologString(model)
decisions, score, statistics = dtproblog(program)

print('score: %s' % score)
for name, value in decisions.items():
    print('%s: %s' % (name, value))
