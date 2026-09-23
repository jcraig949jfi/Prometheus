# Campaign 0 (CWE instrument qualification) -- PREREGISTRATION

Seat: Cosmos[m2-6ed01908]. Written 2026-09-23 (UTC 11:4x) BEFORE the main Campaign 0
observations are collected. Committed in its own commit; the run that consumes it
records the code identity in <out>/identity.json and receipts/campaign_start.

## 0. The question (verbatim from the charter, s XXVI)

Can limited active experimentation over three structurally different executable
worlds recover a compact, normalized phase-boundary relationship that survives
deliberate counterexample construction and correctly predicts a preregistered
intervention in a sealed fourth world?

## 1. Objects

Phenomenon  SELECTIVE_PAYS.v1 (prometheus/cosmos/phenomenon.py): margin =
            fit(SEL) - max(fit(LOG), fit(LAST)), fit = (reward - cost) / reward_per_success,
            PAYS iff margin >= 0.10. WSE contract (archaeon/wse/ssf.py:66,103,107) not
            mutated; translation manifest in the module docstring.
Visible     regs (metered register VM, bit flips, no repair, unbounded registers)
families    ring (delay line, packet loss, dead memory is free, capacity n, eviction)
            ca   (block CA, cell flips, optional majority repair r=3, finite tape)
            Lineage audit: 3 independent lineages (test_planted).
Sealed D    well (overdamped Langevin multi-well attractor; Kramers-approximate hazard).
            sealed_spec.json sha256
            48e709653f2bbda12c6b1d1c499d801339ec7897e9bf3081764c50691cfa8265
            (committed 800072c1e, pushed to origin before this file).
Coordinates declared from the spec only: C (maintenance cost of one cue over the horizon /
            reward), N (expected corruption events on one retained cue; v1 raw carrier count,
            v2 after native repair; only ca differs), K (irrelevant observations), G = 1 - 1/V.
Grammar     terminals C N K G; unary log, exp(-x); binary + - * /; size <= 6; laws = one
            atom or a conjunction of two; LOLO (leave-one-lineage-out) scoring;
            S = mean fold BA - 0.004 * complexity; worst-fold gate 0.75;
            whole-search permutation null (labels permuted within family), n_perm = 19,
            p <= 0.05 required, else NONE.

## 2. Procedure (prometheus/cosmos/campaign0.py, CAMPAIGN_SEED 20260923)

1. Pools: 1200 lattice worlds per visible family. Private oracle labels all of them
   (scoring only; strategies see spec-side fields only -- whitelist test).
2. G1 validity; sampler efficiency (random/grid/boundary/active at budgets 30 and 60 per
   family x seeds 1,2,3; metric = BA on the oracle pool of the law mined from the queried
   rows, plus a 5-NN reference).
3. Main dataset = ACTIVE sampler, 80 queries per family (240 total), seed 20260923.
   Matched single-knob neighbours (cost and noise knobs, 8 worlds per family) go to the
   graph and G1 only, never to mining.
4. Mining on v1 (PRIMARY). v2 and "raw" (C multiplied back by the reward unit R, i.e.
   the cost left in native currency) are DECLARED SECONDARIES, reported, not selected.
5. Adversary: up to 3 rounds. Each round 48 attacks per family (band / coordinate-
   preserving transforms / extremes / error-seeking). A confident (P >= 0.9 or <= 0.1)
   contradiction counts only if two fresh replicates at 4x episodes also contradict with
   |margin - 0.10| > 2 SE. FAILED if confirmed / confident > 0.05. On FAILED the law is
   kept as FAILED with its counterexamples and re-mined on all observed visible rows
   (v1 and v2 both mined; v2 is picked only if it is CANDIDATE and beats v1 by > 0.01
   score). The revised law is a new ledger row with parent = the failed law.
6. The final SURVIVED law is frozen (freeze hash in the ledger and the receipt chain),
   then G5 and G6 run through the broker. If no law survives, G5/G6 are NOT REACHED and
   the campaign result is "no surviving invariant" -- a legitimate outcome.

## 3. Gates (implemented in campaign0.py; thresholds fixed here)

G0 Reproducibility    30 random main worlds replay to identical observation digests AND
                      the receipt chain verifies.
G1 Validity           per family: 0/20 sham worlds PAYS; oracle PAYS rate in [0.05, 0.95];
                      >= 90% of cost-increasing matched edges leave SEL fitness non-increasing.
