"""RB-5: spot-check that the cached exact Q2 used in the census
(rb2_common.qualify_cached) equals a17.qualify(a17.Prov({Q2_NAME: ...}), Q2_NAME,
'RB2') on RB-5 witnesses (T4-admissible class representatives). Forensic."""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rb5_common as C      # noqa: E402


def main(n=8):
    C.worker_init()
    import rb2_common as R2
    progs = []
    ea = json.loads((HERE / "EC_ANALYSIS.json").read_text(encoding="utf-8"))["families"]
    for f, v in ea.items():
        for gr in v.values():
            for c in gr["classes"]:
                if c["t4_admissible"] and c["prog"][0] == "fold":
                    progs.append(tuple(c["prog"]))
    for l in (HERE / "OEIS_SEARCH.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        for gr in ("g4", "g5"):
            for c in r.get(gr, {}).get("classes", []):
                if c["t4_admissible"] and c["prog"][0] == "fold":
                    progs.append(tuple(c["prog"]))
    progs = sorted(set(progs))
    rng = random.Random(C.LABEL + "/q2check")
    pick = rng.sample(progs, min(n, len(progs)))
    rows = []
    for p in pick:
        _, i, b, f = p
        fast = R2.qualify_cached(i, b, f)
        ref = C.a17.qualify(C.a17.Prov({R2.Q2_NAME: (b, f, i)}), R2.Q2_NAME, R2.Q2_LABEL)
        rows.append({"prog": list(p), "cached": fast, "a17_qualify": ref, "equal": fast == ref})
        print(rows[-1], flush=True)
    out = {"n": len(rows), "all_equal": all(r["equal"] for r in rows), "rows": rows,
           "note": "Q2 family name %s, label %s (as RB-2)" % (R2.Q2_NAME, R2.Q2_LABEL)}
    (HERE / "Q2_SPOTCHECK.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
