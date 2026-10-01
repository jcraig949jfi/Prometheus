"""s3 step 2: panel + matched comparators, single-knockout function profiles, dispensable sets.

    python -B s3_singles.py -> s3_singles.json
Panel: the 48 DENSE state-free genomes of core_map.json (the one PLAIN state-free genome is excluded: the question
is about the dense VM). Comparators: 48 of the 80 DENSE state-dependent competent genomes, greedy match per panel
genome in core_map order: (1) same (cell, origin_run); (2) same origin_run string, other cell; (3) same cell and same
campaign family (c_dense_copy / x_dd_dense_copy); (4) same cell. Ties broken by a seeded RNG (20260930).
Single knockouts use core_map.knockout's 3 values per position (s3_common.single_vals).
  state-dependent: function = COMPETENT. Existing (lost, tried) data are used; where tried == 2 (0 lost) the third
    value is assayed so that p_i = lost/3 comes from 3 draws. dispensable <=> lost <= 1 (= not NECESSARY).
  state-free: function = COMPETENT and STATE_FREE, assayed on all 3 values at every position that is not NECESSARY
    (NECESSARY positions are not dispensable by the existing data). The COMPETENT component is checked against the
    existing ko_detail (determinism). dispensable <=> function kept in >= 2 of 3 draws. p_i = lost/3.
"""
import json
import random
import time

import s3_common as S
import s3_pipeline as P

t0 = time.process_time()
rows = json.load(open("core_map.json"))["rows"]
sf = [r for r in rows if r.get("state_free") and r["vm"] == "DENSE"]
sdpool = [r for r in rows if r.get("competent") and not r.get("state_free") and r["vm"] == "DENSE"]
rng = random.Random(20260930)
fam = lambda r: r["origin_run"].split("/")[0]
used, match = set(), []
for r in sf:
    for lev, key in ((1, lambda x: x["cell"] == r["cell"] and x["origin_run"] == r["origin_run"]),
                     (2, lambda x: x["origin_run"] == r["origin_run"]),
                     (3, lambda x: x["cell"] == r["cell"] and fam(x) == fam(r)),
                     (4, lambda x: x["cell"] == r["cell"])):
        c = [i for i, x in enumerate(sdpool) if i not in used and key(x)]
        if c:
            i = rng.choice(c); used.add(i); match.append((lev, i)); break
out = {"panel": [], "comparators": []}
det_mismatch = det_checked = 0
for k, r in enumerate(sf):
    g = bytes.fromhex(r["hex"]); nec = set(r["necessary"])
    prof = {}
    for p in range(64):
        if p in nec:
            continue
        comps = P.comp_draws(r["cell"], g, True, p)
        lost, tried = r["ko_detail"][p]
        det_checked += 1; det_mismatch += (tried - sum(comps[:tried])) != lost
        kept = [c and S.state_free(r["cell"], bytes(m), True) for c, m in
                zip(comps, [bytes(g[:p]) + bytes([v]) + bytes(g[p + 1:]) for v in S.single_vals(g, p)])]
        prof[p] = kept
    disp = sorted(p for p, v in prof.items() if sum(v) >= 2)
    out["panel"].append({"idx": rows.index(r), "hex": r["hex"], "cell": r["cell"], "origin_run": r["origin_run"],
                         "src": r["src"], "n_necessary": len(nec), "p": {str(p): 1 - sum(v) / 3 for p, v in prof.items()},
                         "disp": disp, "sf_lost_positions": sorted(p for p, v in prof.items() if sum(v) < 2)})
    print("SF", k, r["origin_run"][-8:], len(nec), len(disp), round(time.process_time() - t0, 1), flush=True)
for k, (lev, i) in enumerate(match):
    r = sdpool[i]; g = bytes.fromhex(r["hex"]); nec = set(r["necessary"])
    pp = {}
    for p in range(64):
        if p in nec:
            continue
        lost, tried = r["ko_detail"][p]
        if tried == 2:
            m = bytearray(g); m[p] = S.single_vals(g, p)[2]
            lost += not S.competent(r["cell"], bytes(m), True)
        pp[p] = lost / 3
    out["comparators"].append({"idx": rows.index(r), "hex": r["hex"], "cell": r["cell"], "origin_run": r["origin_run"],
                               "match_level": lev, "matched_to": k, "n_necessary": len(nec),
                               "p": {str(p): v for p, v in pp.items()}, "disp": sorted(pp)})
    print("SD", k, lev, r["origin_run"][-8:], len(nec), round(time.process_time() - t0, 1), flush=True)
out["determinism_check"] = {"positions_checked": det_checked, "competence_count_mismatch": det_mismatch}
out["cpu_s"] = round(time.process_time() - t0, 1)
json.dump(out, open("s3_singles.json", "w"))
print(out["determinism_check"], out["cpu_s"])
