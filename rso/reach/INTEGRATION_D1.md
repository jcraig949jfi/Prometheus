# D1 integration note (C-013-T012) -- integrator's checks and qualifiers

Palamedes[harry1-679179c6], 2026-10-10. Reads with rso/reach/RESULT.md (Argus, the result of record); this note adds
the integrator's independent checks and two qualifiers. It changes no number in RESULT.md.

## 1. Independent checks (all passed)

- FROZEN_D1 v1.0.1 (freeze commit 8ddaa4f19; PREREGISTRATION v1.0.1 sha256 4e3c10a0): 48/48 pinned files match
  (LF-normalised) on the merged tree. RUN.json `frozen` is null only because FROZEN_D1.json carries no
  `freeze_commit` key (run_d1.py:132); the hash check itself ran on every call.
- Ledger: 270 rows = 15 complete rounds x 18 (arm, d) cells, n = 15 per cell; CPU 3.2425 core-hours from the row sum.
- `python -B -m rso.reach.analyze --run-dir rso/reach/runs/D1` re-run: all five contrasts identical (pooled counts,
  raw p, Holm p, verdicts). C3 checked by hand: d=1 3-vs-0 of 30 -> C(15,3)/C(30,3) = 0.1121; d=3 1-vs-0 -> 1/2;
  one-sided 0.056, two-sided 0.112 = RESULT.json.
- All 9 certified discoveries re-certified from their stored genomes (`final_prog`) by certify.certify:
  CERTIFIED, selection_ok, oracle_agrees on 9/9. `discovery` equals hit AND NOT seeded AND certified on 270/270
  rows; seeded_hit is false on every row.

## 2. Integrator mutation (recorded as hardening, not a result defect)

Tampering a ledger copy -- de-certifying one X2 d=1 hit and marking one chain_strict d=1 hit as seeded -- left every
contrast unchanged: analyze.py counts the runner-derived `row["discovery"]` (run_d1.py:73) and does not re-derive it
from `hit`, `seeded_hit` and `certificate`. Tampering `discovery` itself is detected (C3 pooled 4 -> 3). The real
ledger is consistent (above), so the result stands; a future analyzer should re-derive `discovery` and refuse a
ledger whose fields disagree. Candidate for the qualified-component registry (rso/scale roadmap s4).

## 3. Qualifier A -- power at the N the cap allowed

The cap stopped the run at N = 15 (CPU per round rose ~630 -> ~980 core-s on thermally limited harry1), below the
registered 20-24 band. Power at N = 15, computed with the registered function (stats.power, 4000 sims, seed 1,
baseline 1/24 per distance, Holm worst-case level 0.01; the same call reproduces the registered N = 24 row as
0.55 / 0.82 / 0.95 / 0.99 and one-distance 0.62):

| N | uniform +0.15 | +0.20 | +0.25 | +0.30 | one distance +0.46 |
|---|---|---|---|---|---|
| 24 (registered) | 0.56 | 0.82 | 0.94 | 0.99 | 0.62 |
| 15 (as run)     | 0.25 | 0.49 | 0.70 | 0.86 | 0.33 |

A design property, not an outcome-dependent analysis. Reading: NOTHING SEPARATES at N = 15 would miss a +0.20
ingredient effect about half the time. The result rules out only large effects (about +0.3 per lineage and up).

## 4. Qualifier B -- the registered baseline did not hold at d = 1

Power and the "1/24" premise assumed a chain baseline of about 1/24 per distance. Observed (descriptive only):
chain_strict 4/15 at d = 1, 0/15 at d = 3 and d = 8. At d = 1 the target is easy for the plain chain, so there is
little room for an ingredient to add; at d = 8 no arm hit at all, so there is nothing to separate. The informative
middle (d = 3) holds 2 discoveries in 90 lineages. No re-analysis follows from this; it is why a null here is weak.

## 5. What the program may and may not take from D1

May: at B = 200,000 on this world, none of neutral acceptance, best-cell retention, count-weighted selection,
worse-into-new-cell admission or behaviour-cell structure produced a LARGE certified-reach advantage; a certified
builder is reachable from d = 1 and d = 3 starts by the plain chain and by X2; no arm reached it from d = 8.
May not: "archives do not help", "search structure is not the lever", or any statement about other deserts. The
roadmap's Horizon-I failure branch ("no arm moves -> search structure alone is not the lever") is NOT triggered by
an under-powered null; see PROMETHEUS_SAGACITY_SCALING_ROADMAP.md s4 as amended.
