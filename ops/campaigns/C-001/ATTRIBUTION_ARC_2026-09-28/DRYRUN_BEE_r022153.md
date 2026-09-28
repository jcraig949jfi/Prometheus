# v5 DRY RUN on BEE r022153 (Archaeon, 2026-09-28) -- NOT the production result

**What this is:** Archaeon's end-to-end run of the v5 pipeline on the drawn BEE run. It is a process commitment
(REVIEW_6_ADJUDICATION.md) to show, before any owner spends compute, that v5 is satisfiable AND informative on real data.
- **Replay:** the frozen harness (git 16fc6c2a, sha256-prefix pins checked) via Bellerophon's traced_replay, with observation-only
  pre-state capture.
- **Labels:** Archaeon's tracer, at commit 9cd6bb4ed (before Amendment C2). The C2 change affects only the reported dependence
  sets. v5 identification is interventional, so no verdict input below depends on C2.
- **Production** remains Bellerophon's native replay (#811/#817/#824), and must agree per locus with the reference tracer.
- **Code:** archaeon/attribution/probes/bee_dryrun_v5.py. Output: C:/Prometheus-data/evidence/attribution_arc_2026-09-28/dry_r022153.json
  (+ .births.json.gz). Run on ubu001, one core, 1,063 s.

## Numbers (birth-clustered bootstrap 95% CIs)

| quantity | value |
|---|---|
| replay vs preserved rows | 32,827 / 32,827 identical (bit-for-bit) |
| births | 32,827 |
| NO_MATERIAL class | 183 |
| TRANSMISSION class (written loci majority identified writer MOVE) | 30,945 (94.3%) |
| identifiable births (>= 90% of written loci identified), non-NO_MATERIAL | 95.2% (gate 80%) |
| performer classes | self 28,091 / other 4,684 / none 52 |
| **Q1: performer != majority donor**, transmission class | **14.0% [13.6, 14.4]**. All are performer = OCCUPANT copying the WRITER's material (4,313 births) |
| Q3: departure from uniparental inheritance, transmission class | 14.1% [13.7, 14.5] (almost entirely the Q1 births) |
| **Q8c** (value dependence outside {donor, performer}), transmission class | **0.0003 [0.0002, 0.0004]** |
| Q8c over all ENTITY loci | 0.027 [0.025, 0.028] |
| Q-homology: identified loci whose source locus != own index | 3.6% [3.4, 3.8] |
| source diversity | 0.997 (copying, not painting) |
| Q4: children capable (exact self-copy in >= 50% of 320 isolated trials), transmission sample | 85% [79, 90] (mean trial success 0.85) |
| flip test (sample 201 births) | 9,517 CONFIRMED, 0 FAILED, 2,595 INAPPLICABLE; coverage 0.79 (floor 0.50) |
| per-byte completeness leak | 0.05% (gate <= 5%) |
| per-byte precision of the dependence sets (reported, C1) | 0.17 |

**Q2** (native resemblance label vs copy-descent majority), over IDENTIFIABLE births:
- native "writer" (30,739): 52 are occupant-majority (0.17%);
- native "target" (333): **191 are WRITER-majority (57%)**;
- overall disagreement: 243 / 31,072 = 0.78%.

## Predictions (v4 s6 as amended by v5 R7)

| # | reading | result | outcome |
|---|---|---|---|
| P1 (Q-homology >= 90% positional) | transmission class | 96.4% positional | HOLDS |
| P2 (native "target" disagrees with copy-descent in >= 10%), v4 wording | all identifiable target-labelled births | 57% (191/333) | HOLDS -> ALTERED: BEE native material labels need an IBD correction field |
| P2, v5 R7 literal | transmission class only | 100% | circular (see below) |
| P5 (Q8c upper bound < 5%), BEE | transmission class | upper bound 0.0004 | HOLDS |

**Defect found in v5 R7 (by the dry run, AFTER the data):**
- R7 evaluates P2 on the TRANSMISSION class, which is DEFINED as writer-majority. So every "target"-labelled birth in it disagrees
  by construction (100%). The restriction is circular for P2.
- v4's original wording (all target-labelled births) is not circular, and it also HOLDS (57%). Both readings give the same
  outcome.
- The correction is recorded as Amendment C3, dated after the data and flagged as such. It does not change the outcome.

## What the dry run says v5 would return for BEE r022153 (subject to production)
- Q8c: VALIDATED territory (upper bound 0.0004 < 5%).
- P2 holds -> **ALTERED** (a native-label correction field is needed for BEE).
- Every gate passes: identifiability 95%, flip coverage 79%, 0 FAILED, completeness leak 0.05%, transmission class 30,945.
- Pending: the round-trip check into attribution-v0 records, the owner's tracer agreement, and the owner fixture pass.

## What this means for attribution v0 (provisional until production + review)
1. The singular-donor copy-descent record is ADEQUATE for 99.97% of the dependence in this run's transmission births (Q8c).
2. **Producer != donor is COMMON, not exotic: 14% of transmission births.** The occupant's code performs the copy of the writer's
   material (K3-type partner-performed copy). v0's separation of performer from donor is load-bearing in BEE.
3. BEE's native resemblance `material` label is wrong in 57% of the births it calls "target" (IBS read as IBD, measured
   byte-level). This confirms Review 1's untestable-v1 finding, now tested properly.
4. 85% of transmission children are isolated self-copiers. In this run, material transmission and capacity transmission mostly
   coincide.

## Dated correction 2026-09-28 (after adversarial Review 7; REVIEW_7_ADJUDICATION.md). The text above is kept as the original claim.
All numbers above were reproduced exactly by an independent reviewer with the independent reference tracer. These READINGS are
corrected:
- **(b)** "14% occupant-performed copy of the writer (K3-type)" -> a heritable PARASITE lineage.
  * 4,313 births; 83% of the parasite writers have no copy opcode; they fall through into the host's absolute-addressed copy loop.
  * Their children are 0/120 capable in isolation.
  * Randomising the host suppresses 88% of these births.
  * 18 of the 4,331 have performer "none" (INPUT/CONSTANT store opcode), not the occupant.
- **(a)** "singular-donor record adequate for 99.97% of the dependence" -> "0.03% of transmission loci change value when entities
  other than the donor and the performer are randomised". Existence dependence on the performer (0.88 in the parasite class) is
  not measured by Q8c. Q8c-whether was not computed; that is now required (C4).
- **(c)** "57%: IBS read as IBD" -> 57% [52, 63] (46% without the identifiability filter). Mechanism: 183/191 are frame-shifted
  copies, and positional fidelity is shift-blind; only 18/191 are IBS-as-IBD.
- **(d)** "material and capacity mostly coincide" -> they coincide for self-performed births (117/120 capable). They diverge
  totally for the parasite class (0/120).
- **Verdict:** "ALTERED via P2" -> v0 VALIDATED on this run (pending production, round-trip and tracer agreement). P2 holds as a
  BEE-native-label finding. The parasite class is represented by existing v0 fields (performer, donor, dependence, capability):
  v0's host_executed_copier fixture, found in a real run.
- **Pipeline deviations acknowledged:** flip test on the sample only; Q8c-whether missing; pooled flip coverage (the "other" class
  is 0.537, MARGINAL); the verdict was set by hand; the Q2 numbers came from an uncommitted births file (now committed:
  dry_r022153.births.json.gz).
