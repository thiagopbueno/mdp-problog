# mdp-problog

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

## Example

```
$ ./mdp-problog.py models/sysadmin/sysadmin.domain.pl models/sysadmin/hub2.pl --eps 0.1 --gamma 0.9

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
V(running(c1,0)=0, running(c2,0)=0, running(c3,0)=0) = 19.7257
V(running(c1,0)=0, running(c2,0)=0, running(c3,0)=1) = 20.9368
V(running(c1,0)=0, running(c2,0)=1, running(c3,0)=0) = 20.9368
V(running(c1,0)=0, running(c2,0)=1, running(c3,0)=1) = 22.0118
V(running(c1,0)=1, running(c2,0)=0, running(c3,0)=0) = 20.8778
V(running(c1,0)=1, running(c2,0)=0, running(c3,0)=1) = 23.7351
V(running(c1,0)=1, running(c2,0)=1, running(c3,0)=0) = 23.7351
V(running(c1,0)=1, running(c2,0)=1, running(c3,0)=1) = 25.3572

>> Value iteration converged in 4.963sec after 44 iterations.
@ Average time per iteration = 0.113sec.
@ Max error = 0.02166
```
