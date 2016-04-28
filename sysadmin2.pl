% Objects
computer(c1).
computer(c2).
computer(c3).
computer(c4).
computer(c5).

% Topology facts & rules
connected(c1,[c2,c3,c4,c5]).
connected(c2,[c1,c4]).
connected(c3,[c1]).
connected(c4,[c1,c2]).
connected(c5,[c1]).

% Decision facts
?::a1.
?::a2.
?::a3.
reboot(c1) :- a1, not(a2), not(a3).
reboot(c2) :- not(a1), a2, not(a3).
reboot(c3) :- a1, a2, not(a3).
reboot(c4) :- not(a1), not(a2), a3.
reboot(c5) :- a1, not(a2), a3.