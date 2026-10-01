"""W2-K Q3: keep probabilities of lens_swap census classes (frozen classify(): SITE fS>=.80, CHANNEL fC>=.80,
MIXTURE fS,fC>=.15 & fS+fC>=.70 & phi_hi<-.30, NEITHER fN>=.50, else UNRESOLVED; gates eligible>=20,
identity>=.90) from the SAVED census records in research/workers/W-M..W-Z/out (no re-evaluation).

Every dict in those files carrying fS/fC/fN/eligible/identity/ci99 is a census record. SE of each fraction is
taken from its recorded 99% pair-bootstrap CI: se = (hi - lo) / (2 * 2.5758) (the bootstrap resamples mirror
pairs, so this is the pair-unit SE). fS+fC uses se(fN) when fX = ftie = 0 (then fS+fC = 1 - fN exactly), else
sqrt(se_S^2 + se_C^2) (conservative-ish; covariance ignored). phi_hi is itself a bound; its distance uses se_phi
from the phi CI width.
For each record: the class recomputed by lens_swap.classify (checked against the recorded class), and for each
condition of the decision list whose flip ALONE changes the class, its SE distance d. Reported: d_min, keep
(predictive) = Phi(d_min/sqrt 2), and keep_all = prod Phi(d_i/sqrt 2) over class-changing conditions
(independence approximation). Census records with no CI are counted, not scored.
"""
import glob
import json
import math
import os
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))
from scipy.stats import norm  # noqa: E402

from prometheus.ananke import lens_swap  # noqa: E402

Q = 2.5758
WORKERS = [f"W-{c}" for c in "MNOPQRSTUVWXYZ"]


def walk(o, path):
    if isinstance(o, dict):
        if all(k in o for k in ("fS", "fC", "fN", "eligible")):
            yield path, o
        for k, v in o.items():
            yield from walk(v, path + [str(k)])
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + [str(i)])


def records():
    for w in WORKERS:
        for fn in sorted(glob.glob(str(REPO / "roles/Ananke/research/workers" / w / "out" / "**" / "*.json*"),
                                   recursive=True)):
            try:
                if fn.endswith(".jsonl"):
                    objs = [(i, json.loads(l)) for i, l in enumerate(open(fn, encoding="utf-8")) if l.strip()]
                else:
                    objs = [(0, json.load(open(fn, encoding="utf-8")))]
            except Exception:                      # noqa: BLE001
                continue
            for line, o in objs:
                for path, rec in walk(o, []):
                    yield os.path.relpath(fn, REPO / "roles/Ananke/research/workers").replace("\\", "/"), line, \
                        "/".join(path), rec


def se_of(ci):
    return None if not ci or ci[0] is None else (ci[1] - ci[0]) / (2 * Q)


def conditions(c):
    """(name, stat, cut, se, holds) for every threshold of classify()."""
    ci = c.get("ci99") or {}
    sS, sC, sN = se_of(ci.get("fS")), se_of(ci.get("fC")), se_of(ci.get("fN"))
    fX = (c.get("fX") or 0) + (c.get("ftie") or 0)
    sSC = sN if (fX == 0 and sN is not None) else (
        math.hypot(sS, sC) if sS is not None and sC is not None else None)
    phi_ci = ci.get("phi")
    phi_hi = phi_ci[1] if phi_ci else None
    s_phi = se_of(phi_ci)
    ident_se = se_of(ci.get("identity"))
    fS, fC, fN = c["fS"], c["fC"], c["fN"]
    out = [("identity>=.90", c["identity"], .90, ident_se),
           ("fS>=.80", fS, .80, sS), ("fC>=.80", fC, .80, sC),
           ("fS>=.15", fS, .15, sS), ("fC>=.15", fC, .15, sC), ("fS+fC>=.70", fS + fC, .70, sSC),
           ("fN>=.50", fN, .50, sN)]
    if phi_hi is not None:
        out.append(("phi_hi<-.30", -phi_hi, .30, s_phi))     # flipped sign: holds iff -phi_hi > .30
    return out


def classify_with(c, override):
    """classify() with one condition forced to the opposite truth value."""
    elig = c["eligible"] >= lens_swap.MIN_ELIGIBLE
    if not elig:
        return "UNDEFINED"
    v = {n: (s >= k if n != "phi_hi<-.30" else s > k) for n, s, k, _ in conditions(c)}
    if "phi_hi<-.30" not in v:
        v["phi_hi<-.30"] = False
    if override:
        v[override] = not v[override]
    if not v["identity>=.90"]:
        return "IDENTITY-BROKEN"
    if v["fS>=.80"]:
        return "SITE"
    if v["fC>=.80"]:
        return "CHANNEL"
    if v["fS>=.15"] and v["fC>=.15"] and v["fS+fC>=.70"] and v["phi_hi<-.30"]:
        return "MIXTURE"
    if v["fN>=.50"]:
        return "NEITHER"
    return "UNRESOLVED"


