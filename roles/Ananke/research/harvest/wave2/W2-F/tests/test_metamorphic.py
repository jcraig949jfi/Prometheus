"""(5) Metamorphic experiment-testing harness. Core only (no PTE import).

Two suites:
  A. a pair-accuracy experiment with engine-neutral relations and four broken experiments (mutants);
  B. HISTORICAL: a reach experiment with a CAUSAL relation ("an intervention that acts after the readout
     cannot be reported as reaching it"). The digest-style reach check (lens.applied_ticks semantics) is the
     mutant, and the relation kills it.
"""
from __future__ import annotations

import numpy as np

from explib.metamorphic import (Relation, cue_blind_must_be_half, negate_world, permute_units, relabel_pairs,
                                run_suite)
from explib.reach import NOT_REACHED, UNAPPLIED, applied_ticks, certify
from explib.toys import ToyRing


# ---------------------------------------------------------------- A. pair-accuracy experiment
def _scores(x, ties=0.5):
    s = np.sign(np.asarray(x["outputs"], float))
    t = np.asarray(x["targets"])
    return np.where(s == 0, ties, (s == t).astype(float)).mean(-1)          # per unit, mean over trials


def _summary(pm):
    return {"acc": float(pm.mean()), "half_pairs": float(np.mean(pm == 0.5)), "min_pair": float(pm.min())}


def experiment(x):
    sc = _scores(x)
    pair = np.asarray(x["pair"])
    pm = np.array([sc[pair == p].mean() for p in np.unique(pair)])
    return _summary(pm)


def mut_adjacent(x):                     # assumes partners are adjacent rows (breaks under reordering)
    return _summary(_scores(x).reshape(-1, 2).mean(-1))


def mut_ties_correct(x):                 # scores a tie as correct
    sc = _scores(x, ties=1.0)
    pair = np.asarray(x["pair"])
    return _summary(np.array([sc[pair == p].mean() for p in np.unique(pair)]))


def mut_index_ids(x):                    # assumes pair ids are 0..P-1
    sc = _scores(x)
    pair = np.asarray(x["pair"])
    P = len(sc) // 2
    pm = np.array([sc[pair == p].mean() if (pair == p).any() else 0.0 for p in range(P)])
    return _summary(pm)


def mut_one_sided(x):                    # scores only the first unit of each pair
    sc = _scores(x)
    pair = np.asarray(x["pair"])
    return _summary(np.array([sc[np.nonzero(pair == p)[0][0]] for p in np.unique(pair)]))


def mut_ignores_targets(x):             # scores "output > 0" as correct, whatever the target
    s = np.sign(np.asarray(x["outputs"], float))
    sc = np.where(s == 0, 0.5, (s > 0).astype(float)).mean(-1)
    pair = np.asarray(x["pair"])
    return _summary(np.array([sc[pair == p].mean() for p in np.unique(pair)]))


def make_input(seed, P=16, K=6, tie_frac=0.2):
    rng = np.random.default_rng(seed)
    y0 = rng.choice([-1, 1], size=(P, K))
    targets = np.empty((2 * P, K), int)
    targets[0::2], targets[1::2] = y0, -y0
    good = rng.random((2 * P, K)) < 0.75
    out = np.where(good, targets, -targets) * rng.integers(1, 5, size=(2 * P, K))
    out[rng.random((2 * P, K)) < tie_frac] = 0
    return {"outputs": out, "targets": targets, "pair": np.repeat(np.arange(P), 2)}


def test_suite_is_adequate_and_every_relation_kills_a_mutant():
    inputs = [make_input(s) for s in range(4)]
    rels = [permute_units(), relabel_pairs(), negate_world(), cue_blind_must_be_half("acc")]
    muts = {"adjacent": mut_adjacent, "ties_correct": mut_ties_correct, "index_ids": mut_index_ids,
            "one_sided": mut_one_sided, "ignores_targets": mut_ignores_targets}
    r = run_suite(experiment, inputs, rels, muts)
    assert r["experiment_passes"], r["experiment"]
    assert r["adequate"], (r["idle_relations"], r["surviving_mutants"], r["kill_matrix"])
    # MUST-FAIL: drop the relations that kill index_ids and the suite is no longer adequate
    r2 = run_suite(experiment, inputs, [negate_world()], muts)
    assert not r2["adequate"] and r2["surviving_mutants"]


