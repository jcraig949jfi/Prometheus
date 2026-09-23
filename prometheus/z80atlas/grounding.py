"""The bounded GROUNDING ROUND (Bellerophon, 2026-09-23 directive Phases 6-8). Not a discovery campaign.

A FIXED, preregistered run plan (no promotion, no adaptive allocation): every lane, cell, arm, seed and override is
generated deterministically by plan() and hashed; roles/Bellerophon/forensics_2026-09-23/GROUNDING_PREREG.md freezes
that hash before the first run. Physics v2 throughout unless a cell declares otherwise (the P1 v1-vs-v2 contrast).

    python -m prometheus.z80atlas.grounding --plan-only --inputs <grounding_inputs.json>            # print hash + counts
    python -m prometheus.z80atlas.grounding --workdir <dir> --inputs <...> --hours 12 --workers 10   # execute
    python -m prometheus.z80atlas.grounding --workdir <dir> --status

STOPPING RULE (frozen): the round stops when every planned run has a result line, OR when the wall clock since the
first start reaches --hours (12 h in the prereg), whichever comes first. Runs are submitted in PRIORITY order (lane
priority, then plan order); a run not completed at the cap is reported NOT_RUN, never dropped silently. A restart
re-executes only runs with no result line (each run is a pure function of its spec, so a re-executed run is
byte-identical); the cap is measured from the FIRST start recorded in STATUS.json."""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import pathlib
import shutil
import time
from typing import Dict, List, Optional

SEED_BASE = 9_000_000_000_000          # campaign seeds lie in [1.6e11, 2.2e12]: disjoint
TICKS, CELLS, BUDGET = 500, 256, 256
BASE = dict(world="GRID", representation="Z80_64", layout="SHARED", reproduction="ENDOGENOUS_COPY", pressure="IMPLICIT",
            spatial="LOCAL", task="INC", scoring="ATOMIC", read_gate="ABR", env_dynamics="FIXED", mutation="BYTE",
            mutation_rate="MED", recombination="NONE", init="RANDOM")
V2 = {"physics": "v2"}
TOPOLOGIES = [("GRID", "LOCAL"), ("GRID", "WELL_MIXED"), ("SOUP", "WELL_MIXED"), ("GRAPH", "LOCAL"),
              ("NICHES", "NICHES_ISOLATED"), ("NICHES", "NICHES_LOW_MIG"), ("NICHES", "NICHES_HIGH_MIG"), ("NICHES", "NICHES_PERIODIC"),
              ("NICHES", "NICHES_COMPETENCE_MIG"), ("NICHES", "NICHES_POLLINATION"), ("NICHES", "NICHES_ENV_MIG"), ("NICHES", "RESERVOIR")]
LANE_PRIORITY = {"G8": 0, "G7P1": 1, "G1": 2, "G3": 3, "G5": 4, "P8": 5, "HIST": 6, "G1T": 7, "G7": 8}


def _nop_copy_ops(tape_hex: str) -> str:
    """the 'intentionally ablated specimen': every LDI/LDIR/COPYALL byte replaced by NOP (0x00)."""
    b = bytearray(bytes.fromhex(tape_hex))
    return bytes(0 if x in (0x14, 0x15, 0x16) else x for x in b).hex()


