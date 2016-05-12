% Propriedades gerais da topologia da rede
accTotal([],A,A).
accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
total(L,T) :- accTotal(L,0,T).
total_connected(C,T) :- connected(C,L), % L é a lista de computadores conectados com C
                        total(L,T).     % T é o total de computadores na lista L

accAlive([],A,A).
accAlive([H|T],A,X) :- running(H,0), B is A+1, accAlive(T,B,X).
accAlive([H|T],A,X) :- not(running(H,0)), B is A, accAlive(T,B,X).
alive(L,A) :- accAlive(L,0,A).
total_running(C,R) :- connected(C,L), % L é a lista de computadores conectados com C
                      alive(L,R).     % R é o total de computadores em L em funcionamento

% Predicados de estado
state_fluent(running(C)) :- computer(C).

% Predicados de ação
action(reboot(C)) :- computer(C).
action(reboot(none)).

% Regras de transição
1.00::running(C,1) :- reboot(C).
0.10::running(C,1) :- not(reboot(C)), not(running(C,0)).
P::running(C,1)    :- not(reboot(C)), running(C,0),
                      total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

% Atributos de utilidade

% custos
utility(reboot(C), -0.75) :- computer(C).

% recompensas
utility(running(C,1),  1.00) :- computer(C).