def main():
    rows, seen = [], set()
    nci = 0
    for fn, line, path, c in records():
        if c.get("fS") is None or c.get("identity") is None:
            continue
        key = (round(c["fS"], 6), round(c["fC"], 6), round(c["fN"], 6), c["eligible"],
               json.dumps(c.get("ci99"), sort_keys=True))
        dup = key in seen
        seen.add(key)
        cls = lens_swap.classify(c) if c.get("ci99") else None
        base = classify_with(c, None)
        if not c.get("ci99"):
            nci += 1
            rows.append({"file": fn, "line": line, "path": path, "dup": dup, "recorded": c.get("class"),
                         "class": base, "scored": False})
            continue
        assert cls == base, (fn, path, cls, base)
        ds = []
        for n, s, k, se in conditions(c):
            if classify_with(c, n) != base:
                d = abs(s - k) / se if se and se > 0 else math.inf
                ds.append((n, round(s, 4), k, None if se is None else round(se, 4), d,
                           classify_with(c, n)))
        dmin = min((x[4] for x in ds), default=math.inf)
        keep = 1.0 if math.isinf(dmin) else float(norm.cdf(dmin / math.sqrt(2)))
        keep_all = 1.0
        for x in ds:
            if not math.isinf(x[4]):
                keep_all *= float(norm.cdf(x[4] / math.sqrt(2)))
        rows.append({"file": fn, "line": line, "path": path, "dup": dup, "recorded": c.get("class"),
                     "class": base, "eligible": c["eligible"], "fS": c["fS"], "fC": c["fC"], "fN": c["fN"],
                     "d_min": None if math.isinf(dmin) else round(dmin, 3), "keep": round(keep, 4),
                     "keep_all": round(keep_all, 4), "nearest": None if not ds else min(ds, key=lambda x: x[4])[:4]
                     + (min(ds, key=lambda x: x[4])[5],), "scored": True})
    sc = [r for r in rows if r["scored"]]
    uniq = [r for r in sc if not r["dup"]]
    mism = [r for r in sc if r["recorded"] and r["recorded"] != r["class"]]
    summ = {"records": len(rows), "scored": len(sc), "unique_scored": len(uniq), "no_ci": nci,
            "recorded_vs_recomputed_mismatch": len(mism),
            "class_counts_unique": Counter(r["class"] for r in uniq)}
    for cls in ("SITE", "CHANNEL", "NEITHER", "MIXTURE", "UNRESOLVED", "IDENTITY-BROKEN", "UNDEFINED"):
        rr = [r for r in uniq if r["class"] == cls]
        if not rr:
            continue
        dd = [r["d_min"] if r["d_min"] is not None else math.inf for r in rr]
        summ[cls] = {"n": len(rr), "within_1SE": sum(d < 1 for d in dd), "within_2SE": sum(d < 2 for d in dd),
                     "within_2.33SE": sum(d < 2.33 for d in dd),
                     "expected_flips_on_rerun": round(sum(1 - r["keep"] for r in rr), 2),
                     "expected_flips_all_conditions": round(sum(1 - r["keep_all"] for r in rr), 2)}
    sc_ = [r for r in uniq if r["class"] in ("SITE", "CHANNEL", "NEITHER")]
    summ["SCN"] = {"n": len(sc_), "within_1SE": sum((r["d_min"] or math.inf) < 1 for r in sc_),
                   "within_2.33SE": sum((r["d_min"] or math.inf) < 2.33 for r in sc_),
                   "expected_flips": round(sum(1 - r["keep"] for r in sc_), 2)}
    summ["by_worker_SCN_within_1SE"] = Counter(r["file"].split("/")[0] for r in sc_
                                               if (r["d_min"] or math.inf) < 1)
    summ["by_worker_SCN"] = Counter(r["file"].split("/")[0] for r in sc_)
    json.dump({"summary": summ, "rows": rows, "mismatch": mism[:50]},
              open(HERE / "out" / "census_keep.json", "w"), indent=1, default=str)
    print(json.dumps(summ, indent=1, default=str))
    print("SCN within 1 SE:")
    for r in sorted(sc_, key=lambda r: r["d_min"] if r["d_min"] is not None else 99):
        if (r["d_min"] or math.inf) < 1:
            print(f'{r["file"]}:{r["line"]} {r["path"][:60]} {r["class"]} fS {r["fS"]:.3f} fC {r["fC"]:.3f} '
                  f'fN {r["fN"]:.3f} d {r["d_min"]} keep {r["keep"]} nearest {r["nearest"]}')


if __name__ == "__main__":
    main()
