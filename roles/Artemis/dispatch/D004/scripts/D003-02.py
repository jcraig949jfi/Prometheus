#!/usr/bin/env python3
"""D003-02 (FR-091 / H-D1-50 / XE-07 / AL-5): tabulations over COMMITTED BEE data. Not run by the author.

Inputs (extract read-only, e.g. `git show <sha>:<path> > <file>`), all @ b960d1a42600:
  G  = roles/Bellerophon/forensics_2026-09-23/receipts/GROUNDING_RESULTS_RAW.jsonl.gz   (grounding round, pinned code a1b066309)
  C  = roles/Bellerophon/coupling_2026-09-24/receipts/COUPLING_RESULTS.json              (coupling campaign summary)
Row schema of G is written by prometheus/z80atlas/grounding.py:_run (lines 138-165): id, lane, cell, arm, pair, k, seed,
summary{...}, first_self_replication, spontaneous, task_reached, dominant_sr_descriptor.

Usage: python3 analysis.py GROUNDING_RESULTS_RAW.jsonl.gz COUPLING_RESULTS.json

What decides the question (stated before running):
 Q1 "Is a scalar objective causally present in BEE's endogenous random-soup worlds?"  Lane G3 cells RANDOM/IMPLICIT/<task> and
    RANDOM/EXPLICIT/<task> share seeds k (grounding.py:51-55, 81-88). EXPLICIT under ENDOGENOUS_COPY adds energy inflow 2*s
    (world.py:700-701); IMPLICIT adds 0.5*s (world.py:716). If the ENDOGENOUS_COPY summaries are identical for (nearly) all
    100+100 matched k, the scalar objective is inert there too, and BEE's G1/P8/B-rand origin results ARE de facto
    "implicit replication with no effective scalar objective" data. If they differ, report spontaneous-SR and first-SR
    tick per pressure (paired, McNemar-style discordant counts) -- that is the XE-07 implicit-vs-explicit contrast on
    one substrate, at the origin stage.
 Q2 "Does the reproduction primitive matter (AL-5 proxy)?"  P8 RANDOM/COPY/base vs ldir_off (matched k): discordant
    pairs for spontaneous. Reported 8/300 vs 0/300 (GROUNDING_REPORT.md:78); this re-derives it from rows.
 Q3 "Does task coupling change origin from random soup?"  coupling B-rand spontaneous_SR per arm, summed.
"""
import gzip
import json
import sys
from collections import defaultdict


def load_rows(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def fsr_tick(r):
    f = r.get("first_self_replication") or {}
    return f.get("tick") if isinstance(f, dict) else None


def main(gpath, cpath):
    rows = list(load_rows(gpath))
    print("grounding rows:", len(rows))
    by = defaultdict(dict)                      # (lane, cell, arm) -> k -> row
    for r in rows:
        by[(r.get("lane"), r.get("cell"), r.get("arm"))][r.get("k")] = r

    # Q1
    print("\nQ1 endogenous IMPLICIT vs EXPLICIT, RANDOM init, matched k (lane G3, arm ENDOGENOUS_COPY)")
    for task in ("INC", "COND_ONE"):
        imp = by.get(("G3", "RANDOM/IMPLICIT/%s" % task, "ENDOGENOUS_COPY"), {})
        exp = by.get(("G3", "RANDOM/EXPLICIT/%s" % task, "ENDOGENOUS_COPY"), {})
        ks = sorted(set(imp) & set(exp))
        same = sum(1 for k in ks if imp[k].get("summary") == exp[k].get("summary"))
        sp_i = sum(1 for k in ks if imp[k].get("spontaneous")); sp_e = sum(1 for k in ks if exp[k].get("spontaneous"))
        disc_i = sum(1 for k in ks if imp[k].get("spontaneous") and not exp[k].get("spontaneous"))
        disc_e = sum(1 for k in ks if exp[k].get("spontaneous") and not imp[k].get("spontaneous"))
        tr_i = sum(1 for k in ks if imp[k].get("task_reached")); tr_e = sum(1 for k in ks if exp[k].get("task_reached"))
        t_i = [fsr_tick(imp[k]) for k in ks if imp[k].get("spontaneous")]
        t_e = [fsr_tick(exp[k]) for k in ks if exp[k].get("spontaneous")]
        print(f"  {task}: pairs {len(ks)}; identical summaries {same}; spontaneous IMP {sp_i} EXP {sp_e} "
              f"(discordant IMP-only {disc_i}, EXP-only {disc_e}); task_reached IMP {tr_i} EXP {tr_e}; "
              f"first-SR ticks IMP {sorted(t for t in t_i if t is not None)} EXP {sorted(t for t in t_e if t is not None)}")
        ext = by.get(("G3", "RANDOM/EXPLICIT/%s" % task, "EXTERNAL"), {})
        print(f"    EXTERNAL (population-manager, explicit fitness-proportional) task_reached: "
              f"{sum(1 for r in ext.values() if r.get('task_reached'))}/{len(ext)}")

    # Q2
    print("\nQ2 P8 RANDOM/COPY base vs ldir_off (matched k)")
    base = by.get(("P8", "RANDOM/COPY/base", "base"), {}); off = by.get(("P8", "RANDOM/COPY/ldir_off", "ldir_off"), {})
    ks = sorted(set(base) & set(off))
    print(f"  pairs {len(ks)}; spontaneous base {sum(1 for k in ks if base[k].get('spontaneous'))} "
          f"ldir_off {sum(1 for k in ks if off[k].get('spontaneous'))}; "
          f"endogenous births mean base {mean([base[k]['summary'].get('endogenous_births') for k in ks])} "
          f"off {mean([off[k]['summary'].get('endogenous_births') for k in ks])}")

    # Q3
    print("\nQ3 coupling campaign B-rand spontaneous_SR by arm (summed over cells)")
    C = json.load(open(cpath, encoding="utf-8"))
    tot = defaultdict(lambda: [0, 0])

    def walk(o):
        if isinstance(o, dict):
            for key, v in o.items():
                if isinstance(key, str) and key.startswith("B-rand|") and isinstance(v, dict) and "spontaneous_SR" in v:
                    for arm, kn in v["spontaneous_SR"].items():
                        tot[arm][0] += kn["k"]; tot[arm][1] += kn["n"]
                else:
                    walk(v)
    walk(C)
    for arm in sorted(tot):
        print(f"  {arm}: {tot[arm][0]}/{tot[arm][1]}")


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(sum(xs) / len(xs), 2) if xs else None


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
