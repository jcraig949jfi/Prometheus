# BETA-04 SYNTHESIS: ESCAPING THE COMPOSITION DESERT (C-015) -- FINAL

C-015, Aphrodite (M4 / harry1). Campaign window 2026-10-10 09:27Z to 2026-10-11, inside the 72 h ceiling (hard stop
2026-10-13 09:27Z). Evidence tier 2, CPU only, $0 cloud, no live models, no Campaign 1, no third generation.

**Ground rules.**
- Every label below is the output of a frozen rule; none was relabelled after its data.
- Interpretations are marked as such. Disagreements are preserved, not resolved by narrative.

**Sources:**
- records: LEDGER.json, CAMPAIGN_STATE.json, windows/W01-W08 reports, FREEZE_*.json, windows/FINAL_LABEL_RULES.md;
- reviews/: independent review v1, v2 and v3, the coordinator responses, and three pre-freeze red teams;
- operator guidance: prompts/2026-10-10_beta04/02_OPERATOR_GUIDANCE_2026-10-11_verbatim.md.

## 1. Final labels

| Field | Value | Frozen basis | Rendering / limits |
|---|---|---|---|
| WORLD_DEMAND_QUALIFIED | **NO** | E1_ADDENDUM_D (strict) | 5 / 12 secret production worlds pass the per-world gate; 2 kind pairings < 3. 15 R3 / R4 families admitted, demand-genuine (hindsight regression 0 / 53; from-scratch 0 at 1e6). R5 = 0 |
| REACHABILITY_ATLAS_COMPLETE | **YES** | A1-B.9 | An atlas of the COMPOSITION step given supplied foundry stones on foundry-selected families: 53 / 53 atlas; 720 / 720 screen; prelaunch PASS; analyzer re-derivation 0 mismatches; independent re-derivation of 30 shards agrees |
| TFS1_INSTRUMENT_QUALIFIED | **NO**, so **TFS1_REACHABILITY_INSTRUMENT = FAIL** | A1-A, A3 | Primary 7 / 15 (bar 12); scratch fails 15 / 15. The A3 OE trigger did not fire (label precedence UD before horizon). Not a scientific rejection of compositional learning. E3-R does NOT relabel this |
| FRONTIER_ARCHIVE_EFFECT | **INCONCLUSIVE** (INCONCLUSIVE_CENSORED) | A1-B.6, A2.3 | Fixed before any outcome: descriptor unvalidated on 10 / 15 families (2 / 5 clusters informative). Descriptive direction in both informative clusters: the archive arm is below both comparators (X3 17 / 40, X3G 25 / 40, neutral 27 / 40) |
| COMPOSITIONAL_DISCOVERY | **INSTRUMENT_UNVALIDATED** | FINAL_LABEL_RULES Rule G | The E3 2x2 lifetime screen is gated off (KP NO). E3-R passing is NOT compositional discovery (decomposition supplied) |
| DEVELOPMENTAL_INHERITANCE | **INSTRUMENT_UNVALIDATED** | Rule G | E4 barred (E1 NO; E3 not passed) |
| SECOND_ORDER_ACQUISITION | **INSTRUMENT_UNVALIDATED** | Rule G | Gated with E3 / E4 |
| ECONOMIC_ADVANTAGE | **INSTRUMENT_UNVALIDATED** | Rule G | No qualified treatment to scale; the E2 4x skip is a declared deviation |

## 2. The causal chain and the first demonstrated failure

