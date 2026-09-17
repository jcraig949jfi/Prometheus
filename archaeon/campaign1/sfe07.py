"""SFE-07 -- CROSS-WORLD EXAPTATION through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe07 [--seeds 1 2 3] [--N 100 --G 40 --E 16] [--dry-run]

Frozen artifacts that were FAILED or SPECIALIZED in World A are exposed PROSPECTIVELY to a
PREDECLARED World B. Sets (frozen before any B evaluation, declared as an artifact first):
  failed_A       the floor genotypes of SFE-01's W1_d1 source searches (cmp1.failures.v0
                 artifacts, fetched BACK from the engine's TERMINATED source world)
  specialized_A  SFE-05 fixed/on elites (competent at Kd 4/8 on the stream cell, lost Kd 0)
  best_A         SFE-05 adaptive/on elites (the successful lineages of the same world)
  random         random genotypes, matched count to failed_A
World B (predeclared): W3_K2 -- K=2, ask_mode one (late binding), 4-bit; none of the sets
was evolved or evaluated on it. Exposure: (a) DIRECT reuse -- best held-out competence of any
member of the set on B; (b) EVOLUTION seeded from the set (padded with randoms to N) for G
generations on B with common random numbers -> held-out competence. Primary per set x seed.
"""
from __future__ import annotations

import argparse
import base64
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import generate as G                      # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj    # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402
from proteus.foundry.vm import SCHEMA                          # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse.evolve import evaluate, run_cell             # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402
from archaeon.campaign1.sfe01 import FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-07"
WORLD_B = WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4)
SETS = ["failed_A", "specialized_A", "best_A", "random"]
MASK62 = (1 << 62) - 1


