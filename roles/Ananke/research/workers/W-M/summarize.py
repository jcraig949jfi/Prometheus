"""Summarise out/census_*.json against W-I reader letters; apply the frozen
single-vs-every change rule and the KA7 handoff rule."""
import csv, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[4])); sys.path.insert(0, str(HERE))
import lens_ins6 as L
import numpy as np
WI = HERE.parent / "W-I" / "out"
CELLS = "2dccdaa5 c16d5231 78f3b0ec 8c37f32e e06701a5 369f5a5b 4781b0a1".split()
NONINFO = ("UNDEFINED", "UNRESOLVED", "IDENTITY-BROKEN")


def f2(x):
    return "  - " if x is None else f"{x:.2f}"


def ci(c, k):
    v = c["ci99"].get(k)
    return "[   -   ]" if not v else f"[{v[0]:+.2f},{v[1]:+.2f}]"


def changed(a, b):
    if a in NONINFO or b in NONINFO:
        return False
    return a != b


out = {"cells": {}}
lines = []
for spec in CELLS + ["E2", "E1"]:
    p = HERE / "out" / f"census_{spec}.json"
    if not p.exists():
        lines.append(f"{spec}: MISSING"); continue
    r = json.loads(p.read_text())
    for mode in ("every", "single"):          # recompute follow census with the fixed code (LOG A7)
        z = np.load(HERE / "out" / f"raw_{spec}_{mode}.npz")
        for o in map(str, r["offsets"]):
            f = L.census_follow(z["normal__s0"], z[f"{o}__s0_site"], z[f"{o}__s0_chan"], z["normal__scored"],
                                r["trials"], n_boot=2000)
            f["class"] = L.classify(f)
            r[mode]["offsets"][o]["follow"] = f
    wi = {}
    if (WI / f"table_{spec}.csv").exists():
        for row in csv.DictReader(open(WI / f"table_{spec}.csv")):
            wi[row["o"]] = row
    lines.append(f"\n== {spec} {r['family']} ro_off {r['ro_off']} normal every {r['every']['normal']}")
    lines.append(" o  WI  sumWI | EVERY frozen/follow        | SINGLE frozen/follow       | single frozen: elig ident fS fC fN  phi ci99 | single follow: elig ident fS fC fN phi")
    rec = {}
    for o in map(str, r["offsets"]):
        e, s = r["every"]["offsets"][o], r["single"]["offsets"][o]
        w = wi.get(o, {})
        ch_frozen = changed(e["class"], s["class"])
        ch_follow = changed(e["follow"]["class"], s["follow"]["class"])
        mix_flip = (e["class"] == "MIXTURE") != (s["class"] == "MIXTURE") or \
                   (e["follow"]["class"] == "MIXTURE") != (s["follow"]["class"] == "MIXTURE")
        rec[o] = {"wi_reader": w.get("reader"), "wi_sum": w.get("sum"), "wi_phi": w.get("phi"),
                  "every": e["class"], "every_follow": e["follow"]["class"],
                  "single": s["class"], "single_follow": s["follow"]["class"],
                  "changed": ch_frozen or ch_follow or mix_flip,
                  "single_stats": {k: s[k] for k in ("eligible", "identity", "fS", "fC", "fN", "phi")},
                  "single_ci": s["ci99"],
                  "single_follow_stats": {k: s["follow"].get(k) for k in ("eligible", "identity", "fS", "fC", "fN", "phi")},
                  "single_follow_ci": s["follow"]["ci99"],
                  "every_stats": {k: e[k] for k in ("eligible", "identity", "fS", "fC", "fN", "phi")},
                  "every_follow_stats": {k: e["follow"].get(k) for k in ("eligible", "identity", "fS", "fC", "fN", "phi")}}
        sf = s["follow"]
        lines.append(f"{o:>2}  {w.get('reader','?'):>2} {w.get('sum','?'):>5} | {e['class'][:10]:>10}/{e['follow']['class'][:10]:<10} | "
                     f"{s['class'][:10]:>10}/{sf['class'][:10]:<10} | {s['eligible']:>4} {f2(s['identity'])} {f2(s['fS'])} {f2(s['fC'])} {f2(s['fN'])} "
                     f"{f2(s['phi'])} {ci(s,'phi')} | {sf['eligible']:>4} {f2(sf['identity'])} {f2(sf['fS'])} {f2(sf['fC'])} {f2(sf['fN'])} {f2(sf['phi'])}"
                     + ("  <== CHANGED" if rec[o]["changed"] else ""))
    ro = r["ro_off"]
    if spec in ("E1", "E2"):
        for mode in ("every", "single"):
            h = L.handoff(r[mode]["offsets"], ro)
            rec[f"handoff_{mode}"] = h
            lines.append(f"  handoff {mode}: {h}")
    out["cells"][spec] = rec
txt = "\n".join(lines)
print(txt)
(HERE / "out" / "summary.txt").write_text(txt)
(HERE / "out" / "summary.json").write_text(json.dumps(out, indent=1, default=float))
