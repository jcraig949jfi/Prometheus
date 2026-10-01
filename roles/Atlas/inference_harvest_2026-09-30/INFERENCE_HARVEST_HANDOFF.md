# INFERENCE_HARVEST_HANDOFF -- Atlas, 2026-09-30

Atlas[m1-a5680f90] (claude-opus-5-5[1m]), M1 / SKULLPORT. The operator's inference-harvest directive (verbatim:
roles/Atlas/prompts/2026-09-30_inference_harvest/01_OPERATOR_DIRECTIVE_verbatim.md, sha256 b2b7ad26) unparked Atlas
for inference-only work until 2026-10-01 05:00 America/New_York. After that Atlas returns to READY.

## 1. What was delivered (all in roles/Atlas/inference_harvest_2026-09-30/)

| file | what it is |
|---|---|
| ATLAS_CROSS_ENGINE_SYNTHESIS_2026-09-30.md | The answer. Eight reconciled findings F1-F8; synthesist vs critic vs Atlas reconciliation table; evidence tables; the reconciled program-level epistemic map; coverage gaps |
| ATLAS_CONTRADICTIONS_AND_NATURAL_EXPERIMENTS.md | 16 contradictions (each classified by source and given a smallest separating test) and 11 natural experiments; Atlas triage of the 8 cheapest decisive tests; verifier corrections |
| ATLAS_ONTOLOGY_GAPS_VNEXT.md | Attack on Atlas's own 20-primitive inventory. The combination index is null by construction. 4 of 5 UNMEASURED primitives are instrumentation gaps. Aliases, missing primitives (initialization_regime, encoding_accessibility, use_coupling, executor_referent), ruler-side fields, and a hand-built intervention matrix |
| ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md | About 50 observations kept apart from the interpretations that buried them, ranked, and marked NEW or catalogued against Tyche's residual catalogue |
| ATLAS_OPERATOR_FRONTIER.md | 12 candidate directions and 5 deliberately alien proposals, each with evidence, falsifier and cost. Operator-facing; NOT a queue; nothing was sent to any seat |
| INFERENCE_HARVEST_HANDOFF.md | this file |
| workers/ | Full provenance: the READER_BRIEF, 7 digests plus 2 part files, REGULARITIES, ARTIFACT_MAP, ATTACK_ON_REGULARITIES, CONTRADICTIONS_NATEXP, two verifier tables, and the cross-family packet and responses |

## 2. The findings in eight lines (reconciled; ATLAS_DERIVED; scopes in SYNTHESIS s1)

1. **F1 (STRONG, program-level).** Absence verdicts and law claims are bounded by instrument validity:
   - 37/94 absence gates were never shown to fire;
   - at least 10 rulers across 8 substrates could not return the opposite outcome;
   - no positive law has beaten a trivial, restated or known baseline.
   The main deflation tool (zero-parameter restatement) has never been given a chance to fail (FR-3).
2. **F2 (STRONG within the Z80 design family; WEAK across).** The world supplies reproduction: a short copy
   primitive plus zero-register addressing. These are probably one addressing dependence. The cross-family test is
   FR-1.
3. **F3 (MODERATE-STRONG, 2 lineages).** Copying and persistence dissociate from task competence (transplants 39/39
   persist, 0/39 competent; incompetent imports take over 12/12). This may be designed in (FR-6).
4. **F4 (SUGGESTIVE-MODERATE, a reconciled finding).** Nominal mutation rate is a minor share of effective
   variation in the byte worlds. Write-back, splice and world-made copies dominate (FR-5).
5. **F5 (SUGGESTIVE).** Answer-before-read. Verification showed it is one seat's citation chain, not independent.
6. **F6 (SUGGESTIVE).** Present or decodable state is not what drives output. One instrument class; no denominator
   (FR-10). The CW01 instance was withdrawn after verification.
7. **F7 (MODERATE, program-level).** Mechanism labels turn over in days. Replayed counts hold; independently
   re-measured counts often move several-fold.
8. **F8 (MODERATE for length; UNTESTED for cliff).** Count-fixed rulers manufacture "length protects" on the Proteus
   VM. The "cliff" that PROTEUS-46 and the frontier suppression rest on has never been re-read (FR-2).

**Meta-finding.** After two claim verifiers, NO cross-engine convergence in the record qualifies as independent
and vocabulary-blind. Every candidate traced to one of: a shared ruler, one design family, a citation chain, a
single-originator comms term, or one model family. The program currently has no mechanism that produces
independent confirmation (SYNTHESIS s4).

## 3. How it was done (so it can be re-run)

