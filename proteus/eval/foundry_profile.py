"""proteus.foundry_profile.v1 -- the regime-level identity of a generation-0 foundry + search kernel.

Why (point release P1 / PROTEUS-29, repair order s3, 2026-09-17). Campaign 2's L2-017 showed the
generation-0 regime is part of the experimental regime, and Archaeon minted its own id for it
(`archaeon/wse/reachability.foundry_id`: "instr<lo>-<hi>:<8 hex>", a sha256 over the foundry
manifest minus seed/n). That string omits the runtime and the grammar, which the same receipts
carry as separate fields. Proteus's own `foundry_identity(fm)` hashes seed and n as well, so it
names a POPULATION, not a regime. This module supplies the missing object:

    profile = regime (foundry manifest minus seed/n)
            + runtime_hash + affordance_hash            (what the genome MEANS)
            + grammar_version + grammar_hash + weights  (how the search MOVES)
            + kernel_qualification                      (the registry's statement about the kernel)

and a deterministic id "pfp1:<16 hex>" over its canonical JSON. A different runtime, grammar,
weight vector or regime is a different profile; seed and n are not part of it. Archaeon's string
is reproduced EXACTLY (same rule, same bytes) so every C1-C3 receipt joins to a catalog row
without re-rendering anything.

Grammar mass profiles (Round 2 lane 3) are NOT minted here; the identity carries `grammar_weights`
so that, when a G-/G+ grammar version exists, it is a distinct profile by construction (see
test_foundry_profile.py::test_different_grammar_weights_cannot_alias). Frozen v0.4 is the only
grammar this catalog names today.

Nothing in this module reads a world, scores an organism or changes the runtime.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from proteus.foundry import affordances as A  # noqa: E402
from proteus.foundry import grammar as G  # noqa: E402
from proteus.foundry.generate import DEFAULT_FOUNDRY_MANIFEST, FOUNDRY_SCHEMA, validate_foundry_manifest  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, canonical_json, hash_obj  # noqa: E402

PROFILE_SCHEMA = "proteus.foundry_profile.v1"
ID_PREFIX = "pfp1:"
ID_HEX = 16
ARCHAEON_SCHEME = "archaeon.wse.reachability.foundry_id.v1"
REGIME_EXCLUDED = ("seed", "n")

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "proteus" / "integration" / "PLAYER_REGISTRY.json"
CATALOG_PATH = ROOT / "proteus" / "eval" / "FOUNDRY_PROFILE_CATALOG.json"


# ------------------------------------------------------------------ regime
def regime_of(fm: dict) -> dict:
    """The foundry manifest minus seed and n, validated as a foundry manifest (with seed=0, n=0)."""
    r = {k: v for k, v in fm.items() if k not in REGIME_EXCLUDED}
    probe = dict(r, seed=0, n=0)
    validate_foundry_manifest(probe)
    return json.loads(canonical_json(r))


def archaeon_regime_id(regime: dict) -> str:
    """EXACT reproduction of archaeon/wse/reachability.foundry_id over a regime dict:
    'instr<lo>-<hi>:<8 hex>' with sha256 over json.dumps(regime, sort_keys=True) -- the default
    separators (', ', ': '), NOT Proteus's compact canonical form. Byte-for-byte the same rule so
    every C1-C3 receipt joins to a catalog row; never re-rendered."""
    f = {k: v for k, v in regime.items() if k not in REGIME_EXCLUDED}
    lo, hi = f.get("genome_instr_range", [0, 0])
    return "instr%d-%d:%s" % (lo, hi, hashlib.sha256(json.dumps(f, sort_keys=True).encode()).hexdigest()[:8])


# ------------------------------------------------------------------ kernel qualification
def registry_kernel_qualification(registry_path: Path = REGISTRY_PATH) -> dict:
    """The frozen registry's own statement about the mutation kernel, read from the committed
    registry (never typed by hand here) so the profile carries what the evidence says."""
    r = json.loads(registry_path.read_text(encoding="utf-8"))
    sq = r["source_qualification"]
    return {
        "registry_id": r["registry_id"],
        "mutation_neutrality": sq["mutation_neutrality"],
        "mutation_current_source": sq["mutation_current_source"],
        "operational_significance": sq["operational_significance"],
        "permitted_use": sq["permitted_use"],
        "prohibited_use": sq["prohibited_use"],
    }


# ------------------------------------------------------------------ the profile
def grammar_identity(version: str = G.GRAMMAR_VERSION, ghash: str = G.GRAMMAR_HASH,
                     names=G.NAMES, weights=G.WEIGHTS) -> dict:
    """The grammar as a search kernel: its version, its hash, and its weight vector by name.
    Weights are rounded to 12 places so the identity does not depend on float formatting."""
    if len(names) != len(weights):
        raise ValueError("names/weights length mismatch")
    return {
        "grammar_version": version,
        "grammar_hash": ghash,
        "grammar_weights": {n: round(float(w), 12) for n, w in zip(names, weights)},
    }


def build_profile(fm: dict, *, grammar: dict | None = None, kernel_qualification: dict | None = None,
                  runtime_hash: str = RUNTIME_HASH, affordance_hash: str = A.AFFORDANCE_HASH) -> dict:
    regime = regime_of(fm)
    body = {
        "schema_version": PROFILE_SCHEMA,
        "regime": regime,
        "runtime_hash": runtime_hash,
        "affordance_hash": affordance_hash,
        "grammar": grammar or grammar_identity(),
        "kernel_qualification": kernel_qualification or registry_kernel_qualification(),
    }
    full = hash_obj(body)
    return {
        **body,
        "profile_id": ID_PREFIX + full[:ID_HEX],
        "profile_sha256": full,
        "archaeon_regime_id": archaeon_regime_id(regime),
        "archaeon_regime_scheme": ARCHAEON_SCHEME,
    }


def verify_profile(p: dict) -> None:
    """Recompute the id and the Archaeon string from the record's own fields; raise on mismatch."""
    body = {k: p[k] for k in ("schema_version", "regime", "runtime_hash", "affordance_hash",
                              "grammar", "kernel_qualification")}
    if body["schema_version"] != PROFILE_SCHEMA:
        raise ValueError("schema mismatch")
    full = hash_obj(body)
    if p["profile_sha256"] != full or p["profile_id"] != ID_PREFIX + full[:ID_HEX]:
        raise ValueError("profile id does not recompute")
    if p["archaeon_regime_id"] != archaeon_regime_id(p["regime"]):
        raise ValueError("archaeon regime id does not recompute")
    validate_foundry_manifest(dict(p["regime"], seed=0, n=0))


