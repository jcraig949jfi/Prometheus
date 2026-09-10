"""C3-2 readout (Track B, F-13). Numbers only; Harmonia rules.

Reads the completed rows of one candidate set from the Vivarium queue
(result projection carried on the row), and reports:

  * per-rule, per-IC-sample accuracy (the four shared IC samples are the
    unit for accuracy; the rule is the unit for D3);
  * the EXACT-SYMMETRY check on the null arm: for each (genome, transform)
    the transformed run must reproduce its untransformed twin's per-sample
    accuracy, n_incorrect and mask digest EXACTLY (the mask, never the
    spacetime digest, which is of the rule actually run on the library's
    own IC draw and is declared not to be an image);
  * ICC(1), one-way random effects with the rule as the group and the four
    IC samples as the repeated measures -- the number Harmonia asked the
    corpus to supply for the unit question.

D3 over C3 (one row per rule, v0 beside v1) is produced only when the
acquisition arm is complete enough for eight independent rules per
descriptor region; before that the section says PARTIAL and why.
"""
from __future__ import annotations

import argparse
import datetime
import json
import statistics
from typing import Any, Dict, List, Optional

CS = "cs-c3-2"
IDENTITY_FIELDS = ("accuracy_stable", "n_incorrect_stable", "mask_digest_stable",
                   "accuracy_at_T", "n_incorrect_at_T", "mask_digest_at_T", "misclassified_ic")
#: plus the CORRECT COUNT (n_ic_total - n_incorrect) as an integer, per Harmonia's gate


SETS = (CS, CS + "-r1")        # the corpus and its transport re-issues (same specs, same hashes)


def fetch(conn, candidate_set=SETS) -> List[Dict[str, Any]]:
    """Rows of the corpus plus its re-issue sets; where a label has a
    completed re-issue, the re-issue REPLACES the failed original (same
    spec hash), and the original stays in the queue as its record."""
    sets = [candidate_set] if isinstance(candidate_set, str) else list(candidate_set)
    cur = conn.cursor()
    cur.execute("SELECT candidate_set_id, arm_id, source_evidence->>'label', status, spec_hash, sfe_experiment_id, "
                "result_summary->'result'->'repeats', result_summary->>'outcome' "
                "FROM viv.research_experiment_queue WHERE candidate_set_id = ANY(%s) ORDER BY candidate_set_id, arm_id, source_evidence->>'label'",
                (sets,))
    rows, by_label = [], {}
    for cs, arm, label, status, spec_hash, exp, reps, outcome in cur.fetchall():
        results = [r.get("result", r) for r in (reps or [])] if status == "completed" else []
        row = {"set": cs, "arm": arm, "label": label, "status": status, "spec_hash": spec_hash,
               "sfe_experiment_id": exp, "outcome": outcome, "repeats": results}
        k = (arm, label)
        if k in by_label:
            prev = by_label[k]
            if prev["status"] != "completed" and status == "completed":
                if prev["spec_hash"] != spec_hash:
                    raise RuntimeError("re-issue of {} carries a different spec hash".format(label))
                row["replaces_failed"] = prev["set"]
                rows[rows.index(prev)] = row; by_label[k] = row
            continue
        by_label[k] = row; rows.append(row)
    return rows


