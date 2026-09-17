"""The Campaign 4 observation surface, frozen (pre-Campaign-4 repair order
s4/s7, 2026-09-17). One function computes the identities from the CODE;
docs/point_release/CAMPAIGN4_FROZEN_SURFACE.json holds the pinned copy;
tests/test_frozen_surface.py asserts they are equal. Changing any of these
during Campaign 4 requires a named defect, preserved evidence, an explicit
version transition and proof of non-retroactivity (order s7); the test is
what makes that a decision rather than a drift.

    python -m ew.frozen_surface           # print the live identities
    python -m ew.frozen_surface --write   # (re)write the pinned file
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

PINNED = HERE / "docs" / "point_release" / "CAMPAIGN4_FROZEN_SURFACE.json"
INBOX_CONTRACT = "pew.events.v1"


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


def live():
    from ew import SCHEMA_VERSION, FOSSIL_CONTRACT_VERSION
    from ew import campaign_ingest as ci
    from ew import projections as pj
    defs = {f"{k[0]}/{k[1]}": {"thresholds": v["thresholds"], "status": v.get("status", "BUILT"),
                               "definition_sha256": hashlib.sha256(v["definition"].encode()).hexdigest()}
            for k, v in pj.DEFINITIONS.items()}
    return {
        "frozen_for": "campaign 4",
        "schema_version": SCHEMA_VERSION,
        "fossil_contract": FOSSIL_CONTRACT_VERSION,
        "migrations": ["014", "015"],
        "reader_version": ci.READER_VERSION,
        "ingestion_contract": ci.CONTRACT_VERSION,
        "foundry_profile_scheme": ci.FOUNDRY_SCHEME,
        "campaign_seed_map": {str(k): v for k, v in ci.SEED_TO_CAMPAIGN.items()},
        "shared_tables": [list(t) for t in ci.SHARED_TABLES],
        "design_factor_keys": list(ci.DESIGN_FACTOR_KEYS),
        "projection_builder": pj.BUILDER_VERSION,
        "projection_thresholds": {"FOOTHOLD_MIN": pj.FOOTHOLD_MIN, "SHELF_MIN": pj.SHELF_MIN, "SUMMIT_MIN": pj.SUMMIT_MIN},
        "projections": defs,
        "campaign4_projection_versions": {"reach_level": "v1", "corridor_edge": "v1"},
        "superseded_projection_versions": {"reach_level": ["v0"]},
        "inbox_contract": INBOX_CONTRACT,
        "envelope_columns": ["campaign_id", "harness_id", "execution_id", "design_id", "design_kind", "attempt_id",
                             "attempt_number", "resumed_from_attempt", "step_id", "foundry_profile", "schedule_id",
                             "rng_identity", "world_id", "engine_instance_id", "engine_source_hash", "logical_time/generation",
                             "origin_kind"],
        "origin_kind_values": ["producer", "reconstructed", "vivarium"],
        "absent_value_rule": "UNKNOWN = an owner exists and the value was not supplied; NULL = not applicable; "
                             "the envelope's UNKNOWN never shares a column with a measured indeterminate value",
    }


def digest(d):
    return "sha256:" + hashlib.sha256(canon(d).encode()).hexdigest()


DIGEST_RULE = ("surface_digest = 'sha256:' + sha256( json.dumps(D, sort_keys=True, separators=(',', ':'), "
               "default=str) ) where D is this object WITHOUT the keys surface_digest and surface_digest_rule; "
               "a third party recomputes it with `python -m ew.frozen_surface` or by that one line. The file's own "
               "sha256 is ALSO a valid identity of this pin (Archaeon #370 Q1) and changes whenever the digest does.")


def main():
    d = live()
    d["surface_digest_rule"] = DIGEST_RULE
    d["surface_digest"] = digest({k: v for k, v in d.items() if k not in ("surface_digest", "surface_digest_rule")})
    if "--write" in sys.argv:
        PINNED.write_text(json.dumps(d, indent=1), encoding="utf-8")
        print("wrote", PINNED)
    print(json.dumps(d, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
