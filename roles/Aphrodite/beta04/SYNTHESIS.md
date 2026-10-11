# BETA-04 SYNTHESIS: ESCAPING THE COMPOSITION DESERT (C-015) -- DRAFT (E3-R pending)

Status: DRAFT, written in W05 before E3-R ran. The sections marked [PENDING E3-R] are completed after E3-R. Nothing
in this draft relabels a frozen result.

**Ground rules.**
- Every label below is the output of a frozen rule. Interpretations are marked as such.
- Disagreements are preserved, not resolved by narrative.

**Sources:** LEDGER.json, CAMPAIGN_STATE.json, windows/W01-W04 reports, reviews/*.md, FREEZE_*.json,
windows/FINAL_LABEL_RULES.md.

## 1. Final labels

| Field | Value | Frozen basis | Rendering / limits |
|---|---|---|---|
| WORLD_DEMAND_QUALIFIED | **NO** | E1_ADDENDUM_D (strict) | 5 / 12 secret production worlds pass the per-world gate; 2 mechanism-kind pairings < 3. 15 R3 / R4 families admitted, demand-genuine (hindsight regression 0 / 53; from-scratch 0 at 1e6). R5 = 0 |
| REACHABILITY_ATLAS_COMPLETE | **YES** | A1-B.9 | Atlas of the COMPOSITION step given supplied foundry stones on foundry-selected families: 53 / 53 atlas; 720 / 720 screen; prelaunch PASS; re-derivation 0 mismatches |
| TFS1_INSTRUMENT_QUALIFIED | **NO**, so **TFS1_REACHABILITY_INSTRUMENT = FAIL** | A1-A, A3 | Primary 7 / 15 (bar 12); scratch fails 15 / 15. Not a scientific rejection of compositional learning |
| FRONTIER_ARCHIVE_EFFECT | **INCONCLUSIVE** (INCONCLUSIVE_CENSORED) | A1-B.6, A2.3 | Fixed before any outcome: descriptor unvalidated on 10 / 15 families (2 / 5 clusters informative). Direction in both informative clusters: archive arm below both comparators (descriptive) |
| COMPOSITIONAL_DISCOVERY | **INSTRUMENT_UNVALIDATED** | Rule G | E3 2x2 lifetime screen gated off (KP NO) |
| DEVELOPMENTAL_INHERITANCE | **INSTRUMENT_UNVALIDATED** | Rule G | E4 barred (E1 NO; E3 not passed) |
| SECOND_ORDER_ACQUISITION | **INSTRUMENT_UNVALIDATED** | Rule G | Gated with E3 / E4 |
| ECONOMIC_ADVANTAGE | **INSTRUMENT_UNVALIDATED** | Rule G | No qualified treatment to scale; the E2 4x was skipped as a declared deviation |

## 2. The causal chain and the first demonstrated failure

| Link | Evidence | Status |
|---|---|---|
| World demand (Q1) | E1 production: genuine demand on 15 families but only 2 pairings and 5 / 12 worlds; the dominant loss is CHAIN_C_FAIL (foundry base search cannot acquire R1 stones) | NOT QUALIFIED. Its shortfall has the SAME root as the link below |
| **Stone acquisition** | E3-KP primary 7 / 15. First-failing links as labelled: UD 7, HORIZON_R1 1. Re-attributed by review v1 (accepted): 3 / 4 UD units are extraction mis-cuts of globally correct R1 programs; seeds 1 / 2 acquire all 4 (order lottery, 1e6 covers about 7% of the size-8 class); 1 / 4 is a genuine world dev-gap (Wc025415a p0). Seed rows 9 / 15, 8 / 15. Fallback-off 0 / 15 | **FIRST DEMONSTRATED FAILURE** |
| Composition given stones | E3-KP given-foundry-stones 14 / 15 (enumeration; about 4 order-fragile). E2 mutation chain REACHED 13 / 15 (>= 1 / 8 seeds; 10 / 15 robust at >= 6 / 8). Desert reference without stones 0 / 120 | Not shown to fail, on the foundry-selected set. Stones open the desert in this cell |
| Credit | E2: chain_neutral 80, credit_blind 68, chain_strict 44 hits / 120. Co-labels CREDIT_GRADIENT 4 / MISLEADING 1 (screening noise in count). Credit gives a 1-2 orders-of-magnitude charge speed-up on several families (descriptive) | No label-level effect |
| Frontier archive | Censored by descriptor qualification; descriptive direction negative | INCONCLUSIVE |
| Development / inheritance / second order | Gated | INSTRUMENT_UNVALIDATED |

**First demonstrated failure: stepping-stone ACQUISITION by enumerative base search with first-dev-consistent
commitment.** Components, ranked by evidence:
1. **Search horizon:** a within-class order lottery at 1e6.
2. **Extraction non-invariance:** a developmental-machinery defect; 3 / 4 UD units.
3. **World dev-gap:** 1 / 4.

[PENDING E3-R: which repair class (OE search pruning, refactoring-invariant extraction, or both) removes it at
>= 12 / 15, with seed stability and the per-family attribution table.]

## 3. Answers to the five research questions (bounded to their cells)
- **Q1 COGNITIVE DEMAND.**
  - Partly. Tasks were built where constant / lookup / reactive / history / fixed-library / small-search / regression
    nulls fail and certified witnesses succeed (15 R3 / R4 families, demand-genuine).
  - BUT the frozen world-level qualification failed on breadth (5 / 12 worlds, 2 pairings), for the same acquisition
    reason.
- **Q2 REACHABILITY.**
  - With supplied stones, stochastic and enumerative search cross the composition step (13 / 15, 14 / 15), and
    without stones neither does (0 / 120; scratch 0 / 15).
  - Whether a certificate-qualified ARCHIVE of stepping stones beats ordinary search is untested: the descriptor
    did not qualify (censored). Descriptively, the archive arm was not better.
- **Q3 COMPOSITION.**
  - Not demonstrated for LEARNED mechanisms. The organism's own stone acquisition is the first failure.
  - Composition from given correct stones succeeds on the selected set. That is a precondition, not Q3.
- **Q4 DEVELOPMENT.** Untested (gated): INSTRUMENT_UNVALIDATED.
- **Q5 ECONOMICS.** Untested (no qualified treatment): INSTRUMENT_UNVALIDATED. Full compute report in
  COMPUTE_REPORT.json.

## 4. Exploratory: alien representation (AR-1)
- AR-1 is a stack-tape machine with a mutation chain. Primary row: 0 / 15; links HORIZON_R1 12, UD 3. It acquires
  1 / 17 units vs TFS-1's 14 / 17.
- **Caveats:**
  - Confounded: representation and search both differ.
  - Composition is untested (no definable given-stones row).
  - It bears only weakly on MIGRATE.
- **What it adds:** the Wc025415a p0 dev-gap reproduces in a second representation. And it proposed mechanisms the
  lambda grammar would not, e.g. a comparison-free predicate.

## 5. Recommendation [PENDING E3-R]
- **Provisional (the reviewer's and the coordinator's current reading): CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY.**
  - Keep the TFS-1 representation.
  - Change stone acquisition: the search horizon (OE pruning or wider in-class coverage, multi-key restarts) and
    refactoring-invariant extraction.
- **Excluded:**
  - CONTINUE_TFS1 as is: the frozen gate (E3 FAIL stops the line).
  - MIGRATE as the primary: no candidate has shown a definable given-stones row or better acquisition; AR-1 acquires
    less.

## 6. Disagreements preserved
1. **World / ruler as the first failure** (the coordinator's withdrawn W03 reading) vs ACQUISITION (review v1;
   accepted).
   - Minority note kept: the sealed decomposition is a ruler convention, and R1 families admitting reducer-commuting
     refactorings leave the mechanism boundary non-canonical.
   - It is a foundry-design item, not the first demonstrated failure.
2. **MIGRATE vs CHANGE.**
   - Counter-case (review v1 s4): the extraction failure is intrinsic to "mechanism = syntactic lambda subterm", and
     successes needed a motif-specific readout fallback.
   - Rebuttal: a behavioural extraction inside TFS-1 removes it in the tested cases, and the binding residual is
     search horizon.
3. **The ID-A1.4 amendment.** Coordinator: a pre-data clarification. Reviewer: written with the KP production stones
   in view; its causal premise is falsified for 3 / 4 units. The interpretation is superseded; the counts stand.
4. **"Composition reachable."** Shown only on the foundry-selected families with foundry stones (selection-
   conditioned, review v1 F5). The E2 mutation chain shows the guard_p order-fragility belonged to the enumeration
   instrument (review v2 E2-3).

## 7. Claim limits
- All results are restricted to the motif-limited admitted set: 2 kind pairings, 5 merged skeletons, 7 worlds.
- Every label is conditional on the readout fallback (fallback-off 0 / 15).
- No significance is inferred from screens (8 seeds).
- No fresh tribunal was used for E3-KP (red-team F11).
- No "RSI"; no recursive claims.
- Process defects (ledger):
  - one lead killed a sibling's run;
  - a transient over-worker episode;
  - ledger / freeze utc stamps running up to 51 min ahead of their commits (corrected; commit times authoritative).

## 8. Deliverables
| Deliverable | Location |
|---|---|
| Artifact manifest | ARTIFACT_MANIFEST.json (git blobs; regenerated at close) |
| Compute | COMPUTE_REPORT.json |
| Receipts | FREEZE_*.json; result files under runs/, foundry/production/, alien/runs/production/ |
| Independent review | reviews/INDEPENDENT_REVIEW_RESULTS_v1.md, _v2_ADDENDUM.md and the coordinator response |
| Pre-freeze red teams | reviews/REDTEAM_*.md |
| Phase-3 interface | PHASE3_WIND_TUNNEL_INTERFACE.md |
