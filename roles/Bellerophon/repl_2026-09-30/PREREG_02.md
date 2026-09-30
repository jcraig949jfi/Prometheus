# E-BEL-REPL-02 -- preregistration: adversarial transformations of the E-BEL-REPL-01 residue

Author: Bellerophon (M2 / SPECTREX5), 2026-09-30. Work order: MWO-0004 + CWO-2026-09-30 s3 BELLEROPHON NEXT, promoted
automatically when E-BEL-REPL-01 closed (DISAPPEARS K3; RESULT.md 279927367).
Frozen files: this file, tools/falsify_run.py, tools/falsify_analysis.py, plus the REPL-01 frozen tools they import
(state_free.py, pilot_worlds.CELL, repl_analysis.fisher_one_sided, FOUNDERS.json). They are hashed in
FREEZE_MANIFEST_02.json in the freeze commit, which precedes every output.

## 0. The residue under test

E-BEL-REPL-01's K1 and K4 survived. The descent reading failed. What is left is a BEE-only candidate:

> In BEE (grounding G1 ENDOGENOUS_PARTIAL/Z80_64 cell), a PARTIAL register scaffold (CARRIED with zero reset at p = 0.9;
> "P90") makes STATE_FREE genomes come to DOMINATE the population more often than an always-present scaffold (ZERO).

REPL-01 read this only through a lineage label (G), and that label is now discredited. This experiment re-reads it
LABEL-FREE on fresh seeds, and then asks which transformations break it. The CWO requires this before any promotion.

## 1. Readout (label-free)

- **DOMINANCE (per run):** at the final checkpoint (tick 2000, or extinction) the population is alive AND at least half of
  the live organisms carry a STATE_FREE genome (tools/state_free.py ruler, unchanged).
- **Strict ruler (M5):** STATE_FREE_strict = at least 16/20 trials produce an EXACT window copy, from both R1 and R2.
  Planted controls: vm.replicator is strict-free and the zero-dependent copier is not (checked before freezing).

## 2. Arms (fresh seeds 33,000,000 + s; paired: the same seed and founder in the P90 and ZERO arms of a transformation)

| transformation | change from REPL-01's BASE world | arms | pairs |
|---|---|---|---|
| BASE | none (founders transplanted, ENDOGENOUS_PARTIAL, mutation MED) | P90, ZERO, RANDOM | 50 |
| NOFND | no founders: random populations only | P90, ZERO | 200 |
| COPY | reproduction ENDOGENOUS_COPY (a birth needs a full-window copy) | P90, ZERO | 50 |
| MUTLO | mutation_rate LOW | P90, ZERO | 50 |

RANDOM means every execution starts from uniform random registers: the strongest payoff for state-freedom.
Total: 750 runs, of which 400 are cheap NOFND runs that mostly go extinct. Estimated ~6-8 core-h, within MWO-0004 R2
(<= 16 per item; today's total stays <= 48).

## 3. Tests (tools/falsify_analysis.py)

For each transformation t: count DOMINANCE in t:P90 and t:ZERO, then apply a one-sided Fisher test (P90 higher).
The reading is:
- **INCONCLUSIVE_POWER** if either arm has fewer than 10 runs alive at the end;
- **ABSENT** if P90 has fewer than 4 dominance runs;
- **HOLDS** if p < 0.05;
- **BROKEN** otherwise.

| test | question |
|---|---|
| M1 BASE | does the residue replicate label-free on fresh seeds? |
| M2 NOFND | does it need the founders? Expected INCONCLUSIVE_POWER: in the pilots, random populations persisted in ~3/100 (ZERO) and 0/100 (plain CARRIED) |
| M3 COPY | does it need 1-byte partial-write physics? |
| M4 MUTLO | does it need mutation supply? |
| M5 STRICT | does it survive a stricter competence ruler (BASE runs, re-read)? |
| M6 RANDOM | reported: is RANDOM >= P90, i.e. is the response monotone in payoff? |

**Verdict:**
- **RESIDUE_NOT_REPLICATED:** M1 is not HOLDS.
- **SURVIVES_ALL:** M1 holds and none of M2-M5 is BROKEN or ABSENT (INCONCLUSIVE_POWER is not a break).
- **CONDITIONAL:** otherwise; the verdict lists what it breaks under.

A CONDITIONAL is a mechanism map, not a failure: it says what the phenomenon depends on.

## 4. Exposure and precommitments

- **Seen before freezing:** REPL-01's full results (the source of this residue), and two smoke runs (pair 900; only
  alive counts and cost were read).
- **Precommitments I can lose:**
  * M1 HOLDS;
  * M3 COPY BROKEN or ABSENT (I expect the phenomenon to live in partial-write turnover);
  * M4 HOLDS;
  * M5 HOLDS;
  * M6 MONOTONE.

## 5. Custody

- Outputs go to C:/Users/James/repl_2026-09-30/production_02/ and are sealed (sha256) and committed before the analysis runs.
- The analysis runs once.
- The run happens under an M2 lease; the token is kept this time.
