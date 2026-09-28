# Threshold provenance and bar-sensitivity of the latest engine verdicts

## 1. WHAT I SET OUT TO TEST

For the latest verdict of each engine, I checked two things about every threshold that decided it. First, where the number came
from: was it derived (from a replicate spread, a permutation null, a bootstrap SE, or a planted-positive check) or authored (a
round number, a seat's choice, or an operator ruling), and was it fixed before or after the data were seen? Second, how far the
observed statistic sat from the bar, in SE units, and whether the verdict flips when the bar moves to a defensible alternative
(x0.5 / x1 / x2, about +-1 SE, or a relative bar). I recomputed labels only from rows that are already committed. The aim was to
tell whether verdicts decided by an arbitrary bar are common in the program or only anecdotal. I also checked whether "derived
versus authored" is the right axis at all, or whether "fixed blind and shown to be attainable" matters more.

## 2. WHAT I DID

No engine was run. All work was read-only reading of documents plus label recomputation over committed JSON, using Python 3
stdlib only. Inputs were exported with `git archive` into `src/` under my scratch directory. Each input and the sha it was read at:

- Aether mechanism combinations and content control: `Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md` s2.3, s3, s5, and
  `ops/campaigns/C-002/E-006/REDUCTION.json`, both @77b11cef5 (branch origin/aether/research-block-2026-09-27). The
  preregistration commit is 39b7f7e85. The earlier round is `Aether/pivot/AETHER_REVIEW_2026-09-27.md` @ee81c0474. Per-origin
  unit files for the combinations are not committed (they are kept off-repo), so I used binomial SEs over 128 origins and the
  per-seed P_sust values quoted in s5.2.
- Ananke mechanism adjudication: `roles/Ananke/pte/c1b/REVIEW_PACKET_PTE_C1b.txt`, `roles/Ananke/pte/PREREG_PTE_C1b.md`,
  `prometheus/ananke/c1b.py`, `c1b_run.py`, and `roles/Ananke/pte/c1b/c1b_rows/rows.jsonl.gz` (27 rows), all @cc98596dd.
- Cosmos memory certificate gate: `roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md`, `runs/GATE_v3_PASS_seeds6to10.json`, and
  `runs/GATE_v3_seeds1to5_notgated.json` @940b486f2.
- Cosmos law-finder location gate: `roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt`, `c1/PREREG.md`, `c2/PREREG.md`,
  `c2x/PREREG.md`, the `adversary.json` files of c1/run2, c2/run_7b14ec99e and c2x/*, and `prometheus/cosmos/locate.py` and
  `campaign0.py`, all @af2af37f4.
- Ensorain LM01: `ensorain/PREREG_WTP_LM01.md` @768ea8ce9 (v0.3.1) and @ee8cbe0c8 (v0.3.2, frozen 2026-09-28). No campaign rows
  exist.
- Ares cycle 2: `ares/DESIGN_C2.md`, `ares/ARES_CYCLE2_REPORT.md`, and `ares/runs/sweep_c2/{gates,recheck,battery}.json`
  @origin/main 6ff2b2f8a (last changed 1dde117f7/3f68be2b9).
- Nestor copy-causality reassay: `roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/{S1C_P11_REASSAY.md,P11_REASSAY.json,
  P11_REASSAY.jsonl}` and `roles/Nestor/campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md` @6ff2b2f8a.
- Archaeon causal lens: `archaeon/causal_lens/PORTABILITY01_REPORT.md` and `V02_REGRESSION_REPORT.md` @6ff2b2f8a.

Code: `analysis.py` in my scratch directory, run once as
`env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 analysis.py`. Its outputs are `results.json` and
`analysis_output.txt`. The script does the following:

1. Aether: recomputes N1, N2 and E-P1 from REDUCTION.json on a 3x3 grid of (floor x0.5/1/2) x (component multiplier x0.5/1/2).
2. Ananke: re-implements the preregistered M3 decision list (T, X, R, M, then the first matching rule) and applies it to the
   specimen rows and the fresh-seed rows. The grid is the SIGNAL bar (lo99 > 0.525 / 0.55 / 0.575) crossed with six bar
   settings: as frozen, absolute x0.5 and x2 of the above-chance margin, and three relative bars that scale with each champion's
   own normal accuracy (f = 0.3 / 0.5 / 0.7). At the frozen bars my relabeller reproduces every committed label exactly (specimens
   TRANSPORT+RULE_SWITCH; fresh f6b6 k0/k1/k3 = C1_CONTROL_NOT_REPRODUCED / RULE_SWITCH_ONLY / NOT_SUPPORTED).
3. Cosmos certificate: reclassifies all 30 gated rows at alpha 0.01 / 0.02 / 0.04 and a P2 z-bar of 1.5 / 3 / 6.
4. Cosmos location gate: recomputes every gated law-round at tolerances 0.05 / 0.10 / 0.20 log2. The locate.py 2-SE rule is kept
   unchanged.
5. Ares: recomputes Gates A, B and C at bars near +-1 binomial SE, under both the code's and the preregistration's reading of
   Gate A.
6. Nestor: counts how many survivors depend on the 2-of-3 draw majority.

Approximation: the Ananke "drops" clause needs lo99 of a paired difference, and that difference is not stored in the rows. I
estimated it from the arm CIs. The estimate reproduces all committed R booleans.

## 3. RESULT

Provenance table. Margins are (observed - bar)/SE, and a positive margin means the gate passed.

| engine / verdict | deciding bar | source | fixed when | margin | flips in range? |
|---|---|---|---|---|---|
| Aether rcv_add NEW_BEHAVIOUR | P_sust >= max(0.10, 2x comp.), super-additive | authored floor (binds) | prereg, before runs; floor carried from prior round | +2.2 SE (binom), +3.6 (per-seed) | no (9/9 cells) |
| Aether rcv_str NEW_BEHAVIOUR | same; N2 P_content >= max(0.05, 3x comp.) | authored floor / authored 3x | same | N1 +0.34 SE (binom), +0.59 (per-seed; 1 seed 0.062); N2 = 0.0 (12/128 equals 3 x 4/128 exactly, a tie passed by >=) | YES: 5 of 8 non-baseline cells give ADDITIVE_OR_LESS (floor x2 or multiplier x2) |
| Aether rcv_cnd ADDITIVE_OR_LESS | same | authored | same | -7.7 SE | no |
| Aether content control E-P1 FAILED | fwd preserved >= 0.05 | authored | prereg | -1.2 SE | YES at floor x0.5 |
| Ananke M3 = transport on readout tick | kills hi99 <= 0.60; C1-window lo99 >= 0.62 | authored | prereg, before any row | kills: large; C1 window +1.4 / +2.0 SE (clause NOT_ELIGIBLE anyway) | no (except x2, where bar > normal acc.) |
| Ananke M3 needs SETRULE | drop >= 0.10 | authored | prereg | drop 0.16-0.17 | no |
| Ananke M3_REPRODUCED: NO | SIGNAL lo99 > 0.55 plus absolute kill/intact bars | authored | prereg | SIGNAL misses: 0a23 k2 -0.03 SE, k0 -0.73; f6b6 k2 -0.97. C1-window bar 0.62 lies above the normal accuracy of f6b6 k0 (0.557), so it cannot be met. For k0 the normal arm's own hi99 (0.578) is <= 0.60, so "kills" is automatic | YES: relative bars (f = 0.3/0.5) give f6b6 3/3 fresh = specimen label, and abs. x0.5 gives 2/3. Reproduced in 11 of 18 grid cells |
| Ananke M2 in flight, reproduced 3/3 | flush kills hi99 <= 0.60 | authored | prereg | +7 to +15 SE | no |
| Ananke M2 not a pure delay line (B false) | lo99(diff) >= -0.10 | authored | prereg | point diff -0.062; paired CI not committed | not computable |
| Cosmos memory certificate gate PASS | P1 perm p <= 0.02 (49 perms); P2 > 3 bootstrap SE | derived (null / SE) + planted 6-system gate | revised twice after data (smoke, failed v2 gate); gated on fresh seeds | P2 z 15-17 (NZ); P1 at p = 0.02 = the minimum attainable | no at alpha 0.04 or z 1.5-6; alpha 0.01 is unattainable with 49 perms (gate FAIL, 10/30) |
| Cosmos law B SURVIVED (location gate) | per-family abs(offset) > max(2 SE, 0.05) and > 0.10 log2 | authored 0.10 (+ derived 2 SE) | after the frozen law's offsets were seen, before the C1/C2 data | -12.5 SE | no |
| Cosmos round-0 law FAILED (why law B exists) | same | same | same | +1.01 SE (regs -0.168, SE 0.067) | YES at 0.20 |
| Cosmos C1: 3 laws FAILED at 2-4% contradiction | same | same | same | +6.0 to +9.1 SE (offsets -0.43 to -0.55) | no: they fail at 0.20 too |
| Cosmos post-holdout arms (descriptive) | same | same | same | c2none28 round 0 FAILED at -0.1003 (+0.01 SE); its survivor passed at +0.097 (-0.36 SE); c2none round 0 +0.99 SE | YES (3 law-rounds) |
| Ensorain LM01 (no verdict yet) | equivalence margin DELTA 0.30 | operator ruling (replaced a retired replicate-derived margin) | after dev rows were read, before campaign rows | n/a | n/a. Positive control E6 passes in 10 of 41 testable strata (v0.3.1), so most absence readings will be UNRESOLVED by rule |
| Ares Gate A OPEN (substitution) | >= 5/10 | authored count | prereg | text reading: c2_no_recur 10/10 above threshold, 0 RECUR (robust). Code reading (majority-class count): 6/10, 5/10, 5/10 (+0.6, 0, 0 SE) | code reading flips at >= 7; text reading does not |
| Ares Gate B ACCESSIBILITY | >= 7/10; p_create(rec) > p_create(keep) | authored count; derived strict inequality | prereg (guard added after smoke) | keep 9/10 clean (+1.4 SE); p_create diff +3.2 SE | no |
| Ares Gate C SHUT (not transplantable) | portable >= 5/10 OR swap >= 0.5 in >= 5/10 | authored count | prereg; statistic corrected after results (max-of-9 to per-pair) | portable 4/9 (-0.33 SE); swap 16/59 (-3.5 SE) | YES: OPEN at a bar of 0.4 (about -0.6 SE), and OPEN under the pre-correction per-host statistic (6/8) |
| Nestor copy-causality: 57 of 1,031 survive | fidelity >= 0.90; authorship >= 0.90; >= 2 of 3 draws | 0.90 fidelity: operator directive; 0.90 authorship and 2/3: seat, before data; fixtures as planted positives | before any case was inspected | per-draw values not committed. 26 of 57 survivors are single-event runs passing exactly 2 of 3 draws. 18 of 57 first events sit at 29/32 = 0.906, the smallest value above 0.90 | count: YES, 57 -> 29-31 under 3 of 3. Conclusion (small minority, depth-1 dominant, no depth 3): no, in the tightening direction; loosening not computable |
| Archaeon causal lens PORTABLE_WITH_DOMAIN_LIMITS | checklist of qualitative promotion criteria | operator ruling | before the regression | no numeric bar decides | n/a |

Counts. I counted 17 numeric verdict components across 6 engines. Archaeon (qualitative) and Ensorain (no verdict) are excluded.

- |margin| < 1 SE, or a tie: 3 components (Aether rcv_str; Ares Gate C; Ananke M3_REPRODUCED, whose deciding SIGNAL misses are
  -0.03 and -0.73 SE and whose C1-window bar cannot be met). At about 1 SE there are 2 more (Cosmos round-0 location kill at
  1.01 SE; Aether E-P1 at 1.2 SE).
- Verdict flips inside the stated range: 5 of 17 (29%): rcv_str, E-P1, M3_REPRODUCED, the Cosmos round-0 kill and Ares Gate C.
  Adding the P-11 survivor count, which roughly halves under the stricter 3-of-3 majority, gives 6 of 17 (35%). One more
  component (Ananke M2 "B false") cannot be computed from committed rows.
- Engine level: 4 of the 6 engines with numeric verdicts (Aether, Ananke, Ares, Nestor) have at least one bar-decided component
  in their latest verdict. Cosmos has one only in a sub-verdict (which law was frozen) and in post-holdout descriptive arms.
- Authored bars with no attainability check: almost every authored bar lacks an explicit attainability check. The exceptions are
  the Cosmos certificate gate, Nestor's fixtures, and Ananke's eligibility plants, which gate only absence readings. In two cases
  the check that does exist shows the bar is not attainable: Ananke's absolute bars for champions near 0.6, and Aether's content
  bar, which its own planted positive (fwd) fails.

Plain conclusion: bar-decided verdicts are not anecdotal. About 30-35% of the latest verdict components move within a defensible
bar range, which puts the program at or just under the one-third line and far above the 10% line. The headline dispositions are
mostly robust, though:

- Aether's "interactions are real" stands on rcv_add alone.
- Cosmos law B holds.
- Ares CONTINUE holds through Gates A and B.
- Nestor's "narrows sharply, none at depth 3" holds.

What is bar-decided is mostly a second positive (rcv_str), a negative (M3 not reproduced, Gate C shut, E-P1), or a count.

## 4. DID IT RESOLVE THE QUESTION

Partly.

What it resolved:
- The provenance table and the margins are complete for the verdicts listed.
- The flip fraction is measured for every verdict whose committed rows allow it.

What it did not resolve:
- The Aether combination per-origin rows and the Nestor per-draw statistics are not committed. Those margins rest on binomial
  SEs and summary fields.
- The Ananke paired-difference CIs had to be approximated. The approximation matches every committed label.
- "Latest verdict" is a moving target. Ananke and Nestor have committed later work (Ananke W-series deposits, Nestor P2) that I
  did not census.

On whether "derived" is safer, the evidence splits the question:
- Every derived bar in the set (the Cosmos permutation/SE rules, Ares' strict inequality, the 2-SE part of the location rule)
  was robust.
- But derived bars do not remove near-bar cases caused by small n. The Cosmos location gate's own SE (0.03-0.07 log2) is a third
  to two thirds of its 0.10 tolerance, so a law with a true offset near 0.10 is a coin flip under any bar.
- The failures that carry the most weight are attainability failures: Ananke's absolute bars are unattainable for champions near
  0.6, Aether's content metric fails its planted positive, and alpha is set at the permutation-resolution floor. They are not
  failures of authorship as such. This supports "fixed blind, checked for attainability, and reported with its SE margin" over
  "derived versus authored".

## 5. CONSEQUENCES

No false premise was found; the premise holds. This work reproduces what was already known (the Ananke absolute-bar limitation
and the Aether rcv_str thin pass) and adds new specifics:

- Aether: rcv_str's N2 pass is an exact tie (12/128 = 3 x 4/128) admitted by ">=". Its N1 pass is 0.34 SE over an authored
  floor. The N2 content metric failed its own positive control (E-P1) in the same block, yet it still counted toward
  NEW_BEHAVIOUR. rcv_str should be read as UNRESOLVED, not NEW_BEHAVIOUR. rcv_add is unaffected. The Aether seat should know.
- Ananke: under a bar that scales with each champion's normal accuracy, the fresh f6b6 champions all take the specimen's label
  (3/3), so "M3 not reproduced (mechanical)" flips. For fresh k0 the normal arm itself satisfies "kills", so its
  C1_CONTROL_NOT_REPRODUCED label is produced by the bar and says nothing about the physics. 0a23's "0/4 reach SIGNAL" includes
  a miss by 0.0005 (-0.03 SE). The Ananke seat should know. A relative-bar amendment is the fix, and it must be written before
  any new rows.
- Ares: Gate C is shut by one organism (4/9 against 5/10). "Transplantability refuted twice" should carry that margin. The code
  implements Gate A differently from the preregistered text; the disposition does not change. The Ares seat should know.
- Cosmos: the question of whether the 0.10 location tolerance is arbitrary is answered for the kills it was asked about. The
  three C1 laws with 2-4% contradiction rates fail at 0.20 too (6-9 SE), so those kills are not decided by the bar. The
  tolerance did decide which law became law B: round 0 was killed at 1.01 SE. In the post-holdout attribution table, one cell is
  decided at 0.01 SE and again at 0.36 SE. The Cosmos seat should know.
- Nestor: the reassay's per-draw fidelity and authorship values are gitignored, so its margins cannot be audited from the
  repository. 26 of the 57 survivors rest on a single event passing exactly 2 of 3 draws. The Nestor seat should commit per-draw
  values or report the survivor count at 3 of 3 alongside the headline.
- Ensorain: LM01's operator-ruled DELTA is fixed blind (good), but its own positive control passes in only 10 of 41 testable
  strata. Most absence readings are therefore UNRESOLVED by construction. That should be stated before the campaign spends
  compute.
- Program: I recommend a fleet rule. Every deciding gate should record its source, when it was fixed, an attainability check
  (a planted maximum-effect case or a relative bar), and the margin of each verdict in SE units. The number of seats that
  re-derived their bars after seeing data (Cosmos twice, LM01, the Ares Gate C statistic) suggests freezing the rule blind
  matters more than whether the number was derived.

## 6. COST

About 2.5 hours of agent time. Under 1 CPU-minute of computation (a single stdlib Python pass, under 1 s). No engine runs, no
GPU, no sealed or holdout data, no database queries. I could not do the following:

- Recompute Aether margins from per-origin rows, because they are not committed.
- Compute Nestor per-draw margins, or any loosened P-11 bar, because the values are not committed.
- Recompute Ananke paired-difference CIs exactly.
- Relabel the two Ananke fresh searches that would reach SIGNAL at a lower bar, because their batteries were never run.
- Census the newer Ananke and Nestor verdicts committed after the listed inputs.
