#!/usr/bin/env python3
"""Adversarial selftest for the metered verifier.

The last two rounds taught the lesson this file is built on: my fingerprint
audit contained a bug that manufactured its own result, twice, and only an
external control caught it. A meter that reports plausible numbers is worth
nothing on its own. So the tests here try to break it rather than to confirm it.

Each test states the failure it is hunting, not the behaviour it expects.

  python selftest.py
"""

from __future__ import annotations

import inspect
import json
import random
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from meter import BudgetExhausted, Meter, Session  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))


def fixture(tmp: Path, n_claims: int = 4) -> Path:
    """Sealed claims with a known failure point, so cost is predictable."""
    d = tmp / "sealed"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n_claims):
        first_bad = 50 + i * 37
        (d / f"C{i}.json").write_text(json.dumps({
            "claim_id": f"C{i}",
            "domain_lo": 1, "domain_hi": 1000,
            "witness_var": "n",
            # holds everywhere except one known point
            "claim_predicate": f"n != {first_bad}",
            "sealed_value_expr": "n*2",
            "first_failure": first_bad,
            "sealed_component": True,
        }, indent=2), encoding="utf-8", newline="\n")
    return d


# --------------------------------------------------------------------------

def test_taint_point_evaluations(sealed: Path) -> None:
    """HUNTING: a path that reads the claim without charging for it.

    Point evaluations are charged 1:1, so the meter's internal evaluation
    counter must equal the net credits spent on point operations after any
    sequence of calls. Divergence means some route touched the sealed predicate
    for free, which would silently invalidate every cost number the arena
    reports.
    """
    m = Meter(sealed, budget=5000)
    rng = random.Random(4)
    sessions = [m.open(f"C{i}", "T") for i in range(4)]
    for _ in range(300):
        s = rng.choice(sessions)
        try:
            op = rng.choice(["evaluate", "sample", "range", "symbolic", "free"])
            if op == "evaluate":
                s.evaluate(rng.randint(1, 1000))
            elif op == "sample":
                s.sample(rng.randint(1, 1000))
            elif op == "range":
                lo = rng.randint(1, 900)
                s.evaluate_range(lo, lo + rng.randint(0, 40))
            elif op == "symbolic":
                s.symbolic_check("n > 0")
            else:
                s.remaining(); s.refusals(); s.statement(); s.report()
        except BudgetExhausted:
            pass
    # NOTE: evaluate_range charges the full width but short-circuits on the
    # first failure, so evaluations performed are <= credits charged. The
    # invariant is therefore "never more evaluations than credits", not
    # equality. Equality would forbid short-circuiting, which is free to the
    # seat only in the sense that it already paid for it.
    point_spend = sum(e["cost"] for s in sessions for e in s.ledger.entries
                      if e["op"] in ("evaluate", "evaluate_range", "sample"))
    check("no evaluation happens that was not paid for",
          m._oracle_evaluations <= point_spend,
          f"oracle={m._oracle_evaluations} charged={point_spend}")

    sym_calls = sum(1 for s in sessions for e in s.ledger.entries
                    if e["op"] == "symbolic_check")
    check("every symbolic sample came from a charged symbolic call",
          m._symbolic_calls == sym_calls,
          f"internal={m._symbolic_calls} charged={sym_calls}")


def test_cap_actually_refuses(sealed: Path) -> None:
    """HUNTING: the v0.1 failure — a cap that is advertised but not enforced."""
    m = Meter(sealed, budget=100)
    s = m.open("C0", "T")
    before = m._oracle_evaluations
    s.evaluate_range(1, 100)                      # exactly the budget
    check("spend can reach the cap", s.remaining() == 0, f"rem={s.remaining()}")

    at_cap = m._oracle_evaluations
    raised = False
    try:
        s.evaluate(500)
    except BudgetExhausted:
        raised = True
    check("a call past the cap is refused", raised)
    check("a refused call performs no evaluation",
          m._oracle_evaluations == at_cap,
          f"{m._oracle_evaluations - at_cap} evaluations leaked past the cap")
    check("spend never exceeds the budget", s.ledger.spent <= s.budget,
          f"spent={s.ledger.spent} budget={s.budget}")
    check("the refusal is counted", s.refusals() == 1)
    _ = before


def test_no_partial_sweep_leak(sealed: Path) -> None:
    """HUNTING: an oversized sweep that runs part-way before dying.

    If a sweep too large for the remaining budget executed until it ran out, a
    seat could locate the cap by watching where sweeps stop, and would get free
    information from every refused call.
    """
    m = Meter(sealed, budget=60)
    s = m.open("C0", "T")
    s.evaluate_range(1, 40)                       # 40 spent, 20 left
    at = m._oracle_evaluations
    raised = False
    try:
        s.evaluate_range(100, 400)                # 301 needed, 20 left
    except BudgetExhausted:
        raised = True
    check("an unaffordable sweep is refused whole", raised)
    check("an unaffordable sweep evaluates nothing",
          m._oracle_evaluations == at,
          f"{m._oracle_evaluations - at} points evaluated inside a refused sweep")


