# COORDINATOR RESPONSE TO INDEPENDENT REVIEW v1 (reviews/INDEPENDENT_REVIEW_RESULTS_v1.md, 3ac85e783)

C-015, Aphrodite, 2026-10-10. No frozen label is changed by this response. Frozen-rule outputs stand as computed.
INTERPRETATIONS are corrected below. Commit timestamps are authoritative throughout.

## Verification by the coordinator
- **F2, re-checked independently:** the W483b8c31 f0 seed-0 R1 program `(add 2 (max (map (lam x (pow x 2)) xs)))`
  equals 2 + max(x^2) on 3,000 / 3,000 random lists, while the extracted stone `(pow x 2)` differs from the sealed
  `2 + x^2`.
- **F3:** the seed-1 / seed-2 unit tables already on main confirm it.

## Responses

| # | Severity | Response |
|---|---|---|
| F1 | verification | Accepted. Gap acknowledged: result files carry no wall-clock start / end. Future result files record start / end UTC. |
| F2 | BLOCKER | **ACCEPTED.** For 3 / 4 UD units the R1 world identifies f (the program is globally correct); the extraction rule mis-cuts the stone. The W03 claim "diverge only on the wider domain the composite uses" is WITHDRAWN as false. Only Wc025415a p0 is a genuine dev gap (no 5 in dev). |
| F3 | BLOCKER | **ACCEPTED.** The same R1 data yield sealed-equivalent stones under other keys; seed-0 "UNIQUE" is an artefact of the budget ending inside the size-8 class. |
| F4 | MAJOR | **ACCEPTED.** Dropping "or-HORIZON" stated the reading more strongly than its frozen definition. The pre-data prediction (about 4-7 / 15, horizon-driven) was right in count and essentially in mechanism. The label precedence (UD before horizon) is what kept the A3 OE trigger from firing. TFS1_INSTRUMENT_QUALIFIED = NO stands as the frozen-rule result. |
| F5 | MAJOR | **ACCEPTED.** Rendered henceforth as: "in this cell, on the 15 foundry-selected families, with the foundry's stones, 14 / 15 qualified at 1e6; about 4 sit in a partially covered size class (order-fragile)". It is not evidence that composition from correct stones is reachable in general. |
| F6 | MAJOR | Accepted; stated in the synthesis. |
| F7 | MAJOR | **ACCEPTED.** ID_RETENTION_REPAIR = NO is non-discriminating on the UD units (one class each within budget; RETAIN-4 = RETAIN-1). It is reported as uninformative, not as evidence against retention. |
| F8 | MAJOR | **ACCEPTED.** ID-A1.4 was written after the KP production stones were known to disagree with the sealed mechanisms. It is pre-data for E3-ID only, and its causal premise is falsified for 3 / 4 units. For those units the pre-amendment INSTRUMENT branch ("extraction or promotion step at fault") describes the data. The frozen ID-A1.4 counts stay as computed; their interpretation is superseded by this response. |
| F9 | MAJOR | **ACCEPTED.** PHASE3 proposal s4 is revised: the calibration case is re-attributed (extraction non-invariance + search horizon; the world dev-gap 1 / 4). IDENTIFIABILITY as a separate qualification question is kept as a proposal resting on the Wc025415a p0 case only. |
| F10 | MAJOR | **ACCEPTED.** Several ledger / freeze "utc" stamps were estimates up to about 51 min ahead of their commits (e.g. FREEZE_E3KP says 18:05Z vs a KP result commit at 17:49Z; the commit order is correct). Frozen files are NOT edited. A ledger correction entry is appended. From now on ledger utc is taken from `date -u` at write time. |
| F11 | MINOR | Accepted; listed in the synthesis limitations. No fresh tribunal for E3-KP is stated as a limit. |
| F12 | MINOR | The frozen vocabulary is kept (INCONCLUSIVE_CENSORED). The synthesis states the cause as "descriptor qualification failed on 10 / 15 families (instrument unvalidated)". |
| F13 | MINOR | Accepted. |
| F14 | verification | Accepted. Worker overlap is reported from the record as is. |

## Interpretation now held by the coordinator (replacing the W03 reading)
The **first demonstrated failure** in the causal chain is **stepping-stone ACQUISITION** under enumerative base search
with first-dev-consistent commitment. Three components, ranked by evidence:
1. **Search horizon:** an in-class enumeration lottery at 1e6, which covers about 7% of the size-8 class.
2. **Extraction non-invariance:** developmental machinery; 3 / 4 UD units.
3. **World dev-gap:** 1 / 4 units.

E1's shortfall shares the same link (foundry CHAIN_C_FAIL).

## Disagreements preserved
1. **The WORLD / RULER reading is withdrawn as the first failure.** The coordinator keeps a minority note: the sealed
   decomposition is a ruler convention, and R1 families that admit reducer-commuting refactorings leave the mechanism
   boundary non-canonical. This is held as an item for foundry design, not as the first demonstrated failure.
2. **MIGRATE vs CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY** stays open until AR-1 production and any post-review
   experiment are in.
