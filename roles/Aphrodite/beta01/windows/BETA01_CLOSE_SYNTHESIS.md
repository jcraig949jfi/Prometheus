# BETA-01 CLOSE SYNTHESIS (C-006 / C-P2B-APH-BETA-01, TH-P2B-APHRODITE-V2B)

Written 2026-10-05 after TEST-12. Twelve DEV/TEST pairs ran from 2026-10-04 11:00Z to 2026-10-05 15:31Z, about 28.5 h
of wall time (the nominal budget was 96 h). Evidence tier 2 throughout: local CPU engine (world W5), no live models,
no W5P assay, no GPU. Historical labels are unchanged. Errata are recorded in place.
Midpoints: MIDPOINT_1_SYNTHESIS.md (after T04) and MIDPOINT_2_SYNTHESIS.md (after T08).

## 0. The twelve tests

| Test | Question | Disposition | One-line result |
|---|---|---|---|
| T01 | known-answer apparatus assay | QUALIFIED | 10/10. The v2b apparatus is fit for use |
| T02 (T53) | A23 capability re-score | MEASUREMENT_FAILED | control mis-specified. Correction: G1 distinct-class 5/10 < 6; shams 8/9/10 |
| T03 (T52) | validation-dose response | MEASURED | selection = recovery of SHOWN structure (0.11 / 0.46 / 0.875) |
| T04 (T51) | natural recurrence, LIN 0-7 | MEASURED | dose slope not shown. Exploratory: a pristine donor derives the base class |
| T05 (GTC) | R7 rule genomes | INCONCLUSIVE_INSTRUMENT | UNSEEN stratum floor; rule genomes output-inert |
| T06 (T51-C) | confirm endogenous derivation | MEASURED, not confirmed | ratio 0.644; when derived, 100% recovery |
| T07 (R7E) | rule changes on the endogenous route | MEASUREMENT_FAILED | oracle gate mis-specified. Diagnostic: correct candidates rejected in 5/15 seeds |
| T08 | validation breadth 4 -> 12 | MEASURED, NO | 86 -> 76 on that draw (later shown to be draw-dependent) |
| T09 | subset-benefit criterion g10 | MEASURED, NO | 98 vs 93, 1/0/14. Erratum: MEMORISE is the hidden winner |
| T10 | OBSERVE breadth 4 -> 10 | MEASURED, NO (rescue YES) | starvation fixed in 2/3 seeds. Erratum: losses are MEMORISE, not derivation |
| T11 | abstraction-only candidacy g11 | MEASURED, NO (underpowered) | 123 vs 99, 4/0/11, p 0.0625 (the attainable minimum); exposed seeds |
| **T12** | **fresh-seed replication** | **MEASURED, YES** | **g11 O10 60 vs I_0 20 on unexposed LIN 16-23; 5/0/3; sign-flip p 0.031** |

## 1. Threads

**TH-018 (first-order compounding).**
- **Constructed recurrence:** compounding is recovery of shown structure (T52, T53-C). Capability is generic and
  occurs only with motif recovery.
- **Natural recurrence:** a pristine improver derives a reusable base abstraction from 4 to 10 observations.
  - Under I_0 it often fails to KEEP it, because its acceptance test prefers memorisation.
  - Fixing that one rule triples held-out reuse on unexposed seeds (T12).
- **Composition beyond the base class pays little** (T51).

**TH-019 (recurrence x visibility).**
- **Recurrence:** present in W8 lineage worlds.
- **Visibility:** adequate at escrow 30k. The historical 250k escrow was the visibility limit.
- **Observation breadth:** fixes outright starvation (T10).
- **Validation evidence:** heterogeneous, and draw-dependent (I_0 at breadth 12 scores 76 vs 93 on two draws).

**TH-020 (second-order readiness).**
- **R7 has its first replicated positive** (T12, tier 2, a single rule, minimal margin).
- **R8 is untested.**
- **W5P stays design-only** (see Q6).

**TH-021 (instrument validity).**
- **Repaired and qualified:** the v2b apparatus (T01), tribunal v1a (0/330 admission flips), the distinctness screen,
  per-job selector isolation (T12 K2).
- **Failures that the instruments themselves caught:** T02 control, T05 UNSEEN floor, T07 oracle gate, T11 power,
  and the T09/T10 `selected_schema = None` conflation.
  - Each closed as labelled, never collapsed into NO.
- **Open:**
  - ruler v2.1 residual 8/47 plus a 24.5% chance floor;
  - T4 v1a is silent on queries 1-2;
  - no receipt check for no-donor-state;
  - r7e drops the selection table.

## 2. The seven close questions

**1. Which historical positives survived the repaired instruments?**
- A23 GENERIC capability (3/3).
- S4 YES, on 2 unseen + 2 related families.
- Endogenous derivation of the base class on natural supply (T51 / T06): when derived, it recovers 100% of the
  inherited benefit.
- The constructed-recurrence selection effect, re-read as shown-structure recovery (T52).

