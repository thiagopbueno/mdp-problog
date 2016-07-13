# MDP-ProbLog

MDP-ProbLog is a framework to represent and solve (infinite-horizon) MDPs by probabilistic logic programming.


## Install

It is required to have Python3 installed.

```
$ pip3 install problog
$ git clone https://github.com/thiagopbueno/mdp-problog.git
```

## Usage

```
$ ./mdp-problog.py --help
usage: mdp-problog.py [-h] [-g GAMMA] [-e EPS] [-v VERBOSE] domain instance

positional arguments:
  domain                path to MDP domain file
  instance              path to MDP instance file

optional arguments:
  -h, --help            show this help message and exit
  -g GAMMA, --gamma GAMMA
                        discount factor (default=0.9)
  -e EPS, --eps EPS     relative error  (default=0.1)
  -v VERBOSE, --verbose VERBOSE
                        verbose mode (default=0)
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
utility(running(C,1),  1.00) :- computer(C).

```

## Example

```
$ ./mdp-problog.py models/sysadmin/domain.pl models/sysadmin/hub2.pl --eps 0.1 --gamma 0.

  >> Preprocessing program ... Done in 0.025sec.
  >> Relevant grounding ... Done in 0.050sec.
  >> Compilation ... Done in 0.017sec.

>> Policy:
Pi(running(c1,0)=0, running(c2,0)=0, running(c3,0)=0) = reboot(c1)
Pi(running(c1,0)=0, running(c2,0)=0, running(c3,0)=1) = reboot(c1)
Pi(running(c1,0)=0, running(c2,0)=1, running(c3,0)=0) = reboot(c1)
Pi(running(c1,0)=0, running(c2,0)=1, running(c3,0)=1) = reboot(c1)
Pi(running(c1,0)=1, running(c2,0)=0, running(c3,0)=0) = reboot(c2)
Pi(running(c1,0)=1, running(c2,0)=0, running(c3,0)=1) = reboot(c2)
Pi(running(c1,0)=1, running(c2,0)=1, running(c3,0)=0) = reboot(c3)
Pi(running(c1,0)=1, running(c2,0)=1, running(c3,0)=1) = reboot(none)

>> Value:
V(running(c1,0)=0, running(c2,0)=0, running(c3,0)=0) = 19.1341
V(running(c1,0)=0, running(c2,0)=0, running(c3,0)=1) = 20.6162
V(running(c1,0)=0, running(c2,0)=1, running(c3,0)=0) = 20.6162
V(running(c1,0)=0, running(c2,0)=1, running(c3,0)=1) = 21.8910
V(running(c1,0)=1, running(c2,0)=0, running(c3,0)=0) = 20.5864
V(running(c1,0)=1, running(c2,0)=0, running(c3,0)=1) = 23.6645
V(running(c1,0)=1, running(c2,0)=1, running(c3,0)=0) = 23.6645
V(running(c1,0)=1, running(c2,0)=1, running(c3,0)=1) = 25.3019

>> Value iteration converged in 0.295sec after 45 iterations.
@ Average time per iteration = 0.007sec.
@ Max error = 0.02158
```
