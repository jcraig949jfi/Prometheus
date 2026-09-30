"""Gate-attainability audit for Archaeon SFE campaigns 2-5 (package D001-04, H-D1-21).

For every experiment's attempt-of-record RECEIPT.json, re-derive from the stored
disposition_candidate block (produced by archaeon/wse/states.py:disposition_candidate)
WHY the machine did or did not reach SUPPORTED_POSITIVE, and classify the binding
constraint:

  NO_PATH            primary is a rank_correlation (states.py:171-185 has no
                     SUPPORTED branch) -> unattainable by construction
  EMPTY_BATTERY      effect >= min_effect, n >= 10, but battery declared == 0
                     (states.py:216 requires a non-empty battery) -> unattainable by design
  N_AND_BATTERY      n < 10 and battery empty
  ATTACK_FAILED      battery non-empty, at least one declared attack failed
  EFFECT             effect < min_effect (the data, not the gate, decided)
  TRIVIAL_THRESHOLD  flag: min_effect <= 0, so "effect >= min_effect" is satisfied by a null
  ASSAY/EXEC/UNDERPOWERED  earlier states pre-empted the science ladder

Inputs (all read-only, repo @ 0424c372a6bba88f50d31f3abbd8b1204871bba6):
  archaeon/campaign2/C2-SFE-*/RECEIPT.json
  archaeon/campaign3/C3-SFE-*/RECEIPT.json
  archaeon/campaign4/C4-*/RECEIPT.json     (C4-REH-1 excluded: rehearsal)
  archaeon/campaign5/C5-*/RECEIPT.json
  archaeon/campaign*/FUNNEL.json           (the record's own disposition, for comparison)

Decision rule for the package question ("gates or substrate?"):
  * Let E = experiments whose machine label was WEAK_POSITIVE.
    If most of E are EMPTY_BATTERY / NO_PATH / N_AND_BATTERY, the zero-SUPPORTED count is a
    property of how the gate was USED, and carries little information about the substrate.
  * Let C = experiments whose design made SUPPORTED attainable (non-empty battery, difference
    primary, min_effect > 0). If every member of C stops on EFFECT or ATTACK_FAILED, then
    where the gate could fire, the data (substrate + search) is what stopped it.
  The hand tally in REPORT.md predicts: |E| = 12; EMPTY_BATTERY-only = 4 (C3-SFE-03, C4-01,
  C4-02, C5-01); NO_PATH = 1 (C3-SFE-06); ATTACK_FAILED = 1 (C3-SFE-04); N_AND_BATTERY = 6.
  Run this script to confirm or refute that tally; do not trust the prediction.
"""
import glob
import json
import os
import sys

REPO = sys.argv[1] if len(sys.argv) > 1 else "."


def classify(dc):
    disp = dc.get("disposition")
    ev = dc.get("evidence") or {}
    bat = dc.get("battery") or {}
    if "rho" in ev:
        return disp, "NO_PATH (rank_correlation)"
    if disp in ("ENGINE_FAILURE", "INSTRUMENT_FAILURE"):
        return disp, "EXEC"
    if disp == "UNDERPOWERED":
        return disp, "UNDERPOWERED"
    if disp in ("INTERVENTION_NOT_APPLIED", "RESIDUE_BELOW_FLOOR", "IMMATURE_ARTIFACT",
                "STREAM_BELOW_THRESHOLD", "TARGET_UNREACHABLE", "READOUT_CANNOT_EXPRESS",
                "POSITIVE_CONTROL_FAILED"):
        return disp, "ASSAY"
    if "effect" not in ev:
        return disp, "NO_PRIMARY"
    eff, me = ev["effect"], ev["min_effect"]
    n = min(ev.get("n_treatment", 0), ev.get("n_control", 0))
    flags = []
    if me <= 0:
        flags.append("TRIVIAL_THRESHOLD")
    if eff < me:
        return disp, "EFFECT" + ("+" + "+".join(flags) if flags else "")
    declared = bat.get("declared", 0)
    survived = bat.get("survived", 0)
    attacked = bat.get("attacked", 0)
    if declared and survived < attacked:
        why = "ATTACK_FAILED"
    elif declared == 0 and n >= 10:
        why = "EMPTY_BATTERY"
    elif declared == 0:
        why = "N_AND_BATTERY"
    elif n < 10:
        why = "N"
    else:
        why = "SUPPORTED"
    return disp, why + ("+" + "+".join(flags) if flags else "")


def main():
    rows = []
    for camp in ("campaign2", "campaign3", "campaign4", "campaign5"):
        for p in sorted(glob.glob(os.path.join(REPO, "archaeon", camp, "C*", "RECEIPT.json"))):
            slot = os.path.basename(os.path.dirname(p))
            if "REH" in slot:
                continue
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
            dc = r.get("disposition_candidate") or {}
            disp, why = classify(dc)
            ev = dc.get("evidence") or {}
            rows.append((slot, disp, why, ev.get("effect", ev.get("rho")), ev.get("min_effect", ev.get("min_abs_rho")),
                         ev.get("n_treatment", ev.get("n")), ev.get("n_control"), (dc.get("battery") or {}).get("declared")))
    print("slot | machine | binding | effect/rho | min | n_t | n_c | battery_declared")
    for row in rows:
        print(" | ".join(str(x) for x in row))
    wp = [r for r in rows if r[1] == "WEAK_POSITIVE"]
    print("\nWEAK_POSITIVE:", len(wp))
    from collections import Counter
    print(Counter(r[2].split("+")[0] for r in wp))
    print("SUPPORTED_POSITIVE:", sum(1 for r in rows if r[1] == "SUPPORTED_POSITIVE"))


if __name__ == "__main__":
    main()
