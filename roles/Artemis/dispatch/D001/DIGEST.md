<!-- Fresh read-only reader (Artemis delegate, ubu002, 2026-09-30): 3 load-bearing claims per D001 package checked at 0424c372a. Owner pointers are factual; routing applies the blind-lane guard (no Crius, Bellerophon, Cyclops). -->
# D001 digest: spot-check of D001-01..10 against the repo

- Repo: /home/jcraig/Prometheus-worktrees/artemis-boot-2026-09-30b.
- Checked at 0424c372a unless another commit is named. All reads were read-only: git show, git log, git grep, plus python3 stdlib parsing of `git show` stdout.
- Later work: I diffed 0424c372a..origin/main (646cbcda8, 210 commits) over the paths the ten reports cite. Only roles/Nestor/ (ancestry-replay, x_mat_internalize, WORK_STATE) and roles/Odysseus/ (fabric_pilot, WORK_STATE) changed. None of those files are cited by the checked claims, so origin/main does not change any "no later work" claim below.
- Three claims were checked per package. `@0424` means @0424c372a.

---

## D001-01: logged query interface / selection boundary (H-D4-12, H-D4-40)
**Answer:** No logged query interface or Q1-Q7 adjudication exists. Vivarium's C6 replay lane is unbuilt, but Archaeon built T0 fingerprints, lane labels, EXO/ENDO pressure history and a replay_packet stub on 2026-09-18.

| claim | verdict | evidence opened |
|---|---|---|
| C3: "logged query interface" occurs in only 4 files (packet + 3 Artemis files) | VERIFIED | `git grep -il` @0424 gives exactly those 4 files. At 646cbcda8 the only extra hits are Artemis D001 dispatch files. |
| C9: Vivarium built none of its C6 items; migrations stop at 010; no vivarium commit since 09-18 | VERIFIED | vivarium/migrations/ @0424 holds 001-010 plus drafts/; `git log --since=2026-09-18 -- vivarium` is empty at both commits; grep for replay.packet, EXOGENOUS, LLM_PROPOSED, evo_segment and provenance_class in vivarium/ finds nothing. |
| C10: Archaeon built lane labels, EXO/ENDO pressure and a replay_packet stub | VERIFIED | archaeon/campaign6/c6base.py:12-13@0424 (LANES, PRESSURE_KINDS); segment.py:87,275,281,425@0424 (`"replay_packet": {..., "changed": {}}`); commits 9736e38a0, ca5453497, dc404e9c8 are all dated 2026-09-18. |

- **Owner pointer:**
  - SerendipityFoundry/selection_boundary/: operator commit ef504133f. The report attributes Q1-Q7 to Daedalus, and no seat STATUS claims the directory.
  - vivarium/: Vivarium.
  - archaeon/campaign6/: Archaeon.
- **Caveat:** absence claims rest on search.

## D001-02: weird physics vs learnability (Ensorain WTP-03)
**Answer:** The report's per-law attribution is not established. Weirdness in field algebra and topology survives admission; weirdness that breaks the channel or stationarity does not (this is a hypothesis).

| claim | verdict | evidence opened |
|---|---|---|
| C3: stratum denominators ~17.7k/9.5k/10.8k; wild vs clean_channel not distinguishable (P ~ 0.20) | VERIFIED (arithmetic) | ensorain/wtp3/campaign3.py:41-69@0424 (STRATA 0.45/0.25/0.30 and the propose() fallback). Assuming the first 2,000 candidates have no parents, the split is 17,700/9,500/10,800. My recomputed binomial P(clean>=4 of 7 \| p=0.349) = 0.199. Admitted per stratum is 174/4/3 (ensorain/runs/wtp03/analysis.json:21-25@0424). |
| C6: 60/181 non-tensor_index geometries; rewire 60/181; door_close 73/181 | VERIFIED | Parsed ensorain/runs/wtp03/waveA.json@0424 (181 admitted): tensor_index 121, the other four kinds 15 each; rewire_period>0 in 60; door_close>0 in 73. |
| C8: basis_change>0 and catastrophe>0 in 0/181; drift in 16/181 | VERIFIED | Same parse: 0, 0 and 16. Also confirmed the non-empty field chain count of 90 and observation chain count of 45 (C5/C10). |

