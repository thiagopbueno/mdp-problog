% Objetos
computer(c1).
computer(c2).
computer(c3).
computer(c4).
computer(c5).
computer(c6).
computer(c7).
computer(c8).
computer(c9).
computer(c10).

% Topologia da rede
connected(c1,[c4,c9]).
connected(c2,[c8]).
connected(c3,[c4,c9]).
connected(c4,[c5]).
connected(c5,[c7]).
connected(c6,[c4,c8]).
connected(c7,[c9]).
connected(c8,[c6,c10]).
connected(c9,[c6]).
connected(c10,[c2]).