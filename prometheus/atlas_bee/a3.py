"""A3 -- retention under necessity (source: NPE cw01-e01).

Source (Atlas nestor.cw01/cw01-2026-09-17:cw01-e01, POSITIVE): retention is load-bearing -- erasing an organism's
retained state costs about -10.2% versus a cost-matched sham, and a "recurrence 0" control shows the benefit is due
to situations RECURRING (5/5).

BEE instantiation: organisms are evolved (under recurrence, with lifetime kv) to actually USE their retained state
-- A6 showed that random memory-users do not, so the question is only well-posed for organisms whose retention is
load-bearing. Then a 2x3 grid is run on the top elites:
  recurrence: RECUR (episode_seeds recur, distinct=k, situations repeat) vs NO_RECUR (all episode seeds distinct)
  arm:        off (retain) / erase (kv_weather erase) / sham (kv_weather sham, cost-matched)
The e01 prediction is erase < sham UNDER recurrence and erase ~= sham without it (the recurrence-0 control).
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

WORLD = dict(world_seed=8, start_charge=40, yield_amt=10, stoch_rate=0)
EPISODES = 6
DISTINCT = 2                     # recurrence: 2 world seeds cycle across 6 episodes
HORIZON = 24
N, GENERATIONS, KEEP = 20, 10, 6
TOPK = 3
RATE, WEATHER_SEED = 0.6, 5
TRAIN = {"base": 1, "n_seeds": 6}
TEST = {"base": 50, "n_seeds": 8}
ARMS = {"off": "off", "erase": "erase", "sham": "sham"}


def _spec_of(p) -> PlayerSpec:
    if isinstance(p, PlayerSpec):
        return p
    return PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {}))


class A3(Adaptation):
    id = "a3"
    source = {"atlas_key": "nestor.cw01/cw01-2026-09-17:cw01-e01", "disposition": "POSITIVE",
              "original": "retention load-bearing; erase costs -10.2% vs cost-matched sham; recurrence-0 control; 5/5"}

    def manifest(self) -> Manifest:
        m = Manifest(self.id, self.source["atlas_key"])
        m.add("retention substrate", "an organism's retained state across recurring situations",
              "substrate.kv.v1 / kv_weather.v1 scope=lifetime (workspace persists across episodes)", "ANALOGOUS",
              "lifetime kv persists across the episodes of a run; the organism carries state between recurrences")
        m.add("recurrence", "situations recur", "budget.episode_seeds={kind:recur,distinct:k} (the S4 scaffolding)",
              "IDENTICAL", "recurring episode seeds make the SAME world situations repeat within a run")
        m.add("recurrence-0 control", "situations do not recur", "episode_seeds distinct = n_episodes (all distinct)",
              "IDENTICAL", "every episode a fresh world seed: retention has nothing to recur against")
        m.add("erase / sham", "erasing retained state vs a cost-matched sham",
              "kv_weather erase vs sham (sham rewrites the same value, pays the write)", "IDENTICAL",
              "the sham fires as often and pays the write but loses no information")
        m.add("organism", "an organism whose retention is load-bearing", "statemachine.v2 EVOLVED under recurrence for charge",
              "MODIFIED", "A6 showed random memory-users do not benefit from memory; the question is only posed for "
              "organisms selected to use their retained state")
        m.add("objective / effect size", "performance, reported as a percent cost", "objective.charge.v1; effect = (erase-sham)/sham",
              "ANALOGOUS", "BEE measures the same erase-vs-cost-matched-sham gap, as a fraction of the sham charge")
        m.add("control", "determinism", "control.replay.v1 (BIT under seeded weather)", "IDENTICAL", "seeded weather replays bit-for-bit")
        m.add("scientific-conclusion layer", "e01's disposition (POSITIVE)", "-", "OMITTED", "BEE authors no conclusion")
        return m

    def prereg_body(self) -> Dict:
        return {
            "question": "Is retained state load-bearing (erase < cost-matched sham), and is that cost SPECIFIC to "
                        "recurring situations (present under RECUR, absent under NO_RECUR -- the recurrence-0 control)?",
            "world": "world.integer.v1(%s)" % WORLD,
            "organisms": "top-%d elites of a statemachine.v2 search evolved UNDER recurrence (distinct=%d) for charge" % (TOPK, DISTINCT),
            "initial_state": "empty workspace each run; lifetime state accrues across the run's episodes",
            "interventions": {"recurrence": {"RECUR": "episode_seeds distinct=%d" % DISTINCT, "NO_RECUR": "episode_seeds distinct=%d (all)" % EPISODES},
                              "arm": {k: "kv_weather mode=%s rate=%s weather_seed=%s" % (v, RATE, WEATHER_SEED) for k, v in ARMS.items()}},
            "objective": "objective.charge.v1",
            "observations": ["mean charge per (elite, recurrence, arm)", "erase-vs-sham cost per recurrence, as a percent of sham"],
            "controls": ["control.replay.v1 on every cell", "sham as the cost-matched control for erase",
                         "NO_RECUR as the recurrence-0 control"],
            "seeds": {"train": TRAIN, "test": TEST}, "budgets": {"episodes": EPISODES, "horizon": HORIZON, "search": {"n": N, "generations": GENERATIONS}},
            "stopping_rules": "fixed budget; erase>=sham everywhere is a valid ABSENT result",
            "decision_criteria": {
                "PHENOMENON_PRESERVED": "erase < sham under RECUR and erase ~= sham under NO_RECUR (retention cost is recurrence-specific, as e01)",
                "PHENOMENON_CHANGED": "erase < sham but the recurrence-specificity differs (e.g. the cost is present or larger without recurrence)",
                "PHENOMENON_ABSENT": "erase ~= sham in both (retention not load-bearing for these organisms)",
            },
        }

    # ---- execution --------------------------------------------------------------------------------------------
    def _evolve_elites(self, workdir: pathlib.Path, reg) -> List[PlayerSpec]:
        t = Experiment(family="a3_ev", world=ref("world.integer.v1", **WORLD), substrate=ref("substrate.kv.v1", scope="lifetime"),
                       players=[], objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                       seed_policy=dict(TRAIN), budget={"episodes": EPISODES, "horizon": HORIZON, "episode_seeds": {"kind": "recur", "distinct": DISTINCT}})
        sd = workdir / "evolve"
        SR.evolve(t, ref("selector.truncation.v1", keep=KEEP, n=N, representation="statemachine.v2"),
                  generations=GENERATIONS, workdir=sd, seed=7, registry=reg)
        rows = [r for r in SR.load_rows(sd / "archive.jsonl") if r["kind"] == "elite" and isinstance(r.get("objective"), (int, float))]
        rows.sort(key=lambda r: r["objective"], reverse=True)
        return [(_spec_of(r["player"]), r["objective"]) for r in rows[:TOPK]]

    def _cell(self, spec: PlayerSpec, mode: str, distinct: int, tag: str, workdir: pathlib.Path, reg) -> Dict:
        e = Experiment(family="a3_%s" % tag, world=ref("world.integer.v1", **WORLD),
                       substrate=ref("substrate.kv_weather.v1", scope="lifetime", rate=RATE, mode=mode, weather_seed=WEATHER_SEED),
                       players=[spec.manifest()], objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                       controls=[ref("control.replay.v1")], seed_policy=dict(TEST),
                       budget={"episodes": EPISODES, "horizon": HORIZON, "episode_seeds": {"kind": "recur", "distinct": distinct}})
        f = workdir / ("%s.jsonl" % tag)
        rep = execute(lower(e, reg).job, f, reg)
        prim = [r for r in read_all(f) if r["arm"] == "primary"]
        objs = [(r["science"].get("objective") or {}).get("value") for r in prim]
        objs = [o for o in objs if isinstance(o, (int, float))]
        return {"mean": statistics.mean(objs) if objs else None, "file": str(f),
                "replay": (rep.controls.get("replay", {}) or {}).get("outcome") if getattr(rep, "controls", None) else None}

    def run(self, workdir: pathlib.Path, reg=None) -> Dict:
        reg = reg or default_registry()
        workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
        elites = self._evolve_elites(workdir, reg)
        cells = []; receipt_files = []
        conditions = {"RECUR": DISTINCT, "NO_RECUR": EPISODES}
        for i, (spec, train_obj) in enumerate(elites):
            for cond, dist in conditions.items():
                for arm, mode in ARMS.items():
                    tag = "e%d_%s_%s" % (i, cond, arm)
                    c = self._cell(spec, mode, dist, tag, workdir, reg)
                    cells.append({"elite": i, "train_obj": train_obj, "recurrence": cond, "arm": arm, **c})
                    receipt_files.append(c["file"])
        return {"observed": {"cells": cells, "n_elites": len(elites)}, "receipt_files": receipt_files,
                "notes": ["organisms EVOLVED under recurrence to make retention load-bearing (per manifest MODIFIED)"]}

    def compare(self, observed: Dict) -> Dict:
        cells = observed["cells"]
        def mean_arm(cond, arm):
            vs = [c["mean"] for c in cells if c["recurrence"] == cond and c["arm"] == arm and isinstance(c["mean"], (int, float))]
            return statistics.mean(vs) if vs else None
        table = {cond: {arm: mean_arm(cond, arm) for arm in ARMS} for cond in ("RECUR", "NO_RECUR")}
        def cost(cond):
            er, sh = table[cond]["erase"], table[cond]["sham"]
            if er is None or sh is None or sh == 0:
                return None
            return (er - sh) / abs(sh)      # negative = erase costs vs the cost-matched sham
        recur_cost, norecur_cost = cost("RECUR"), cost("NO_RECUR")
        replays = [c["replay"] for c in cells]
        load_bearing = lambda c: c is not None and c < -0.02       # erase at least 2% below sham
        signals = {"RECUR_erase_vs_sham": recur_cost, "NO_RECUR_erase_vs_sham": norecur_cost,
                   "table": table, "all_replay_MET": all(r == "MET" for r in replays)}
        new_phenomena = []
        if not load_bearing(recur_cost) and not load_bearing(norecur_cost):
            verdict = "PHENOMENON_ABSENT"
            headline = "erase ~= sham in both conditions: retention not load-bearing for these organisms"
        elif load_bearing(recur_cost) and not load_bearing(norecur_cost):
            verdict = "PHENOMENON_PRESERVED"
            headline = "erase costs vs sham under RECUR (%.1f%%) but not NO_RECUR: recurrence-specific retention, as e01" % (100 * recur_cost)
        else:
            verdict = "PHENOMENON_CHANGED"
            headline = "retention is load-bearing (erase < sham) but the recurrence-0 control does NOT hold: cost under RECUR=%s NO_RECUR=%s" % (
                None if recur_cost is None else "%.1f%%" % (100 * recur_cost), None if norecur_cost is None else "%.1f%%" % (100 * norecur_cost))
            if load_bearing(norecur_cost) and (recur_cost is None or norecur_cost < recur_cost):
                new_phenomena.append("retention costs MORE without recurrence than with it -- the opposite of e01's recurrence-necessity: "
                                     "in BEE retained state buys resilience to situational DIVERSITY, not to recurrence")
        differences = {
            "scientific": [headline],
            "representational": ["retention = lifetime kv workspace persisting across a run's episodes",
                                 "organisms had to be EVOLVED to use retention (random memory-users do not -- see A6)"],
            "executor": ["BEE local scalar execution; every cell replays bit-for-bit (seeded weather)"],
            "resource": ["top-%d evolved elites; %d test seeds; %d episodes x %d ticks; distinct=%d (recur) vs %d (no-recur)" % (
                TOPK, TEST["n_seeds"], EPISODES, HORIZON, DISTINCT, EPISODES)],
            "measurement": ["erase-vs-sham gap as a fraction of the cost-matched sham charge, meaned over elites"],
        }
        return {"verdict": verdict, "signals": signals, "differences": differences, "new_phenomena": new_phenomena,
                "summary": headline + " | replay MET=%s" % signals["all_replay_MET"]}
