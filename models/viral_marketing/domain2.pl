% state
state_fluent(marketed(P)) :- person(P).
state_fluent(buys(P)) :- person(P).

% actions
action(market(P)) :- person(P).
action(market(none)).

% utility
utility(market(P), -1) :- person(P).
utility(buys(P,1), 5) :- person(P).

% rules
marketed(X,1) :- market(X).
0.5::marketed(X,1) :- not(market(X)), marketed(X,0).

0.2::buy_from_marketing.
0.3::buy_from_trust.
0.1::buy_again.
buys(X,1) :- marketed(X,1), buy_from_marketing.
buys(X,1) :- trusts(X,Y), buys(Y,1), buy_from_trust.
buys(X,1) :- not(market(X)), buys(X,0), buy_again.
