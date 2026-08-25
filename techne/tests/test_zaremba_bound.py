"""`zaremba_test`'s search bound — cycle 060, finding #12.

Cycle 059's corrected input sweep recorded `techne/lib/cf_expansion.py::zaremba_test(2**63)`
as the arsenal's second HANG. It is not a non-terminating loop: the body is
`for a in range(1, q)`, which terminates in principle and never in practice. The loop's ledger
splits the two shapes as `S6a` (true non-termination) and `S6b` (unbounded runtime) precisely
because a guard for one does not catch the other.

Four categories per `.claude/skills/math-tdd`.
"""
from __future__ import annotations

import time

import pytest
from hypothesis import given, settings, strategies as st

from techne.lib.cf_expansion import (ZAREMBA_DEFAULT_MAX_Q, cf_expand,
                                     cf_max_digit, zaremba_test)


# --------------------------------------------------------------------------------------
# 1. AUTHORITY
# --------------------------------------------------------------------------------------

def test_authority_zaremba_holds_for_every_q_up_to_200():
    """Zaremba's conjecture with bound 5 holds for every q in 1..200.

    Reference: Zaremba, S. K. (1972), "La methode des 'bons treillis'..."; the conjecture is
    numerically verified far past this range, and Niederreiter (1986) proved it outright for
    q = 2^k and q = 3^k. The range here is chosen small enough to run in a test and large
    enough to include both proved families and many q outside them.

    The value being adjudicated is the CONJECTURE, not a snapshot of this function's output,
    so a bug that fabricated witnesses would have to fabricate them consistently with an
    external mathematical fact.

    **q = 1 WAS EXCLUDED FOR ONE CYCLE, AND THE EXCLUSION WAS THE FINDING.** Written first
    over `range(1, 201)`, this test failed at its FIRST element: `zaremba_test(1)` reported
    `satisfies=False`, because the body iterated `range(1, q)`, which is empty at q = 1 -- a
    trivially-satisfied case presented as a counterexample to a conjecture. Logged as cycle
    060 finding #16, narrowed to `range(2, 201)` for exactly ONE cycle so the defect stayed
    visible in the suite rather than being absorbed, and fixed in cycle 061 as its own
    isolated commit because it changes a RETURNED VALUE rather than adding a refusal. The
    range is now the full 1..200 it should always have been.
    """
    for q in range(1, 201):
        r = zaremba_test(q)
        assert r["satisfies"], f"no witness found for q={q}"


def test_authority_hand_checked_small_cases():
    """q = 13: 3/13 = [0; 4, 3], max digit 4 <= 5, so a = 3 is a witness. Hand-computed:
    13 = 4*3 + 1, 3 = 3*1 + 0, giving quotients 0, 4, 3.

    q = 1: a = 1 is the witness. gcd(1, 1) = 1 and 1/1 = [1], whose largest partial quotient
    is 1 <= 5. Hand-computed: divmod(1, 1) = (1, 0), so the expansion terminates at [1].

    This assertion previously read `n_tested == 0 and witness is None`, pinning the cycle-060
    defect in place so it could not drift while it waited for its own commit. It now pins the
    CORRECT value. Both expectations are recorded, because an assertion that quietly changes
    meaning between cycles is indistinguishable from one that was always right.
    """
    assert cf_expand(3, 13) == [0, 4, 3]
    assert cf_expand(1, 1) == [1]
    r13 = zaremba_test(13)
    assert r13["satisfies"] and cf_max_digit(r13["witness"], 13) <= 5
    r1 = zaremba_test(1)
    assert r1["satisfies"] and r1["witness"] == 1
    assert r1["n_tested"] == 1 and r1["min_max_digit"] == 1


# --------------------------------------------------------------------------------------
# 2. PROPERTY
# --------------------------------------------------------------------------------------

@settings(max_examples=60, deadline=None)
@given(st.integers(min_value=2, max_value=400))
def test_property_reported_witness_really_is_one(q):
    """INVARIANT: if a witness is reported, it is coprime to q and its CF digits are bounded.

    Verified through `cf_expand`, which does not share the search loop -- so a witness that
    only looked valid inside `zaremba_test`'s own bookkeeping fails here.
    """
    from math import gcd
    r = zaremba_test(q)
    if r["witness"] is not None:
        assert gcd(r["witness"], q) == 1
        assert max(cf_expand(r["witness"], q)) <= r["bound"]


