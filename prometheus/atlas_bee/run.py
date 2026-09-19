"""atlas_bee.run -- freeze, execute natively in BEE, replay and compare one or all adaptations (Phases 4-6).

  python -m prometheus.atlas_bee.run <id|all> [--workroot DIR]

For each adaptation it writes, into roles/Bellerophon/atlas_bee/:
  PREREG_<id>.json   the frozen, hashed preregistration -- written BEFORE the run (Phase 4)
  RESULT_<id>.json   observed result + replay verification + Phase-6 comparison (Phases 5-6)

A repair is a NEW adaptation id, never an edit of a frozen prereg. The workroot holds the BEE receipts (kept for
provenance and replay); only the two JSON summaries land in the packet.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import time

from prometheus.atlas_bee.harness import PACKET, freeze_and_write, replay_all


def _registry():
    reg = {}
    import importlib
    for aid, mod, cls in (("a1", "a1", "A1"), ("a2", "a2", "A2"), ("a3", "a3", "A3"),
                          ("a4", "a4", "A4"), ("a5", "a5", "A5"), ("a6", "a6", "A6")):
        try:
            m = importlib.import_module("prometheus.atlas_bee." + mod)
            reg[aid] = getattr(m, cls)
        except (ImportError, AttributeError):
            pass
    return reg


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_one(aid: str, workroot: pathlib.Path) -> dict:
    cls = _registry()[aid]
    ad = cls()
    rec = freeze_and_write(ad)                                   # Phase 4: freeze BEFORE the run
    t0 = time.time()
    run = ad.run(workroot / aid)                                 # Phase 5: execute natively in BEE
    replay = replay_all([pathlib.Path(p) for p in run.get("receipt_files", [])])
    comparison = ad.compare(run["observed"])                     # Phase 6: compare
    result = {"adaptation_id": aid, "source": ad.source, "utc": _utc(), "wall_s": round(time.time() - t0, 1),
              "prereg_sha256": rec["freeze"]["sha256"], "manifest_counts": rec["prereg"]["manifest"]["counts"],
              "observed": run["observed"], "notes": run.get("notes", []),
              "replay": replay, "replay_ok": all((r.get("status") in ("OK", "NO_SUMMARY")) and not r.get("divergent") for r in replay),
              "comparison": comparison}
    (PACKET / ("RESULT_%s.json" % aid)).write_text(json.dumps(result, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("which", help="an adaptation id (a1..a6) or 'all'")
    ap.add_argument("--workroot", default=None, help="dir for BEE receipts (default: a temp dir)")
    a = ap.parse_args(argv)
    reg = _registry()
    ids = sorted(reg) if a.which == "all" else [a.which]
    workroot = pathlib.Path(a.workroot) if a.workroot else pathlib.Path(__import__("tempfile").mkdtemp(prefix="atlas_bee_"))
    workroot.mkdir(parents=True, exist_ok=True)
    for aid in ids:
        if aid not in reg:
            print(json.dumps({"adaptation_id": aid, "status": "NOT_BUILT"})); continue
        r = run_one(aid, workroot)
        print(json.dumps({"adaptation_id": aid, "verdict": r["comparison"]["verdict"], "wall_s": r["wall_s"],
                          "replay_ok": r["replay_ok"], "prereg_sha256": r["prereg_sha256"][:12]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
