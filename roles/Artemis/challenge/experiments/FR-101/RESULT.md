# RESULT A-RUN FR-101 (reduced): particle2 vs generic rules under the same encoding

Artemis delegate, 2026-09-28. This run executes PREREG.md @ 591209b9e as written. The decision
rules, rule set, seeds and gate are unchanged. Not committed.

DECISION: CLOSE-with-note. particle2 is far above the random-rule band. Plain transport explains
the margin: shift1, shift2 and shift3 each score 1.000.

## Provenance and harness

- The code ran only in a `git archive` copy under the session scratchpad, with GIT_DIR,
  GIT_WORK_TREE and GIT_INDEX_FILE unset. OMP and OPENBLAS threads were set to 1, and
  `ulimit -v` was 2 GB.
- Archive sources:
  - herakles/ca_stream and herakles/evca @ 5a0458fd6 (on PYTHONPATH);
  - archaeon/campaign3 and archaeon/campaign2 @ cb9135104 (for the committed rows.json);
  - c3_sfe09.py @ fe3c1647c, which is byte-identical to the file at cb9135104.
- ca_stream/core.py, reset_v2.py and evca/genomes.py are byte-identical at 5a0458fd6, fe3c1647c
  and cb9135104.
- evca/core.py differs across those commits only by the `exact_count` IC option and comments.
  This harness does not use that code path.
- ClampedCA and feats are copied verbatim from c3_sfe09.py:45-71 @ fe3c1647c.
- base_acc reproduces c3_sfe09.run_genome lines 82-91 exactly:
  - catalogue: all_streams(8);
  - partitions: cs.partitions(256, 64, 64, seed=20260920+seed), train 64 / confirmation 128;
  - reset_root = 20260920+seed;
  - port 0, N=31, Bernoulli-0.5 reset, delayed recall d=2;
  - ridge lambda 1.0, threshold 0.5.
- Script: run_fr101.py (this directory). Raw data: rows.json (every rule x seed accuracy, gate
  rows, diagnostic rows, rule hex).

## Gate (harness validity): PASS, 8/8

Recomputed particle2 accuracies are within 5e-5 of the committed values in all 8 seeds. The
committed values are rounded to 4 decimals.

| seed | recomputed | C3-SFE-09 rows.json |
|------|------------|---------------------|
| 1 | 0.54036 | 0.5404 |
| 2 | 0.60026 | 0.6003 |
| 3 | 0.59245 | 0.5924 |
| 4 | 0.61198 | 0.6120 |
| 5 | 0.57422 | 0.5742 |
| 6 | 0.56641 | 0.5664 |
| 7 | 0.59115 | 0.5911 |
| 8 | 0.59896 | 0.5990 |

particle1 and GKL also match their committed C3 rows to 4 decimals in every seed. That was not
required by the gate.

## Rule set R and results (mean and sd of confirmation accuracy over seeds 1..8)

Rule definitions:
- Named rules: the 6 rules in herakles/evca/genomes.py NAMES, which C2 ran as ca:*. particle2
  and GKL are among them.
- Transport rules, built with the evca bit convention (neighbour j = cell i-3+j, j=0 is the MSB):
  - identity: new[i] = old[i];
  - shiftk: new[i] = old[i-k], so content moves away from port 0 toward higher indices.
- Supplementary rules shiftL1..3: new[i] = old[i+k]. They are not in the prereg transport set,
  so they do not enter the decision. The prereg does not fix a shift direction; both directions
  give the same answer.
- Random rules: `numpy.random.default_rng(20260928).integers(0, 2, size=(64, 128))`, one row
  per table.

| rule | family | mean | sd |
|------|--------|------|----|
| particle2 | named | 0.5845 | 0.0230 |
| particle1 | named | 0.5632 | 0.0240 |
| par | named | 0.5269 | 0.0180 |
| GKL | named | 0.5246 | 0.0171 |
| maj | named | 0.5226 | 0.0155 |
| exp | named | 0.5195 | 0.0179 |
| identity | transport | 0.5093 | 0.0239 |
| shift1 | transport | 1.0000 | 0.0000 |
| shift2 | transport | 1.0000 | 0.0000 |
| shift3 | transport | 1.0000 | 0.0000 |
| shiftL1..3 | supplementary | 1.0000 | 0.0000 |
| 64 random, mean of means | random | 0.5028 | (range of means 0.4883 - 0.5220) |
| random, 95th percentile of means | random | 0.5127 | numpy linear; nearest-rank 0.5127 |
| random, top 6 means | random | 0.5117 0.5125 0.5127 0.5130 0.5163 0.5220 | |

The per-rule table for all 64 random rules is in rows.json. Each random rule's per-seed sd is
0.009-0.030.

- particle2's percentile among the 64 random rules: 100. It is above every random rule, and
  above the maximum (0.5220) by 0.062.
- Transport means: identity 0.5093; shift1, shift2 and shift3 1.0000 each. The transport maximum
  is 1.0000 (shift1, first in order).

## Decision (applied verbatim)