@settings(max_examples=60, deadline=None)
@given(st.integers(min_value=1, max_value=500))
def test_property_the_bound_never_changes_an_in_range_answer(q):
    """A guard that altered results inside its own domain would be a bug, not a guard.

    `max_q=None` (unbounded) and the default ceiling must agree for every q below the ceiling.
    This is the false-block check for finding #12: the campaign requires the cost of a control
    to be reported beside its benefit, and the cost here is zero only if this holds.
    """
    assert zaremba_test(q) == zaremba_test(q, max_q=None)


# --------------------------------------------------------------------------------------
# 3. EDGE
# --------------------------------------------------------------------------------------

def test_edge_the_hang_input_now_refuses_immediately():
    """`zaremba_test(2**63)` -- the exact cycle-059 hang -- refuses in well under a second.

    Timing is asserted loosely (< 1 s) because the point is the difference between "returns an
    error" and "runs for ~10^5 years", not a performance figure. A tight threshold here would
    be a gate narrower than its own measurement error, which this loop has been burned by.
    """
    t = time.perf_counter()
    with pytest.raises(ValueError, match="exceeds max_q"):
        zaremba_test(2 ** 63)
    assert time.perf_counter() - t < 1.0


def test_edge_domain_and_type_refusals():
    """Enumerated edges:
    - q = 0 and q < 0: outside the conjecture's domain, ValueError
    - q = 1: in-domain, a = 1 is the witness (asserted in the authority test)
    - q just above the ceiling: refused; q at the ceiling: accepted by the guard
    - q a float or bool: TypeError, since `range(1, 2.0)` would fail confusingly later
    - max_q=None: the deliberate unbounded escape hatch still exists
    """
    with pytest.raises(ValueError):
        zaremba_test(0)
    with pytest.raises(ValueError):
        zaremba_test(-5)
    with pytest.raises(TypeError):
        zaremba_test(13.0)
    with pytest.raises(TypeError):
        zaremba_test(True)
    with pytest.raises(ValueError, match="exceeds max_q"):
        zaremba_test(ZAREMBA_DEFAULT_MAX_Q + 1)
    # At the ceiling the guard must not fire; a tiny explicit max_q proves the boundary is
    # `>` and not `>=` without running a 10-million-iteration search.
    assert zaremba_test(50, max_q=50)["q"] == 50
    with pytest.raises(ValueError):
        zaremba_test(51, max_q=50)


def test_edge_refusal_message_carries_a_number_and_its_provenance():
    """The refusal must let a caller decide whether to raise the ceiling.

    Cycle 059 reported "~131,000 years" for this function from a rate measured at q = 20,000
    and applied to q = 2^63 with no check that it held -- the extrapolate-across-populations
    move, committed inside a correction cataloguing eight prior instances of it. The message
    therefore quotes the q at which the rate was measured and says the projection is an
    extrapolation.
    """
    with pytest.raises(ValueError) as exc:
        zaremba_test(2 ** 63)
    msg = str(exc.value)
    assert "iter/s" in msg and "extrapolation" in msg and "years" in msg
    assert "max_q=None" in msg


# --------------------------------------------------------------------------------------
# 4. COMPOSITION
# --------------------------------------------------------------------------------------

def test_composition_min_max_digit_matches_an_independent_scan():
    """`min_max_digit` recomputed from `cf_expand` alone, without the search loop.

    Chains `zaremba_test` -> `cf_expand` -> `cf_max_digit`: three entry points that must agree
    about the same rational. A bookkeeping slip inside the search (`best_a` updated without
    `best_max`, say) survives every single-function test and dies here.
    """
    from math import gcd
    for q in (13, 47, 97, 144):
        r = zaremba_test(q)
        independent = min(cf_max_digit(a, q) for a in range(1, q) if gcd(a, q) == 1)
        assert r["min_max_digit"] == independent
        assert cf_max_digit(r["best_a"], q) == independent
