% PBN (ProbLog)
% https://dtai.cs.kuleuven.be/problog/editor.html#task=prob&hash=7b033ef5ba69ac619614fdc5fe77f24b

% intervention
action(u1).
action(noop).

% state
state_fluent(x1).
state_fluent(x2).

% PBN (transition)

% gene x1
1.0::f(1,1).

x1(1) :- f(1,1), not(u1), not(x1(0)), x2(0).
x1(1) :- f(1,1), not(u1), x1(0), not(x2(0)).
x1(1) :- f(1,1), u1, not(x1(0)), not(x2(0)).
x1(1) :- f(1,1), u1, not(x1(0)), x2(0).
x1(1) :- f(1,1), u1, x1(0), x2(0).

% gene x2
0.5::f(2,1);0.5::f(2,2).

% f1
x2(1) :- f(2,1), not(u1), x1(0), x2(0).
x2(1) :- f(2,1), u1, not(x1(0)), x2(0).
x2(1) :- f(2,1), u1, x1(0), not(x2(0)).
x2(1) :- f(2,1), u1, x1(0), x2(0).

% f2
x2(1) :- f(2,2), u1, x1(0), x2(0).
