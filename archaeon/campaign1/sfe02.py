"""SFE-02 -- H3 PROSPECTIVE VALUE OF RETAINED DIVERSITY through the live engine (campaign 1).

    python -m archaeon.campaign1.sfe02 [--seeds 1 2 3] [--stream 1024] [--cap 32] [--dry-run]

One COMMON candidate stream per seed (every organism evaluated by a WSE search on the
source cell, in evaluation order, with its source score and a fixed descriptor vector) is
replayed OFFLINE through archaeon.producer.h3_replay's four retention policies under one
item cap and one byte cap; the archives are FROZEN (digested, published as artifacts on the
engine) BEFORE a sealed future-query manifest (held-out cells of the same grammar) is
scored by DIRECT REUSE (a query is solved iff some retained candidate scores >= threshold
on it). Prospective utility = solve fraction per policy; diversity = distinct descriptor
cells retained. Engine: stream manifest + archives + sealed queries as artifacts; one
experiment + observation per (policy, seed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
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

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.producer import h3_replay as H3                  # noqa: E402
from archaeon.wse.economics import REGIMES                     # noqa: E402
from archaeon.wse.evolve import evaluate                       # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for        # noqa: E402
from archaeon.campaign1.sfe01 import FOUNDRY_C1, CAMPAIGN_SEED, engine_client, sha   # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SFE-02"
SOURCE = WorldSpec("W1_d1", delay=1, value_bits=4)
QUERY_CELLS = [WorldSpec("W0", value_bits=4), WorldSpec("W1_d4", delay=4, value_bits=4),
               WorldSpec("W2_K2", K=2, value_bits=4), WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4),
               WorldSpec("W1_d16", delay=16, value_bits=4)]
SOLVE_THRESHOLD = 0.5
PERSIST_CODE = {"none": 0.0, "regs": 1.0, "tape": 2.0, "all": 3.0}
EDGES = [[0.5, 1.5, 2.5], [4.5, 5.5, 6.5, 7.5], [0.25, 0.5, 0.75]]      # persist | log2 tape | ops-share
MASK62 = (1 << 62) - 1


def build_stream(seed: int, n: int, N: int, E: int) -> List[dict]:
    """Every organism a short WSE search evaluates on the SOURCE cell, in order: a
    policy-independent stream with source score, descriptors and the manifest for replay."""
    from proteus.foundry.lineage import descend
    rng = SplitMix64(seed_from("cmp1.sfe02.stream", CAMPAIGN_SEED, seed))
    fm = dict(FOUNDRY_C1); fm["seed"] = rng.next_u64() & MASK62; fm["n"] = N
    pop = G.generate(fm)
    out: List[dict] = []
    g = 0
    while len(out) < n:
        eps = episodes_for(SOURCE, CAMPAIGN_SEED, "train", g * 100003 + seed, E)
        scored = []
        for org in pop:
            ev = evaluate(org["manifest"], eps, rng_seed=seed_from("cmp1.sfe02.eval", seed, g))
            m = org["manifest"]
            ops_share = min(1.0, ev["ops_per_episode"] / (m["tick_budget"] * 4.0))
            out.append({"stream_id": len(out), "manifest": m, "score": ev["reward"], "gen": g,
                        "descriptors": (PERSIST_CODE[m["persist"]], float(m["tape_words"].bit_length() - 1), round(ops_share, 3)),
                        "byte_size": 4 * len(m["genome"]) + 24})
            scored.append((ev["reward"], org))
            if len(out) >= n:
                break
        scored.sort(key=lambda z: -z[0])
        new = [z[1] for z in scored[:4]]
        while len(new) < N:
            p = scored[rng.randbelow(len(scored))][1]; q = scored[rng.randbelow(len(scored))][1]
            child, _ = descend(p, rng.next_u64() & MASK62, mate=q if q is not p else None)
            new.append(child)
        pop = new; g += 1
    return out


def to_candidates(stream: List[dict]) -> List[H3.Candidate]:
    return [H3.Candidate(stream_id=r["stream_id"], candidate_digest=hash_obj(r["manifest"]), birth_status="evaluated",
                         assay_ref="wse:W1_d1:4bit", score=r["score"], descriptors=tuple(r["descriptors"]),
                         byte_size=r["byte_size"], replay_ref="manifest:%s" % hash_obj(r["manifest"])) for r in stream]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--stream", type=int, default=1024)
    ap.add_argument("--N", type=int, default=128)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--cap", type=int, default=32)
    ap.add_argument("--reserve", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ws = _ws.assert_not_canonical("run SFE-02")
    OUT.mkdir(parents=True, exist_ok=True)
    T = time.time()
    receipt: Dict = {"experiment": "SFE-02", "campaign_seed": CAMPAIGN_SEED, "workspace": ws, "runtime_hash": RUNTIME_HASH,
                     "engine_path": not a.dry_run, "timings": {}, "worlds": {}, "artifacts": {}, "engine_records": {}, "errors": [],
                     "caps": {"items": a.cap, "bytes": a.cap * 300}, "reserve": a.reserve, "edges": EDGES, "solve_threshold": SOLVE_THRESHOLD}
    c = None
    if not a.dry_run:
        t0 = time.time()
        c, _ = engine_client()
        sid = c.create_session("cmp1-sfe02")
        w = c.create_world(sid, "cmp1-sfe02-retention", sharing_policy="ISOLATED", seed_root=CAMPAIGN_SEED)
        c.start(w["world_id"]); wid = w["world_id"]
        receipt["worlds"]["retention"] = wid; receipt["session_id"] = sid
        receipt["engine_records"]["hypothesis"] = c.hypothesis(wid, "Retention policies (top_k, uniform, behavioral, hybrid) applied to ONE "
                                                                     "candidate stream under one item+byte cap differ in PROSPECTIVE solve fraction "
                                                                     "on sealed future queries; diversity-preserving policies do not trail top_k.")
        receipt["timings"]["startup_s"] = round(time.time() - t0, 2)

    # sealed future queries (before any archive)
    queries = [{"query_id": "q%02d" % i, "cell": q.name, "knobs": q.knobs(), "family": "future", "index": 100 + i, "n_episodes": 24,
                "solves": "held-out reward >= %.2f" % SOLVE_THRESHOLD} for i, q in enumerate(QUERY_CELLS)]
    sealed = H3.seal_future_queries(queries)
    receipt["future_queries"] = sealed
    if c is not None:
        qb = json.dumps(sealed, sort_keys=True).encode()
        receipt["artifacts"]["future_queries"] = c.artifact(wid, "cmp1.h3.future_queries.v0", qb, {"info_kind": "hypothesis"}, expected_blob_hash=sha(qb))["artifact_id"]

    rows = []
    for seed in a.seeds:
        t0 = time.time()
        stream = build_stream(seed, a.stream, a.N, a.E)
        cands = to_candidates(stream)
        rep = H3.replay_all(cands, receipt["caps"], EDGES, a.reserve, seed, attempt_id="cmp1-sfe02-s%d" % seed)
        by_id = {r["stream_id"]: r for r in stream}
        archives = {name: [by_id[i] for i in pol["retained_ids"]] for name, pol in rep["policies"].items()}
        # FREEZE: digests + artifacts before any query is examined
        frozen = {name: {"digest": pol["archive_digest"], "n": pol["retained_n"], "bytes": pol["bytes"], "bounds": pol["bounds"],
                         "distinct_cells": len({tuple(H3._cell(cnd, EDGES) for cnd in [to_candidates([r])[0]]) for r in archives[name]})}
                  for name, pol in rep["policies"].items()}
        if c is not None:
            sb = json.dumps({"seed": seed, "stream_manifest": rep["stream"], "n": len(stream)}, sort_keys=True).encode()
            receipt["artifacts"]["stream_s%d" % seed] = c.artifact(wid, "cmp1.h3.stream.v0", sb, {"info_kind": "artifact", "seed": seed}, expected_blob_hash=sha(sb))["artifact_id"]
            for name in archives:
                ab = json.dumps({"seed": seed, "policy": name, "frozen": frozen[name], "manifests": [r["manifest"] for r in archives[name]]}, sort_keys=True).encode()
                receipt["artifacts"]["archive_%s_s%d" % (name, seed)] = c.artifact(wid, "cmp1.h3.archive.v0", ab, {"info_kind": "artifact", "seed": seed, "policy": name},
                                                                                    expected_blob_hash=sha(ab))["artifact_id"]
        # SCORE by direct reuse, after the freeze
        cache: Dict[tuple, float] = {}

        def solves(cand: H3.Candidate, q: dict) -> bool:
            key = (cand.stream_id, q["query_id"])
            if key not in cache:
                spec = WorldSpec(**q["knobs"])
                cache[key] = evaluate(by_id[cand.stream_id]["manifest"], episodes_for(spec, CAMPAIGN_SEED, q["family"], q["index"] * 10 + seed, q["n_episodes"]), rng_seed=17)["reward"]
            return cache[key] >= SOLVE_THRESHOLD

        arch_c = {name: [cands[i] for i in rep["policies"][name]["retained_ids"]] for name in archives}
        scores = H3.score_archives(arch_c, sealed["queries"], solves)
        # also: best held-out reward per query per policy (a landscape, not a binary)
        best = {name: {q["query_id"]: round(max((cache.get((cd.stream_id, q["query_id"]), 0.0) for cd in arch_c[name]), default=0.0), 4) for q in sealed["queries"]} for name in arch_c}
        # WHOLE-STREAM ceiling: what an uncapped archive would solve (the prospective value is bounded by it)
        ceiling = {}
        for q in sealed["queries"]:
            spec = WorldSpec(**q["knobs"]); eps = episodes_for(spec, CAMPAIGN_SEED, q["family"], q["index"] * 10 + seed, q["n_episodes"])
            top = sorted(stream, key=lambda r: -r["score"])[:64]
            ceiling[q["query_id"]] = round(max(evaluate(r["manifest"], eps, rng_seed=17)["reward"] for r in top), 4)
        row = {"seed": seed, "stream_n": len(stream), "stream_digest": rep["stream"]["stream_digest"], "policies": frozen, "solve": scores,
               "best_per_query": best, "ceiling_top64_of_stream": ceiling, "source_score_max": max(r["score"] for r in stream),
               "source_score_mean": round(sum(r["score"] for r in stream) / len(stream), 4), "wall_s": round(time.time() - t0, 1)}
        if c is not None:
            for name in archives:
                try:
                    exp = c.experiment(wid, {"experiment": "SFE-02", "seed": seed, "policy": name, "caps": receipt["caps"], "archive_digest": frozen[name]["digest"],
                                             "future_queries_digest": sealed["manifest_digest"], "runtime_hash": RUNTIME_HASH})
                    obs = c.observation(wid, exp["exp_id"], {"solve": scores[name], "best_per_query": best[name], "distinct_cells": frozen[name]["distinct_cells"]},
                                        "SURVIVED" if scores[name]["solved"] > 0 else "FALSIFIED")
                    row.setdefault("engine", {})[name] = {"exp_id": exp["exp_id"], "obs_id": obs}
                except Exception as e:                               # noqa: BLE001
                    receipt["errors"].append({"step": "record", "seed": seed, "policy": name, "error": repr(e)})
        rows.append(row)
        print(json.dumps({"seed": seed, "solve": {k: v["solve_fraction"] for k, v in scores.items()}, "distinct_cells": {k: v["distinct_cells"] for k, v in frozen.items()},
                          "ceiling": ceiling, "wall_s": row["wall_s"]}), flush=True)

    if c is not None:
        t0 = time.time()
        try:
            c.terminate(wid); receipt["teardown"] = {"retention": c.get_world(wid).get("state")}
        except Exception as e:                                       # noqa: BLE001
            receipt["teardown"] = {"retention": "ERROR " + repr(e)}
        receipt["timings"]["teardown_s"] = round(time.time() - t0, 2)
    receipt["timings"]["total_s"] = round(time.time() - T, 1)
    receipt["rows"] = rows
    (OUT / "RECEIPT.json").write_text(json.dumps(receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({"timings": receipt["timings"], "errors": receipt["errors"], "teardown": receipt.get("teardown")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
