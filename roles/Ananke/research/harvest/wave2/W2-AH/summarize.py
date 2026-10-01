import json, sys, numpy as np, pathlib
HERE = pathlib.Path(__file__).resolve().parent
which = sys.argv[1]
d = json.load(open(HERE / "out" / f"rows_{which}.json"))
rows = d["rows"]
names = [k for k in rows[0] if k not in ("cell", "wave", "family", "base", "li", "rep", "economy", "recorded", "ka_match")
         and not k.endswith("_lo99") and not k.endswith("_emit_per_world")]
names = sorted(set(names) | ({"relay_flood"} if any("relay_flood" in r for r in rows) else set()))
for wave in ("B", "B2"):
    for base in sorted({r["base"] for r in rows}):
        for lvl in ("off", "low", "high"):
            R = [r for r in rows if r["wave"] == wave and r["base"] == base and r["economy"] == lvl]
            if not R: continue
            s = f"{wave:2s} b{base} {lvl:4s} rec " + " ".join(f"{r['recorded']:.3f}" for r in R)
            for n in names:
                if n in R[0]:
                    s += f" | {n} " + " ".join(f"{r[n]:.3f}" for r in R) + " lo " + " ".join(f"{r[n+'_lo99']:.3f}" for r in R) \
                         + f" em {np.mean([r[n+'_emit_per_world'] for r in R]):.0f}"
            if "ka_match" in R[0]:
                s += " KA " + str(all(r["ka_match"] for r in R))
            print(s)
print(d["compute"])
