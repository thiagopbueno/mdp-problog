state_fluent(on(D1,D2)) :- disk(D1), disk(D2), D1 < D2.
state_fluent(on(D,P)) :- disk(D), peg(P).

action(move(D1,D2)) :- disk(D1), disk(D2), D1 < D2.
action(move(D,P)) :- disk(D), peg(P).
action(noop).

applicable(move(D1,D2)) :- clear(D1,0), clear(D2,0).

blocked(D,0) :- on(D1,D,0), D1 \== D.
clear(D,0) :- not(blocked(D,0)).
moved(D) :- move(D,_).

on(D1,D2,1) :- applicable(move(D1,D2)), move(D1,D2).
on(D1,D2,1) :- not(moved(D1)), on(D1,D2,0).

utility(move(D1,D2), -1) :- disk(D1), disk(D2), D1 < D2.
utility(move(D,P), -1) :- disk(D), peg(P).
utility(noop, 0).

utility(goal, 10).
