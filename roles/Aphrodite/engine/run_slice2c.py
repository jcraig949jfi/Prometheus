"""Slice 2C execution, frozen by AMENDMENT_6_2026-09-21.md.

Phase 1 evolves and hashes all 16 artifacts. Phase 2 -- and only then --
constructs the hostile tribunal and adjudicates. No lineage is ever handed a
tribunal, and no adjudication result reaches the search.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v2 as B    # noqa: E402
import engine as E      # noqa: E402
import slice2c as S     # noqa: E402

LINEAGE_IDS = ["L2C-%03d" % i for i in range(1, 17)]
BUDGET = 10 ** 7


def main():
    base_art = E.Artifact.from_modules(dict(E.base_image()))
    t0 = time.perf_counter()

    frozen = []
    for lid in LINEAGE_IDS:
        esc = E.Escrow(BUDGET)
        lin = S.Lineage2C(lineage_id=lid, base=E.base_image())
        started = time.perf_counter()
        try:
            lin.evolve(generations=E.FROZEN_GENERATION, escrow=esc)
        except E.EscrowExhausted:
            pass
        art = lin.extract(lin.generation)
        print("[phase1] %s gen=%d spent=%d %.1fs" % (lid, lin.generation, esc.spent,
              time.perf_counter() - started), flush=True)
        frozen.append({"lineage_id": lid, "artifact_sha256": art.sha256,
                       "generation": art.generation,
                       "non_base": art.sha256 != base_art.sha256,
                       "escrow_spent": esc.spent,
                       "seconds": round(time.perf_counter() - started, 2),
                       "dev_final_score": lin.history[-1]["score"] if lin.history else None,
                       "telemetry": E.structural_telemetry(art),
                       "_art": art})

    print("[phase2] all %d artifacts frozen; constructing tribunal" % len(frozen), flush=True)
    for row in frozen:
        art = row.pop("_art")
        print("[phase2] adjudicating %s" % row["lineage_id"], flush=True)
        if art.generation != E.FROZEN_GENERATION:
            row["qualifies"] = False
            row["disposition"] = "did not reach the frozen generation"
            continue
        trib = S.Tribunal2C.after_freeze(art)

        r = E.Recipient.fresh(seed=7)
        rec = r.load(art)
        membrane_clean = (rec["hash_at_extraction"] == rec["hash_at_load"] == art.sha256
                          and list(rec["crossed"]) == ["artifact_bytes"]
                          and rec["donor_reads"] == [art.sha256])
        row["membrane"] = {"clean": membrane_clean, "crossed": rec["crossed"],
                           "donor_reads": rec["donor_reads"]}

        folds = S.parse_folds(art)
        per_class, load_bearing_classes = {}, []
        for cls_ in S.HEADROOM:
            sc = trib.score(art, cls_)
            base_r = E.Recipient.fresh(seed=4242)
            base_r.load(base_art)
            sc["base_held_out"] = base_r.run_tasks(
                B.tasks(cls_, 200, E.tribunal_entropy("2c-" + cls_, 1),
                        length_range=B.EXTRAPOLATION_LENGTHS), E.Escrow(10 ** 7))["accuracy"]
            sc["improves"] = sc["held_out_extrapolation"] > sc["base_held_out"]
            sc["survives_falsification"] = (sc["counterexample_accuracy"] >= 0.99
                                            and sc["metamorphic_pass"] is True)
            sc["extrapolates"] = (sc["held_out_extrapolation"] >= 0.99
                                  and sc["stress_length_200"] >= 0.99)
            if cls_ in folds:
                sc["structure"] = S.adjudicate_structure(art, cls_, folds[cls_])
                sc["mechanism"] = folds[cls_]
                if sc["structure"]["load_bearing"]:
                    load_bearing_classes.append(cls_)
            else:
                sc["structure"] = {"load_bearing": False,
                                   "note": "no fold present for this class"}
            per_class[cls_] = sc
        row["tribunal"] = per_class

        q = {
            "Q1_endogenous": row["non_base"],
            "Q3_membrane": membrane_clean,
            "Q4_two_classes": sum(1 for v in per_class.values()
                                  if v["improves"] and v["survives_falsification"]) >= 2,
            "Q5_survives_falsification": all(v["survives_falsification"] or not v["improves"]
                                             for v in per_class.values()),
            "Q6_load_bearing_structure": len(load_bearing_classes) >= 1,
            "Q7_extrapolates": all(v["extrapolates"] for v in per_class.values() if v["improves"]),
            "Q8_no_undeclared_payload": ("SECRET" not in art.bytes.decode()
                                         and "gold" not in art.bytes.decode()),
        }
        row["criteria"] = q
        row["qualifies"] = all(q.values())
        row["load_bearing_classes"] = load_bearing_classes
        row["disposition"] = ("QUALIFIES" if row["qualifies"]
                              else "failed: " + ",".join(k for k, v in q.items() if not v))

    hashes = [r["artifact_sha256"] for r in frozen]
    qual = [r for r in frozen if r.get("qualifies")]
    both = [r for r in qual if len(r.get("load_bearing_classes", [])) >= 2]
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine_sha256": E.source_hash(),
        "grammar_hash": E.grammar_hash(),
        "tier": "2 (apparatus) -- NOT Campaign 1 evidence",
        "independent_lineages": len(LINEAGE_IDS),
        "qualifying_artifacts": len(qual),
        "discovery_yield": "%d/%d" % (len(qual), len(LINEAGE_IDS)),
        "distinct_artifact_hashes": "%d/%d" % (len(set(hashes)), len(LINEAGE_IDS)),
        "reuse_load_bearing_in_both_classes": "%d/%d" % (len(both), len(LINEAGE_IDS)),
        "reuse_load_bearing_in_one_class_only": "%d/%d" % (len(qual) - len(both), len(LINEAGE_IDS)),
        "total_seconds": round(time.perf_counter() - t0, 1),
        "lineages": frozen,
    }
    (HERE / "SLICE2C_RESULTS_2026-09-21.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "lineages"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
