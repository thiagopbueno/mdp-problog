disk(1).
disk(2).
disk(3).

peg(a).
peg(b).
peg(c).

goal :- on(disk(1),disk(2),0), on(disk(2),disk(3),0), on(disk(3),peg(c),0).
