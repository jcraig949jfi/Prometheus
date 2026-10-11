"""BEL-48H Window 3 analysis (frozen classification, BEL_48H_PREREG.md s6; committed before the W3a replays were read).

    python3 analyze_w3.py RESULTS.jsonl OUT.json [LABEL]"""
import json
import sys
from collections import Counter

from analyze_w2 import wilson


def classify(e, L=64):
    kind = e["kind"]
    steps = len(e.get("necessary_changed") or []) if kind in ("MUTATION", "SELF_CONSTRUCT", "UPTAKE", "SELF_MOVE", "OTHER") else None
    pre = e.get("old_copy_extent")
    via = e.get("critical_via") or ""
    assisted = (e.get("carrier_mech") not in (None, "init", "seed", "transplant")) and via.count("i") * 2 >= max(1, len(via))
    if kind in ("UPTAKE", "BORN_ASSEMBLY", "BORN_CONSTRUCT"):
        pathway = "ASSEMBLY"
    elif pre is None:
        pathway = "BORN_OTHER"
    elif pre > 0:
        pathway = "INCREMENTAL"
    elif steps is not None and steps >= 2:
        pathway = "ATOMIC"
    else:
        pathway = "SINGLE_STEP_FROM_NOTHING"
    return {"cause": kind, "steps": steps, "precursor": pre, "assisted": assisted, "pathway": pathway}


def main(res_path, out_path, label="W3a"):
    R = [json.loads(l) for l in open(res_path)]
    voids = [r for r in R if r.get("void")]
    R = [r for r in R if not r.get("void")]
    out = {"label": label, "n": len(R) + len(voids), "voids": len(voids),
           "replay_identical": sum(1 for r in R if r.get("replay_identical")), "replay_checked": sum(1 for r in R if "replay_identical" in r)}
    rows = []
    for r in R:
        e = (r.get("origin") or {}).get("origin_event")
        if not e:
            rows.append({"id": r["id"], "cell": r.get("cell"), "arm": r.get("arm"), "origin": None}); continue
        c = classify(e)
        rc = r.get("reach") or {}
        c.update({"id": r["id"], "cell": r.get("cell"), "arm": r.get("arm"), "tick": e["tick"], "n_critical": len(e.get("critical") or []),
                  "critical_via": e.get("critical_via"), "ldir_critical": rc.get("ldir_critical"),
                  "zero_to_halt_func": rc.get("func_zero_to_halt"), "uptake_bytes": (r["origin"]["O"] or {}).get("uptake_bytes", 0),
                  "history_kinds": "".join(h[1][0] for h in (e.get("history") or e.get("writer_history") or [])),
                  "history_extents": [h[2] for h in (e.get("history") or e.get("writer_history") or [])]})
        rows.append(c)
    got = [x for x in rows if x.get("cause")]
    n = len(got)
    out["rows"] = rows
    out["cause"] = dict(Counter(x["cause"] for x in got))
    out["pathway"] = dict(Counter(x["pathway"] for x in got))
    out["assisted"] = sum(1 for x in got if x["assisted"])
    st = [x for x in got if x["steps"] is not None]
    one = sum(1 for x in st if x["steps"] == 1)
    out["W3-P1"] = {"steps_eq_1": [one, len(st)], "wilson": wilson(one, len(st)), "holds": (one / len(st) >= 0.6) if st else "NOT_TESTABLE",
                    "steps_hist": dict(Counter(x["steps"] for x in st))}
    inc = sum(1 for x in got if x["pathway"] == "INCREMENTAL")
    out["W3-P2"] = {"incremental": [inc, n], "wilson": wilson(inc, n), "holds": (inc / n >= 0.4) if n else "NOT_TESTABLE",
                    "precursor_hist": dict(Counter(x["precursor"] for x in got))}
    out["W3-P3"] = {"replay_identical": [out["replay_identical"], out["replay_checked"]],
                    "holds": out["replay_identical"] == out["replay_checked"] == len(R) and len(R) > 0}
    ld = sum(1 for x in got if x.get("ldir_critical")); zh = sum(1 for x in got if x.get("zero_to_halt_func") is False)
    out["W3-P4"] = {"ldir_critical": [ld, n], "nop_slide_dependent": [zh, n], "holds": n > 0 and ld == n and zh / n >= 0.5}
    out["no_origin_event"] = sum(1 for x in rows if x.get("origin") is None and not x.get("cause"))
    json.dump(out, open(out_path, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in out if k != "rows"}, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
