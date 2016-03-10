#! /usr/bin/env python3

from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString

model = """
computer(c1).
computer(c3).
computer(c2).

?::reboot(X) :- computer(X), X \== c0.

utility(reboot(X), -0.75) :- computer(X), X \== c0.
utility(running(X), 1.00) :- computer(X), X \== c0.

1.00::running(X) :- reboot(X).
0.10::running(X) :- not(reboot(X)), not(was_running(X)).
1.00::running(X) :- not(reboot(X)), was_running(X), was_running(Y), was_running(Z), Y \== Z.
0.83::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), was_running(Z), Y \== Z.
0.56::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), not(was_running(Z)), Y \== Z.

was_running(c0).
"""

program = PrologString(model)
decisions, score, statistics = dtproblog(program)

print('score: %s' % score)
for name, value in decisions.items():
    print('%s: %s' % (name, value))
