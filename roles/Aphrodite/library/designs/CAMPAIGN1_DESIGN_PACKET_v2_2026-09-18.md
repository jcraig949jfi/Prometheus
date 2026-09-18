# Campaign 1 design packet v2 (TIER 3; execution NOT authorised)

Currency: 2026-09-18. Supersedes CAMPAIGN1_DESIGN_PACKET_2026-09-18.md
(kept). Built to the operator's list for "the next operator packet"
(directive of 2026-09-18, item 10). One item is still missing, and it is
labelled rather than estimated: MEASURED compute economics await the
host-path benchmark, which this seat cannot run from M4 (s6).

## 1. Campaign 0C: preregistration and verdict (tier 2)

Prereg c21e4aab9 (before code); run 9ef14c424 (clean, 15,200
experiments). PASS on all four gates: calibration (false DISCOVERY <=
0.3% in null, screen-gaming and near-miss worlds), precision 99.7%, power
0.935-1.000 at L 64 for 10-20% prevalence with +24 to +42-point
discoveries, estimate-stage bias 0.000 with 95.1% coverage. Reported
limits: prevalence of 1-2% and discoveries of ~+11 points are not
detectable at L <= 64; family-specialised discoveries are a blind spot
(0.5%); rho_P is an effect-size-dependent lower bound on prevalence.

## 2. The two endpoints, side by side (operator item 2)

                 PRIMARY                          SECONDARY
  question       do TYPICAL evolved improvers     does evolution produce RARE
                 transfer?                        transferable discoveries under
                                                  a fixed discovery procedure?
  estimand       mean over lineages of the         rho_P: per-lineage rate of
                 compute-matched held-out gain     independently confirmed
                 (I_8 vs I_0, stripped, fresh      discoveries > 3 points
                 agent, sealed families)
  analysis       Campaign 0 assay, frozen          screen (c 0.10, top 25%) ->
                 (6195af410): per-lineage values,  decide (8 fresh families x 40,
                 Holm over 16, TOST at delta       t vs delta, Holm) -> estimate
                                                   (8 further fresh families)
  verdicts       SUPERIOR / EQUIVALENT / TRIVIAL / DISCOVERY iff >= 2 confirm;
                 INDETERMINATE per contrast;       q_screen, q_confirm, confirmed
                 BELOW RESOLUTION stated           effect + interval reported
  qualified by   Campaign 0 (+0B limits)           Campaign 0C
  independence   a secondary success never rescues or alters the primary
                 verdict; separate multiplicity families

## 3. Frozen delta (operator item 6)

delta = 3 points of held-out tasks solved at fixed compute, for both
endpoints. Not widened for a smaller campaign; a smaller campaign narrows
its claims instead.

## 4. Exact claims supported at 64 vs 32 lineages (tier 2 qualification)

  claim                                   L = 64          L = 32
  P  typical transfer (MDE)               yes (~4.7 pts)  yes (~7.1 pts)
  P  memory vs machinery                  yes             yes
  P  worker vs machinery transfer         yes             yes
  P  single-module attribution            yes             yes
  P  compute-cheat contrast               yes             no (meter only)
  P  specialisation                       yes (0.905;     no
                                          fragile)
  P  mixed causes                         yes             no
  P  EQUIVALENT ("no transfer > 3 pts")   yes (87%)       no -> BELOW
                                                          RESOLUTION
  P  jackpot-concentrated transfer        no (primary     no
                                          is not that
                                          instrument)
  S  DISCOVERY at 10% prevalence, +24 pts yes (0.935)     weak (0.647)
  S  DISCOVERY at 20% prevalence, +24 pts yes (0.993)     yes (0.960)
  S  DISCOVERY at 5% prevalence           ceiling ~0.84   no
  S  prevalence <= 2% or +11-pt effects   no              no
  S  family-specialised discoveries       no              no
Sixteen lineages: not a Campaign 1 configuration (operator item 7).

## 5. Proposed task / model / sandbox combination

- TASKS: short procedural families with code-checked answers (~2k tokens
  per evaluation target), four types as in the benchmark harness, to be
  replaced by Archaeon's sealed generators once its contract lands
  (request posted, comms #452).
- MODEL: undecided until measured. Candidates: small open models (1.5-8B,
  quantised) served on the M1/M2 RTX 5060s through an OpenAI-compatible
  server. Selection rule: highest measured evaluation throughput among
  models whose baseline accuracy on the task families lies between 15%
  and 70% (headroom for improvement, above the floor), plus a second
  model family of similar size for the substrate-transfer arm.
- SANDBOX / METER: per Vivarium's and Harmonia's contracts (requests
  posted, comms #454 and #453): lineage isolation, code-level mutation
  with two-phase commit, meter below the improver with per-module
  resource handles and an enforced escrow.

## 6. Measured compute economics: PENDING (the one missing item)

The benchmark (science/benchmark/bench.py, BENCHMARK_SPEC.md) runs the
Campaign 1 loop shape at capped scale and reports tokens/task, wall
time per evaluation, evaluations/generation, GPU utilisation, lineage
cost and projected campaign wall time. It must run on M1 or M2 against a
local model server; neither host is reachable from M4 (probed
2026-09-18). OPERATOR: who runs it, and which candidate models. Until
then the only economics on file are the ASSUMED 1-217 two-GPU-day range
in packet v1, which this packet does not rely on.

## 7. Kill and resize rules before any GPU execution (proposed)

K1 CONTRACT GATE: no Campaign 1 run until the Archaeon, Harmonia and
   Vivarium contracts exist and their cheat fixtures are caught.
K2 BUDGET RESIZE: if the measured projection for L = 64 exceeds the
   operator's wall-time budget (proposed: 30 days on M1 + M2), first
   shorten tasks or reduce evolution evaluations per generation; only
   then resize to L = 32 with the section 4 claims; never widen delta;
   never go below 32.
K3 HEADROOM: if the chosen model's baseline accuracy is outside 15-70%
   on the families, change model or task difficulty before any run.
K4 METER INTEGRITY: any unmetered call or escrow breach in a lineage
   flags that lineage and reports it; the lineage is kept and analysed
   with and without flagged lineages, never silently dropped.
K5 OPERATIONAL STOP: if more than 10% of lineages fail preflight
   repeatedly, or total spend exceeds 120% of the preregistered budget,
   stop and report; no outcome contrast is inspected before the
   preregistered analysis point.
K6 NO SUBSTITUTION: a secondary DISCOVERY never substitutes for, or
   alters, the primary verdict.

## 8. What the operator still has to decide

Who runs the benchmark on M1/M2 and with which models (s6); the
wall-time budget behind K2; then, after the measured packet, whether to
authorise Campaign 1.
