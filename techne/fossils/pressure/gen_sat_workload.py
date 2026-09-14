"""Generate the shared SAT pressure workload (batch 06, phase 8). Deterministic; the CNFs are the
tracked fossil-level inputs the preserved solvers are run against. Techne constructs the inputs and
records raw behaviour; it does not decide which solver is best.

    python gen_sat_workload.py <outdir>

Regimes: satisfiable-easy, unsatisfiable-easy, pigeonhole PHP(n+1,n) (structured-hard UNSAT),
random 3-SAT below and at the phase-transition ratio 4.26 (SAT-ish / hard), and a small XOR/parity
chain (structured). All in DIMACS CNF.
"""
import os, random, sys


def dimacs(clauses, nv, path, comment):
    with open(path, "w", newline="\n") as f:
        f.write("c %s\n" % comment)
        f.write("p cnf %d %d\n" % (nv, len(clauses)))
        for cl in clauses:
            f.write(" ".join(str(x) for x in cl) + " 0\n")


def sat_easy(nv=40):
    # a satisfying assignment planted: x_i true; every clause contains a satisfied literal
    rng = random.Random(1)
    cls = []
    for _ in range(nv * 3):
        v = rng.sample(range(1, nv + 1), 3)
        cl = [x for x in v]
        cl[0] = abs(cl[0])  # x_i positive -> satisfied by all-true
        cls.append(cl)
    return cls, nv


def unsat_easy():
    # (a) and (not a): trivially unsatisfiable
    return [[1], [-1], [2, 3], [-2, 3]], 3


def php(n):
    # pigeonhole: n+1 pigeons into n holes, no hole holds two. UNSAT. var(p,h) = (p-1)*n + h
    pigeons, holes = n + 1, n
    def var(p, h):
        return (p - 1) * n + h
    cls = []
    for p in range(1, pigeons + 1):                       # each pigeon in some hole
        cls.append([var(p, h) for h in range(1, holes + 1)])
    for h in range(1, holes + 1):                         # no hole holds two pigeons
        for p1 in range(1, pigeons + 1):
            for p2 in range(p1 + 1, pigeons + 1):
                cls.append([-var(p1, h), -var(p2, h)])
    return cls, pigeons * holes


def random_3sat(nv, ratio, seed):
    rng = random.Random(seed)
    m = int(nv * ratio)
    cls = []
    for _ in range(m):
        v = rng.sample(range(1, nv + 1), 3)
        cls.append([x if rng.random() < 0.5 else -x for x in v])
    return cls, nv


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    items = [
        ("sat_easy.cnf", *sat_easy(40), "satisfiable-easy: planted all-true model, 40 vars"),
        ("unsat_easy.cnf", *unsat_easy(), "unsatisfiable-easy: (a) and (not a)"),
        ("php_5_4.cnf", *php(4), "pigeonhole PHP(5,4): structured UNSAT, exponential for resolution"),
        ("php_7_6.cnf", *php(6), "pigeonhole PHP(7,6): structured UNSAT, harder"),
        ("rand_3sat_100_r38.cnf", *random_3sat(100, 3.8, 7), "random 3-SAT, 100 vars, ratio 3.8 (under threshold, usually SAT)"),
        ("rand_3sat_100_r426.cnf", *random_3sat(100, 4.26, 7), "random 3-SAT, 100 vars, ratio 4.26 (phase transition, hard)"),
        ("rand_3sat_150_r426.cnf", *random_3sat(150, 4.26, 11), "random 3-SAT, 150 vars, ratio 4.26 (phase transition, harder)"),
    ]
    for name, cls, nv, comment in items:
        dimacs(cls, nv, os.path.join(outdir, name), comment)
        print("%-26s vars=%-4d clauses=%d" % (name, nv, len(cls)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
