"""W-I analysis: labels, trajectory strings, motifs, robustness test (PLAN.md rules)."""
import csv
import itertools
import json
import pathlib
import sys

import numpy as np
from scipy.stats import spearmanr

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.resolve().parents[4]))
import traj  # noqa: E402

OUT = HERE / "out"
PANEL_DIGEST = "d9ccb6a71d986501"
census = {r["cell"]: r for r in csv.DictReader(open(HERE.parent / "W-F/out/census_table.csv"))}
SUB_SKIP = ("site_all", "channel_all", "joint")


def reader_label(d):
    vs, vc, vj = d["site_all"]["verdict"], d["channel_all"]["verdict"], d["joint"]["verdict"]
    a_s, a_c = d["site_all"]["acc"][0], d["channel_all"]["acc"][0]
    if vs == "FLIP" and vc == "FLIP":
        return "D"
    if vs == "FLIP":
        return "S"
    if vc == "FLIP":
        return "C"
    if vj == "FLIP":
        if abs(a_s + a_c - 1) <= 0.15 and d["phi"] is not None and d["phi"] <= -0.3:
            return "M"
        return "J"
    if vs == vc == vj == "NO-EFFECT":
        return "E"
    return "X"


def compress(s):
    return "".join(k for k, _ in itertools.groupby(s))


def motifs_reader(lab):
    m = []
    if lab and all(c in "SD" for c in lab):
        m.append("R1")
    if lab and all(c == "C" for c in lab):
        m.append("R2")
    sc = compress("".join(c for c in lab if c in "SC"))
    if len(sc) >= 2 and sc[0] == "S" and sc[-1] == "C":
        m.append("R3")
    if len(sc) >= 2 and sc[0] == "C" and sc[-1] == "S":
        m.append("R4")
    if len(sc) >= 3:
        m.append("R5")
    if "MM" in lab:
        m.append("R6")
    if "JJ" in lab:
        m.append("R7")
    first = next((i for i, c in enumerate(lab) if c in "SCD"), None)
    if first is not None:
        rest = lab[first:]
        if any(k and len(list(g)) >= 2 for k, g in itertools.groupby(rest, key=lambda c: c in "EX")):
            m.append("R8")
    return m


def motifs_phys(rows, fam):
    m = []
    iv = [r for r in rows if r["interval"]]
    if fam != "HOLD":
        xs = [(r["o"], r["S_dsrc"]) for r in iv if r["S_dsrc"] is not None]
        if len(xs) >= 3:
            rho = spearmanr([a for a, _ in xs], [b for _, b in xs]).correlation
            if rho == rho and rho >= 0.7 and max(b for _, b in xs) >= 2:
                m.append("P1")
    if any((r["fire"] or 0) >= .5 and (r["fl_cnt"] or 0) >= .5 and (r["emit_pay"] or 0) < .2 for r in iv):
        m.append("P2")
    if any((r["fl_pay"] or 0) >= .5 and (r["fl_cnt"] or 0) < .2 for r in iv):
        m.append("P3")
    if not any(max(r["fl_cnt"] or 0, r["fl_pay"] or 0, r["fire"] or 0) >= .5 for r in iv):
        m.append("P4")
    return m


def load_all():
    sp = {}
    for f in sorted(OUT.glob("traj_*.json")):
        r = json.loads(f.read_text())
        sp[r["cell"][:8]] = r
    return sp


PK = ("S", "S_act", "nS", "S_dsrc", "S_dact", "inbox", "Kp", "r", "w", "fl_cnt", "fl_pay", "n_fl",
      "fl_dact", "fire", "n_fire", "fire_dsrc", "fire_at_src", "emit_pay", "emit_chan")


def specimen_rows(r):
    readable = r["normal"][1] >= 0.60
    cl = r["cue_len"]
    tw = r["twin"]["avg"]
    rows = []
    for o_s, d in sorted(r["offsets"].items(), key=lambda x: int(x[0])):
        o = int(o_s)
        ph = tw.get(o_s, {})
        subs = [n for n in r["arms"] if n not in SUB_SKIP and d[n]["verdict"] == "FLIP"]
        sens = [n for n in r["arms"] if n not in SUB_SKIP and d[n]["verdict"] == "CHANCE"]
        row = {"o": o, "interval": o >= cl - 1, "phase": "pre" if o < 0 else ("cue" if o < cl - 1 else "int"),
               "reader": reader_label(d) if readable else "?",
               "site_acc": round(d["site_all"]["acc"][0], 3), "chan_acc": round(d["channel_all"]["acc"][0], 3),
               "sum": round(d["site_all"]["acc"][0] + d["channel_all"]["acc"][0], 3),
               "joint_acc": round(d["joint"]["acc"][0], 3),
               "phi": None if d["phi"] is None else round(d["phi"], 2),
               "site_ident": d["site_all"]["arm_identical"], "chan_ident": d["channel_all"]["arm_identical"],
               "sub_flip": "+".join(subs), "sub_chance": "+".join(sens),
               "phys": traj.phys_label(ph) if ph else ""}
        for k in PK:
            row[k] = None if ph.get(k) is None else round(ph[k], 2)
        rows.append(row)
    return rows, readable


