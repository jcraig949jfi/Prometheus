"""s1_analyze.py -- FROZEN analysis for S1 (committed with the preregistration).

Reads runs/ (search populations) and transfer/ (cross-family transfer evaluations) and
computes the preregistered endpoints and the kill/continue threshold. This script is
frozen before any scored number exists; edits after the first result are dated amendments.

Primary:  ENRICHMENT = overall_rate(map_elites archive) / overall_rate(random),
          where a member is "useful on W_t" iff fitness >= tau_t, and tau_t is the
          75th-percentile fitness of the DISTINCT random population pooled on W_t.
Controls: 6a dead-world (must be ~random, no false value); 6b size-matched random.
Threshold: ENRICHMENT >= 2.0 across >=2 families, surviving 6b -> PASS (continue);
           else FAIL (stop scheduled evolutionary mining, keep the infrastructure).
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
RUNS, TRANSFER = ROOT / "runs", ROOT / "transfer"


def _load(d):
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(d.glob("*.json"))]


def _pct(vals, q):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    k = (len(vals) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(vals) - 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def main():
    transfers = _load(TRANSFER)
    runs = _load(RUNS)
    if not transfers:
        print("no transfer files yet -- run phase transfer first.")
        return 0

    # tau_t: 75th percentile of DISTINCT random-member fitness pooled per target world
    rand_fit_on = defaultdict(list)
    for t in transfers:
        if t["driver"] == "random":
            for r in t["rows"]:
                if r.get("fitness") is not None:
                    rand_fit_on[t["target_world"]].append(r["fitness"])
    tau = {w: _pct(v, 0.75) for w, v in rand_fit_on.items()}
    print("tau_t (75th pct of random fitness) per target:",
          {w: round(x, 4) if x is not None else None for w, x in tau.items()})

    # overall rate per driver, and per source-family
    def useful(row, w):
        f, t = row.get("fitness"), tau.get(w)
        return (f is not None and t is not None and f >= t)

    agg = defaultdict(lambda: [0, 0])           # driver -> [useful, total]
    by_fam = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # fam -> driver -> [u,t]
    dead = defaultdict(lambda: [0, 0])          # driver -> [u,t] for DEAD source
    for t in transfers:
        d = t["driver"]
        for r in t["rows"]:
            if r.get("fitness") is None:
                continue
            u = 1 if useful(r, t["target_world"]) else 0
            bucket = dead if t["source_family"] == "DEAD" else agg
            bucket[d][0] += u
            bucket[d][1] += 1
            if t["source_family"] != "DEAD":
                by_fam[t["source_family"]][d][0] += u
                by_fam[t["source_family"]][d][1] += 1

    def rate(pair):
        return pair[0] / pair[1] if pair[1] else None

    r_me, r_rnd = rate(agg["map_elites"]), rate(agg["random"])
    enrich = (r_me / r_rnd) if (r_me and r_rnd) else None
    print(f"\nPRIMARY (live worlds): rate(map_elites)={r_me}  rate(random)={r_rnd}  "
          f"ENRICHMENT={round(enrich,3) if enrich else None}")
    fams_passing = 0
    for fam, dd in sorted(by_fam.items()):
        a, b = rate(dd["map_elites"]), rate(dd["random"])
        e = (a / b) if (a and b) else None
        if e and e >= 2.0:
            fams_passing += 1
        print(f"  {fam}: rate_me={a} rate_rnd={b} enrichment={round(e,3) if e else None}")

    # duplicate rate + coverage (secondary)
    for rn in runs:
        if rn["driver"] == "map_elites":
            cov = rn["report"].get("archive_stats", {}).get("coverage")
            n_arch = len(rn["archive_members"])
            addrs = [rn["meta"].get(a, {}).get("genotype_addr") for a in rn["archive_members"]]
            dup = 1 - (len({x for x in addrs if x}) / n_arch) if n_arch else None
            if rn["family"] == "DEAD":
                print(f"\nDEAD-WORLD map_elites: coverage={cov} archive_n={n_arch} "
                      f"dup_rate={round(dup,3) if dup is not None else None} "
                      f"best_fitness={rn['report'].get('best_fitness')}")

    # CONTROL 6a: dead-world transfer rate must be ~random (no false value)
    dr_me, dr_rnd = rate(dead["map_elites"]), rate(dead["random"])
    print(f"\nCONTROL 6a DEAD source transfer: rate_me={dr_me} rate_rnd={dr_rnd} "
          f"(must be ~equal; map_elites must NOT show enrichment on a dead world)")

    # VERDICT
    print("\n" + "=" * 60)
    passed = (enrich is not None and enrich >= 2.0 and fams_passing >= 2)
    dead_clean = (dr_me is None or dr_rnd is None
                  or (dr_me <= 1.5 * dr_rnd + 1e-9))
    print(f"threshold: ENRICHMENT>=2.0 across >=2 families  -> "
          f"enrichment={round(enrich,3) if enrich else None}, families_passing={fams_passing}")
    print(f"dead-world control clean (no false enrichment): {dead_clean}")
    print(f"VERDICT (pre-control-6b): {'PASS' if passed and dead_clean else 'FAIL'}")
    print("NOTE: control 6b (size+diversity-matched random) applies before any PASS is "
          "final; a PASS that vanishes under matching is withdrawn as bookkeeping.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
