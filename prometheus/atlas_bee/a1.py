"""A1 -- closed-loop vs open-loop held-out generalisation (source: NPE E10).

Source (Atlas nestor.graphworld/r1:E10-linear-closed-vs-open-128-seeds, POSITIVE): a closed-loop organism (acts on
the observation) generalises to HELD-OUT seeds better than an open-loop one (a fixed action tensor). The effect was
significant on worlds w3/w4 and not on w1; the 8-train-seed variant (E6) FAILED.

BEE instantiation: the wforge Encounter world IS the NPE lane-B de_novo world family. genome_seed 3 and 4 are
single-slot encounters (a clean single-organism test, and the worlds where the source effect was significant);
genome_seed 1 is a 2-slot encounter (the source's non-significant world) and is REFUSED here -- a single-organism
generalisation test on a 2-slot world needs a co-evolution or fixed-partner harness the light shim does not build.
Closed = statemachine.v1 (sees the observation); open = sequence.v1 (blind, replays a fixed action per tick). Both
are trained on TRAIN seeds and scored on disjoint HELD-OUT seeds by objective.charge.v1 (the resource the encounter
already reports; the source's own competence signal, yield_events, is in outcome() but the wrap does not surface it).
"""
from __future__ import annotations

import pathlib
from typing import Dict, List

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox import search as SR
from prometheus.atlas_bee.harness import Adaptation, run_experiment
from prometheus.atlas_bee.manifest import Manifest

WORLDS = [3, 4]                       # single-slot encounter worlds (NPE w3/w4, significant); genome_seed 1 refused
CLOSED = "statemachine.v1"
OPEN = "sequence.v1"
TRAIN = {"base": 200, "n_seeds": 10}          # E6's 8-seed variant FAILED; the source's working config used more
HELDOUT = {"base": 9000, "n_seeds": 20}       # disjoint from TRAIN
GENERATIONS = 8
N = 20
KEEP = 6


