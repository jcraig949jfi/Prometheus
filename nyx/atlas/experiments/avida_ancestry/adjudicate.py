"""Reference harness for MECH-AVIDA-ANCESTRY-RETENTION-001. THIS IS THE ONLY MODULE THAT OPENS THE BODY'S .spop FILES.

The packet author (Nyx) wrote it and tested it on synthetic fixtures only (nyx/tests/test_avida_ancestry.py) and has
NOT run it against the body: the packet is blind. It is offered to the adjudicator as a convenience; an independent
harness is better evidence, and the packet's rows are defined by the packet text, not by this file.

    TECHNE_FOSSIL_VAULT=<vault holding avida> python -m nyx.atlas.experiments.avida_ancestry.adjudicate --adjudicator <seat> [out.json]

Verdict per row: PREDICTION_INDETERMINATE when nothing was eligible (nothing could have fired), SUPPORTED when the
violation count is 0 among a non-zero eligible count, PREDICTION_FAILED otherwise (offending files listed).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from nyx.atlas.experiments.avida_ancestry import spop
from nyx.atlas.experiments.avida_ancestry.strata import OUT as STRATA, stratum

ROWS = {  # intervention -> (stratum, [violation keys], eligible key)
    "I1-PARENT-CLOSURE": ("S_A", ["I1_dangling_parent_refs"], "I1_eligible_parent_refs"),
    "I2-NO-DEAD-LEAF": ("S_B", ["I2_dead_leaves"], "I2_eligible_dead_rows"),
    "I3-DEPTH-IS-PARENT-PLUS-ONE": ("S_A", ["I3_depth_violations"], "I3_eligible_rows"),
    "I4-LIVING-GENOME-IS-A-KEY": ("S_B", ["I4_live_duplicate_keys"], "I4_eligible_live_rows"),
    "I5-HISTORIC-OFF-WRITES-NO-DEAD-ROW": ("S_H0", ["I5_dead_rows"], "I5_eligible_rows"),
    "I6-CLOCK-FENCEPOST": ("S_B", ["I6_born_at_zero", "I6_born_after_T_plus_1"], "I6_eligible_rows"),
}


def _verdict(count: int, eligible: int) -> str:
    return "PREDICTION_INDETERMINATE" if eligible == 0 else ("SUPPORTED" if count == 0 else "PREDICTION_FAILED")


def run(strata: dict, load) -> dict:
    """load(row) -> (text, sha256 of the bytes) or None when the file is absent on this host."""
    per_file, missing, hash_mismatch = [], [], []
    for row in strata["files"]:
        got = load(row)
        if got is None:
            missing.append(row["path"]); continue
        text, sha = got
        if sha != row["sha256"]:
            hash_mismatch.append(row["path"]); continue
        f = spop.read_text(text, row["path"].split("/")[-1])
        m = spop.measure(f)
        m["in_scope"] = f["in_scope"]
        per_file.append({"row": row, "file": f, "m": m, "strata": stratum(row, m)})

    out = {"schema": "nyx.avida_ancestry_adjudication/1", "n_files": len(strata["files"]), "missing": missing, "hash_mismatch": hash_mismatch,
           "population_files_in_scope": sum(1 for p in per_file if p["m"]["in_scope"] and p["row"]["kind"] == "population"),
           "in_scope_files_with_unparsed_rows": [p["row"]["path"] for p in per_file if p["m"]["in_scope"] and p["m"]["n_unparsed"]],
           "stratum_sizes": {s: sum(1 for p in per_file if p["strata"][s]) for s in ("S_A", "S_B", "S_H0")},
           "stratum_distinct_sha": {s: len({p["row"]["sha256"] for p in per_file if p["strata"][s]}) for s in ("S_A", "S_B", "S_H0")},
           "rows": {}}
    for iid, (s, keys, ek) in ROWS.items():
        members = [p for p in per_file if p["strata"][s]]
        count = sum(p["m"][k] for p in members for k in keys)
        elig = sum(p["m"][ek] for p in members)
        out["rows"][iid] = {"stratum": s, "files": len(members), "violations": count, "eligible": elig, "verdict": _verdict(count, elig),
                            "offending_files": [p["row"]["path"] for p in members if any(p["m"][k] for k in keys)][:40]}
    # series rows
    v7 = e7 = v8 = e8 = 0
    ser = {}
    for name in sorted({p["row"]["series"] for p in per_file if p["row"]["series"]}):
        members = [p for p in per_file if p["row"]["series"] == name and p["strata"]["S_B"]]
        sever = next((p["row"]["sever_at"] for p in members), None)
        r = spop.measure_series([p["file"] for p in members], sever_at=sever)
        ser[name] = {k: v for k, v in r.items() if k != "R_loss_curve"}
        ser[name]["files_in_S_B"] = len(members)
        ser[name]["R_loss_curve"] = r["R_loss_curve"]
        v7 += r["I7_missing_at_earlier_save"] + r["I7_changed_immutable_fields"]; e7 += r["I7_eligible_rows"]
        if sever is not None:
            v8 += r["I8_rows_stamped_before_severance"] + r["I8_roots_not_stamped_at_severance"]
            e8 += r["I8_eligible_rows"] if r["I8_max_rows_in_a_save_before_severance"] > 1 and r["I8_roots"] > 0 else 0
    out["rows"]["I7-SERIES-PERSISTENCE"] = {"stratum": "series in S_B", "violations": v7, "eligible": e7, "verdict": _verdict(v7, e7)}
    out["rows"]["I8-SEVERANCE"] = {"stratum": "series in S_B with a severing event", "violations": v8, "eligible": e8, "verdict": _verdict(v8, e8)}
    out["series"] = ser
    # READOUTS (requested, not predicted): every file, claimed or not
    out["readouts"] = [{"path": p["row"]["path"], "strata": p["strata"], "in_scope": p["m"]["in_scope"],
                        **{k: p["m"][k] for k in ("n_rows", "n_live", "n_dead", "n_roots", "n_unparsed", "n_shifted_rows", "multi_parent", "parasite",
                                                  "I1_dangling_parent_refs", "I2_dead_leaves", "I3_depth_violations", "I4_live_duplicate_keys",
                                                  "I6_born_at_zero", "I6_born_after_T_plus_1", "R_live_rows_with_parent",
                                                  "R_live_rows_whose_parents_are_all_live")}} for p in per_file]
    out["cut_kill"] = out["population_files_in_scope"] == 0
    return out


def _load_from_body(body: Path):
    def load(row):
        p = body / "upstream" / row["path"]
        if not p.is_file():
            return None
        b = p.read_bytes()
        return b.decode("utf-8", errors="replace"), hashlib.sha256(b).hexdigest()
    return load


def main(argv) -> int:
    if len(argv) < 2 or argv[0] != "--adjudicator":
        print(__doc__)
        print("REFUSED: name the adjudicating seat with --adjudicator <seat>. The packet author does not run this.")
        return 2
    if argv[1].strip().lower().startswith("nyx"):
        print("REFUSED: Nyx is the packet author (operator 2026-09-19b s8: the author does not adjudicate).")
        return 2
    from techne.fossils import vault
    body = vault.body_dir("avida")
    res = run(json.loads(STRATA.read_text(encoding="utf-8")), _load_from_body(body))
    res["adjudicator"] = argv[1]
    text = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if len(argv) > 2:
        Path(argv[2]).write_text(text, encoding="utf-8", newline="\n")
    for iid, r in res["rows"].items():
        print(f"{iid:38s} {r['verdict']:26s} violations {r['violations']} / eligible {r['eligible']}")
    print("CUT_KILL" if res["cut_kill"] else f"in-scope population files {res['population_files_in_scope']}; missing {len(res['missing'])}; hash mismatch {len(res['hash_mismatch'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
