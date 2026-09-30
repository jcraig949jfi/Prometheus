# Atlas inference harvest -- digest: GROUP = nestor_npe (Nestor + NPE)

Reader: fresh-context, read-only. Repo F:/Prometheus-worktrees/atlas-base-role @ 1da3130d3 (origin/main 2026-09-30 18:00 -0400).
Tags: RAN / OBSERVED / CONCLUDED (seat's words, author named) / ATLAS_DERIVED (my hypothesis).

Pointer shorthand (sha = `git log -1 --format=%h -- <path>`):
- **F** = roles/Nestor/FINDINGS.md @19ef51610 (line numbers are file lines)
- **G** = roles/Nestor/EXPERIMENT_GRAPH.jsonl @afb25f9ad (92 ids; last line per id wins)
- **CR9** = roles/Nestor/campaigns/c9x-explore-2026-09-24/CAMPAIGN_REPORT.md @76061ddd9
- **W1R** = roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/W1_REPORT.md @d63b76a5f
- **P2S** = roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27/SYNTHESIS.md @948b3a45f
- **A3S** = roles/Nestor/campaigns/npe-arc3-2026-09-28/SYNTHESIS_ARC3.md @f443bcef0
- **XMI** = roles/Nestor/campaigns/npe-frontier-2026-09-30/x_mat_internalize/RESULT.md @ac5ed7a26
- **XTG** = roles/Nestor/campaigns/npe-frontier-2026-09-30/x_task_gate/PREREG.md @62d30e443
- **AR** = roles/Nestor/campaigns/ancestry-replay-2026-09-28/ (GATES.json @3d59ac090, CVTR_RECONCILIATION.md @334b6ad55, INCIDENT_RUN3_2026-09-29.md @8927e1fbf)
- **CW** = roles/Nestor/campaigns/cw01-2026-09-17/ (CAMPAIGN_STATE.json @3af735d67; loop/CYCLE_REPORT_CYCLE4 @ce97fbcc4, CYCLE5 @8a01ddede)
- **WS** = roles/Nestor/WORK_STATE.json @e2f26c4d3 (updated 2026-09-30T18:04Z)
- comms = scratchpad/comms_since_0925.txt, cited as #id

---

## 0 Coverage

**Read in full or near full:** F (644 lines); STATUS.md @fdc73636f; WS; G (all 92 ids, last-line summary); CR9; W1R; P2S; A3S;
XMI + VERDICT.json; XTG (first ~5 KB); AR GATES / CVTR / INCIDENT (first 40 lines) / PRODUCTION_RUN1_INVALIDATED / REVIEW_PACKET_RUN2;
C3_HOLDOUT_D_REPORT.md @e5b95744f (custody/status only); CW CAMPAIGN_STATE (e01-e10 headlines and limitations, loop dispositions,
totals); CW cycle 4/5 reports (grep for ruler/damage lines); CW cycle 8 report (grep for plateau lines). Archaeon's
E003_NPE_LEG_RESULT.md on BRANCH:archaeon/attribution-arc-2026-09-28@056320b4c (NOT on main).

**Comms read (full bodies):** #739, #742, #771, #808, #924, #947, #948, #1054, #1153 (Nestor); #793 Artemis, #803 Odysseus,
#1057 Harmonia. Header lines scanned: every Nestor-authored message 578-1177 and every header mentioning NPE/ancestry/P-11/CVT-R.

**Branches:** the five named branches (s1-forensics-2026-09-23, d2v3-2026-09-29, s4v21-2026-09-29, s4v2-2026-09-29,
d-seal-merge-2026-09-28) have **0 commits not on origin/main**. So is c3-holdout-d-2026-09-25. Branches with unmerged commits
are all 2026-09-14 GraphWorld-era builds: bld-g (5), bld-q (5), bld-h (2), design-review (1). They are out of this group's scope
and I did not read them.

**Not read, with reasons:**
- The individual experiment directories (PREREG/run scripts/results) for ~90 nodes. I relied on G/F/syntheses; no numbers were
  re-derived from raw results.
- P2 BACKLOG.md (40 threads), BACKLOG_ARC3.md, work_packages WP-1..12, delegates/ (EXTERNAL_RESEARCH, CROSS_ENGINE,
  ACCESSIBILITY): cited only via syntheses.
- z80atlas-2026-09-19 PREREGISTRATION/REPORT.html; z80atlas-forensics S1A/S1C/H4 docs (cited via F section E).
- CW cycles 1-3 and 6-8 in full (169 KB cycle 8 report grep only); CW DEFECTS.jsonl (92 rows, a few read); CW e01-e06 detail.
- journal/: holds only 2026-09-14.md (pre-NPE). No Nestor journal exists for 09-17..09-30 on main.
- sidequests/graphworld, the 09-14/15 swarm rounds (memory index lists them; outside NPE scope).
- **Sealed holdout D/D2 CONTENT: deliberately not read** (brief rule). Only existence, custody and status are reported.
- The T-003 child-genome Q4/L5 recertification by Odysseus (#813): no result was found in what I read.

**Staleness warning:** STATUS.md currency line says 2026-09-26 07:15 and only prepends P2/W1. It carries no ARC3, ancestry-replay,
D2 or frontier state. WORK_STATE.json (09-30) is the current state record.

---

## 1 Experiment ledger (most recent first; 28 rows)

| id | date | question | substrate / ruler | controls, n | OBSERVED | CONCLUDED (Nestor unless named) | status | pointer |
|---|---|---|---|---|---|---|---|---|
| X-TASK-GATE | 09-30 | Does task competence spread through the organisms' own causal replication when interaction is competence-gated? | ffa6 cell, dense VM, ATOMIC; rulers P11/LABEL/EXT/INIT provenance + held>=0.5 AND reader | SHUF planted null (gate reads 2 other orgs); Stage 0 EXTERNAL positive arms; 18 seeds/arm | RAN: **nothing**; syntax-checked only | "most likely outcome of Stage 1 is FLOOR or NO_REPLICATOR_REGIME" (eligibility declared) | frozen, NOT executed (needs a separate Aporia dispatch) | XTG; WS; #1155 |
| X-MAT-INTERNALIZE | 09-30 | Is C-A3 internalization material, or pair-tape bookkeeping/transplant? | dense_taint byte-maker tags; X = XENO share of attributed bytes | replay gate 26/26; 18 REPLACEMENT runs as descriptive contrast (no planted transplant) | 8/8 EVENT runs ENDOGENOUS_MATERIAL; median X 0.020, max 0.107; MUT share 18-56% in 6/8; 2 events = 1 organism | "ENDOGENOUS"; "closes the transplant/bookkeeping alternative" | confirmed (by prereg rule); Harmonia #1057 SUPPORTED, with disclosures | XMI; #1054; #1057 |
| T-003 ancestry replay (NPE leg of Archaeon E-003, #812) | 09-28/29 | Byte-level who-built-which-byte on the 11 T-003 runs | independent Z8 shadow tracer vs Archaeon reference; s4 flip test | G1 451/451 fixtures; G2 fresh sets; 9 sims / 29 distinct births | tracer agreement 1.0 on all gated fields; flip coverage self 159/496=0.321, other 48/168=0.286, TIED 8/32; FAILED 0; leak 0 | Archaeon: "INCONCLUSIVE"; later corrected: only the R3 route (<30 births) is clean, and "the NPE leg was uninformative by construction" | inconclusive (by design) | AR; #947, #948; BRANCH:archaeon/attribution-arc-2026-09-28@056320b4c E003_NPE_LEG_RESULT.md |
| X-A3-WITHDRAW | 09-28 | Does gradual vs abrupt withdrawal of the zero-reset scaffold matter (Bourrat 2022)? | cycle-aware robust share | paired seeds identical to epoch 300; CONTROL_ZERO; 32/arm | persists GRADUAL - ABRUPT = 0.00; 12/12 persist; robust share 0.22->0.94 (ABRUPT), 0.24->0.93 (GRADUAL), 0.15->0.10 (control) | CLEAN_NULL on speed; readout = "internalization under scaffold REMOVAL" (EXPLORE) | inconclusive / C-A3-WITHDRAW-ROBUST PLANNED, never run | F:533-553; G |
| C-A3-INTERNALIZE | 09-28 | Do lineages founded by environment-dependent donors come to be competent from random registers? | P-11 construction competence from random entry state | frozen 86f929241; 144 fresh runs; bar 4 | 8 events (ffa6 7, 7ae3 1); state-free at first donor 1/94 donor runs (93/94 absent); 18 runs via replacement | "endogenous internalization of register initialization" | confirmed | F:524-531; #808 |
| X-A3-FORENSIC-16000006 | 09-28 | Is the 7ae3 16000006 robustness gain a single-change transition? | knock-in / revert / cross-graft | preregistered causal rule | knock-in 0/5, revert 0/8, cross-graft 0/12; 118-126 replications, 49-54/64 bytes changed | "KILLED as single-change"; robustness arose by distributed change | falsified (single-change) | F:501-509; G |
| X-A3-FAIR / X-A3-AUTOPSY | 09-28 | Is zero-specialization a ruler artefact? Where do post-copy losses occur? | treatment-blind ruler over zero/0x5A/random entry | worlds CARRIED/ZERO/0x5A | S_ZERO 0.867 (30 donor runs) vs S_5A 0.111; runaway 23/48 ZERO vs 3/48 0x5A; losses C3 child material 0.51/0.63; exact copies 4/63, 38/340 | "Zero-specialization is real"; "post-copy bottleneck is copy fidelity" | confirmed (EXPLORE) | A3S s2-s3; G |
| CVT-R on Nestor donor sets (Artemis) | 09-28 | Are P-11-competent donors heredity-capable? | CVT-R (perturb parent bytes, 2 generations, recurrence) | prereg 77bc0dbce | (a) 23/32, (b) 83/100, (c) 8/8; 19 genomes fail (11 at gen 2, 8 recurrence) | Nestor: "construction is not heredity, measured" (qualification) | confirmed qualification | F:595-614; #891 |
| C-ZERO-SPECIFIC | 09-27 | Is the fresh-state establishment rescue specific to ZERO? | establishment = runaway given donor | frozen b498b133b; fresh 16-donor panel; 48/arm | ZERO 26/48, CONST(0x5A) 2/48, CARRY 6/48, RANDOM 3/48; p = 2.4e-8 | "dependence on environment-supplied zero addressing that the donor's own block copy consumes" | confirmed | F:466-473; P2S s0; #771 |
| X-P2-PLANT / X-P2-SHAM / X-P2-ATTRIB | 09-27 | Is acquisition driven by encoding, by density, or by availability? | donor acquisition runs | stock vs dense VM; 96 runs/arm | PLANT (2-byte copy planted once/genome) 32/96; SHAM 0/96; plain 0/96; dense 49/96; ATTRIB 372/372 lose competence on stock VM (0.927->0.000); planted carriers 0.76->0.16 | "acquisition limited by AVAILABILITY of copy-capable material"; "encoding accessibility" NARROWED | confirmed (EXPLORE, not promoted) | F:475-480; P2S s1 |
| X-P2-BRIDGE / X-P2-REGSTATE | 09-27 | Does the ffa6/7ae3 split replicate? Which reset state rescues? | S1-S5 stage chain; 32 runs/arm | fixed implanted panel | effect E: C7 +0.25, C7S +0.22, C7N +0.09, CF +0.09; S5 CF CARRY .281/ZERO .531/CONST .156/RAND .188 | "split does NOT replicate -- it reverses"; "Persistence per se REFUTED" | falsified (W1 reading) | P2S s1-s2, s5; G |
| C-STATELESS-FFA6 | 09-26 | Is establishment in ffa6 limited by register-state persistence? | runaway given fresh-start-competent donor | frozen 0cba4eb5c; 48 seeds/arm; post-hoc cell restriction declared | DENSE 11/33 vs STATELESS 34/42; p = 3e-5 | "gated by REGISTER-STATE PERSISTENCE" (later re-described by C-ZERO-SPECIFIC) | confirmed number, mechanism re-described | F:453-462; W1R |
| C-STATELESS | 09-26 | same, both cells | same | frozen d4f7ba271 | 11/24 vs 23/29; p = 0.012 (bar 0.001) | NOT_CONFIRMED | inconclusive | G |
| C-DENSE-COPY | 09-26 | Is donor acquisition limited by block-copy encoding accessibility? | fresh-start-competent donor (P-11) | frozen 57c1cd359; 64 seeds/arm | PLAIN 1/64 vs DENSE_COPY 39/64; p = 1e-14; block-copy encodings present in 87/96 plain runs | "limited by the ENCODING ACCESSIBILITY ... Presence is not the barrier" | confirmed number; reading narrowed in P2 | F:443-451; #739 |
| X-DONOR-DISCOVERY | 09-26 | How often does a competent donor arise in random pair-tape pops? | L1-L4 ladder | PC-ASSAY, PC-RUN | 1/96 (7ae3 1/48, ffa6 0/48); that donor had NO OP_SELF | "acquisition-limited"; L1 ruler (SELF+LDIR) "too narrow" | confirmed (EXPLORE) | W1R s1 |
| C-CORE | 09-25 | What founder material does runaway heredity conserve? | z8taint founder-byte frequency | frozen 1c982e7e7; 64 fresh seeds | 27/64 ran away; 17/27 meet CORE4 endpoint (bar 60%); pos 23 27/27, 52 23/27, others <=13/27 | "conserves ... OP_SELF and LDIR ... and little else"; Aporia #621: exactly what purifying selection predicts | confirmed, thin margin | F:376-389; #620-#622 |
| X-CONTENT | 09-25 | Is "founder-descended" content inheritance? | z8taint byte provenance | 19 pops, 0 replay mismatches | founder byte share median 0.134 (own), 0.253 (foreign); anc0 share ~1.0; 17/19 pops no organism >=50% founder bytes | "lineage descent, not content inheritance" | confirmed (EXPLORE) | F:368-372 |
| C-SWAP-ACQUIRE | 09-25 | Does the 7ae3 genome run away in foreign cells vs a random implant? | founder-descended runaways | frozen 82b6caeb3; 240/arm | 9/240 vs 0/240; p = 0.0018; rule needed 10 vs 0 | NOT CONFIRMED | inconclusive | F:363-367 |
| X-ATOMIC-RANDOM | 09-25 | Does C-ATOMIC C1 need the genome? | world-level runaway + anc marker | 80/arm | random implant 0/80 vs 46/80; p = 1.3e-18; 100% of the final population carries the founder marker | "C-ATOMIC C1 reads as stated" | confirmed (EXPLORE) | F:353-357; C9-D24 caveat F:555ff |
| C-ATOMIC (C1/C2) | 09-25 | Does tape-write erosion stop pair-tape heredity? | P-11 depth >= 20 (world-level) | frozen; 80 seeds/arm (C1); 15 specimens x 8 (C2) | C1 46/80 vs 1/80, p = 4e-17; C2 1/120 vs 0/120 | C1 "Tape-write erosion is what stops pair-tape heredity in 7ae3's cell"; C2 NOT CONFIRMED | C1 confirmed; C2 inconclusive | F:328-334; CR9 s3 |
| X-STALL / X-STALL-F0 / X-STERILE | 09-25 | Why do losing tickets stop copying? | fresh-state copy assay on live lineage members | founder positive control 166/192 | 177/192 GENOME-sterile at epoch 100; with mutation OFF 187/192; children fertile at birth 75-80%; 57% of interactions change genome, ~5.5 bytes | "tape-write EROSION ... ~5%/byte/epoch, ~25x the nominal rate" | confirmed (EXPLORE) | F:316-327 |
| X-DOSE-CURVE | 09-24 | Are founders superadditive (critical mass)? | depth >= 5; LRT | k = 1, 2, 4, 8; 64 seeds each | s(k)=1-(1-p)^k, p=0.13 fits; LRT p = 0.42 (runaways p = 0.57) | "founders are independent lottery tickets"; "critical mass" name wrong | falsified (superadditivity) | F:308-311 |
| C-RUNAWAY | 09-24 | Does the recombination splice prevent runaway pair-tape heredity? | P-11 depth >= 20 | frozen; 150/arm | 7/150 splice-off vs 0/150; p = 0.0073; max depth 549 vs 13 | "the operator that manufactured ~88% of the predecessor's 'replicators' ... prevents real ones" | confirmed (one specimen, 7ae3) | F:286-296 |
| C-DENSE / C-ABLATE | 09-24 | Non-pair physics: is spontaneous replication blocked by op-chain encoding length? Which relieved barriers are necessary? | evidence-backed replication (ALLOC/BIRTH gate) | frozen; 40 fresh cells | C-DENSE 13/40 vs 0/40, p = 3.8e-5; C-ABLATE self-location 15->1 (p = 6.1e-5), search 15->6 (p = 0.0059); energy-for-depth 3 vs 3 | "the discovery barrier is encoding length" (permissive world) | confirmed | F:247-262 |
| C-SELFLOC / C-ENERGY | 09-24 | Non-pair physics: self-location gate; depth-1 wall | P-11 depth | frozen; 36 / 40 fresh cells | SELFLOC 13/36 vs 0/36, p = 1.6e-10; ENERGY 20/40 vs 4/40, p = 7.2e-5; side prediction (RESOURCE_GATED) falsified 2->6/12 | "self-location is the gate"; "depth-1 wall is newborn starvation" | confirmed (implanted copier only) | F:225-245 |
| C9 + C9-H1R | 09-24 | Cycle-9 frozen inner experiment (H1 cue gating, H2 propagation, H3 reservoir) | frozen protocol 5819bc6d; audit 21/21 | 1,200 runs | H1 arms identical (C9-D16) -> rerun: I = +0.20; gate+cost competence 0.000 vs 0.200; H2 4/16 vs 0/16 (7ae3); H3 1/1/0 of 64 certificates | H1 "COST_INTERACTION_ONLY"; H2 "EVENTS_WITHOUT_PROPAGATION"; H3 NOT_DEMONSTRATED | H1 invalid->repaired confirmed; H2 weak; H3 retired | F:264-284; CR9 s1 |
| S1-S4 forensics (S1C-P11-REASSAY, S1B-H4) | 09-23/24 | Do the 72 h campaign's 1,031 "spontaneous replicators" survive a causal criterion? | P-11 causal-copy assay (3 draws, majority 2) | 256/256 replay match; T-P11 14/14 | 1,031 -> 57 (48 literal); 69/7,919 events causal; max P-11 depth 2; splice made 6,287/6,547 matches (Z80A-D05); H4 source run had 0 births | A-1 "NARROWED three times"; A-4 WITHDRAWN | confirmed (narrowing) | F:182-223 |
| Z80A-72H | 09-19..22 | Broad Z80 x Atlas search | predecessor PAIR_EXECUTION detector (donor wrote >= 25% of a half) | 23,471 runs; 10,741 matched pairs | 1,031 ADMISSIBLE, all PAIR_EXECUTION; depth 1 in 911 | first report inflated; four REPORT defects (R-01..R-04) | superseded by S-series | F:13-142 |
| CW01 e07 / e08 / e09 | 09-18 | weather/brain damage; rank-tax tensors; algorithmic soup | admissibility gates P1-P5; held64 | e07 gate refused twice; e08 8 lineages/arm; e09 single-op ceiling | e07 P1 false, P4 false; e08 competent lineages 2/1/2/3 per arm (min 6); e09 single-op ceiling 142.5-159.0 = abstain floor 159.0, 0/64 competent | INCONCLUSIVE / DESIGN UNREACHABLE (all three) | inconclusive | CW CAMPAIGN_STATE e07-e09 |

---

## 2 Mechanisms (seat's words; claimed level vs my judgement)

| mechanism (Nestor's words) | claimed | my judgement (ATLAS_DERIVED) | synonyms elsewhere | pointer |
|---|---|---|---|---|
| **Barrier map**: "variation -> donor acquisition -> causal copy -> descendant competence -> sustained heredity" | organizing frame; each stage "moved" by a CONFIRM | Solid as a staged decomposition. "Descendant competence" was never measured separately in W1 (W1R s3 says so). P2's S1-S5 chain gives the only stage shares (S2->S3 and S4->S5 are the lossy steps). | R0/branching decomposition "acquisition vs establishment" shared with Archaeon and BEE (XE-EST-1, P2S s7) | W1R s3; P2S s5; #739/#742/#771 |
| **"Encoding accessibility, not presence"** (acquisition) | CONFIRMED (C-DENSE-COPY) | The number stands; the mechanism reading was narrowed twice by the seat: to "availability of copy-capable material" (P2) and then to "CARRIER EXPOSURE = frequency x persistence" (ARC3, one-parameter hazard fitted on one arm predicts the other: PLANT 28.6 vs obs 32; DENSE 54.8 vs obs 49). Two informative arms, one parameter: suggestive, as the seat says. | Aphrodite slice 4 "ACCESSIBLE vs REPRESENTABLE"; Odysseus acquisition census | F:443, F:475-480, F:495-499; A3S s1 |
| Non-pair "discovery barrier is encoding length" (6-byte ALLOC->copy->BIRTH chain; found at 3 bytes) | CONFIRMED (C-DENSE) | Scope: permissive world only (search + free self-location + energy inheritance). It is a separate result from C-DENSE-COPY (different physics). | same accessibility family | F:247-262 |
| **Tape-write erosion**: write-back of both halves after every interaction, "~5%/byte/epoch, ~25x the nominal rate" | CONFIRMED in 7ae3's cell (C-ATOMIC C1); NOT general (C2) | Strong within one cell; it is the second barrier "once copying starts". A world-physics artefact (write-back policy), not an organism property. | "mutational meltdown" / error load; "write authority" | F:316-334 |
| **Recombination splice prevents runaway** (and manufactured ~88% of predecessor replicators) | CONFIRMED (C-RUNAWAY, 7ae3 only) | One specimen; effect size 7/150. | variation operator as ruler contaminant | F:286-296 |
| **Newborn starvation** (energy 0 at birth caps the slice) | CONFIRMED (C-ENERGY) | Implanted copier; non-pair physics; not needed for a first spontaneous copy (C-ABLATE energy arm null). | resource bootstrap / maternal provisioning | F:236-245 |
| **Self-poisoning register state** -> re-described as "dependence on environmental scaffolding that the reproducer's own action destroys" (LDIR advances HL/DE; the donor borrowed HL from never-written zeros) | W1 CONFIRMED (ffa6); P2 re-described and CONFIRMED (C-ZERO-SPECIFIC) | The re-description is better supported. Seat flags circularity: "the COMPETENT ruler certifies from zeros". X-A3-FAIR (treatment-blind ruler) supports that zero-specialization is real. | Tierra "stale registers are a hijack channel"; Ananke T-M3-1 evolved state-reset bootstrap; Archaeon "265/265 random copiers are environment-gated" | F:453-473; P2S s3; A3S s2 |
| **"The environment is the self-location machinery"**: 95.7% of competent donors are SELF-free offset-64 copiers, work only at tape offset 0 | EXPLORE corpus result | Well supported by the transplant delegate (280/280 SELF-free copiers fail when moved >= 16 bytes). | literature: every published soup supplies self-location via resets (P2S s6) | P2S s4; F:490-494 |
| **Endogenous internalization of register initialization** (copier fixes its own destination, e.g. LD DE,3200 before LDDR) | CONFIRMED (C-A3-INTERNALIZE 8/144); material (X-MAT-INTERNALIZE 8/8) | Confirmed at a low rate (8/144; 7 of 8 in ffa6). "Competent" = P-11 construction; CVT-R set (c) 8/8 on the 16000006 lineage supports heredity for that one lineage only. | Bourrat 2022 scaffold internalization; Ananke state normalization | F:524-531; XMI |
| **Self-location NOT internalized**: only 2/332 true locators (one motif, seed 16000026) | EXPLORE | Supported; this is the scaffold that stays external. | "support the lineages never replace" | A3S s5-s6 |
| **Founders are independent lottery tickets** (~13%, decided in ~12 epochs; loss = cessation, not extinction) | EXPLORE CLEAN_NULL + WEAK_SIGNAL | Supported. | establishment probability, R0 < 1 branching | F:308-315 |
| **Heredity conserves the SELF+LDIR core, turns over the rest** | CONFIRMED (C-CORE) | Aporia #621: purifying selection + drift predicts exactly this; theory-aware by date. | copy-core conservation (Archaeon lineages keep 0.0 founder material: "not a law", P2S s7) | F:376-397 |
| **Cost interaction** (answer-before-read obstruction is "the price of reading the cue, not the ordering itself") | CONFIRMED (C9-H1R I = +0.20) + transplant to 4 transforms | Supported; mechanism: guessers carry all ungated competence; no reader evolves. | CW01 cycle-8 "identity plateau" | F:264-284 |

---

## 3 Failures and invalidations (what was LOST vs what SURVIVES)

| failure | LOST (interpretation) | SURVIVES (raw observation) | pointer |
|---|---|---|---|
| **Similarity detector** (09-19 rehearsal): 90% byte-identity called a half "a copy"; fired the top flag on junk | "spontaneous replicator from random bytes" in rehearsal | resemblance-without-writing is kept as its own counter (`births_similar_no_write`), a world property | memory feedback_similarity_is_not_copying; F:404 lesson 2 |
| **Z80A-D05**: pair-tape fidelity read AFTER `_mutate`; the RECOMBINATION splice made the match in 6,287/6,547 events | 910 of 1,031 "replicators" (F:424) | 1,031 events where a donor wrote >= 25% of a half; 57 P-11 survivors | F:209-223, F:424 |
| **P-11 certifies CONSTRUCTION, not heredity** (Artemis #793; Odysseus #803): painters pass at 0.90-1.00 | every "competent donor/replicator" statement -> "P-11-certified construction event"; the 57 S1-C survivors: 2 copy themselves, 1 context-dependent, 17 paint, 37 do nothing from reachable states | P-11 as a construction-causality assay; 7ae3 founder is a genuine copier, so C-RUNAWAY/C-ATOMIC/C-CORE keep their basis | F:510-522 |
| **CVT-R**: 19 P-11-certified genomes fail (11 at gen 2) | "competent" = heritable, for 17-28% of sets (a),(b) | construction competence itself; set (c) 8/8 | F:595-614 |
| **C9-D14**: an organism keeps its id while its bytes are replaced (identity 0.97 after 1 epoch, 0.00 by 600) | H3 id-based certificate "certifies identity, not heredity" | repaired by material ruler R3 (tournament 9/9) | F:223; CR9 s4 |
| **C9-D16**: `world.Runner` never passed output_gate/cue_cost; four H1 arms identical to the last decimal | C9 H1 NO_DETECTED_EFFECT | repaired rerun C9-H1R I = +0.20 | F:268-270 |
| **C9-D17 / C9-D24**: RANDOM_MATCHED == in situ (same RNG draws); ACTUAL shifts the stream by L | H2 "random 0/16 and in situ 0/16" as two nulls (it is ONE null); any per-seed pairing | all unpaired contrasts (T-DEF-D24 audit: no verdict changes) | F:555-593 |
| **X-DENSE-OPS**: VM module leaked across reused pool workers (PERMISSIVE 103,193 births vs 337) | that run | rerun X-DENSE-OPS-R | G X-DENSE-OPS |
| **X-POSITION**: "copying needs register state" | withdrawn: partner sabotage in the assay draw (randomized victim runs first) | a real P-11 assay hazard: side-1 copiers hijackable | F:434-436 |
| **Self-state ruler cycles** (rate after ONE own execution; 16000006 founders copy after 0, 2, 5 executions, fail after 1, 3, 4) | "poisoned/robust" labels in X-DD-SELFSTATE, X-P2-ENDOSTATE, X-P2-D0CHECK | 18/18 NO_COPY donors copy at 0.0 after one execution (as a one-point snapshot) | F:501-509 |
| **X-PAIR-NORECOMB**: floor-vs-floor (P-11 events 0/0 in both arms) | CLEAN_NULL downgraded to INVALID | nothing | F:627-631; Artemis #888 R-11 |
| **R-05**: P-11 reassay per-draw files gitignored; 26 of the 57 rest on one event passing exactly 2 of 3 | the "57" as a robust count; cannot be re-audited | "57, of which 26 rest on one 2-of-3 event" | F:638-644 |
| **C9-D12**: H2 bar depth >= 5 had no precedent (max P-11 depth over 1,031 was 2) | - | recorded | F:221 |
| **FORCED_READ is not a read-order change** (tasks.episodes passes base = v XOR key) | A-3 forced-read advantage; "cycle 8 established one" WITHDRAWN (a proposal was misattributed as a finding) | ANSWER_BEFORE_READ favoured in both pair sets | F:66-78 |
| **A-4 endogenous-only accessibility** (1 instance) | WITHDRAWN: 0 births, 0 deaths, 0 mutations in 4,000 epochs; exact control crossed at epoch 48 | - | F:80-88, F:203-207 |
| **Z80A-D04**: 64 of 65 endogenous-reach flags judged against a control not run for them | those flags | - | F:212 |
| **CW01 fixed-count damage rulers** | P-D01 length dose, P-E05 depth coupling, P-E05 rule "DISAPPEAR"; P-D01 set and P-F06 select "SHRINK" under scattered Bernoulli(f) | P-D01 operand effect "SURVIVES_RULER_CHANGE"; raw fixed-count losses | CW cycle 5 lines 198, 202 |
| **CW01 e07**: P1 damage unattainable at primary severity (only f >= 0.44), P4 not separable; evolution never reaches state use (intact 0.37-0.43 vs accumulator 0.74) | e07 question never posed ("not null because the causal comparison was never posed") | gate credibility 5/5 broken fixtures refused | CW e07 |
| **CW01 e08**: competent lineages below frozen min 6 | tax effect c_tax = null | scalar burden CONTROL 1.725 vs TAX 0.834 vs TAX+AMP 0.512 (not promoted) | CW e08 |
| **CW01 e09**: organism has no call/compose/reuse (one 3-bit nudge per tick) | composition question | single-op ceiling at the abstain floor; 3-op chains overfit train8 | CW e09 |
| **Ancestry replay run 1** invalidated (duplicate_of = itself); **run 3** unauthorized (stale one-shot schtask) destroyed 10/11 run-2 1% sample files | run 1 statistics; the 1% sample (operator decision) | births byte-identical run1 vs run2 11/11; births-agreement PASS (#927) | AR PRODUCTION_RUN1_INVALIDATED.json; AR INCIDENT |
| **X-MAT-INTERNALIZE disclosures**: pilot began before the freeze (7m49s); "not blind to transplant" overread a descriptive control | the "transplant would be detected" claim (no planted transplant exists) | 8/8 endpoint; replay 26/26 | XMI Disclosures; #1057 |

---

## 4 Rulers

| ruler | sees | cannot see | audit |
|---|---|---|---|
| Predecessor PAIR_EXECUTION detector (donor wrote >= 25% of a half) | write events | whether the write is a copy; reads after the splice (D05) | killed by S-series |
| 90% byte-identity (rehearsal) | resemblance | causation; fires loudest in converged pops | withdrawn 09-19 |
| **P-11** causal-copy assay (donor re-executed against a randomized victim; 3 draws, majority 2) | construction causality from the donor's writes | heredity; painters; copiers needing >1 slice (96-byte cells); state it was certified from (not stored) | T-P11 14/14; Artemis panel, Odysseus recert |
| **CVT-R** (Artemis; perturb parental bytes, 2 generations, recurrence) | transmission of variation | - (applied to 140 Nestor genomes only) | prereg 77bc0dbce |
| P-11 chain depth (world-level vs founder-rooted) | unbroken certified chain | long lineages: ~5-16% of events uncertified cap chain at ~1/p generations (X-CERT-BREAK) | F:389-395 |
| anc marker (ancestry) | slot-lineage descent | content (13-25% founder bytes) | X-CONTENT |
| z8taint / dense_taint (byte provenance) | who made each byte | mutation-made bytes (18-56% in XMI); no planted-transplant test | XMI limits |
| Fresh-state competence (zero registers) | competence from the environment's zero state | life-state competence; circular with the zero reset | X-A3-FAIR repair |
| Self-state robustness (1 own execution) -> cycle-aware k = 1..6 | carried-state robustness | single-k cycling (defect) | F:501 |
| Material ruler R3 (Cycle-9 H3) | material heredity | - | tournament 9/9 |
| s4 flip test (T-003 replay) | identified loci whose flip changes output | bytes executed before their final store (data-as-code): "irreducibly INAPPLICABLE" | flip coverage 0.25-0.32, all FAIL floor 0.50 |
| DOM (dominant-byte share) painter screen | homopolymer painting | non-homopolymer constructors | W1/P2/ARC3 corpora max 0.28; T-003 children 29/29 >= 0.75 |
| CW01 damage rulers: fixed-k / contiguous / round(f n) vs Bernoulli(f) | fraction damage (Bernoulli) | count-fixing rulers hit short genomes harder | Bernoulli ruler QUALIFIED on 126 programs (hit counts chi p 0.48-0.49; length slope 2.8e-5 inside band; sham displacement 0) |

**Cases where the ruler could not see the target (OBSERVED):** P-11 cannot see heredity (#793); flip test cannot decide
data-as-code loci (E003); id-based certificate cannot see byte replacement (C9-D14); H4 endogenous arm cannot reproduce, so it
cannot test accessibility (C9-D07); the T-003 corpus (29 births) is below the R3 minimum of 30 by design.

---

## 5 Repairs (and whether the outcome moved)

| repair | outcome moved? | pointer |
|---|---|---|
| similarity -> donor-wrote-bytes gate -> P-11 -> CVT-R | yes, each time: 1,031 -> 57 -> 2 genuine self-copiers (+1 context) | F A-1, E-3, :516 |
| read fidelity before the splice (D05 fix) | 910/1,031 became splice artefacts | F:424 |
| C9-D16 wiring fix (C9-H1R) | null -> I = +0.20 | F:268 |
| world-level -> founder-rooted endpoint (X-ROOT-AUDIT) | 46/80 -> 12/80; then reversed back by X-ATOMIC-RANDOM + X-CERT-BREAK (chain breaks, not native lineages) | F:349-395 |
| fresh-state ruler -> treatment-blind ruler (X-A3-FAIR) | zero-specialization survived | A3S s2 |
| single-k -> cycle-aware self-state ruler | X-P2-ENDOSTATE null reproduced (326/341 agree); single candidate killed as single-change | G X-A3-ENDOSTATE-R |
| fixed-count -> Bernoulli(f) damage ruler (CW01 P-G01/P-G02/P-G08) | 4 of 7 damage claims disappeared or shrank | CW cycle 5 |
| X-DENSE-OPS one job per process | contaminated result -> clean 23/47 vs 0/47 | G |
| ancestry replay: tracer v1 -> v2 -> v3 (fresh sets after each exposure); s4 v2 -> v2.1 -> v2.2 | agreement reached 1.0; s4 conformance 2/2; verdict stayed INCONCLUSIVE | AR GATES |
| D2 successor seal v2 -> v13 (12 re-audits FAIL, v13 PASS) | custody gate AUDIT passed | WS fabric_tasks |

---

## 6 Primitive-level interventions (outcome change)

| primitive | intervention | outcome | pointer |
|---|---|---|---|
| **encoding / representation** | 1-byte ALLOC/LDIR/BIRTH aliases (non-pair) | replication 0/40 -> 13/40 | C-DENSE |
| encoding | 1-byte LDIR/LDDR alias (pair tape) | donor acquisition 1/64 -> 39/64 | C-DENSE-COPY |
| encoding (control) | 1-byte block-WRITE density with random src/dst | 0/96 (killed density rival) | X-P2-SHAM |
| **material availability** | plant the 2-byte copy once per initial genome | 0/96 -> 32/96; carriers 0.76 -> 0.16 | X-P2-PLANT |
| **write authority** | ATOMIC write-back (a half changes only by an accepted copy) | runaway 1/80 -> 46/80 (7ae3); 1/120 vs 0/120 elsewhere | C-ATOMIC |
| **variation operator** | recombination splice off | runaway 0/150 -> 7/150 | C-RUNAWAY |
| variation | in-place mutation off | wins 6 -> 8/64 (p = 0.39), minor | X-DECAY |
| variation (search) | per-epoch in-place mutation in FREE physics | births 0 -> 87, none faithful; necessary under dense ops (15 -> 6) | X-NONPAIR-SEARCH; C-ABLATE |
| **locality / self-location** | free self-location | necessary (15 -> 1); implanted copier 0/36 -> 13/36 | C-SELFLOC; C-ABLATE |
| **energy** | half-energy transfer at birth | child replication 4/40 -> 20/40 | C-ENERGY |
| **reset / initialization** | STATELESS (fresh state every execution) | establishment 0.33 -> 0.81 (ffa6) | C-STATELESS-FFA6 |
| reset | ZERO vs CONST(0x5A) vs RANDOM vs CARRY | 26/48 vs 2/48 vs 3/48 vs 6/48 | C-ZERO-SPECIFIC |
| reset | reset on genome change only | 0.38 -> 0.43 (null) | X-DD-STATE-RESET |
| reset (withdrawal) | remove zero reset after establishment, abrupt vs gradual | persistence identical; robust share rises to ~0.93 | X-A3-WITHDRAW |
| **founder dose** | 4 founders vs 1 | depth >= 5 5/80 -> 41/80; independent-ticket model fits | C-CRITICAL-MASS; X-DOSE-CURVE |
| **selection / time gating** | answer gated on cue consumption, with VM cost vs free cue | competence 0.200 -> 0.000 with cost; 0.197 vs 0.197 free | C9-H1R |
| selection coupled to task (pair tape) | TASK_GATED interaction vs SHUF | not executed | X-TASK-GATE |
| **damage (ruler as intervention)** | scattered vs contiguous deletion | scattered more destructive at every fraction (.564/.761/.878 vs .463/.652/.795) | CW cycle 2-5 T-ARCH4/D1 |

---

## 7 Buried signals

- OBSERVED: **one spontaneous SELF-free donor** in X-DONOR-DISCOVERY (n = 1) turned out to be the dominant architecture (95.7% in
  the P2 corpus). The early n = 1 observation was right; the L1 ruler that required SELF was wrong. (W1R s1; P2S s4)
- OBSERVED: **X-P2-PLANT's planted instruction decays** (carriers ~210 -> <21 per 256), yet donors arise while it is common. This
  means copy material is not selected to persist before it becomes a donor. It is the basis of the carrier-exposure model and is
  otherwise unexplored. (A3S s1)
- OBSERVED: **neutral mutation walk reaches competence at about the soup's rate** (pilot ratio 1.75, p = 0.20). The full
  baseline, WP-9 (~9 CPU-h, portable), was never run. The seat says "no evidence yet that the soup helps FIRST APPEARANCE". This
  is the Knierim 2026 question, and it is parked. (A3S s8)
- OBSERVED: **"losing the copy instruction is a trap" (0/144 recovered)**; copiers sit on broad neutral networks (72-80% of
  1-step mutants stay competent); partial copiers become competent in one step 22-27% of the time. (F:495; A3S s1)
- OBSERVED: **only 6-11% of certified copies are exact**; the post-copy loss is child material (0.51 / 0.63). The copy-fidelity
  thread T-DC-5 is open. (A3S s3)
- OBSERVED: **9-15% of foreign runaway populations carry genomes competent where the founder is not** (X-ACQUIRE, lower bound).
  C-SWAP-ACQUIRE missed its rule by one event (9 vs 10). The descendant-acquires-competence reading is unconfirmed, not refuted. (F:363-367)
- OBSERVED: **side asymmetry**: 7ae3 copies only from tape side 1; P2 copiers are side-0-only in 1,052 of 1,154. The seat named it
  an open child and never ran it. (STATUS RESUME s3; P2S s1)
- OBSERVED: **X-H2-7AE3 depth ceiling**: mean depth ~1.4 -> ~2.6, "lineages stall at depth 1-4 regardless of dose". It was later
  explained by erosion, but only in 7ae3's cell. In the 13/15 specimens that never reach depth 5, the ceiling is unexplained
  beyond "donor copy competence 0.0". (G; F:335)
- OBSERVED: **the CW01 cycle-8 identity plateau**: the regime word is READ INTO A REGISTER that predicts the regime at accuracy 1.0,
  and it is NEVER USED. Information is present and not accessible to computation. This parallels "encoding accessibility, not
  presence" in a different substrate. (CW cycle 8 line 298)
- OBSERVED: **CW01 e07 raw retention DOUBLED under weather** (0.181 -> 0.359), while the frozen ability-adjusted ratio reads
  NEGATIVE because the normalizing margin is ~0.003 (CW01-D071). Both readings are on record and neither was promoted. (CW cycle 8 T-E07)
- OBSERVED: **CW01 e08 scalar burden 2-3x lower under tax** (1.725 -> 0.834 / 0.512), buried under NOT_VERIFIED competence counts. (CW e08)
- OBSERVED: **T-003 children: 29/29 have a dominant-byte share >= 0.75, and 27/29 are 0x36**. The NPE T-003 specimen is a painter
  ecology. Only 2 of 29 children later act as parents. (AR CVTR s2)
- OBSERVED: **Scope-limited pressure effect**: the +0.30 EXPLICIT_FITNESS effect is EXTERNAL-reproduction-only. Under
  PAIR_EXECUTION the TASK_GATED effect is d = -0.037 (32 pairs), and held >= 0.75 occurs in 2/45 runs. NPE has never had a
  task-coupled endogenous test. (F:60-64; XTG s1)
- PARKED: C-A3-WITHDRAW-ROBUST (declared, never run); WP-7 tape rotation (withdraw the self-location scaffold); T-STATE-2
  (route of internalization); e160 coverage of X-CORE; SI knockout + purifying-selection null (operator-gated); CW01 e10 PENDING.

---

## 8 Contradictions and cross-engine hooks

**Inside the group:**
1. "Presence is not the barrier" (W1: block-copy encodings in 87/96 plain pops) vs "presence suffices" (X-P2-PLANT 32/96).
   ATLAS_DERIVED: the two "presence" rulers differ. W1 counted occurrence anywhere; PLANT puts the copy in every initial genome.
   The seat's ARC3 resolution, carrier exposure (frequency x persistence), reconciles them. Neither W1 nor P2 retracts its number.
2. C-STATELESS-FFA6 ("ffa6-specific") vs X-P2-BRIDGE: with a fixed panel the effect is largest in 7ae3 (+0.25 vs +0.09). The seat
   withdrew "ffa6-specific" as low power (8 donor runs per arm in W1).
3. "Persistent register state is the barrier" (W1) vs C-ZERO-SPECIFIC (only ZERO rescues; CONST and RANDOM are worse than CARRY).
   The W1 reading is withdrawn.
4. C-CORE conserves OP_SELF as material in 7ae3 runaways, yet 95.7% of spontaneous competent copiers are SELF-free, and 33/52 SELF
   users still copy to a fixed destination. ATLAS_DERIVED: conserved OP_SELF in C-CORE need not be functioning as self-location.
   The 7ae3 route is atypical of the spontaneous route. Not tested.
5. X-SWAP-ORIGIN "NATIVE" -> reversed (X-ATOMIC-RANDOM, X-SWAP-ANCESTRY) -> re-qualified (X-CONTENT: lineage, not content). The
   net state: foreign runaways need the genome at the start, but carry 13-25% of its bytes.
6. C-CRITICAL-MASS "k=4 exceeds independent prediction, p = 1e-6" vs X-DOSE-CURVE LRT p = 0.42. Withdrawn (lesson D12).
7. The T-003 E003 route label: "INCONCLUSIVE by two independent frozen routes" vs the dated correction (the flip-floor route is
   SPEC_DEFECT under a strict reading; only R3 is clean). BRANCH:archaeon/attribution-arc-2026-09-28@056320b4c.

**Cross-engine (named in the text):**
- **Archaeon**: 265/265 random exact copiers environment-gated (XE-ENV-1); MATERIAL-only heredity ruler blind to execution state
  (XE-LENS-1); T-003 ancestry commission; Campaign 4 locality law (scattered > contiguous damage) ran inside CW01 (T-ARCH4). Archaeon
  lineages keep 0.0 founder material ("copy-core conservation is not a law", P2S s7).
- **Aphrodite** slice 4 = same experiment as the alias (accessible vs representable); T-XE-APH-1 carrier exposure.
- **Ananke** T-M3-1 evolved state-reset bootstrap = precedent for internalized register init.
- **Aether**: a hidden flag breaks a bytes-only causal predicate.
- **BEE**: first self-replicators are built by others' copying (XE-ENV-2). Archaeon's BEE dry run found a heritable parasite
  lineage (13%, #841).
- **Artemis / Odysseus**: P-11 unsound for heredity; CVT-R; Odysseus ranks NPE N5 (copiers set own registers) and N1 (X-ACQUIRE)
  among the three strongest Z80-family acquisition cases (#803).
- **Cosmos** C3 holdout D/D2 (custody only, below).
- Literature anchors used by the seat: Knierim 2026 (pair soup is not a better search than a random walk); Bourrat 2022
  (gradual withdrawal; not borne out); Tierra / Baugh 2015 (designed reproducers degrade to exploiting leftover registers);
  BFF (seeded takeover 22%).

**C3 holdout D / D2 custody (existence and status only):**
- D was sealed on 2026-09-25: commitment ae4479c6...57ac, commit a56ef7787, report #599. It was merged into main by 7c018d92b on
  09-28, so the original set is EXPOSED and "never to be used blind".
- D2 opaque successor at prometheus/cosmos/c3_holdout_D2/ (95b31a30d): AES-256-GCM ciphertext; key and salt on M1 only; Nestor is
  custodian.
- The D2 firewall passed at v13 after 12 FAIL re-audits (Odysseus; FIREWALL_AUDIT_1 anchored, entry_hash e1a2e48b).
- #1153 (09-30): "SEALED / UNREAD / UNSPENT". Blocked on the operator's COSMOS-C3 decision (WS blocked_on).
- One key-holder scan is outstanding (stopped for low memory; WS next_actions).

---

## 9 Five things a cross-engine synthesist must know about this group

1. **The replication count collapsed four rulers deep, and each ruler measured a different thing.** 1,031 "spontaneous
   replicators" (the donor wrote >= 25% of a half) became 57 once a causal criterion was applied. 910 were splice artefacts, since
   the detector read after the variation operator. Of the 57 P-11 constructions, about 2 are genuine self-copiers (17 painters, 37
   inert). Separately, 17-28% of the P-11-competent W1/P2 donors fail CVT-R heredity. NPE's standing rule is now "competent = P-11
   construction; heredity needs CVT-R or byte provenance". Any cross-engine table that counts "replicators" must name the ruler row
   by row. (F A-1, E-3, :510-522, :595-614)
2. **The barrier map is real, but every stage's mechanism reading was revised within 48 h, while the numbers stayed.**
   - Acquisition moved from "encoding accessibility" to "availability" to "carrier exposure (frequency x persistence)".
   - Establishment moved from "register persistence" to "loss of environment-supplied zero addressing that the copy itself
     destroys".
   - The confirmed numbers (1/64 -> 39/64; 11/33 -> 34/42; 26/48 vs 2/48) all still stand.
   - Treat NPE mechanism labels as provisional and the frozen counts as durable.
3. **NPE reproduction is mostly supplied by the environment.**
   - Zero reset plus tape offset 0 IS the self-location; 280/280 SELF-free copiers are tape-anchored.
   - Lineages internalize register initialization recurrently but rarely (C-A3-INTERNALIZE 8/144; material, XMI 8/8).
   - They almost never internalize placement (2/332 true locators).
   - This split, internalizable vs non-internalizable scaffolding, is the group's most portable claim. It directly matches
     Archaeon's 265/265 environment-gated copiers and Ananke's state-reset bootstrap.
4. **Pair-tape heredity has two barriers in series, both in world physics, and both confirmed in only one specimen's cell (7ae3).**
   - First, donor copy competence: 12/16 panel donors copy at 0.0 from a fresh state.
   - Second, tape-write erosion from write-back of both halves, ~25x the nominal mutation rate. Its generality across specimens is
     NOT confirmed (C2 1/120 vs 0/120).
   - Founders are independent ~13% lottery tickets, and the lottery is decided by cessation of copying within ~12 epochs, not by
     extinction.
   - Heredity does not equal task competence: NPE has never tested task-coupled endogenous reproduction (X-TASK-GATE is frozen and
     unexecuted), and the pressure effect is EXTERNAL-only.
5. **Rulers were themselves the dominant defect class, and the group documents the reusable lessons.**
   - Similarity is not copying.
   - Measure a copy where it happens, not after the variation operator.
   - Count-fixing damage rulers manufacture "length protects": 4 of 7 CW01 damage claims were lost under Bernoulli(f).
   - Single-point state rulers can cycle.
   - Identity-by-id is not heredity (C9-D14).
   - Identical arms are a defect signature (C9-D16).
   - Implant arms were unpaired by the RNG (C9-D24).
   - Three CW01 experiments (e07, e08, e09) closed "DESIGN UNREACHABLE": the organism or world could not express the tested
     capability, so the question was never posed. That is not a null.
   - The T-003 NPE ancestry leg was "uninformative by construction": 29 births against an R3 minimum of 30, with data-as-code loci
     undecidable by the flip test.
