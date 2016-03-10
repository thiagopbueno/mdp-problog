% Objects
computer(c3).
computer(c1).
computer(c2).

% Decision facts (actions)
?::reboot(X) :- computer(X).

% Utility attributes (rewards and costs)
utility(reboot(X), -0.75) :- computer(X).
utility(running(X), 1.00) :- computer(X).

% Utility attributes (expected future rewards - value function)
% gamma = 0.9 (discount)

state(s1) :- not(running(c1)), not(running(c2)), not(running(c3)).
utility(state(s1), 0 * 0.9).

state(s2) :- running(c1), not(running(c2)), not(running(c3)).
utility(state(s2), 1 * 0.9).

state(s3) :- not(running(c1)), running(c2), not(running(c3)).
utility(state(s3), 1 * 0.9).

state(s4) :- running(c1), running(c2), not(running(c3)).
utility(state(s4), 2 * 0.9).

state(s5) :- not(running(c1)), not(running(c2)), running(c3).
utility(state(s5), 1 * 0.9).

state(s6) :- running(c1), not(running(c2)), running(c3).
utility(state(s6), 2 * 0.9).

state(s7) :- not(running(c1)), running(c2), running(c3).
utility(state(s7), 2 * 0.9).

state(s8) :- running(c1), running(c2), running(c3).
utility(state(s8), 3 * 0.9).

% Background Knowledge
1.00::running(X) :- reboot(X).
0.10::running(X) :- not(reboot(X)), not(was_running(X)).
1.00::running(X) :- not(reboot(X)), was_running(X), was_running(Y), was_running(Z), Y \== Z.
0.83::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), was_running(Z), Y \== Z.
0.56::running(X) :- not(reboot(X)), was_running(X), not(was_running(Y)), not(was_running(Z)), Y \== Z.

% Current state
was_running(c1).
was_running(c3).
