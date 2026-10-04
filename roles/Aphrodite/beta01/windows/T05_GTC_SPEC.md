# T05 -- R7 IMPROVER-MUTABILITY PROBE: GENOME TRANSFER-CORRELATION (GTC), BOUNDED (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 5. Frozen in DEV-5, 2026-10-04. Rung **R7 IMPROVER_CHANGED** (necessary
condition). Program P2 (improver evolution) is kept separate from the compounding dispositions (W4). Evidence tier 2.

## 1. Question (W4 s6.2, adapted)
Does any CONTENT-FREE improver rule (a genome mapping the donor's own traces to its search/selection behaviour)
beat the ancestral improver I_0 on UNSEEN families? Does the advantage GROW from generation 1 to generation 2? And
can the instrument SEE a planted overfitter? If not, no outer loop could find a transferable, dynamics-changing
improver in this DSL, and P2 stops with a clean reason.

## 2. Apparatus
- `engine/v2b/gtc.py` (sha256 b3901fd2...): donor_g, a copy of a18.donor with genome hooks.
  **Conformance gate PASSED: donor_g('g0') == a18.donor on 3/3 real T51 donor jobs** (P, G1, PA kinds; selection,
  entries, table, meta charges, derivations identical).
- Genomes:

  | Genome | Rule |
  |---|---|
  | g0 | I_0 (ancestral improver) |
  | g2 | hits_per_obs = 2 |
  | g3 | trace-frequency proposal order (top-level operator of the donor's own solved observation programs walked first) |
  | g4 | replace-subsumed insertion |
  | **g5** | **observed-finals, the PLANTED OVERFITTER** (positive control for detecting overfitting) |

  g1 (P18 dovetail) is DEFERRED: it needs a search-loop rewrite. Declared.
- `engine/v2b/gtc_run.py` (sha256 f07934a8...); plan `beta01/runs/T05_GTC/GTC_PLAN.json` (sha256 f47aeafc...).

## 3. Design
- **Supply:** T51's qualified LIN foundry (escrow 30k; T4 v1 foundry qualification; same instruments).
- **Strata by top-level body operator:** DEV = {+, -}; UNSEEN = {*, //, %, gcd, pow}.
- **4 chains** (seed pairs 0->4, 1->5, 2->6, 3->7). All chains fill (plan check 4/4).
  - gen 1: donor_g(genome), start PRISTINE, OBSERVE 4 (DEV, 0 < p <= .75) + VALIDATE 4 (DEV) on seed c.
  - gen 2: donor_g(genome), start = gen-1 selected library, OBSERVE 4 + VALIDATE 4 (DEV) on seed c+4.
- **Scoring:** both generations' selected libraries, plus PRISTINE as reference, on seed c+4 held-out families never
  used in roles: 12 DEV + 8 UNSEEN, 1 cell each.
  - D endpoint: first T4-v1a-qualified program at <= 1M (artifact-confirmed). value = number of families solved.
- **Size:** 5 genomes x 4 chains x 2 generations = 40 donors. About 3-4 CPU-h. M4, 4 workers.

## 4. Frozen decision rules (gtc_run.stage_report)
- adv(g, gen, stratum) = value(g) - value(g0), per chain.
- **beats_unseen(g):** gen-2 UNSEEN advantage > 0 in >= 3 of 4 chains AND > 0 in total.
- **growth(g):** total gen-2 UNSEEN advantage minus total gen-1 UNSEEN advantage > 0.
- **genome variance share (UNSEEN, gen 2):** between-genome variance of means / total variance.
- **overfit_seen:** g5's total DEV advantage (gen 1 + gen 2) > 0 AND its total UNSEEN advantage < 0.
- **Verdict:**

  | Verdict | Condition |
  |---|---|
  | INCONCLUSIVE_FLOOR | every genome value is 0 |
  | INCONCLUSIVE_INSTRUMENT | g5 overfitting not seen |
  | **GO** | some g in {g2, g3, g4} has beats_unseen AND growth, AND share >= 0.10 |
  | **STOP** ("improver levers transfer-inert or one-shot only") | no candidate beats_unseen, or no candidate shows growth |
  | INCONCLUSIVE | otherwise |

## 5. Interpretation
- **GO:** some content-free improver rule has transferable, compounding value. That earns a preregistered P2 Stage-3
  (transplant + longer chains). It is still not RSI: it is R7 feasibility.
- **STOP:** no rule-level improver change transfers and grows in this DSL. R8 negatives cannot be blamed on missing
  R7 levers of THESE kinds. The improver limit is then representational or proposal-mechanism-level.
- **INCONCLUSIVE_INSTRUMENT:** the probe cannot see overfitting at this n. Nothing is read; the next DEV enlarges or
  repairs it.

## 6. Disclosure (pre-freeze smoke)
A smoke (chain 0; genomes g0, g5; scoring cap 20k, which is not the endpoint) validated run, score and report. Donor
selections do NOT depend on the scoring cap, so **chain-0 selections for g0 and g5 were seen before the freeze:**
- gen 1: (acc - {H}) for both;
- gen 2: ({H} + v) for g0, None for g5.
The smoke's report printout (20k cap, partial genomes) is not a result. The verdict rules above were already coded
before the smoke and were not changed afterwards (only the cap was made environment-driven). The smoke outputs were
deleted (chains sha256 prefix 20dfe6cb).
