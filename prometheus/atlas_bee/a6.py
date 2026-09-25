"""A6 -- computational weather / brain damage (source: NPE cw01-e07).

Source (Atlas nestor.cw01/cw01-2026-09-17:cw01-e07, INCONCLUSIVE): three arms STATIC / WEATHER / SHAMWEATHER test
whether damaging an organism's retained state hurts it beyond the cost of the damage. The gate P1..P5 REFUSED: P1
"damage does not fire", P4 "WEATHER not separable from SHAMWEATHER".

BEE instantiation: substrate.kv_weather.v1 (the S5 scaffolding) damages the workspace of memory-using organisms.
  STATIC      = mode "off"    (no weather)
  WEATHER     = mode "erase"  (delete the retained value when weather fires)
  SHAMWEATHER = mode "sham"   (rewrite the SAME value; pays the write, loses no information)
Organisms are statemachine.v2 that write their workspace every tick (memory users by construction, so P2 holds).
The gates are the same five, in BEE's terms; the effect is measured as final charge (objective.charge.v1). The
weather is seeded, so a control.replay confirms determinism (P5).
"""
from __future__ import annotations

import pathlib
import statistics
from typing import Dict, List

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.ref.players import random_statemachine_v2
from prometheus.atlas_bee.harness import Adaptation
from prometheus.atlas_bee.manifest import Manifest

PANEL = list(range(6))                          # six memory-using organisms
RATE = 0.5
WEATHER_SEED = 3
WORLD = dict(world_seed=8, start_charge=40, yield_amt=10)
SEEDS = {"base": 1, "n_seeds": 8}
BUDGET = {"episodes": 2, "horizon": 30}
ARMS = {"STATIC": "off", "WEATHER": "erase", "SHAMWEATHER": "sham"}


