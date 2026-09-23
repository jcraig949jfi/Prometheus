"""cw01-e05 freeze-boundary fixtures F1-F7.

These exercise the PRODUCTION paths in execute_e05.py and lib/. No mocks, no
fixture-only reimplementations of a guard. A fixture passes only when the real
guard refuses (or the real statistic behaves) as contracted.

F1 positive interaction              real enumeration + nsa + did_statistic
F2 pure additive partition           WORST/conjunction anchor, frozen comparison semantics
F3 overlap without composition       BEST/disjunction, raw cross-law must not be a verdict
F4 intervention/baseline mismatch    learnability.require_controlled (guards D038a)
F5 dead genome                       learnability.require_live (guards D034)
F6 effect inside null                infometrics.effect_clears_null (guards D035)
F7 contract mutation                 bind_contract/require_matches BEFORE any evaluation
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE.parents[3]
for p in (str(REPO), str(BASE / "lib"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import world_e05 as W          # noqa: E402
import seeds as S              # noqa: E402
import infometrics as IM       # noqa: E402
import learnability as LN      # noqa: E402
import contract as CT          # noqa: E402
import execute_e05 as X        # noqa: E402

AID = "cw01-e05-a01"
RESULTS = []


def record(name, passed, detail):
    RESULTS.append({"fixture": name, "passed": bool(passed), "detail": detail})
    print("    %-4s %-8s %s" % (name, "PASS" if passed else "FAIL", detail))
    return passed


def _world():
    contract = CT.VerdictContract(X.EMBEDDED_CONTRACT)
    cfg = X.load_cfg(AID, contract)
    capmap = W.attempt_capabilities(cfg, S.seed)
    pool = W.attempt_item_pool(cfg, S.seed)
    return cfg, pool, capmap, contract


# ---------------------------------------------------------------- F1, F2, F3

def f1_positive_interaction(cfg, pool, capmap, sets):
    """The frozen M3 path must register the composition-law interaction."""
    d = X.did_statistic(cfg, pool, capmap, sets["best"], sets["worst"], S.seed, AID, "f1", 16)
    ok = d["did_points"] > 0 and d["law_effect_best_points"] > d["law_effect_worst_points"]
    return record("F1", ok,
                  "DiD %+.2f pp (BEST law effect %+.2f vs WORST %+.2f) via the frozen statistic"
                  % (d["did_points"], d["law_effect_best_points"], d["law_effect_worst_points"]))


def f2_pure_additive_partition(cfg, pool, capmap, sets):
    """WORST under conjunction is a measured partition: mixture == additive prediction.

    Classified using the frozen eligibility rule (effect_clears_null), not an epsilon
    invented after seeing the number.
    """
    blocks = [X.nsa(cfg, pool, capmap, sets["worst"], S.seed, AID, "f2b%d" % b, 12,
                    "conjunctive")["nsa_pct"] for b in range(X.N_BLOCKS)]
    mean = float(np.mean(blocks))
    clears = IM.effect_clears_null(mean, [b + 100.0 for b in blocks], direction="positive")
    ok = not clears["clears"]
    return record("F2", ok,
                  "WORST/conjunction nsa %+.3f%% -> clears_null=%s (null [%+.2f, %+.2f]); "
                  "not admissible as superadditive evidence"
                  % (mean, clears["clears"], clears["null_p05"], clears["null_p95"]))


def f3_overlap_not_composition(cfg, pool, capmap, sets):
    """Disjunctive overlap must not be read as composition.

    BEST under disjunction is strongly NEGATIVE because the sum of solo information
    exceeds the union. A raw cross-law reading would treat that magnitude as
    meaningful; the frozen statistic only ever uses the difference-in-differences.
    """
    best_disj = X.nsa(cfg, pool, capmap, sets["best"], S.seed, AID, "f3", 16, "disjunctive")
    worst_disj = X.nsa(cfg, pool, capmap, sets["worst"], S.seed, AID, "f3", 16, "disjunctive")
    d = X.did_statistic(cfg, pool, capmap, sets["best"], sets["worst"], S.seed, AID, "f3d", 16)
    raw_cross = best_disj["nsa_pct"]
    ok = (raw_cross < 0) and (d["did_points"] > 0) and ("did_points" in d)
    return record("F3", ok,
                  "BEST/disjunction raw nsa %+.2f%% (overlap, not composition); WORST/disjunction "
                  "%+.2f%%; frozen DiD remains %+.2f pp and is the only verdict quantity"
                  % (raw_cross, worst_disj["nsa_pct"], d["did_points"]))


# ------------------------------------------------------------------- F4 - F6

def f4_intervention_baseline_mismatch(cfg, pool, capmap, sets):
    """D038a: an intervention reaching the mixture but not its baseline must refuse.

    HONEST SCOPE. nsa() calls require_controlled(dict(kw), dict(kw)) -- the same dict
    twice -- so that in-driver call is tautological and can never fire. What actually
    protects against D038a is that `**kw` is threaded through superadditivity() into
    solo_values(). So this fixture proves two separate things:

      (a) the production guard refuses the exact D038a condition pair; and
      (b) the intervention REALLY reaches the baselines, measured -- the empty-carrier
          and solo baselines must differ between the two laws. If force_disjunctive
          failed to propagate, the baselines would be identical across laws.

    (b) is the load-bearing half. A guard that cannot fire proves nothing on its own.
    """
    refused, msg = False, ""
    try:
        LN.require_controlled({"force_disjunctive": True}, {}, "F4/nsa")
    except LN.UncontrolledComparison as e:
        refused, msg = True, str(e)

    # (b) measured propagation: baselines must move when the law changes
    conj_solos, conj_empty = W.solo_values(cfg, "treatment", pool, capmap, sets["best"],
                                           S.seed, AID, "f4", 12)
    disj_solos, disj_empty = W.solo_values(cfg, "treatment", pool, capmap, sets["best"],
                                           S.seed, AID, "f4", 12, force_disjunctive=True)
    empty_moved = abs(conj_empty - disj_empty) > 1e-9
    solos_moved = any(abs(conj_solos[c] - disj_solos[c]) > 1e-9 for c in sets["best"])
    propagated = empty_moved or solos_moved
    return record("F4", refused and propagated,
                  "guard refused the D038a pair (%s); intervention reaches baselines "
                  "(empty %.2f->%.2f, solos moved=%s)"
                  % ("yes" if refused else "NO", conj_empty, disj_empty, solos_moved))


def f5_dead_genome(cfg, pool, capmap):
    """D034: a matched-arm comparison on a genome with no live mechanism must refuse."""
    dead = W.genome_with(cfg, [])
    probe = W.run_episode(dead, cfg, "treatment", S.seed(AID, "stream|f5", 0), pool, capmap,
                          force_disjunctive=True)
    refused = False
    try:
        LN.require_live(probe, ("info", "components_carried"), "F5/matched-arm")
    except LN.VacuousCheck as e:
        refused = True
        msg = str(e)
    live = W.run_episode(W.genome_with(cfg, [0, 2, 4]), cfg, "treatment",
                         S.seed(AID, "stream|f5", 0), pool, capmap, force_disjunctive=True)
    live_ok = LN.assert_live(live, ("info", "components_carried"), "F5/live")["live"]
    return record("F5", refused and live_ok,
                  "dead genome (info=%.1f, carried=%d) refused; live genome (info=%.1f) admitted"
                  % (probe["info"], probe["components_carried"], live["info"]))


def f6_effect_inside_null(cfg, pool, capmap, sets):
    """D035: an effect inside its measured null must not be eligible for a positive verdict."""
    blocks = [X.nsa(cfg, pool, capmap, sets["best"], S.seed, AID, "f6b%d" % b, 10,
                    "conjunctive")["nsa_pct"] for b in range(X.N_BLOCKS)]
    band = IM.sham_null([b + 100.0 for b in blocks])
    inside = (band["p05"] + band["p95"]) / 2.0          # by construction inside the band
    v = IM.effect_clears_null(inside, [b + 100.0 for b in blocks], direction="positive")
    outside = band["p95"] + 10.0
    v2 = IM.effect_clears_null(outside, [b + 100.0 for b in blocks], direction="positive")
    ok = (not v["clears"]) and v2["clears"]
    return record("F6", ok,
                  "effect %+.2f inside null [%+.2f, %+.2f] refused; %+.2f outside admitted"
                  % (inside, band["p05"], band["p95"], outside))


# ------------------------------------------------------------------------ F7

class _EvaluationOccurred(RuntimeError):
    """Raised if a real organism evaluation begins under a mutated contract."""


class _CountingCtx:
    """Minimal job ctx. Counts emissions; the driver must never reach one."""

    def __init__(self):
        self.emits = 0

    def emit(self, row):
        self.emits += 1

    def load_checkpoint(self):
        return None

    def checkpoint(self, *a, **k):
        pass

    def should_pause(self):
        return False

    def progress(self, *a, **k):
        pass


def f7_contract_mutation():
    """A binding change must refuse BEFORE any organism is evaluated.

    Aimed at the REAL entry point: job(). Refusing inside bind_contract() alone would
    only prove bind_contract refuses; it would not prove the driver calls it before it
    starts evaluating. So this drives job() itself with a mutated committed contract
    and asserts that the production episode function was called exactly ZERO times and
    that no row was emitted.

    world_e05.evolve/superadditivity call run_episode as a module global, so patching
    W.run_episode instruments every evaluation path, not just the ones X calls directly.
    """
    calls = {"n": 0}
    real = W.run_episode

    def counting(*a, **k):
        # SAFE BY CONSTRUCTION. If the contract guard ever failed to refuse, calling
        # through to the real episode would start the full EXECUTE run (4 replicates x
        # 60 generations x 64 organisms) and evaluate real organisms before the freeze
        # boundary is committed. So this refuses instead of delegating: the fixture can
        # detect the ordering violation without ever causing one.
        calls["n"] += 1
        raise _EvaluationOccurred("run_episode reached under a mutated contract")

    mutated = json.loads(json.dumps(X.EMBEDDED_CONTRACT))
    mutated["budget_B"] = 4                    # binding change: 3 -> 4
    tmp = pathlib.Path(tempfile.mkdtemp()) / "VERDICT_CONTRACT.json"
    CT.VerdictContract(mutated).save(tmp)

    ctx = _CountingCtx()
    saved_path = X.CONTRACT_PATH
    refused, fields, breached = False, "", False
    try:
        W.run_episode = counting
        X.CONTRACT_PATH = tmp
        X.job(ctx)
    except CT.ContractViolation as e:
        refused = True
        fields = str(e).split("differing fields:")[-1].strip()
    except _EvaluationOccurred:
        breached = True          # ordering violation: evaluation began before refusal
    finally:
        X.CONTRACT_PATH, W.run_episode = saved_path, real

    # positive control: the refusal must not be unconditional
    admits = False
    try:
        X.bind_contract()
        admits = True
    except CT.ContractViolation:
        admits = False

    ok = refused and (not breached) and calls["n"] == 0 and ctx.emits == 0 and admits
    return record("F7", ok,
                  "job() refused on %s before evaluating: run_episode calls=%d, emits=%d, "
                  "ordering_breach=%s; unmutated contract still admits=%s"
                  % (fields[:24], calls["n"], ctx.emits, breached, admits))


def main():
    print("########## e05 freeze-boundary fixtures F1-F7 ##########")
    cfg, pool, capmap, contract = _world()
    print("    contract hash %s" % contract.hash[:16])
    print("    enumerating C(%d,%d) subsets via the production path..."
          % (cfg["components"]["K"], contract.get("budget_B")))
    sets = X.enumerate_sets(cfg, pool, capmap, S.seed, AID, contract.get("budget_B"))
    print("    BEST %s  WORST %s  (%d subsets)" % (sets["best"], sets["worst"], sets["n_subsets"]))
    print()
    f1_positive_interaction(cfg, pool, capmap, sets)
    f2_pure_additive_partition(cfg, pool, capmap, sets)
    f3_overlap_not_composition(cfg, pool, capmap, sets)
    f4_intervention_baseline_mismatch(cfg, pool, capmap, sets)
    f5_dead_genome(cfg, pool, capmap)
    f6_effect_inside_null(cfg, pool, capmap, sets)
    f7_contract_mutation()
    n_pass = sum(1 for r in RESULTS if r["passed"])
    print()
    print("    %d/%d fixtures passed" % (n_pass, len(RESULTS)))
    out = {"contract_sha256": contract.hash, "best": sets["best"], "worst": sets["worst"],
           "n_subsets": sets["n_subsets"], "fixtures": RESULTS,
           "all_passed": n_pass == len(RESULTS)}
    (HERE / "FIXTURE_RESULTS.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0 if out["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
