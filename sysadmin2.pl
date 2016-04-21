% Objects
computer(c1).
computer(c2).
computer(c3).
computer(c4).
computer(c5).

% State variables
state(running(C)) :- computer(C).

%?::running(C,0) :- computer(C).

% Topology facts & rules
connected(c1,[c2,c3,c4,c5]).
connected(c2,[c1,c4]).
connected(c3,[c1]).
connected(c4,[c1,c2]).
connected(c5,[c1]).

accTotal([],A,A).
accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
total(L,T) :- accTotal(L,0,T).

accAlive([],A,A).
accAlive([H|T],A,X) :- running(H,0), B is A+1, accAlive(T,B,X).
accAlive([H|T],A,X) :- not(running(H,0)), B is A, accAlive(T,B,X).
alive(L,A) :- accAlive(L,0,A).

total_connected(C,T) :- connected(C,L), total(L,T).
total_running(C,R)   :- connected(C,L), alive(L,R).

% Transition rules
1.00::running(C,1) :- reboot(C).
0.10::running(C,1) :- not(reboot(C)), not(running(C,0)).
P::running(C,1) :- not(reboot(C)), running(C,0), total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

% Decision facts
?::a1.
?::a2.
?::a3.
reboot(c1) :- a1, not(a2), not(a3).
reboot(c2) :- not(a1), a2, not(a3).
reboot(c3) :- a1, a2, not(a3).
reboot(c4) :- not(a1), not(a2), a3.
reboot(c5) :- a1, not(a2), a3.

% Utility attributes
utility(reboot(C), -0.75)   :- computer(C).   % costs
utility(running(C,1), 1.00) :- computer(C).   % rewards