- M(particle2) = 0.5845 > random 95th percentile 0.5127, so the rule is not CLOSE.
- M(particle2) = 0.5845 <= transport max 1.0000 (shift1), so the rule is not REOPEN.
- Result: **CLOSE-with-note: plain transport explains it.**

As the prereg specifies:
- The CA delayed-recall line stays closed.
- C4-10's retirement stands, now with a note: the margin is not an encoding or reset artefact
  (random tables sit at chance under the identical port, reset and readout), but a one-cell
  shift reaches 1.000 on the same task.

## Diagnostic (no decision): C2 reset-leakage probe with a non-index-order split

What changed relative to herakles/ca_stream/reset_v2.py:222-248:
- Lines 233-244 are unchanged: the no-injection reset-lattice features and the targets are
  computed exactly as in the probe. They are re-implemented in `reset_only_feats` with the same
  reset_seed, the same Bernoulli draw and the same `evca.step` loop.
- Only the split at lines 245-247 changes. The committed probe fits on feats[:128] and scores on
  feats[128:] in index order. This run computes three splits:
  - (a) index_order: exactly as committed, as a reproduction check;
  - (b) random_half: a 128/128 split from `default_rng(20260928+seed).permutation(256)`;
  - (c) base_partition: the base_acc partition, `cs.partitions(256, 64, 64,
    seed=20260918+seed)`, train 64 / confirmation 128.
- Settings are C2's: CAMPAIGN_SEED 20260918 (archaeon/campaign2/runner.py:47), seeds 1..4, all 6
  named rules.

Results, 24 rows (6 rules x 4 seeds):

| split | min | max | mean |
|-------|-----|-----|------|
| index_order (committed) | 0.4232 | 0.4779 | 0.4497 |
| random_half | 0.4635 | 0.5339 | 0.4991 |
| base_partition | 0.4583 | 0.5156 | 0.4927 |

- Split (a) reproduces the committed C2 reset_only_acc values exactly in 24/24 rows.
- For particle2 in seeds 1..4:
  - random_half: 0.487, 0.490, 0.512, 0.487;
  - base_partition: 0.488, 0.500, 0.474, 0.499.
- Under a non-index-order split, the reset-only readout sits at chance, scattered roughly
  +/-0.035 around 0.50. The committed "below chance" (0.42-0.48) is an artefact of the
  index-order split, as MATURE_REVIEW predicted.
- The record should cite reset-only = chance: no leakage, and nothing more. The C3 comparison
  point is particle2 base 0.540-0.612.

## Runtime

- 207 CPU-s (3.5 min wall), single thread, peak RSS 42 MB.
- This is well inside the 30 CPU-min expectation and the 60 CPU-min cap. The run is not partial.

## Surprising or worth noting

1. Random rules do NOT score above chance. All 64 random rules have means in 0.488-0.522, close
   to the 0.50 base rate. The encoding, reset and readout alone give no margin. This is the
   opposite of the Glover-style worry.
2. Every named density-classification rule beats the random 95th percentile (0.5127), including
   hand-designed maj (0.5226) and GKL (0.5246). The same holds for exp (0.5195) and par (0.5269).
   The "above random" property is therefore generic to density-classifying rules, not specific
   to evolved particle2. particle2 (0.5845) and particle1 (0.5632) are the top two.
3. The transport clause was bound to fire. Any shift rule makes x[t-2] sit at a fixed cell at
   time t, and ports never overwrite cells 1..3 or 29..31. A linear readout then solves d=2
   exactly. This is the same fact as C2's ShiftRegister control scoring 1.0.
   - The prereg's transport comparison therefore tests whether particle2 beats perfect memory,
     which no density rule could.
   - CLOSE-with-note is the correct verbatim label.
   - A reader should not take it to mean that particle2's 0.08 margin is "explained" by
     transport in a mechanistic sense. It means only that the task is trivially solvable by
     transport. This is an observation, not a change to the decision.
4. identity (0.5093) is near chance, as expected. The input sits only at port 0 at the current
   step, like DirectInput.

## Artemis reading (added after the result; the preregistered label stands)

The preregistered label is CLOSE-with-note. Artemis's own prereg was
partly degenerate: the transport clause could not fail to fire, because
any shift rule solves the d=2 task exactly (C2's ShiftRegister already
scored 1.0, and FR-101's UNCERTAINTY (d) said so). Logged in the
calibration ledger. What the run establishes, independent of the label:
1. The Glover encoding confound does NOT explain particle2's margin here:
   64 random radius-3 tables under the identical encoding score at chance
   (means 0.488-0.522).
2. C3's closing reading ("position-keyed reset readout") is not supported:
   the reset lattice alone scores at chance on a random split (mean
   0.499); the recorded "below chance" (0.423-0.478) is the index-order
   split artefact, reproduced exactly in 24/24 rows.
3. Above-random is generic to density-classifying rules (maj, exp, GKL,
   par, particle1 all above the random 95th percentile); particle2 is the
   best of them, and all are far below trivial transport (1.000).
Net: the CA delayed-recall line stays closed, but the reason on record
should change from "reset keying" to "the task cannot distinguish
computation: generic density rules beat random, trivial transport beats
all of them." Thread FR-101: ANSWERED (A-RUN).
