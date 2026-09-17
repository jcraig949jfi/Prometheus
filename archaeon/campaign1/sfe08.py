"""SFE-08 -- FRANKENSTEIN CHIMERA through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe08 [--seeds 1 2 3] [--n-chimeras 100] [--N 100 --G 40 --E 16] [--dry-run]

ORGANS from independently FAILED lineages: SFE-01's W1_d1 floor genotypes, one lineage per
source seed (fetched back from the engine; L1 = seed 1, L2 = seed 2, L3 = seed 3). An organ is
an aligned 2-4-instruction segment of a lineage member. A CHIMERA = [organ from lineage X] +
[organ from lineage Y] (X != Y), composed with explicit provenance (lineage, member index,
offset, length for each half). Sets exposed to task T = W2_K2 (4-bit; no lineage ever saw it):
  ancestors_L1/L2/L3      the lineage members themselves (rebuilt manifests, L-025)
  chimera_XY              n intended chimeras (X,Y drawn over the three lineages)
  random_recomb           n recombinations with the same operation over RANDOM genomes
  shuffled_organs         n chimeras whose two organs come from the SAME lineage (within-
                          lineage recombination: is cross-lineage the active ingredient?)
Exposure: direct reuse (best member on 48 held-out T episodes) and evolution seeded from the
set (N, G, E; common RNG). Synergy claim requires chimera > every ancestor set AND > random
recombination AND > within-lineage recombination; executability alone counts for nothing
(every word sequence executes in this VM).
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
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from         # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse.evolve import evaluate, run_cell             # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402
from archaeon.campaign1.sfe01 import BASE, CACERT, FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402
from archaeon.campaign1.sfe07 import manifest_from_genome      # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-08"
TASK = WorldSpec("W2_K2", K=2, value_bits=4)
MASK62 = (1 << 62) - 1


def fetch_lineages(c, receipt: dict) -> Dict[str, List[List[int]]]:
    r1 = json.loads((HERE / "SFE-01" / "RECEIPT.json").read_text(encoding="utf-8"))
    src_w = r1["worlds"]["source"]
    out: Dict[str, List[List[int]]] = {}
    if c is None:
        return out
    from sfclient.client import EngineClient
    reader = EngineClient(BASE, c.token, cafile=CACERT, client_id=c.client_id)     # session-less (D-013)
    for s, ids in r1["artifacts"].items():
        content = reader.artifact_content(src_w, ids["failures"])
        raw = base64.b64decode(content["content_b64"])
        receipt.setdefault("fetch", {})["L%s" % s] = {"bytes": len(raw), "hash_ok": sha(raw) == str(ids.get("failures_hash", "")).replace("sha256:", "")}
        out["L%s" % s] = json.loads(raw)["failures"]
    return out


def organ(genome: List[int], rng: SplitMix64) -> dict:
    n = len(genome) // 4
    k = min(n, 2 + rng.randbelow(3))
    off = rng.randbelow(max(1, n - k + 1))
    return {"words": genome[4 * off:4 * (off + k)], "offset": off, "k": k}


def compose(lineages: Dict[str, List[List[int]]], rng: SplitMix64, n: int, mode: str, seed: int) -> List[dict]:
    """mode: cross (X != Y), within (X == Y), random (organs from random genomes)."""
    names = sorted(lineages)
    fm = dict(FOUNDRY_C1); fm["seed"] = seed_from("cmp1.sfe08.random", CAMPAIGN_SEED, seed) & MASK62; fm["n"] = 64
    randoms = [o["manifest"]["genome"] for o in G.generate(fm)]
    out = []
    for i in range(n):
        if mode == "random":
            gx, gy = randoms[rng.randbelow(len(randoms))], randoms[rng.randbelow(len(randoms))]
            px, py = ("random", None), ("random", None)
        else:
            x = names[rng.randbelow(len(names))]
            y = x if mode == "within" else names[(names.index(x) + 1 + rng.randbelow(len(names) - 1)) % len(names)]
            ix, iy = rng.randbelow(len(lineages[x])), rng.randbelow(len(lineages[y]))
            gx, gy = lineages[x][ix], lineages[y][iy]
            px, py = (x, ix), (y, iy)
        ox, oy = organ(gx, rng), organ(gy, rng)
        genome = list(ox["words"]) + list(oy["words"])
        m = manifest_from_genome(genome, seed * 1000 + i)
        out.append({"manifest": m, "provenance": {"mode": mode, "x": {"lineage": px[0], "member": px[1], "offset": ox["offset"], "k": ox["k"]},
                                                   "y": {"lineage": py[0], "member": py[1], "offset": oy["offset"], "k": oy["k"]}}})
    return out


def run_set(job: dict) -> dict:
    name, seed, mans = job["set"], job["seed"], job["manifests"]
    N, G_, E = job["N"], job["G"], job["E"]
    t0 = time.time()
    eps = episodes_for(TASK, CAMPAIGN_SEED, "heldoutT", seed, 48)
    scores = []
    for m in mans:
        try:
            scores.append(evaluate(m, eps, rng_seed=7)["reward"])
        except Exception:                                            # noqa: BLE001
            scores.append(0.0)
    init = [G.organism_record(m, None, 0) for m in mans]
    fm = dict(FOUNDRY_C1); fm["seed"] = 808 + seed; fm["n"] = max(0, N - len(init))
    if fm["n"]:
        init = init + G.generate(fm)
    res = run_cell(TASK, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, G_=G_, E=E, init_pop=init[:N], branch="cmp1-sfe08-common", foundry=FOUNDRY_C1)
    ho = evaluate(res["elite"]["manifest"], eps, rng_seed=7)
    return {"set": name, "seed": seed, "n_members": len(mans), "direct_best": max(scores), "direct_mean": sum(scores) / max(1, len(scores)),
            "direct_share_above_chance": sum(1 for s in scores if s > 0.125) / max(1, len(scores)),
            "evolved_heldout": ho["reward"], "first_solved_gen": next((t["gen"] for t in res["trace"] if t["best_reward"] >= 0.5), None),
            "wall_s": round(time.time() - t0, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--n-chimeras", type=int, default=100)
    ap.add_argument("--N", type=int, default=100)
    ap.add_argument("--G", type=int, default=40)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-08")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-08", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "errors": [], "task": TASK.knobs()}
    c = None
    if not a.dry_run:
        t0 = time.time(); c, _ = engine_client()
        sid = c.create_session("cmp1-sfe08")
        w = c.create_world(sid, "cmp1-sfe08-chimera", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED); c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["chimera"] = wid; receipt["session_id"] = sid
        receipt["hypothesis"] = c.hypothesis(wid, "Organs from independently failed lineages, composed cross-lineage with explicit provenance, are more useful on "
                                                  "W2_K2 than their ancestors, than within-lineage recombination and than random recombination.")
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)
    lineages = fetch_lineages(c, receipt)
    if not lineages:
        fm = dict(FOUNDRY_C1); fm["seed"] = 1; fm["n"] = 30
        pop = G.generate(fm)
        lineages = {"L1": [o["manifest"]["genome"] for o in pop[:10]], "L2": [o["manifest"]["genome"] for o in pop[10:20]], "L3": [o["manifest"]["genome"] for o in pop[20:]]}
        receipt["errors"].append({"step": "lineages", "note": "dry run: synthetic lineages"})
    receipt["lineage_sizes"] = {k: len(v) for k, v in lineages.items()}
    sets: Dict[str, List[dict]] = {}
    for name, gs in lineages.items():
        sets["ancestors_" + name] = [manifest_from_genome(g, int(name[1:])) for g in gs]
    rng = SplitMix64(seed_from("cmp1.sfe08.compose", CAMPAIGN_SEED))
    comp = {"chimera_XY": compose(lineages, rng, a.n_chimeras, "cross", 1), "shuffled_organs": compose(lineages, rng, a.n_chimeras, "within", 2),
            "random_recomb": compose(lineages, rng, a.n_chimeras, "random", 3)}
    for k, v in comp.items():
        sets[k] = [x["manifest"] for x in v]
    if c is not None:
        for k, v in comp.items():
            b = json.dumps({"set": k, "members": v}, sort_keys=True).encode()
            receipt["artifacts"][k] = c.artifact(wid, "cmp1.chimera.set.v0", b, {"info_kind": "artifact", "set": k, "provenance": "per member"}, expected_blob_hash=sha(b))["artifact_id"]
    jobs = [{"set": k, "seed": s, "manifests": v, "N": a.N, "G": a.G, "E": a.E} for k, v in sets.items() for s in a.seeds]
    t0 = time.time()
    with mp.Pool(processes=min(a.procs, len(jobs))) as pool:
        rows = pool.map(run_set, jobs)
    receipt["timings"]["exposure_s"] = round(time.time() - t0, 1)
    if c is not None:
        t0 = time.time()
        for r in rows:
            try:
                exp = c.experiment(wid, {"experiment": "SFE-08", "set": r["set"], "seed": r["seed"], "n_members": r["n_members"], "task": TASK.knobs(), "N": a.N, "G": a.G, "E": a.E})
                obs = c.observation(wid, exp["exp_id"], {k: v for k, v in r.items() if k not in ("set", "seed")}, "SURVIVED" if r["evolved_heldout"] >= 0.5 else "FALSIFIED")
                r["engine"] = {"exp_id": exp["exp_id"], "obs_id": obs}
            except Exception as e:                                   # noqa: BLE001
                receipt["errors"].append({"step": "record", "set": r["set"], "seed": r["seed"], "error": repr(e)})
        receipt["timings"]["records_s"] = round(time.time() - t0, 2)
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"chimera": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"chimera": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    summ = {}
    for k in sets:
        rs = [r for r in rows if r["set"] == k]
        summ[k] = {"direct_best": [round(r["direct_best"], 3) for r in rs], "direct_share_above_chance": [round(r["direct_share_above_chance"], 3) for r in rs],
                   "evolved": [round(r["evolved_heldout"], 3) for r in rs], "evolved_mean": round(sum(r["evolved_heldout"] for r in rs) / len(rs), 4),
                   "footholds": sum(1 for r in rs if r["evolved_heldout"] >= 0.5), "first_solved_gen": [r["first_solved_gen"] for r in rs]}
    receipt["summary"] = summ
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    (OUT / "rows.json").write_text(json.dumps(rows, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"lineage_sizes": receipt["lineage_sizes"], "summary": summ, "timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
