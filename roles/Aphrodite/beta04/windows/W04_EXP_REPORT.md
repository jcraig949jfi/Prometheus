# W04 (EXP) REPORT: E2 COMPLETE, AR-1 COMPLETE, TWO INDEPENDENT REVIEWS, E3-R FROZEN

C-015, 2026-10-10 21:27Z to 2026-10-11 01:27Z. The report was committed at about 01:05Z.

## E2 (FREEZE_E2; A1 + A2) -- REACHABILITY_ATLAS_COMPLETE = YES
- **Coverage:** atlas 53 / 53; 1x screen 720 / 720 shards; prelaunch PASS. The analyzer re-derived 1,468 programs with
  0 mismatches. Review v2 re-derived 30 sampled shards independently and found them in agreement; its recount of all
  720 shards matched.
- **Screen.** Library = the foundry-acquired stones of each family's constituents (oracle decomposition supplied),
  on the 15 foundry-selected R3 / R4 families, at B = 2e5, 8 seeds.

  | Arm | Primary hits / 120 |
  |---|---|
  | chain_neutral | 80 |
  | credit_blind | 68 |
  | chain_strict | 44 |
  | desert_ref (no library) | **0** |

- **Headline labels:**
  - REACHED 13 (>= 1 / 8 seeds). Only 10 / 15 are robust at >= 6 / 8. F033 and W483b8c31-F046 are reached at 1 / 8.
  - DESERT_OR_HORIZON 2 (both fs:post_fold).
  - Co-labels (analyzer flags = coordinator derivation): CREDIT_GRADIENT 4, CREDIT_MISLEADING 1. This is screening;
    about 3 such families are expected by chance.
  - Descriptive: credit speeds hitting by 1-2 orders of magnitude in charges on several families.
- **FRONTIER_ARCHIVE_EFFECT = INCONCLUSIVE (INCONCLUSIVE_CENSORED)**, fixed pre-outcome.
  - Descriptor unvalidated on 10 / 15 families.
  - On the 5 qualified families: X3 17 / 40, X3G 25 / 40, chain_neutral 27 / 40. The direction is negative for the
    archive arm in both informative clusters (descriptive).
- **4x escalation NOT run** (declared deviation; windows/FINAL_LABEL_RULES.md): budget cannot resolve descriptor
  censoring, and no treatment qualified.

## AR-1 alien reserve (FREEZE_ALIEN_AR1; exploratory)
- 0 / 15 chain-qualified; scratch fails 15 / 15.
- First failing links: HORIZON_R1 12, UNDERDETERMINED_STONE 3. AR-1 acquires 1 / 17 units vs TFS-1's 14 / 17.
- **Caveats:**
  - Confounded: representation AND search both differ from TFS-1.
  - Composition is untested: there is no given-stones row.
  - It bears only weakly on MIGRATE.
  - It reproduces the Wc025415a p0 dev gap in a second representation.

## Independent review v1 (results) and v2 (addendum)
**v1** (3ac85e783).
- The four headline labels are supported.
- BLOCKERS F2 / F3 against the coordinator's E3-ID reading were ACCEPTED (reviews/COORDINATOR_RESPONSE_REVIEW_v1.md):
  - 3 / 4 "underdetermined" stones are extraction mis-cuts of globally correct R1 programs;
  - seeds 1 / 2 acquire all 4;
  - the world dev-gap is 1 / 4.
- The first failure is now held to be **stepping-stone ACQUISITION** (search horizon + extraction non-invariance).
- The "world / ruler" reading was withdrawn. A W03 erratum and comms correction #2107 were issued.

**v2** (7e7109663).
- E2 and AR-1 custody and labels were verified.
- Recommended values for all 8 final fields; the recommendation CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY is
  strengthened.
- Process MAJOR: four final fields had no frozen definition. Fixed by **windows/FINAL_LABEL_RULES.md (Rule G)**, written
  before the synthesis with all outcomes disclosed as known: gated fields = INSTRUMENT_UNVALIDATED.
- Ledger corrections were appended for:
  - the analyzer co-labels;
  - the "composition reachable" wording;
  - the 4x reason;
  - the AR-1 qualifier.

## E3-R (NEW prereg: repair-class discrimination, OE x X-ABS)
- **Process:** draft -> red team (reviews/REDTEAM_E3R_PREFREEZE.md: 2 BLOCKER / 7 MAJOR; FREEZE_WITH_AMENDMENTS) ->
  E3R-A1 (adopted in full) -> E3R-A2 (review v2) -> code (40fdf5eab; E3 tests 28 / 28) -> E3R-A3 (text = code) ->
  **FREEZE_E3R** (8efd1ae71, 00:01Z).
- **Development pilot:** BOTH_REQUIRED (MAJORITY; seed 0 alone read SEARCH).
- **Launcher:** queued for 2026-10-11T11:30Z, rolling-cap timing, 2 workers, envelope 14 core-h.
- **Scope:** it discriminates repair class WITHIN TFS-1 only. It cannot relabel anything, and it cannot decide
  CHANGE vs MIGRATE.

## Compute (measured from result files, unique searches only)
- E2 10.4 core-h (projection 14.3);
- E3-KP all rows 2.3;
- AR-1 2.5;
- leads and reviews: about 1-3 each (estimates).

The rolling total remains under the 48 core-h cap. At most 4 workers ran concurrently.

## Next (W05-W07)
1. No experiment compute until E3-R at 11:30Z.
2. Drafts: SYNTHESIS, ARTIFACT_MANIFEST, COMPUTE_REPORT, final PHASE3 proposal.
