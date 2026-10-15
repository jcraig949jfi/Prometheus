"""Completeness-manifest TEMPLATE for the parts-suitability draft (PREREG_DRAFT_PARTS_SUITABILITY.md s8).

    python -m rso.gen5.ananke.eval.prereg_template [--n 8] [--out qual/MANIFEST_TEMPLATE_parts_suitability.json]

One shard per (arm, cell); seeds = the idx list; one row per search. Digests are placeholders: the OWNER fills n, G and
source hashes at sign-off and seals; the Observatory pins the sealed sha256 before reading a target row. The template is
built with rso.completeness.manifest.build, so its shape is the verifier's.
"""
from __future__ import annotations

import argparse
import json
import os

from rso.completeness import manifest as MF

from . import owner

ARMS = ("CONTROL", "REUSE", "SHAM_MISMATCH", "SHAM_SCRAMBLED", "COMPUTE_MATCHED", "CONSTRUCTED_POSITIVE")
TBF = "TO_BE_FILLED_AT_FREEZE"


def template(n_per_cell: int = 8) -> dict:
    cells = [c["cell_id"] for c in owner.cells()]          # GATE is admitted at all four C4 cells
    shards = []
    for arm in ARMS:
        for cid in cells:
            shards.append({"id": f"{arm}.{cid}", "seeds": list(range(n_per_cell)), "arm_counts": {f"{arm}|{cid}": n_per_cell},
                           "rows": n_per_cell, "rows_sha256": TBF, "meta_sha256": TBF})
    return MF.build("DRAFT parts-suitability GATE ladder (owner sign-off required; NOT FROZEN)", ARMS, shards,
                    sources={"owner_runner": TBF, "owner_half_worlds": TBF, "library_halves": TBF,
                             "rso/gen5/ananke/eval/access.py": TBF, "rso/gen5/ananke/eval/mechanics.py": TBF},
                    row_key_fields=("arm", "cell"), seed_field="idx")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "qual", "MANIFEST_TEMPLATE_parts_suitability.json"))
    x = ap.parse_args(argv)
    m = template(x.n)
    with open(x.out, "w", newline="\n") as f:
        json.dump(m, f, indent=1, sort_keys=True)
    print(x.out, len(m["shards"]), "shards", m["manifest_sha256"][:12], "(template seal; re-sealed at sign-off)")


if __name__ == "__main__":
    main()