- **Owner pointer:** ensorain/ belongs to Ensorain.
- **Caveat:** the batch-1 assumption (2,000 candidates) was not checked against logs, and the report says so itself.

## D001-03: can neutral drift or duplication cross the PROTEUS-46 cliff?
**Answer:** Open. Nothing tested it; PROTEUS-46's walks could not have detected it; a 5-edit neutral route exists on paper only.

| claim | verdict | evidence opened |
|---|---|---|
| C1: no later experiment; last proteus/roles/Proteus commit is 6a98ef0bb (09-18); code unchanged to HEAD | VERIFIED | `git log -- proteus roles/Proteus` @0424 and @646cbcda8 both end at 6a98ef0bb (2026-09-18). `git diff 6a98ef0bb 0424c372a -- proteus/{graph,eval,foundry,round2}` is empty. |
| C2: greedy walks never accept a neutral child | VERIFIED | proteus/round2/falsifier_46.py:117-131@0424. The incumbent key is `(cur, 0)` and a child's key is `(two, -ops)`, so a child with equal score and ops>=1 never beats the incumbent. |
| C5: 2,000 of 3,132 NEUTRAL (41% of 4,881) come from 5 operators neutral by construction; NEUTRAL_DIFF ~0.001 | VERIFIED (counts) | proteus/round2/PROTEUS-46_FALSIFIER.json:210-262@0424. CROSSOVER_SUBGRAPH, EDGE_ADD, NODE_ADD, SUBGRAPH_COPY and SUBGRAPH_COPY_ATTACH each score NEUTRAL 400/400. NEUTRAL_DIFF is 5/4,881 = 0.001. |

- **Owner pointer:**
  - proteus/ and roles/Proteus/: Proteus.
  - Supporting evidence also comes from archaeon/ (Archaeon) and roles/Odysseus/.
- **Caveat:** C5's structural explanation and C7's 5-edit path are hand derivations. The route awaits analysis.py part B, which was not run here.

## D001-04: zero SUPPORTED_POSITIVE across Archaeon campaigns 2-5: gates or substrate?
**Answer:** Both. SUPPORTED was out of reach by design for 11 of 12 weak positives (a gate-usage defect). The capable negatives are informative and point at substrate plus search.

| claim | verdict | evidence opened |
|---|---|---|
| C1: SUPPORTED needs effect >= min_effect, n >= 10, a non-empty battery, and all attacks survived; there is no significance test (C2: the rank_correlation branch tops out at WEAK) | VERIFIED | archaeon/wse/states.py:171-185 and 206-222@0424. |
| C4 + C6: 12 WEAK_POSITIVE, 0 SUPPORTED; 11/12 unreachable (4 empty battery only, 1 rank correlation, 6 with n<10); only C3-SFE-04 stopped by data | VERIFIED | Parsed archaeon/campaign{2..5}/FUNNEL.json@0424: 40 slots, 12 WEAK_POSITIVE, matching the listed IDs. Read the 12 RECEIPT.json files: C3-SFE-03 (12/12), C4-01 (57/57), C4-02 (57/57) and C5-01 (47/10) have battery declared=0; C3-SFE-06 has rho; six have n<=6; C3-SFE-04 has a declared battery. |
| C9: assay_capable true in 39/40 slots (C4-06 false); no positive_control_passed=false | VERIFIED | Same FUNNEL parse: 39/40, only C4-06 false, and none with positive_control_passed=false. |

- **Owner pointer:** archaeon/ and roles/Archaeon/ belong to Archaeon.
- **Caveat:** none on the three claims checked.

