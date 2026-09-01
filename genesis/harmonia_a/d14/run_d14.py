#!/usr/bin/env python
"""D-14 measurement runner, per FREEZE_D14.txt. Deterministic; no LLM.

Issues 10 displacement calls (frozen seeds 900001..900010) + 1 replay
control, fetches genotypes, diffs sites, writes raw pair rows. The
verdict lives in analyze_d14.py, not here.
"""

import hashlib
import json
import os
import ssl
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\ZeusE\d12\client")
from remote import FoundryClient, FoundryHTTPError, TransportIndeterminate

D13_PIN = ("50b5c2327c64bf112c635ca1487f2b1a"
           "8fd64e1b7faade9476d5dfa7215fd492")
BASE = "https://192.168.1.202:8799"
SEEDS = list(range(900001, 900011))
OPERATOR = {"operator_id": "stackvm.point_indel.v1",
            "parameters": {"p_point": 1.0, "p_insert": 0.0,
                           "p_delete": 0.0, "p_dup_block": 0.0,
                           "max_point_sites": 1}}
OUT = Path("results")
JOURNAL = Path("JOURNAL.jsonl")


def journal(entry):
    entry.setdefault("t_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                            time.gmtime()))
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def client():
    ctx = ssl.create_default_context(cafile=os.environ["FOUNDRY_M1_CERT"])
    fc = FoundryClient(BASE, token=os.environ["FOUNDRY_ADMIN_TOKEN"],
                       expected_release_hash=D13_PIN, tls_context=ctx,
                       timeout_s=900.0)
    v = fc.check_release()
    journal({"kind": "gate", "op": "check_release", "result": "match",
             "source_tree_hash": v.get("source_tree_hash"),
             "git_commit": v.get("git_commit"),
             "n_files": v.get("n_files")})
    return fc


CALLS = 0


def sp_call(fc, seed, trace_suffix=""):
    global CALLS
    CALLS += 1
    if CALLS % 25 == 0:
        fc._release_checked = False
        fc.check_release()
    body = {"system_id": "stackvm-v1", "seed": seed,
            "world": {"world_id": "seq_transducer_v1", "horizon": 4,
                      "oracle_kind": "affine_residual"},
            "battery": {"kind": "x_uniform", "seed": seed, "size": 8},
            "n_parents": 32, "mutations_per_parent": 16,
            "max_steps": 2000, "operator": OPERATOR}
    return fc.post("/v0/search-physics/displacement", body,
                   trace_id=f"d14-sp-s{seed}{trace_suffix}")


GENO_CACHE = {}


def genotype(fc, art_id):
    global CALLS
    if art_id in GENO_CACHE:
        return GENO_CACHE[art_id]
    CALLS += 1
    if CALLS % 25 == 0:
        fc._release_checked = False
        fc.check_release()
    g = fc.get(f"/v0/artifacts/{art_id}/genotype")
    GENO_CACHE[art_id] = g
    return g


def geno_bytes(g):
    """Extract the serialized genotype sequence from the response."""
    if isinstance(g, dict):
        for k in ("genotype", "bytes", "code", "program", "data"):
            if k in g:
                g = g[k]
                break
    if isinstance(g, str):
        try:
            return bytes.fromhex(g)
        except ValueError:
            return g.encode("utf-8")
    if isinstance(g, list):
        return bytes(int(x) & 0xFF for x in g)
    raise ValueError(f"unrecognized genotype payload: {type(g)}")


def main():
    OUT.mkdir(exist_ok=True)
    fc = client()
    rows = []
    call_meta = []
    replay_check = None
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = sp_call(fc, seed)
        call_meta.append(dict(seed=seed, metric=r.get("metric"),
                              battery_hash=r.get("battery_hash"),
                              n=r.get("n"),
                              op_hash=r.get("operator_config_hash"),
                              wall_s=round(time.time() - t0, 1)))
        print(f"seed {seed}: n={r.get('n')} metric={r.get('metric')} "
              f"{round(time.time()-t0,1)}s", flush=True)
        if seed == SEEDS[0]:
            r2 = sp_call(fc, seed, trace_suffix="-replay")
            replay_check = dict(
                displacements_equal=(r.get("displacements")
                                     == r2.get("displacements")),
                pair_ids_equal=([p.get("child_id") for p in r["pairs"]]
                                == [p.get("child_id")
                                    for p in r2["pairs"]]))
            print("C1 replay:", replay_check, flush=True)
        for k, p in enumerate(r["pairs"]):
            rows.append(dict(seed=seed, order=k,
                             parent_id=p.get("parent_id"),
                             child_id=p.get("child_id"),
                             displacement=p.get("displacement"),
                             exact_match=p.get("exact_behavior_match"),
                             child_faulted=p.get("child_faulted"),
                             parent_faulted=p.get("parent_faulted",
                                                  False),
                             censored=p.get("censored_from_kgh")))
    # genotype diffs
    handcheck = []
    for row in rows:
        try:
            gp = geno_bytes(genotype(fc, row["parent_id"]))
            gc = geno_bytes(genotype(fc, row["child_id"]))
        except (FoundryHTTPError, TransportIndeterminate) as e:
            row["geno_error"] = str(e)[:120]
            continue
        row["len_parent"], row["len_child"] = len(gp), len(gc)
        if len(gp) == len(gc):
            diff = [i for i in range(len(gp)) if gp[i] != gc[i]]
            row["diff_count"] = len(diff)
            row["site"] = diff[0] if len(diff) == 1 else None
        else:
            row["diff_count"] = -1
            row["site"] = None
        if len(handcheck) < 5 and row["child_id"]:
            h = hashlib.sha256(gc).hexdigest()
            handcheck.append(dict(child_id=row["child_id"],
                                  sha256_of_genotype=h,
                                  match=row["child_id"].endswith(h)))
    with (OUT / "pairs_raw.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    json.dump(dict(calls=call_meta, replay_check=replay_check,
                   handcheck=handcheck,
                   genotype_cache_size=len(GENO_CACHE)),
              open(OUT / "run_meta.json", "w"), indent=1)
    journal({"kind": "measurement_complete", "n_pairs": len(rows),
             "n_genotypes": len(GENO_CACHE),
             "replay_check": replay_check})
    print(f"DONE: {len(rows)} pairs, {len(GENO_CACHE)} genotypes")


if __name__ == "__main__":
    main()
