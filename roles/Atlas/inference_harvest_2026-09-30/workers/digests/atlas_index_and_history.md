# Digest: atlas_index_and_history

Reader: fresh-context, read-only, 2026-09-30.
Scope: (a) Atlas's own structured layer plus the live `atlas` index, queried with SELECT only; (b) Prometheus history before about 2026-09-22.

Tags: every row carries one of **RAN**, **OBSERVED**, **CONCLUDED** (a seat's own words) or **ATLAS_DERIVED** (my inference, a hypothesis).

Pointer abbreviations:
- **DB** means a live read-only query of schema `atlas` on M1 on 2026-09-30.
- **AT** means `roles/Atlas/theory/*.jsonl` @f8df65681.
- **MODEL** means `roles/Atlas/MODEL.md` @f8df65681.
- **LEDGER** means `roles/Atlas/calibration/LEDGER.md` @4e0fb48cb.
- **REP26** means `roles/Atlas/reports/REPORT_2026-09-26.txt` @7190591f4.
- **RM25** means `roles/Atlas/reports/ROADMAP_2026-09-25.txt` @d5141caa9.
- **NF** means `roles/Nestor/FINDINGS.md` @19ef51610.
- **GW/** means `roles/Nestor/sidequests/graphworld/`, with these short names:
  - P1 to P7: `REVIEW_PACKET_ROUND{n}_*.txt`
  - G3: `ROUND3_G_METRIC_HARDENING_REPORT_2026-09-14.md`
  - SM4: `SMOKE_TEST_FINDINGS_R4_2026-09-15.md`
  - RR8 / RD8: `R8_RECOVERED_RESULTS.json` / `R8_DISPUTES.json`
- **C1R..C5R** means `archaeon/campaign{1..5}/CAMPAIGN_REPORT.md` (0728e9989, 4d80d4b1d, cb9135104, 8f1a82ced, cdb55e152).
- **CW** means `roles/Nestor/campaigns/cw01-2026-09-17/` (CAMPAIGN_STATE.json and DEFECTS.jsonl @3af735d67).
- **MEM** means `C:/Users/jcrai/.claude/projects/F--Prometheus/memory/<file>`.

Parts of (b) were read by three read-only sub-readers I launched:
- graphworld R1-R8;
- Archaeon C1-5, CW01 and Vivarium;
- Theophrastus, alien_circuitry, Nyx/Techne, evidence_wiki and the Harmonia pre-09-22 audits.

I carried their pointers over as they gave them and spot-checked only where they overlapped my own reads.

---

## 0 Coverage

### Read directly
- All of `roles/Atlas/theory/`. **COMBINATIONS.jsonl and EVIDENCE.jsonl do not exist.** Combinations live only in `atlas.combination`, and evidence only in `atlas.proposition_evidence` and inline in PROPOSITIONS.
- `roles/Atlas/{MODEL,STATUS}.md`, `calibration/LEDGER.md`, REPORT_2026-09-26 and ROADMAP_2026-09-25 (sections 5-7). The `proposals/` directory was listed only.
- Live DB tables: primitive, primitive_use, combination, proposition(+_evidence), blind_spot, signal, defect, experiment (class and disposition distributions), and fact name counts.
- NF in full. MEM: the index plus every `feedback_*` description (153 files) and about 12 project notes.

### Via sub-readers
- GW packets P1-P7, G3, SM4, RR8, RD8 and parts of the journals.
- C1R-C5R plus the C4-01 and C4-08 READOUTs.
- CW state, defects and boundary reports for cycles 2-8.
- Vivarium receipts.
- Theophrastus founding, round-2 and THEO-14 packets; alien_circuitry receipts; the Nyx and Techne journals 09-12 to 09-17; evidence_wiki integration JSONs and packets.
- Harmonia: AUDIT_20260918_number_scope, VACUOUS_READINGS, AUDIT_20260819_detector_band, AUDIT_20260622_instrument_monoculture, and the PARTICLES 001/002 and ASAL/ancestry packets.

### Not read
- Harmonia audits dated 2026-09-30 (out of window, deliberately excluded).
- SWARM_R*.md bodies, BOOT/BUILD files and R16 JSONs.
- CW01 CYCLE_REPORTs (up to 169 KB each) and EVIDENCE/TRAJECTORIES row detail.
- Per-slot RECORD files for Archaeon C1-C3.
- The Vivarium point_release directory.
- The live evidence_wiki DB (the service was not queried).
- No branch-only material turned up in this group:
  - `alien-circuitry/phase-ab-2026-09-12@93cdb3392` is tree-identical to main;
  - `mnemosyne/baserole-adopt@b219e2a88` is an ancestor of HEAD.

### Index state (OBSERVED, DB)
- 2,053 experiments, 221 defects, 192 OPEN signals.
- Newest modelled experiment activity is 2026-09-22 15:07 (-04:00).
- Last comb pass was 2026-09-26 (REP26 s4).
- **So the index sees almost nothing after 09-22.** Every index-derived statement below is a statement about pre-09-22 history.

### Echo facts (OBSERVED)
- The brief's roughly 300k `frontier.blocked_by_suppression` echo facts are **already pruned**:
  - today there is 1 fact with that name and 1,680 CONCLUDED facts in total (DB);
  - on 09-26 there were 301,671 CONCLUDED facts (REP26 s1).
- The Atlas commit d5141caa9 names the "frontier suppression-echo defect".

---

## 1 Experiment ledger (most informative, newest first; pre-09-22 unless marked)

| # | id / date | question | substrate | ruler / controls | n | OBSERVED | CONCLUDED (seat) | status | pointer |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Z80xAtlas 72 h, frozen 09-22 | spontaneous replication from random bytes | NPE Z80 pair-tape and other physics | ALLOC/BIRTH evidence gate; pair-tape "donor wrote >=25%" path | 23,471 runs | 1,031 admissible; all 1,031 PAIR_EXECUTION; chain depth 1 in 911 | "NARROWED, three times" | re-adjudicated: 57 under P-11, then only 2 true self-copiers | NF A-1, E-3, ARC3 qualification |
| 2 | Z80A matched pairs, 09-22 | factor effects | same | Hamming-1 pairs | 10,741 pairs | EXPLICIT vs NONE_IMPLICIT +0.3036 (513 pairs); PAIR vs EXTERNAL −0.1197 | "HOLDS"; scoped 09-29 to EXTERNAL reproduction only | confirmed (scoped) | NF A-2 |
| 3 | CW01 cycle 8, 09-19 | why answer-before-read plateaus | NPE e-worlds, tape genomes | exhaustive 1-edit census; witness seeding | 12,880 edits/genome; 2,000+2,000 grammar samples | 0 hits; 4-instruction XOR witness, every prefix scores 0.0; 1 witness among 95 fixes in 10/12 runs | "THE OBSTRUCTION IS TOPOLOGICAL, NOT METRIC" | confirmed; later re-described as cost of reading (C9-H1R I=+0.20, post-09-22) | MEM project_nestor_cw01_priority_loop; CW BR8 l.17-30 |
| 4 | CW01 P-G02/P-G08 ruler swap, 09-19 | do damage claims survive a fraction-fixing ruler? | CW01 genomes | scattered Bernoulli(f) vs fixed count; qualified first (P-G01, 25,200 draws, chi2 p .49) | 7 claims | 4 of 7 disappear; P-F06 6/6 → 0/6 | "every count-fixing ruler manufactures 'length protects'" | ruler invalidation | MEM feedback_count_fixing…; CW BR5 |
| 5 | T-ARCH4 tranche, 09-18 | locality of damage | Proteus VM (Archaeon C4 frozen runtime) | scattered vs contiguous deletion at matched k | 6 runs | scattered loses more at every fraction (.564/.761/.878 vs .463/.652/.795); in cycle 2, mostly dose (+.145/doubling) plus small locality (+.024) | "Locality law" | confirmed then narrowed | CW BR-A4 l.44-51, BR2 l.35-40 |
| 6 | CW01 e07/e08/e09, 09-18 | brain damage; rank tax; algorithmic soup | NPE worlds; TT organism | pre-QUALIFY gates; frozen min-count rules | e08: 4 lineages per tax level; e09: 0/64 competent | e07 gate refused twice (P1 attainable only at f ≥ .44); e08 burden fell 2-3x under tax; e09 ceiling 142.5 < abstain 159.0 | INCONCLUSIVE / "DESIGN UNREACHABLE" | inconclusive (design) | CW DEF D058, D066, D068; shas 397dad9a2, 10ece30ba, 7e17bacc8 |
| 7 | Archaeon C5, 09-18 | does representation B / deep neutral walk / fair ecology unlock discovery? | Proteus VM, 57 parents | CRN, world screen (9/25 eligible) | 96 cells (C5-09) | 0 held-out gains in 96 cells; C5-02 0/24 improved; "elite IS the starting parent after 36,000 evaluations" | "BOUNDARY_CREATED_NO_DISCOVERY_GAIN — ACCEPTED" | negative | C5R l.4-7, 60-143 |
| 8 | Archaeon C4-01 / C5-05, 09-18 | damage geometry | Proteus VM | D-class census; identity and randomize controls | 5,472 edits (C4); 5,586 (C5 replication) | D7=0; displacement bimodal, 1-3% of edits in between; D6 exaptive 34 (30 on shelf parents) | "a cliff in behaviour, not a slope" | confirmed, with denominator caveat (§4) | C4-01 READOUT S1-S7; C5R |
| 9 | Archaeon C4-08 → C5-08, 09-18 | what makes robustness | Proteus VM | length bins; dead-code ablation | — | loss .419 → .125 while length went 19.1 → 62.5; dead-code ablation only .435 → .409 | C4: "ROBUST_WITHOUT_MECHANISM… neutrality+length"; C5-08: "MIXED, length carries it" | interpretation superseded | `archaeon/campaign4/SUPERSESSION_2026-09-18.md` |
| 10 | Archaeon C3, 09-17 | why W2_K2 plateaus at half credit | Proteus VM | full-solve telemetry; strategy-signature probe | 24x300 generations; 4,800 children | 0 summits; shelf elites are "one-value memory" (6/12 first-PUT, 4/12 last-PUT); 0/480 greedy paths reach 0.9 | "half-credit shelf… one-value memory" | confirmed | C3R l.120-141; defect L3-006 |
| 11 | Archaeon C3-SFE-10, 09-17 | does import takeover reflect capability? | Proteus VM | permuted incompetent imports | 228 runs | mature 12/12; permuted 11-12/12; no import 0/12 | "mechanics, not capability" | confirmed (kills an earlier reading) | C3R l.288-307 |
| 12 | Archaeon C3-SFE-03 ladder, 09-17 | delay corridor | Proteus VM | direct search | 12 seeds | 11/12 delay-general; held-out d8/d16 1.0 vs direct 0/6, 1/6 | WEAK_POSITIVE (5/12 were standing variation) | weak positive | C3R l.147-161 |
| 13 | Archaeon C2 attack on C1 positives, 09-17 | are SFE-01 and SFE-07 real? | Proteus VM | shuffled, opcode-only and length-matched controls | 10-12 | +0.009 and +0.002; shuffled controls beat intact | killed | falsified | C2R l.155-178 |
| 14 | GW R7 Clause B E-R7-1, 09-16 | does a graft transfer? | wforge w14→w13, TT | sham + scratch, EVIDENCE_N_v1 | CANDIDATE_N | graft−scratch +0.738 (p .046); graft−sham −0.662; sham−scratch +1.400 | FAIL, "negative in a useful way" | falsified | GW/P7:122-132, 175 |
| 15 | GW R5-R7 B-R5-1, 09-15/16 | 16-byte int4a4 compression survives the floor | w13 train128 | progress-above-floor; 32 runs / 4 families / 8 | 32 runs | progress 1.591 [1.139, 1.827]; LOO 4/4 but leave-out-4200 CI low 0.9964; 3/32 below floor, all in family 3303 | "NOT promoted… still a CANDIDATE" | inconclusive (thin) | GW/P5:84-106, P6:110-121 |
| 16 | GW R3 floors, 09-14 | are R2 parity passes real? | wforge w1-w4 | trivial-policy floors | 28 cells | a zero-byte abstain policy beats every held64 baseline (w4 107.75 vs 98.76) | "The search, not only the world, was weak" | invalidates R2 | GW/G3:13-20 |
| 17 | GW R4 R16 screen → R8 Route B, 09-15/17 | which worlds admit compression? | 74 cells, then 232 new worlds | progress ≥0.95 | 74 cells | only w13 t128 SURVIVED; 4 PENDING → SURVIVAL_IMPOSSIBLE; w8000036 SURVIVED (replication never consumed) | R8 "UNRECEIPTED … OBSERVATIONS" | open | GW/P4:241-256; RR8 |
| 18 | Theophrastus founding/round 2, 09-13/14 | contrast-first ecology loop | SFE CA density | CONTRAST with z ≥ 4 both passes; 10 cheats | 46 executions; 21 rows | 23 REPRODUCIBLE, of which 14 are positive controls; exp's published score = a constant classifier's | "LOOP_REAL…YES"; "SIGNALS_ARE_DISCOVERIES… no"; SPEC-001 MARGIN_RESPONSE | confirmed (instrument) | `roles/Theophrastus/REVIEW_PACKET_FOUNDING…:17-22`, ROUND2:17-23 |
| 19 | alien_circuitry AC-01D-v2, 09-13 | is T_7 D(f,t) an alien structure? | T_7 transformation monoid | orbit table; label-permutation control | 25,382 orbits | HC_D 0.998 | "STRONG POSITIVE… retires the C5 result" (C5 was a symbol-bound approximation) | confirmed (deflationary) | `AC01D_V2_RECEIPT.md:5-20` |
| 20 | ASAL-LEGIT-SEARCH-001, 09-18 | do legit ASAL searches cross? | Lenia/ASAL fossil | frozen class thresholds | 395/1,045 rollouts executed | 105 crossers: 49 metric exploit, 47 unclassified, 9 genuine | I0 PREDICTION_FAILED; best crosser a METRIC_EXPLOIT | partial | Harmonia ASAL packet:97-125 |
| 21 | Archaeon seasons S1-S7 / ARCH-46A, 09-12/13 | can fossil inference improve a producer? | exact toy worlds | preregistered | 5,463 audited decisions | S1-S4 no advantage; S7 GATE_FAILS_TO_ISOLATE on one float tie at 2e-15; ARCH-46A exact rational → LICENSED_ENDGAME_REPAIR | as stated | confirmed after repair | MEM project_archaeon_seat |
| 22 | Vivarium queue, 09-05 to 09-18 | infrastructure | SFE/Vivarium | — | 1,155 rows | 579 completed, 79 failed, 492 cancelled (246 test contamination) | — | infrastructure only; Archaeon C1-5 never ran on the queue | `roles/Vivarium/receipts/CONSUMER_DEATH_2026-09-14_M1_REBOOT.md` l.17 |

---

## 2 Mechanisms

For each mechanism: the seat's words (CONCLUDED), the evidence level it claims, my judgement of the actual level, and synonyms other engines may use.

- **"Copying is not heredity"**
  - Atlas proposition P-copy-not-heredity, MODERATE (AT).
  - Claimed evidence: Z80A-D05, where the splice made the match in 6,287 of 6,547 events.
  - My judgement: STRONG and repeated. It was reinforced after 09-22: 57 P-11 donors → 2 true copiers, 17 painters, 37 inert (NF ARC3 qualification), and CVT-R rejected 17-28% of "competent" genomes (NF QUALIFICATION).
  - Synonyms: construction vs heredity; P-11 vs CVT-R; similarity vs copying; "painters".
- **Accessibility cliff / topological obstruction**
  - CW01 cycle 8 (#3); C4-01 bimodal displacement (#8); P-accessibility-cliffs, MODERATE.
  - My judgement: MODERATE. The "cliff" holds for per-edit displacement but not for loss against radius: C4-02's preregistered cliff predicate reads NO, largest step .170 (C4-01/C4-02 readouts via sub-reader).
  - Synonyms: moat, valley, encoding topology, answer-before-read, DESIGN UNREACHABLE.
- **Flat elite / selection without search**
  - C5-02 (#7); P-selection-not-search, MODERATE. A frontier idea (LIN-ffc7ae5d) says it may be an N=50 artefact.
  - My judgement: MODERATE. The same shape appears as NPE E-1: non-pair physics never varied because mutation was gated behind birth (NF E-1).
  - Synonyms: stasis, TEMPORAL_STASIS, no pre-birth variation, bootstrap barrier.
- **One-value memory shelf**
  - Archaeon C3 (#10). Claimed as confirmed; I judge MODERATE-HIGH.
  - Synonyms: half-credit shelf, partial-credit plateau, rung-boundary cliff.
- **Import takeover is mechanics**
  - C3-SFE-10 (#11). Claimed confirmed; I judge HIGH (a strong control killed the capability reading).
  - Synonyms: injection dose, write authority over the population.
- **Robustness comes from length**
  - C5-08 supersedes the C4 reading of neutrality/dead code (#9).
  - Cross-engine tie: CW01 D084 shows fixed-count rulers manufacture "length protects". ATLAS_DERIVED: part of the SFE length effect may share this ruler geometry (see §8).
- **Locality law**
  - Scattered deletion beats contiguous (#5), later narrowed to mostly dose. Synonyms: damage geometry, clustered vs distributed lesions.
- **Measurement before mechanism**
  - P-measurement-before-mechanism, STRONG (AT). This is the only STRONG proposition.
  - My judgement: STRONG. It is the most repeated finding in this whole group; see §9.
- **Self-verdicting at emission**
  - Harmonia: "99.98% of the substrate's 658M lifetime records were verdicted by the generator that authored them" (`roles/Harmonia/AUDIT_20260819_detector_band.md:21-22`).
  - Synonyms: same-model verification, which every GW packet discloses (P1:69-70).

---

## 3 Failures and invalidations (LOST vs SURVIVES)

| failure | what was LOST | what SURVIVES (raw observation) | pointer |
|---|---|---|---|
| Similarity detector (90% byte identity) | the campaign's top flag SPONTANEOUS_REPLICATOR | `births_similar_no_write` rate as a world property | MEM feedback_similarity_is_not_copying |
| Z80A-D05: fidelity read after `_mutate` | about 88% of 1,031 "replicators" | 57 P-11 events, of which 26 rest on one event passing 2 of 3 draws | NF E-3, E-5, R-05 |
| C9-D14: pair-tape identity is not heredity | the H3 certificate | id-to-genome identity decay: 0.97 → 0.00 by epoch 600 | NF E-5 |
| C9-D16: H1 gate never passed to the task | all of C9 H1 (four arms were identical) | rerun C9-H1R: I=+0.20 | NF E-9 |
| C9-D24 / D17: RANDOM_MATCHED == in situ | paired reasoning in H2, C-SWAP-ACQUIRE and X-ATOMIC-RANDOM | the unpaired counts; no verdict changed | NF D24 |
| CW01 D084 / P-G08 fixed-count ruler | 4 of 7 damage claims | operand softness (−.19 over 124 pairs) and operand-slot order a>b>c | CW BR5 |
| CW01 D071, ill-conditioned retention ratio | P-B03 NEGATIVE | raw retention was higher (0.359 vs 0.181) | CW DEF l.72 |
| CW01 D089, in-sample lookup | "the register reads the regime" | overwriting the register changes 0% of answers | MEM cw01 loop |
| Archaeon C1 SFE-01 and SFE-07 | both positives | frozen rows; the controls were harness-seeded (L2-011, L2-029) | C2R l.166-178 |
| C2 CA "localized readout" | its value as a mechanism signature | k50=1 and the 0.58 margin (a hand rule is equally localized) | C3-SFE-09 |
| C2 basin rho −0.59 | the causal knob (C3 found a pooled two-strata artefact) | 1 of 4 within-stratum cells replicates | C3R; L3-029 |
| C5-03 representation B | preregistered status (a01 PREREG_FAILED; statistic changed post hoc) | the site-TVD of .785 | C5R l.85-90 |
| GW R2 8-byte parity | all 28 Clause A passes (abstain floor) | the int4 → int2 compression path | GW/G3:13-20; P2:210-212 |
| GW R4 16 B/36 B claims | invalidated by the top-16 readout | under a top-1 re-read, 1.121 / 1.283 | GW/P4:304-306, 435-438 |
| GW C7 charge-index bug (29/36 worlds) | the C7d reading; plasticity line closed | C7e: the affine learner detects 73/130 switches | GW/P1:225-228 |
| GW D1 metered channel | learner viability ("silence" trap, recurred 3 times) | Lua = numpy settlement; 13/13 cheats caught | GW/P1:262-265; P7:194-198 |
| GW C1 CPU bounty (1.43x) | the claim (retracted) | CPU beats GPU 125-666x at batch 1 | GW/P1:210-215 |
| E GPU "reversal" (34 ms) | the claim | warm copy 5.13 ms; the original compared unlike estimators | GW/P5:147-149; MEM feedback_ratio_of_unlike_estimators |
| Hephaestus gauntlet `bool()` coercion | a would-be SEARCH_ROUTING verdict (the true answer was the opposite) | the defects list | MEM feedback_frozen_instrument_is_not_validated |
| Vivarium phase-2 | 48 rows (fix landed 4 h 47 m after the consumer started), 24 C3-hist rows, 246 contaminated rows | 119 orphans classified | MEM feedback_deployed_is_not_live; `RV/ledgers/ORPHAN_VERDICTS_2026-09-11.json` |
| Techne harvest.run in-place builds | preservation claims for 23 of 57 bodies | the outputs; restore gave 57/57 | `roles/Techne/journal/2026-09-12.md:36-69` |
| evidence_wiki V1 | "metabolization differential": all 16 arms scored 4/4 (saturated) | none as evidence | `REVIEW_PACKET_V1.txt:88,185-193` |
| Atlas policy/1 | the prioritiser (novelty was 0.000 for all 46 proposals) | the weights, carried into policy/2 | LEDGER 2026-09-24 |

---

## 4 Rulers

| ruler | can see | cannot see / audit | pointer |
|---|---|---|---|
| Atlas primitive axis rules (axis_rules/1) | presence of a primitive in an engine's CATALOGUE axes | **anything experiment-specific.** Every experiment-level `primitive_use` row is "inherited from <engine> via campaign" (DB evidence column). There are 0 experiment rows for broadcast_state, copy_mechanism, partial_observability, environmental_feedback, mutable_interpreter and operator_composability, and 0 rows anywhere for the 5 UNMEASURED primitives. Vivarium's 1,242 experiments have no primitive_use at all. | DB |
| atlas_class POSITIVE | the reported disposition word | PASS on infrastructure (kernel crossover, VRAM budget, FalkorDB config) is counted the same as a science PASS. 649 of 723 POSITIVE rows are Vivarium queue "completed" jobs. | DB class x engine; GW r1 rows |
| Comb R01-R13 | recurrence over indexed facts | R02, R03 and R13 key on the bare name "effect" (8 full names across 5 campaigns). An earlier pass read schema fields as effects (14/14; LEDGER 09-19). | REP26 s7 |
| policy/2 score | proposal ranking | `gain` = 1.00 for 13 of the top 15 proposals (RM25 s5): saturation moved from novelty (policy/1) to gain. ATLAS_DERIVED. | RM25 |
| NPE P-11 causal copy | a causal rebuild of the victim half | does not perturb the donor, so painters pass; construction ≠ heredity | NF ARC3 |
| NPE pair-tape "donor wrote ≥25%" | overwrite events | copying vs splice (Z80A-D05) | NF A-1 |
| NPE founder causal depth | unbroken certified chains | capped at about 1/p by a 5-16% break rate | NF X-CERT-BREAK |
| NPE self-state ruler (rate after 1 own execution) | a one-point snapshot | register state that cycles (copies after 0, 2 and 5 executions, fails after 1, 3 and 4) | NF ARC3 RULER DEFECT |
| CW01 fixed-count damage | — | manufactures "length protects" (D084) | CW DEF l.85 |
| CW01 relative loss (s0−sd)/s0 | — | explodes near a zero baseline (D086, mean −2.66) | CW DEF |
| SFE C4-01 D-classes | per-edit displacement | D2 inherits parent degeneracy (99.8% of gen0_random children). The "D7=0 in 5,472" figure uses a denominator in which 606 edits could not apply (applied edits sum to 4,866; the sub-reader's arithmetic) | C4-01 READOUT S1, S3 |
| SFE foothold at 0.5 | footholds | hid the half-credit shelf until C2 | C2R l.375-377 |
| GW held64 median + 0.5xIQR | parity | saturated by do-nothing (abstain); the IQR moves 2x with the RNG family | GW/G3; P2:259-262 |
| GW top-16 readout | — | moves the progress scale about 1.4x (w13 denominator 14.68 to 23.06) | GW/SM4:187; P4:327-331 |
| GW trace-hash oracle | cheat detection | catches 79.7% of fix_unaffordable; the fitness gate passes a wrong world in 30/40 | GW/P1:172-175; P2:255-258 |
| GW planted nulls (C) | — | "cannot PASS by construction", so a failing null proves nothing | GW finals_r8/H.json |
| Theophrastus admission gate | contrasts | no prior-evidence notion: 14 of 23 "signals" are controls | FOUNDING:162-163 |
| alien_circuitry HC_D | orbit navigation | denominator C_K roughly doubles under an arbitrary tie-break (196.3 vs 88.6) | `RESULTS_C_B.md:60-81` |
| Harmonia ancestry ruler | edges | P1 and P3 VACUOUS; D2 .spop loses 100% of extinct branches; 25% id corruption drops anc_recall to 0.105 | ASAL packet:129-150 |
| Harmonia void-miner | in-class laws | expresses 4/16 known EC structure; out-of-class laws 0/12 | AUDIT_20260622:28-55 |
| Detector-band tool | — | printed "SUPPORTED" at 36.4% | AUDIT_20260819:262-267 |

---

## 5 Repairs (did the outcome move?)

- **Moved:**
  - SFE C1 → C2 machinery (reachability table, CRN, typed states): incapable assays 3 → 0, and both C1 positives died.
  - GW R3 floors: 28 PASSes → BELOW_FLOOR.
  - GW 32/4/8 sample + top-1 readout: w13 was invalidated, then re-won at progress 1.591.
  - CW01 Bernoulli ruler: 4/7 claims gone.
  - NPE C9-D16 rerun: INVALID → COST_INTERACTION_ONLY.
  - NPE atomic write-back: runaways 1/80 → 46/80 (post-09-22, NF C-ATOMIC).
  - Archaeon ARCH-46A exact rational: GATE_FAILS → LICENSED.
  - Atlas policy/1 → /2 (novelty variance restored), though gain saturated instead.
- **Did not move:**
  - C4-01 resume (byte-identical tables).
  - C5-09 a02 (same numbers).
  - CW01 e06 (invasion direction reversed, verdict unchanged).
  - e07 correction (state dependence .03 → .09, gate still refused).
  - GW B2 compiled rollout (746 h → 3-7 h, still never screened).
  - GW R16 full screen (w13 still the only survivor).
  - GW anti-prior calibration across R5-R8: still unvalidated, 4/4 undiscriminating in R7.
- **Pattern (CONCLUDED, Archaeon C3R l.408-412):** "an instrument gated on a fixed constant rather than on the measured state of its own space."

---

## 6 Primitive-level interventions

### Atlas's 20 primitives (OBSERVED, AT and DB)

**AXIS_RULE (15):** local_state, broadcast_state, partial_observability, self_location, copy_mechanism, resource_coupling, selection_pressure, memory_persistence, communication_topology, environmental_feedback, competition, niche_separation, operator_composability, environment_generation, mutable_interpreter.

**UNMEASURED (5):**

| primitive | stated reason (AT) |
|---|---|
| partial_heredity | "no indexed source records offspring-parent similarity as a continuous quantity" |
| write_authority | "write permissions live in substrate specs and code" |
| temporal_gating | "a property of the interpreter" |
| reproductive_closure | "requires an ablation … that no indexed experiment reports" |
| error_correction | "needs a measured fidelity and a channel baseline" |

All five say "Needs ATLAS-39".

### primitive_use counts (DB)

- Experiment rows: local_state 751, selection_pressure 751, environment_generation 580, memory_persistence 211, niche_separation 211, communication_topology 158, competition 118, resource_coupling 118, self_location 53.
- Everything else appears only on catalogued external ecosystems.

### Combinations by outcome (DB)

Method: POSITIVE+WEAK_POSITIVE vs NEGATIVE+NULL+FAILED over experiments that carry any primitive_use.

- **POS n=90:**
  - 69 = {communication_topology, environment_generation, local_state, memory_persistence, niche_separation, selection_pressure}, i.e. NPE graphworld;
  - 17 = {local_state, memory_persistence, niche_separation, selection_pressure, self_location}, i.e. SFE;
  - 4 = {competition, local_state, resource_coupling, selection_pressure}, i.e. CW01.
- **NEG n=90:** the same three tuples, 66 / 20 / 4.
- Every pair count is within ±3 between the two groups.
- **ATLAS_DERIVED:** the combination signal is **null by construction.** Primitive use is inherited per engine, so a "combination" is an engine label, and outcome-by-combination only restates each engine's outcome mix. The index currently cannot answer "which primitive combinations predict success". Doing so needs experiment-level primitive tagging (ATLAS-39).
- `atlas.combination` (DB), 190 pairs:
  - 89 TESTED (by co-presence in any entity, including external ecosystems);
  - 85 UNEXPLORED;
  - 16 SUGGESTED_BY_EVIDENCE.
  - The highest interest scores (1.3) go to copy_mechanism×partial_heredity, partial_heredity×temporal_gating and environmental_feedback×error_correction. Each involves at least one UNMEASURED primitive.

### Interventions recorded in history (OBSERVED; see §1 and §3 for pointers)

| primitive | interventions and effect |
|---|---|
| **Heredity/copying** | Fragment, organ and component transfer (SFE C1-C2): null, and kill arms beat the treatments. Whole mature solvers carry a sub-solution to the shelf, never the summit. Recombination: 0 crossings (C4-06); in CW01 the splice acted as mutation. NPE: the splice manufactures apparent replicators AND prevents runaway heredity (splice off: 7/150 vs 0/150). |
| **Write authority** | Imports take over within 2-8 generations whatever their competence (C3-SFE-10). Pair-tape write-back erosion runs at about 25x the nominal mutation rate; atomic write-back → heredity (NF, post-09-22). |
| **Memory/state** | Summit needs a two-value keyed memory (C3). CW01 persist=none .72 → .03 (D085). |
| **Encoding** | Balanced encoding is 9x slower despite more accessible variation (C1-SFE-06). An NPE 1-byte alias for copy ops: 0/47 → 13/40 spontaneous replication (NF E-8). Representation B: 0 gain in 96 cells. |
| **Temporal gating** | Mutation only at birth → non-pair physics never varied (907/907 zero births, NF E-1). The answer gate abolishes competence only when reading costs (C9-H1R). |
| **Selection** | CW01: selection is not the obstruction (1 witness fixes 10/12). C5 flat elite. |
| **Admission/gating** | C5 world screen (9/25 eligible) after C4-09 had 3/4 worlds pre-solved. CW01 pre-QUALIFY gates refused e06 and e07. |
| **Energy** | NPE newborn starvation: a half-energy transfer at birth gives 20/40 vs 4/40 (NF E-7). CW01 length price shrank genomes 44 → 5-6 instructions at unchanged reward. |
| **Locality** | Scattered > contiguous damage (#5); opcode edits 2.3x more lethal than operand edits. |
| **Self-location** | Necessary for faithful copying (NF E-6, E-8 ablation 15 → 1). |
| **Error correction / closure** | No intervention recorded in the index (UNMEASURED). |

---

## 7 Buried signals (observation kept apart from its fate)

1. **R06 "null with rich telemetry"** flags 33 NEGATIVE, NULL or INCONCLUSIVE experiments with 30-102 observed measurements each (DB signal). Examples: C3-SFE-10 has 102, C3-SFE-07 94, CW01 e05 80. None has been mined.
2. **R04 attempt disagreement** in 17 SFE experiments. 10 of those 17 (9 of the 15 in C2-C3, plus C5-09) had at least one POSITIVE_CONTROL_FAILED attempt before a CAPABLE_NEGATIVE or WEAK_POSITIVE of record. The final dispositions rest on the attempt after an instrument repair (DB signal R04).
3. **Two-value organisms** under all-or-nothing credit (5/12 at 0.438-0.646, C3-SFE-08) were never followed as a stepping stone to the summit.
4. **The shelf is the only productive stratum**: 30 of 34 D6 exaptive edits and C4-02's only traversable cell (C4-01 READOUT).
5. **W2_K2 stream solving rare cells** by direct reuse: W1_d4 0.96, W1_d16 0.92 (C2 L2-032).
6. **The GW NK line is unaffected by the abstain floor:**
   - a 132-byte target-blind policy beats a fixed bitset on 64 unseen landscapes 8/8 (+3.4%) (GW/P2:242-245);
   - R8 NK corruption +5.5% held (MWU p .0035, post hoc) (RD8).
   - Neither was revisited.
7. **Sham beats scratch.** GW R7 sham−scratch +1.400; R8 scale-only arm +2.10 [1.19, 2.98]. This suggests an initialisation-scale effect masquerading as transfer (GW/P7:127; `replay_r8/E-R8-H1.json`).
8. **w8000036** SURVIVED under 4 variants; its replication trigger fired and was never consumed (RR8).
9. **Operator bundling in the code learner:** split moves escape 10/10 vs 0/10 (GW/P2:252-254). This is an operator-composability datum the index has no rule for.
10. **CW01 transients:**
    - a new surface in world C at generation 75, "archived, not followed";
    - unselected XOR machinery decays .80 → .52 in 60 generations;
    - e08 TAX+AMP had the highest capability (171.2) at the lowest burden (0.512) and was never promoted (sub-reader, CW BR7, P-J03).
11. **Opcode-level recovery (C5):** REAL_LOCAL_RECOVERY is almost all v0.4 grammar under interpreter B (219 vs 123). B's own grammar is net negative (15 vs 34). ATLAS_DERIVED from C5R l.113-114.
12. **ASAL:** 5/152 catalogued lifeforms already cross "garbage" with their published parameters, and one is coherent (0.94) (ASAL packet:111-113).
13. **THEO-14:** only 24/150 bench rows are informative. The same all-zero C3-2 corpus made Harmonia V-001 structurally void, so two seats hit it independently.
14. **NYX-44 c04:** PENDING ruling since 09-15, no trace after 09-17, apparently orphaned.
15. **evidence_wiki:**
    - s7 scores skipped gates as pass (I3, X1);
    - no engine anchor has ever been verified;
    - 0/12,858 encounters carry `ecology`.
16. **Vivarium:** the engine lifetime tally is FALSIFIED 592 / SURVIVED 395, yet all 27 rows completed on 09-11 scored SURVIVED (the S1 rule scored everything SURVIVED).

---

## 8 Contradictions and cross-engine hooks

1. **Length vs robustness across engines.**
   - SFE C4-08/C5-08: robustness is carried by length (.17 → .71 across length bins).
   - NPE CW01 D084/P-G08: fixed-count damage rulers manufacture "length protects".
   - Has the SFE damage census (C4-01, C5-05, C5-08) been re-run under a fraction-fixing ruler? Not found. **Open.**
2. **"Cliff" wording.** C4R headline: "a cliff in behaviour". C4-02 preregistered cliff predicate: NO. P-accessibility-cliffs cites the headline. Bears on NPE's cycle-8 "valley".
3. **C4-07 vs C4-08 label.** The SUPERSESSION note and the Atlas conclusion row say C4-07. The content being superseded is C4-08's robustness reading. INFERENCE by the sub-reader; P-task-competence-not-mechanism's evidence row inherits the label.
4. **Delay invariance vs forced-read.** SFE C3 found delay-general elites appear at the first delay rung. NPE A-3 found ANSWER_BEFORE_READ favoured in both independent pair sets. Both engines report that competence arises without reading the late cue, and neither seat cites the other.
5. **Recombination.**
   - SFE C4-06: splice −.08 viability, 0 crossings.
   - CW01 P-I04: splice = mutation.
   - NPE: the splice both fakes replicators and suppresses runaway heredity.
   - Three engines, one operator, three readings. **Cross-engine hook.**
6. **Import/injection takeover (SFE C3) vs founder establishment (NPE C-CRITICAL-MASS / X-DOSE-CURVE)** are the same dose-vs-capability question; the lottery model in NPE fitted with p=0.13. **Hook.**
7. **Proposition evidence is one-sided.** 10 propositions have 7 evidence rows in total and **zero CONTRADICTS rows** (DB). MODERATE confidence for P-copy-not-heredity rests on one SHARPENS row.
8. **Atlas vs index.** STATUS says there are 4,099 primitive_use rows; DB has 4,249. REP26 CONCLUDED facts 301,671 vs DB 1,680 today. These are pruning and harvest drift, not contradictions, but any quoted counts must be dated.
9. **Tally drift.**
   - CW01: CAMPAIGN_STATE says 28 science defects, DEFECTS.jsonl has 26 (DB also 26).
   - C1: severities 15/14/3 in the report vs 13/16/3 in the ledger.
   - evidence_wiki: campaign_release 16/16 vs STATUS 15/15.

---

## 9 Five things a cross-engine synthesist must know about this group

1. **The Atlas index cannot yet test primitive combinations.** Experiment-level primitive_use is inherited from the engine's catalogue axes. POS and NEG groups carry identical tuples: 90 vs 90, the same three engine signatures (DB). The 5 primitives the propositions care most about (partial_heredity, write_authority, temporal_gating, reproductive_closure, error_correction) are UNMEASURED. Treat any "combination X predicts success" from the index as void until ATLAS-39 tags experiments individually. atlas_class POSITIVE also mixes infrastructure PASS with science.
2. **The index stops at 2026-09-22.** Nothing after it is modelled: the NPE W1/P2/ARC3 confirmations, CVT-R and the Artemis/Odysseus requalifications are absent. The propositions' confidence bases pre-date those qualifications.
3. **The dominant historical result is negative for discovery and positive for instrument repair.**
   - SFE C1-C5: 0 supported discovery positives across 5 campaigns; C5 "NO_DISCOVERY_GAIN".
   - CW01: 9 attempted, 2 COMPLETE.
   - GW: 1 surviving world out of 74, and 0 promoted claims over 8 rounds.
   - Most reversals were ruler, control or design defects, not substrate facts (P-measurement-before-mechanism, STRONG).
4. **Heredity claims need a heredity ruler.** Across NPE the chain went similarity → donor-wrote-bytes → P-11 construction → CVT-R. Each step removed most earlier "replicators": 1,031 → 57 → 2 genuine copiers.
5. **Recurring failure TYPES across history.** Counts are lower bounds from the sources read; the grouping is ATLAS_DERIVED. The MEM `feedback_*` files date each type.

| # | failure type | count (≥) | examples (date) |
|---|---|---|---|
| F1 | Target/gate/threshold not shown attainable before freezing | 20 | MEM gate_must_be_shown_reachable (08-23), preregistered_rules_need_an_eligibility_count (3 in 4 days, 09-04); SFE C1 L-014/L-017/L-028, C2 and C3 POSITIVE_CONTROL_FAILED (4 + 2), C4-09 pre-solved worlds, C5-03 PREREG_FAILED; CW01 D058, D066, e06/e07/e09 DESIGN UNREACHABLE; GW E2 ≤5% bar unattainable, AP-04 cannot bind on w13; ASAL I0 band; particles-001 positive band |
| F2 | Guard/control that cannot fail, or vacuous PASS | 25 | MEM guard_that_cannot_fire (09-18), controls_must_gate_on_transport (08-19); CW01 D043, D034 ("third time in four experiments"); GW about 8 vacuous PASSes plus 4/4 undiscriminating anti-prior cells (R7) plus close_sweep `checks_run: 0`; C3 L3-034; Nyx P-a5 `all()` over empty; Harmonia V-001…V-008 (8); evidence_wiki skip = pass; float32 tolerance 1e-9 |
| F3 | Ruler geometry manufactures the effect (ill-conditioned, fixed-count, pooled, wrong summary) | 15 | CW01 D071, D084, D086, D088, D089, D090; C3 L3-029 (pooled rho), L3-037 (median of bimodal), L3-030; GW held64/abstain floor, top-16 readout, 0.5xIQR; MEM count_fixing_damage_rulers (09-19), onpolicy_score_conflates (08-27), se_on_the_wrong_unit (57x, 08-24) |
| F4 | Detector measures resemblance or construction, not causation/heredity | 6 | 90% byte identity (09-19); Z80A-D05 splice; P-11 painters; C9-D14 id vs bytes; founder causal depth vs break rate; MEM similarity_is_not_copying |
| F5 | Arms not draw-matched / seed confounds | 12 | SFE L-008 (twice), L-030, L2-011, L2-028; CW01 D010, D019, D076, D083; NPE C9-D24/D17; MEM census_seed_must_not_index_the_target (09-13), replicate_seeds |
| F6 | Intervention not delivered to the measurement (arms identical) | 5 | NPE C9-D16; CW01 D009 (re_entries=0), D038a; SFE INTERVENTION_NOT_APPLIED ×4 (C2); C1 L-007 inert tabu |
| F7 | Small-n / one-draw bars / unlike estimators | 10 | GW R1 1-4 seeds, IQR 2x by family, w13 13.6% of draws, one-draw bars killed C3b and C7c; SFE C1 "seed noise at n=3 is the size of the effects"; MEM ratio_of_unlike_estimators (09-15), slow_baseline_is_a_remeasure_signal (09-14), gate_must_exceed_measurement_error |
| F8 | Claim sourced from a summary / scope inflation / tally drift | 12 | NF R-01..R-04 (sign inversion etc.); Harmonia HARM-32, 3 of 17 numbers out of scope; CW01 D049, D051, D078; MEM three_claim_inflations (08-25), wrong_population_statistics (4, 08-21/23), verification_must_be_aimed_at_the_claim (8 in one day, 09-10), ai_to_ai_inflation |
| F9 | Frozen or preserved instrument not validated in the new domain | 6 | Hephaestus bool() gauntlet (09-11); MD5 LP64 (09-13); avida submodules; GZIP line 667 vs 672; ASAL port refused 650/1,045; ancestry ruler tie-break on ids |
| F10 | Operations corrupt the record (deployed ≠ live, rebase-orphaned SHA, stash, heredoc/backtick, test writes to prod) | 20 | GW rebase-orphaned SHAs ×6; Vivarium 48 + 24 + 246 rows; CW01 D020, D036 (5 shell-escaping failures), D057; MEM feedback on backticks (2 of 12 gate checks deleted, 09-16), git_stash, deployed_is_not_live (09-10), committed_sha_orphaned (08-31), gate_commits_on_tool_exit (09-14), stale_prior_round_worker (09-15) |
| F11 | Same-path verification / self-verdicting | pervasive | every GW packet; Harmonia 99.98% of 658M records self-verdicted; MEM promotion_requires_independent_failure_mode (08-25), neutrality_gate_can_be_tautological (08-27) |
| F12 | Scoring or prioritisation layer lacks variance | 3 | Atlas policy/1 novelty 0.000 ×46; horizons emitted identical directives; policy/2 gain 1.00 ×13 of top 15 (ATLAS_DERIVED) |

These twelve types recur on every engine in this group. In most reversals a detector or gate was trusted before anyone asked what input would make it fire (or fail) when the phenomenon is absent.
