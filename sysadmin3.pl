% Objects
computer(c3).
computer(c1).
computer(c2).

% Decision facts (actions)
?::reboot(X) :- computer(X).

% Utility attributes (rewards and costs)
utility(reboot(X), -0.75) :- computer(X).
utility(running(X), 1.00) :- computer(X).

% Background Knowledge
1.00::running(X) :- reboot(X).
0.10::running(X) :- not(reboot(X)), not(was_running(X)).

1.00::running(c1) :- not(reboot(c1)), was_running(c1), was_running(Y), was_running(Z), Y \== Z.
0.83::running(c1) :- not(reboot(c1)), was_running(c1), not(was_running(Y)), was_running(Z), Y \== Z.
0.56::running(c1) :- not(reboot(c1)), was_running(c1), not(was_running(Y)), not(was_running(Z)), Y \== Z.

1.00::running(X) :- not(reboot(X)), was_running(X), was_running(c1), X \== c1.
0.75::running(X) :- not(reboot(X)), was_running(X), not(was_running(c1)), X \== c1.

% Current state
