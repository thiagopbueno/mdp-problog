subset([], []).
subset([X|A], [X|B]):- subset(A, B).
subset([_|A], B):- subset(A, B).

member(X,[X|_]).
member(X,[_|A]) :- member(X,A).

% actions
action(market(X)) :- people(L), subset(L,X).

% costs
utility(market(X), -C) :- people(L), subset(L,X), length(X,C).

% state
state_fluent(marketed(P)) :- people(L), member(P,L).
state_fluent(buys(P)) :- people(L), member(P,L).

% transition
marketed(P,1) :- market(L), member(P,L).
0.5::marketed(P,1) :- market(L), not(member(P,L)), marketed(P,0).

% reward model
0.2::buy_from_marketing.
0.3::buy_from_trust.
0.1::buy_again.

buys(P,1) :- marketed(P,1), buy_from_marketing.
buys(P,1) :- trusts(P,Y), buys(Y,1), buy_from_trust.
buys(P,1) :- market(L), not(member(P,L)), buys(P,0), buy_again.

utility(buys(P,1), 5) :- people(L), member(P,L).