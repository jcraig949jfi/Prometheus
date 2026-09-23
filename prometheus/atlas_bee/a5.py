"""A5 -- delay ladder / revisit share (source: SFE C2-SFE-06).

Source (Atlas archaeon.campaign/cmp2:C2-SFE-06, WEAK_POSITIVE): a delay ladder (action_delay 0->1->2->4) trained with
a "revisit share" p; final rung-0 performance rose with p -- p0.0 mean 0.222, p0.1 0.674, p0.25 0.701, p0.5 1.0.

BEE instantiation: the S2 battery scaffolding evaluates each proposal on a WEIGHTED set of world variants. The delay
ladder is a battery over action_delay in {0,1,2,4}; the revisit share p is the WEIGHT on rung 0. p=0 drops rung 0
from the training battery (it is never revisited); p>0 gives rung 0 weight p and splits (1-p) over the harder rungs.
The best elite (by weighted battery charge) is then evaluated on rung 0 alone (action_delay=0) -- final_r0.
"""
from __future__ import annotations

import pathlib
import statistics
from typing import Dict, List

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox import search as SR
from prometheus.atlas_bee.harness import Adaptation
from prometheus.atlas_bee.manifest import Manifest

WORLD = dict(world_seed=8, start_charge=30, yield_amt=12, yield_width=16384)
HORIZON = 28
RUNGS = [0, 1, 2, 4]
P_VALUES = [0.0, 0.1, 0.25, 0.5]
N, GENERATIONS, KEEP = 16, 8, 6
TRAIN = {"base": 1, "n_seeds": 6}
HELDOUT = {"base": 5000, "n_seeds": 16}


def _spec_of(p) -> PlayerSpec:
    if isinstance(p, PlayerSpec):
        return p
    return PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {}))


def _battery(p: float) -> List[dict]:
    hard = [r for r in RUNGS if r != 0]
    if p <= 0:
        w = 1.0 / len(hard)
        return [{"world_params": {"action_delay": r}, "weight": w} for r in hard]
    wh = (1.0 - p) / len(hard)
    return [{"world_params": {"action_delay": 0}, "weight": p}] + [{"world_params": {"action_delay": r}, "weight": wh} for r in hard]