def manifest_from_genome(genome: List[int], seed: int) -> dict:
    """SFE-01's failure artifacts carry genomes only (the manifest fields were not stored --
    an artifact schema gap, L-025): rebuild a manifest with the campaign's gen-0 sampling
    ranges, seeded, so the genome is the only thing carried from World A."""
    rng = SplitMix64(seed_from("cmp1.sfe07.rebuild", seed, tuple(genome)))
    tape = max(16, 4 * ((len(genome) // 4 + 3) // 4) * 4)
    tape_choices = [t for t in (16, 32, 64, 128, 256) if t >= len(genome)] or [256]
    return {"schema_version": SCHEMA, "n_regs": rng.randint(2, 16), "tape_words": tape_choices[rng.randbelow(len(tape_choices))],
            "genome": list(genome), "code_writable": bool(rng.randbelow(2)), "persist": ["none", "regs", "tape", "all"][rng.randbelow(4)],
            "tick_budget": [16, 64, 256][rng.randbelow(3)], "out_cap": [1, 4][rng.randbelow(2)]}


def load_sets(c, receipt: dict) -> Dict[str, List[dict]]:
    sets: Dict[str, List[dict]] = {k: [] for k in SETS}
    # failed_A: fetch SFE-01's failure artifacts back from the engine (TERMINATED world)
    r1 = json.loads((HERE / "SFE-01" / "RECEIPT.json").read_text(encoding="utf-8"))
    src_w = r1["worlds"]["source"]
    fetched = 0
    # attempt 2 (L-026): cross-SESSION reads of an earlier world are refused with the campaign
    # session's key (403 SESSION_MISMATCH) but admitted with NO session key under advisory
    # enforcement -- use a session-less reader for cross-experiment artifact reads.
    reader = None
    if c is not None:
        from sfclient.client import EngineClient
        from archaeon.campaign1.sfe01 import BASE, CACERT
        reader = EngineClient(BASE, c.token, cafile=CACERT, client_id=c.client_id)
    for s, ids in r1["artifacts"].items():
        try:
            if reader is not None:
                content = reader.artifact_content(src_w, ids["failures"])
                raw = base64.b64decode(content["content_b64"])
                receipt.setdefault("fetch", {})["failures_s%s" % s] = {"bytes": len(raw), "hash_ok": sha(raw) == str(ids.get("failures_hash", "")).replace("sha256:", ""),
                                                                      "world_state_at_fetch": "TERMINATED (SFE-01 teardown)"}
                genomes = json.loads(raw)["failures"]
            else:
                genomes = []
            for g in genomes:
                sets["failed_A"].append(manifest_from_genome(g, int(s)))
            fetched += len(genomes)
        except Exception as e:                                       # noqa: BLE001
            receipt["errors"].append({"step": "fetch_failed_A", "seed": s, "error": repr(e)})
    if not sets["failed_A"]:
        # dry run or fetch failure: fall back to the committed attempt rows (genomes not stored there either) -> randoms labelled
        receipt["errors"].append({"step": "fetch_failed_A", "note": "no genomes fetched; failed_A EMPTY"})
    r5 = json.load(open(HERE / "SFE-05" / "rows.json", encoding="utf-8"))
    sets["specialized_A"] = [r["elite_manifest"] for r in r5 if r["challenge"] == "fixed" and r["transfer"] == "on"]
    sets["best_A"] = [r["elite_manifest"] for r in r5 if r["challenge"] == "adaptive" and r["transfer"] == "on"]
    fm = dict(FOUNDRY_C1); fm["seed"] = seed_from("cmp1.sfe07.random", CAMPAIGN_SEED) & MASK62; fm["n"] = max(3, len(sets["failed_A"]))
    sets["random"] = [o["manifest"] for o in G.generate(fm)]
    return sets


def run_set(job: dict) -> dict:
    name, seed, mans = job["set"], job["seed"], job["manifests"]
    N, G_, E = job["N"], job["G"], job["E"]
    t0 = time.time()
    direct = {}
    eps = episodes_for(WORLD_B, CAMPAIGN_SEED, "heldoutB", seed, 48)
    best_direct = 0.0
    for i, m in enumerate(mans):
        try:
            r = evaluate(m, eps, rng_seed=7)["reward"]
        except Exception:                                            # noqa: BLE001
            r = 0.0
        direct[i] = r; best_direct = max(best_direct, r)
    init = [G.organism_record(m, None, 0) for m in mans]
    fm = dict(FOUNDRY_C1); fm["seed"] = 909 + seed; fm["n"] = max(0, N - len(init))
    init = init + [o for o in G.generate(fm)] if fm["n"] else init
    res = run_cell(WORLD_B, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, init_pop=init[:N], branch="cmp1-sfe07-common", foundry=FOUNDRY_C1)
    ho = evaluate(res["elite"]["manifest"], eps, rng_seed=7)
    return {"set": name, "seed": seed, "n_members": len(mans), "direct_best": best_direct, "direct_mean": sum(direct.values()) / max(1, len(direct)),
            "evolved_heldout": ho["reward"], "first_solved_gen": next((t["gen"] for t in res["trace"] if t["best_reward"] >= 0.5), None),
            "persist": ho["persist"], "trace_best": [t["best_reward"] for t in res["trace"]], "wall_s": round(time.time() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--N", type=int, default=100)
    ap.add_argument("--G", type=int, default=40)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-07")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-07", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "errors": [], "world_B": WORLD_B.knobs()}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe07")
        w = c.create_world(sid, "cmp1-sfe07-worldB", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED); c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["B"] = wid; receipt["session_id"] = sid
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)
    # PREDECLARATION artifact: World B and the set definitions, sealed BEFORE any set is loaded or evaluated
    decl = {"world_B": WORLD_B.knobs(), "sets": {"failed_A": "SFE-01 cmp1.failures.v0 floor genotypes of W1_d1 (fetched from the engine)",
                                                "specialized_A": "SFE-05 fixed/on elites", "best_A": "SFE-05 adaptive/on elites", "random": "matched-count random genotypes"},
            "exposure": {"direct": "best held-out competence of any member on B (48 episodes)", "evolved": "N=%d G=%d E=%d from the set, common RNG" % (a.N, a.G, a.E)},
            "declared_at": time.time()}
    receipt["predeclaration"] = decl
    if c is not None:
        db = json.dumps(decl, sort_keys=True).encode()
        receipt["artifacts"]["predeclaration"] = c.artifact(wid, "cmp1.exapt.predeclaration.v0", db, {"info_kind": "hypothesis"}, expected_blob_hash=sha(db))["artifact_id"]
        receipt["hypothesis"] = c.hypothesis(wid, "Artifacts that failed or specialized in World A (W1_d1 floor genotypes; Kd-4 specialists) become useful on the "
                                                  "predeclared World B (W3_K2) beyond matched random genotypes, by direct reuse or as evolutionary seeds.")
    sets = load_sets(c, receipt)
    receipt["set_sizes"] = {k: len(v) for k, v in sets.items()}
    if c is not None:
        for k, v in sets.items():
            b = json.dumps({"set": k, "manifests": v}, sort_keys=True).encode()
            receipt["artifacts"]["set_" + k] = c.artifact(wid, "cmp1.exapt.frozen_set.v0", b, {"info_kind": "artifact", "set": k}, expected_blob_hash=sha(b))["artifact_id"]
    jobs = [{"set": k, "seed": s, "manifests": v, "N": a.N, "G": a.G, "E": a.E} for k, v in sets.items() for s in a.seeds if v]
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, max(1, len(jobs)))) as pool:
        rows = pool.map(run_set, jobs)
    receipt["timings"]["exposure_s"] = round(time.time() - t0, 1)
    if c is not None:
        t0 = time.time()
        for r in rows:
            try:
                exp = c.experiment(wid, {"experiment": "SFE-07", "set": r["set"], "seed": r["seed"], "n_members": r["n_members"], "world_B": WORLD_B.knobs(),
                                         "N": a.N, "G": a.G, "E": a.E, "predeclaration": receipt["artifacts"].get("predeclaration")})
                obs = c.observation(wid, exp["exp_id"], {"direct_best": r["direct_best"], "evolved_heldout": r["evolved_heldout"], "first_solved_gen": r["first_solved_gen"]},
                                    "SURVIVED" if max(r["direct_best"], r["evolved_heldout"]) >= 0.5 else "FALSIFIED")
                r["engine"] = {"exp_id": exp["exp_id"], "obs_id": obs}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "record", "set": r["set"], "seed": r["seed"], "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"B": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"B": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    summ = {}
    for k in SETS:
        rs = [r for r in rows if r["set"] == k]
        if rs:
            summ[k] = {"direct_best": [r["direct_best"] for r in rs], "evolved_heldout": [r["evolved_heldout"] for r in rs],
                       "evolved_mean": sum(r["evolved_heldout"] for r in rs) / len(rs), "footholds": sum(1 for r in rs if r["evolved_heldout"] >= 0.5)}
    receipt["summary"] = summ
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"set_sizes": receipt["set_sizes"], "summary": summ, "fetch": receipt.get("fetch"), "timings": receipt["timings"],
                      "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
