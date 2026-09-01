"""Daily wall ranking (charter §11). Produces TOP_READY_MINTS.txt / .json. Not ranked by excitement."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hephaestus.src import packet as P  # noqa: E402

DIMS = ["evidence_current_set_cannot_express", "frequency_across_worlds", "number_of_independent_origins",
        "potential_cross_world_utility", "quality_of_reproducer", "quality_of_falsifier",
        "cheap_search_exhaustion", "minimality_of_required_extension"]


def score(p: dict) -> dict:
    d = dict(p["PRIORITY"].get("dimensions") or {})
    ce = p.get("CLOSURE_EVIDENCE") or []
    d.setdefault("evidence_current_set_cannot_express",
                 1.0 if ce and isinstance(ce[0], dict) and ce[0].get("registry_ops_that_commit_comparison") == 0 else (0.5 if ce else 0.0))
    srcs = len(p.get("PROVENANCE") or [])
    d.setdefault("number_of_independent_origins", min(1.0, srcs / 4))
    d.setdefault("frequency_across_worlds", 0.5 if "Charon" in (p.get("SOURCE_WORLD") or "") else 0.25)
    d.setdefault("potential_cross_world_utility", 0.5)
    d.setdefault("quality_of_reproducer", 1.0 if p.get("MINIMAL_REPRODUCER") and (p.get("POSITIVE_EXAMPLES") or []) else 0.0)
    d.setdefault("quality_of_falsifier", 1.0 if (p.get("COUNTERFEIT_TESTS") or []) and (p.get("FORBIDDEN_SHORTCUTS") or []) else 0.0)
    d.setdefault("cheap_search_exhaustion", 0.0)
    d.setdefault("minimality_of_required_extension", 0.5)
    total = round(sum(float(d.get(k, 0) or 0) for k in DIMS) / len(DIMS), 3)
    return {"score": total, "dimensions": {k: d.get(k) for k in DIMS}}


def main() -> None:
    rows = []
    for p in P.iter_packets():
        s = score(p)
        p["PRIORITY"]["score"] = s["score"]
        p["PRIORITY"]["dimensions"].update(s["dimensions"])
        P.save(p)
        rows.append({"MINT_ID": p["MINT_ID"], "STATUS": p["STATUS"], "score": s["score"], "family": p.get("FAILURE_FAMILY"),
                     "missing_for_ready": P.missing_for_ready(p) if p["STATUS"] in P.UNRESOLVED else [],
                     "attempts": len(p.get("CHEAP_MODEL_ATTEMPTS") or []), "best_failed": p.get("BEST_FAILED_CANDIDATE"),
                     "dimensions": s["dimensions"], "rationale": p["PRIORITY"].get("rationale", "")})
    order = {"READY-FOR-DEEP-MINT": 0, "APPRENTICE-EXHAUSTED": 1, "CANDIDATE-PRODUCED": 1, "APPRENTICE-TESTING": 2,
             "EXPRESSIVITY-SUSPECTED": 3, "COMPOSITION-SUSPECTED": 4, "TRIAGE": 5, "OBSERVED": 6, "DORMANT": 8, "SCRAPPED": 9}
    rows.sort(key=lambda r: (order.get(r["STATUS"], 7), -r["score"]))
    (P.HEPH / "TOP_READY_MINTS.json").write_text(json.dumps({"generated": P.now_iso(), "walls": rows}, indent=2, default=str), encoding="utf-8")
    lines = [f"TOP_READY_MINTS  generated {P.now_iso()}  (charter s11; read in < 2 min)", ""]
    ready = [r for r in rows if r["STATUS"] == "READY-FOR-DEEP-MINT"]
    lines.append(f"READY-FOR-DEEP-MINT: {len(ready)}   (operator invokes the Master Smith; nothing here auto-escalates)")
    for r in rows:
        bf = r["best_failed"] or {}
        lines.append(f"  {r['MINT_ID']}  {r['STATUS']:<22} score {r['score']:.2f}  attempts {r['attempts']:>2}  "
                     f"best-failed holdout {bf.get('holdout_acc', '-')}  | {str(r['family'])[:70]}")
        if r["missing_for_ready"]:
            lines.append(f"      missing for READY: {', '.join(r['missing_for_ready'])}")
        if r["rationale"]:
            lines.append(f"      {r['rationale'][:110]}")
    lines += ["", "Packets: hephaestus/mint_queue/<MINT_ID>/packet.md   Handoff: hephaestus/HEPHAESTUS_HANDOFF.txt"]
    (P.HEPH / "TOP_READY_MINTS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
