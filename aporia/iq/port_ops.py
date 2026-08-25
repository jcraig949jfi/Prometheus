"""port_ops.py — IQ-PORT-1. The `all_but_n` port, kept OUTSIDE apollo/src on purpose.

The baseline pool C is `blackboard_evolve.REGISTRY`, byte-frozen and untouched (hash in
PREREG_IQ_PORT_1_2026-08-25.md). C u {p} is assembled in the measurement harness by adding
the ops defined here. Keeping the port in a separate module is what makes DeltaE and the
IQ-NULL step measurable at all -- if the port were edited into the registry there would be
no `C` left to compare against.

THREE components, and the honest split between them is the point:

  parse_all_but_n   NEW CODE. Nothing in C writes `quantities` (blackboard_evolve.py:100
                    records the slot as having no producer). The parser makes a dead slot
                    live. This is not a port; it is new.
  op_all_but_n      THE PORT. It must DELEGATE to fp.all_but_n and may not recompute T-N.
                    Delegation is verified by execution (monkeypatch), not by reading.
  (no new scorer)   The tail is C's own op_aggregate_quantities -> score_by_aggregate__g.

The four mutants exist only to be falsified. They are deliberately NOT ports: each computes
its own wrong arithmetic rather than delegating, because a mutant that delegated would not
be a mutant.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apollo" / "src"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

from blackboard import blackboard_op, BlackboardState, BlackboardOp  # noqa: E402
import forge_primitives as fp  # noqa: E402


# "There were 15 items. 1 were removed. How many remain?"
# Deliberately a little looser than the literal template (items?/was|were), but this is a
# template-shaped parser and that is a KNOWN limitation, not a hidden one: generalisation
# is TRANSFER-1's job, not IQ-PORT-1's. Quoting an all_but_n number from this step as
# evidence of a general capability would be the distribution counterfeit.
_RE_TOTAL = re.compile(r"there were\s+(\d+)\s+items?\b", re.IGNORECASE)
_RE_REMOVED = re.compile(r"\b(\d+)\s+(?:were|was)\s+removed\b", re.IGNORECASE)


@blackboard_op(reads=["problem_text"], writes=["quantities"])
def parse_all_but_n(state: BlackboardState) -> BlackboardState:
    """Parse a total and a removed-count into the `quantities` slot.

    Writes ONE slot, reads only `problem_text`. Writes nothing at all when either half of
    the pattern is absent -- that is what keeps the footprint to the tasks it is about.
    """
    m_total = _RE_TOTAL.search(state.problem_text)
    m_removed = _RE_REMOVED.search(state.problem_text)
    if not (m_total and m_removed):
        return state
    q = dict(state.quantities) if state.quantities else {}
    q["total"] = int(m_total.group(1))
    q["removed"] = int(m_removed.group(1))
    state.quantities = q
    return state


def _write_remaining(state: BlackboardState, value: int, provenance: str) -> BlackboardState:
    out = dict(state.counts) if state.counts else {}
    out["remaining"] = {"count": value, "provenance": provenance}
    state.counts = out
    return state


@blackboard_op(
    reads=["quantities"],
    writes=["counts"],
    precondition=lambda s: "total" in s.quantities and "removed" in s.quantities,
)
def op_all_but_n(state: BlackboardState) -> BlackboardState:
    """THE PORT. Delegates to forge_primitives.all_but_n; computes nothing itself.

    The attribute lookup `fp.all_but_n` is late-bound on purpose: monkeypatching the forge
    function must change this op's output, and that is the adapter-vs-rewrite test.
    """
    value = fp.all_but_n(total=state.quantities["total"], n=state.quantities["removed"])
    return _write_remaining(state, value, "fp.all_but_n(total,removed)")


# ── Mutation battery (answer-counterfeit falsifier). Not ports. ──────────────


def _mutant(name: str, kernel):
    def fn(state: BlackboardState) -> BlackboardState:
        return _write_remaining(state, kernel(state.quantities["total"],
                                              state.quantities["removed"]), f"mutant:{name}")
    return BlackboardOp(
        fn, reads=["quantities"], writes=["counts"],
        precondition=lambda s: "total" in s.quantities and "removed" in s.quantities,
        on_fail="skip", name=name,
    )


MUTANTS = {
    "M1_plus": _mutant("M1_plus", lambda t, n: t + n),
    "M2_off_by_one": _mutant("M2_off_by_one", lambda t, n: t - n + 1),
    "M3_swapped": _mutant("M3_swapped", lambda t, n: n - t),
    "M4_identity": _mutant("M4_identity", lambda t, n: t),
}

PORT_OPS = {
    "parse_all_but_n": parse_all_but_n,
    "op_all_but_n": op_all_but_n,
}


# ── IQ-NULL fixture, defined here so it is frozen alongside the port ─────────


@blackboard_op(reads=["problem_text"], writes=["quantities"])
def null_noop(state: BlackboardState) -> BlackboardState:
    """Type-compatible no-op: same reads/writes signature as parse_all_but_n, writes
    nothing. IQ-NULL requires DeltaE(null_noop) == 0 exactly. A non-zero reading would
    mean the assay measures search dynamics rather than expressivity."""
    return state
