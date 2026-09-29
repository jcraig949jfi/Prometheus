"""Apply PLAN.md s5 decision rules (frozen) to out/engine.json vs out/predictions.json."""
import json

import numpy as np

import conditions as C

GAPS = C.GAPS
THR = 0.65


def interval(curve):
    ok = [g for g in GAPS if curve[g] >= THR]
    return (min(ok), max(ok)) if ok else None


def iv_holds(a, b):
    if a is None or b is None:
        return a is None and b is None
    return abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1


if __name__ == "__main__":
    pred = json.loads((C.HERE / "out/predictions.json").read_text())
    eng = json.loads((C.HERE / "out/engine.json").read_text())
    rows, out = [], {}
    for key, rec in eng.items():
        if len(rec) < len(GAPS):
            continue
        m = {g: rec[str(g)][0] for g in GAPS}
        lo = {g: rec[str(g)][1] for g in GAPS}
        r = {"measured": m, "lo99": lo}
        for mode in ("sat", "nosat"):
            p = {g: pred[key][mode][str(g)] for g in GAPS}
            mae = float(np.mean([abs(m[g] - p[g]) for g in GAPS]))
            r[mode] = {"mae": mae, "fit": mae <= 0.07, "iv_pred": interval(p),
                       "iv_holds": iv_holds(interval(m), interval(p)),
                       "argmax_pred": max(GAPS, key=lambda g: p[g])}
        r["iv_meas"] = interval(m)
        r["argmax_meas"] = max(GAPS, key=lambda g: m[g])
        out[key] = r
        s = r["sat"]
        rows.append(f"{key:22s} MAE {s['mae']:.3f} {'FIT' if s['fit'] else 'no '} "
                    f"iv meas {r['iv_meas']} pred {s['iv_pred']} {'HOLD' if s['iv_holds'] else 'miss'} "
                    f"| nosat MAE {r['nosat']['mae']:.3f} | peak m{r['argmax_meas']} p{s['argmax_pred']}")
    print("\n".join(rows))
    # gold standard over non-base physics / env / program conditions
    for mode in ("sat", "nosat"):
        test = [k for k in out if not k.startswith(("base:", "_"))]
        good = [k for k in test if out[k][mode]["fit"] and out[k][mode]["iv_holds"]]
        frac = len(good) / max(1, len(test))
        verdict = "PREDICTS" if frac >= 0.75 else "PARTIAL" if frac >= 0.5 else "FAILS"
        print(f"[{mode}] gold standard: {len(good)}/{len(test)} = {frac:.2f} -> {verdict}")
        out[f"_gold_{mode}"] = {"n": len(test), "good": len(good), "verdict": verdict,
                                "bad": sorted(set(test) - set(good))}
    # specific predictions
    champs = ["4ab2ba01", "fresh1", "fresh2", "fresh3"]
    sp = {}
    if all(f"ad0:{c}" in out for c in champs):
        sp["P-a"] = all(out[f"ad0:{c}"]["lo99"][g] <= 0.55 for c in champs for g in GAPS if g >= 13)
    if all(f"base:{c}" in out for c in champs):
        b = [out[f"base:{c}"]["measured"] for c in champs]
        sp["P-b"] = sum(x[7] > x[8] > x[9] for x in b) >= 3
        sp["P-b_detail"] = [(x[7], x[8], x[9]) for x in b]
        spec = np.mean([b[0][g] for g in range(2, 6)])
        fr = [np.mean([x[g] for g in range(2, 6)]) for x in b[1:]]
        if "pr0:4ab2ba01" in out:
            pr = np.mean([out["pr0:4ab2ba01"]["measured"][g] for g in range(2, 6)])
            sp["P-c"] = bool(spec < min(fr) and pr - spec >= 0.05)
            sp["P-c_detail"] = {"spec": spec, "fresh": fr, "pr0_spec": pr}
    for c in ("4ab2ba01", "fresh3"):
        if f"pipe:{c}" in out and f"base:{c}" in out:
            bm, pm = out[f"base:{c}"], out[f"pipe:{c}"]
            ivb, ivp = bm["iv_meas"], pm["iv_meas"]
            ok = (ivb and ivp and abs(pm["argmax_meas"] - bm["argmax_meas"] - 2) <= 1
                  and abs(ivp[0] - ivb[0] - 2) <= 1 and abs(ivp[1] - ivb[1] - 2) <= 1)
            sp[f"P-e:{c}"] = bool(ok)
            sp[f"P-e:{c}_detail"] = {"base_iv": ivb, "pipe_iv": ivp, "base_peak": bm["argmax_meas"],
                                    "pipe_peak": pm["argmax_meas"]}
    if "canon:uniform" in eng and "base:fresh3" in out and "canon:specimen" in eng:
        def mae(a, b):
            return float(np.mean([abs(out[a]["measured"][g] - out[b]["measured"][g]) for g in GAPS]))
        sp["P-f"] = {"uniform_vs_fresh3": mae("canon:uniform", "base:fresh3"),
                     "uniform_vs_fresh1": mae("canon:uniform", "base:fresh1"),
                     "specimen_vs_4ab2": mae("canon:specimen", "base:4ab2ba01")}
        sp["P-f_holds"] = (sp["P-f"]["uniform_vs_fresh3"] <= 0.07 and sp["P-f"]["specimen_vs_4ab2"] <= 0.07)
    # interval moves vs base
    mv = {}
    for k in out:
        if k.startswith("_") or k.startswith("base:") or k.startswith("canon"):
            continue
        cond, c = k.split(":")
        if f"base:{c}" not in out:
            continue
        ivb, ivm, ivp = out[f"base:{c}"]["iv_meas"], out[k]["iv_meas"], out[k]["sat"]["iv_pred"]
        mv[k] = {"base": ivb, "meas": ivm, "pred": ivp,
                 "moved_as_predicted": bool(ivb and ivm and ivp and out[k]["sat"]["iv_holds"]
                                            and (abs(ivm[0] - ivb[0]) >= 2 or abs(ivm[1] - ivb[1]) >= 2))}
    out["_specific"] = sp
    out["_moves"] = mv
    print(json.dumps(sp, indent=1, default=str))
    for k, v in mv.items():
        print(k, v)
    (C.HERE / "out/evaluation.json").write_text(json.dumps(out, indent=1, default=str))