**2. What weakened or disappeared?**
- **A23's G1-SPECIFIC capability:** 5/10 under distinct-class accounting; shams match it.
- **The A20-A23 P/OFF_0 controls** could never score.
- **T51's derivation rate** did not confirm (0.644).
- **Midpoint 2's "R3 criterion is the limit" and T08's "breadth hurts"** were both draw-dependent / mis-attributed.
- **T09's and T10's mechanism readings:** corrected by erratum, with MEMORISE as the hidden winner.
- **G1 has no privileged status anywhere.**

**3. Was natural recurrence sufficient and visible?**
**Yes, for the base abstraction class:**
- W8 lineage supply recurs it;
- escrow 30k makes it visible;
- a pristine improver derives it.

But:
- composition beyond it is not supplied at a useful rate;
- reachable held-out families beyond PRISTINE are 23% on fresh seeds (g11: 60/256) and 26% on exposed seeds (123/480).

**Supply is not the binding limit. What the improver keeps is.**

**4. Did the current process ever change the improver rather than its library?**
**Yes, once, replicated at tier 2.**
- g11 is a content-free rule about which candidates may survive selection: non-generalising memorised libraries are
  excluded.
- It is applied by a pristine improver that carries no library.
- It raises reusable acquisition on unexposed natural supply: 20 -> 60 held-out families, 5/0/3, p = 0.031, which is
  the attainable minimum.
- The two other rule changes (the g10 subset criterion; OBSERVE breadth) are **inert on fresh seeds without it**.
- This is first-order R7. It is not R8 (the improved improver has not been shown to improve itself or later
  improvement), and it is not RSI.

**5. Where does the causal ladder currently stop?**
**At R8, untested.** Below it, on natural supply after g11, the residual limits are:
- **starvation:** seeds with no usable observations (T09 seed 12, T12 seed 16);
- **validation-to-transfer mismatch** between real abstractions (T11 seed 1).

**The deepest Beta-01 finding:** I_0's acceptance test cannot distinguish memorisation from abstraction on natural
supply. I_0 chooses memorisation in 4/8 fresh seeds.

**6. Is W5P / primitive promotion scientifically justified?**
**Not yet.**
- Representation has not been shown binding anywhere in Beta-01. Every limit located so far sits in the improver's
  SELECTION and OBSERVATION rules.
- W5P would add representation to an improver whose acceptance test was, until T12, choosing memorisation.
- **Prerequisites:**
  1. an independent, higher-powered replication of g11 (including g11 at O4);
  2. the R8 discriminator (does a g11-built library make the NEXT generation's acquisition better than I_0's?).
- If R8 shows the chain stalls on what the DSL can express, W5P becomes justified. Its design remains frozen-ready.

**7. Is Campaign 1 or another Tier-4 bridge worth future model spend?**
**A narrow bridge only, after replication.**
- The transferable prediction is concrete: improvers that accept library additions on aggregate validation savings
  will preferentially admit memorised solutions over abstractions when the supply is natural (lineage-recurrent).
  Excluding or penalising non-generalising entries should raise held-out reuse.
- That is cheap to test in an LLM skill-library setting (a Tier-4 bridge) and would discriminate.
- Broad Campaign-1 spend is not justified by tier-2 evidence with p at its attainable minimum.

## 3. Statement (the operator's target form)
"First-order compounding works when the improver keeps the abstractions it derives:
- On naturally generated lineage worlds, the base abstraction class recurs and is visible at escrow 30k.
- A pristine improver derives it from a handful of observations.
- With an acceptance rule that excludes non-generalising memorised libraries, about a quarter of held-out families
  (23-26%) become reachable beyond the pristine baseline. That is triple the historical improver on unexposed seeds.
- **The historical improver's chaining stopped at its ACCEPTANCE TEST (memorisation outranks abstraction), not at
  recurrence, visibility or representation.**
- With that repaired (R7, tier 2, replicated once), the ladder now stops at R8, which is untested."

## 4. Recommended next campaign items (not started; need authorisation where marked)
1. **Replicate g11** at higher power:
   - W8 regeneration of LIN 24+ seeds;
   - add g11 at O4;
   - ideally by another seat (independence).
2. **R8 discriminator:** a two-generation chain on LIN 16-23 with the start library from g11 vs I_0. Design first.
3. **Endpoint-aligned selection score:** a principled replacement for the type rule.
4. **Tier-4 bridge:** the memorisation-vs-abstraction acceptance test in an LLM skill library. **Needs operator
   authorisation; no model spend implied here.**
5. **W5P:** stays design-only until item 2 shows a representation limit.

## 5. Compute and process
- **Compute:** about 60 core-h over Beta-01 on M4/HARRY1, kept under the rolling 48 core-h/24h cap with one compute
  hold (T09).
- **Fabric output retrieval** stayed broken (#1404). All heavy work ran on M4 with 4 workers.
- **Technical events:** 1 (the T09 host memory-reaper kill; resumed cleanly).
- **Every window is closed and merged** with its report, receipts and STATE history.