## D001-05: corpus hygiene (unfired Gemini deep-research queue, off-target Moros reports)
**Answer:** 370 of 423 queue items are unfired (the harvest said "about 360"). All fires were on 05-13/14; none of the 20 D-4 prompts fired. The 32 Moros reports are off-target by construction because the prompt gives only a file path.

| claim | verdict | evidence opened |
|---|---|---|
| C1: 423 entries: 53 fired, 370 unfired | VERIFIED | Parsed aporia/docs/gemini_research_queue/queue.jsonl@0424: 423 entries, 53 true, 370 false. |
| C2 + C3: all 53 fires on 2026-05-13/14; the only later row is an operator request (OP-2026-09-17-RSI); queue unchanged since cf2438a5d | VERIFIED | fired_log.jsonl:4-56@0424 has 38 rows on 05-13 and 15 on 05-14; row 57 is OP-2026-09-17-RSI. `git log --all -- queue.jsonl` returns only cf2438a5d. |
| C6: the Moros DR prompt contains only the artifact path but demands verbatim quotes | VERIFIED | charon/agents/moros/daemon.py:533-560@0424. Only `{artifact_rel}` is interpolated, and the prompt says "must quote a specific line from the artifact (not paraphrase)". There are 32 moros files under aporia/docs/deep_research_reports. |

- **Owner pointer:**
  - aporia/docs/ (queue and reports): Aporia.
  - charon/agents/moros/: Charon / Moros agent.
  - engine/queues/: routing rows, not checked.
- **Caveat:** C6's downstream "no content injection" is marked medium by the report and was not checked here.

## D001-06: what should a world pay for? co-evolving environments (World-0, H-D1-48, H-D4-10)
**Answer:** All three questions are unanswered. A COEVO_ENV environment already exists in Nestor's grammar (the report treats this as a correction). Odysseus's sandbox gives one weak exploratory negative on memory-in-world.

| claim | verdict | evidence opened |
|---|---|---|
| C5: no World-0 generator, null battery, C0-A or K15 in *.py; incubator has only 2 commits (09-02) | VERIFIED | `git log --all -- SerendipityFoundry/incubator` returns 17f2b8d3a and 1ac333f43, both 2026-09-02. `git grep` in *.py for null.battery, structure.probe, C0-A and K15 hits only aporia/experiments/reasoning_steering, which is unrelated. |
| C17: COEVO_ENV is implemented in Nestor Z80xAtlas and has appeared only as a drift confound | VERIFIED (existence); the "never analysed as treatment" half was only spot-checked | roles/Nestor/campaigns/z80atlas-2026-09-19/grammar.py:37@0424. It is also used as an environment level in c9x-explore-2026-09-24 CELLS.json. roles/Nestor/FINDINGS.md:156,205@0424 mention it as a bypass and confound (E-4, A-4 WITHDRAWN). |
| C9: Odysseus sandbox: gate PASS; unplanted 3,000-generation run reached no rung; readers selected out; wall = bootstrap | VERIFIED | roles/Odysseus/expedition/sandbox/RESULT.md:13-74@0424 ("Highest rung reached: NONE (not even R0) in every unplanted arm"; U_sigma evolution success .553; "first wall is BOOTSTRAP"). This file is unchanged at 646cbcda8. |

- **Owner pointer:**
  - SerendipityFoundry/incubator/: operator commits; no seat STATUS claims it.
  - SerendipityFoundry/worldfoundry/: Ludus (roles/Ludus/STATUS.md:6, "World Foundry").
  - roles/Nestor/: Nestor.
  - roles/Odysseus/: Odysseus.
  - roles/Atlas/ (blind spots): Atlas.
- **Caveat:** Nestor and Odysseus both had later commits on origin/main, in fabric_pilot, x_mat_internalize and WORK_STATE. None touch expedition/sandbox or the z80atlas grammar.

