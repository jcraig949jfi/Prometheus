"""Diomedes — harvest cache with a population-identity proof.

Charter section 9 permits repairing operational inefficiency ONLY on demonstrated identity
with the frozen population: "Hash/count/check equivalence. Do not let an optimization
become an experimental change."

This module caches cycle001_run.harvest() and proves the cache is the frozen population:

  1. DETERMINISM  — harvest() is run twice from scratch; both canonical hashes must match.
                    If harvest were order- or environment-dependent, caching would silently
                    change the population and this check fails loudly.
  2. FIDELITY     — the cache is written, reloaded, re-hashed; the hash must match the live one.
  3. COUNTS       — record counts are compared field by field, not just the aggregate hash,
                    so a mismatch says WHERE it differs.

Canonicalisation preserves ORDER of `parents` (cycle 002 samples per state in iteration
order, so order is experimentally load-bearing) and sorts every mapping/set.

    python roles/Diomedes/harvest_cache.py          # build + verify
    from harvest_cache import load_verified         # use in a runner
"""
import hashlib
import json
import pathlib
import pickle

import cycle001_run as R

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "harvest_cache.pkl"
PROOF = HERE / "harvest_cache_proof.json"


def canonical(bundle):
    """Deterministic JSON form of the whole harvest. Order preserved where load-bearing."""
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = bundle
    obj = {
        "values": [[list(k), sorted(v.items())] for k, v in sorted(values.items())],
        # ORDER-SENSITIVE: cycle 002 iterates parents and samples per state.
        "parents": [[[k, p[k]] for k in sorted(p)] for p in parents],
        "obj_seen": sorted(obj_seen.items()),
        "obj_broke": sorted(obj_broke.items()),
        "obj_cells": [[k, sorted(v)] for k, v in sorted(obj_cells.items())],
        "obj_rels": [[k, sorted(v)] for k, v in sorted(obj_rels.items())],
    }
    return json.dumps(obj, sort_keys=False, separators=(",", ":"), default=str)


def digest(bundle):
    return hashlib.sha256(canonical(bundle).encode("utf-8")).hexdigest()


def counts(bundle):
    values, parents, obj_seen, obj_broke, obj_cells, obj_rels = bundle
    return {
        "n_value_keys": len(values),
        "n_object_value_pairs": sum(len(v) for v in values.values()),
        "n_parents": len(parents),
        "n_obj_seen": len(obj_seen),
        "sum_obj_seen": sum(obj_seen.values()),
        "n_obj_broke": len(obj_broke),
        "sum_obj_broke": sum(obj_broke.values()),
        "n_obj_cells": len(obj_cells),
        "n_obj_rels": len(obj_rels),
    }


def build_and_verify():
    print("harvest run 1/2 (live) ...", flush=True)
    b1 = R.harvest()
    h1, c1 = digest(b1), counts(b1)

    print("harvest run 2/2 (determinism check) ...", flush=True)
    b2 = R.harvest()
    h2, c2 = digest(b2), counts(b2)

    deterministic = (h1 == h2) and (c1 == c2)

    CACHE.write_bytes(pickle.dumps(b1, protocol=pickle.HIGHEST_PROTOCOL))
    b3 = pickle.loads(CACHE.read_bytes())
    h3, c3 = digest(b3), counts(b3)
    faithful = (h3 == h1) and (c3 == c1)

    proof = {
        "purpose": "charter section 9 population-identity proof for the cycle-002 harvest cache",
        "harvest_source": "cycle001_run.harvest (unmodified)",
        "frozen_params": {"MAX_FILES": R.MAX_FILES, "MAX_LINES": R.MAX_LINES,
                          "RELATIONS": sorted(R.RELATIONS), "K": R.K},
        "digest_live_run_1": h1,
        "digest_live_run_2": h2,
        "digest_cache_roundtrip": h3,
        "determinism_pass": deterministic,
        "cache_fidelity_pass": faithful,
        "counts": c1,
        "counts_match_run2": c1 == c2,
        "counts_match_cache": c1 == c3,
        "verdict": "IDENTICAL — cache may be used for the frozen cycle-002 population"
                   if (deterministic and faithful) else
                   "MISMATCH — cache MUST NOT be used; run live",
    }
    PROOF.write_text(json.dumps(proof, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in proof.items() if k != "counts"}, indent=1))
    print("counts:", json.dumps(c1, indent=1))
    return deterministic and faithful


def load_verified():
    """Return the cached harvest, refusing if the identity proof is absent or failed."""
    if not (CACHE.exists() and PROOF.exists()):
        raise RuntimeError("no verified cache; run harvest_cache.py first")
    p = json.loads(PROOF.read_text(encoding="utf-8"))
    if not (p.get("determinism_pass") and p.get("cache_fidelity_pass")):
        raise RuntimeError(f"cache identity proof FAILED: {p.get('verdict')}")
    b = pickle.loads(CACHE.read_bytes())
    if digest(b) != p["digest_live_run_1"]:
        raise RuntimeError("cache digest drifted from its proof; refusing to use it")
    return b


if __name__ == "__main__":
    ok = build_and_verify()
    raise SystemExit(0 if ok else 1)
