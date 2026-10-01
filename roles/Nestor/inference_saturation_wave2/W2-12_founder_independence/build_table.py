"""W2-12 step 1: one table of every comparable 7ae3 run in c9x (read-only over committed JSON).

Row fields: exp, block (= experiment x seed base), seed, k, splice (ON/OFF), writeback (BASE/ATOMIC),
tier, epochs, depth, p11_events (if recorded), comparable (bool: 7ae3, splice OFF, BASE, tier M, nominal
mutation/copy-error), note.  Seed bases and conditions are taken from each runner's docstring/code
(see SOURCES below).  No world is run.
"""
import glob
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
C = HERE.parents[1] / "campaigns" / "c9x-explore-2026-09-24"
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
TIER, EPOCHS = "M", 2000          # grammar.TIERS["M"]; no runner passes max_epochs

# (exp, file, seed_base, row-filter, k-getter, splice, writeback, comparable-to-pool, note)
SOURCES = []


def rows(f):
    d = json.loads((C / f).read_text())
    return d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))


def add(out, exp, base, r, k, splice, wb, seed=None, comparable=True, note=""):
    s = r.get("s")
    out.append({"exp": exp, "block": exp, "seed_base": base,
                "seed": seed if seed is not None else base + s, "k": k, "splice": splice,
                "writeback": wb, "tier": TIER, "epochs": EPOCHS, "depth": r["depth"],
                "p11_events": r.get("p11_events"), "comparable": comparable, "note": note})


def build():
    out = []
    # --- k-dose blocks (splice OFF, BASE): k-1 extra 7ae3 founders replace random seeds
    for exp, f, base in (("x_dose_curve", "x_dose_curve/RESULTS.json", 9_997_000),
                         ("x_critical_mass", "x_critical_mass/RESULTS.json", 9_993_000),
                         ("c_critical_mass", "c_critical_mass/RESULTS.json", 9_996_000)):
        for r in rows(f):
            add(out, exp, base, r, r["k"], "OFF", "BASE")
    # --- splice ON dose block
    for r in rows("x_h2_7ae3/RESULTS.json"):
        add(out, "x_h2_7ae3", 9_970_000, r, r["k"], "ON", "BASE", comparable=False, note="splice ON")
    # --- splice OFF/ON k=1 arms
    for r in rows("x_h2_norecomb/RESULTS.json"):
        on = r["arm"] == "BASE"
        add(out, "x_h2_norecomb", 9_980_000, r, 1, "ON" if on else "OFF", "BASE", comparable=not on,
            note="arm " + r["arm"])
    for r in rows("c_runaway_confirm/RESULTS.json"):
        on = r["arm"] == "BASE"
        add(out, "c_runaway_confirm", 9_990_500, r, 1, "ON" if on else "OFF", "BASE", comparable=not on,
            note="arm " + r["arm"])
    for r in rows("c_norecomb_confirm/RESULTS.json"):
        if r["spec"] != SPEC:
            continue
        on = r["arm"] == "BASE"
        add(out, "c_norecomb_confirm", 9_985_000, r, 1, "ON" if on else "OFF", "BASE", comparable=not on,
            note="arm " + r["arm"] + "; NOT in dossier-A 630 pool")
    # --- instrumented k=1 splice-OFF BASE blocks
    for p in sorted(glob.glob(str(C / "x_ticket/results/*.json"))):
        r = json.loads(pathlib.Path(p).read_text())
        add(out, "x_ticket", 9_998_000, r, 1, "OFF", "BASE")
    for r in rows("x_decay/RESULTS.json"):
        add(out, "x_decay", 9_999_000, r, 1, "OFF", "BASE", comparable=r["f"] == 1.0,
            note="in-place mutation x%s" % r["f"])
    for r in rows("x_sterile/RESULTS.json"):
        add(out, "x_sterile", 9_999_500, r, 1, "OFF", "BASE", comparable=r["g"] == 1.0,
            note="copy-error x%s" % r["g"])
    for r in rows("x_atomic/RESULTS.json"):
        at = r["arm"] == "ATOMIC"
        add(out, "x_atomic", 9_999_800, r, 1, "OFF", r["arm"], comparable=not at,
            note="" if at else "BASE arm; NOT in dossier-A 630 pool")
    for r in rows("c_atomic/RESULTS.json"):
        if r["specimen"] != SPEC:
            continue
        at = r["arm"] == "ATOMIC"
        add(out, "c_atomic", 12_000_000, r, 1, "OFF", r["arm"], seed=r["seed"], comparable=not at,
            note="" if at else "BASE arm; NOT in dossier-A 630 pool")
    for r in rows("c_core/RESULTS.json"):
        add(out, "c_core", 14_000_000, {"depth": r["depth"]}, 1, "OFF", "ATOMIC", seed=r["seed"],
            comparable=False, note="ATOMIC; founder bytes tagged")
    # --- C9 H2 frozen arm B (splice ON), depths quoted in x_h2_7ae3/run_h.py docstring
    for i, d in enumerate((6, 0, 1, 1, 12, 3, 15, 2, 0, 1, 2, 7, 1, 0, 0, 0)):
        out.append({"exp": "c9_h2_frozen", "block": "c9_h2_frozen", "seed_base": None, "seed": "C9#%d" % i,
                    "k": 1, "splice": "ON", "writeback": "BASE", "tier": TIER, "epochs": EPOCHS, "depth": d,
                    "p11_events": None, "comparable": False, "note": "C9 bundle harness; from docstring"})
    # sanity: no (seed, condition) duplicated across experiments
    seen = {}
    for r in out:
        key = (r["seed"], r["k"], r["splice"], r["writeback"], r["note"])
        assert key not in seen, (key, seen.get(key), r["exp"])
        seen[key] = r["exp"]
    return out


if __name__ == "__main__":
    t = build()
    (HERE / "run_table.json").write_text(json.dumps(t, indent=0))
    from collections import Counter
    cnt = Counter()
    for r in t:
        key = (r["exp"], r["k"], r["splice"], r["writeback"], r["comparable"])
        cnt[key] += 1
    summ = []
    for key in sorted(cnt, key=str):
        rs = [r for r in t if (r["exp"], r["k"], r["splice"], r["writeback"], r["comparable"]) == key]
        d = [r["depth"] for r in rs]
        summ.append({"exp": key[0], "k": key[1], "splice": key[2], "writeback": key[3], "comparable": key[4],
                     "n": len(d), "seed_range": [min(r["seed"] for r in rs if isinstance(r["seed"], int)) if isinstance(rs[0]["seed"], int) else None,
                                                 max(r["seed"] for r in rs if isinstance(r["seed"], int)) if isinstance(rs[0]["seed"], int) else None],
                     "d_ge5": sum(x >= 5 for x in d), "d_ge20": sum(x >= 20 for x in d), "max": max(d)})
        print("%-20s k=%d splice=%-3s %-6s comp=%-5s n=%3d d>=5=%3d d>=20=%3d max=%d" % (
            key[0], key[1], key[2], key[3], key[4], len(d), summ[-1]["d_ge5"], summ[-1]["d_ge20"], max(d)))
    (HERE / "table_summary.json").write_text(json.dumps(summ, indent=1))
    pool = [r for r in t if r["comparable"] and r["k"] == 1]
    print("comparable k=1 pool n=%d d>=5=%d d>=20=%d" % (len(pool), sum(r["depth"] >= 5 for r in pool),
                                                          sum(r["depth"] >= 20 for r in pool)))
