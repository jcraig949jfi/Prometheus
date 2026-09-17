"""C2-SFE-05 -- RETENTION REPLAY WITH A PROVEN-CAPABLE STREAM (parent SFE-02).

    python -m archaeon.campaign2.c2_sfe05 [--seeds 1..6] [--N 200 --E 16 --G-cap 70] [--cap 32] [--dry-run]

SFE-02 (campaign 1) replayed four retention policies over streams of 1024 and 4096
organisms and found nothing above the sealed query threshold in either: the retention
question was never posed. Here the stream is every organism a W2_K2 4-bit search evaluates
(step API), run until FIVE generations past its first solver (cap G_cap), and the stream's
CAPABILITY is checked against the SEALED future queries BEFORE any archive is frozen: the
top-64 organisms by source score are scored on every sealed query cell; a seed is capable
iff some organism reaches the sealed threshold (0.5) on some query. The threshold is sealed
with the queries and never touched. Then the four policies of archaeon.producer.h3_replay
(top_k, uniform, behavioral, hybrid) retain under one item + byte cap, the archives are
FROZEN (digested, published) and scored by direct reuse on the sealed queries.

Rows: one per (seed, policy): solve fraction over the queries, best held-out per query,
plus per-seed stream telemetry (capable, ceiling per query, source maturity). The retention
comparison is made over CAPABLE seeds only; STREAM_BELOW_THRESHOLD fires if no seed is.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List

from proteus.foundry.identity import hash_obj

from archaeon.producer import h3_replay as H3
from archaeon.wse import telemetry as T
from archaeon.wse.economics import REGIMES
from archaeon.wse.evolve import Evolution, evaluate
from archaeon.wse.worlds import WorldSpec, episodes_for
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment
from archaeon.campaign2.runner import CAMPAIGN_SEED

SOURCE = WorldSpec("W2_K2", K=2, value_bits=4)
QUERY_CELLS = [WorldSpec("W0", value_bits=4), WorldSpec("W1_d1", delay=1, value_bits=4), WorldSpec("W1_d4", delay=4, value_bits=4),
               WorldSpec("W1_d16", delay=16, value_bits=4), WorldSpec("W3_K2", K=2, ask_mode="one", value_bits=4)]
SOLVE_THRESHOLD = 0.5
POLICIES = ["top_k", "uniform", "behavioral", "hybrid"]
PERSIST_CODE = {"none": 0.0, "regs": 1.0, "tape": 2.0, "all": 3.0}
EDGES = [[0.5, 1.5, 2.5], [4.5, 5.5, 6.5, 7.5], [0.25, 0.5, 0.75]]      # persist | log2 tape | ops-share
CHANCE = 1.0 / 16


def build_stream(job: dict) -> dict:
    """Every organism the source search evaluates, in order, until 5 generations past the
    first solver (cap G_cap): a policy-independent stream with source score, descriptors and
    manifest, plus the source population's maturity block."""
    seed, N, E, G_cap = job["seed"], job["N"], job["E"], job["G_cap"]
    ev = Evolution(SOURCE, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c2-sfe05-stream", foundry=FOUNDRY_C2)
    out: List[dict] = []
    stop_at = None
    for g in range(G_cap):
        last = g == G_cap - 1 or (stop_at is not None and g >= stop_at)
        ev.evaluate_generation(last=last)
        for f, org, e in ev.scored:
            m = org["manifest"]
            ops_share = min(1.0, e["ops_per_episode"] / (m["tick_budget"] * 4.0))
            out.append({"stream_id": len(out), "manifest": m, "score": e["reward"], "gen": g,
                        "descriptors": (PERSIST_CODE[m["persist"]], float(m["tape_words"].bit_length() - 1), round(ops_share, 3)),
                        "byte_size": 4 * len(m["genome"]) + 24})
        if ev.first_solved_gen is not None and stop_at is None:
            stop_at = g + 5
        if last:
            break
        ev.reproduce()
    res = ev.result()
    mat = T.maturity(SOURCE.name, res["elite_eval"]["reward"], [z["reward"] for z in res["final_population"]], chance=CHANCE,
                     budget={"N": N, "G": res["generations"], "E": E}, generation=res["generations"] - 1)
    return {"seed": seed, "stream": out, "maturity": mat, "first_solved_gen": res["first_solved_gen"], "generations": res["generations"],
            "trace_best": [t["best_reward"] for t in res["trace"]], "_res": res}


def to_candidates(stream: List[dict]) -> List[H3.Candidate]:
    return [H3.Candidate(stream_id=r["stream_id"], candidate_digest=hash_obj(r["manifest"]), birth_status="evaluated",
                         assay_ref="wse:W2_K2:4bit", score=r["score"], descriptors=tuple(r["descriptors"]),
                         byte_size=r["byte_size"], replay_ref="manifest:%s" % hash_obj(r["manifest"])) for r in stream]


def query_episodes(q: dict, seed: int):
    spec = WorldSpec(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in q["knobs"].items()})
    return episodes_for(spec, CAMPAIGN_SEED, q["family"], q["index"] * 10 + seed, q["n_episodes"])


