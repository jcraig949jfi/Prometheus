# HT-faa9277e02 / W1 -- implementation notes (round 2, control-first)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and
2026-09-29_probe_round1/PREREG.md. Written BEFORE any code was run.

## Spec field -> code

| spec field | code (sim.py unless noted) |
|---|---|
| mechanism: GM kinetics, 48x48, 4-neighbour edges | `step()`: a_t = sum_e D0*g_e*(a_j-a_i) + a^2/h - a ; h_t = Dh*lap(h) + mu*(a^2 - h). Open (non-periodic) grid: 48*47 horizontal + 47*48 vertical = 4512 edges (matches spec "4512 edges"), so boundaries are no-flux. |
| activator diffusion on edge e = D0*g_e | arrays `gh` (48x47), `gv` (47x48); flux on edge = D0*g*(a_j-a_i). Inhibitor diffusion is uniform Dh (spec makes only activator plastic). |
| dg = eta*(a_i a_j/mean(a)^2 - 1) - lambda*(g-1), clip [0.2,5] | `plastic_update()`, applied each step as g += dt*dg then clip; mean(a) = spatial mean of a at that step. |
| intervention Phase A | `phase_a(seed)`: 3000 steps, plasticity on, init uniform steady state + noise from RNG(seed). Returns final a map and learned (gh, gv). |
| intervention Phase B | `phase_b(graph, seed+1000)`: fields reset to uniform steady state + fresh noise from RNG(seed+1000), plasticity off, 3000 steps. |
| control (CONTROL arm, phase 2) | Phase B on g = 1 everywhere. |
| positive_control | Phase B on hand-carved graph from Phase A final map (see readings). |
| null_twin | Phase B on learned g values permuted across all 4512 edges with RNG(seed+2000) (identical histogram and mean). |
| CHEAT (prereg round 1) | Phase B final map replaced by the Phase A final map (success injected into the observable). |
| observable | Pearson r between z-scored Phase A final activator map and Phase B final activator map (`pearson_z`). |
| success_criterion | evaluator: mean r (10 seeds) >= 0.5 AND mean r - null-twin mean >= 0.3 AND one-sided Wilcoxon signed-rank (paired seeds, arm > null twin, exact) p < 0.01 AND positive-control mean r >= 0.7. |
| failure_criterion | mean r - null-twin mean < 0.1, OR positive-control mean r < 0.5. |
| seeds | 10 seeds s = 0..9 (spec says 10; also needed: exact one-sided Wilcoxon with n=5 has minimum p = 1/32 > 0.01, so n=5 could never pass). |

## Parameters (chosen from the spec + standard GM linear analysis, not from any run)

- Kinetics (dimensionless GM): a_t = a^2/h - a, h_t = mu*(a^2 - h); homogeneous
  steady state a*=h*=1. Jacobian (1,-1; 2mu,-mu): stable without diffusion iff mu>1.
- mu = 2.0, D0 (activator) = 0.5, Dh (inhibitor) = 10.0, grid spacing 1.
  Turing condition Dh*1 - D0*mu = 9 > 2*sqrt(D0*Dh*mu) = 6.3 -> unstable;
  critical k^2 = 9/(2*0.5*10) = 0.9, wavelength ~6.6 cells (~7 per side).
- dt = 0.02 (explicit Euler; max activator node sum 4*0.5*5*dt = 0.2, inhibitor 4*10*dt = 0.8 < 1).
- 3000 steps per phase = 60 time units.
- Plasticity eta = 0.1, lambda = 0.1 (per time unit): equilibrium g = a_i a_j/mean(a)^2,
  i.e. ~1 at mean co-activity, towards 5 inside hot spots and 0.2 in cold zones;
  relaxation time 10 time units << 60.
- Noise: a = 1 + 0.01*N(0,1), h = 1 + 0.01*N(0,1) (fresh RNG per phase). Full reset: no Phase A state survives into Phase B.
- Numerical guards: h floored at 1e-6, a floored at 0 (recorded as anomaly counts if hit).

## Ambiguities and chosen readings

1. "activator-high domains" (positive control): cells with Phase A final a above its spatial mean (z > 0). Edge with both endpoints high -> g=5; edge joining high and low (domain boundary) -> g=0.2; edge with both endpoints low -> g=1 (spec silent; baseline value).
2. "positive control r >= 0.7": read as the mean over the 10 seeds.
3. Null twin "meets success": the relative clauses (exceeds null-twin mean by 0.3, Wilcoxon vs null twin) are undefined for the null twin against itself; read as null-twin mean r >= 0.5 (the absolute clause). Recorded as a reading; also reported in phase 2: null twin vs CONTROL arm with the full relative clauses, as a statistic only.
4. For the positive control and cheat arms in the pilot, "meets success" = the full criterion applied with that arm in the treatment slot (mean >= 0.5, minus null mean >= 0.3, Wilcoxon p < 0.01 vs null twin, positive-control mean >= 0.7).
5. "cheat detected" = cheat arm meets the success criterion under reading 4.
6. Degenerate map (std 0) -> r = 0 and an anomaly is recorded.
7. Phase A (plastic) is shared infrastructure: the null twin and positive control both need it. The pilot runs Phase A, but NEVER runs Phase B on the unpermuted learned graph (that is the treatment).

## Budget

Estimate: 10 Phase A + 20 Phase B pilot runs + 50 phase-2 Phase B runs of 3000 steps on 48x48, numpy single core: < 2 core-minutes. Timings recorded in rows.

## Log

(appended below as the run proceeds)

### Pilot attempt 1 (2026-09-29) -- FAIL
PILOT.json: positive control mean r = -0.047 (per-seed -0.34..0.38), null twin
mean r = 0.002, cheat r = 1.0 on every seed but "not detected" because under
reading 4 the success criterion includes the positive-control clause (>= 0.7),
which failed. No NaNs, no floor hits. Phase A forms a labyrinth pattern
(amap std ~0.49); learned g mean 1.21, 16% at 0.2, 0% at 5.

Diagnosis (structural, from the Phase A map and the carved graph only; no
treatment arm has been run): reading 1 (high = z > 0) marks 57% of cells
high and they form ONE percolating domain (seed 0: 527-cell component), so
"domains" in the spec's plural sense do not exist under that reading. g=5 on
over half the grid sets activator D to 2.5 there, below the Turing threshold
(needs Dh/D_a > ~11.7; here 4), so that half is forced homogeneous and the
rest patterns freely at its own phase -> r ~ 0. The construction did not have
the effect by design.

### Repair (the ONE allowed; controls only, thresholds unchanged)
Reading 1 changed to: activator-high domains = cells with Phase A z > 1
(pattern cores). Seed 0 check: 14.5% of cells, 45 separate domains, largest
22 cells. Edge rules otherwise unchanged (high-high 5, high-low 0.2,
low-low 1). Evaluator, criteria, readings 2-7, kinetics, seeds unchanged.
Chosen by reasoning before rerunning; no other variant was run. Attempt-1
files kept as pilot_rows.jsonl / PILOT.json; attempt 2 writes
pilot_rows_attempt2.jsonl / PILOT_attempt2.json.

### Pilot attempt 2 -- FAIL -> OUTCOME SPEC_UNATTAINABLE
Positive control mean r = 0.282 (0.18..0.35; Wilcoxon vs null p = 0.00098 but
mean < 0.5 and < 0.7); null twin 0.002; cheat 1.0 (not detected only via the
positive-control clause). Second pilot failure -> OUTCOME.json written with
SPEC_UNATTAINABLE; phase 2 not built. No treatment statistic exists.
