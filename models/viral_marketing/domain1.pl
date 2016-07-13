% state
state_fluent(marketed(P)) :- person(P).

% actions
action(market(P)) :- person(P).
action(market(none)).

% utility
utility(market(P), -1) :- person(P).
utility(buys(P,1), 5) :- person(P).

% transition model
marketed(X,1) :- market(X).
0.5::marketed(X,1) :- not(market(X)), marketed(X,0).

% reward model
0.2::buy_from_marketing(P) :- person(P).
0.3::buy_from_trust(P) :- person(P).
buys(X,1) :- marketed(X,1), buy_from_marketing(X).
buys(X,1) :- trusts(X,Y), buys(Y,1), buy_from_trust(X).
