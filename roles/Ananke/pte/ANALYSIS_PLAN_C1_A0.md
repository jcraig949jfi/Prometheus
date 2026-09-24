# PTE-C1 A0 interaction analysis -- plan committed BEFORE A0 closes

Currency: 2026-09-24 (A0 at ~4300/5000 cells; only per-family marginal
counts have been looked at: plant-viable and sensitive fractions).
Prompted by the operator's note of the same day (reactivity vs functional
transport; find the interaction structure behind RELAY's ~2%). This is an
ANALYSIS plan over rows the frozen campaign already produces; PTE-C1 is
not touched.

## 1. The ladder, measured with fields A0 already records

  L1 input-reactive        gen0.frac_sensitive_any  (a random genome's cue
                           perturbs ANY site at ANY tick)
  L2 reaches the readout   gen0.frac_contrast_pos   (the actuator's S0 moves
                           with the target at readout, random genome,
                           mechanism-agnostic)
  L2' known transport      plant.acc >= 0.75        (ONE hand-written design)
  L3 exploitable           A1 SIGNAL                (evolved, held-out)
  L4 reusable/adaptive     C/D TRANSFER_SUPPORT, FLIP SIGNAL, state transplant

Caveat recorded before looking: the operator's contrast (11-22% reactive
vs 2% RELAY plant-viable) compares L1 with L2', which is not like for
like. L1 counts perturbation anywhere; L2' is one design's viability and
can fail for design-specific reasons (it floods via packets that do not
carry direction, and needs its 12-line program). The mechanism-agnostic
middle rung is L2; the claim "reactivity is common, transport is rare"
is scored on L1 -> L2 first, and L2' is reported beside it.

## 2. Candidate physical ratios (fixed now, before fitting)

  R_time   transit / budget = (lat_base + lat_hop*d + lat_jitter) * hops(d, radius) / delta
           (HOLD: gap in place of delta, hops 0)
  R_surv   expected copies arriving = fanout_eff * (1-loss)^(hops if loss_per_hop else 1) * (1+dup)
           fanout_eff = R if dest_mode=all else fanout
  R_mem    decay horizon / budget = (2^decay_shift if decay_shift>0 else inf) / delta
  R_band   offered load / capacity = fanout_eff * degree_in / cap  (cap 0 = inf), by collision policy
  R_clock  effective update rate = update_period^-1 (sync) or update_p (async), times cue_len
  plus topology x fanout as a categorical interaction.
  (Operator suggested latency x TTL: v1 has no TTL -- packets are not
  auto-forwarded; the nearest v1 quantity is R_time. TTL is ANANKE-11.)

## 3. Test (per family, per ladder rung L1, L2, L2')

Split A0 cells by cell_id hash into FIT and CONFIRM halves (fixed now:
first hex digit 0-7 FIT, 8-f CONFIRM). On FIT: (a) single-dial model, (b)
single dials + the five ratios, (c) depth-3 decision tree on dials +
ratios. Report CONFIRM log-loss and AUC for each. A ratio "explains" a
rung only if (b) beats (a) on CONFIRM by >= 0.02 AUC and the ratio's
threshold (tree split) sits at the same value +-1 level on both halves.
Every interaction claimed is then re-checked on the B phys-track
transects where one dial moves and the ratio moves with it.
Null to beat: the same models with the family label permuted within
topology (a ratio that "explains" every family equally is suspect).

## 4. What it feeds

A1's living-biased half is already fixed by the freeze; this analysis
only interprets it: SIGNAL rate in L2/L2'-viable cells vs uniform cells
separates "evolution fails where transport is possible" from "evolution
fails in hostile physics". C2 (operator direction, not yet a prereg):
take the confirmed habitable region and raise informational load
(concurrent cue streams, distractor traffic on shared channels) to find
where transport collapses under interference and whether any region
reorganises instead.
