% PBN (ProbLog)
% https://dtai.cs.kuleuven.be/problog/editor.html#task=prob&hash=7b033ef5ba69ac619614fdc5fe77f24b

% reward
utility(u1, -1).
utility(noop, 0).

utility(r1,  0).
utility(r2, -1).
utility(r3, -2).
utility(r4, -3).

r1 :- not(x1(0)), not(x2(0)).
r2 :- not(x1(0)), x2(0).
r3 :- x1(0), not(x2(0)).
r4 :- x1(0), x2(0).
