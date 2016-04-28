% Objetos
computer(c1). computer(c2). computer(c3).

% Topologia da rede
connected(c1,[c2,c3]). connected(c2,[c1]). connected(c3,[c1]).

% Ações
?::a1.
?::a2.
reboot(c1) :- a1, not(a2).
reboot(c2) :- not(a1), a2.
reboot(c3) :- a1, a2.