def plan(inputs: Optional[Dict] = None) -> List[Dict]:
    inputs = inputs or {}
    P: List[Dict] = []
    lane_no = {}

    def add(lane, cell, k, vec, over=None, arm=None, pair=None, init_tapes=(), n_seed=None):
        ln = lane_no.setdefault(lane, len(lane_no))
        seed = SEED_BASE + ln * 10 ** 9 + (n_seed if n_seed is not None else k)
        P.append({"lane": lane, "cell": cell, "arm": arm, "pair": pair, "k": k, "vec": dict(BASE, **vec),
                  "config_overrides": dict(V2, **(over or {})), "init_tapes": list(init_tapes), "seed": seed})

    # G8 instrument integrity: positive / negative / cheat controls (20 each)
    for k in range(20):
        add("G8", "pos_seeded_replicator", k, {"init": "SEEDED_REPLICATOR"})
        add("G8", "pos_witness_external", k, {"reproduction": "EXTERNAL", "init": "SEEDED_WITNESS", "pressure": "EXPLICIT"})
        add("G8", "pos_hybrid_endogenous", k, {"init": "SEEDED_HYBRID", "pressure": "EXPLICIT"})
        add("G8", "neg_external_neutral", k, {"reproduction": "EXTERNAL", "scoring": "NEUTRAL"})
        add("G8", "neg_no_copy_chemistry", k, {}, over={"ldir": "off"})
        add("G8", "cheat_bare_ldir_transplant", k, {}, init_tapes=["1500" + "ff"])
        add("G8", "cheat_smear_transplant", k, {}, init_tapes=[bytes([0x07, 63, 0x08, 0, 0x03, 128, 0x15, 0xFF]).hex()])
        add("G8", "cheat_capture_partial", k, {"reproduction": "ENDOGENOUS_PARTIAL"}, init_tapes=[bytes([0x01, 0x77, 0x08, 70, 0x11, 0xFF]).hex()])
    # G7-P1: the causal test of the POLLINATION/RESERVOIR 'topology effect': v1 (world copies) vs v2 (moves), same seeds
    for spatial in ("NICHES_POLLINATION", "RESERVOIR", "NICHES_ISOLATED"):
        for k in range(150):
            for phys in ("v1", "v2"):
                add("G7P1", spatial, k, {"world": "NICHES", "spatial": spatial}, over={"physics": phys}, arm=phys, pair=k)
    # G1 replication accessibility from fresh random populations (+ G2 sustained, + G6 genealogy)
    for repro in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "PAIR_EXECUTION", "CONSTRUCTIVE"):
        for k in range(400):
            add("G1", "%s/Z80_64" % repro, k, {"reproduction": repro})
    for rep in ("VM_COPY", "BYTECODE32"):
        for k in range(200):
            add("G1", "ENDOGENOUS_COPY/%s" % rep, k, {"representation": rep})
    # G3 endogenous causal advantage: paired seeds, identical initial population, one-axis flip (ext_mut_mult 0 =
    # external offspring are exact copies, as endogenous copies are); historical 4x in a secondary cell
    for init in ("RANDOM", "SEEDED_HYBRID"):
        for pressure in ("IMPLICIT", "EXPLICIT"):
            for task in ("INC", "COND_ONE"):
                cell = "%s/%s/%s" % (init, pressure, task)
                for k in range(100):
                    for arm in ("ENDOGENOUS_COPY", "EXTERNAL"):
                        add("G3", cell, k, {"init": init, "pressure": pressure, "task": task, "reproduction": arm},
                            over={"ext_mut_mult": 0.0}, arm=arm, pair=k)
    for k in range(100):
        for arm in ("ENDOGENOUS_COPY", "EXTERNAL"):
            add("G3", "SEEDED_HYBRID/IMPLICIT/INC/extmut4", k, {"init": "SEEDED_HYBRID", "reproduction": arm},
                over={"ext_mut_mult": 4.0}, arm=arm, pair=k)
    # G5 architecture response: task ON / OFF / ALT, identical seeded-replicator populations, equal compute
    for k in range(100):
        add("G5", "ON_INC", k, {"init": "SEEDED_REPLICATOR", "pressure": "EXPLICIT", "task": "INC", "scoring": "INCREMENTAL"}, arm="ON", pair=k)
        add("G5", "OFF_NEUTRAL", k, {"init": "SEEDED_REPLICATOR", "pressure": "EXPLICIT", "task": "INC", "scoring": "NEUTRAL"}, arm="OFF", pair=k)
        add("G5", "ALT_ECHO", k, {"init": "SEEDED_REPLICATOR", "pressure": "EXPLICIT", "task": "ECHO", "scoring": "INCREMENTAL"}, arm="ALT", pair=k)
    # Phase 8 substrate-ablation probes (one factor at a time, matched seeds)
    for name, over, vec in (("base", {}, {}), ("ldir_off", {"ldir": "off"}, {}), ("ldir_cost4", {"ldir": "cost4"}, {}),
                            ("undefined_halt", {"undefined_op": "HALT"}, {}), ("mut_low", {}, {"mutation_rate": "LOW"}),
                            ("mut_vlow", {"mutation_rate": "VLOW"}, {})):
        for k in range(300):
            add("P8", "RANDOM/COPY/" + name, k, vec, over=over, arm=name, pair=k)
    for name, over in (("base", {}), ("target_zero", {"target_fill": "zero"})):
        for k in range(300):
            add("P8", "RANDOM/PARTIAL/" + name, k, {"reproduction": "ENDOGENOUS_PARTIAL"}, over=over, arm=name, pair=k)
    for name, over, vec in (("base", {}, {}), ("ldir_cost4", {"ldir": "cost4"}, {}), ("undefined_halt", {"undefined_op": "HALT"}, {}),
                            ("mut_low", {}, {"mutation_rate": "LOW"}), ("mut_vlow", {"mutation_rate": "VLOW"}, {})):
        for k in range(60):
            add("P8", "SEEDED/ON/" + name, k, dict({"init": "SEEDED_REPLICATOR", "pressure": "EXPLICIT", "scoring": "INCREMENTAL"}, **vec),
                over=over, arm=name, pair=k)
    # historical specimens: each independent historical origin transplanted into a fresh random population, intact
    # and with its copy instructions NOPed (the intentionally ablated specimen), same seed
    for k, sp in enumerate(inputs.get("historical_origins") or []):
        vec = {"representation": sp["representation"], "reproduction": "ENDOGENOUS_COPY"}
        add("HIST", "intact", k, vec, init_tapes=[sp["tape"]], arm="intact", pair=k)
        add("HIST", "copy_ops_nopped", k, vec, init_tapes=[_nop_copy_ops(sp["tape"])], arm="ablated", pair=k)
    # G1 across task families (ENDOGENOUS_COPY / Z80_64)
    for task in ("CONST", "ECHO", "INC", "COND_ONE", "COND_MULTI", "SUM2"):
        for k in range(150):
            add("G1T", task, k, {"task": task})
    # G7 topology under fixed allocation: fresh random populations and seeded replicators
    for world, spatial in TOPOLOGIES:
        for k in range(150):
            add("G7", "RANDOM/%s/%s" % (world, spatial), k, {"world": world, "spatial": spatial})
        for k in range(40):
            add("G7", "SEEDED/%s/%s" % (world, spatial), k, {"world": world, "spatial": spatial, "init": "SEEDED_REPLICATOR"}, n_seed=10 ** 6 + k)
    for i, p in enumerate(P):
        p["id"] = "g%06d" % (i + 1)
        p["priority"] = LANE_PRIORITY[p["lane"]]
    return P


