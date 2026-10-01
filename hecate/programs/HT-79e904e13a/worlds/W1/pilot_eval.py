"""Evaluate pilot rows -> PILOT.json. Usage: python pilot_eval.py <attempt>"""
import sys, time
from common import *  # noqa

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
SRC = os.path.join(HERE, "pilot_rows.jsonl" if ATTEMPT == 1 else f"pilot_rows_attempt{ATTEMPT}.jsonl")


def pilot_verdict(rows):
    by = {a: [r for r in rows if r["arm"] == a] for a in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT", "CHEAT_NULL") if any(r["arm"] == a for r in rows)}
    summ = {a: arm_summary(v) for a, v in by.items()}
    pos = positive_meets(summ["POSITIVE_CONTROL"])
    cheat = success(summ["CHEAT"], summ["CHEAT_NULL"] if "CHEAT_NULL" in summ else summ["NULL_TWIN"])
    null_meets = arm_level_success(summ["NULL_TWIN"])
    stats = {a: s for a, s in summ.items()}
    stats["null_twin_le_0.2_at_-0.5_and_-0.2"] = null_le_02(summ["NULL_TWIN"])
    stats["max_logm_imag"] = {a: max(max(r["logm_max_imag"].values()) for r in v) for a, v in by.items()}
    return pos, cheat, null_meets, stats


if __name__ == "__main__":
    t0c, t0w = time.process_time(), time.time()
    pos, cheat, null_meets, stats = pilot_verdict(read_rows(SRC))
    out = {"positive_meets_success": pos, "cheat_detected": cheat,
           "null_twin_meets_success": null_meets,
           "pilot_pass": bool(pos and cheat and not null_meets),
           "stats": stats, "attempt": ATTEMPT, "rows": os.path.basename(SRC)}
    with open(os.path.join(HERE, "PILOT.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    log_cpu("pilot_eval.py", t0c, t0w, {"attempt": ATTEMPT})
    print(json.dumps(out, indent=1))