# ---------------------------------------------------------------- B. causal relation on reach
T, RO_T, RO = 12, 10, 3


def reach_experiment(x):
    e = ToyRing(mode="relay", ro=RO, T=T)
    U = e.n_units
    return certify(e, T, {x["t"]: x["target"]}, [RO_T] * U, [RO] * U)["verdict"]


def digest_reach_mutant(x):
    """lens.verify_reach's applied half: 'applied' if the whole-run digest ever differs."""
    e = ToyRing(mode="relay", ro=RO, T=T)
    U = e.n_units
    r = certify(e, T, {x["t"]: x["target"]}, [RO_T] * U, [RO] * U)
    return "APPLIED" if applied_ticks(r["record"]) > 0 else UNAPPLIED


def post_readout() -> Relation:
    """CAUSAL relation: move the intervention to the readout tick (it then acts after the readout); the
    experiment must not report anything that could license a 'reached' reading."""
    tf = lambda x, rng: dict(x, t=RO_T)
    return Relation("post_readout_cannot_reach", tf, lambda y, y2, *_: y2 in (UNAPPLIED, NOT_REACHED), "causal")


def test_causal_relation_kills_applied_is_reached_mutant():
    inputs = [{"t": 9, "target": ("flip_s", RO)}, {"t": 9, "target": ("flip_s_except", RO)},
              {"t": 5, "target": ("flip_s", 1)}]
    r = run_suite(reach_experiment, inputs, [post_readout()], {"digest_applied": digest_reach_mutant})
    assert r["experiment_passes"] and r["kill_matrix"]["digest_applied"]["post_readout_cannot_reach"]
    assert r["adequate"]


# ---------------------------------------------------------------- C. mutation operators (W2-C vocabulary)
def _no_delivery(step):
    def wrapped(self, w, t):
        w.mail[t % self.D] = 0
        return step(self, w, t)
    return wrapped


def test_operator_suite_with_W2C_vocabulary():
    """A channel-disabling operator must change a comm-dependent fixture's verdict (and is self-detected by the
    mirror identity alarm) and is invariant on a local latch; a no-op operator is EQUIVALENT."""
    import contextlib

    from explib.controls import mirror_identity
    from explib.metamorphic import StageResult, patched_attr, run_operator_suite
    from explib.toys import pair_means, unit_scores

    def stage(e):
        w = e.make("A")
        for t in range(20):
            e.step(w, t)
        out = w.s[:, e.ro].copy()
        acc = float(pair_means(unit_scores(out, e.y)).mean())
        alarm = ("MIRROR_IDENTITY",) if mirror_identity(out, e.y).outcome == "FAIL" else ()
        return StageResult("SIGNAL" if acc > 0.75 else "NULL", alarm, (out.tobytes().hex(),), {"acc": acc})

    class DisableChannel:
        name = "disable_channel"

        def active(self):
            return patched_attr(ToyRing, "step", _no_delivery(ToyRing.step))

    class NoOp:
        name = "noop"

        def active(self):
            return contextlib.nullcontext()

    fixtures = {"relay": ToyRing(T=40, mode="relay", ro=3), "latch": ToyRing(T=40, mode="latch")}
    expect = lambda op, fx: "invariant" if (op == "noop" or fx == "latch") else "change"
    r = run_operator_suite(stage, fixtures, [DisableChannel(), NoOp()], expect)
    cat = {k: v["category"] for k, v in r["rows"].items()}
    assert cat[("disable_channel", "relay")] == "KILLED(A)"
    assert cat[("disable_channel", "latch")] == "EQUIVALENT"
    assert cat[("noop", "relay")] == cat[("noop", "latch")] == "EQUIVALENT"
    assert not r["survivors"] and not r["fragile"]
    assert ToyRing.step.__name__ == "step"                       # the operator restored the engine
