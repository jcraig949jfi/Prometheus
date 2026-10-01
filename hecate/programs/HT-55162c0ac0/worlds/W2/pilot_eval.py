"""Pilot evaluator -> PILOT.json (decision rules A9 in NOTES.md)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core as K

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rows = [json.loads(l) for l in open(os.path.join(HERE, "pilot_rows.jsonl"), encoding="utf-8")]
    pos = K.pool(rows, "POSITIVE_CONTROL")
    pos_by_p = {p: pos[K.POS_C][p] for p in K.POS_PS}
    positive = all(f >= 0.8 for f in pos_by_p.values())

    cheat = K.pool(rows, "CHEAT")
    cheat_twin = K.pool(rows, "CHEAT", key="twin_grid")
    crit_cheat = K.criterion(cheat, cheat_twin)
    cheat_detected = crit_cheat["success"]

    null = K.pool(rows, "NULL_TWIN")
    crit_null = K.criterion(null, null)  # part B on itself: does the shuffled fit stabilise p>=2?
    null_meets = bool(crit_null["partA"] or not crit_null["partB"])

    upos = {p: {k: v for k, v in K.find_upo(p)[1].items() if k != "orbit"} for p in K.PS}
    out = dict(positive_meets_success=bool(positive), cheat_detected=bool(cheat_detected),
               null_twin_meets_success=null_meets,
               pilot_pass=bool(positive and cheat_detected and not null_meets),
               stats=dict(positive_pooled_frac_C16=pos_by_p,
                          positive_per_seed=[{p: r["grid"][str(K.POS_C)][str(p)] for p in K.POS_PS}
                                             for r in rows if r["arm"] == "POSITIVE_CONTROL"],
                          cheat_criterion=crit_cheat,
                          cheat_twin_uncontrolled_max_frac=max(v for byp in cheat_twin.values() for v in byp.values()),
                          null_twin_criterion=crit_null,
                          null_twin_pooled_grid=null,
                          upos=upos,
                          cpu_seconds=sum(r["cpu_seconds"] for r in rows)),
               attempt=attempt)
    with open(os.path.join(HERE, "PILOT.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("positive_meets_success", "cheat_detected",
                                         "null_twin_meets_success", "pilot_pass")}))
    print("pos", pos_by_p, "null pmax", crit_null["p_max"], "null twin max", crit_null["twin_max_frac_p_ge_2"])


if __name__ == "__main__":
    main()