class Retention(Experiment):
    ID = "C2-SFE-05"
    TITLE = "retention replay with a proven-capable stream"
    PARENTS = ["SFE-02"]
    METRICS = ("solve_fraction", "n_solved")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--G-cap", type=int, default=70)
    ap.add_argument("--cap", type=int, default=32)
    ap.add_argument("--reserve", type=int, default=8)
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    X = Retention(dry_run=a.dry_run, procs=a.procs)
    reach = X.reachability_for([(SOURCE, a.N, 60, a.E, "E0")])
    caps = {"items": a.cap, "bytes": a.cap * 300}
    queries = [{"query_id": "q%02d" % i, "cell": q.name, "knobs": q.knobs(), "family": "future", "index": 100 + i, "n_episodes": 24,
                "solves": "held-out reward >= %.2f" % SOLVE_THRESHOLD} for i, q in enumerate(QUERY_CELLS)]
    sealed = H3.seal_future_queries(queries)
    X.seal({
        "question": "Gate: does a stream of every organism a W2_K2 4-bit search evaluates (run 5 generations past its first solver) contain an organism "
                    "scoring >= 0.5 on at least one SEALED future query cell (W0, W1_d1, W1_d4, W1_d16, W3_K2)? Science (capable seeds only): do the four "
                    "retention policies under one cap (%d items) differ in prospective solve fraction on the sealed queries?" % a.cap,
        "parent_evidence": "SFE-02: streams of 1024 and 4096 W1_d1 organisms held nothing above threshold (twice INCONCLUSIVE). Table: W2_K2 4-bit N200 G60 E16 "
                           "7/17 REACHABLE; W0 4-bit COMMON by ~G35; sub-solutions of W2_K2 solvers score 0.5 on W0-like cells (C2-SFE-03/04).",
        "assay_capability_requirement": "per seed: max over the stream's top-64 (by source score) of held-out reward on any sealed query >= %.2f, checked BEFORE "
                                        "freezing archives; experiment: >= 3 capable seeds (else UNDERPOWERED); no capable seed => STREAM_BELOW_THRESHOLD" % SOLVE_THRESHOLD,
        "positive_control": "the stream's own top-64 organisms on the sealed queries (the uncapped ceiling); the threshold %.2f is sealed here and never changed" % SOLVE_THRESHOLD,
        "reachability_estimate": reach,
        "arms": POLICIES,
        "crn_policy": "one stream per seed shared by every policy (policy-independent by construction); policies are deterministic given the stream and the seed",
        "budget": {"N": a.N, "E": a.E, "G_cap": a.G_cap, "stop_rule": "5 generations past the first solver", "caps": caps, "reserve": a.reserve,
                   "seeds": a.seeds, "queries": [q["cell"] for q in queries], "query_episodes": 24, "solve_threshold": SOLVE_THRESHOLD, "edges": EDGES},
        "primary_observable": "solve_fraction (queries solved by direct reuse / queries) per policy x capable seed; behavioral vs top_k",
        "claim_ceiling": "weak at best (<= 6 capable seeds, 5 queries); a capable negative = diversity-preserving retention does not beat top_k prospectively",
        "falsification_condition": "behavioral - top_k < 0.20 (one query of five) over capable seeds => CAPABLE_NEGATIVE for the diversity hypothesis",
        "typed_failure_conditions": ["STREAM_BELOW_THRESHOLD (no capable seed)", "UNDERPOWERED (< 3 capable seeds)", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["per-seed capability + ceiling per query", "stream length and first solver generation", "source maturity", "archive digests",
                                       "best held-out per query per policy", "reachability rows (stream runs as treated: stop rule)"],
        "machine_changes_exercised": ["B (STREAM_BELOW_THRESHOLD from a pre-freeze check)", "G (stop rule)", "E (archives carry maturity)", "F", "I"],
        "decl": {"stream": {"threshold": SOLVE_THRESHOLD}, "n_min": 3,
                 "primary": {"treatment": "behavioral", "control": "top_k", "metric": "solve_fraction", "min_effect": 0.20},
                 "sealed_queries_digest": sealed.get("manifest_digest")},
    })
    X.decision("D2-013: capability is checked per seed on the sealed queries BEFORE freezing; the comparison uses capable seeds only; the threshold is sealed")
    X.open("cmp2-sfe05")
    wid = X.world("retention", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    X.publish(wid, "future_queries", "cmp2.h3.future_queries.v1", sealed, {"info_kind": "hypothesis"})
    X.receipt["future_queries"] = sealed

    streams = X.pool_map(build_stream, [{"seed": s, "N": a.N, "E": a.E, "G_cap": a.G_cap} for s in a.seeds], "streams_s")
    rows: List[dict] = []
    per_seed = {}
    t0 = time.time()
    for st in streams:
        seed = st["seed"]; stream = st["stream"]; res = st.pop("_res")
        X.reach_row(SOURCE, res, N=a.N, G=st["generations"], E=a.E, regime="E0", seed=seed, arm="stream", kind="treated")
        # capability BEFORE freezing: top-64 by source score on every sealed query
        top = sorted(stream, key=lambda r: -r["score"])[:64]
        cache: Dict[tuple, float] = {}
        ceiling = {}
        for q in sealed["queries"]:
            eps = query_episodes(q, seed)
            best = 0.0
            for r in top:
                v = evaluate(r["manifest"], eps, rng_seed=17)["reward"]; cache[(r["stream_id"], q["query_id"])] = v; best = max(best, v)
            ceiling[q["query_id"]] = round(best, 4)
        capable = max(ceiling.values()) >= SOLVE_THRESHOLD
        cands = to_candidates(stream)
        rep = H3.replay_all(cands, caps, EDGES, a.reserve, seed, attempt_id="%s-a%02d-s%d" % (X.ID.lower(), X.att.number, seed))
        by_id = {r["stream_id"]: r for r in stream}
        frozen = {name: {"digest": pol["archive_digest"], "n": pol["retained_n"], "bytes": pol["bytes"], "bounds": pol["bounds"]} for name, pol in rep["policies"].items()}
        X.publish(wid, "stream_s%d" % seed, "cmp2.h3.stream.v1", {"seed": seed, "stream_manifest": rep["stream"], "n": len(stream), "capable": capable, "ceiling": ceiling},
                  {"info_kind": "artifact", "seed": seed})
        for name in POLICIES:
            X.publish(wid, "archive_%s_s%d" % (name, seed), "cmp2.pop.archive.v1",
                      {"seed": seed, "policy": name, "frozen": frozen[name], "manifests": [by_id[i]["manifest"] for i in rep["policies"][name]["retained_ids"]]},
                      {"info_kind": "artifact", "seed": seed, "policy": name}, maturity=st["maturity"])

        def solves(cand, q):
            key = (cand.stream_id, q["query_id"])
            if key not in cache:
                cache[key] = evaluate(by_id[cand.stream_id]["manifest"], query_episodes(q, seed), rng_seed=17)["reward"]
            return cache[key] >= SOLVE_THRESHOLD
        arch_c = {name: [cands[i] for i in rep["policies"][name]["retained_ids"]] for name in POLICIES}
        scores = H3.score_archives(arch_c, sealed["queries"], solves)
        best = {name: {q["query_id"]: round(max((cache.get((cd.stream_id, q["query_id"]), 0.0) for cd in arch_c[name]), default=0.0), 4) for q in sealed["queries"]} for name in POLICIES}
        per_seed[seed] = {"capable": capable, "ceiling": ceiling, "stream_n": len(stream), "first_solved_gen": st["first_solved_gen"], "generations": st["generations"],
                          "source_score_max": max(r["score"] for r in stream), "maturity": st["maturity"], "frozen": frozen}
        for name in POLICIES:
            sc = scores[name] if isinstance(scores, dict) else scores
            solved = sc.get("solved", sc.get("n_solved")) if isinstance(sc, dict) else None
            frac = sc.get("solve_fraction", sc.get("fraction")) if isinstance(sc, dict) else None
            if frac is None and isinstance(sc, dict):
                per_q = sc.get("per_query") or sc.get("queries") or {}
                solved = sum(1 for v in (per_q.values() if isinstance(per_q, dict) else per_q) if v) if per_q else solved
                frac = (solved or 0) / len(sealed["queries"])
            n_solved = sum(1 for q in sealed["queries"] if best[name][q["query_id"]] >= SOLVE_THRESHOLD)
            rows.append({"arm": name, "seed": seed, "capable": capable, "solve_fraction": round(n_solved / len(sealed["queries"]), 4), "n_solved": n_solved,
                         "solve_fraction_h3": frac, "best_per_query": best[name], "retained_n": frozen[name]["n"], "archive_digest": frozen[name]["digest"],
                         "ceiling_max": max(ceiling.values())})
    X.att.timing("replay_s", t0)
    X.receipt["per_seed"] = per_seed
    capable_seeds = [s for s, v in per_seed.items() if v["capable"]]
    X.receipt["capable_seeds"] = capable_seeds
    t0 = time.time()
    for r in rows:
        X.record(wid, r, {"experiment": X.ID, "policy": r["arm"], "seed": r["seed"], "caps": caps, "archive_digest": r["archive_digest"],
                          "future_queries_digest": sealed.get("manifest_digest"), "capable": r["capable"], "prereg_digest": X.prereg["prereg_digest"]},
                 {k: v for k, v in r.items()}, "SURVIVED" if r["n_solved"] > 0 else "FALSIFIED", (r["arm"], r["seed"]))
    X.att.timing("records_s", t0)
    comp_rows = [r for r in rows if r["capable"]]
    X.receipt["effects"] = {"capable_seeds": capable_seeds,
                            "means_capable": {p: (sum(r["solve_fraction"] for r in comp_rows if r["arm"] == p) / max(1, len(capable_seeds))) for p in POLICIES},
                            "means_all": {p: (sum(r["solve_fraction"] for r in rows if r["arm"] == p) / max(1, len(a.seeds))) for p in POLICIES}}
    meas_extra = {"stream_max_score": max((v["ceiling"] and max(v["ceiling"].values())) or 0.0 for v in per_seed.values()) if per_seed else 0.0}
    X.rows_for_states = comp_rows
    out = X.close(comp_rows if comp_rows else rows, meas_extra=meas_extra)
    X.att.write("rows_all.json", rows)
    print(json.dumps({"effects": X.receipt["effects"], "per_seed": {s: {k: v for k, v in d.items() if k not in ("maturity", "frozen")} for s, d in per_seed.items()}, **out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
