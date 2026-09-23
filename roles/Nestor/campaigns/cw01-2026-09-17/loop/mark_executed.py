"""Append-only 'executed' amendments: a candidate that has run under a frozen tranche is never
re-selected unchanged (replication must be its own candidate). Reads PRIORITY_*.json tags and
the RESULT.json files that exist."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

PERT = HERE / "PERTURBATIONS.jsonl"
TRANCHES = {"2026-09-18": "cw01-loop1", "ARCH4_2026-09-18": "cw01-arch4"}


def main(extra=None):
    done = set()
    for l in PERT.read_text(encoding="utf-8").splitlines():
        if l.strip():
            d = json.loads(l)
            if d.get("amend") and d.get("executed_in"):
                done.add(d["id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    tr = list(TRANCHES.items()) + list(extra or [])      # pairs, not a dict: one tag may span directories (D077)
    added = []
    with PERT.open("a", encoding="utf-8") as fh:
        for tag, expdir in tr:
            p = HERE / ("PRIORITY_%s.json" % tag)
            if not p.exists():
                continue
            pr = json.loads(p.read_text(encoding="utf-8"))
            for c in pr["frozen_top_ten"]:
                rp = HERE.parent / "experiments" / expdir / c["id"] / "RESULT.json"
                if rp.exists() and c["id"] not in done:
                    fh.write(json.dumps({"id": c["id"], "amend": True, "executed_in": tag, "result": str(rp.relative_to(HERE.parent)),
                                         "recorded": ts}, ensure_ascii=True) + "\n")
                    done.add(c["id"])
                    added.append(c["id"])
    RS.require_ascii_safe(PERT)
    print("marked executed:", added)


if __name__ == "__main__":
    main([tuple(a.split("=", 1)) for a in sys.argv[1:]] if len(sys.argv) > 1 else None)