def plan_hash(P: List[Dict]) -> str:
    return hashlib.sha256(json.dumps(P, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _run(p: Dict) -> Dict:
    from prometheus.z80atlas.runner import run_spec
    from prometheus.z80atlas import adjudication as A
    rd = pathlib.Path(p["workdir"]) / p["id"]
    if rd.exists():
        shutil.rmtree(rd)                              # a partial directory from an interrupted attempt: re-execute
    spec = {"id": p["id"], "family": "%s:%s" % (p["lane"], p["cell"]), "vec": p["vec"], "seed": p["seed"], "ticks": TICKS, "cells": CELLS,
            "budget": BUDGET, "parents": [], "reason": "grounding %s %s arm=%s pair=%s" % (p["lane"], p["cell"], p["arm"], p["pair"]),
            "stage": "grounding", "workdir": p["workdir"], "init_tapes": p["init_tapes"], "config_overrides": p["config_overrides"]}
    res = run_spec(spec)
    s = res["summary"]
    cfg_d = json.loads((rd / "config.json").read_text(encoding="utf-8"))["config"]
    from prometheus.z80atlas.world import Config
    cfg = Config(**{k: (tuple(v) if k == "init_tapes" else v) for k, v in cfg_d.items()})
    dom = s.get("dominant_sr_tape")
    desc = A.repro_descriptor(bytes.fromhex(dom), cfg) if dom else None
    keep = ("extinct", "extinct_tick", "alive_fraction", "final_alive", "endogenous_births", "external_births", "self_rep_births", "sr_max_depth",
            "sr_alive_end", "sr_distinct_alive", "sr_variants_born", "sr_variants_transmitted", "world_copies_under_endogenous", "tail_h",
            "verified", "captures", "births_by_mechanism", "deaths", "wall_s", "physics", "geometry")
    out = {k: p[k] for k in ("id", "lane", "cell", "arm", "pair", "k", "seed")}
    out["summary"] = {k: s.get(k) for k in keep}
    fsr = s.get("first_self_replication")
    out["first_self_replication"] = fsr
    out["dominant_sr_tape"] = dom; out["dominant_sr_descriptor"] = desc
    out["spontaneous"] = A.spontaneous(s, p["vec"], bool(p["init_tapes"]))
    out["task_reached"] = A.task_reached(s)
    out["config_sha256"] = s.get("config_sha256")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir")
    ap.add_argument("--inputs", default=None)
    ap.add_argument("--hours", type=float, default=12.0)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args(argv)
    inputs = json.loads(pathlib.Path(a.inputs).read_text(encoding="utf-8")) if a.inputs else {}
    P = plan(inputs)
    h = plan_hash(P)
    counts: Dict[str, int] = {}
    for p in P:
        counts[p["lane"]] = counts.get(p["lane"], 0) + 1
    if a.plan_only:
        print(json.dumps({"plan_sha256": h, "runs": len(P), "by_lane": counts}, indent=1))
        return 0
    wd = pathlib.Path(a.workdir); wd.mkdir(parents=True, exist_ok=True)
    st_path = wd / "STATUS.json"; res_path = wd / "results.jsonl"
    st = json.loads(st_path.read_text(encoding="utf-8")) if st_path.exists() else {}
    done = set()
    if res_path.exists():
        for line in res_path.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["id"])
            except (ValueError, KeyError):
                pass                                   # a truncated final line: that run is simply re-executed
    if a.status:
        print(json.dumps(dict(st, done=len(done), planned=len(P)), indent=1)); return 0
    if st.get("plan_sha256") and st["plan_sha256"] != h:
        raise SystemExit("plan hash changed since the round started: refusing to continue")
    st.setdefault("plan_sha256", h); st.setdefault("first_start_ts", time.time()); st.setdefault("hours_cap", a.hours)
    st.setdefault("starts", []).append(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    st_path.write_text(json.dumps(st, indent=1), encoding="utf-8")
    deadline = st["first_start_ts"] + st["hours_cap"] * 3600.0
    todo = sorted((p for p in P if p["id"] not in done), key=lambda p: (p["priority"], p["id"]))
    runs_dir = wd / "runs"; runs_dir.mkdir(exist_ok=True)
    for p in todo:
        p["workdir"] = str(runs_dir)
    stopped = "complete"
    with mp.Pool(a.workers) as pool, res_path.open("a", encoding="utf-8", newline="\n") as fh:
        i = 0; chunk = a.workers * 4
        while i < len(todo):
            if time.time() >= deadline:
                stopped = "wall_cap"; break
            batch = todo[i:i + chunk]; i += len(batch)
            for out in pool.imap_unordered(_run, batch):
                fh.write(json.dumps(out, sort_keys=True, default=str) + "\n"); fh.flush()
            st["last_batch_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()); st["submitted"] = len(done) + i
            st_path.write_text(json.dumps(st, indent=1), encoding="utf-8")
    st["stopped"] = stopped; st["stopped_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    st_path.write_text(json.dumps(st, indent=1), encoding="utf-8")
    print(json.dumps({"stopped": stopped, "plan_sha256": h}))
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