## D001-07: are inherited libraries on the causal path of winners?
**Answer:** Mostly no where it was measured (Forge, Crius). IQ-NULL was run on 08-25 and passed (ADVANCE), which corrects the harvest's "none found".

| claim | verdict | evidence opened |
|---|---|---|
| C1: IQ-NULL ran 2026-08-25; both nulls gave dE = 0.0; verdict ADVANCE | VERIFIED | aporia/iq/RESULT_IQ_NULL.json:92-112@0424 (delta_E_null_noop 0.0, delta_E_check_transitivity 0.0, verdict ADVANCE). Commit 953a8e97b is dated 2026-08-25. |
| C6: Lexis G1 found 86.19% of called primitives are decoration; 61.1% of tools wholly decorative; 5.94% load-bearing | VERIFIED | roles/Lexis/notes/G1_ABLATION_2026-08-25.md:33-64@0424 (the lines state 86.19%, 121/198 = 61.1%, and 125 = 5.94%). |
| C9: Crius C2 had 0 reproducible reuse candidates in 18 runs; 32-block tops score identically under ACC/FRESH/RESET/SCRAMBLED; hand-built controls pass F/G | VERIFIED | crius/CRIUS_C2_TERMINAL_REVIEW.md:87-100 (F PASS, G PASS) and 104-149@0424 (18 runs; 32 blocks with 43 and 49 invocations; "identical under ACCUMULATED / FRESH / RESET / SCRAMBLED"). |

- **Owner pointer:**
  - aporia/iq/: Aporia.
  - roles/Lexis/ and forge/: Lexis (Forge audit).
  - crius/: Crius.
  - roles/Aphrodite/: Aphrodite.
  - hephaestus/: Hephaestus.