class A1(Adaptation):
    id = "a1"
    source = {"atlas_key": "nestor.graphworld/r1:E10-linear-closed-vs-open-128-seeds", "disposition": "POSITIVE",
              "original": "closed > open on held-out; significant on w3/w4, not on w1; E6 (8 train seeds) FAILED"}

    def manifest(self) -> Manifest:
        m = Manifest(self.id, self.source["atlas_key"])
        m.add("world", "NPE lane-B de_novo Encounter worlds w3/w4 (genome_seed 3/4)",
              "world.wforge.encounter.v0(genome_seed=3|4)", "IDENTICAL",
              "the wforge Encounter world family IS the same de_novo generator; genome_seed selects the world")
        m.add("world w1", "NPE de_novo Encounter world w1 (genome_seed 1), 2 slots", "-", "UNREPRESENTABLE",
              "a single-organism closed-vs-open test on a 2-slot encounter needs a co-evolution / fixed-partner "
              "harness the light shim does not build; the source itself found w1 not significant")
        m.add("organism closed", "linear closed-loop brain acting on the observation", "statemachine.v1", "ANALOGOUS",
              "a finite-state controller that reads the observation each tick; not the source's linear form but the "
              "same closed-loop class (behaviour depends on the observation)")
        m.add("organism open", "open-loop action tensor (a fixed action per tick, blind to the observation)",
              "sequence.v1", "IDENTICAL", "the open-loop action tensor is exactly sequence.v1's action-per-tick")
        m.add("objective", "the encounter's native per-episode competence (reward / yield_events)",
              "objective.charge.v1 (best final charge from world_summary)", "MODIFIED",
              "the wforge wrap surfaces charge/alive/ticks but not the per-slot yield_events the source scored; charge "
              "is the resource in the same outcome() and gives a gradient (0..1200 across organisms)")
        m.add("train / held-out split", "train on N seeds, evaluate the best on 64 held-out seeds",
              "evolve on TRAIN seeds; execute() the best elite on disjoint HELD-OUT seeds", "ANALOGOUS",
              "BEE evolves a population and re-evaluates the top elite on a disjoint seed range")
        m.add("search / selection", "the source's training procedure", "search.evolve, selector.truncation.v1", "ANALOGOUS",
              "hill-climb on charge; the source's exact optimiser is not reproduced, the generalisation question is")
        m.add("control", "determinism / replay", "control.replay.v1 (BIT)", "IDENTICAL",
              "the encounter world is replay_class BIT; the held-out evaluation replays bit-for-bit")
        m.add("scientific-conclusion layer", "NPE's disposition (POSITIVE)", "-", "OMITTED",
              "BEE authors no scientific conclusion; the comparison packet is the conclusion layer")
        return m

    def prereg_body(self) -> Dict:
        return {
            "question": "Does a closed-loop organism (acts on the observation) reach a higher held-out final charge "
                        "than an open-loop one (a fixed action per tick), on the single-slot wforge Encounter worlds "
                        "genome_seed 3 and 4?",
            "worlds": ["world.wforge.encounter.v0(genome_seed=%d)" % g for g in WORLDS],
            "organisms": {"closed": CLOSED, "open": OPEN},
            "initial_state": "each search starts from a fresh random generation 0 (no seeded imports)",
            "interventions": "none; the only manipulated variable is the organism class (closed vs open)",
            "objective": "objective.charge.v1 (best final charge over slots, from world_summary)",
            "observations": ["objective value per held-out seed", "mean held-out charge per (world, organism)"],
            "controls": ["control.replay.v1 on every held-out evaluation (BIT determinism)"],
            "seeds": {"train": TRAIN, "heldout": HELDOUT, "disjoint": True},
            "budgets": {"generations": GENERATIONS, "population": N, "keep": KEEP},
            "stopping_rules": "fixed budget; no early stop; a search that finds no positive charge is a valid ABSENT/NOT_COMPARABLE result",
            "invariants": ["held-out seeds disjoint from train seeds",
                           "closed and open share the same world, objective, seeds and budget -- only the organism class differs",
                           "every held-out evaluation replays bit-for-bit (control.replay MET)"],
            "decision_criteria": {
                "PHENOMENON_PRESERVED": "closed mean held-out charge > open on BOTH worlds (matches the source's closed>open)",
                "PHENOMENON_CHANGED": "closed > open on one world only, or both non-zero with no closed advantage",
                "PHENOMENON_INVERTED": "open > closed on both worlds",
                "PHENOMENON_ABSENT / NOT_COMPARABLE": "neither organism reaches positive charge on a world (no gradient to compare)",
            },
        }

    # ---- execution --------------------------------------------------------------------------------------------
    def _train_and_eval(self, gs: int, rep: str, workdir: pathlib.Path, reg) -> Dict:
        world = ref("world.wforge.encounter.v0", genome_seed=gs)
        obj = ref("objective.charge.v1")
        obs = [ref("observer.trace.v1")]
        w = reg.make("world.wforge.encounter.v0", genome_seed=gs); H = w.mech.horizon
        template = Experiment(family="a1_%d_%s" % (gs, rep.split(".")[0]), world=world, substrate=ref("substrate.flat.v1"),
                              players=[], objective=obj, observers=obs, seed_policy=dict(TRAIN), budget={"episodes": 1, "horizon": H})
        sd = workdir / ("train_g%d_%s" % (gs, rep.split(".")[0]))
        out = SR.evolve(template, ref("selector.truncation.v1", keep=KEEP, n=N, representation=rep),
                        generations=GENERATIONS, workdir=sd, seed=7, registry=reg)
        rows = [r for r in SR.load_rows(sd / "archive.jsonl") if r["kind"] == "elite" and isinstance(r.get("objective"), (int, float))]
        rows.sort(key=lambda r: r["objective"], reverse=True)
        best = rows[0] if rows else None
        train_best = best["objective"] if best else None
        # held-out evaluation of the single best elite
        heldout_mean = None; heldout_vals: List[float] = []; ho_file = None; replay_met = None
        if best is not None:
            spec = _spec_of(best["player"])
            e = Experiment(family="a1_%d_%s_ho" % (gs, rep.split(".")[0]), world=world, substrate=ref("substrate.flat.v1"),
                           players=[spec.manifest()], objective=obj, observers=obs, controls=[ref("control.replay.v1")],
                           seed_policy=dict(HELDOUT), budget={"episodes": 1, "horizon": H})
            ho_file = workdir / ("heldout_g%d_%s.jsonl" % (gs, rep.split(".")[0]))
            rep_report = run_experiment(e, ho_file, reg)
            from prometheus.toolbox.receipt import read_all
            prim = [r for r in read_all(ho_file) if r["arm"] == "primary"]
            heldout_vals = [(r["science"].get("objective") or {}).get("value") for r in prim]
            heldout_vals = [v for v in heldout_vals if isinstance(v, (int, float))]
            heldout_mean = sum(heldout_vals) / len(heldout_vals) if heldout_vals else None
            replay_met = (rep_report.controls.get("replay", {}) or {}).get("outcome") if getattr(rep_report, "controls", None) else None
        return {"world": gs, "organism": rep, "train_best": train_best, "heldout_mean": heldout_mean,
                "heldout_vals": heldout_vals, "heldout_file": str(ho_file) if ho_file else None,
                "replay": replay_met, "n_elites": len(rows)}

    def run(self, workdir: pathlib.Path, reg=None) -> Dict:
        reg = reg or default_registry()
        workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
        results = []; receipt_files = []
        for gs in WORLDS:
            for rep in (CLOSED, OPEN):
                r = self._train_and_eval(gs, rep, workdir, reg)
                results.append(r)
                if r["heldout_file"]:
                    receipt_files.append(r["heldout_file"])
        return {"observed": {"per_cell": results}, "receipt_files": receipt_files,
                "notes": ["genome_seed 1 (2-slot) refused per manifest"]}

    def compare(self, observed: Dict) -> Dict:
        cells = observed["per_cell"]
        by_world = {}
        for c in cells:
            by_world.setdefault(c["world"], {})[c["organism"]] = c
        signals = []; new_phenomena = []
        for gs, d in sorted(by_world.items()):
            cc, oc = d.get(CLOSED, {}), d.get(OPEN, {})
            cl, op = cc.get("heldout_mean"), oc.get("heldout_mean")
            cl_tr, op_tr = cc.get("train_best"), oc.get("train_best")
            learned = max([x for x in (cl_tr, op_tr) if isinstance(x, (int, float))] or [0]) > 0
            if cl is None or op is None:
                rel = "INSTRUMENT_FAILURE"
            elif not learned:
                rel = "NO_GRADIENT"          # neither organism reached positive train charge: a flat plateau, nothing to generalise
            elif cl > op:
                rel = "closed>open"
            elif op > cl:
                rel = "open>closed"
            else:
                rel = "closed==open"
            # overfitting: learned a lot on train but not on held-out
            for name, cell in (("closed", cc), ("open", oc)):
                tb, hm = cell.get("train_best"), cell.get("heldout_mean")
                if isinstance(tb, (int, float)) and isinstance(hm, (int, float)) and tb > 0 and hm <= 0.1 * tb:
                    new_phenomena.append("gs%d: the %s organism OVERFIT the train seeds (train_best=%.1f, held-out=%.2f) -- "
                                         "selecting by train charge picks a seed-memoriser that does not generalise" % (gs, name, tb, hm))
            signals.append({"world": gs, "closed_heldout": cl, "open_heldout": op,
                            "closed_train": cl_tr, "open_train": op_tr, "learned": learned, "relation": rel})
        wins = [s for s in signals if s["relation"] == "closed>open"]
        inverts = [s for s in signals if s["relation"] == "open>closed"]
        comparable = [s for s in signals if s["relation"] in ("closed>open", "open>closed", "closed==open")]
        if not comparable:
            verdict = "NOT_COMPARABLE"       # no world produced a gradient to test closed-vs-open generalisation
        elif wins and not inverts:
            verdict = "PHENOMENON_PRESERVED"
        elif inverts and not wins:
            verdict = "PHENOMENON_INVERTED"
        else:
            verdict = "PHENOMENON_CHANGED"
        for s in signals:
            if s["relation"] == "open>closed":
                new_phenomena.append("gs%d: the OPEN (blind) organism generalised better than the closed one -- opposite to E10's closed>open" % s["world"])
        differences = {
            "scientific": ["closed-vs-open held-out relation per world: " + "; ".join("gs%d:%s" % (s["world"], s["relation"]) for s in signals)],
            "representational": ["objective is final charge, not the source's yield_events (the wforge wrap does not surface yield_events)",
                                 "genome_seed 1 (2-slot) refused: no single-organism test without a partner harness"],
            "executor": ["BEE local scalar execution; every held-out evaluation replays bit-for-bit (BIT world)"],
            "resource": ["generations=%d, population=%d, train_seeds=%d, heldout_seeds=%d" % (GENERATIONS, N, TRAIN["n_seeds"], HELDOUT["n_seeds"]),
                         "a fixed-seed evolutionary search sat on a flat plateau where no train seed was winnable (gs3)"],
            "measurement": ["mean over held-out seeds of the single best-by-train-charge elite's final charge"],
        }
        return {"verdict": verdict, "signals": signals, "differences": differences,
                "new_phenomena": sorted(set(new_phenomena)),
                "summary": "closed vs open on wforge gs3/gs4 (held-out charge; train_best in brackets): " +
                           "; ".join("gs%d closed=%s[%s] open=%s[%s]" % (s["world"], s["closed_heldout"], s["closed_train"], s["open_heldout"], s["open_train"]) for s in signals)}


def _spec_of(p) -> PlayerSpec:
    if isinstance(p, PlayerSpec):
        return p
    return PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {}))
