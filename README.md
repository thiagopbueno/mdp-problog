# MDP-ProbLog

> MDP-ProbLog is a framework to represent and solve (infinite-horizon) MDPs by probabilistic logic programming.


## Install

It is required to have Python3 installed.

```
$ pip3 install mdpproblog
```

## Usage

```
$ mdp-problog --help
usage: mdp-problog [-h] [-g GAMMA] [-e EPSILON] domain instance

positional arguments:
  domain                path to MDP domain file
  instance              path to MDP instance file

optional arguments:
  -h, --help            show this help message and exit
  -g GAMMA, --gamma GAMMA
                        discount factor (default=0.9)
  -e EPSILON, --epsilon EPSILON
                        maximum error (default=0.1)
```

## Input

Domain specification for the sysadmin planning problem (models/sysadmin/domain.pl).

```prolog

% Network topology properties
accTotal([],A,A).
accTotal([_|T],A,X) :- B is A+1, accTotal(T,B,X).
total(L,T) :- accTotal(L,0,T).
total_connected(C,T) :- connected(C,L),
                        total(L,T).

accAlive([],A,A).
accAlive([H|T],A,X) :- running(H,0), B is A+1, accAlive(T,B,X).
accAlive([H|T],A,X) :- not(running(H,0)), B is A, accAlive(T,B,X).
alive(L,A) :- accAlive(L,0,A).
total_running(C,R) :- connected(C,L),
                      alive(L,R).

% State fluents
state_fluent(running(C)) :- computer(C).

% Actions
action(reboot(C)) :- computer(C).
action(reboot(none)).

% Transition model
1.00::running(C,1) :- reboot(C).
0.05::running(C,1) :- not(reboot(C)), not(running(C,0)).
P::running(C,1)    :- not(reboot(C)), running(C,0),
                      total_connected(C,T), total_running(C,R), P is 0.45+0.50*R/T.

% Utility attributes

% costs
utility(reboot(C), -0.75) :- computer(C).
utility(reboot(none), 0.00).

% rewards
utility(running(C,0),  1.00) :- computer(C).

```

## Example

```
$ mdp-problog models/sysadmin/domain.pl models/sysadmin/star2.pl --epsilon 0.01 --gamma 0.9

Value(running(c1,0)=0, running(c2,0)=0, running(c3,0)=0) = 16.976
Value(running(c1,0)=1, running(c2,0)=0, running(c3,0)=0) = 19.314
Value(running(c1,0)=0, running(c2,0)=1, running(c3,0)=0) = 19.343
Value(running(c1,0)=1, running(c2,0)=1, running(c3,0)=0) = 23.173
Value(running(c1,0)=0, running(c2,0)=0, running(c3,0)=1) = 19.343
Value(running(c1,0)=1, running(c2,0)=0, running(c3,0)=1) = 23.173
Value(running(c1,0)=0, running(c2,0)=1, running(c3,0)=1) = 21.525
Value(running(c1,0)=1, running(c2,0)=1, running(c3,0)=1) = 25.752

Policy(running(c1,0)=0, running(c2,0)=0, running(c3,0)=0) = reboot(c1)
Policy(running(c1,0)=1, running(c2,0)=0, running(c3,0)=0) = reboot(c3)
Policy(running(c1,0)=0, running(c2,0)=1, running(c3,0)=0) = reboot(c1)
Policy(running(c1,0)=1, running(c2,0)=1, running(c3,0)=0) = reboot(c3)
Policy(running(c1,0)=0, running(c2,0)=0, running(c3,0)=1) = reboot(c1)
Policy(running(c1,0)=1, running(c2,0)=0, running(c3,0)=1) = reboot(c2)
Policy(running(c1,0)=0, running(c2,0)=1, running(c3,0)=1) = reboot(c1)
Policy(running(c1,0)=1, running(c2,0)=1, running(c3,0)=1) = reboot(none)

>> Value iteration converged in 0.181sec after 59 iterations.
>> Average time per iteration = 0.003sec.
```

## License

Copyright (c) 2016-2017 Thiago Pereira Bueno All Rights Reserved.

MDPProbLog is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

MDPProbLog is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with MDPProbLog. If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).
