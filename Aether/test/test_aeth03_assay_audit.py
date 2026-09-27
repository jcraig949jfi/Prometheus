"""Adversarial fixtures from PROPAGATION_ASSAY_AUDIT.md.

1. A difference in carried non-byte state (rcv's received flag) must be able
   to cause visible differences, and a BYTES-ONLY predicate must then record
   locality violations while the assay's full predicate records none. If the
   bytes-only predicate stopped breaking, this fixture would no longer prove
   the flag matters.
2. Every law stays within its declared causal radius on random flips (a
   small light-cone sample; the full one is evidence, this is a regression
   guard).
3. The counterfactual parent audit agrees with the assay on a law where
   every differing neighbour is a cause (a payload relay chain), and finds
   no joint events there.
"""

import os
import sys

import numpy as np
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_HERE, "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth03_assay_audit as A          # noqa: E402
from observatory import aeth03_propagation as P          # noqa: E402
from observatory import aeth03_variants as V             # noqa: E402


def test_hidden_flag_breaks_a_bytes_only_predicate_but_not_the_assay():
    res = A.hidden_flag(n=32, ticks=40, rng=np.random.default_rng(5), trials=3)
    assert res["visible_later"] == 3
    assert res["violations_full_predicate"] == 0
    assert res["violations_bytes_only"] > 0


@pytest.mark.parametrize("law", A.LAWS)
def test_light_cone_within_declared_radius(law):
    res = A.lightcone(law, n=24, trials=60, rng=np.random.default_rng(11),
                      warm_ticks=40, worlds=4)
    assert res["premise_holds"], res


def test_parent_audit_matches_assay_on_a_pure_relay():
    n, length = 32, 10
    f = [np.zeros((n, n), dtype=np.uint8) for _ in range(5)]
    f[0][:] = 7
    f[4][:] = 200
    r = 5
    for c in range(2, 2 + length):
        f[0][r, c] = K.WRITE_OPCODE
        f[1][r, c] = K.EAST
        f[2][r, c] = K.PAYLOAD
        f[3][r, c] = 50
    par = dict(seed=7, write_cost=1, maintenance_cost=0, replenish_numer=0,
               replenish_amount=0, mut_numer=0)
    a = P.World("v1", f)
    b = a.copy()
    b.f[3][r, 2] ^= np.uint8(1 << 4)
    site = A.site_state_diff(a, b)
    events = sufficient = 0
    for t in range(1, 15):
        a_prev, b_prev, prev = a.copy(), b.copy(), site
        a.step(t, par)
        b.step(t, par)
        site = A.site_state_diff(a, b)
        for (rr, cc) in np.argwhere(site & ~prev):
            parents = [((rr + dr) % n, (cc + dc) % n) for dr, dc in P._NB
                       if prev[(rr + dr) % n, (cc + dc) % n]]
            assert parents
            events += 1
            sufficient += int(any(
                A.site_differs(A.patched_step(a_prev, b_prev, [p], t, par), a, rr, cc)
                for p in parents))
    assert events == length and sufficient == events