# ------------------------------------------------------------------ the catalog: what has RUN
# The three regimes are the committed dicts of the consumers, restated here field by field (not
# imported: proteus must not import archaeon). The Archaeon strings recorded in the receipts are
# asserted in test_foundry_profile.py against the recomputation.
_BASE = {
    "schema_version": FOUNDRY_SCHEMA,
    "n_regs_range": [2, 16],
    "tape_words_choices": [16, 32, 64, 128, 256],
    "code_writable_weights": [1, 1],
    "persist_weights": [1, 1, 1, 1],
    "tick_budget_choices": [16, 64, 256],
    "out_cap_choices": [1, 4],
}

KNOWN_REGIMES = (
    {
        "name": "c1_c2_c3_instr1_16",
        "regime": dict(_BASE, genome_instr_range=[1, 16]),
        "ran_in": ["campaign1 FOUNDRY_C1 (archaeon/campaign1/sfe01.py)",
                   "campaign2 FOUNDRY_C2 (archaeon/campaign2/c2base.py; identical dict)",
                   "campaign3 (archaeon/campaign3/c3base.py imports FOUNDRY_C2)"],
        "recorded_archaeon_id": "instr1-16:6528b9dc",
    },
    {
        "name": "c2_default_instr1_32",
        "regime": dict(_BASE, genome_instr_range=[1, 32]),
        "ran_in": ["campaign2 W1_d1 8-bit rows (archaeon/wse/evolve.py FOUNDRY default)"],
        "recorded_archaeon_id": "instr1-32:199105b4",
    },
    {
        "name": "registry_instr1_64",
        "regime": {k: v for k, v in DEFAULT_FOUNDRY_MANIFEST.items() if k not in REGIME_EXCLUDED},
        "ran_in": ["the 64-specimen frozen registry (proteus/integration/PLAYER_REGISTRY.json build)"],
        "recorded_archaeon_id": "instr1-64:97ce0af8",
    },
)


def build_catalog() -> dict:
    rows = []
    for k in KNOWN_REGIMES:
        p = build_profile(dict(k["regime"], seed=0, n=0))
        rows.append({"name": k["name"], "ran_in": k["ran_in"],
                     "recorded_archaeon_id": k["recorded_archaeon_id"], **p})
    ids = [r["profile_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("catalog profiles alias")
    doc = {
        "schema_version": "proteus.foundry_profile_catalog.v1",
        "currency": "2026-09-17",
        "runtime_hash": RUNTIME_HASH,
        "affordance_hash": A.AFFORDANCE_HASH,
        "grammar": grammar_identity(),
        "kernel_qualification": registry_kernel_qualification(),
        "note": ("Every profile that has RUN under the frozen runtime/grammar. Archaeon's strings are "
                 "reproduced by the same rule and stay verbatim in every receipt; this catalog is the "
                 "join, not a replacement. Grammar mass profiles (Round 2 lane 3) are not minted here."),
        "profiles": rows,
    }
    doc["catalog_id"] = hash_obj({k: v for k, v in doc.items() if k != "catalog_id"})
    return doc


def write_catalog(path: Path = CATALOG_PATH) -> dict:
    doc = build_catalog()
    path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    doc = write_catalog()
    print(CATALOG_PATH)
    print("catalog_id", doc["catalog_id"][:16], "| runtime", RUNTIME_HASH[:12], "| grammar",
          doc["grammar"]["grammar_version"], doc["grammar"]["grammar_hash"][:12])
    for r in doc["profiles"]:
        ok = r["archaeon_regime_id"] == r["recorded_archaeon_id"]
        print("  %-24s %s  archaeon %s  recorded %s  %s" % (
            r["name"], r["profile_id"], r["archaeon_regime_id"], r["recorded_archaeon_id"],
            "MATCH" if ok else "MISMATCH"))
    return 0 if all(r["archaeon_regime_id"] == r["recorded_archaeon_id"] for r in doc["profiles"]) else 1


if __name__ == "__main__":
    sys.exit(main())