| Link | Evidence | Status |
|---|---|---|
| World demand (Q1) | E1: genuine demand on 15 families, but breadth fails (5 / 12 worlds, 2 pairings). Dominant loss: CHAIN_C_FAIL (the foundry's own base search cannot acquire R1 stones) | NOT QUALIFIED; shares its root with the next link |
| **Stone acquisition** | E3-KP primary 7 / 15 (seed rows 9 / 15, 8 / 15). Review v1 (accepted): 3 / 4 UD units are extraction mis-cuts of globally correct R1 programs; seeds 1 / 2 acquire all 4; 1 / 4 is a world dev-gap (Wc025415a p0: no 5 in dev). Fallback-off 0 / 15. AR-1 (alien) acquires 1 / 17 units | **FIRST DEMONSTRATED FAILURE** |
| Repair of acquisition (E3-R) | REPAIR_CLASS = SEARCH (MAJORITY; seed labels SEARCH / BOTH_REQUIRED / SEARCH; unconditional). OE main effect +5.5 / +2.5 / +4.5 vs X-ABS +2.5 / +1.5 / +0.5; interaction +1 at every seed; no X-ABS-only rescue | Pruning is dominant and necessary; seed-robust qualification needed BOTH (see s3) |
| Composition given stones | E3-KP given-foundry-stones 14 / 15 (enumeration; about 4 order-fragile). E2 mutation chain REACHED 13 / 15 (>= 1 / 8; 10 / 15 robust at >= 6 / 8). No-stone desert reference 0 / 120 | Not shown to fail on the foundry-selected set. Supplied stones open the desert in this cell |
| Credit | E2 hits / 120: chain_neutral 80, credit_blind 68, chain_strict 44. Co-labels CREDIT_GRADIENT 4 / MISLEADING 1 (screening noise in count). Descriptive 1-2 orders-of-magnitude charge speed-up on several families | No label-level effect |
| Frontier archive | Censored by descriptor qualification; descriptive direction negative | INCONCLUSIVE |
| Development / inheritance / second order | Gated | INSTRUMENT_UNVALIDATED |

**First demonstrated failure: stepping-stone ACQUISITION** by enumerative base search with first-dev-consistent
commitment. Components, ranked:
1. **Search coverage of the stone's size class:** 1e6 covers about 7% of the size-8 class. E3-R confirms pruning as
   the dominant repair. Part of OE's gain is coverage; part is a reshuffle of which variant comes first (review v3
   R3-1).
2. **Extraction non-invariance:** a developmental-machinery defect; 3 / 4 UD units in E3-KP.
3. **World dev-gap:** 1 / 4 units. It is the residual failure in the best E3-R cell.

## 3. E3-R: repair-class discrimination (new prereg; FREEZE_E3R; ran 2026-10-11 11:30-13:33Z)
Chain-qualified / 15 (OE x extraction), seed 0 / 1 / 2:

| Cell | Seed 0 | Seed 1 | Seed 2 |
|---|---|---|---|
| OE off, frozen extraction | 7 | 9 | 8 |
| OE off, X-ABS | 9 | 10 | 8 |
| OE on, frozen extraction | **12** | 11 | **12** |
| OE on, X-ABS | **15** | **13** | **13** |