1. **Corpus repair.**
   - frontier/4 collapsed Archaeon's 299,991 suppression-enforcement echoes into one fact carrying count, range and
     runs. Producer semantics came from Archaeon (#735). Result: index facts 333,044 -> 33,054, reproducing
     Archaeon's run boundaries exactly.
   - Migration 013 retired the orphaned per-line pointers (sources 313,015 -> 13,025).
   - A full harvest, comb and report followed (REPORT_2026-09-30).
   - Tests: 73 passed. Commit 0e039fb46.
2. **Seven fresh-context read-only reader digests.** One per engine group, written against workers/READER_BRIEF.md,
   with RAN/OBSERVED/CONCLUDED/ATLAS_DERIVED tags and path@sha pointers.
3. **Three independent fresh-context synthesists over the same corpus.** Regularities; an adversarial common-cause
   map plus a claim-by-claim attack; contradictions and natural experiments.
4. **Two claim verifiers** (60 claims): 32 confirmed, 25 corrected, 3 contradicted, 0 unverifiable. Every
   correction was applied (workers/VERIFY_*.md).
5. **A cross-model-family blind re-derivation.** See s7.
6. **Atlas reconciliation and writing.**

**Compute:** none leased. Every worker was a read-only Claude subagent inside this session, plus a few
non-Claude API calls through NVIDIA NIM (s7). The only writes were to schema atlas (the frontier/4 pass and
migration 013, both under the 2026-09-26 authorization) and to Atlas's own directories.

## 4. Limits the operator should weigh

- **Brief echo.** Atlas's READER_BRIEF asked every reader for "search/reachability limits" and for "any case where
  the ruler could not see the target", and supplied the primitive bins. Two regularity families partly return
  the brief to its author. Mitigation: OBSERVED-only support, the adversarial pass, and the cross-family check.
- **One model family** wrote, attacked, verified and reconciled everything except s7. The critic's list of this
  author family's priors (construct splitting, deflation is safe, literature-anchor fit) is in
  workers/ARTIFACT_MAP.md s C. Treat F1 and the "it's the instrument" flavour of the whole document with that in
  mind.
- **The index still models nothing after 09-22.** There are no adapters for PTE, BEE, Aether, Hecate, Ensorain or
  Tyche, and the NPE adapter misses W1/P2/ARC3. The synthesis ran over the record through digests, which summarize
  seat syntheses, not raw rows.
- **Not visible from M1:** host-local M2 evidence (BEE raw results, the Cosmos C3 withheld branches, SFE ledgers).
  Holdout D2 is sealed and was not read.
- **Seats underweighted:** NPE dominates the comms volume (91 messages vs Hecate 2, Tyche 1).
- **Several load-bearing challenges are Artemis/Odysseus WORKER claims,** some marked unverified by their own seats
  (R-22, R-26, R-33, D002-03q). They are labelled wherever used.
- **Ananke ran a parallel inference harvest.** Its deliverables did not exist when the digests were read
  (~22:00Z), so nothing of it is cited here.

## 5. Verification record

| verifier | scope | confirmed | corrected | contradicted | notable |
|---|---|---|---|---|---|
| VERIFY_DRAFTS_1 | buried signals + ontology (30 claims) | 16 | 13 | 1 | The CW01 "register predicts regime at 1.0, never used" reading was withdrawn by CW01-D089. A6 was misattributed (NPE ARC3, not Deep Frontier). The A10 denominator was wrong |
| VERIFY_SYNTHESIS_2 | synthesis + contradictions (30 claims) | 16 | 12 | 2 | F5 is not independent (a C3 -> CW01 -> C9 citation chain). D002-03q did not time out; the full D002-03 did. Several worker claims were mistagged [OBS] |

Index figures re-derived live by the verifier matched exactly: 69/17/4 vs 66/20/4; 649/723 POSITIVE; 1,242 Vivarium
experiments with no primitive rows.

## 6. State at handoff, and what Atlas does next

- Atlas returns to **READY** at the cutoff (2026-10-01 05:00 America/New_York), or earlier once this handoff is
  pushed and reported, unless separately directed. No loop, watcher or index cadence is running.
- **Nothing was routed to any seat.** The frontier (12 + 5) is for the operator. Some items would need Aporia
  dispatch under CWO-C (e.g. X-TASK-GATE in FR-6).
- **Atlas-internal follow-ups** (Atlas's own backlog; none needs another seat):
  - ATLAS-39 redefined: tag primitive interventions per experiment arm. Seed it from the ONTOLOGY s7 matrix.
  - Add the ruler-side fields: ruler_id, ruler_can_return_opposite, zero_parameter_baseline, author_family,
    readout_type.
  - Adapters for PTE, BEE, Aether, Ensorain, Hecate and Tyche, plus NPE campaign directories after 09-22.
  - Vocabulary fixes: "Z80" (three ISAs), "ATOMIC" (two mechanisms), "competent", "content", "carrier".
- Open decisions carried from before (unchanged): the E-003 verdict of record (the operator's); the Cosmos C3
  decision gating D2.

## 7. Cross-model-family blind re-derivation (the author-prior check)

**What was done (RAN).**
- A Claude worker, blinded to the synthesis files, built a 231-line packet of OBSERVED/RAN facts only
  (workers/xfamily/PACKET.md, sha256 3a145bb7...0fe06).
  - Engines were masked as E1-E12; the key is in KEY.md.
  - CONCLUDED text was dropped.
  - Seat mechanism vocabulary was neutralized: "painter", "scaffold", "internalization", "zero-parameter rung",
    "cliff", "carrier" and so on became literal descriptions.
- The packet went through NVIDIA NIM (temperature 0.3) with one fixed prompt: "8-12 strongest cross-engine
  regularities, supports by line, independence, one falsifier; 3 things the corpus cannot tell us".
- Results:
  - gpt-oss-120b, qwen3.5-397b and glm5 are retired (HTTP 410).
  - kimi-k2.5 returned 404.
  - glm-5.3 ran out its token budget in reasoning, twice.
  - **Answered: moonshotai/kimi-k3 (10 regularities) and deepseek-ai/deepseek-v4.1-flash (12).**
  - Raw responses are in workers/xfamily/RESP_*.md; the call log is query_log.jsonl. No credential was written
    anywhere.

**Scoring against the Atlas findings (ATLAS_DERIVED; scored by Atlas, which is not blind).**

| Atlas finding | Kimi K3 | DeepSeek v4.1 | reading |
|---|---|---|---|
| F1 measurement/baselines bound the claims | YES (#5 baselines, #6 procedure as effect modifier, #9 funnel attrition) | YES (#8, #9, #10) | recovered by both, from OBSERVED rows with the vocabulary stripped |
| F2 world-supplied copy primitive + zero/fresh register state | YES (#2 affordances, #3 state scaffold) | YES (#1, #2, #12 encoding) | recovered by both; both also flag the shared byte-tape/copy design space as limiting independence, as the critic did |
| F3 copying/persistence dissociate from competence | partly (#3 transplant 0/39) | YES (#7) | recovered |
| R6 labels are not causal ancestry | YES (#1, #10) | YES (#6) | recovered by both; both rate it MODERATE, as the critic did |
| R3/F8 "reachability" | as LANDSCAPE: neighbourhoods flat, neutral or lethal; greedy fails (#4) | same (#5) | recovered as a LANDSCAPE fact. Neither model produced "search, not physics". That framing appears to come from the program and its brief, as the critic argued (FR-4 needle size) |
| F4 nominal mutation minor vs write/interaction physics | no (write-back appears only as one affordance in #2) | no | NOT recovered |
| F5 answer-before-read | no | no | NOT recovered |
| F6 present != used | no | no | NOT recovered |
| F7 label turnover | n/a (CONCLUDED text excluded by design) | n/a | not testable with this packet |

**New from the non-Claude models (not in Atlas's findings):**
- (i) **Tick phase, latency and readout timing are causal variables** (Kimi #7; E1-dominated, low independence).
- (ii) **Within-run success overstates held-out, fresh-world or transformed performance** (Kimi #8, six engines,
  with stated exceptions).
- (iii) **Topology and locality change extinction, exploration and relay** (DeepSeek #4).
- (iv) **A unified reading of recombination**: it makes long-range byte matches and deeper copy chains but lowers
  viability without adding function (DeepSeek #11). Atlas had recorded "three incompatible readings".

Atlas notes (ii) and (iii) as candidates it under-weighted. They are cheap to re-examine in the existing digests.

**What this does and does not show.**
- The strongest Atlas findings (F1, F2, F3, R6) survive a change of model family when seat vocabulary is removed.
  Both non-Claude models found them in the OBSERVED rows. That makes them less likely to be pure author-family or
  vocabulary artifacts.
- The three findings they did not recover (F4, F5, F6) are exactly the ones Atlas already rates SUGGESTIVE.
- Not controlled:
  - the packet's ROW SELECTION was made by a Claude worker from Claude-written digests of Claude-written seat
    records, so selection bias from the author family remains;
  - there are two models, one prompt, one packet, and no replicates;
  - Atlas scored the overlap itself, not blind.
- A stronger version is FR-11: a non-Claude model selects rows from raw seat files, and a third party scores the
  overlap.

**Net effect on confidence.** F1, F2, F3 and R6 keep their ratings, with the author-prior objection now partly
answered. F4, F5 and F6 stay SUGGESTIVE. "Search, not physics" is further weakened as a framing. Timing, held-out
fragility and topology are added as under-weighted candidates.