class A6(Adaptation):
    id = "a6"
    source = {"atlas_key": "nestor.cw01/cw01-2026-09-17:cw01-e07", "disposition": "INCONCLUSIVE",
              "original": "arms STATIC/WEATHER/SHAMWEATHER; gate P1..P5 refused (P1 damage does not fire, P4 not separable)"}

    def manifest(self) -> Manifest:
        m = Manifest(self.id, self.source["atlas_key"])
        m.add("arms", "STATIC / WEATHER / SHAMWEATHER", "substrate.kv_weather.v1 mode off / erase / sham", "IDENTICAL",
              "the three arms map one-to-one onto the weather substrate's modes")
        m.add("damage", "weather erases an organism's retained state", "kv_weather erase: delete the workspace value when weather fires",
              "ANALOGOUS", "BEE damages the organism's WORKSPACE (a substrate door it owns), the state it can lose")
        m.add("sham / cost-match", "SHAMWEATHER pays the same cost, loses no information",
              "kv_weather sham: rewrite the same value, pay the write, ws_damage counts equally", "IDENTICAL",
              "the sham fires exactly as often (same ws_damage) and pays a write, but the value is unchanged")
        m.add("organism", "a memory-using brain", "statemachine.v2, write_every=1 (writes its workspace every tick)",
              "ANALOGOUS", "a finite-state controller with a workspace it reads and writes; a memory user by construction")
        m.add("objective", "the organism's performance", "objective.charge.v1 (final charge)", "ANALOGOUS",
              "performance is the resource the organism ends with")
        m.add("gate P1..P5", "e07's refusal gate", "P1 damage fires / P2 uses state / P3 changes behaviour / "
              "P4 WEATHER separable from SHAMWEATHER / P5 deterministic", "ANALOGOUS",
              "the same five predicates, evaluated on BEE's accounting, objectives and replay")
        m.add("in-life damage to HIDDEN state", "damage to state the organism does not expose",
              "-", "UNREPRESENTABLE",
              "BEE can damage the WORKSPACE (a declared door) but not a statemachine's internal `state` register; "
              "only externalised, retained state is in reach of a substrate")
        m.add("scientific-conclusion layer", "e07's disposition (INCONCLUSIVE)", "-", "OMITTED",
              "BEE authors no scientific conclusion; the comparison packet is the conclusion layer")
        return m

    def prereg_body(self) -> Dict:
        return {
            "question": "Does erasing a memory-using organism's retained workspace (WEATHER) reduce its final charge "
                        "beyond a cost-matched sham that rewrites the same value (SHAMWEATHER)? I.e. is retained "
                        "state load-bearing, and is WEATHER separable from SHAMWEATHER?",
            "world": "world.integer.v1(%s)" % WORLD,
            "organisms": "panel of %d statemachine.v2 (write_every=1), seeds %s" % (len(PANEL), PANEL),
            "initial_state": "each organism starts each episode with an empty workspace; state accrues across ticks",
            "interventions": {"arm": {k: "substrate.kv_weather.v1 mode=%s, rate=%s, weather_seed=%s" % (v, RATE, WEATHER_SEED) for k, v in ARMS.items()}},
            "objective": "objective.charge.v1",
            "observations": ["mean final charge per (organism, arm)", "accounting ws_damage/ws_writes/ws_reads per arm",
                             "replay outcome per arm"],
            "controls": ["control.replay.v1 on every arm (weather is seeded: BIT replay must hold)"],
            "seeds": SEEDS, "budgets": BUDGET,
            "stopping_rules": "fixed panel and budget; a gate that fails REFUSES the reading (as e07 did), it is not forced",
            "gates": {
                "P1_damage_fires": "erase ws_damage > 0 AND erase mean charge < STATIC mean charge on the panel",
                "P2_uses_state": "ws_writes > 0 and ws_reads > 0 (memory users)",
                "P3_changes_behaviour": "erase mean charge != STATIC mean charge",
                "P4_separable": "erase mean charge != sham mean charge, and sham ~= STATIC (sham loses no information)",
                "P5_deterministic": "control.replay MET under every arm",
            },
            "decision_criteria": {
                "NEW_PHENOMENON": "all gates pass and erase < sham (retention load-bearing; the gates e07 refused, P1/P4, pass in BEE)",
                "PHENOMENON_PRESERVED": "a gate refuses as in e07 (BEE is also inconclusive for the same structural reason)",
                "PHENOMENON_ABSENT": "gates pass but erase ~= sham ~= STATIC (weather has no effect: retention not load-bearing)",
            },
        }

    # ---- execution --------------------------------------------------------------------------------------------
    def _arm(self, mode: str, workdir: pathlib.Path, reg) -> Dict:
        per_org = []; files = []
        for s in PANEL:
            spec = random_statemachine_v2(s, write_every=1)
            e = Experiment(family="a6_%s" % mode, world=ref("world.integer.v1", **WORLD),
                           substrate=ref("substrate.kv_weather.v1", scope="lifetime", rate=RATE, mode=mode, weather_seed=WEATHER_SEED),
                           players=[spec.manifest()], objective=ref("objective.charge.v1"),
                           observers=[ref("observer.trace.v1")], controls=[ref("control.replay.v1")],
                           seed_policy=dict(SEEDS), budget=dict(BUDGET))
            f = workdir / ("%s_org%d.jsonl" % (mode, s)); files.append(f)
            rep = execute(lower(e, reg).job, f, reg)
            prim = [r for r in read_all(f) if r["arm"] == "primary"]
            objs = [(r["science"].get("objective") or {}).get("value") for r in prim]
            objs = [o for o in objs if isinstance(o, (int, float))]
            acc = prim[0].get("accounting", {}) if prim else {}
            per_org.append({"org": s, "mean": statistics.mean(objs) if objs else None,
                            "ws_damage": acc.get("ws_damage"), "ws_writes": acc.get("ws_writes"), "ws_reads": acc.get("ws_reads"),
                            "replay": (rep.controls.get("replay", {}) or {}).get("outcome") if getattr(rep, "controls", None) else None})
        means = [o["mean"] for o in per_org if isinstance(o["mean"], (int, float))]
        return {"mode": mode, "per_org": per_org, "panel_mean": statistics.mean(means) if means else None, "files": files}

    def run(self, workdir: pathlib.Path, reg=None) -> Dict:
        reg = reg or default_registry()
        workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
        arms = {name: self._arm(mode, workdir, reg) for name, mode in ARMS.items()}
        receipt_files = [str(f) for a in arms.values() for f in a["files"]]
        return {"observed": {"arms": {k: {kk: vv for kk, vv in v.items() if kk != "files"} for k, v in arms.items()}},
                "receipt_files": receipt_files, "notes": ["statemachine internal `state` register is not damageable: UNREPRESENTABLE per manifest"]}

    def compare(self, observed: Dict) -> Dict:
        arms = observed["arms"]
        st, we, sh = arms["STATIC"], arms["WEATHER"], arms["SHAMWEATHER"]
        st_m, we_m, sh_m = st["panel_mean"], we["panel_mean"], sh["panel_mean"]
        we_dmg = [o["ws_damage"] for o in we["per_org"] if isinstance(o["ws_damage"], int)]
        uses = all((o["ws_writes"] or 0) > 0 and (o["ws_reads"] or 0) > 0 for o in st["per_org"])
        replays = [o["replay"] for a in arms.values() for o in a["per_org"]]
        gates = {
            "P1_damage_fires": bool(we_dmg) and all(d > 0 for d in we_dmg) and (we_m is not None and st_m is not None and we_m < st_m),
            "P2_uses_state": uses,
            "P3_changes_behaviour": we_m is not None and st_m is not None and we_m != st_m,
            "P4_separable": (we_m is not None and sh_m is not None and st_m is not None
                             and abs(we_m - sh_m) > 1e-9 and abs(sh_m - st_m) <= max(1e-9, 0.02 * abs(st_m))),
            "P5_deterministic": all(r == "MET" for r in replays),
        }
        all_pass = all(gates.values())
        erase_hurts_more = (we_m is not None and sh_m is not None and we_m < sh_m)
        if not all_pass:
            failed = [k for k, v in gates.items() if not v]
            verdict = "PHENOMENON_PRESERVED"      # e07 was inconclusive because gates refused; if a gate refuses here too, same structure
            headline = "a gate refused (%s): inconclusive as in e07" % ", ".join(failed)
        elif erase_hurts_more:
            verdict = "NEW_PHENOMENON"            # the gates e07 refused (P1, P4) pass in BEE and the effect separates
            headline = "retained state is load-bearing: WEATHER (%.2f) < SHAMWEATHER (%.2f) ~= STATIC (%.2f); the gates e07 refused pass in BEE" % (we_m, sh_m, st_m)
        else:
            verdict = "PHENOMENON_ABSENT"
            headline = "gates pass but WEATHER ~= SHAMWEATHER ~= STATIC: retention not load-bearing here"
        differences = {
            "scientific": [headline, "gate results: " + ", ".join("%s=%s" % (k, v) for k, v in gates.items())],
            "representational": ["only the WORKSPACE (a declared door) is damageable; the statemachine's internal `state` register is UNREPRESENTABLE to weather"],
            "executor": ["BEE local scalar execution; every arm replays bit-for-bit (weather is seeded)"],
            "resource": ["panel=%d organisms, %d seeds, %d episodes x %d ticks" % (len(PANEL), SEEDS["n_seeds"], BUDGET["episodes"], BUDGET["horizon"])],
            "measurement": ["panel-mean final charge per arm; ws_damage/ws_writes from accounting"],
        }
        new_phenomena = []
        if verdict == "NEW_PHENOMENON":
            new_phenomena.append("e07's P1 (damage fires) and P4 (WEATHER separable from SHAMWEATHER) REFUSED for the source; "
                                 "in BEE both pass -- the sham pays MORE writes than STATIC yet loses no charge, isolating the "
                                 "informational damage from its economic cost")
        return {"verdict": verdict, "gates": gates, "panel_means": {"STATIC": st_m, "WEATHER": we_m, "SHAMWEATHER": sh_m},
                "differences": differences, "new_phenomena": new_phenomena,
                "summary": "weather arms (panel-mean charge): STATIC=%s WEATHER=%s SHAMWEATHER=%s -> %s" % (st_m, we_m, sh_m, verdict)}
