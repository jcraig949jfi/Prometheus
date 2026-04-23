"""Initialize ANCHOR_PROGRESS_LEDGER sidecar for FRAME_INCOMPATIBILITY_TEST@v2.

Forward-path deployment of the ANCHOR_PROGRESS_LEDGER Tier 3 candidate
(CANDIDATES.md; 2 authors + auditor 3rd attestation). Populates the Redis
HASH symbols:FRAME_INCOMPATIBILITY_TEST:anchor_progress with the 11 catalogs
from v2 section 2.E worked-examples table.

Anchor data source: FRAME_INCOMPATIBILITY_TEST_v2_DRAFT.md section 2.E
+ sync-message evidence at specific mids.
"""
import sys, io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from agora.symbols.anchor_progress import update_anchor_progress, export_progress_md

NAME = "FRAME_INCOMPATIBILITY_TEST"

# One dict per anchor: anchor_id -> {resolver, cross_resolvers, tier, fp_apps}
# Derived from v2 2.E worked-examples table + sync-stream evidence.
ANCHORS = {
    "lehmer": {
        "resolver": "Harmonia_M2_sessionC",
        "cross_resolvers": ["Harmonia_M2_sessionB"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "collatz": {
        "resolver": "Harmonia_M2_sessionC",
        "cross_resolvers": ["Harmonia_M2_sessionB"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "zaremba": {
        "resolver": "Harmonia_M2_sessionB",
        "cross_resolvers": ["Harmonia_M2_sessionC", "Harmonia_M2_sessionA"],
        "tier": "coordinate_invariant",
        "fp_apps": ["zaremba_live_Y_consumed_auditor_1776901907841"],
    },
    "brauer_siegel": {
        "resolver": "Harmonia_M2_sessionC",
        "cross_resolvers": ["Harmonia_M2_sessionB"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "knot_concordance": {
        "resolver": "Harmonia_M2_sessionB",
        "cross_resolvers": ["Harmonia_M2_sessionC"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "ulam_spiral": {
        "resolver": "Harmonia_M2_sessionB",
        "cross_resolvers": ["Harmonia_M2_sessionC"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "hilbert_polya": {
        "resolver": "Harmonia_M2_sessionC",
        "cross_resolvers": ["Harmonia_M2_sessionB"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "p_vs_np": {
        "resolver": "Harmonia_M2_sessionC",
        "cross_resolvers": ["Harmonia_M2_sessionB"],
        "tier": "surviving_candidate",
        "fp_apps": [],
    },
    "irrationality_paradox": {
        "resolver": "Harmonia_M2_sessionA",
        "cross_resolvers": ["Harmonia_M2_sessionC"],
        "tier": "shadow_contested",
        "fp_apps": ["forward_path_1st_new_catalog_sessionA_1776907566863"],
    },
    "knot_nf_lens_mismatch": {
        "resolver": "Harmonia_M2_sessionC",
        "cross_resolvers": ["Harmonia_M2_sessionA", "Harmonia_M2_sessionB"],
        "tier": "coordinate_invariant",
        "fp_apps": ["forward_path_2nd_new_catalog_sessionC_1776907566863"],
    },
    "drum_shape": {
        "resolver": "Harmonia_M2_sessionA",
        "cross_resolvers": ["Harmonia_M2_sessionB", "Harmonia_M2_sessionC"],
        "tier": "surviving_candidate",
        "fp_apps": ["forward_path_3rd_new_catalog_sessionA_1776909057747"],
    },
}


def main():
    print(f"Initializing anchor_progress for {NAME} — {len(ANCHORS)} anchors")
    print()
    for anchor_id, data in ANCHORS.items():
        rec = update_anchor_progress(
            NAME, anchor_id,
            resolver=data["resolver"],
            tier=data["tier"],
            rationale="v2 promotion-time state from 2.E table",
        )
        for xr in data["cross_resolvers"]:
            update_anchor_progress(NAME, anchor_id, cross_resolver_add=xr)
        for fp in data["fp_apps"]:
            update_anchor_progress(NAME, anchor_id, forward_path_application_add=fp)
        print(f"  {anchor_id:28s} tier={data['tier']:22s} xr={len(data['cross_resolvers'])} fp={len(data['fp_apps'])}")
    print()
    print("=== MD EXPORT SAMPLE (first 2 anchors) ===")
    md = export_progress_md(NAME)
    lines = md.splitlines()
    # print header + first 2 anchor blocks
    preview = []
    anchor_count = 0
    for line in lines:
        if line.startswith("## "):
            anchor_count += 1
        if anchor_count > 2:
            preview.append("... (truncated, see full export)")
            break
        preview.append(line)
    print("\n".join(preview))

if __name__ == "__main__":
    main()
