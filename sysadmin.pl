% Objetos
computer(c1). computer(c2). computer(c3).

% Topologia da rede
connected(c1,[c2,c3]). connected(c2,[c1]). connected(c3,[c1]).