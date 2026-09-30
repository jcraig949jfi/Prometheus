<!-- Fresh read-only readers (Artemis delegate, ubu002, 2026-09-30): 3 load-bearing claims per D003 package at b960d1a42. Owner pointers are factual; routing applies the blind-lane guard (no Crius, Bellerophon, Nyx, Aether, Cyclops, Techne, Theophrastus). -->
# D003 digest — spot-check of 10 research packages against b960d1a42600e17128f6270282b30e8e6abb5086

Method: read-only. 3 load-bearing claims per package (some packages got 1 extra side-check), evidence opened with `git show b960d1a42:<path>` and git log/grep; numeric claims recounted with stdlib python where the data is in-repo. No tests run, no analysis.py run. Owner/activity pointers from roles/*/STATUS.md and last-commit dates at b960d1a42.

## D003-01 — Accessibility rulers on a second substrate

**Answer:** Not answered; the named Crius rulers (foothold density, d_flat, rho, semantic-link survival) have no measurement on any non-Crius substrate at b960d1a42. The report's evidence supports this.

**Claims:**
- C1 [VERIFIED] The rulers exist only as proposals, with Crius as the only values, and the essay says none has been tested. Evidence: docs/essays/2026-09-24-accessibility-frontier.md:146-158@b960d1a42 ("rulers to attack, not results"; rho at :156-158, "We do not yet have a form we trust") and :222@b960d1a42 ("None of these has been tested anywhere"). Line numbers are exact.
- C3 [VERIFIED, within the limits below] No committed code or receipt computes the rulers on another substrate. Evidence: `git grep -il` at b960d1a42 for foothold density|d_flat|flat_valley|accessibility ratio|semantic-link survival|hiff. Every code hit is a false positive:
  - alien_circuitry `naive_flattening`
  - falsification `D_flat` (a Sobolev field)
  - archaeon `flat_control`
  - proteus `flatter_programs`
  - an Aether base64 blob
  - herakles A_FIELD_MAP naming HIFF as a literature family

  All remaining hits are Artemis, Odysseus or Crius planning/harvest/prompt text, or unrelated aporia/harmonia prose. I did not re-run the report's all-branch `git log -G` history search.
- C6 [VERIFIED as transcribed; the numbers themselves are UNCHECKABLE] A content-addressed measure in Ares does not beat fitness: rho_fit -0.42, rho_acc +0.37, bootstrap diff 0.05, CI [-0.18, 0.28], partial rho 0.30. Evidence: roles/Artemis/selftest/runs/R-29/REPORT.md:135-141@b960d1a42. The text matches exactly. The underlying data is outside the repo (/home/jcraig/artemis-selftest/work/R-29), so it cannot be recomputed.
- (extra) C2 [VERIFIED] FR-003 is RAW at roles/Artemis/backlog/INDEX.md:24@b960d1a42. No FR-003.md exists in backlog/threads/. FR-001.md:35-37 lists "Crius controlled pair and rulers" under "Proposed, never built".

**Owner:**
- **Crius** (crius/, docs/essays): the rulers' origin. roles/Crius/STATUS.md says "CLOSED 2026-09-23 ... Not PARKED ... a new charter would be a new campaign". Last commit to roles/Crius or crius/ is 8ad374ed5 on 2026-09-25.
- **Artemis** (roles/Artemis/backlog FR-003/FR-001, selftest R-07/R-29, challenge P16/P17): ACTIVE, last commit 2026-09-30.
- **Odysseus** (the I3 BEE foothold proposal): ACTIVE, working on the agent fabric.
- **Herakles** (the K7 bar): no seat commit since 2026-09-17, so it looks dormant.

**Caveats:**
- R-07 and R-29, the report's "incomplete" evidence, are Artemis self-test reports whose work directories are not committed. The key numbers can only be checked against the report text.
- Crius is closed, so the dispute R-07 raises over Crius's "accessible path length: undefined" has no active owner to rebut it.

## D003-02 — Implicit replication with no scalar objective (AL-5 / XE-07)

**Answer:** XE-07 and AL-5 were never run as specified. BEE has already run large arms with no effective task term, however, and in them the rate of spontaneous replication from random soup is identical across coupling arms. The report's corrections to the harvest note hold up.

**Claims:**
- C1 [VERIFIED] XE-07 is PROPOSED, AL-5 is IDEA and the blind spot is COMMISSIONED, each unchanged since the commit that created it.
  - roles/Atlas/proposals/2026-09-19_cross_ecosystem/EXPERIMENTS.jsonl:7@b960d1a42 has status PROPOSED, suggested_owner "Archaeon or Nestor (a new engine lane)".
  - roles/Atlas/proposals/2026-09-21_prior_art_raid/EXPERIMENTS.jsonl:18@b960d1a42 has status IDEA.
  - roles/Atlas/theory/BLIND_SPOTS.jsonl:4@b960d1a42 is BS-explicit-fitness-everywhere, COMMISSIONED.
  - `git log` gives exactly one commit per file: f8df65681, 2c7a19adb, 98972f55a.
  - roles/Artemis/backlog/FRONTIER.md:128-129@b960d1a42 reads "commissioned, never run".
  - Outside Artemis, Atlas and Odysseus, `git grep` for XE-07 or AL-5 finds only a false positive ("FAL-5" in evidence_wiki).
- C2 [VERIFIED] In BEE's coupling campaign, no task term reaches energy.
  - prometheus/z80atlas/coupling_campaign.py:27-29@b960d1a42 sets COMMON to reproduction=ENDOGENOUS_COPY, pressure=IMPLICIT, scoring=NEUTRAL.
  - world.py:716@b960d1a42 returns `base + (0.5 * s if cfg.scoring != "NEUTRAL" else 0.0)`, so energy income is a flat 1.0.
  - world.py:694 gives uniform weights with the comment "drift under survival".
  - prometheus/z80atlas/coupling.py:12@b960d1a42 defines OFF as "nothing (base income only; copying still charged)".
  - coupling_campaign.py:135-145 builds the B-rand ON/OFF/SHUFFLED/YOKED arms on shared k.
  - Note: v3 physics adds a separate copy-resource ledger (base_income 16 or 40, plus bonus 64 in ON). The report's "flat 1.0" refers to energy only, which is correct.
- C4 [VERIFIED, recounted] The B-rand spontaneous_SR count is 7/800 in every arm. Evidence: roles/Bellerophon/coupling_2026-09-24/receipts/COUPLING_RESULTS.json:746-1075@b960d1a42 (the spontaneous_SR blocks start at :746, :850, :954 and :1058). Parsing the JSON gives these per-cell counts (CONST_K16, CONST_K40, INC_K16, INC_K40):
  - OFF, ON and YOKED: 0/3/2/2
  - SHUFFLED: 0/3/1/3

  Every arm sums to 7/800, matching the report exactly. COUPLING_CAMPAIGN_REPORT.md:53 reads "0 de novo competent replicators in any arm", as quoted.
- (extra) C6 [VERIFIED] roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:78-84@b960d1a42 reads "base 8 spontaneous; LDIR off 0 ... replication is reachable ONLY through LDIR plus the neutral undefined-byte slide". I did not open vm.py:120-121, which is cited for "LDI and byte stores remain".

**Owner:**
- **Atlas** (roles/Atlas/proposals and theory): owns the proposal records. STATUS says "PARKED by the operator 2026-09-19 for the index LOOP"; last commit 2026-09-26.
- **Bellerophon** (prometheus/z80atlas and roles/Bellerophon): owns the BEE substrate and data. seat state ACTIVE (worlds-kernel charter); multi-day campaign TERMINAL 2026-09-29; last commit 2026-09-30.
- **Nestor** (NPE): budget window CLOSED; campaigns closed by 2026-09-27; last commit 2026-09-30. It looks parked or closed.
- **Archaeon**: there is no roles/Archaeon/STATUS.md at this sha; last commit 2026-09-28.
- **Odysseus** (TH-13, POI-033): ACTIVE.
- No seat owns XE-07 or AL-5.

**Caveats:**
- "Explicit endogenous scalar is also inert", from equal mean births of 1973.3 (C9), is an inference the report itself flags. It is not verified here.
- The spontaneous_SR label depends on provenance. Odysseus S1 found that 29% of labelled self-replicators cannot copy themselves in isolation (cited by the report, not re-checked here).
- The NPE and Archaeon points and the Tierra/Avida fossil status come partly from sub-agent reads and were not re-checked here.

## D003-03 — Composition science: quotient payoff, composition zero point, unit of mechanism

**Answer:** None of the three threads has moved toward a predictive theory. CRUCIBLE-E was withdrawn, not merely left unrun. D16C is held on ED-001. Nyx has 7 mechanisms, and 0 of them have survived transplant.

**Claims:**
- C01 [VERIFIED] Only crucibles B and C have results; A, D and E never ran; the last alien_circuitry commit is 93cdb3392 (2026-09-14). Evidence: alien_circuitry/nursery/CRUCIBLES.md:1,6,72,92@b960d1a42 and alien_circuitry/nursery/crucibles/RESULTS_C_B.md:6,37,90@b960d1a42. `git log -1 -- alien_circuitry` gives 93cdb3392 on Sep 14. `git grep CRUCIBLE-(A|D|E)` hits only alien_circuitry/nursery/* and roles/Artemis/{backlog/harvest/D4_sfe_era.md, dispatch/D003/D003-03.package.md}. RESULTS_C_B.md:21-23 confirms reduction 0.47 (2.69 to 2.22), HC 0.28 and permutation p = 0.005 per seed.
- C08 [VERIFIED] D16C pilot and freeze (steps 10-11) are HELD on ED-001 GEN21_ORIGIN_LAUNDERING (CRITICAL, 6/6 laundered), and no fix is committed. Evidence: genesis/harmonia_c/d16c/D16C_PHASE0_REPORT.md:20-23,55,60-61,66@b960d1a42 and D16C_DESIGN_PACKET.md:51@b960d1a42. Every GEN21_ORIGIN_LAUNDERING hit outside harmonia_c is a Necropolis catalogue entry. That is 4 files (CANDIDATE_INDEX.jsonl:211, scout_table.json, import_verify.json, file_exists.json), not the single row the report implies. harmonia_b's B-X04-ORIGIN-LAUNDERING is a separate amendment and not a fix. The last commit on genesis/harmonia_c is f2e3148e3 (2026-09-05).
- C12 [VERIFIED] There are 7 registered mechanisms. MECH-AVIDA-ANCESTRY-RETENTION (registered 2026-09-30) bundles parent-edge founding with reference-counted retention and does not register the founding clock as a second mechanism. Evidence: nyx/atlas/gates/MECHANISMS.json:178-184,203@b960d1a42; I parsed the file and counted 7 entries. roles/Nyx/STATUS.md@b960d1a42 has "mechanisms_registered 7" and "MECHANISMS_THAT_SURVIVED_TRANSPLANT 0". Not checked: the claim that the "unit drifted by author judgement" is the report's own interpretation, and I did not check the organ-to-boundary line mapping.

**Owner:**
- alien_circuitry/nursery has no role dir. Commits are by the operator (James Craig), and CRUCIBLE-C concerns Diomedes states. The directory has been dormant since 2026-09-14. roles/Diomedes STATUS currency is 2026-09-11, so that seat looks parked.
- genesis/harmonia_c is dormant since 2026-09-05. The Harmonia seat itself is active (last commit 2026-09-30).
- The ED-001 fix is owned by Daedalus (write_qualifications.py:43). Daedalus's last commit was 2026-09-17, so it looks parked.
- nyx/ and roles/Nyx are active (STATUS block dated 2026-09-30).
- Nestor (C10, not checked) is at rest: its budget window closed on 2026-09-26.

**Caveats:**
- The absence claims (C03, C07, EVAL02) rest on keyword greps. I did not re-grep C03 or C07.
- C10 (the Nestor cw01-e05 numbers) was not checked.

## D003-04 — Mutation-kernel nonequilibrium current: outcome bias and minimum detectable current

**Answer:**
- U1 (does the current bias outcomes): still NOT_YET_ADJUDICATED, with no experiment built.
- U2 (the residual current): real, about 19x noise, source unattributed.
- MDC: none exists. The instrument is admitted as a detector only.

**Claims:**
- C3 [VERIFIED] The U2 residual sigma is 1.4418e-03 with unreachable_removal zeroed. That is 19x the K_A/K_B disagreement (7.65e-05). Its source is unresolved. Evidence: roles/Proteus/PROTEUS_V0_6_FINAL_EXTERNAL_REVIEW_PACKET.txt:425-432,458-465,1137-1145@b960d1a42. Recount: 1.4418e-3/7.65e-5 = 18.85, and 1.4418e-3/1.7531e-18 = 8.2e14. Both match the report. Harmonia's ruling at RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md:41-46@b960d1a42 confirms that the reversible reference "CANNOT FAIL", which is the basis for C4.
- C7+C8 [VERIFIED] Operational significance is NOT_YET_ADJUDICATED at HEAD. No U1 experiment exists. The last Proteus commit is 6a98ef0bb (2026-09-18), and the kernel code was last touched by d884b3513 (2026-09-11). Evidence:
  - proteus/eval/FOUNDRY_PROFILE_CATALOG.json:26,58@b960d1a42
  - proteus/graph/GRAPH_PROFILE_CATALOG.json:26-30@b960d1a42 (USE_B prohibited)
  - proteus/graph/profile.py:29@b960d1a42
  - The git log matches exactly.
  - Note: proteus/v0_7/ does exist. Its last commit was 2026-09-05, and it holds only meter, registry and ablation results with no current work. The report's wording ("no v0_7 kernel-current work") is therefore accurate.
- C11 [VERIFIED] run_kernel.py has no positive control, no MDC and no floor guard. Evidence: proteus/v0_5/run_kernel.py:126-143@b960d1a42 sets noise_floor = max(noise), with no zero check and no injection. The audit script confirms that the sampled-kernel MDC is something "run_kernel.py never measures" (roles/Harmonia/science/proteus_current_instrument_audit.py:87-106@b960d1a42).
  - Minor: the report says the grep for MDC, NOT_DETECTED_ABOVE and "floor guard" "hits only Harmonia's ruling, audit and ledger". It also hits roles/Harmonia/STANDING_RULES.md, roles/Harmonia/pivot/HARMONIA_M2CA1148_BACKLOG_PASS_REVIEW_2026-09-18.md, the Artemis backlog and dispatch files, and one unrelated hephaestus xpol raw file.
  - Either way there is no Proteus implementation, so the conclusion holds.

**Owner:**
- proteus/ and roles/Proteus are parked. There is no STATUS.md, only dated STATUS_2026-09-0x files, and the last commit was 2026-09-18.
- P-1 through P-6 are delegated to Proteus.
- The instrument ruling belongs to Harmonia (roles/Harmonia/rulings, STANDING_RULES.md CURRENT-DET). Harmonia is active (last commit 2026-09-30).

**Caveats:**
- The V0.6 numbers are quoted from the packet. Neither the report nor I recomputed them from proteus/v0_6/RESULT_*.json.
- C13 (outcome bias possible only through selection coupling or finite horizons) is the worker's own theory and is not checkable against the repo.
- analysis.py is unrun, so the MDC is still pending.

## D003-05 — Harness channels credited as organism copying (TH-008 -> TH-014 leak fixtures)
**Answer:** PARTIAL. A schema-level guard with synthetic leak fixtures exists on main in attribution-v0, not in schema_v03. Transplant is covered only by a regression case, and TH-014 is still OPEN.
**Claims:**
- C2 [VERIFIED] There are 6 same-byte TH-014 histories plus 9 leaky variants (3 channels x SELF_LABEL/ORGANISM_CARRIER/MISLOGGED_CHANNEL). — archaeon/attribution/fixtures.py:70-102@b960d1a42; archaeon/tests/test_attribution_v0.py:11-34@b960d1a42 — Recounted: TH014_LEAK has 6 keys, and the loop at fixtures.py:88 covers 3 channels x 3 forms = 9. The report cites 71-81, but the dict actually starts at line 70 (cosmetic).
- C4 [VERIFIED] Transplant has no leaky-variant fixture and is covered only by the regression case z80atlas_seeded_transplant. inflow_injection has no fixture. — archaeon/attribution/fixtures.py:88@b960d1a42; archaeon/attribution/regression.py:47-52@b960d1a42; archaeon/attribution/ATTRIBUTION_V0.md:173-186@b960d1a42 — Inside archaeon/, "inflow_injection" appears only in schema.py, classify.py:20 and the spec table, never in fixtures or tests.
- C7 [VERIFIED (by code reading; not executed)] A16 treats only harness_log/operator_log as infrastructure, so a mis-logged copy with via=provenance_log or by_construction and a SELF_COPY label passes check(). — archaeon/attribution/schema.py:50,53,244-246,264-282@b960d1a42 — Traced by hand: A2 passes (executed_write with an organism carrier); A5 passes (the via is in MATERIAL_VIA); A9 passes (organism channel, producer = donor P); A14 does not fire, because SELF_COPY is in SELF_LABELS and DESCENT_LABELS but not REPRO_LABELS (schema.py:61-63). I did not run analysis.py G2.
- (side check) C1/C9: TH-014.md:5 carries the TH-008 alias; TH-008.md:1 on main is an Aether thread; TH-014.md:7 reads "Status: OPEN" and :17 still names the v0.3 fixture as the next step. VERIFIED.
**Owner:** Archaeon seat, in archaeon/attribution/, ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/ and ops/threads/TH-014.md. It looks active: the last commit to archaeon/ was 1e9042017 on 2026-09-29, and roles/Archaeon was last touched at f38759992 on 2026-09-28. roles/Archaeon has no STATUS.md (it has RESUME.md and TODO.md).
**Caveats:** I did not execute any test ("51 tests pass" comes from the packet). I did not check the claim that E-003 is branch-only (C8).

## D003-06 — Does the three-axis error taxonomy predict misreadings on an unseen engine?
**Answer:** Unanswered. The predictive test was never run, and attribution v0 (five axes) superseded the model in-sample.
**Claims:**
- C1 [VERIFIED] Block B calls the reduction post hoc and not tested predictively, and says sufficiency for new substrates is not established. — ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/B_B1_B6_B8.md:70-74@b960d1a42; .../REPORT.md:31@b960d1a42 — The quotes match. The case table (:18-29) has 10 rows: 9 errors plus 1 clean case, all from Archaeon, BEE, NPE or PTE, which is consistent with C3.
- C4 [VERIFIED (within keyword-search limits)] No committed artefact assigns coordinates to any Aether or Ensorain field, and the FALSE_FRIENDS ledger stops at FF-34. — archaeon/causal_lens/FALSE_FRIENDS.md@b960d1a42 — Highest FF id = FF-34. A repo-wide grep for FF-3[5-9]/FF-4x hits only an unrelated Lexis OpenAlex JSON. The only file in archaeon/ matching aether|ensorain is FALSE_FRIENDS.md. A grep for "coordinates before|three-axis" over ops/, archaeon/, Aether/, ensorain/ and the relevant roles finds only a mention in E_DELEGATION_H_ROLE.md:28.
- C11 [VERIFIED] The Aether audit predates Block B. — git log: 7e01f564a (PROPAGATION_ASSAY_AUDIT.md creation) 2026-09-27 11:45:38 -0400; 72923db05 2026-09-27 13:43:55 -0400 — This matches the report exactly. Also confirmed (C2): 72923db05 is an ancestor of b960d1a42, so the "unmerged" note is stale.
**Owner:** The taxonomy and attribution v0 belong to the Archaeon seat (ops/campaigns/C-001/DEEP_BLOCK_2026-09-27, archaeon/causal_lens, archaeon/attribution). The last commit to ops/campaigns/C-001 was 2026-09-28, and archaeon/ was last touched 2026-09-29, so it looks active. The candidate ground truth belongs to the Aether seat (Aether/AETH-03). roles/Aether/STATUS.md reads "seat state: ACTIVE" (currency 2026-09-27), and the last Aether/ commit was 2026-09-30 (1b4fb4523), so it is active. TH-017 is OPEN (ops/threads/TH-017.md:7).
**Caveats:** Absence claims rest on keyword greps, which the report also flags. I did not check the E-003 branch content (C9) or the Aether audit line ranges (C10).

## D003-07 — hstrat / phylotrack as per-birth ancestry for BEE and NPE

**Answer:** Mostly no. BEE already records the parent label on every birth. The 33% UNRESOLVED gap is about content provenance (byte sources that are not persisted), and the establishment gap comes from missing death records. Hstrat is not adopted anywhere. The harvest's H-D1-56 note ("later evidence: none found") is stale because of Nyx's frozen Avida packet.

**Claims:**
- C2 [VERIFIED] UNRESOLVED = `other = n_window_writes - copied_from_own >= L/2`, so it is a content-provenance gap; 9,578,442 of 28,964,089 births = 33.1% — archaeon/causal_lens/adapters/bee.py:20-24,93-99@b960d1a42; archaeon/causal_lens/PORTABILITY01_REPORT.md:48 (row) and :13,35 (total 28,964,089)@b960d1a42; OBSERVATORY_DESIGN.md:40-41,59-60@b960d1a42 — Recomputed 9578442/28964089 = 0.3307. The logic is at bee.py:93-99. The docstring at 17-24 states the rule. Cited ranges are within a line or two.
- C6 [VERIFIED] No hstrat, phylotrackpy or tskit in any .py, requirements, toml or cfg file; only pins and citations exist — `git grep -l -iE 'hstrat|phylotrack|tskit' b960d1a42 -- '*.py' '*requirements*' '*.toml' '*.cfg'` returns nothing; pins at techne/acquisition/poet_alife/AUTOPSY_CLAIMS_2026-09-17.json:25-26@b960d1a42; Harmonia plan at roles/Harmonia/archaeology/POET_ALIFE_BENCH_STEERING_2026-09-18.md:130-134@b960d1a42 — Grep scope was limited to those file types, same as the report's.
- C12 [VERIFIED] MECH-AVIDA-ANCESTRY-RETENTION-001 was frozen blind at e9b0783e5 (2026-09-30 07:13) over 177 shipped .spop files. It is unadjudicated and by design does not measure loss against a full pedigree — roles/Nyx/reports/REVIEW_PACKET_2026-09-30_boot_avida_ancestry.txt:73-90,156-161@b960d1a42; nyx/atlas/predictions/MECH-AVIDA-ANCESTRY-RETENTION-001.json:138 (known_uncertainty c), :334 (to_seat Harmonia)@b960d1a42 — No adjudication commit appears between e9b0783e5 and b960d1a42. HARM-48 is still OPEN at roles/Harmonia/BACKLOG_H0H5.md:120@b960d1a42.

**Owner:**
- archaeon/causal_lens (Archaeon lens adapters): last touched 2026-09-29. roles/Archaeon has no STATUS.md, and its latest roles/ commit is 2026-09-28. Status: quiet, not clearly parked.
- prometheus/z80atlas (Bellerophon, BEE): last commit 8a2390d82, 2026-09-30. Status: active. STATUS says the multi-day campaign is terminal and awaiting merge.
- Harmonia (HARM-48, ancestry ruler): commits on 2026-09-30. Status: active. STATUS.md currency line is dated 09-25.
- Nyx (Avida packet): active on 2026-09-30.
- Artemis backlog FR-034: RAW, no owner.

**Caveats:** The live BEE births logs are off-repo (C:\...), so the 33.1% is only as reported in PORTABILITY01. That hstrat tracks label descent rather than content comes from the repo's own prior-art note, not from the library.

## D003-08 — stackvm a768fad8 double solve; treegp/push sterility

**Answer:** No representation-independent attractor is supported, and WOW-C-005 is formally unstateable with no retirement ruling. The treegp/push "sterility" (A6) looks like a treegp binding defect plus a tiny, equal budget. Apollo's committed calibration shows push-pyshgp solving identity on the same instrument. Mechanism answers need off-repo data (F:\SerendipityD).

**Claims:**
- C1 [VERIFIED] WOW-C-005 is unstateable in both later classifications, and no Q5 retirement ruling exists — SerendipityFoundry/stackvm_admission/CONSOLIDATED_EXTERNAL_REVIEW_PACKET.txt:315-317,329,430-431@b960d1a42 (`NOT_CURRENTLY_STATEABLE`; Q5 posed as a question); SerendipityFoundry/selection_boundary/STACKVM_CLAIM_CLASSIFICATION.json:71-75@b960d1a42 (`U_unstateable`); selection_boundary/EXTERNAL_REVIEW_PACKET.txt:327-328@b960d1a42 — Repo-wide grep for "formally retired" and WOW-C-005 finds only the packets, queues, Artemis harvest/dispatch copies and unrelated uses (charon residue thesis, Redis, Hermes seat). No ruling found.
- C3 [VERIFIED] Apollo's 2026-09-01 cross-engine calibration (budget 600, seed 20260901) shows treegp-deap at 0.000 on all 5 functions including identity. It is labelled a SUSPECTED INSTRUMENT DEFECT and was never diagnosed — apollo/cycles/S1_archive_value/CALIBRATION_FINDING.md:56-70@b960d1a42 (added in c6a2b2a44, 2026-09-01); roles/Apollo/STATUS.txt:68@b960d1a42 (`errors: treegp-deap suspected mis-wired ... (0.000)`) — The 1/12 floor is consistent with X_TRAIN containing 0 (apollo/serendipity/s1_worlds.py:11, 12 cases).
- C5 [VERIFIED, with its own hedge] push-pyshgp has a committed identity SOLVED 1.0, which conflicts with A6's "ZERO successes" for push — CALIBRATION_FINDING.md:59@b960d1a42 (c6a2b2a44, 2026-09-01, before WOW a6f86c3d3 on 2026-09-03); A6 text is at SerendipityFoundry/wow/WOW_ARCHAEOLOGY_REVIEW_PACKET.txt:168-169@b960d1a42 (the report cites 169-170, off by one); `grep -i success SerendipityFoundry/wow/extract.py` returns no matches, consistent with "no SUCCESS handling" — Whether a driver-reported solve emits a ledger SUCCESS event is not checkable in the repo. The conflict is real as stated, but its cause is inference. APOLLO-19 is still open (roles/Apollo/BACKLOG_H0H5.md:28@b960d1a42).

**Owner:**
- SerendipityFoundry/ (stackvm_admission, selection_boundary, wow): last commit 2026-09-18. There is no STATUS file under roles/ for it. Status: dormant.
- Apollo (apollo/, roles/Apollo): last commit 2026-09-11. STATUS.txt says "SCHEDULED MINING SUSPENDED", gate eligibility INDETERMINATE, and the APOLLO-04 retire decision is pending with the operator. Status: parked.

**Caveats:**
- The genotypes, tasks.json and the stackvm VM are off-repo, so C8 (a768fad8 is identity or x+1) and C7 (3,008 ≈ 5×600) are low-confidence inference. I did not verify them beyond noting that the arithmetic holds.
- The report's own caveat stands: it did not check that the WOW read and Apollo's calibration cover the same ledger window.

## D003-09 — Ensorain: structure-discovery failure, learning-time/lifetime ratio, E0/E1 status

**Answer:** E2's structure-discovery failure is already explained by measured causes in the verdict. The learning-time/lifetime ratio was asserted, never computed or searched. The founding TT question is answered in substance but not by a gate-clean verdict.

**Claims:**
- C1 [VERIFIED] E2 failure shapes: best in-life TT id MI 0.32/0.27; SD chose TT 73/120 in CP worlds; 3-way works, 17-way does not; overfit final pick; correct model reaches R^2 only 0.90/0.79/0.44. Evidence: ensorain/E2_VERDICT.md:42-68@b960d1a42. All numbers match the text. The formal verdict is still INDETERMINATE (controls, :11-22), and the report says so.
- C11 [VERIFIED] Operator s14 lists "learning time / world-change time" and "recurrence interval / memory lifetime", not learning time/lifetime. `ratios()` records `learn_over_change = updates/drift_period` and has no lifetime field. Evidence: roles/Ensorain/prompts/2026-09-24_wtp03_authorization/01_OPERATOR_WTP03_AUTHORIZATION_verbatim.md:356-367; ensorain/wtp3/campaign3.py:148-168 (field at :165) @b960d1a42. `ratios` is called only inside `unit()` (:192), which sits in the Wave B section and is used on admitted worlds. The only uses of "learning time / lifetime" are in ENSORAIN_WTP03_REPORT.md:169 and :201.
- C14 [VERIFIED] The harvest's "Phase 2 never done (no DMRG/spectral descriptors found)" (roles/Artemis/backlog/harvest/D5_older_lines.md:245) is false. Phases 2 through 5b ran: DMRG with a 4-test instrument-trust unit test, and prod_x/sum_of_squares/random_gaussian as rank-1/rank-2/incompressible calibrations that PASS. Evidence: whitepapers/descriptor_collapse_audit.md:30,74,189-217@b960d1a42. exploratory/zoo/ contains run_phase2..5b, unit_test_dmrg.py, descriptors/spectral.py and lineage/check.py. The Phase-2 scope defined at harmonia/memory/methodology_toolkit.md:335-338 (DMRG + spectral descriptors + lineage) matches.

**Owner:** Ensorain seat (ensorain/, roles/Ensorain/). ACTIVE: STATUS says "ACTIVE, ARC3 research program" and the last commit is 2026-09-30. LM01 is NOT LAUNCHED and waits on the operator. The TT zoo belongs to Harmonia (exploratory/zoo, whitepapers/). That line is parked: last zoo commit 2026-05-05, harmonia/ last 2026-08-31. The Harmonia seat itself is active (roles/Harmonia commit 2026-09-30).

**Caveats:** Not checked: C13's claim that the harvest is stale (it relies on ARC3 THREADS/QUEUE), and C12 (preflight Lc=min(T,600)). C6/C8 are inference by the author's own label.

## D003-10 — program_ecology "untested" cells: blind spots or vocabulary artifacts?

**Answer:** The seven PE MISSING_CELL rows reflect the 2026-09-01 V0 hand curation scored by (mechanism total x substrate total). PE is the largest substrate, so its empty cells rank high. Two of the seven are random-control cells, and the public slate order reveals which ones.

**Claims:**
- K2 [VERIFIED, recounted] Snapshot = V0 curation: 81 findings, 99 mechanism labels, 57 observed cells, 286-57-5 = 224 eligible. PE has 26 labels across 21 findings, and each PE score = mechanism total x 26 (native_vocabulary 5->130, instrument_tautology 4->104, seed_instability 1->26, circular_verification 1->26). accessibility_geometry x lmfdb = 150. Evidence: evidence_wiki/gold/curation_v1.json (assignments)@b960d1a42; evidence_wiki/benchmarks/gap_prospective_v1.json:5-6@b960d1a42; evidence_wiki/benchmarks/gap_slates_v1c.py:50@b960d1a42. My recount from the JSON gives exactly these figures.
- K3 [VERIFIED, recounted] 11 of 22 mechanisms are empty on PE. Poisson expectation is 8.01 empty cells. The smallest P(empty) is confound_conditioning at 0.16, and the other six match (0.27/0.27/0.27/0.35/0.77/0.77). Evidence: curation_v1.json@b960d1a42 (recomputed with stdlib). This is still an approximation; the exact permutation null in analysis.py was not run, per the rules.
- K4 [VERIFIED] The code builds `public` in fixed order (marginal top-5 sorted descending, then uniform seed 7, then freq-weighted seed 8), publishes `score` = weight, and never shuffles. In slate_public, seed_instability x PE sits at position 10 (uniform block) and circular_verification x PE at position 12 (freq-weighted block). native_vocabulary and instrument_tautology are at positions 2-3 (marginal). Evidence: evidence_wiki/benchmarks/gap_slates_v1c.py:52-80@b960d1a42; gap_prospective_v1.json slate_public@b960d1a42. I did not open the sealed mapping (derived/v1c_sealed_methods.json), but position alone fixes membership given the code.
- (extra) K12 [VERIFIED, code] Status defaults to HYPOTHESIZED and the schema comment says it "never leaves HYPOTHESIZED by mutation". No `UPDATE ew.hypotheses` exists in the tree. Evidence: evidence_wiki/migrations/001_ew_schema.sql:190-202@b960d1a42. The live DB was not checked.

**Owner:** Mnemosyne/PEW (evidence_wiki/, roles/Mnemosyne/) is parked. evidence_wiki/FROZEN.md says "No V4 ... ontology work"; the last evidence_wiki commit and the roles/Mnemosyne STATUS currency are both 2026-09-18; the V1-C slate is sealed until its 60-day window (~2026-11-01). PE content comes from Ergon (ergon/, roles/Ergon/). Ergon STATUS says "ACTIVE", but the last commit to ergon/ and roles/Ergon is 2026-09-11, so it looks dormant.

**Caveats:** Not checked: the cell-by-cell relabelling judgements (K5-K11), which the author rates medium or medium-low. K10's post-snapshot seed_instability replication rests on Ergon gen2/gen3 packets that I did not open.

## Tally

| Package | Core claims checked | VERIFIED | PARTLY | WRONG | UNCHECKABLE | Extra side-checks |
|---|---|---|---|---|---|---|
| D003-01 | 3 | 3 | 0 | 0 | 0 | C2 VERIFIED |
| D003-02 | 3 | 3 | 0 | 0 | 0 | C6 VERIFIED |
| D003-03 | 3 | 3 | 0 | 0 | 0 | — |
| D003-04 | 3 | 3 | 0 | 0 | 0 | (C7+C8 read together) |
| D003-05 | 3 | 3 | 0 | 0 | 0 | C1/C9 VERIFIED |
| D003-06 | 3 | 3 | 0 | 0 | 0 | C2 VERIFIED |
| D003-07 | 3 | 3 | 0 | 0 | 0 | — |
| D003-08 | 3 | 3 | 0 | 0 | 0 | — |
| D003-09 | 3 | 3 | 0 | 0 | 0 | — |
| D003-10 | 3 | 3 | 0 | 0 | 0 | K12 VERIFIED (code only) |
| **Total** | **30** | **30** | **0** | **0** | **0** | 5 extra, all VERIFIED |

Minor citation slips (conclusions unaffected): D003-05 fixture block starts fixtures.py:70 not 71; D003-08 A6 cite off by one (168-169 not 169-170); D003-03 C08 "one row" outside harmonia_c is actually 4 Necropolis catalogue files; D003-04 C11 MDC/floor-guard grep has a few more non-Proteus hits than stated.
Recounts matched: D003-04 ratios 18.85 (~19x) and 8.2e14 (~8e14x); D003-07 9,578,442/28,964,089 = 0.3307; D003-02 7/800 per arm; D003-10 81/99/57/224, PE score = mech total x 26, Poisson 8.01 empty cells.
Weak spots: absence claims (D003-06 C4, D003-07 C6, D003-08 C1) rest on keyword greps; D003-01 C6 R-29 numbers and D003-10 live-DB state are outside the repo; D003-05 C7 verified by code reading only.
