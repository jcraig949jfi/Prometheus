"""Differential test: compiled kernel (wm_mini.py) against the pure-Python oracle (oracle.py).

Compares, trial by trial: trial type, stimulus, action, correctness; then the
final persistent store and the instruction count. Runs designed organisms and
random programs, under every harness and world switch.

    python differential_test.py            # exit 0 if every comparison is identical

It also contains its own fire test: a deliberately wrong oracle (SUB computed
as ADD) must be reported as a mismatch. A comparison that cannot fail is not a
comparison.
"""
import sys

import numpy as np

import oracle
import organisms as org
import rulers
import wm_mini as wm


def compare(prog, store0, P, life, aff_store, reset_fmem, leaky, oracle_mod=oracle):
    L = rulers.Life(prog, store0, life, P, aff_store=aff_store, reset_fmem=reset_fmem, leaky=leaky).run(P.E)
    rows, store, instr = oracle_mod.run_life([tuple(int(v) for v in w) for w in prog], list(store0),
                                             P.seed, life, P.K, P.R, P.E, P.T, P.F, P.cap,
                                             aff_store=aff_store, reset_fmem=reset_fmem, leaky=leaky)
    if [tuple(r) for r in L.rows] != [tuple(r) for r in rows]:
        return "rows differ"
    if [int(v) for v in L.store] != [int(v) for v in store]:
        return "final store differs"
    if int(L.instr) != int(instr):
        return "instruction count differs (%d vs %d)" % (L.instr, instr)
    return None


def random_program(rng, n):
    p = np.empty((n, 4), dtype=np.int64)
    p[:, 0] = rng.integers(0, 4 * wm.NOPS, n)      # exercises "op mod NOPS"
    p[:, 1:] = rng.integers(0, 100, (n, 3))        # exercises field reduction
    return p


def main():
    P = rulers.Params()
    rng = np.random.default_rng(12345)
    cases = []
    designed = {
        "builder(8)": (org.builder(P.K), org.empty_store(P.S)),
        "builder(3)": (org.builder(3), org.empty_store(P.S)),
        "holder(8)": (org.holder(P.K), org.empty_store(P.S)),
        "constant": (org.constant(), org.empty_store(P.S)),
        "lookup": (org.lookup(), org.lookup_store(P.seed, 7, P.K, P.R, P.S)),
        "leak_reader": (org.leak_reader(), org.empty_store(P.S)),
    }
    for name, (prog, st) in designed.items():
        cases.append((name, prog, st))
    for i in range(300):
        n = int(rng.integers(1, 40))
        st = rng.integers(0, 65536, P.S).astype(np.int64) if i % 3 == 0 else org.empty_store(P.S)
        cases.append(("random_%03d" % i, random_program(rng, n), st))

    switches = [(True, True, False), (False, True, False), (True, False, False), (True, True, True)]
    checked = bad = 0
    for name, prog, st in cases:
        for (aff, rst, leak) in switches:
            for life in (0, 5, 1_000_003):
                err = compare(prog, st, P, life, aff, rst, leak)
                checked += 1
                if err:
                    bad += 1
                    print("MISMATCH %s aff=%s reset=%s leaky=%s life=%d: %s" % (name, aff, rst, leak, life, err))
    print("differential: %d comparisons, %d mismatches" % (checked, bad))

    # fire test: a wrong oracle must be caught
    class WrongMachine(oracle.Machine):
        def phase(self, obs, phase):
            saved = self.prog
            self.prog = [((5,) + w[1:]) if w[0] % 19 == 6 else w for w in saved]   # SUB -> ADD
            try:
                return super().phase(obs, phase)
            finally:
                self.prog = saved

    class WrongOracle:
        @staticmethod
        def run_life(*a, **k):
            real = oracle.Machine
            oracle.Machine = WrongMachine
            try:
                return oracle.run_life(*a, **k)
            finally:
                oracle.Machine = real

    err = compare(org.builder(P.K), org.empty_store(P.S), P, 0, True, True, False, oracle_mod=WrongOracle)
    fired = err is not None
    print("fire test (oracle with SUB computed as ADD): %s" % ("caught: " + err if fired else "NOT CAUGHT"))

    ok = (bad == 0) and fired
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