G2 Compression        final law: worst LOLO fold BA >= 0.75, mean >= 0.85, and law score
                      >= raw-coordinate best score + 0.03 (normalization must earn itself).
G3 Artifact resist.   planted suite (tests marked slow) passes on the campaign commit:
                      positive + interaction recovered (functional agreement >= 0.95/0.93),
                      artifact not promoted, broken -> NONE, null -> NONE,
                      shared-code -> NONE or INSUFFICIENT_INDEPENDENCE.
G4 Adversarial        a law reaches SURVIVED within 3 rounds.
G5 Held-out           sealed-D balanced accuracy >= 0.80 AND >= (5-NN transfer from visible
                      rows) - 0.05. Majority-visible baseline reported.
G6 Intervention       protocol inside the sealed spec: 12 bases (law P >= 0.9), do(kappa: a -> a f);
                      direction correct on >= 10/12 AND |log2(f_obs / f_star)| <= 1 on >= 8/12.
G7 Family residual    family-dependence permutation test: PASS if p > 0.01 or mu < 0.02 bits/row.

Each gate is reported as PASS / FAIL / NOT REACHED; a gate that did not execute is never
reported as passed.

## 4. Precommitments written to be lost (Cosmos's own predictions, before data)

P1  The first v1 law will have a band structure (two atoms: a cost ceiling from the
    memoryless reference and a cost floor from the logger reference).
P2  The v1 law will be attacked successfully through the ca family's redundancy transform
    (r 1 <-> 3 at constant v1 coordinates), so round 0 FAILS; v2 will be picked on revision.
P3  Capacity (ring n, ca Lc) is not a declared coordinate; I expect it to generate
    counterexamples to the cost-floor atom (the logger loses its cue when crowded).
P4  Active sampling beats random by >= 0.03 law-BA at budget 30 (mean over seeds).
P5  G5: the Kramers-declared N of the sealed family is accurate enough that G5 passes;
    my confidence is low (0.5), because the approximation is poor at low barriers.
Any of these may be wrong; the calibration ledger records the outcome.

## 5. Conflicts of interest and known weaknesses (declared)

- One author wrote all four families, the phenomenon, the miner and the gates. The lineage
  audit detects shared CODE, not shared IDEAS; the four physics were written knowing the
  shared functional task. Independence here is implementation-level only.
- The sealed family's physics was written by the same author before sealing; only its
  outcomes are sealed (never computed in the mining process), not its design.
- The shared functional demand and the shared certificate are a single evaluator by
  construction (the phenomenon definition). Physics evaluators are independent.
- Before this file, an engineering runtest ran a QUICK campaign (150-world pools, budget 30,
  n_perm 5) on the visible families; only its gate verdicts were displayed
  (G0 PASS, G1 PASS, G2 FAIL). No visible-family law expression was inspected. The sealed
  family has never been run except the controls-only selftest on two fixed non-sealed worlds.
- Clock: the Hour-1 status of this campaign carried an ESTIMATED timestamp (12:21Z); the
  true time was ~11:1xZ. Recorded in roles/Cosmos/calibration/LEDGER.md.

## Amendment A1 (2026-09-23 ~11:55Z, BEFORE any main-dataset law was computed)

Run 1 (c0_main_1d4465df9, code 1d4465df9) crashed at the first mining call with
BrokenProcessPool (a null-search worker died at spawn; the machine was resource-starved:
`tasklist` hung at the same time). Outputs that existed at the crash: identity, oracle
summary, G1 (PASS), sampler_eta (read; P4 LOST, recorded in the calibration ledger). No law
on the main dataset was computed or seen. Run 2 reruns the SAME procedure with the SAME
seeds (the main dataset is deterministic: G0), changed only as follows:
- engineering: the null pool retries with half the workers, then serially, on a crash
  (miner._null_scores); default workers 10 (was 20); crashes listed in REPORT.
- attack composition: each coordinate-preserving attack also observes its base world
  ("coordpres_base", counted inside the same per-family quarter of 48 attacks), and the
  report adds metamorphic pair statistics (same declared coordinates, different
  microphysics: verdict flips). Kill rule, confirmation rule and thresholds unchanged.
- reporting: world quotient and all-observation log. No gate threshold changed.
The sampler_eta results of run 1 are the preregistered eta result; run 2 recomputes them
identically (same seeds) and both are kept.
