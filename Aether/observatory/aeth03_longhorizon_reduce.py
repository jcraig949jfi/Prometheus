"""Apply PHYSICS_DESIGN_03 s1's preregistered horizon criteria (Block C).

Reads long-horizon unit results (aeth03_unit.py --instrument longhorizon;
files carry "origins" and "inputs") from one or more directories, pools
origins per (law, arm), and reports, per horizon, the share of origins
still differing, the share whose max radius so far is >= 5, breaches, and
the share that set a new maximum generation after tick 2,000. Then applies
the "locality conclusions DEPEND on the horizon" rule verbatim, for OFF
arms only:
  (i)  share(max radius >= 5) at +10,000 >= 2 x share at +500 AND >= 0.10;
  (ii) any region breached;
  (iii) >= 10% of origins set a new maximum generation after tick 2,000.
"""

import argparse
import glob
import json
import os

HORIZONS = ("100", "400", "500", "1000", "2000", "5000", "10000")


def load(dirs):
    rows = {}
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "*.json"))):
            with open(p, encoding="utf-8") as fh:
                r = json.load(fh)
            if "origins" not in r or "inputs" not in r:
                continue
            inp = r["inputs"]
            key = (inp["law"], inp["arm"])
            rows.setdefault(key, []).append(r)
    return rows


def summarise(results):
    origins = [o for r in results for o in r["origins"]]
    n = len(origins)
    ticks = max(r["inputs"]["ticks"] for r in results)
    out = {"origins": n, "ticks": ticks,
           "seeds": sorted(r["inputs"]["seed_index"] for r in results),
           "breached": sum(o["breached_at"] is not None for o in origins),
           "locality_violations": sum(r["locality_violations"] for r in results),
           "new_max_gen_after_2000": sum(o["last_new_gen_tick"] > 2000 for o in origins)
           / float(n) if n else None,
           "by_horizon": {}}
    for h in HORIZONS:
        rows = [o["horizons"].get(h) for o in origins if h in o["horizons"]]
        rows = [x for x in rows if x and not x.get("breached")]
        if not rows:
            continue
        m = len(rows)
        out["by_horizon"][h] = {
            "unbreached": m,
            "alive": sum(x["alive"] for x in rows) / float(m),
            "max_radius_ge5": sum(x["max_radius_so_far"] >= 5 for x in rows) / float(m),
            "max_radius_max": max(x["max_radius_so_far"] for x in rows),
            "max_gen_max": max(x["max_gen_so_far"] for x in rows),
            "median_differing_sites_alive": sorted(
                [x["differing_sites"] for x in rows if x["alive"]] or [0])[
                len([x for x in rows if x["alive"]]) // 2] if any(x["alive"] for x in rows) else 0,
        }
    return out


def judge(s):
    bh = s["by_horizon"]
    early = bh.get("500", {}).get("max_radius_ge5")
    late = bh.get("10000", {}).get("max_radius_ge5")
    c1 = (early is not None and late is not None
          and late >= 2 * early and late >= 0.10)
    c2 = s["breached"] > 0
    c3 = (s["new_max_gen_after_2000"] or 0) >= 0.10
    return {"i_growth": c1, "ii_breach": c2, "iii_late_generations": c3,
            "horizon_dependent": c1 or c2 or c3}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args(argv)
    rows = load(a.dirs)
    out = {}
    for (law, arm), rs in sorted(rows.items()):
        s = summarise(rs)
        if arm == "off":
            s["verdict"] = judge(s)
        out["%s_%s" % (law, arm)] = s
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
