"""Does organism_id pin EXECUTION, or only BYTES? Measured.

Directive section 3. organism_id = sha256(canonical_json(manifest)). The manifest carries
schema_version but NOT runtime_hash and NOT affordance_hash. The runtime decodes every
instruction as `op = word mod N_OPCODES`, so N_OPCODES is a divisor of the whole program's
meaning and it lives in the affordance table, outside the hashed bytes.

Consequence to test: if the affordance table gains ONE opcode (25 -> 26), the identical manifest
bytes -- identical organism_id -- decode to a different program. This quantifies how much of each
specimen re-decodes, i.e. how far "same id" is from "same player".

entry_id is also checked: it covers the identity block (runtime_hash, affordance_hash), so the
REGISTRY does pin the interpretation even though the organism_id does not.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry.affordances import AFFORDANCE_HASH, MNEMONIC, N_OPCODES
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj
from proteus.integration.registry import compute_entry_id, intrinsic_view

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(HERE, "PLAYER_REGISTRY.json")
IW = 4


def main() -> int:
    reg = json.load(open(REG, encoding="utf-8"))
    entries = reg["entries"]

    # 1. is runtime/affordance identity an input to organism_id?
    m0 = entries[0]["manifest"]
    manifest_keys = sorted(m0.keys())
    organism_id_inputs = {
        "hashed_bytes": "canonical_json(manifest)",
        "manifest_keys": manifest_keys,
        "includes_runtime_hash": "runtime_hash" in m0,
        "includes_affordance_hash": "affordance_hash" in m0,
        "recomputed_matches": hash_obj(m0) == entries[0]["organism_id"],
    }

    # 2. does entry_id cover the interpretation?
    iv = intrinsic_view(entries[0])
    entry_id_inputs = {
        "intrinsic_view_keys": sorted(iv.keys()),
        "identity_block": sorted(iv["identity"].keys()),
        "covers_runtime_hash": iv["identity"].get("runtime_hash") == RUNTIME_HASH,
        "covers_affordance_hash": iv["identity"].get("affordance_hash") == AFFORDANCE_HASH,
        "recomputed_matches": compute_entry_id(entries[0]) == entries[0]["entry_id"],
    }

    # 3. how much of each specimen re-decodes if the table gains one opcode?
    redecoded, totals = [], []
    fully_stable = 0
    for e in entries:
        g = e["manifest"]["genome"]
        n = len(g) // IW
        changed = sum(1 for i in range(0, len(g), IW)
                      if g[i] % N_OPCODES != g[i] % (N_OPCODES + 1))
        redecoded.append(changed)
        totals.append(n)
        if changed == 0:
            fully_stable += 1
    frac = [c / t for c, t in zip(redecoded, totals)]
    frac_sorted = sorted(frac)

    out = {
        "organism_id": organism_id_inputs,
        "entry_id": entry_id_inputs,
        "affordance_change_probe": {
            "probe": "N_OPCODES 25 -> 26 (one opcode appended to the table)",
            "organism_id_changes": False,
            "instructions_total": sum(totals),
            "instructions_that_redecode": sum(redecoded),
            "fraction_redecoding_overall": round(sum(redecoded) / sum(totals), 4),
            "per_organism_fraction_min": round(frac_sorted[0], 4),
            "per_organism_fraction_median": round(frac_sorted[len(frac_sorted) // 2], 4),
            "per_organism_fraction_max": round(frac_sorted[-1], 4),
            "organisms_completely_unaffected": fully_stable,
            "organisms_total": len(entries),
        },
        "verdict": (
            "organism_id pins BYTES, not EXECUTION. The registry entry_id pins execution because "
            "it covers runtime_hash and affordance_hash. Therefore a specimen quoted by "
            "organism_id alone is under-specified for replay; quoted by (organism_id, entry_id) "
            "or (organism_id, runtime_hash, affordance_hash) it is exact."),
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