def null_identity(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by = {(r["arm"], r["label"]): r for r in rows if r["status"] == "completed"}
    out = {"checked": [], "identical": 0, "not_identical": 0, "indeterminate": 0, "fields": IDENTITY_FIELDS}
    for (arm, label), r in sorted(by.items()):
        if arm != "C3-null":
            continue
        genome, transform = label.split(":")
        twin = by.get(("C3-hist", genome))
        rec = {"genome": genome, "transform": transform}
        if twin is None or len(twin["repeats"]) != len(r["repeats"]) or not r["repeats"]:
            rec["verdict"] = "INDETERMINATE"; rec["reason"] = "twin missing or repeat count differs"
            out["indeterminate"] += 1; out["checked"].append(rec); continue
        diffs, indeterminate, flip_signature = [], [], []
        for i, (a, b) in enumerate(zip(twin["repeats"], r["repeats"])):
            # Harmonia's gate (RULING_H1H0_FAIRNESS_C3_2_ANALYSIS): all three of
            # correct count, incorrect count and mask digest, as integers /
            # exact strings; accuracy-and-count without the digest is
            # INDETERMINATE (two incorrect sets can share a count); accuracy
            # == 1 - original is the signature of a target flip not applied.
            n = a.get("n_ic_total") or b.get("n_ic_total")
            if not a.get("mask_digest_stable") or not b.get("mask_digest_stable"):
                indeterminate.append({"repeat": i, "reason": "mask digest absent"})
                continue
            for f in IDENTITY_FIELDS:
                if a.get(f) != b.get(f):
                    diffs.append({"repeat": i, "field": f, "twin": str(a.get(f))[:60], "transformed": str(b.get(f))[:60]})
            if n and a.get("n_incorrect_stable") is not None and b.get("n_incorrect_stable") is not None:
                ca, cb = n - a["n_incorrect_stable"], n - b["n_incorrect_stable"]
                if ca != cb:
                    diffs.append({"repeat": i, "field": "correct_count", "twin": ca, "transformed": cb})
                if ca + cb == n and ca != cb:
                    flip_signature.append(i)
        if indeterminate and not diffs:
            rec["verdict"] = "INDETERMINATE"; rec["reason"] = indeterminate
            out["indeterminate"] += 1; rec["diffs"] = []; out["checked"].append(rec); continue
        rec["verdict"] = "IDENTICAL" if not diffs else "NOT_IDENTICAL"
        rec["diffs"] = diffs
        if flip_signature:
            rec["target_flip_not_applied_signature"] = flip_signature
        rec["spacetime_is_image_of_untransformed"] = [x.get("spacetime_is_image_of_untransformed") for x in r["repeats"]]
        rec["twin_accuracy_by_sample"] = [x.get("accuracy_stable") for x in twin["repeats"]]
        out["identical" if not diffs else "not_identical"] += 1
        out["checked"].append(rec)
    out["n"] = len(out["checked"])
    return out


def icc1(groups: List[List[float]]) -> Dict[str, Any]:
    """One-way random-effects ICC(1): (MSB - MSW) / (MSB + (k-1) MSW),
    k = measures per group (equal here). Groups with fewer than 2 measures
    are dropped and counted."""
    g = [x for x in groups if len(x) >= 2]
    dropped = len(groups) - len(g)
    if len(g) < 2:
        return {"icc1": None, "groups": len(g), "dropped": dropped, "reason": "fewer than two groups"}
    k = statistics.mean(len(x) for x in g)
    grand = statistics.mean(v for x in g for v in x)
    msb = sum(len(x) * (statistics.mean(x) - grand) ** 2 for x in g) / (len(g) - 1)
    msw = sum((v - statistics.mean(x)) ** 2 for x in g for v in x) / sum(len(x) - 1 for x in g)
    icc = (msb - msw) / (msb + (k - 1) * msw) if (msb + (k - 1) * msw) > 0 else None
    return {"icc1": icc, "msb": msb, "msw": msw, "k": k, "groups": len(g), "dropped": dropped,
            "grand_mean": grand}


def readout(rows: List[Dict[str, Any]], d3: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    done = [r for r in rows if r["status"] == "completed"]
    by_arm: Dict[str, int] = {}
    for r in rows:
        by_arm.setdefault(r["arm"], {}).setdefault(r["status"], 0)
        by_arm[r["arm"]][r["status"]] += 1
    table = []
    for r in done:
        accs = [x.get("accuracy_stable") for x in r["repeats"]]
        table.append({"arm": r["arm"], "label": r["label"], "outcome": r["outcome"],
                      "accuracy_by_sample": accs,
                      "n_incorrect_by_sample": [x.get("n_incorrect_stable") for x in r["repeats"]],
                      "criteria_agree": [x.get("criteria_agree") for x in r["repeats"]],
                      "accuracy_at_T_by_sample": [x.get("accuracy_at_T") for x in r["repeats"]],
                      "mean": statistics.mean(accs) if accs and None not in accs else None,
                      "sfe_experiment_id": r["sfe_experiment_id"]})
    # per-sample column means over all completed non-null rows (the shared IC samples' own effect)
    k = max((len(t["accuracy_by_sample"]) for t in table), default=0)
    cols = [[t["accuracy_by_sample"][i] for t in table if t["arm"] != "C3-null" and len(t["accuracy_by_sample"]) > i]
            for i in range(k)]
    sample_means = [statistics.mean(c) if c else None for c in cols]
    # ICC over rules: exclude the null arm (duplicates of hist by construction) and structural zeros
    groups_all = [t["accuracy_by_sample"] for t in table if t["arm"] != "C3-null"]
    groups_nonzero = [g for g in groups_all if any(v > 0 for v in g)]
    return {"schema": "archaeon.c3.readout.v0", "candidate_set": CS,
            "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            # COMPLETE = nothing left to run; a failed row is a recorded outcome, not pending work
            "complete": all(r["status"] in ("completed", "failed", "cancelled") for r in rows),
            "n_failed": sum(1 for r in rows if r["status"] == "failed"),
            "failed_labels": [r["label"] for r in rows if r["status"] == "failed"],
            "status_by_arm": by_arm, "n_rows": len(rows), "n_completed": len(done),
            "table": table, "ic_sample_means": sample_means,
            "icc1_rules_all": icc1(groups_all), "icc1_rules_excluding_structural_zeros": icc1(groups_nonzero),
            "null_identity": null_identity(rows),
            "structural_zeros": {"acq_completed": sum(1 for t in table if t["arm"] == "C3-acq"),
                                 "acq_zero_on_every_sample": sum(1 for t in table if t["arm"] == "C3-acq" and t["mean"] == 0.0),
                                 "hist_zero": [t["label"] for t in table if t["arm"] == "C3-hist" and t["mean"] == 0.0],
                                 "base_zero": [t["label"] for t in table if t["arm"] == "C3-base" and t["mean"] == 0.0]},
            "d3_over_c3": d3 or _d3_over_c3_status(rows, table)}


def _d3_over_c3_status(rows, table):
    complete = all(r["status"] in ("completed", "failed", "cancelled") for r in rows)
    acq = [t for t in table if t["arm"] == "C3-acq"]
    zeros = sum(1 for t in acq if t["mean"] == 0.0)
    if acq and zeros == len(acq):
        return {"status": "STRUCTURALLY_VOID" if complete else "STRUCTURALLY_VOID_PROVISIONAL",
                "reason": "the acquisition arm is constant zero under `stable` and `at_T` ({} of {} rules); every D3 region "
                          "built from random rules has zero within-region variance and is SKIPPED, and this does not change "
                          "with completion because the value is constant by construction of the criterion, not by sample size "
                          "(Harmonia a1d0ed9c8). cs-c3-2 answers G1, H1 and Q2; it CANNOT answer H2, and that is a vacuous "
                          "reading, never evidence against it.".format(zeros, len(acq)),
                "next": "C3-3 under R-C3-1..5 with a criterion whose attainable range for random tables is not a point "
                        "(Herakles cellwise_majority_match: random 0.4998 over [0.4939, 0.5099])"}
    return {"status": "PARTIAL", "reason": "acquisition arm incomplete; D3 needs eight independent rules per descriptor region"}



def to_markdown(r: Dict[str, Any]) -> str:
    L = ["# C3-2 readout ({}) -- {}".format(r["candidate_set"], "COMPLETE" if r["complete"] else "PARTIAL"),
         "", "Written {}. Numbers only; Harmonia rules. Unit for accuracy: the IC sample (four shared samples, one seed_root). Unit for D3: the rule.".format(r["written"]),
         "", "## Progress", ""]
    for arm, st in sorted(r["status_by_arm"].items()):
        L.append("- {}: {}".format(arm, ", ".join("{} {}".format(v, k) for k, v in sorted(st.items()))))
    L += ["", "## Exact-symmetry null (C3-null vs its C3-hist twin)", "",
          "Fields compared per IC sample: {}. Spacetime digest excluded by design (declared not an image under a transform).".format(", ".join(r["null_identity"]["fields"])),
          "", "- checked {n}: IDENTICAL {identical}, NOT_IDENTICAL {not_identical}, INDETERMINATE {indeterminate}".format(**r["null_identity"]), ""]
    for c in r["null_identity"]["checked"]:
        L.append("- {}:{} -> {}{}".format(c["genome"], c["transform"], c["verdict"],
                                          "" if not c.get("diffs") else " " + json.dumps(c["diffs"][:2])))
    L += ["", "## Per-rule accuracy by IC sample (stable criterion)", ""]
    for t in r["table"]:
        if t["arm"] == "C3-null":
            continue
        L.append("- {} {}: {} mean {}{}".format(t["arm"], t["label"], t["accuracy_by_sample"],
                                                 None if t["mean"] is None else round(t["mean"], 3),
                                                 "" if all(t["criteria_agree"]) else "  (criteria DISAGREE on some sample)"))
    L += ["", "IC-sample column means (all non-null completed rows): {}".format([None if m is None else round(m, 4) for m in r["ic_sample_means"]]),
          "", "## ICC(1), rule as group, four IC samples as measures", "",
          "- all rules: {}".format(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r["icc1_rules_all"].items()})),
          "- excluding structural zeros (rules with 0.0 on every sample under `stable`): {}".format(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r["icc1_rules_excluding_structural_zeros"].items()})),
          "", "## Structural zeros", "", "- {}".format(json.dumps(r["structural_zeros"])),
          "", "## D3 over C3", "", "- {}".format(json.dumps(r["d3_over_c3"])), ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.c3_readout")
    ap.add_argument("--out", default="archaeon/docs/h0h5/C3_2_READOUT")
    a = ap.parse_args(argv)
    from evidence_wiki.ew import db as ewdb
    conn = ewdb.connect()
    try:
        rows = fetch(conn)
    finally:
        conn.close()
    r = readout(rows)
    with open(a.out + ".json", "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, sort_keys=True)
    with open(a.out + ".md", "w", encoding="utf-8") as f:
        f.write(to_markdown(r))
    print(json.dumps({"complete": r["complete"], "n_completed": r["n_completed"], "null": {k: r["null_identity"][k] for k in ("n", "identical", "not_identical", "indeterminate")},
                      "icc1_all": r["icc1_rules_all"].get("icc1"), "icc1_nonzero": r["icc1_rules_excluding_structural_zeros"].get("icc1"),
                      "sample_means": r["ic_sample_means"]}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
