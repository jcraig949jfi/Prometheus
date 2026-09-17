"""SFE-01 -- H0 FAILURE + COMPONENT EXCHANGE through the live SFE engine (campaign 1).

    python -m archaeon.campaign1.sfe01 [--seeds 1 2 3] [--N 200 --G 60 --E 16] [--procs 12]
                                       [--dry-run]  (no engine calls; standalone, ENGINE_PATH=false)

Flow (RECORD.md section A): register/load client -> session -> topology group -> SOURCE world
(FULLY_SHARED) -> source search (standalone loop) -> publish FAILURES + COMPONENTS artifacts
-> six TARGET worlds (EXPLICIT_IMPORT_ONLY), each imports what its cell needs and fetches the
bytes back (hash-checked) -> target search per cell x seed -> experiments + observations on
the engine -> teardown (terminate every cmp1-sfe01 world; verify) -> rows + receipt.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                      # noqa: E402
from proteus.foundry.grammar import GRAMMAR_HASH               # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse.evolve import FOUNDRY, evaluate, run_cell    # noqa: E402
from archaeon.wse.readout import strip_timing                  # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-01"
BASE = "https://192.168.1.191:8811"
CACERT = str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient" / "config" / "m2.crt")
CONFIG = HERE / "config.local.json"          # gitignored (token never committed)
CAMPAIGN_SEED = 20260917
FOUNDRY_C1 = dict(FOUNDRY, genome_instr_range=[1, 16], tape_words_choices=[16, 32, 64, 128, 256],
                  tick_budget_choices=[16, 64, 256])
SOURCE = WorldSpec("W1_d1", delay=1, value_bits=4)
TARGET = WorldSpec("W2_K2", K=2, value_bits=4)
CELLS = ["00", "10", "01", "11", "10r", "01r"]
MASK62 = (1 << 62) - 1


# ------------------------------------------------------------------ engine helpers
def engine_client():
    from sfclient.client import EngineClient
    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    c = EngineClient(BASE, cfg.get("token"), cafile=CACERT, client_id=cfg.get("client_id"))
    if not cfg.get("token"):
        c.register("cmp1-archaeon")
        cfg = {"token": c.token, "client_id": c.client_id, "registered_at": time.time(), "engine": BASE}
        CONFIG.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    return c, cfg


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def opsig(genome) -> tuple:
    """Attempt 2 (D-008): the FAILURE signature of a genotype is its opcode sequence
    (word mod 25 per instruction), so that a tabu can fire on operand-only variants."""
    return tuple(w % 25 for w in genome[0::4])


# ------------------------------------------------------------------ residue
def harvest_residue(res: dict, rng: SplitMix64, max_fail: int = 64) -> dict:
    """FAILURES = final-generation organisms at the reward floor (genome tuples);
    COMPONENTS = aligned 2-4-instruction segments of the top-8 final organisms."""
    pop = res["final_population"]
    floor = [o for o in pop if o["reward"] == 0.0]
    failures = [o["manifest"]["genome"] for o in floor[:max_fail]]
    comps = []
    for o in [z for z in pop if z["reward"] > 0.0][:8]:
        g = o["manifest"]["genome"]
        n = len(g) // 4
        for k in (2, 3, 4):
            for i in range(0, max(1, n - k + 1)):
                seg = g[4 * i:4 * (i + k)]
                if len(seg) == 4 * k:
                    comps.append({"words": seg, "source_reward": o["reward"], "k": k})
    return {"failures": failures, "components": comps, "n_floor": len(floor), "n_pop": len(pop)}


def random_residue(rng: SplitMix64, n_fail: int, n_comp: int) -> dict:
    fm = dict(FOUNDRY_C1); fm["seed"] = rng.next_u64() & MASK62; fm["n"] = n_fail + 8
    pop = G.generate(fm)
    failures = [o["manifest"]["genome"] for o in pop[:n_fail]]
    comps = []
    for o in pop[n_fail:]:
        g = o["manifest"]["genome"]; n = len(g) // 4
        for k in (2, 3, 4):
            for i in range(0, max(1, n - k + 1)):
                seg = g[4 * i:4 * (i + k)]
                if len(seg) == 4 * k:
                    comps.append({"words": seg, "source_reward": None, "k": k})
    return {"failures": failures, "components": comps[:n_comp]}


def seeded_pop(N: int, seed: int, components: Optional[List[dict]]) -> List[dict]:
    fm = dict(FOUNDRY_C1); fm["seed"] = seed_from("cmp1.sfe01.gen0", CAMPAIGN_SEED, seed) & MASK62; fm["n"] = N
    pop = G.generate(fm)
    if not components:
        return pop
    rng = SplitMix64(seed_from("cmp1.sfe01.splice", CAMPAIGN_SEED, seed))
    out = []
    for org in pop:
        m = dict(org["manifest"]); g = list(m["genome"])
        seg = components[rng.randbelow(len(components))]["words"]
        cap = m["tape_words"]
        n = len(g) // 4
        pos = rng.randint(0, n) * 4
        g = g[:pos] + list(seg) + g[pos:]
        while len(g) > min(cap, 4096) or len(g) > 4 * 64:
            g = g[:-4]
        m["genome"] = g
        out.append(G.organism_record(m, org["lineage_id"], 0))
    return out


# ------------------------------------------------------------------ jobs
def run_target(job: dict) -> dict:
    cell, seed = job["cell"], job["seed"]
    res_in = job["residue"]
    tabu = set(opsig(g) for g in res_in.get("failures", [])) if cell in ("10", "11", "10r") else None
    comps = res_in.get("components") if cell in ("01", "11", "01r") else None
    init = seeded_pop(job["N"], seed, comps)
    t0 = time.time()
    res = run_cell(TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=job["N"], G_=job["G"], E=job["E"],
                   init_pop=init, branch="cmp1-common", rng_label="cmp1-common", foundry=FOUNDRY_C1, tabu=tabu, tabu_key=opsig)   # attempt 2: common RNG (D-007), opcode-signature tabu (D-008)
    elite = res["elite"]
    ho = evaluate(elite["manifest"], episodes_for(TARGET, CAMPAIGN_SEED, "heldout", seed, 48), rng_seed=7)
    return {"cell": cell, "seed": seed, "competence_heldout": ho["reward"], "train_last": res["elite_eval"]["reward"],
            "ops_per_episode": ho["ops_per_episode"], "persist": ho["persist"], "persistent_words": ho["meter"]["persistent_state_words"],
            "elite_id": elite["organism_id"], "tabu_hits": res["tabu_hits"], "n_tabu": len(tabu) if tabu else 0,
            "n_components": len(comps) if comps else 0, "first_solved_gen": next((t["gen"] for t in res["trace"] if t["best_reward"] >= 0.5), None),
            "trace_best": [t["best_reward"] for t in res["trace"]], "wall_s": round(time.time() - t0, 1),
            "elite_manifest": elite["manifest"]}


def run_source(seed: int, N: int, G_: int, E: int) -> dict:
    res = run_cell(SOURCE, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, branch="cmp1-source", rng_label="cmp1-source", foundry=FOUNDRY_C1)
    rng = SplitMix64(seed_from("cmp1.sfe01.residue", CAMPAIGN_SEED, seed))
    return {"seed": seed, "elite_reward": res["elite_eval"]["reward"], "residue": harvest_residue(res, rng),
            "trace_best": [t["best_reward"] for t in res["trace"]]}


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=60)
    ap.add_argument("--G-source", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-01")
    OUT.mkdir(parents=True, exist_ok=True)
    receipt: Dict = {"experiment": "SFE-01", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "grammar_hash": GRAMMAR_HASH, "engine_path": not a.dry_run, "N": a.N, "G": a.G, "E": a.E,
                     "timings": {}, "worlds": {}, "artifacts": {}, "imports": {}, "engine_records": {}, "errors": []}
    T = time.time()

    # ---- startup
    c = None
    if not a.dry_run:
        t0 = time.time()
        c, cfg = engine_client()
        receipt["client_id"] = c.client_id
        receipt["engine_version"] = c.version()
        sid = c.create_session("cmp1-sfe01")
        gid = c.create_topology_group("cmp1-sfe01 residue exchange")
        src = c.create_world(sid, "cmp1-sfe01-source", sharing_policy="FULLY_SHARED", topology_group=gid,
                             seed_root=CAMPAIGN_SEED)
        c.start(src["world_id"])
        receipt["session_id"] = sid; receipt["topology_group"] = gid; receipt["worlds"]["source"] = src["world_id"]
        hyp = c.hypothesis(src["world_id"], "Residue of a W1_d1 search (floor genotypes; segments of above-floor genotypes) "
                                            "changes held-out competence of a later W2_K2 search: main effects F, C and interaction I.")
        receipt["engine_records"]["source_hypothesis"] = hyp
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)

    # ---- source searches (one per seed)
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(a.seeds))) as pool:
        sources = pool.starmap(run_source, [(s, a.N, a.G_source, a.E) for s in a.seeds])
    receipt["timings"]["source_s"] = round(time.time() - t0, 1)
    source_by_seed = {s["seed"]: s for s in sources}

    # ---- publish residue as artifacts on the source world; failures also as first-class failures
    art_ids: Dict[int, Dict[str, str]] = {}
    if c is not None:
        t0 = time.time()
        for s in a.seeds:
            r = source_by_seed[s]["residue"]
            fb = json.dumps({"seed": s, "failures": r["failures"], "n_floor": r["n_floor"], "n_pop": r["n_pop"]}, sort_keys=True).encode()
            cb = json.dumps({"seed": s, "components": r["components"]}, sort_keys=True).encode()
            fa = c.artifact(src["world_id"], "cmp1.failures.v0", fb, {"info_kind": "failure", "seed": s, "source_world": "W1_d1"},
                            expected_blob_hash=sha(fb))
            ca = c.artifact(src["world_id"], "cmp1.components.v0", cb, {"info_kind": "artifact", "seed": s, "source_world": "W1_d1"},
                            expected_blob_hash=sha(cb))
            art_ids[s] = {"failures": fa["artifact_id"], "components": ca["artifact_id"], "failures_hash": fa.get("blob_hash"),
                          "components_hash": ca.get("blob_hash")}
            try:
                fid = c.failure(src["world_id"], failure_type="SEARCH_FLOOR",
                                falsifier="held-out competence of W1_d1 search seed %d; n_floor=%d of %d; artifact=%s" % (s, r["n_floor"], r["n_pop"], fa["artifact_id"]),
                                violated="organism answers above the 1/16 chance floor")   # attempt 1: 'evidence' kw refused (422 extra_forbidden), L-006
                art_ids[s]["failure_record"] = fid
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "failure_record", "seed": s, "error": repr(e)})
        receipt["artifacts"] = art_ids
        receipt["timings"]["publish_s"] = round(time.time() - t0, 2)

    # ---- target worlds + imports (per cell); the residue each cell RUNS WITH is what it fetched back
    residue_for: Dict[tuple, dict] = {}
    rr = SplitMix64(seed_from("cmp1.sfe01.random_residue", CAMPAIGN_SEED))
    if c is not None:
        t0 = time.time()
        for cell in CELLS:
            w = c.create_world(sid, "cmp1-sfe01-target-%s" % cell, sharing_policy="EXPLICIT_IMPORT_ONLY", topology_group=gid,
                               seed_root=CAMPAIGN_SEED)
            c.start(w["world_id"])
            receipt["worlds"]["target_" + cell] = w["world_id"]
            for s in a.seeds:
                got: Dict[str, list] = {}
                for kind in (["failures"] if cell in ("10", "11") else []) + (["components"] if cell in ("01", "11") else []):
                    try:
                        imp = c.import_artifact(w["world_id"], src["world_id"], art_ids[s][kind])
                        content = c.artifact_content(w["world_id"], imp["artifact_id"])
                        raw = base64.b64decode(content["content_b64"])
                        ok = sha(raw) == str(art_ids[s][kind + "_hash"] or "").replace("sha256:", "")   # attempt 1 compared against the 'sha256:' prefixed form
                        got[kind] = json.loads(raw)[kind]
                        receipt["imports"]["%s_s%d_%s" % (cell, s, kind)] = {"artifact_id": imp["artifact_id"], "origin": imp.get("origin"),
                                                                             "source_world": imp.get("source_world"), "bytes": len(raw), "hash_ok": ok}
                    except Exception as e:                           # noqa: BLE001
                        receipt["errors"].append({"step": "import", "cell": cell, "seed": s, "kind": kind, "error": repr(e)})
                if cell == "10r" or cell == "01r":
                    src_r = source_by_seed[s]["residue"]
                    got = random_residue(rr.derive("r", cell, s), len(src_r["failures"]), len(src_r["components"]))
                residue_for[(cell, s)] = got
        receipt["timings"]["targets_setup_s"] = round(time.time() - t0, 2)
    else:
        for cell in CELLS:
            for s in a.seeds:
                src_r = source_by_seed[s]["residue"]
                if cell in ("10r", "01r"):
                    residue_for[(cell, s)] = random_residue(rr.derive("r", cell, s), len(src_r["failures"]), len(src_r["components"]))
                else:
                    residue_for[(cell, s)] = src_r

    # ---- target searches
    jobs = [{"cell": cell, "seed": s, "residue": residue_for[(cell, s)], "N": a.N, "G": a.G, "E": a.E} for cell in CELLS for s in a.seeds]
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(jobs))) as pool:
        rows = pool.map(run_target, jobs)
    receipt["timings"]["targets_s"] = round(time.time() - t0, 1)

    # ---- engine records: experiment + observation per row
    if c is not None:
        t0 = time.time()
        for r in rows:
            wid = receipt["worlds"]["target_" + r["cell"]]
            try:
                exp = c.experiment(wid, {"experiment": "SFE-01", "cell": r["cell"], "seed": r["seed"], "N": a.N, "G": a.G, "E": a.E,
                                         "target": TARGET.knobs(), "source": SOURCE.knobs(), "n_tabu": r["n_tabu"],
                                         "n_components": r["n_components"], "runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH})
                obs = c.observation(wid, exp["exp_id"], {"competence_heldout": r["competence_heldout"], "train_last": r["train_last"],
                                                         "ops_per_episode": r["ops_per_episode"], "persistent_words": r["persistent_words"],
                                                         "tabu_hits": r["tabu_hits"], "first_solved_gen": r["first_solved_gen"]},
                                    "SURVIVED" if r["competence_heldout"] >= 0.5 else "FALSIFIED")
                r["engine"] = {"world_id": wid, "exp_id": exp["exp_id"], "obs_id": obs, "spec_hash": exp.get("spec_hash")}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "record", "cell": r["cell"], "seed": r["seed"], "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)

    # ---- effects
    def mean(cell):
        v = [r["competence_heldout"] for r in rows if r["cell"] == cell]
        return sum(v) / len(v)
    m = {cell: mean(cell) for cell in CELLS}
    effects = {"F_main": (m["10"] + m["11"]) / 2 - (m["00"] + m["01"]) / 2,
               "C_main": (m["01"] + m["11"]) / 2 - (m["00"] + m["10"]) / 2,
               "interaction": m["11"] - m["10"] - m["01"] + m["00"],
               "F_vs_random": m["10"] - m["10r"], "C_vs_random": m["01"] - m["01r"], "cell_means": m,
               "per_seed": {cell: [r["competence_heldout"] for r in rows if r["cell"] == cell] for cell in CELLS}}

    # ---- teardown
    if c is not None:
        t0 = time.time()
        td = {}
        for name, wid in receipt["worlds"].items():
            try:
                c.terminate(wid)
                td[name] = c.get_world(wid).get("state")
            except Exception as e:                                   # noqa: BLE001
                td[name] = "ERROR " + repr(e)
        receipt["teardown"] = td
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
        try:
            receipt["source_events_tail"] = c.events(receipt["worlds"]["source"], limit=5)
            receipt["knowledge_target_11"] = c.knowledge_set(receipt["worlds"]["target_11"])
        except Exception as e:                                       # noqa: BLE001
            receipt["errors"].append({"step": "post", "error": repr(e)})
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    receipt["sources"] = [{k: v for k, v in s.items() if k != "residue"} | {"n_failures": len(s["residue"]["failures"]),
                          "n_components": len(s["residue"]["components"]), "n_floor": s["residue"].get("n_floor")} for s in sources]
    receipt["effects"] = effects
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"effects": effects, "timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
