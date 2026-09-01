"""
Anti-cheat / leakage battery (D7 section 47).  Fail closed.
"""

from __future__ import annotations
from substrate import sha


def audit(proof_kit, store, S, T):
    """Return dict of checks; all must be True."""
    checks = {}
    world = proof_kit["world"]

    # 1) proof endpoints do not appear as data in the relational history
    #    (history is per-artifact marginal/pair signatures over dev worlds only)
    endpoint_tuples = {tuple(S), tuple(T)}
    for (s, t) in proof_kit["pairs"]["family"]:
        endpoint_tuples.add(tuple(t))
    blob = str(store["marginal"]) + str(store["pair"])
    checks["no_endpoint_bytes_in_history"] = not any(str(list(e)) in blob for e in endpoint_tuples)

    # 2) dev worlds are not the proof world (endpoint-exclusion by construction)
    dev_fps = set(store["dev_fingerprints"])
    checks["dev_worlds_exclude_proof"] = world.fingerprint() not in dev_fps

    # 3) history carries no task-family / target-coordinate labels (only coord ints,
    #    frozen flag, costs, emergent-coord ints)
    allowed_marg = {"coords", "frozen", "cost"}
    allowed_pair = {"emergent", "changed", "cost"}
    checks["history_schema_is_machine_native"] = (
        all(set(v.keys()) <= allowed_marg for v in store["marginal"].values())
        and all(set(v.keys()) <= allowed_pair for v in store["pair"].values()))

    # 4) no oracle/proof-certificate fields leaked into the store
    forbidden = ["barrier", "reachable", "invariant", "opens", "target", "cut", "R_B"]
    checks["no_oracle_fields"] = not any(f in blob for f in forbidden)

    # 5) the store references only real artifact ids
    ids = set(proof_kit["hoard"].keys())
    pair_ids = set()
    for k in store["pair"]:
        a, b = k.split("|")
        pair_ids.add(a); pair_ids.add(b)
    checks["store_ids_are_real"] = (set(store["marginal"].keys()) <= ids) and (pair_ids <= ids)

    ok = all(checks.values())
    return {"pass": ok, "checks": checks}


def symmetry_assertion(cfg_z0, cfg_z1):
    """Confirm Z0 and Z1 share grammar/hoard/verifier/budget; only priors differ."""
    same = (cfg_z0["grammar"] == cfg_z1["grammar"]
            and cfg_z0["hoard_fp"] == cfg_z1["hoard_fp"]
            and cfg_z0["budget"] == cfg_z1["budget"]
            and cfg_z0["verifier"] == cfg_z1["verifier"])
    return {"pass": same,
            "note": "Z0/Z1 identical except the proposal prior (art_w)"}
