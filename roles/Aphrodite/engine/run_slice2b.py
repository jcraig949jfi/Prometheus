"""Slice 2B: launch independent lineages, freeze, then judge with a hostile
tribunal that did not exist while they evolved.

Preregistered by AMENDMENT_3_2026-09-21.md. The lineage identifiers below are
the preregistered set; development and search entropy are derived from them by
the frozen rule, and tribunal entropy comes from a disjoint domain.

Order is enforced by construction, not by discipline: every artifact is
extracted and hashed BEFORE `Tribunal.after_freeze` is called, and no tribunal
object is ever passed to a lineage.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E  # noqa: E402

LINEAGE_IDS = ["L-%03d" % i for i in range(1, 17)]     # preregistered: 16 lineages
BUDGET = 10 ** 7


def main():
    base_art = E.Artifact.from_modules(dict(E.base_image()))
    t0 = time.perf_counter()

    # ---- PHASE 1: evolve and freeze. No tribunal exists yet.
    frozen = []
    for lid in LINEAGE_IDS:
        esc = E.Escrow(BUDGET)
        lin = E.Lineage(seed=0, base=E.base_image(), lineage_id=lid)
        started = time.perf_counter()
        try:
            lin.evolve(generations=E.FROZEN_GENERATION, escrow=esc)
        except E.EscrowExhausted:
            pass
        art = lin.extract(lin.generation)
        frozen.append({
            "lineage_id": lid,
            "artifact_sha256": art.sha256,
            "generation": art.generation,
            "non_base": art.sha256 != base_art.sha256,
            "structural": E.structural_change(art),
            "escrow_spent": esc.spent,
            "seconds": round(time.perf_counter() - started, 3),
            "dev_final_score": lin.history[-1]["score"] if lin.history else None,
            "_artifact": art,
        })

    # ---- PHASE 2: only now does the tribunal come into existence.
    for row in frozen:
        art = row["_artifact"]
        if art.generation != E.FROZEN_GENERATION:
            row["qualifies"] = False
            row["note"] = "did not reach the frozen generation"
            continue
        trib = E.Tribunal.after_freeze(art)

        # C2: crosses the qualified membrane through the ONE loader path
        r = E.Recipient.fresh(seed=7)
        rec = r.load(art)
        row["membrane"] = {
            "loader_path": rec["loader_path"],
            "hash_at_extraction": rec["hash_at_extraction"],
            "hash_at_load": rec["hash_at_load"],
            "crossed": rec["crossed"],
            "donor_reads": rec["donor_reads"],
            "clean": (rec["hash_at_extraction"] == rec["hash_at_load"] == art.sha256
                      and list(rec["crossed"]) == ["artifact_bytes"]),
        }

        per_class, improved_classes, falsified = {}, 0, []
        for cls in E.HEADROOM_FAMILIES:
            got = trib.score(art, cls)
            base_got = trib.score(base_art, cls)
            got["base_held_out_accuracy"] = base_got["held_out_accuracy"]
            got["improves"] = got["held_out_accuracy"] > base_got["held_out_accuracy"]
            got["survives_falsification"] = (got["counterexample_accuracy"] >= 0.99
                                             and got["metamorphic_pass"] is True)
            per_class[cls] = got
            if got["improves"]:
                improved_classes += 1
            if got["improves"] and not got["survives_falsification"]:
                falsified.append(cls)
        row["tribunal"] = per_class

        c = {
            "C1_endogenous": row["non_base"],
            "C2_membrane": row["membrane"]["clean"],
            "C3_improves_on_tribunal": improved_classes >= 1,
            "C4_survives_counterexamples": len(falsified) == 0 and improved_classes >= 1,
            "C5_two_classes": sum(1 for v in per_class.values()
                                  if v["improves"] and v["survives_falsification"]) >= 2,
            "C6_structural": row["structural"],
        }
        row["criteria"] = c
        row["qualifies"] = all(c.values())
        row["falsified_classes"] = falsified
        del row["_artifact"]

    hashes = [r["artifact_sha256"] for r in frozen]
    qualifying = [r for r in frozen if r.get("qualifies")]
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine_sha256": E.source_hash(),
        "tier": "2 (apparatus) -- NOT Campaign 1 evidence (RULING 7)",
        "independent_launched_lineages": len(LINEAGE_IDS),
        "distinct_extracted_artifact_hashes": len(set(hashes)),
        "non_base_artifacts": sum(1 for r in frozen if r["non_base"]),
        "structural_artifacts": sum(1 for r in frozen if r["structural"]),
        "qualifying_artifacts": len(qualifying),
        "discovery_yield": "%d/%d" % (len(qualifying), len(LINEAGE_IDS)),
        "total_seconds": round(time.perf_counter() - t0, 1),
        "lineages": frozen,
    }
    p = HERE / "SLICE2B_RESULTS_2026-09-21.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "lineages"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
