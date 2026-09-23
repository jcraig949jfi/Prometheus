"""Slice 4 execution: representational search leverage at equal expressive power.

Frozen by AMENDMENT_8 (026ccc847) and gated by the expressivity certificate.

Protocol per recipient: search its arm's coordinate until a program is exact on
its OWN development instances, adopt that program (the search stops there, as
evolve() does), freeze and hash the artifact, and only then let the tribunal
see it. A dev-exact program that the tribunal rejects counts as a FALSE
POSITIVE and the recipient does not qualify.

DEV_PER_RECIPIENT = 4 is declared here; AMENDMENT 8 fixed the entropy rule but
not the count. Four keeps overfitting reachable while making it unlikely that
the first dev-exact program is spurious.
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
import basis_v4 as G    # noqa: E402
import engine as E      # noqa: E402

CERT = json.loads((HERE / "EXPRESSIVITY_CERTIFICATE_2026-09-22.json").read_text())
FAMILIES = CERT["selected_families"]
N = 16
ESCROW = 1_500_000
DEV_PER_RECIPIENT = 4


def dev_for(family, i):
    return G.tasks(family, DEV_PER_RECIPIENT, E.dev_entropy("S4-%s-%03d" % (family, i), 0))


def artifact_for(family, prog):
    return E.Artifact.from_modules(
        dict(E.base_image(), search=E.base_image()["search"] + G.program_source(family, prog)),
        generation=E.FROZEN_GENERATION)


def organ_then_g4(rng):
    for item in G.organ_candidates(rng):
        yield item
    for item in G.scratch_candidates(rng):      # fallback keeps power equal
        yield item


def sham_then_g4(rng):
    for item in G.sham_candidates(rng):
        yield item
    for item in G.scratch_candidates(rng):
        yield item


ARMS = {
    "ORGAN": lambda rng: organ_then_g4(rng),
    "SCRATCH": lambda rng: G.scratch_candidates(rng),
    "SHAM": lambda rng: sham_then_g4(rng),
}


def run_recipient(family, arm, i):
    rng = random.Random(E.search_entropy("S4-%s-%s-%03d" % (family, arm, i)))
    esc = E.Escrow(ESCROW)
    dev = dev_for(family, i)
    t0 = time.perf_counter()
    found = G.search(ARMS[arm](rng), dev, esc, ESCROW)
    row = {"recipient": i, "arm": arm, "family": family,
           "escrow_spent": esc.spent, "seconds": round(time.perf_counter() - t0, 2)}
    if not found:
        row.update({"qualified": False, "charges_to_solution": None,
                    "disposition": "no dev-exact program within escrow"})
        return row
    prog, tag, charges = found
    art = artifact_for(family, prog)
    trib = G.Tribunal4.after_freeze(art, family)      # only now does it exist
    sc = trib.score(art)
    row.update({
        "charges_to_solution": charges,
        "program": {"shape": prog[0], "parts": list(prog[1:])},
        "coordinate": tag[0],
        "artifact_sha256": art.sha256,
        "artifact_bytes": len(art.bytes),
        "tribunal": sc,
        "qualified": trib.qualified(sc),
        "rediscovered_fold": G.rediscovered_fold(prog),
    })
    row["disposition"] = ("QUALIFIED" if row["qualified"] else
                          "FALSE POSITIVE: dev-exact but tribunal-rejected "
                          "(extrap=%.3f ce=%.3f meta=%s)"
                          % (sc["held_out_extrapolation"], sc["counterexample_accuracy"],
                             sc["metamorphic_pass"]))
    return row


def positive(family):
    from certify_expressivity import witness_for
    prog = witness_for(family)
    art = artifact_for(family, prog)
    trib = G.Tribunal4.after_freeze(art, family)
    sc = trib.score(art)
    return {"family": family, "arm": "POSITIVE", "qualified": trib.qualified(sc),
            "tribunal": sc, "artifact_bytes": len(art.bytes)}


def summarise(rows):
    qual = [r for r in rows if r.get("qualified")]
    charges = [r["charges_to_solution"] for r in qual if r.get("charges_to_solution")]
    fp = [r for r in rows if r.get("charges_to_solution") and not r.get("qualified")]
    hashes = {r.get("artifact_sha256") for r in rows if r.get("artifact_sha256")}
    return {
        "M2_qualified": "%d/%d" % (len(qual), len(rows)),
        "M1_median_charges": statistics.median(charges) if charges else None,
        "M1_min_charges": min(charges) if charges else None,
        "M1_max_charges": max(charges) if charges else None,
        "M3_median_escrow_spent": statistics.median([r["escrow_spent"] for r in rows]),
        "M4_median_tribunal": (statistics.median(
            [r["tribunal"]["held_out_extrapolation"] for r in rows if r.get("tribunal")])
            if any(r.get("tribunal") for r in rows) else None),
        "M5_median_stress200": (statistics.median(
            [r["tribunal"]["stress_length_200"] for r in rows if r.get("tribunal")])
            if any(r.get("tribunal") for r in rows) else None),
        "M6_median_bytes": (statistics.median(
            [r["artifact_bytes"] for r in rows if r.get("artifact_bytes")])
            if any(r.get("artifact_bytes") for r in rows) else None),
        "M7_distinct_hashes": "%d/%d" % (len(hashes), len(rows)),
        "M8_rediscovered_fold": "%d/%d" % (sum(1 for r in rows if r.get("rediscovered_fold")),
                                           len(rows)),
        "false_positives": "%d/%d" % (len(fp), len(rows)),
    }


def main():
    t0 = time.perf_counter()
    out = {"written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "grammar_version": G.GRAMMAR_VERSION_4, "organ_sha256": G.ORGAN_SHA256,
           "families": FAMILIES, "recipients_per_arm": N, "escrow": ESCROW,
           "dev_per_recipient": DEV_PER_RECIPIENT,
           "space_sizes": G.space_sizes(),
           "analytic_expected_charges_randomised_order": {
               "ORGAN": G.space_sizes()["ORGAN_macro_total"] // 2,
               "SCRATCH": G.space_sizes()["G4_fold_shape_total"] // 2},
           "per_family": {}, "detail": {}}
    for fam in FAMILIES:
        out["per_family"][fam] = {}
        out["detail"][fam] = {}
        for arm in ARMS:
            rows = [run_recipient(fam, arm, i) for i in range(N)]
            out["detail"][fam][arm] = rows
            out["per_family"][fam][arm] = summarise(rows)
            print("[%s/%s] %s" % (fam, arm, json.dumps(out["per_family"][fam][arm])), flush=True)
        out["per_family"][fam]["POSITIVE"] = positive(fam)
        print("[%s/POSITIVE] qualified=%s" % (fam, out["per_family"][fam]["POSITIVE"]["qualified"]),
              flush=True)
    out["total_seconds"] = round(time.perf_counter() - t0, 1)
    (HERE / "SLICE4_RESULTS_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "detail"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