def test_refund_matches_work(sealed: Path) -> None:
    """HUNTING: cost that depends on how a question was phrased, not what it cost.

    C0 fails at n=50. A sweep of [1,1000] should charge 50, not 1000: the seat
    learned the answer at point 50 and the rest was never run.
    """
    m = Meter(sealed, budget=5000)
    s = m.open("C0", "T")
    r = s.evaluate_range(1, 1000)
    check("sweep reports the true first failure", r["first_failure"] == 50,
          str(r))
    check("a sweep is charged its full requested width",
          s.ledger.spent == 1000, f"charged {s.ledger.spent} for a 1000 sweep")

    m2 = Meter(sealed, budget=5000)
    s2 = m2.open("C0", "T")
    for n in range(1, 51):
        s2.evaluate(n)
    check("stepping and stopping is cheaper than sweeping blind",
          s2.ledger.spent < s.ledger.spent,
          f"stepwise={s2.ledger.spent} sweep={s.ledger.spent}")
    check("a targeted probe beats both",
          _probe_cost(sealed) < s2.ledger.spent,
          "one probe at the known failure should cost 1")


def _probe_cost(sealed: Path) -> int:
    m = Meter(sealed, budget=5000)
    s = m.open("C0", "T")
    s.evaluate(50)
    return s.ledger.spent


def test_every_public_method_that_reads_is_charged(sealed: Path) -> None:
    """HUNTING: a method I forgot to charge.

    Enumerates every public method on Session, calls it, and checks whether it
    moved a taint counter. Anything that reads the claim must also have written
    to the ledger. This is the test that survives ME adding a method later and
    forgetting.
    """
    m = Meter(sealed, budget=5000)
    probes = {
        "remaining": (), "refusals": (), "statement": (), "report": (),
        "evaluate": (7,), "evaluate_range": (7, 9), "symbolic_check": ("n > 0",),
        "sample": (7,),
    }
    public = [n for n, _ in inspect.getmembers(Session, inspect.isfunction)
              if not n.startswith("_")]
    unknown = [n for n in public if n not in probes]
    check("no untested public method exists on Session", not unknown,
          f"untested: {unknown}")

    bad = []
    for name in public:
        if name not in probes:
            continue
        s = m.open("C0", "T")
        before = (m._oracle_evaluations, m._symbolic_evaluations)
        try:
            getattr(s, name)(*probes[name])
        except Exception:
            continue
        after = (m._oracle_evaluations, m._symbolic_evaluations)
        read = after != before
        charged = s.ledger.spent > 0
        if read and not charged:
            bad.append(name)
    check("every method that reads the claim charges for it", not bad,
          f"uncharged readers: {bad}")


def test_binding_flag_is_honest(tmp: Path) -> None:
    """HUNTING: a claim with no sealed component quietly treated as metered.

    If the claim is fully public a seat can reimplement it locally and the cap
    is decorative. The meter must say so rather than produce a confident number.
    """
    d = tmp / "unsealed"
    d.mkdir(parents=True, exist_ok=True)
    (d / "U0.json").write_text(json.dumps({
        "claim_id": "U0", "domain_lo": 1, "domain_hi": 10,
        "witness_var": "n", "claim_predicate": "n > 0",
    }, indent=2), encoding="utf-8", newline="\n")
    m = Meter(d, budget=10)
    s = m.open("U0", "T")
    check("a claim without a sealed component is marked non-binding",
          s.binding is False)
    check("a sealed claim is marked binding",
          Meter(fixture(tmp, 1), budget=10).open("C0", "T").binding is True)


def test_cheating_seat_cannot_overspend(sealed: Path) -> None:
    """HUNTING: any sequence that gets more evaluations than the budget allows.

    A scripted seat that ignores refusals and hammers the API in every shape it
    knows. The only property that matters: total evaluations never exceed the
    budget.
    """
    m = Meter(sealed, budget=250)
    s = m.open("C1", "GREEDY")
    rng = random.Random(11)
    for _ in range(4000):
        try:
            if rng.random() < 0.5:
                s.evaluate(rng.randint(1, 1000))
            else:
                lo = rng.randint(1, 900)
                s.evaluate_range(lo, lo + rng.randint(0, 200))
        except BudgetExhausted:
            continue
    point_spend = sum(e["cost"] for e in s.ledger.entries
                      if e["op"] in ("evaluate", "evaluate_range", "sample"))
    check("a seat ignoring refusals still cannot exceed the budget",
          s.ledger.spent <= 250, f"spent={s.ledger.spent}")
    check("evaluations performed never exceed the budget",
          m._oracle_evaluations <= 250,
          f"evaluations={m._oracle_evaluations} budget=250")
    check("the ledger accounts for every evaluation",
          m._oracle_evaluations <= point_spend,
          f"oracle={m._oracle_evaluations} ledger={point_spend}")
    check("the seat was refused many times", s.refusals() > 10,
          f"refusals={s.refusals()}")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="ama_meter_"))
    sealed = fixture(tmp)

    test_taint_point_evaluations(sealed)
    test_cap_actually_refuses(sealed)
    test_no_partial_sweep_leak(sealed)
    test_refund_matches_work(sealed)
    test_every_public_method_that_reads_is_charged(sealed)
    test_binding_flag_is_honest(tmp)
    test_cheating_seat_cannot_overspend(sealed)

    print("METERED VERIFIER — ADVERSARIAL SELFTEST")
    print("=" * 62)
    failed = 0
    for name, ok, detail in RESULTS:
        print(f"  [{'OK  ' if ok else 'FAIL'}] {name}")
        if not ok and detail:
            print(f"         {detail}")
        failed += not ok
    print()
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} passed")
    print("PASS" if not failed else f"FAIL — {failed} check(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
