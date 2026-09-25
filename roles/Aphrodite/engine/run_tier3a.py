"""TIER 3A transplant: fresh improvers, frozen artifact, unseen problems.

AMENDMENT 9 sections 4-7 plus ADDENDUM 1 (mt_prodshift_minus_first excluded by
its own positive control, before any arm ran).

Fresh improvers carry NO donor history: no cached solutions, no development
instances, no observed artifacts, and entropy derived from the recipient index
and arm only. The single thing that crosses from the donor is the frozen
library's bytes.
"""
import json
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E          # noqa: E402
import improver as I        # noqa: E402
import meta_tribunal as M   # noqa: E402

ART = json.loads((HERE / "TIER3A_ARTIFACT_2026-09-22.json").read_text())
EXCLUDED = ["mt_prodshift_minus_first"]            # ADDENDUM 1
FAMILIES = [f for f in I.META_TRIBUNAL if f not in EXCLUDED]
N = 16
ESCROW = 400_000
DEV_PER_RECIPIENT = 4

EVOLVED = I.Library(ART["evolved_library"])
PRISTINE = I.pristine_library()
SHAM = I.Library(ART["sham_library"])
ARMS = {"EVOLVED": EVOLVED, "PRISTINE": PRISTINE, "SHAM": SHAM}


def dev_for(family, i):
    """Recipient entropy depends on the family and recipient index ONLY -- no
    donor state is reachable from it."""
    return I.tasks(family, DEV_PER_RECIPIENT,
                   E.dev_entropy("T3A-rx-%s-%03d" % (family, i), 0))


def run_recipient(family, arm, i):
    lib = ARMS[arm]
    rng = random.Random(E.search_entropy("T3A-%s-%s-%03d" % (family, arm, i)))
    esc = E.Escrow(ESCROW)
    t0 = time.perf_counter()
    got = I.search(lib, dev_for(family, i), esc, ESCROW, rng)
    row = {"recipient": i, "arm": arm, "family": family, "escrow_spent": esc.spent,
           "seconds": round(time.perf_counter() - t0, 2)}
    if not got:
        row.update({"qualified": False, "charges_to_solution": None,
                    "disposition": "no development-exact program within escrow"})
        return row
    prog, coord, charges = got
    art = M.artifact_for(family, prog)              # frozen and hashed...
    trib = M.MetaTribunal.after_freeze(art, family)  # ...before the tribunal exists
    sc = trib.score(art)
    row.update({"charges_to_solution": charges, "coordinate": coord,
                "program": list(prog[1:]), "artifact_sha256": art.sha256,
                "artifact_bytes": len(art.bytes), "tribunal": sc,
                "qualified": trib.qualified(sc)})
    row["disposition"] = ("QUALIFIED" if row["qualified"] else
                          "FALSE POSITIVE: dev-exact but tribunal-rejected")
    return row


def summarise(rows):
    q = [r for r in rows if r.get("qualified")]
    ch = [r["charges_to_solution"] for r in q]
    censored = [r["charges_to_solution"] if r.get("qualified") else ESCROW for r in rows]
    coords = {}
    for r in q:
        coords[r.get("coordinate")] = coords.get(r.get("coordinate"), 0) + 1
    return {
        "PRIMARY_censored_mean_effort": round(statistics.mean(censored), 1),
        "M2_qualified": "%d/%d" % (len(q), len(rows)),
        "charges_median_winners_only_TELEMETRY": statistics.median(ch) if ch else None,
        "tribunal_median_extrapolation": (statistics.median(
            [r["tribunal"]["held_out_extrapolation"] for r in rows if r.get("tribunal")])
            if any(r.get("tribunal") for r in rows) else None),
        "solutions_by_coordinate": coords,
        "false_positives": sum(1 for r in rows
                               if r.get("charges_to_solution") and not r.get("qualified")),
        "distinct_hashes": len({r.get("artifact_sha256") for r in rows
                                if r.get("artifact_sha256")}),
    }


def main():
    t0 = time.perf_counter()
    out = {"written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "evolved_library_sha256": ART["evolved_library_sha256"],
           "pristine_library_sha256": ART["pristine_library_sha256"],
           "sham_library_sha256": ART["sham_library_sha256"],
           "meta_charges_spent": ART["meta_charges_spent"],
           "families": FAMILIES, "excluded_families": EXCLUDED,
           "recipients_per_arm": N, "escrow": ESCROW,
           "per_family": {}, "detail": {}}
    for fam in FAMILIES:
        out["per_family"][fam] = {}
        out["detail"][fam] = {}
        for arm in ARMS:
            rows = [run_recipient(fam, arm, i) for i in range(N)]
            out["detail"][fam][arm] = rows
            out["per_family"][fam][arm] = summarise(rows)
            print("[%s/%s] %s" % (fam, arm, json.dumps(out["per_family"][fam][arm])), flush=True)

    # cost accounting (AMENDMENT 9 section 7)
    marginal = {}
    for fam in FAMILIES:
        p = out["per_family"][fam]["PRISTINE"]["PRIMARY_censored_mean_effort"]
        e = out["per_family"][fam]["EVOLVED"]["PRIMARY_censored_mean_effort"]
        marginal[fam] = {"pristine": p, "evolved": e, "saved_per_recipient": round(p - e, 1),
                         "ratio": round(p / e, 2) if e else None}
    total_saved = sum(v["saved_per_recipient"] for v in marginal.values()) / len(marginal)
    out["cost_accounting"] = {
        "marginal_inheritance_value_per_family": marginal,
        "mean_saved_charges_per_recipient_per_family": round(total_saved, 1),
        "meta_search_cost_charges": ART["meta_charges_spent"],
        "break_even_descendants": (round(ART["meta_charges_spent"] / total_saved, 1)
                                   if total_saved > 0 else None),
        "note": ("break-even counts descendant searches needed for cumulative "
                 "downstream savings to repay the meta-search that produced the "
                 "library; a mechanism may qualify scientifically while remaining "
                 "economically negative"),
    }
    out["total_seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / "TIER3A_RESULTS_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "detail"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
