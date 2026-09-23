"""TIER 3B steps 3-5: discrimination qualification, positive controls, shams.

Run BEFORE meta-development. Produces one frozen artifact containing:
  - each load-bearing family's false-positive basin and qualified dev size;
  - the positive-control verdict for every meta-tribunal family;
  - the eight sham libraries with their hashes.
Nothing here looks at any evolved artifact, which does not yet exist.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E          # noqa: E402
import improver as I        # noqa: E402
import meta_tribunal as M   # noqa: E402
import tier3b as T          # noqa: E402

M.use_provider(T)   # the frozen Tier-3B catalog, installed before any scoring


def positive_control(family):
    prog = T.witness(family)
    art = M.artifact_for(family, prog)
    trib = M.MetaTribunal.after_freeze(art, family)
    sc = trib.score(art)
    return {"family": family, "tribunal": sc, "PASSES": trib.qualified(sc)}


def main():
    # step 3: discrimination, for every load-bearing family
    quals = {}
    for fam in T.META_DEV + T.META_TRIBUNAL:
        quals[fam] = T.qualify_family(fam, E.dev_entropy("T3B-pool-" + fam, 0))
        q = quals[fam]
        print("[discrim] %-28s classes=%5d basin %4d -> %d at dev=%d %s"
              % (fam, q["reachable_semantic_classes"], q["initial_false_positive_basin"],
                 q["final_false_positive_basin"], q["development_size"],
                 "SUITABLE" if q["SUITABLE"] else "UNSUITABLE"), flush=True)

    # step 4: positive controls on the frozen meta-tribunal catalog
    pcs = {}
    for fam in T.META_TRIBUNAL:
        pcs[fam] = positive_control(fam)
        print("[positive] %-28s %s %s" % (fam, pcs[fam]["PASSES"],
                                          json.dumps(pcs[fam]["tribunal"])), flush=True)

    usable = [f for f in T.META_TRIBUNAL if pcs[f]["PASSES"] and quals[f]["SUITABLE"]]
    unseen_usable = [f for f in usable if f in T.UNSEEN_BODY]
    transfer_usable = [f for f in usable if f in T.TRANSFER]

    # step 5: the sham distribution, hashes frozen before meta-development
    base = I.pristine_library().entries
    shams = T.sham_libraries(base)

    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "discrimination": quals,
        "positive_controls": pcs,
        "usable_meta_tribunal_families": usable,
        "usable_transfer_families": transfer_usable,
        "usable_unseen_body_families": unseen_usable,
        "requirement_more_than_one_unseen_body_family": len(unseen_usable) > 1,
        "meta_dev_all_suitable": all(quals[f]["SUITABLE"] for f in T.META_DEV),
        "sham_distribution": [{"index": s["index"], "sha256": s["sha256"],
                               "bodies": s["bodies"]} for s in shams],
        "sham_libraries": [s["entries"] for s in shams],
        "descendant_horizon": T.DESCENDANT_HORIZON,
        "status": "QUALIFICATION ONLY -- no meta-development has been run",
    }
    out["VERDICT"] = ("PROCEED" if (out["meta_dev_all_suitable"]
                                    and len(unseen_usable) > 1 and len(transfer_usable) >= 1)
                      else "STOP: qualification requirements not met")
    (HERE / "TIER3B_QUALIFICATION_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("discrimination", "positive_controls",
                                   "sham_libraries")}, indent=2, sort_keys=True))
    return 0 if out["VERDICT"] == "PROCEED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
