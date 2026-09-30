"""DRAFT -- dev / Q2 query draw widened to 1..97 (W7, ARC3 PKG-6 fix (b)).

NEW MODULE; engine/a17.py is imported and never modified. NOTHING HERE IS
ADOPTED until the Aphrodite seat freezes it in a dated AMENDMENT.

Defect addressed: a17.Prov.task draws the query m = rng.randint(3, 97) while
T4 v1 declares (and tests) the query domain 1..97. Fix (b) keeps T4 v1 as the
instrument of record and makes the TRAINING distribution cover T4's declared
domain: dev examples, the Q2 probe pool and the pilot/validation/transfer
cells all draw m from 1..97.

Consequences (measured in w7_fixb.py, stated in REPORT.md):
  * The rng stream changes: randint(1, 97) and randint(3, 97) consume the
    Mersenne stream differently at rejection-sampling boundaries, so after the
    first divergent draw every later list value and query differs. EVERY dev
    set, every Q2 probe pool and hence possibly every Q2 size and every walk
    changes -- not only those of the query-1/2-sensitive families.
  * Q2's wrong-set now includes PRISTINE programs that differ from the witness
    only at queries 1/2, so Q2 sizes can grow for exactly the affected families.
  * Every p_* statistic, OBSERVE/VALIDATE/TRANSFER role draw and donor
    selection downstream of the foundry is re-drawn.
"""
import random

import a17
import basis_v4 as G

QUERY_LO = 1


class Prov197(a17.Prov):
    """a17.Prov with the query drawn from 1..97 (everything else identical)."""

    def task(self, f, rng, lr=G.SEARCH_LENGTHS):
        lo, hi = lr
        xs = [rng.randint(2, 30) for _ in range(rng.randint(lo, hi))]
        m = rng.randint(QUERY_LO, 97)
        return (("Family %s over: " % f) + ", ".join(map(str, xs)) + " with %d." % m,
                str(G.run_program(self.witness(f), xs + [m], True)))


def qualify(prov, f, label):
    """a17.qualify (exact-fast Q2) is provider-driven: with a Prov197 provider
    its probe pool is drawn from the widened distribution. Re-exported for
    clarity; no logic changes."""
    return a17.qualify(prov, f, label)


def _selftest():
    p = Prov197({"x": ("(acc + v)", "(acc // last)", "0")})
    ms = [p.nums_of(t)[-1] for t in p.tasks("x", 400, 7)]
    assert min(ms) == 1 and max(ms) <= 97
    old = a17.Prov({"x": ("(acc + v)", "(acc // last)", "0")})
    same = sum(a == b for a, b in zip(p.tasks("x", 400, 7), old.tasks("x", 400, 7)))
    print("Prov197 self-test OK; tasks identical to v1 draw: %d/400" % same)


if __name__ == "__main__":
    _selftest()