def robust_class(lab):
    if not lab:
        return "OTHER"
    if any(c in "CM" for c in lab):
        return "CHANNEL-USING"
    if sum(c in "SD" for c in lab) / len(lab) >= 0.8:
        return "SITE-ONLY"
    return "OTHER"


def boot_diff(a, b, n=10000, seed=0):
    g = np.random.default_rng(seed)
    a, b = np.asarray(a), np.asarray(b)
    d = [np.median(a[g.integers(0, len(a), len(a))]) - np.median(b[g.integers(0, len(b), len(b))])
         for _ in range(n)]
    return float(np.median(a) - np.median(b)), float(np.quantile(d, .025)), float(np.quantile(d, .975))


def main():
    sp = load_all()
    summ, motif_occ = [], {}
    for c, r in sp.items():
        rows, readable = specimen_rows(r)
        with open(OUT / f"table_{c}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        iv = [x for x in rows if x["interval"]]
        lab = "".join(x["reader"] for x in iv)
        pre = next(x for x in rows if x["o"] == -1)
        mr = motifs_reader(lab) if readable else []
        mp = motifs_phys(rows, r["family"])
        if readable:
            for m in mr + mp:
                motif_occ.setdefault(m, []).append((c, r["phys_digest"]))
        summ.append({"cell": c, "wave": r["wave"], "family": r["family"], "digest": r["phys_digest"],
                     "topology": r["physics"]["topology"], "census": census.get(c, {}).get("class", "?"),
                     "normal": round(r["normal"][0], 3), "lo99": round(r["normal"][1], 3), "readable": readable,
                     "reader_full": lab, "reader": compress(lab),
                     "phys": " ".join(x["phys"] for x in iv),
                     "pre_site": pre["site_acc"], "pre_chan": pre["chan_acc"], "pre_label": pre["reader"],
                     "motifs": "+".join(mr + mp), "rclass": robust_class(lab) if readable else "UNREADABLE"})
    with open(OUT / "traj_table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0]))
        w.writeheader()
        w.writerows(summ)
    named = {m: {"n": len(v), "digests": len({d for _, d in v}), "cells": [c for c, _ in v],
                 "NAMED": len(v) >= 3 and len({d for _, d in v}) >= 2} for m, v in sorted(motif_occ.items())}
    (OUT / "motifs.json").write_text(json.dumps(named, indent=1))
    rb = json.loads((OUT / "robust.json").read_text()) if (OUT / "robust.json").exists() else {}
    S = {s["cell"]: s for s in summ}
    ret = {}
    for c, r in rb.items():
        b = r["base"][0]
        ret[c] = {k: ((v[0] - 0.5) / (b - 0.5) if b > 0.5 else None) for k, v in r.items() if k != "base"}
    tests = {}
    for scope in ("panel", "all"):
        for cond in ("latency", "jitter", "loss", "distractor", "size"):
            def pick(cls):
                return [ret[c][cond] for c in ret if c in S and S[c]["rclass"] == cls and ret[c][cond] is not None
                        and (scope == "all" or (S[c]["digest"] == PANEL_DIGEST and S[c]["family"] == "RELAY"))]
            A, B = pick("SITE-ONLY"), pick("CHANNEL-USING")
            t = {"nSITE": len(A), "nCHAN": len(B), "medSITE": float(np.median(A)) if A else None,
                 "medCHAN": float(np.median(B)) if B else None}
            if len(A) >= 4 and len(B) >= 4:
                d, lo, hi = boot_diff(A, B)
                t.update(diff=d, lo=lo, hi=hi)
                if cond in ("latency", "jitter", "loss"):
                    t["decision"] = ("SUPPORTED" if d >= 0.2 and lo > 0 else
                                     "CONTRADICTED" if hi < 0 else "NOT SUPPORTED")
                else:
                    t["decision"] = "two-sided: " + ("SITE>CHAN" if lo > 0 else "CHAN>SITE" if hi < 0
                                                     else "no difference")
            else:
                t["decision"] = "INCONCLUSIVE (too few)"
            tests[f"{scope}:{cond}"] = t
    (OUT / "robust_tests.json").write_text(json.dumps({"retention": ret, "tests": tests}, indent=1))
    for s in summ:
        print(f"{s['cell']} {s['wave']:2s} {s['family']:5s} {s['topology']:10s} {s['census']:10s} "
              f"n={s['normal']:.3f}/{s['lo99']:.3f} pre={s['pre_label']}({s['pre_site']},{s['pre_chan']}) "
              f"R={s['reader_full']:20s} [{s['reader']}] {s['rclass']} {s['motifs']}")
    print(json.dumps({k: (v["n"], v["digests"], v["NAMED"]) for k, v in named.items()}))
    print(json.dumps(tests, indent=0))


if __name__ == "__main__":
    main()
