"""Run Herakles's exact-symmetry check (herakles/evca/c3_null_check.py) on
the live C3-2 null rows.

His check pairs rows by twin id and compares mask digest, witness,
incorrect counts and per-sample accuracy; it returns INDETERMINATE unless
the transformed row RECORDS that the initial condition was transformed and,
under complement, that the majority target flipped. Vivarium's ca_density_v0
result carries neither flag (the wrapper applies both by construction,
ca_density.py apply_transform + the library's target recomputation, but does
not say so on the row). So the check is run TWICE and both results are kept:

  raw               the rows exactly as recorded            -> expected INDETERMINATE
  contract_flags    the two flags supplied from the wrapper's source contract,
                    labelled as supplied, not recorded

The gap between the two is a finding for Vivarium: record `ic_transformed`
and `majority_target_flipped` on the result so the check can pass on the
row's own evidence.
"""
from __future__ import annotations

import datetime
import json
from typing import Any, Dict, List

from herakles.evca import c3_null_check as HC


def rows_from_readout(rows: List[Dict[str, Any]], supply_contract_flags: bool) -> List[Dict[str, Any]]:
    """One check row per (rule, IC sample). `rows` is c3_readout.fetch()."""
    out = []
    for r in rows:
        if r["status"] != "completed" or r["arm"] not in ("C3-hist", "C3-null"):
            continue
        genome = r["label"].split(":")[0]
        transform = "none" if r["arm"] == "C3-hist" else r["label"].split(":")[1]
        for i, x in enumerate(r["repeats"]):
            row = {"twin_id": "{}:{}".format(genome, i), "transform": transform,
                   "mask_digest": x.get("mask_digest_stable"),
                   "incorrect_counts": x.get("n_incorrect_stable"),
                   "accuracy_per_sample": x.get("accuracy_stable"),
                   "witness": x.get("misclassified_ic"),
                   "witness_truncated": bool(x.get("witness_truncated", False))}
            if supply_contract_flags and transform != "none":
                row["ic_transformed"] = True                       # vivarium/viv/ca_density.py apply_transform(name, table, ics)
                if "complement" in transform:
                    row["majority_target_flipped"] = True          # the library recomputes the majority target on the transformed IC
                row["_flags_source"] = "supplied from the wrapper's source contract, NOT recorded on the result row"
            out.append(row)
    return out


def run(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    raw = HC.check_rows(rows_from_readout(rows, supply_contract_flags=False))
    flagged = HC.check_rows(rows_from_readout(rows, supply_contract_flags=True))

    def summary(res):
        c = {"IDENTICAL": 0, "NOT_IDENTICAL": 0, "INDETERMINATE": 0}
        for x in res:
            c[x["verdict"]] = c.get(x["verdict"], 0) + 1
        reasons = {}
        for x in res:
            for m in x.get("reasons", []):
                reasons[m[:90]] = reasons.get(m[:90], 0) + 1
        return {"counts": c, "n": len(res), "reasons": reasons}
    return {"schema": "archaeon.c3.null_check_herakles.v0",
            "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "checker": "herakles/evca/c3_null_check.py",
            "raw": {"summary": summary(raw), "results": raw},
            "contract_flags": {"summary": summary(flagged), "results": flagged},
            "finding_for_vivarium": "ca_density_v0 results do not record ic_transformed / majority_target_flipped; "
                                    "Herakles's check is INDETERMINATE on the row's own evidence until they are recorded"}


def main(argv=None) -> int:
    from evidence_wiki.ew import db as ewdb
    from . import c3_readout as R
    conn = ewdb.connect()
    try:
        rows = R.fetch(conn)
    finally:
        conn.close()
    out = run(rows)
    path = "archaeon/docs/h0h5/C3_2_NULL_CHECK_HERAKLES_2026-09-10.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps({"raw": out["raw"]["summary"]["counts"], "contract_flags": out["contract_flags"]["summary"]["counts"],
                      "raw_reasons": out["raw"]["summary"]["reasons"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