**Custody and checks.**
- Reproduction: off_frozen = the frozen E3-KP result (7); off_xabs = 9 (the reviewer's estimate reproduced).
- 0 censored scratch searches; UTC on every new search.
- Review v3 re-derived every cell, the labels and the attribution tables exactly, and spot-checked 4 qualified OE-cell
  families independently.

**What it licenses** (review v3, accepted):
1. **Frozen label:** REPAIR_CLASS = SEARCH (MAJORITY). OE pruning alone sits exactly at the 12 / 15 bar on seeds 0
   and 2 and at 11 on seed 1, so one family separates SEARCH from BOTH_REQUIRED.
2. **The SEARCH margin rests partly on lottery outcomes.**
   - At seed 0, 2 of OE's 5 rescues (Wc025415a-F041 / F044) only reorder the ambiguous x > 4 / x > 5 variant, with
     the certifier-guided retry doing the rest. Both are lost at seeds 1 and 2.
   - Two other seed-0 rescues still carry the mis-cut stones; the chain absorbed the missing part late in budget.
   - Only W483b8c31-F046 is clearly a horizon cure by coverage.
3. **The only configuration at or above the bar at every seed is OE + X-ABS** (15 / 13 / 13). Its residual failures
   are the Wc025415a world dev-gap.
4. **Every cell relies on the foundry-derived readout fallback.** Fallback-off with both repairs gives 9 / 15. The
   frozen fallback "agreement" check cannot detect anything for a SEARCH label; it is NOT robustness evidence.
5. **X-ABS is a post-hoc, in-sample, single-motif patch** (the hoisted reducer). It needs confirmation on fresh,
   independently generated families.
6. **E3-R relabels nothing, opens no E3 gate, is not compositional discovery, and cannot decide CHANGE vs MIGRATE.**
   Never write "TFS-1 would have qualified".

## 4. Acquisition / utilization / autonomy (operator guidance 2026-10-11)

| Measurement | Question | Beta-04 evidence | Reading |
|---|---|---|---|
| **ACQUISITION** | Did the learner independently discover the reusable component? | Only with the decomposition SUPPLIED (R1 tasks indexed by the sealed decomposition; certifier-guided R1 retry). TFS-1 base search: 7 / 15 chains with correct-enough stones at 1e6 (9 / 8 at other seeds); 3 globally correct programs mis-cut; 1 dev-gap. With OE + X-ABS: 15 / 13 / 13. Without a supplied decomposition: **not tested** | Acquisition-given-decomposition is repairable at 1e6 with search + extraction changes. Autonomous acquisition (deciding WHAT to learn) is untested: the Beta-05 question |
| **UTILIZATION** | Could the learner solve something new using that component? | Given correct (foundry) stones: enumeration 14 / 15; mutation chain 13 / 15 (>= 1 / 8 seeds); without stones 0 / 120 and scratch 0 / 15 | Yes, on the foundry-selected families: stones are necessary in this cell and make the composite reachable. Selection-conditioned (review v1 F5) |
| **AUTONOMY** | How much of each success was the learner vs search infrastructure vs developmental machinery vs certifier? | **World / ruler:** supplied the decomposition and the R1 curriculum. **Certifier:** R1 retry selection and final test + tribunal judgement; 2 OE rescues depended on the certifier-guided retry after a reorder. **Developmental machinery:** the readout fallback is required (fallback-off 0 / 15; 9 / 15 with both repairs), and X-ABS fixed 3 stones. **Search infrastructure:** OE pruning is the dominant repair. Archive and credit give no label-level benefit. **The learner proper:** blind search over candidates inside that scaffold | Low autonomy. Most of what made success possible was supplied (decomposition, fallback, certifier) or is infrastructure (OE). Hestia's triviality concern stands for any "discovery" reading |

## 5. Answers to the five research questions (bounded to their cells)
- **Q1 COGNITIVE DEMAND.**
  - Partly. Tasks were built where constant / lookup / reactive / history / fixed-library / small-search /
    regression nulls fail and certified witnesses succeed (15 families).
  - World-level qualification failed on breadth, for the same acquisition reason.
- **Q2 REACHABILITY.**
  - With supplied stones, search crosses the composition step (13-15 / 15); without them nothing crosses (0 / 120;
    0 / 15).
  - Whether a certificate-qualified archive beats ordinary search is untested (descriptor censored). Descriptively
    the archive arm was not better.
- **Q3 COMPOSITION.**
  - Not demonstrated for LEARNED mechanisms acquired autonomously.
  - Given a supplied decomposition, repaired acquisition (OE + X-ABS) plus composition qualifies 13-15 / 15. That is
    a precondition, not Q3.
- **Q4 DEVELOPMENT.** Untested (gated).
- **Q5 ECONOMICS.**
  - Untested (no qualified treatment).
  - Compute for the whole campaign: 36.4 core-h (18.4 measured + 18.0 reported); COMPUTE_REPORT.json.
  - OE pruning costs are on an INFRA ledger, not yet accounted in an economics comparison.

## 6. Exploratory: alien representation AR-1
- AR-1 is a stack-tape machine with a mutation chain. Primary row 0 / 15; links HORIZON_R1 12, UD 3. It acquires
  1 / 17 units vs TFS-1's 14 / 17.
- **Caveats:**
  - Confounded: representation and search both differ.
  - Composition is untested (no definable given-stones row).
  - It bears only weakly on MIGRATE.
- **What it adds:** the Wc025415a p0 dev-gap reproduces in a second representation.
- **Not claimed:** the pilot found tapes such as a comparison-free predicate, but whether TFS-1 could express them
  within its budget was not checked (review v3).

## 7. Recommendation
**CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.** Keep the TFS-1 representation.

- **First demonstrated failure: stepping-stone ACQUISITION.** Search coverage of the stone's size class, plus an
  extraction rule that is not invariant to semantics-preserving refactorings; a world dev-gap in 1 / 4 units.
- **The frozen E3-R repair class is SEARCH** (majority 2 / 3; at the 12 / 15 bar on seeds 0 and 2, 11 / 15 on
  seed 1). Pre-registered OE pruning is the dominant and necessary factor: there are no X-ABS-only rescues.
- **Seed-robust qualification needed pruning PLUS refactoring-invariant extraction** (15 / 13 / 13, a positive
  interaction at every seed). Every cell relies on the readout fallback (fallback-off with both repairs: 9 / 15). The
  residual failure is a world dev-gap.
- **Under the operator's direction map,** the evidence fits the "both interventions work" branch better than "search
  pruning alone".
  - Search geometry and reachability lead.
  - A generalized, target-blind extraction is a co-requirement. It is developmental machinery, not representation
    complexity.
- **Next (Beta-05 design inputs):**
  1. stone DISCOVERY without a supplied decomposition (not R8);
  2. on fresh, independently generated families;
  3. with improved search (OE or equivalent coverage gains) and a generalized extraction validated out of sample;
  4. fallback-disabled controls;
  5. pruning costs accounted;
  6. an R1 identifiability check on dev sets (boundary inputs present).
- **Excluded:**
  - CONTINUE_TFS1 as is: the frozen gate (E3-KP FAIL).
  - MIGRATE as primary: no alternative has shown better acquisition or a definable given-stones row; AR-1 acquires
    less.

## 8. Disagreements preserved
1. **First failure: world / ruler** (the coordinator's withdrawn W03 reading) vs **ACQUISITION** (review v1;
   accepted).
   - Minority note: the sealed decomposition is a ruler convention, and R1 families admitting reducer-commuting
     refactorings leave the stone boundary non-canonical.
   - This is a foundry-design item.
2. **MIGRATE vs CHANGE.**
   - Counter-case (review v1 s4): extraction failure is intrinsic to "mechanism = syntactic lambda subterm", and every
     success needs the readout fallback.
   - Rebuttal: a behavioural extraction inside TFS-1 removes the mis-cuts; OE is the dominant repair. It stays open
     for out-of-sample extraction.
3. **SEARCH vs BOTH.**
   - The frozen label says SEARCH.
   - The reviewer (v3) and coordinator recommendation lead with SEARCH but name BOTH, because the SEARCH margin is one
     family and partly lottery.
   - The frozen label stands.
4. **ID-A1.4.** Written with the KP production stones in view; its causal premise is falsified for 3 / 4 units. The
   interpretation is superseded; the counts stand.
5. **"Composition reachable."** Shown only on foundry-selected families with foundry stones (selection-conditioned).

## 9. Claim limits and process record
- **Scope:** all results are restricted to the motif-limited admitted set (2 kind pairings, 5 merged skeletons,
  7 worlds), with oracle decomposition and certifier-guided R1 retry.
- **Fallback:** every positive is conditional on the readout fallback.
- **Statistics:** no significance is inferred from screens (8 seeds) or from E3-R (3 seeds).
- **Tribunal:** no fresh tribunal for E3-KP / E3-R (same test + tribunal as foundry admission).
- **Language:** no "RSI"; no recursive claims.
- **Process defects (ledger):**
  - a lead killed a sibling's run;
  - transient over-worker episodes;
  - ledger / freeze utc stamps ran up to 51 min ahead of their commits (corrected; commit times authoritative);
  - the coordinator posted an over-read interpretation (#2096) before independent review (corrected in #2107).

## 10. Deliverables

| Deliverable | Location |
|---|---|
| Artifact manifest | ARTIFACT_MANIFEST.json (git blobs; regenerated at close) |
| Compute | COMPUTE_REPORT.json |
| Receipts | FREEZE_E2, FREEZE_E3KP, FREEZE_E3ID, FREEZE_ALIEN_AR1, FREEZE_E3R (git blobs); result files under runs/, foundry/production/, alien/runs/production/ |
| Independent review | reviews/INDEPENDENT_REVIEW_RESULTS_v1.md, _v2_ADDENDUM.md, _v3_E3R.md; reviews/COORDINATOR_RESPONSE_REVIEW_v1.md |
| Pre-freeze red teams | reviews/REDTEAM_FOUNDRY_PREFREEZE.md, REDTEAM_E2_E3KP_PREFREEZE.md, REDTEAM_E3R_PREFREEZE.md |
| Phase-3 interface | PHASE3_WIND_TUNNEL_INTERFACE.md |
