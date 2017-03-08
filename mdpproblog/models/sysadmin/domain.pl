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
action(reboot(C)) :- computer(C).
action(reboot(none)).

% transition model
1.00::running(C,1) :- reboot(C).
0.05::running(C,1) :- not(reboot(C)), not(running(C,0)).
P::running(C,1)    :- not(reboot(C)), running(C,0),
                      total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

% utility attributes

% costs
utility(reboot(C), -0.75) :- computer(C).
utility(reboot(none), 0.00).

% rewards
utility(running(C,0),  1.00) :- computer(C).
