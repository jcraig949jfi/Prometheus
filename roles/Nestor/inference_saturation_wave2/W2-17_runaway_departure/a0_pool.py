"""W2-17 a0: the K2b BASE splice-off depth pool, with source and seed per run (read-only, nothing run)."""
import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
C9X = HERE.parents[1] / "campaigns" / "c9x-explore-2026-09-24"

def load():
    rows = []
    for f in (C9X / "c_atomic" / "results").glob("7ae3*_BASE.json"):
        d = json.loads(f.read_text()); rows.append(("c_atomic", f.stem, d["depth"]))
    for r in json.loads((C9X / "x_atomic" / "RESULTS.json").read_text()):
        if r["arm"] == "BASE": rows.append(("x_atomic", r.get("s"), r["depth"]))
    for r in json.loads((C9X / "c_norecomb_confirm" / "RESULTS.json").read_text()):
        if r["spec"].startswith("7ae3") and r["arm"] == "NO_RECOMB": rows.append(("c_norecomb_confirm", r.get("s"), r["depth"]))
    for name in ("c_runaway_confirm", "x_h2_norecomb"):
        for r in json.loads((C9X / name / "RESULTS.json").read_text()):
            if r["arm"] == "NO_RECOMB": rows.append((name, r.get("s"), r["depth"]))
    for name in ("c_critical_mass", "x_critical_mass"):
        for r in json.loads((C9X / name / "RESULTS.json").read_text()):
            if r["k"] == 1: rows.append((name, r.get("s"), r["depth"]))
    for f in (C9X / "x_dose_curve" / "results").glob("*_k1.json"):
        rows.append(("x_dose_curve", f.stem, json.loads(f.read_text())["depth"]))
    for f in (C9X / "x_ticket" / "results").glob("*.json"):
        rows.append(("x_ticket", int(f.stem), json.loads(f.read_text())["depth"]))
    return rows

if __name__ == "__main__":
    rows = load()
    print(len(rows))
    deep = sorted([r for r in rows if r[2] >= 8], key=lambda r: r[2])
    for r in deep: print(r)
    json.dump({"n": len(rows), "depths": [r[2] for r in rows], "deep_ge8": deep}, open(HERE / "a0_pool.json", "w"), indent=0)
