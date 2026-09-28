# PKG-F prerequisite probe (DEV, 2026-09-28): restoring the discarded distinctions

Status: prerequisite probe allowed by directive Block F. Not preregistered; not a result about the law.
- Data: results/pkgf_probe.json. Code: pkgf_probe.py.
- 3 families (F2 noise, F3 obsolete, F5 spurious) x 2 generators x 4 dev worlds (seeds 9_800_000-003; shams
  9_850_000-003), L2, frozen LM01 SELECTIVE substrate at cap cells/4.
- 53 s, single process, BELOW_NORMAL.

## Instrument checks (all pass)

- LOSSLESS: (theta_S, D_S) reconstructs the admitted history to max error 8.9e-16.
- PC-help (restoration restores information): on exact-hit recall, S+D beats S in every stratum. Mean delta AC
  +0.45 .. +2.32.
- SHAM behaves as designed:
  - the learned readout IGNORES the size-matched sham (a = 0 in 23 of 24 worlds; delta 0.00);
  - the forced sham HURTS by -0.23 .. -1.32.
  - So "any extra records" burden is visible and a learned readout can opt out.

## Readings on the headline (never-seen / OOD) test. Mean delta AC vs S (4 worlds)

| stratum | S+D learned | S+D forced | SHAM learned | SHAM forced | learned a |
|---|---|---|---|---|---|
| F2 lowrank (noise) | +0.01 | +0.02 | 0.00 | -0.25 | 1, 1, .5, .5 |
| F2 spectral | +0.09 | +0.17 | 0.00 | -0.33 | .5 x4 |
| F5 cp (spurious) | 0.00 | +0.03 | 0.00 | -0.33 | 1, 1, .5, 1 |
| F5 spectral | +0.04 | +0.03 | 0.00 | -0.23 | .5, 1, .5, .5 |
| F3 cp (obsolete) | -0.90 | -1.13 | 0.00 | -0.91 | 1, 1, .5, .5 |
| F3 tt | -1.32 | -1.59 | 0.00 | -1.32 | 1, 1, .5, .5 |

## Reading (dev probe; provisional)

1. NOISE (F2) and SPURIOUS NUISANCE (F5): the restored discarded channel is nearly INERT for generalization, even when
   the readout is forced to use it. Discarding these distinctions was not causally necessary here. The prior from
   Kirichenko et al. (harm under forced use for spurious features) is NOT reproduced in this form.
2. OBSOLETE STRUCTURE (F3): restoring the discarded channel HURTS sharply, even under the readout that may ignore it,
   while the size-matched sham is ignored.
   - This is the SELECTIVITY_CAUSAL pattern of PKG-F s6. But the learned readout picks its weight on a holdout drawn
     from the WHOLE history, which is dominated by the old episodes.
   - The harm may therefore be a RETRIEVAL/SELECTION failure: the readout cannot identify which history is relevant
     (directive H). It may not be a property of the information itself.
   - Discriminator (added to PKG-F as a required arm): S+D/learned-recent, with the weight chosen on a holdout of the
     MOST RECENT records only (legitimate learner behaviour, no test leak). If the harm vanishes, obsolete history hurts
     only through readout selection. If it persists, the evidence for causal selectivity is stronger.
3. The F5 null and the F3 harm must both be tested against the NO-CHANGE control (PKG-F s7: stationary twins) before any
   causal reading.

## Consequence for the design

PKG-F moves from "design" to "instrument validated on dev". The next step is the recency-holdout arm and stationary
twins (cheap), then the preregistration after LM01 integration.

## v2: recency-holdout discriminator + stationary twins (results/pkgf_probe_v2.json; 32 dev worlds, 72 s)

Mean delta AC vs S on the headline test:

| stratum | S+D learned (holdout = all history) | S+D learned-recent (holdout = last 20%) | learned-recent weights |
|---|---|---|---|
| F3 cp (obsolete) | -0.90 | -0.01 | 0, .25, 0, 0 |
| F3 tt (obsolete) | -1.32 | 0.00 | 0, 0, 0, 0 |
| F2 cp (stationary twin) | +0.03 | +0.03 | .5, .5, 1, .5 |
| F2 tt (stationary twin) | 0.00 | 0.00 | 1, 1, .25, .25 |
| F2 lowrank / spectral | +0.01 / +0.09 | +0.01 / +0.09 | - |
| F5 cp / spectral | 0.00 / +0.04 | +0.03 / +0.04 | - |

DEV FINDING (provisional; 4 worlds per stratum; one readout family):
- The F3 harm from restoring obsolete distinctions VANISHES when the readout chooses its use of the channel on recent
  records. The obsolete information can stay stored and be IGNORED; it hurt only because the readout's selection
  signal was dominated by the old regime.
- In these worlds, discarding was NOT causally necessary. What mattered was the SELECTION SIGNAL (which records the
  readout trusts), not the storage.
- This bears directly on the ARC3 central question ("can irrelevant distinctions remain stored but simply be ignored?"):
  here, YES, given a regime-appropriate selection signal.
- Scope: an additive residual readout with a 4-value weight grid. The PKG-F campaign must add richer readouts, more
  worlds, the decaying-reliability nuisance (N5), and a regime-change detector that must DISCOVER recency rather than
  being handed "last 20%".
