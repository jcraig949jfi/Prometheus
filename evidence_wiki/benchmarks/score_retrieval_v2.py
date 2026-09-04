"""Deterministic V2 retrieval scoring (frozen rule in PREREGISTRATION_V2).

RECOVERED iff the proposal text contains the item's claim_id/evidence_id,
its source-path hint, or any frozen marker (case-insensitive). Also verifies
the sealed gold hash before scoring. Negative/correction flags are resolved
live from the wiki store. Outputs benchmarks/retrieval_v2.json.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import db  # noqa: E402

OUT_DIR = HERE / "v2" / "arm_outputs"


def load_gold():
    blob = (HERE / "derived" / "v2_gold.json").read_text(encoding="utf-8")
    sealed = (HERE / "gold" / "v2_gold_sha256.txt").read_text().strip()
    assert hashlib.sha256(blob.encode()).hexdigest() == sealed, "gold hash mismatch"
    return json.loads(blob)


def item_flags(conn, gold):
    """negative / has-correction flags per ref, from the canonical store."""
    flags = {}
    with db.dict_cur(conn) as cur:
        for task, spec in gold.items():
            for it in spec["items"]:
                neg = corr = False
                if it.get("evidence_id"):
                    cur.execute("SELECT negative FROM ew.evidence WHERE evidence_id=%s",
                                (it["evidence_id"],))
                    r = cur.fetchone()
                    neg = bool(r and r["negative"])
                if it.get("claim_id"):
                    cur.execute("SELECT 1 FROM ew.relations WHERE (src_id=%s OR dst_id=%s) "
                                "AND relation_type IN ('CORRECTS','CONTRADICTS','SUPERSEDES') LIMIT 1",
                                (it["claim_id"], it["claim_id"]))
                    corr = cur.fetchone() is not None
                flags[(task, it["ref"])] = {"negative": neg, "correction": corr}
    return flags


def recovered(text_l, it):
    if it.get("claim_id") and it["claim_id"].lower() in text_l:
        return "claim_id"
    if it.get("evidence_id") and it["evidence_id"].lower() in text_l:
        return "evidence_id"
    if it.get("source_path_hint") and it["source_path_hint"].lower() in text_l:
        return "source_path"
    for m in it["markers"]:
        if m.lower() in text_l:
            return f"marker:{m}"
    return None


def main():
    gold = load_gold()
    conn = db.connect()
    flags = item_flags(conn, gold)
    conn.close()
    rows = []
    for f in sorted(OUT_DIR.glob("*.md")):
        name = f.stem  # e.g. V2-T01_B_haiku
        parts = name.split("_")
        task, arm, model = parts[0], parts[1], "_".join(parts[2:])
        if task not in gold:
            continue
        text_l = f.read_text(encoding="utf-8", errors="replace").lower()
        items = []
        for it in gold[task]["items"]:
            how = recovered(text_l, it)
            fl = flags[(task, it["ref"])]
            items.append({"ref": it["ref"], "kind": it["kind"],
                          "recovered": bool(how), "how": how, **fl})
        core = [i for i in items if i["kind"] == "core"]
        supp = [i for i in items if i["kind"] == "supporting"]
        neg = [i for i in items if i["negative"] and i["kind"] != "misleading"]
        corr = [i for i in items if i["correction"] and i["kind"] != "misleading"]
        def rate(xs):
            return round(sum(i["recovered"] for i in xs) / len(xs), 3) if xs else None
        rows.append({
            "task": task, "arm": arm, "model": model, "file": f.name,
            "core_recall": rate(core), "supporting_recall": rate(supp),
            "weighted_recall": round(
                (sum(i["recovered"] for i in core) + 0.5 * sum(i["recovered"] for i in supp))
                / (len(core) + 0.5 * len(supp)), 3) if core or supp else None,
            "negative_recall": rate(neg), "correction_recall": rate(corr),
            "misleading_recovered": [i["ref"] for i in items
                                     if i["kind"] == "misleading" and i["recovered"]],
            "items": items,
        })
    out = {"rows": rows}
    # arm-level aggregates over primary tasks only
    prim = [r for r in rows if r["task"].startswith("V2-")]
    for arm in ("A", "B", "C"):
        sub = [r for r in prim if r["arm"] == arm]
        if sub:
            import numpy as np
            out[f"arm_{arm}"] = {
                "n": len(sub),
                "mean_core_recall": round(float(np.mean([r["core_recall"] for r in sub])), 3),
                "mean_weighted_recall": round(float(np.mean([r["weighted_recall"] for r in sub])), 3),
                "mean_negative_recall": round(float(np.mean([r["negative_recall"] for r in sub if r["negative_recall"] is not None])), 3),
                "mean_correction_recall": round(float(np.mean([r["correction_recall"] for r in sub if r["correction_recall"] is not None])), 3),
            }
    (HERE / "benchmarks" / "retrieval_v2.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    slim = {k: v for k, v in out.items() if k != "rows"}
    slim["per_proposal"] = [{k: r[k] for k in ("task", "arm", "model",
                            "core_recall", "negative_recall")} for r in rows]
    print(json.dumps(slim, indent=1))


if __name__ == "__main__":
    main()
