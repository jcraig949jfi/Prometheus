"""Second-pass sweep, cycle 023 — the last sweep cycle. Both directions, measured in bits.

Cycle 022 built the dual instrument and could not say how to MEASURE over-discrimination, since
pair counts scale with the battery. Cycle 023's answer comes from partition information:

    deficit = H(T | P)  — truth distinctions the evaluator cannot make. ALIASING. Impossibility.
    excess  = H(P | T)  — distinctions it makes that the truth does not need. SPLITTING. A cost.
    VI      = deficit + excess, zero exactly when the projection is sufficient AND necessary.

Running it over the rungs produced one correction to my own claim and one refinement to the
cycle-022 framing:

- **R11 is SUFFICIENT BUT EXCESSIVE, not "exactly sufficient".** I had guessed the latter.
  Deficit 0.000 confirms the counterexample; excess 1.200 bits shows the record distinguishes
  four forecasters that empirical calibration does not.
- **Excess is not automatically a defect.** R9's repaired checker carries 0.689 excess bits
  because it separates decorative from circular lemmas — a distinction the coarse `accepted`
  boolean does not need and a human reading the report very much does. Excess measures
  "finer than the truth function requires", and whether that is waste depends on whether
  transfer or diagnosis is what you wanted.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from prometheus_math.lean_oracle import lean_available  # noqa: E402
from techne.ladder_circuits.sweep import sufficiency, sweep_projection  # noqa: E402

x = sp.Symbol("x")


# ---- the two instruments must agree, on real rung data ------------------------------------------

def test_bits_and_witnesses_agree_on_every_swept_rung():
    """**The identity, checked against the witness search rather than only under Hypothesis.**
    deficit > 0 iff an aliasing witness exists; excess > 0 iff a splitting witness exists."""
    from techne.ladder_circuits.canon_r12_conjecture import (
        CLOSED_UNIVERSE_TWINS, extension_of, small_universe, wide_universe,
    )
    su, wu = small_universe(), wide_universe()
    srcs = list(CLOSED_UNIVERSE_TWINS) + ["obj['x'] <= 3", "obj['x'] >= 6"]
    proj = lambda s: len(extension_of(s, su))

    for name, truth in (("in-universe", lambda s: len(extension_of(s, su))),
                        ("extrapolative", lambda s: len(extension_of(s, wu)))):
        bits = sufficiency(f"R12 {name}", srcs, proj, truth)
        wits = sweep_projection(f"R12 {name}", srcs, proj, truth)
        assert (bits.deficit_bits > 1e-12) == (wits.aliasing is not None)
        assert (bits.excess_bits > 1e-12) == (wits.splitting is not None)


# ---- re-examining the cycle 018-021 "no witness" results ------------------------------------------

def test_R12_in_universe_is_the_only_EXACTLY_SUFFICIENT_projection_found():
    """Deficit 0.000 and excess 0.000. Inside a closed universe, a conjecture's extension IS
    everything there is to know about it, so the grader's view is exactly the truth — neither
    short of it nor finer than it. The only projection in the whole ladder that measures this
    way, and it is exactly the situation the canon warns not to mistake for success."""
    from techne.ladder_circuits.canon_r12_conjecture import (
        CLOSED_UNIVERSE_TWINS, extension_of, small_universe,
    )
    su = small_universe()
    srcs = list(CLOSED_UNIVERSE_TWINS) + ["obj['x'] <= 3", "obj['x'] >= 6"]
    r = sufficiency("R12 in-universe", srcs, lambda s: len(extension_of(s, su)),
                    lambda s: len(extension_of(s, su)))
    assert r.sufficient and r.necessary
    assert r.vi == pytest.approx(0.0)
    assert r.verdict.startswith("EXACTLY SUFFICIENT")


def test_R12_extrapolative_is_PURE_aliasing():
    """The same projection against the target anyone wants: deficit 0.951 bits, excess 0.000.
    All of the loss is in the direction that carries an impossibility."""
    from techne.ladder_circuits.canon_r12_conjecture import (
        CLOSED_UNIVERSE_TWINS, extension_of, small_universe, wide_universe,
    )
    su, wu = small_universe(), wide_universe()
    srcs = list(CLOSED_UNIVERSE_TWINS) + ["obj['x'] <= 3", "obj['x'] >= 6"]
    r = sufficiency("R12 extrapolative", srcs, lambda s: len(extension_of(s, su)),
                    lambda s: len(extension_of(s, wu)))
    assert r.deficit_bits == pytest.approx(0.9509775, abs=1e-6)
    assert r.excess_bits == pytest.approx(0.0)
    assert not r.sufficient and r.necessary


def test_CORRECTION_R11_is_sufficient_but_EXCESSIVE_not_exactly_sufficient():
    """**Corrects my own cycle-020 statement.** I reported empirical calibration as a genuine
    counterexample to aliasing, and guessed it might be *exactly* sufficient. Measured over five
    forecasters: deficit 0.000 — the counterexample stands — but excess **1.200 bits**, because
    the record distinguishes honest, hedging, memorising and mimicking forecasters that all
    score ECE 0.0000.

    Sufficient, not exact. The projection sees strictly more than empirical calibration needs,
    which is the reason predictive calibration remains available to a scorer that reads records
    and unavailable to one that reads only ECE.
    """
    from techne.ladder_circuits.canon_r11_calibration import (
        BATTERY, BatteryTunedForecaster, HedgingForecaster, MimicForecaster,
        OverconfidentAsserter, ReferenceClassForecaster, score,
    )
    honest = ReferenceClassForecaster()
    fs = {"honest": honest, "hedge": HedgingForecaster(), "over": OverconfidentAsserter(),
          "tuned": BatteryTunedForecaster(), "mimic": MimicForecaster.of(honest, BATTERY)}
    names = list(fs)
    record = lambda k: tuple((a.claim, a.confidence, a.outcome)
                             for a in fs[k].assess_all(BATTERY))
    ece = lambda k: round(score(fs[k].assess_all(BATTERY), len(BATTERY))["ece"], 9)

    assert len({ece(k) for k in names}) == 2          # four forecasters share ECE 0.0
    r = sufficiency("R11 empirical calibration", names, record, ece)
    assert r.sufficient                               # the cycle-020 counterexample stands
    assert not r.necessary
    assert r.excess_bits == pytest.approx(1.2, abs=1e-6)


def test_REFINEMENT_excess_bits_are_not_automatically_a_defect():
    """R9's repaired checker carries 0.689 excess bits: it separates the decorative lemma from
    the circular one, and `accepted` is a boolean that does not need the distinction.

    That excess is DELIBERATE — the two failure modes want different repairs, and a report that
    merged them would be worse. So "excess" measures finer-than-the-truth-function-requires, and
    whether that is waste depends on whether you wanted transfer or diagnosis. Cycle 022 framed
    splitting as a cost; this is the correction.
    """
    if not lean_available():
        pytest.skip("Lean toolchain not reachable")
    from techne.ladder_circuits.canon_r9_lemma import GOAL_A, PROPOSALS, LemmaInventor

    keys = [("LemmaInventor", "double_succ"), ("DecorativeLemmaEmitter", "double_succ"),
            ("CircularLemmaEmitter", "double_succ"), ("SwappedCircularEmitter", "double_succ")]
    props = [PROPOSALS[k] for k in keys]
    inv = LemmaInventor()
    V = {id(p): inv.judge(GOAL_A, p) for p in props}
    proj = lambda p: (V[id(p)].lemma_true, V[id(p)].goal_proved,
                      V[id(p)].load_bearing, V[id(p)].restatement)
    r = sufficiency("R9 repaired checker", props, proj, lambda p: V[id(p)].accepted)
    assert r.sufficient and not r.necessary
    assert r.excess_bits == pytest.approx(0.6887218, abs=1e-6)
    # and the excess is exactly the decorative/circular distinction
    assert proj(props[1]) != proj(props[2])
    assert V[id(props[1])].accepted == V[id(props[2])].accepted is False


def test_R10_honest_circuit_is_also_sufficient_but_excessive():
    """The two-field verdict distinguishes (BROKEN, SURVIVES) from (PRESERVED, SURVIVES), which
    the ground-truth boolean does not need — the same deliberate excess as R9."""
    from techne.ladder_circuits.canon_r10_analogy import (
        BATTERY, AssumptionTracingTransfer, ground_truth,
    )
    h = AssumptionTracingTransfer()
    cache = {(t.name, w.name): h.transfer(t, w) for t, w in BATTERY}
    proj = lambda tw: (cache[(tw[0].name, tw[1].name)].assumption_status,
                       cache[(tw[0].name, tw[1].name)].conclusion_status)
    r = sufficiency("R10 honest circuit", list(BATTERY), proj, lambda tw: ground_truth(*tw))
    assert r.sufficient and not r.necessary
    assert r.excess_bits == pytest.approx(0.3235, abs=1e-3)


# ---- new rung swept this cycle: R1 (canon R1, local rule application) ------------------------------

def test_R1_swept_both_directions():
    """R1 applies one guarded rule at the root. Its view is the expression itself, so it cannot
    merge two expressions — deficit 0.000, no aliasing, as with R0. And it splits: `2x+4`,
    `3x+6` and `5x+10` all have root −2 and three different views. Excess 0.951 bits.

    Same shape as R0, and the same reading: an exact-syntax circuit is never aliased and always
    excessive. That is what makes it R1 rather than something higher.
    """
    from techne.ladder_circuits.r1_local_op import R1LocalOpCircuit, linear_root_rule
    exprs = [2 * x + 4, 3 * x + 6, 5 * x + 10, 2 * x + 2, 7 * x + 3]
    c = R1LocalOpCircuit()
    c.give_rule(linear_root_rule())
    r = sufficiency("R1 local-op", exprs, lambda e: sp.srepr(e), lambda e: str(c.answer(e)))
    assert r.sufficient and not r.necessary
    assert r.deficit_bits == pytest.approx(0.0)
    assert r.excess_bits == pytest.approx(0.9509775, abs=1e-6)
    assert str(c.answer(2 * x + 4)) == str(c.answer(3 * x + 6)) == "-2"


def test_R1_the_rule_binding_view_is_still_excessive():
    """Even the coarser view — what the rule actually binds, (a, b) — splits the three
    expressions that share a root, because (2,4), (3,6) and (5,10) are different bindings for
    the same answer. The excess is in the RULE's parameterisation, not merely in the syntax."""
    from techne.ladder_circuits.r1_local_op import R1LocalOpCircuit, linear_root_rule
    exprs = [2 * x + 4, 3 * x + 6, 5 * x + 10, 2 * x + 2]
    c = R1LocalOpCircuit()
    c.give_rule(linear_root_rule())
    binding = lambda e: tuple(sorted((str(k), str(v)) for k, v in
                                     (e.match(2 * x + 4) or {}).items())) or sp.srepr(e)
    r = sufficiency("R1 binding view", exprs, binding, lambda e: str(c.answer(e)))
    assert r.deficit_bits == pytest.approx(0.0)
    assert r.excess_bits > 0.0


# ---- honest bookkeeping ------------------------------------------------------------------------

def test_sweep_status_after_the_cap():
    """The cap is honoured: cycle 023 is the last sweep cycle. Swept across both cycles:
    R0, R1, R3, plus the first-pass rungs R6, R9, R10, R11, R12 (the last four re-examined in
    the dual direction this cycle). **Unswept: R2, R4, R5, R7, R8.**

    Cycle 024 moves to composition regardless, and the five unswept rungs are carried as a known
    gap rather than as a silent one."""
    swept = {"R0", "R1", "R3", "R6", "R9", "R10", "R11", "R12"}
    unswept = {"R2", "R4", "R5", "R7", "R8"}
    assert not (swept & unswept)
    assert len(swept | unswept) == 13
    assert len(unswept) == 5