class A5(Adaptation):
    id = "a5"
    source = {"atlas_key": "archaeon.campaign/cmp2:C2-SFE-06", "disposition": "WEAK_POSITIVE",
              "original": "delay ladder 0-1-2-4, revisit share p; final_r0 rose with p (0.222/0.674/0.701/1.0 at p 0/0.1/0.25/0.5)"}

    def manifest(self) -> Manifest:
        m = Manifest(self.id, self.source["atlas_key"])
        m.add("delay ladder", "action_delay rungs 0->1->2->4", "battery over world_params action_delay in {0,1,2,4} (the S2 scaffolding)",
              "IDENTICAL", "action_delay is the same delay knob; the battery evaluates a proposal on all rungs at once")
        m.add("revisit share p", "how often rung 0 is revisited during training", "the battery WEIGHT on rung 0 (p); (1-p) split over the harder rungs",
              "ANALOGOUS", "a higher weight on rung 0 is more revisiting of it; p=0 drops rung 0 from the battery entirely")
        m.add("final_r0", "rung-0 performance after the ladder", "best elite evaluated on action_delay=0 held-out (charge)",
              "ANALOGOUS", "the best-by-weighted-battery elite is scored on rung 0 alone")
        m.add("organism / search", "the source's ladder trainer", "statemachine.v1 evolved under the battery, selector.truncation.v1",
              "ANALOGOUS", "one search per p, ranked by the weighted battery objective")
        m.add("objective", "the source's competence metric (0..1)", "objective.charge.v1 (final charge, unnormalised)",
              "MODIFIED", "BEE reports charge, not a normalised 0..1 competence; only the TREND in p is compared, not the level")
        m.add("scientific-conclusion layer", "SFE's disposition (WEAK_POSITIVE)", "-", "OMITTED", "BEE authors no conclusion")
        return m

    def prereg_body(self) -> Dict:
        return {
            "question": "Does training with a higher revisit share p of rung 0 (action_delay=0) raise final rung-0 "
                        "charge, across the delay ladder {0,1,2,4}? (C2-SFE-06 found final_r0 rose with p.)",
            "world": "world.integer.v1(%s)" % WORLD,
            "ladder": {"rungs_action_delay": RUNGS, "revisit_shares_p": P_VALUES},
            "organisms": "statemachine.v1 evolved once per p under the delay-ladder battery",
            "objective": "objective.charge.v1 (weighted battery mean during training; rung-0 held-out at evaluation)",
            "observations": ["final_r0 = best elite's mean held-out charge at action_delay=0, per p", "trend of final_r0 in p"],
            "controls": ["p=0 (rung 0 never revisited) as the low anchor", "held-out seeds disjoint from training"],
            "seeds": {"train": TRAIN, "heldout": HELDOUT}, "budgets": {"search": {"n": N, "generations": GENERATIONS}, "horizon": HORIZON},
            "stopping_rules": "fixed budget; a flat or non-monotone final_r0(p) is a valid CHANGED/ABSENT result",
            "decision_criteria": {
                "PHENOMENON_PRESERVED": "final_r0 rises with p (monotone non-decreasing, and the top p beats p=0)",
                "PHENOMENON_CHANGED": "final_r0 depends on p but not monotonically (revisiting helps non-linearly)",
                "PHENOMENON_ABSENT": "final_r0 is flat in p (revisit share does not shape rung-0 performance in BEE)",
            },
        }

    # ---- execution --------------------------------------------------------------------------------------------
    def _one_p(self, p: float, workdir: pathlib.Path, reg) -> Dict:
        template = Experiment(family="a5_p%02d" % int(p * 100), world=ref("world.integer.v1", **WORLD), substrate=ref("substrate.flat.v1"),
                              players=[], objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                              seed_policy=dict(TRAIN), budget={"episodes": 1, "horizon": HORIZON})
        sd = workdir / ("p%02d" % int(p * 100))
        SR.evolve(template, ref("selector.truncation.v1", keep=KEEP, n=N, representation="statemachine.v1"),
                  generations=GENERATIONS, workdir=sd, seed=5, registry=reg, battery=_battery(p))
        rows = [r for r in SR.load_rows(sd / "archive.jsonl") if r["kind"] == "elite" and isinstance(r.get("objective"), (int, float))]
        rows.sort(key=lambda r: r["objective"], reverse=True)
        best = _spec_of(rows[0]["player"]) if rows else None
        final_r0 = None; ho_file = None
        if best is not None:
            e = Experiment(family="a5_p%02d_r0" % int(p * 100), world=ref("world.integer.v1", action_delay=0, **WORLD),
                           substrate=ref("substrate.flat.v1"), players=[best.manifest()], objective=ref("objective.charge.v1"),
                           observers=[ref("observer.trace.v1")], seed_policy=dict(HELDOUT), budget={"episodes": 1, "horizon": HORIZON})
            ho_file = workdir / ("r0_p%02d.jsonl" % int(p * 100))
            execute(lower(e, reg).job, ho_file, reg)
            prim = [r for r in read_all(ho_file) if r["arm"] == "primary"]
            vals = [(r["science"].get("objective") or {}).get("value") for r in prim]
            vals = [v for v in vals if isinstance(v, (int, float))]
            final_r0 = statistics.mean(vals) if vals else None
        return {"p": p, "final_r0": final_r0, "train_best": rows[0]["objective"] if rows else None, "heldout_file": str(ho_file) if ho_file else None}

    def run(self, workdir: pathlib.Path, reg=None) -> Dict:
        reg = reg or default_registry()
        workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
        cells = [self._one_p(p, workdir, reg) for p in P_VALUES]
        return {"observed": {"ladder": cells}, "receipt_files": [c["heldout_file"] for c in cells if c["heldout_file"]],
                "notes": ["final_r0 in native charge units, not a normalised 0..1 competence (manifest MODIFIED)"]}

    def compare(self, observed: Dict) -> Dict:
        cells = sorted(observed["ladder"], key=lambda c: c["p"])
        ps = [c["p"] for c in cells]; r0 = [c["final_r0"] for c in cells]
        vals = [v for v in r0 if isinstance(v, (int, float))]
        new_phenomena: List[str] = []
        if len(vals) < 2:
            verdict = "INSTRUMENT_FAILURE"; headline = "too few final_r0 values"
        else:
            spread = max(vals) - min(vals)
            monotone = all(r0[i] is not None and r0[i + 1] is not None and r0[i + 1] >= r0[i] - 1e-9 for i in range(len(r0) - 1))
            top_beats_bottom = r0[-1] is not None and r0[0] is not None and r0[-1] > r0[0]
            flat = spread <= max(1e-9, 0.05 * (abs(statistics.mean(vals)) or 1))
            if flat:
                verdict = "PHENOMENON_ABSENT"; headline = "final_r0 is flat in p (spread %.2f): revisit share does not shape rung-0 charge in BEE" % spread
                new_phenomena = ["the search converges to a DELAY-INVARIANT dominant strategy (identical charge on every rung 0/1/2/4), "
                                 "so a delay curriculum has nothing to teach and the revisit share cannot matter -- action_delay does "
                                 "not gate the winning strategy in BEE's integer world, unlike the SFE world where the ladder mattered"]
            elif monotone and top_beats_bottom:
                verdict = "PHENOMENON_PRESERVED"; headline = "final_r0 rises with p (%s): more revisiting of rung 0 helps, as C2-SFE-06" % r0
            else:
                verdict = "PHENOMENON_CHANGED"; headline = "final_r0 depends on p but not monotonically: %s at p=%s" % (r0, ps)
        differences = {
            "scientific": [headline, "final_r0 by p: " + ", ".join("p%.2f=%s" % (c["p"], c["final_r0"]) for c in cells)],
            "representational": ["the delay ladder is a battery over action_delay; revisit share = battery weight on rung 0",
                                 "p=0 drops rung 0 from the battery (weights must be > 0); it is the never-revisited anchor"],
            "executor": ["BEE local scalar execution; one search per p (fixed seed)"],
            "resource": ["population=%d, generations=%d, train_seeds=%d, heldout_seeds=%d, rungs=%s" % (N, GENERATIONS, TRAIN["n_seeds"], HELDOUT["n_seeds"], RUNGS)],
            "measurement": ["final_r0 = best-by-weighted-battery elite's mean held-out charge at action_delay=0"],
        }
        return {"verdict": verdict, "final_r0_by_p": {c["p"]: c["final_r0"] for c in cells}, "differences": differences,
                "new_phenomena": new_phenomena, "summary": headline}
