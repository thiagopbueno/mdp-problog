% Objects
computer(c0).
computer(c1).
computer(c2).
computer(c3).

% Decision facts (actions)
?::reboot(X) :- computer(X), X \== c0.

% Utility attributes (rewards and costs)
utility(reboot(X), -0.75) :- computer(X), X \== c0.
utility(running(X), 1.00) :- computer(X), X \== c0.

% Background Knowledge
1.00::running(X) :- reboot(X).
0.10::running(X) :- not(reboot(X)), not(was_running(X)).
1.00::running(X) :- not(reboot(X)), was_running(X), was_running(Y), was_running(Z), Y \== Z.
0.83::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), was_running(Z), Y \== Z.
0.56::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), not(was_running(Z)), Y \== Z.

% Current state
was_running(c0).