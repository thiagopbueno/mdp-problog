% topology
connected(c1,[c2,c3]).
connected(c2,[c1]).
connected(c3,[c1]).

% current state
running(c1).

% total number of connected computers
accTotal([],A,A).
accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
total(L,T) :- accTotal(L,0,T).

% total number of running connected computers
accAlive([],A,A).
accAlive([H|T],A,X) :- running(H), B is A+1, accAlive(T,B,X).
accAlive([H|T],A,X) :- not(running(H)), B is A, accAlive(T,B,X).
alive(L,A) :- accAlive(L,0,A).

total_connected(C,T) :- connected(C,L), total(L,T).
total_running(C,R)   :- connected(C,L), alive(L,R).
prob(C,P) :- total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.