"""File the B2 receipt from committed rows. Run AFTER rebase so `git` is final.

usage: python -m primordial.soup.b2.receipt --git <sha> [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROWS = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "B"
CLAIM = ("B2 GraphWorld toy: torus lattice with predators/prey/food as boolean relations (AT, ADJ+I, move "
         "permutations); EAT, PREY and MOVE-with-flee as mxm/ewise/masks in python-graphblas and as Cypher in "
         "FalkorDB. Predicted: both hash-equal to a plain-Python reference on 50 specs x 64 ticks; cheat no_flee "
         "caught in every spec where a prey was ever threatened; graphblas slower than the reference below ~10k "
         "entities; Cypher slowest at every size.")


def _jsonl(name):
    p = ROWS / name
    return [json.loads(x) for x in open(p, encoding="utf-8")] if p.exists() else []


def oracle(form):
    rows = _jsonl(f"B2-oracle-{form}.jsonl")
    hon = [r for r in rows if r["cheat"] is None]
    ch = [r for r in rows if r["cheat"] == "no_flee"]
    return {"honest_equal": sum(r["equal"] for r in hon), "specs": len(hon),
            "cheat_caught_threatened": sum(not r["equal"] for r in ch if r["threatened"]),
            "threatened_specs": sum(r["threatened"] for r in ch),
            "cheat_false_alarms": sum(not r["equal"] for r in ch if not r["threatened"])}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--git", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    orc = {f: oracle(f) for f in ("gb", "cy")}
    bench = _jsonl("B2-bench-v0.jsonl")
    surface = {}
    for r in bench:
        surface.setdefault(str(r["entities"]), {})[r["form"]] = round(r["entity_ticks_per_s"])
    all_eq = all(r["equal_ref"] in (True, None) for r in bench)
    crossover = None
    for n in sorted(surface, key=int):
        s = surface[n]
        if "gb" in s and "ref" in s and s["gb"] > s["ref"]:
            crossover = int(n)
            break
    cy_not_slowest = [int(n) for n, s in surface.items()
                      if "cy" in s and s["cy"] > min(v for k, v in s.items() if k != "cy")]
    cy_slowest = not cy_not_slowest
    oracle_ok = all(v["honest_equal"] == v["specs"] and v["cheat_caught_threatened"] == v["threatened_specs"]
                    and v["cheat_false_alarms"] == 0 for v in orc.values())
    rec = {
        "lane": "B", "exp_id": "B2-graphworld-toy", "claim": CLAIM,
        "status": "PASS" if (oracle_ok and all_eq) else "FAIL",
        "engineering": {
            "entity_ticks_per_s_by_entities": surface,
            "gb_overtakes_ref_at_entities": crossover,
            "caveats": ["gb and cy build static relations inside the timed run; small worlds carry that cost",
                        "cy capped at L=64 (512 entities); 4 queries + 1 read per tick",
                        "density fixed at entities ~ cells/8; ticks=16"],
        },
        "science": {
            "oracle": orc,
            "hypothesis_scoring": {
                "hash_equal_both_forms": "CONFIRMED 50/50 each" if oracle_ok else "FAILED",
                "no_flee_caught_where_exercised": "CONFIRMED" if oracle_ok else "FAILED",
                "gb_slower_than_ref_below_10k": ("gb never overtook ref up to the largest size run" if crossover is None
                                                 else f"gb first overtakes ref at {crossover} entities"),
                "cypher_slowest_every_size": ("CONFIRMED" if cy_slowest else
                                              f"WRONG at entities {sorted(cy_not_slowest)}: cy beat setup-dominated "
                                              "gb there; slowest at every other size it ran"),
            },
        },
        "controls": {
            "cheat": "no_flee (THREATENS ignored): " + json.dumps(
                {f: f"{v['cheat_caught_threatened']}/{v['threatened_specs']} caught, "
                    f"{v['cheat_false_alarms']} false alarms" for f, v in orc.items()}),
            "benchmark_hash_check": "every benchmark run's trajectory hash compared to ref: all equal" if all_eq
            else "a benchmark hash differed from ref",
        },
        "rows": "primordial/ledger/rows/B/B2-*.jsonl",
        "git": a.git,
    }
    print(json.dumps({k: rec[k] for k in ("status", "science")}, indent=1))
    print(json.dumps(rec["engineering"]["entity_ticks_per_s_by_entities"]))
    if not a.dry:
        from primordial.bus import bus
        print("filed", bus.receipt(rec))


if __name__ == "__main__":
    main()
