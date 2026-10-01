# W2-22 PREREG: is there a kin/density second regime under BASE (7ae3, X-TICKET cell)?

Written 2026-10-01T01:42:57Z (`date -u`), before any simulation in this folder was run.

## Process
- W2-14's `ffield.py` (imported, unedited): 7ae3 arm-B cell, atlas_axis NONE, tier M, rule BASE, horizon T = 300.
- Arms (all PARTNER = BANK, CTX = CARRY, MUT = ON, W2-14 `banks.pkl`):
  - FIELD BANK (kin pairing + density present).
  - FREE BANK (private bank partner per member, no kin, no density).
- `w22.py` holds `run2()`, a copy of `ffield.run` with (a) extra readouts and (b) optional counterfactual
  mechanism switches. Before use, `run2(mech=None, stop="orig")` must reproduce `ffield.run` exactly on
  >= 20 seeds per arm (all output fields equal). If not, nothing below is run.
- Stop rule in production (`stop="xk"`): W2-14's stops, except the runaway stop also requires B_xk >= 163.
  This only delays stopping; dynamics before the stop are unchanged.
- **Seeds: fresh, disjoint from W2-14's 0-39.** BASE seed = 9_998_000 + s.
  - FIELD BANK: s = 1000..1599 (600 seeds).
  - FREE BANK: s = 1000..2199 (1200 seeds; FREE costs ~0.2 CPU-s/seed vs ~1 for FIELD).

## Readouts
- B: W2-14's B (cumulative P-11-causal births in the founder's causal lineage).
- B_xk: the subset of B whose victim was NOT a founder-label (anc 0) member before the interaction
  (recruitment births; excludes kin-on-kin re-conversion). In FREE, B_xk == B by construction.
- Conditioning event E27: B >= 27 at any time by epoch 300.
- **Primary.** P(B >= 163 | E27), FIELD BANK vs FREE BANK.
- **Secondary.** P(B >= 163); P(E27). Diagnostic (not rule-bearing): P(B_xk >= 163 | B_xk >= 27); maxA >= 128.

## Censoring (FREE only)
FREE stops at `free_cap256` when the lineage occupies 256 labels (slots exhausted) - the run is censored, not failed.
- Treatment C+ : a cap256 run with E27 counts as reaching B >= 163 (conservative AGAINST "supported").
- Treatment C- : counts as not reaching (conservative AGAINST "no second regime").
- SUPPORTED must hold under C+. NO SECOND REGIME must hold under C-. Otherwise UNRESOLVED.
  (Burden symmetry: each verdict must survive the censoring treatment that is least favourable to it.)

## Rule (primary readout, conditional rates p_FIELD, p_FREE)
- **SECOND REGIME SUPPORTED** if, under C+: one-sided Fisher exact (FIELD > FREE) p < 0.01 AND p_FIELD >= 3 * p_FREE
  (p_FREE = 0 with p_FIELD > 0 counts as >= 3x).
- **NO SECOND REGIME** if, under C-: the two-sided 95% CI for the ratio p_FIELD / p_FREE (Koopman score
  interval, by inversion on a grid) lies entirely below 3.
  ("CI on the difference excludes a 3x ratio" is operationalised as the ratio CI excluding 3.)
- Otherwise **UNRESOLVED**.

## Eligibility (computed before running, from W2-14's rates)
- P(E27) FIELD BANK 2/40 = 0.05 (95% CP 0.006-0.169); pooled FIELD BANK family 8/120 = 0.067.
- P(E27) FREE BANK 1/40 = 0.025 (95% CP 0.0006-0.132).
- Expected conditioned runs: FIELD 600 x 0.05 = 30; FREE 1200 x 0.025 = 30.
- P(>= 10 conditioned) at the point rates: ~1.0 per arm; at rate 0.02 (FIELD) or 0.01 (FREE): ~0.76.
- **Rule:** an arm with < 10 conditioned runs -> one pre-specified top-up (FIELD s = 1600..2199, FREE s = 2200..3399),
  budget permitting. If still < 10, the primary is INELIGIBLE and no verdict is claimed.

## Mechanism arms (counterfactual wrappers; only after the primary; FIELD BANK, same seeds s = 1000..1599)
Implemented inside `run2` around the world's own `_pair_interact`; world code is not changed. Labelled COUNTERFACTUAL.
- **M1 KIN_COSTLY.** A birth whose victim was a founder-label member and whose donor is a founder-label member
  is turned into a loss: the victim slot becomes a background organism (genome + registers drawn from the BANK
  at that epoch, anc = 1), and the birth is not recorded (no lineage edge, not in B).
- **M2 NO_REPAIR.** Same event class, restricted to ERODED victims: pre-interaction genome fidelity to the
  donor's pre-interaction genome < 0.9 (`world._fidelity`). The overwrite is undone: the victim keeps its
  pre-interaction genome, oid, pid and label (registers as left by the interaction), and the birth is not recorded.
- Mechanism readout: P(B >= 163 | E27) and the diagnostic B_xk version, vs FIELD BANK primary.
  Mechanism implicated if one-sided Fisher (FIELD BANK > arm) p < 0.01 on the B_xk conditional readout
  (B_xk is used because M1/M2 remove kin births from B by construction; B_xk is defined the same way in all arms).
  Only meaningful if the primary is SUPPORTED; otherwise reported descriptively.

## ATOMIC world check (only if budget remains)
`ffield.run("ATOMIC", 12_000_000 + s, "FIELD", "FULL")`, s = 0..29, T = 300 (bit-exact world rung).
Readouts depth_world >= 20, depth_f >= 20, B >= 163, maxA >= 40, per seed vs C-ATOMIC's 2000-epoch depth.
- If world@300 depth>=20 rate is within the model's 0.23-0.33 band (|diff| <= 0.10): F's ATOMIC gap is horizon censoring.
- If world@300 is >= 0.50: the gap is model error at equal horizon.
- Otherwise mixed.

## Budget
<= 90 CPU-min, <= 6 processes, `python -B`. Projection: validation ~2, FIELD 600 ~10-20, FREE 1200 ~5,
M1+M2 ~20-40, ATOMIC 30 ~15-25. Hard stop if cumulative CPU > 85 min; report what was completed.
