subset([], []).
subset([X|A], [X|B]):- subset(A, B).
subset([_|A], B):- subset(A, B).

member(X,[X|_]).
member(X,[_|A]) :- member(X,A).

% network topology properties
accTotal([],A,A).
accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
total(L,T) :- accTotal(L,0,T).
total_connected(C,T) :-
                 connected(C,L), % L = list of computers connected to computer C
                 total(L,T).     % T = total number of computers in list L

accAlive([],A,A).
accAlive([H|T],A,X) :- running(H,0), B is A+1, accAlive(T,B,X).
accAlive([H|T],A,X) :- not(running(H,0)), B is A, accAlive(T,B,X).
alive(L,A) :- accAlive(L,0,A).
total_running(C,R) :-
                connected(C,L), % L = list of computers connected to computer C
                alive(L,R).     % R = total number of running computers in list L

% state fluents
state_fluent(running(C)) :- computer(C).

% actions
max_nondef_actions(3).
action(reboot(X)) :- network(L), subset(L,X),  % L = list of networked computers
                     length(X,S), max_nondef_actions(M), S =< M.

% transition model
1.00::running(C,1) :- reboot(L), member(C,L).
0.05::running(C,1) :- reboot(L), not(member(C,L)), not(running(C,0)).
P::running(C,1)    :- reboot(L), not(member(C,L)), running(C,0),
                      total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

% utility attributes

% costs
utility(reboot(X), -0.75*T) :- network(L), subset(L,X), length(X,T).

% rewards
utility(running(C,1),  1.00) :- computer(C).
