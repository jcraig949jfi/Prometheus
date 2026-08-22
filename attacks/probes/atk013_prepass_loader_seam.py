#!/usr/bin/env python
"""ATK-013 probe — writer/reader schema seam in the probe pre-pass ledger.

Registry entry: attacks/REGISTRY.md ATK-013.
Origin: found by Techne's loop (HITL #78, cycles 025-042, unruled for 17 cycles),
root-caused at cycle 042, realized blast radius confirmed ZERO at cycle 048 (the
campaign halted at P1; P3 never constructed the arms). Independently reproduced by
execution here 2026-08-22.

The defect: `campaign.py` writes pre-pass rows with the replicate index nested as
`key: [rep, uid]`. `ergon/probe/assemble.py:load_prepass` filters on a TOP-LEVEL
`rep` field that the campaign writer never emits, so every row is discarded. The
downstream failure is silent and inverted in meaning: the F-prom-retrieved arm ships
"(no residue recorded at this distance)" and the census reports the stratum
UNSUPPLIED — i.e. the experiment reads "the substrate recorded nothing" when the
truth is "the loader could not read the ledger".

Why it matters even at zero realized blast radius: Tier B is precisely a campaign
that reaches P3. Run this before any campaign advances past P1.

Usage:
    PYTHONPATH=. python attacks/probes/atk013_prepass_loader_seam.py

Exit 0 = defect ABSENT (loader reads what the writer wrote).
Exit 1 = defect PRESENT (rows on disk, zero accepted).
Exit 2 = INDETERMINATE (no ledger to test — never read as a pass).
"""

import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "ergon" / "probe" / "ledgers" / "campaign"


def main() -> int:
    ledgers = sorted(LEDGER_DIR.glob("p1_prepass*.jsonl"))
    if not ledgers:
        print(f"INDETERMINATE: no p1_prepass*.jsonl under {LEDGER_DIR}")
        print("A missing ledger is not a passing probe — re-run after a pre-pass.")
        return 2

    sys.path.insert(0, str(ROOT))
    from ergon.probe.assemble import load_prepass

    total_on_disk = total_accepted = total_rep1_by_writer = 0
    for path in ledgers:
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        rep1_by_writer = sum(
            1 for d in rows
            if isinstance(d.get("key"), list) and len(d["key"]) == 2 and d["key"][0] == 1
        )
        accepted = len(load_prepass(path))
        total_on_disk += len(rows)
        total_accepted += accepted
        total_rep1_by_writer += rep1_by_writer
        print(f"{path.name}: on_disk={len(rows)} rep1_by_writer_schema={rep1_by_writer} "
              f"loader_accepted={accepted}")

    print(f"\nTOTAL on_disk={total_on_disk} rep1_by_writer={total_rep1_by_writer} "
          f"loader_accepted={total_accepted}")

    if total_rep1_by_writer > 0 and total_accepted == 0:
        print("\nDEFECT PRESENT — the loader drops 100% of the writer's rep-1 rows.")
        print("Do not advance any campaign to P3 until the seam is repaired by its owner "
              "(Ergon). Silent absence is indistinguishable from unreadability.")
        return 1

    print("\nDefect ABSENT on this ledger set.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