- **Caveat:** C3 and C4 (IQ-NULL's standing is qualified: its rung is INADMISSIBLE and the E9 host battery fails independent authorship) were not checked.

## D001-08: Ares parked items (redundancy under attack, GA dependence, pressure combinations, ancestry)
**Answer:** The "later evidence: none" claim holds. The W15 "redundancy" is a mislabel for co-dependence. ARES-27 and the combination question already had partial cycle-1 answers.

| claim | verdict | evidence opened |
|---|---|---|
| C1: REDUNDANT means cut_all collapses but no single cut does; MIXED means each of the listed classes collapses on its own | VERIFIED | ares/carriers.py:135-149@0424 (the classify() function). |
| C2: W15 has 1/10 REDUNDANT and 6/10 MIXED (p+r 5, k+p+r 1) | VERIFIED | ares/runs/sweep_c2/gates.txt:13@0424 (W15_present classes PLAST 1, MIXED:p+r 5, RECUR 2, REDUNDANT 1, MIXED:k+p+r 1). Also confirmed the C6 shuffled recurrent-edge values 6.5/7.5/4.5 at lines 1 and 15-18. |
| C9: no Ares commit after 3f68be2b9 (09-25); the seat is parked | VERIFIED | `git log --all --since=2026-09-24 -- ares roles/Ares` returns only 3f68be2b9 (2026-09-25). There are no Ares changes on 646cbcda8. |

- **Owner pointer:** ares/ and roles/Ares/ belong to Ares (parked). W13 context is in ares/ARES_CYCLE1_REPORT.md.
- **Caveat:** C5 (by-product vs selection) is inference, as the report labels it.

## D001-09: does accumulated executable history add findability beyond diversity? (D6A, D7, D8)
**Answer:** Unresolved. The D8 content-vs-random pairing is 7/6 (p = 1.0). The "diversity does the work" reading is also not significant (10/5). D7's positive holds only inside its designed family.

| claim | verdict | evidence opened |
|---|---|---|
| K2: ledgers give M1F 29/60, HRND 28/60, M0b 23/60; M1F vs M0b discordance 11/5 | VERIFIED | Parsed SerendipityFoundry/D8/agent_d8/ledgers/eval_{M1F,HRND,M0b}.jsonl@0424 (96 rows each; families F1-F3 give 60 tasks). The counts match exactly, and exact McNemar p = 0.21. |
| K3: M1F vs HRND is 7/6, p = 1.0, with the listed task IDs | VERIFIED | Same parse. M1F-only: F1-03, 06, 10, 17, F2-14, F3-10, 17. HRND-only: F1-16, 19, F2-07, 16, 17, F3-18. Both lists match the claim ID for ID. |
| K8: no D6A/D7/D8 follow-up; directories untouched since d332658cf | VERIFIED (minor caveat) | `git log --all` over the three directories returns d332658cf (2026-09-01) only. The claim says no role file outside Artemis references H-RANDOM or agent_d8, but roles/Daedalus/GENESIS.md:23 does mention agent_d8. It is an inventory row committed in the same d332658cf, not a backlog item or a follow-up. |

- **Owner pointer:** SerendipityFoundry/D6A, D7 and D8 belong to Daedalus (roles/Daedalus/GENESIS.md:20-23 inventories them; commit d332658cf is titled "Daedalus: ...").
- **Caveat:** K4 and K6 (the CI and the 650-700 task estimate) are normal approximations and were not recomputed.

## D001-10: host coupling and placement (H-D1-65, SFE T4)
**Answer:** Few placements are inherent (CUDA/NPE on M1, PTE because it needs torch, Aether GPU on RunPod, Windows/SKULLPORT work, SFE on M2 by ruling). The measured costs of co-location are operational, not reduced N. Two harvest notes conflate events.

| claim | verdict | evidence opened |
|---|---|---|
| C11: the SFE/PEW hang coincided with the 09-24 24+4-worker launch, not the sanctioned 6-worker co-run of 09-25 | VERIFIED | roles/Vivarium/receipts/INCIDENT_2026-09-24_M2_HOST_EXHAUSTION.md:25-44@0424 (21:32Z hang; 98% committed; envgate2 --workers 24 plus audit --workers 4; the causal claim is "a reading", untested). roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md:157@0424 puts the co-run at 09-25 18:30:33Z, 38.9 min, minimum free RAM 17.2 GB. |
| C13: the SI memo's "reduces N" is a concern; NOT_RUN was 0; 8.63 h active against the caps | VERIFIED | Coupling report lines 10-12 and 161@0424 (8.63 h active; NOT_RUN 0 in every phase). programs/selective_irreversibility/memo/PORTFOLIO_MEMO_2026-09-25.md:105-108 ("Aporia's concern stands"). RESOURCE_CONFLICTS.md:51-53 (caps 18 h / 22 h) and 76-79 (M2-1 closed). |
| C15: an operator topology ruling (2026-09-16) exists, so "no placement decisions" is too strong | VERIFIED | SerendipityFoundry/SerendipityFoundryEngine/docs/RUNNING_M1_VS_M2.md:3-11@0424 (Postgres/Redis on M1; every other service on exactly one machine; SFE on M2). |

- **Owner pointer:**
  - ops/campaigns/C-001 and C-002: operator / Artemis ops.
  - archaeon/envgate2/: Archaeon.
  - roles/Bellerophon/: Bellerophon.
  - roles/Vivarium/: Vivarium.
  - programs/selective_irreversibility/: SI program (Aporia raised the concern, Cyclops ruled M2-1).
  - The SFE docs are in SerendipityFoundry/SerendipityFoundryEngine.
- **Caveat:** C9's 48-child attribution across seats is unreconciled, as the report states. C18's timing is labelled low confidence by the report.

---

## Tally (30 claims)
- VERIFIED: 30. Two carry qualifiers:
  - D001-06 C17: the "never analysed as a treatment" half was only spot-checked.
  - D001-09 K8: a GENESIS inventory row mentions agent_d8.
- PARTLY: 0
- WRONG: 0
- UNCHECKABLE: 0

No analysis.py was run. No file in any repo was modified. Temporary files are in the scratchpad only (f.txt and the D8 ledger copies).
