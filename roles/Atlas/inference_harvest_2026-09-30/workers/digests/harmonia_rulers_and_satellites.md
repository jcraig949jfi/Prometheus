# Digest: harmonia_rulers_and_satellites

Reader: Atlas fresh-context reader, 2026-09-30. Repo: F:/Prometheus-worktrees/atlas-base-role @ 1da3130d3 (origin/main).
Layer tags: RAN / OBSERVED / CONCLUDED / ATLAS_DERIVED (ATLAS_DERIVED = my hypothesis, not a seat claim).
Pointer form: path (section or line) @ last-commit sha of that file, or comms #id.

---

## 0 Coverage

READ IN FULL or in the load-bearing parts:
- roles/Harmonia: all four AUDIT_*.md (instrument monoculture a6db26b1f; stall map 3e13f736c; detector band 7ad201fb3;
  number scope f2c2452ea); audits/ (EVIDENCE_AUDIT_2026-09-30 + SAMPLE2/3/4 d3f99cfdc; RULER_QUALITY_2026-09-30 d3f99cfdc);
  rulings/ RECORD_D2_GOVERNING_AUDIT_AND_SEAL_GATE (9cfa0bc13, Addenda A-R), RECORD_HARM55_HARM56 (646cbcda8),
  RULING_MECH_POET_NOVELTY_ESTIMATOR_001 (646cbcda8), RULING_IQ_NULL..., RULING_GAP_PROSPECTIVE_V1..., RULING_ASAL_LEGIT_SEARCH_001
  (2ead5e011, s0-s3), RULING_PROTEUS_CURRENT_INSTRUMENT (c387de555, s0-s1); STANDING_RULES.md (sections A-F, d3f99cfdc);
  VACUOUS_READINGS.md (f2c2452ea); STATUS.md head (f423a09ac, currency 09-25, stale vs journals); journals 2026-09-27 (c17d4c477)
  and 2026-09-29 (68c6e7f68); REVIEW_20260812_program_and_instrument_audit s2-s3 (583887f7c).
- Branch origin/harmonia/m2-475d761f-mwo1-2026-09-28 (tip 43ad5b853): **0 commits ahead of origin/main; fully merged.** No BRANCH-only material.
- programs/selective_irreversibility/: HYPOTHESIS, EXPERIMENTS, ANOMALIES, DISAGREEMENTS (full); comms #798 (Artemis SI attack).
- roles/Artemis: STATUS, selftest/RESULT.md, challenge/prospective/PREREG.md, challenge/p11/RESULT.md, selftest/runs/R-11/REPORT.md,
  dispatch/D002 + D004 RESULT.md; comms #793, #891, #1129-#1132.
- roles/Odysseus: expedition/EXPEDITION_1_REPORT.md, expedition/YIELD.md.
- roles/Nyx/STATUS.md (09-30 block); roles/Techne/WORK_STATE.json; roles/Vivarium/STATUS.md (currency 09-17).
- ops/fleet/UNOWNED.json, ops/fleet/CENSUS.json (both 7d373ac02, as of 2026-09-30T18:05Z).
- comms_since_0925.txt: grep only (Harmonia, P-11, SR criterion, pc < L, CVT, zero-parameter).

NOT READ (reasons): Harmonia rulings older than 09-17 except as cited by the audits (budget); qualification/, science/*.py code,
BOUNDARY_DEPTH packets, RESUME_20260925 (only via journal); older worker journals (Apr-Jun); SI memo/, FALSIFIERS, BLIND_LANES,
PORTFOLIO_MAP, SI probes; Artemis backlog/threads FR-001/FR-011 files themselves, CVT-R RESULT body, SI RESULT body beyond grep;
Odysseus recert/RESULT.md body, bacc/, census/ bodies, frontier/poi; Nyx nyx/atlas code and predictions JSONs; Techne fossil
records; Vivarium campaign6 lane beyond grep. Vivarium has no status newer than 09-17, so "the research queue" was not found as a
current artifact (SI EXPERIMENTS 2026-09-25T18:07Z records the Vivarium consumer NOT running on M2).

---

## 1 Experiment ledger (most recent first)

| # | id / date | question | substrate | ruler | controls | n | OBSERVED | CONCLUDED (author) | status | pointer |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Harmonia RULER_QUALITY 09-30 | are recent frozen verdict clauses reachable / discriminating? | Tyche dark-ecology v0; Hecate autopsy + alien-lawful | exact binomials, sims, frozen rule on committed baselines | HV re-verification | 3 prereg packages | Tyche H1: valid worlds 3 (P1,P2,P5) vs rule >=4 (P3 0.227, P4 0.109, P6 0.141 VOID); H3 neg arm passed 0/20 simulated random ecologies; Hecate rule passed by localtab baseline (AUC 0.844, pair 0.800) | "H1 and H6 ... UNREACHABLE_BY_DESIGN"; "The rule validates lawful-vs-noise discrimination, not novelty" (Harmonia m2-475d761f). C-1: own H4 rating wrong (K1 baseline 1.000 -> 0.547 -> 0.518) | confirmed (C-1 self-correction) | roles/Harmonia/audits/RULER_QUALITY_2026-09-30.md s1-s3, C-1 @d3f99cfdc |
| 2 | Harmonia EVIDENCE_AUDIT samples 1-4, 09-30 | do dispositions follow from frozen rules? | Hecate x3, Odysseus S3, Aphrodite A23, Ensorain T25, Ananke W-O/W-Q/W-Y, Bellerophon E-003, E-BEL-REPL-01, Aether E-010, Nestor X-MAT | re-execution + git ancestry | HV | 13 packages | E-003: VALIDATED needed post-exposure C4.2 (17 min after dry run); P2 lower bounds 0.456 / 0.407 >= 0.10 -> ALTERED; E-BEL-REPL-01 K3 0/93 | E-003 "NOT_SUPPORTED as labelled (BLOCKING)"; J downgraded to SUPPORTED_WITH_DEFECTS: "K3 had no demonstrated route to SURVIVES" | confirmed; owner errata filed | audits/EVIDENCE_AUDIT_2026-09-30*.md @adbf7fdb5/751026426/d3f99cfdc |
| 3 | HARM-55/56, 09-30 | is the ASAL crossing phenomenon an artifact of observer reconstruction (torch vs native Flax CLIP)? | 395 Lenia frames, CLIP ViT-B/32 | harm55_compare, harm56_map (frozen 68713424d) | torch cheat 16/16 (max diff 5.96e-7); native STATIC 0.8750002 | 333 compared | max abs err 4.77e-7, Spearman 1.0; 324 stable / 9 unresolved; C-SELF, C-STATIC fields null | "A_OBSERVER_STABLE ... says nothing new about whether the crossings are open-endedness" | confirmed (scope-limited) | rulings/RECORD_HARM55_HARM56... @646cbcda8 |
| 4 | MECH-POET-NOVELTY-ESTIMATOR-001, 09-30 | does POET's novelty.py have four structural properties? | poet_distributed/novelty.py @0b40743d | run_mech_poet_001.py (committed first, f76cc5e3b) | order-invariance, far-candidate, identical=0 all pass | 4 rows | I1 regime change 1.0; I2 range dominance 2.667; I3 absence=zero 0.0; I4 deflation 0 increases, 2.890 -> 0.236 | "CUT_SUPPORTED ... NOT CONFIRMATORY: every row was seen before the freeze and the payload is deterministic" | confirmed as code fact | rulings/RULING_MECH_POET... @646cbcda8 |
| 5 | Holdout D2 governing audit v2-v13, 09-29 | can the D2 firewall/order protocol pass? | prometheus/cosmos/c3_holdout_D2 | Odysseus audits + protocol status | self-tests | 12 audit rounds | v2-v12 FAIL; v13 PASS (FIREWALL_AUDIT_1 67e05df12); DEF-HARM-D2-001 SEAL gate unpassable on real history (3 merges) | Addendum Q: C3 rejected pre-holdout; "D2 is unspent ... a correct stop"; Addendum R: grep incident NO_INFORMATION | D2 SEALED/UNSPENT | rulings/RECORD_D2... @9cfa0bc13 |
| 6 | IQ-NULL + D001-07 ruling, 09-30 | admissibility | aporia/iq | prereg table vs code | - | 1 run; 572 tools | code adds N6, no PARK, 0 asserts; 57/572 = 0.0997 vs 57/560 = 0.1018 | "IQ-NULL stays INADMISSIBLE"; "INDETERMINATE_BY_RULE_GAP" | confirmed | rulings/RULING_IQ_NULL... (5702e9fa3 per log) |
| 7 | Artemis self-test (blinded yield test), 09-28 | does Artemis's sharpening raise research yield? | 19 S vs 19 B backlog threads | CONSEQUENTIAL category, blind scorers | seeded matched cohorts; sealed mapping | 36 executions, 17 pairs | S 1.000 vs B 0.882 (+0.118); sens. +0.059/+0.091; Brier B 0.470 vs const 0.391; 34/36 consequential | "sharpening NOT shown to add yield"; "the constraint is throughput and routing" (Artemis) | confirmed (ceiling-limited) | roles/Artemis/selftest/RESULT.md s1-s4 @781c11349 |
| 8 | Artemis R-11 gate census, 09-28 | how many silence-bearing gates were shown to fire? | 11 engines | hand census, codebook | 10-row second reader (47/50 agree) | 116 rows (94 absence-read) | never fired 37/94 (39.4%); same-substrate fire 12/94 (12.8%); curves 1, blind 0; C6 det 1-2 fire 3/12 and 0/12 at frozen thresholds | "only about 1 in 10 absence-reading gates has fired on an independent planted positive on the substrate it now judges" | confirmed (sample-scoped) | roles/Artemis/selftest/runs/R-11/REPORT.md s3 @e7b630113 |
| 9 | Artemis P-11 challenge, 09-28 | is NPE's P-11 a heredity certificate? | z8 VM, toy ISA, 57 natural survivors | P-11, FERT, LOCAL, CVT-1/2/R | 17-specimen panel with ground truth | 17 + 57 | P-11 accepts all 4 zero-bit painters (0.90-1.00), rejects 4 real copiers; Z1 20/20 vs Z3u96 0/20; fresh-state 6/57 recertify | "UNSOUND FOR HEREDITY"; "CVT-2 is the weakest adequate heredity certificate" | confirmed; Nestor accepted (#802) | roles/Artemis/challenge/p11/RESULT.md s3-s6 @2af325f7b |
| 10 | Artemis CVT-R on Nestor sets, 09-28 | do P-11-certified donors pass CVT-R? | Nestor donor sets a/b/c | CVT-R | prereg 77bc0dbce | 32 / 100 / 8 | 23/32, 83/100, 8/8; 19 P-11-certified fail (11 at gen 2) | "competent constructors whose children do not carry variation forward" | confirmed | comms #891; challenge/cvtr_nestor/RESULT.md @d050937ec |
| 11 | Artemis SI resource-model attack, 09-28 | is irreversibility required for predictive sufficiency? | unifilar sources on a register machine | exact causal states; erase/export meters | FX3/FX4 controls | 87 W=inf cells; 387 merging cells | reversible learner exact, zero erasure in all 87; premium ~12x/134x/2064x at 4/16/64 states; erasure forced only at W=1 bounded (7/7) | "Irreversibility is NOT required ... the cost moves into compute ... and into the environment's kept past" | confirmed within model | comms #798; roles/Artemis/challenge/si/RESULT.md l.82, l.123 @aabb22779 |
| 12 | Odysseus Expedition 1, 09-28 | competence acquisition, labels, accessibility | Z80/BEE/NPE/WSE/RBN | recert harness (24/24 known answers), bacc, census Q1-Q8 | cold-start worker | 64 census rows | NPE P-11 true of 3/57 (17 paint, 37 inert, 16 hand-set registers); BEE SR 1,414/1,425; B/G WSE 0.011, Z80 0.0011, RBN 0.30; 94% of Z80 neutral mutations hit never-executed bytes | "Three Z80 cases survive at R1~ ... all three are a lineage INTERNALISING something the world supplied" | exploratory | roles/Odysseus/expedition/EXPEDITION_1_REPORT.md s0-s5 @610e0e296 |
| 13 | Artemis D002/D004 frozen-analysis dispatch, 09-30 | re-run workers' frozen analyses | various | workers' own frozen rules | - | 11 + 6 tasks | accessibility rulers wrong direction on 2nd substrate; Proteus MDC 1e-4; FR-081 0/181 worlds can show ratio; FR-091 copy-primitive removal 8/300 vs 0/300; PROTEUS-46 cliff crossable by 5-edit neutral path | per-row frozen-rule outcomes | confirmed / undecided per row | dispatch/D002/RESULT.md @ae043e65f; D004/RESULT.md @0b0759dba |
| 14 | ENVGATE-02 (Archaeon, recorded by SI), 09-26 | window rescue model | Archaeon M2 | Phase-C gate | 24 blocks x 5 arms | 24 | cond 6 failed (P2 0+/2-, P3 1+/0-) | "WINDOW_NOT_SUPPORTED"; "NOT SI evidence" (Aporia) | falsified (window) | programs/selective_irreversibility/EXPERIMENTS.md 2026-09-26T08:00Z @61b970537 |
| 15 | C-CORE / X-CONTENT (Nestor, recorded by SI), 09-25 | what founder material persists? | NPE pair-tape | z8taint byte provenance | 64 fresh seeds | 27 runaways | anc share ~1.0 but 13-25% founder bytes; 17/27 meet endpoint vs 60% bar | Aporia: "NOT evidence for or against the law ... calling them relevant BECAUSE conserved is circular" | confirmed (thin margin) | SI EXPERIMENTS 2026-09-25T21:15Z |
| 16 | C-SWAP-ACQUIRE (Nestor), 09-25 | genome vs random implant acquisition | NPE | frozen count+p rule | RANDOM arm | 240/240 | 9 vs 0, Fisher p 0.0018 (bar p<0.001, diff>=8) | "NULL on the frozen rule ... not 'almost confirmed'" | null | SI EXPERIMENTS 2026-09-25T19:35Z |
| 17 | ASAL-LEGIT-SEARCH-001, 09-18 | does a legitimate ALIVE Lenia search cross below garbage? | Techne numpy Lenia port + torch CLIP | CLIP OE score | cheat 0.8303 garbage; blank 0.8749995 | 395 of 1,045 budgeted | I1 min 0.7665; best crosser METRIC_EXPLOIT; 105 crossers: 49 exploit / 47 unclassified / 9 genuine | "CUT_SUPPORTED on the boundary ... I0 PREDICTION_FAILED" (gandalf-6cd1348b) | confirmed; budget 38% | rulings/RULING_ASAL_LEGIT_SEARCH_001 s0-s3 @2ead5e011 |
| 18 | Detector-band audit, 08-19 | are Theseus nulls detector blindness? | 56 generators, 658,454,531 lifetime records | F2 content_aware_promote, verify() _DISPATCH, emission-path check | positive a1, cheat a3 both pass | 7,914 executed | representable 36.4%; _DISPATCH intersection 0; 99.98% self-verdicted | "The ceiling is at the emission side, not the detection side" (Harmonia D) | confirmed | AUDIT_20260819_detector_band.md s0-s5 @7ad201fb3 |
| 19 | Instrument monoculture, 06-22 | is "0 novel EC laws" exhaustion or ceiling? | EC void-miner | hypothesis_class_coverage_audit.py | hand-curated 16-law table | 16 laws | coverage 4/16; in-class found 2/2; out-of-class 0/12 | "a B2 result ... wearing B1 clothing" (Harmonia A) | confirmed structure; 25% "illustrative" | AUDIT_20260622_instrument_monoculture.md l.28-33 @a6db26b1f |

---

## 2 Mechanisms (seat's words; claimed vs judged evidence)

| Mechanism (seat wording) | Seat / pointer | Claimed level | Judged level (ATLAS_DERIVED) | Synonyms elsewhere |
|---|---|---|---|---|
| "expressiveness ceiling ... instrument monoculture of one hypothesis class" | Harmonia A, AUDIT_20260622 l.28-43 | confirmed on EC; program-wide = "hypothesis" | one strong datum + Apollo FP-003; program-wide never executed (generalised coverage diagnostic not found run) | FP-003; "class-relative exhaustion"; "shadows on the wall" |
| "the measurement carries its own answer inside itself" (one failure primitive at three altitudes) | REVIEW_20260812 s3 @583887f7c | working theory | recurs later: zero-parameter definition rule reproduces Cosmos C3 104/120 (#1112 area; RECORD_D2 Addendum Q); Hecate rule passed by lookup table | FP-001 "baseline costume"; R6 payload leak |
| "self-verdicting at emission" -- generator computes holds from values it wrote | AUDIT_20260819 s3.3 | measured 99.98% | strong (ledger arithmetic corroborates 0.023% unaccounted) | "no detector in the kill path" |
| "P-11 certifies construction, not heredity" | Artemis p11 RESULT s3; Nestor #802 accepted | preregistered panel | strong; three independent routes (Artemis panel, Odysseus recert 3/57, CVT-R 19 fails) | "painting", "self-painting", "construction-causality assay" |
| "silent, not latent, neutrality" / behavioural poverty | Odysseus EXPEDITION s0 item 6, s5 | NEW-MECHANISM? | exploratory spike; converges with Artemis FR-001 (YIELD Y03, Y24) | cryptic vs silent variation (Y37) |
| "copy-loop bytes ~2.4 decades each; world-reset pointer ~4.1 decades" | Odysseus s4 (BEE only) | estimator-based pilot | single substrate | Nestor npe-p2 "block-copy encoding accessibility" (#742); Artemis FR-011 |
| "internalisation of world-supplied scaffolding" | Odysseus s0 item 2, YIELD Y35 | R1~ survivors | 3 Z80 cases, controls partial | Nestor EXTERNAL_SCAFFOLDING, X-MAT ENDOGENOUS |
| "irreversibility as the W-bounded corner of a memory x compute x environmental-retention frontier" | Artemis #798 | within preregistered model | model-internal theorem-like result; no empirical substrate | SI s1 "selective irreversibility"; LM01 "retained exact records frontier" (ANOMALIES 09-26T02:49Z) |
| "selective advantage may be a claim about bias-structure MATCH" (generator sets winning arm) | Cyclops, SI ANOMALIES 09-26T01:29Z | dev finding, not a result | plausible confound; not tested | "GENERATOR_DEPENDENT" |
| "purifying selection on a functional core, with drift elsewhere" as the null for C-CORE | Aporia, SI EXPERIMENTS 21:15Z | null model proposed | unexecuted | - |
| POET novelty estimator: regime change at n=5, unnormalized range dominance, absence = zero presence, deflation | Harmonia POET ruling | executed structural identity | code fact only; consequence for open-endedness untested | Nyx MECH-POET-NOVELTY-ESTIMATOR EVIDENCE_SUPPORTED |
| ASAL OE score rewarded by "turbulence more cheaply than" coherent life | ASAL ruling s3 | reported, not adjudicated | strong enough to doubt every CLIP-OE claim | METRIC_EXPLOIT |

---

## 3 Failures and invalidations

| Failure | Kind | LOST (interpretation) | SURVIVES (raw observation) | Pointer |
|---|---|---|---|---|
| Theseus "a year of nulls" as detector blindness | wrong disjunction premise | blind-band / translator argument for the Theseus corpus | 367,214,821 kills sound within 33 claim kinds; 36.4% representable; 17.0% misrouted | AUDIT_20260819 s3, s5 |
| verify() never saw a Theseus record | ontology disjoint (5 vs 33 kinds, intersection 0) | any "verify() rejects unknown kinds -> nulls" argument | verify() unknown_kind fired 160/160 at R5/R7/R8 (08-12) in the reasoning ladder | AUDIT_20260819 s3.1 |
| sigma_kernel.PROMOTE never re-runs the kill battery | gate trusts caller-asserted survival | the falsification thesis "may be partially hollow at its center" | discovery_promotion.py manufactures CLEAR from unvalidated survival_evidence | AUDIT_20260622_stall s2 (re-execute audit prescribed; not found run) |
| R6 probe ships truth/cex in payload | answer leak | Icarus progress at R6 | R5 not broken; leak scoped to one tier | REVIEW_20260812 s2 |
| Tyche H1/H6 | unreachable PASS (3 valid < 4) | any FAIL reading of lens evolution | P1/P2/P5 SOLVED statuses; H2 + admission gate sound | RULER_QUALITY s1 |
| Harmonia's own H4 rating | reachability read at t=0 | "H4 is a sanity check" | K1 baseline 1.000 -> 0.547 -> 0.518; H4 FAIL attained | RULER_QUALITY C-1 |
| Hecate "zero UNFAMILIAR mechanisms" | detector never calibrated on UNFAMILIAR (0 items) | absence claim | 400 rows, detector sha 91fbe8f2, INDETERMINATE M1 | EVIDENCE_AUDIT B |
| Hecate W6 ORIG "not fired" | carrier implemented at unreadable r=0.2 only | PARK classification text | ALT levels r=0.65 LLE -0.919 ARI 1.0 -> KNOWN_ANALOGUE_FOUND | EVIDENCE_AUDIT A |
| "affine beats Claude" | mismatched subset/metric | the reversal | same 5 systems, t2_comp: Claude 0.512 vs affine 0.487 | EVIDENCE_AUDIT C |
| E-003 BEE VALIDATED | post-exposure route removal C4.2, undisclosed | VALIDATED as confirmatory | ALTERED pre-exposure; replay 32,827/32,827 bit-exact; Q8c 0.00115 [0.00098, 0.00134] | SAMPLE2 H + addendum |
| E-BEL-REPL-01 DISAPPEARS | K3 founder-snapshot ruler cannot reach SURVIVES; blinding leaked via merge incl. a Harmonia commit subject | "descent absent"; "chance-level" | K3 0/93; founder FM share ~0.01 by tick 500 in every arm; NPE descendants differ at 58-62 of 64 bytes; LCS median 2 vs null 1 | SAMPLE4 C-2 |
| P-11 as heredity certificate | over-permissive (painters) and over-strict (budget-limited copiers) | heredity reading of Nestor "competent" claims; X-PAIR-NORECOMB CLEAN_NULL (downgraded INVALID, comms #894) | 1,031 admissible / 57 surviving P-11 remain true of that instrument | p11 RESULT s3-s6; comms #891 |
| C-SWAP-ACQUIRE | frozen p bar not met | "confirmed" | 9/240 vs 0/240, p 0.0018 | SI EXPERIMENTS 19:35Z |
| PTE-C1 M3 packet ablation and routing null | vacuous by physics (delay = delta = 4; dest_mode "all") | C1 "no effect" null readings | positive components (drop_readout_tick_only kills) stay readable | SI ANOMALIES 23:45Z, 09-26T04:40Z |
| WTP-LM01 equivalence margin #691 | noise-derived margin makes noisy arms "equivalent" | tilt toward falsification | proposal delta = 0.3 AC (not binding) | SI DISAGREEMENTS 08:55Z, 09:35Z |
| ENVGATE-02 analyze.main() key bug | analysis-code defect (wrapper, disclosed) | - | frozen analyze.analyze() unchanged; WINDOW_NOT_SUPPORTED | SI EXPERIMENTS 09-26T08:00Z |
| D2 SEAL gate | --full-history counts benign merges | D2 readiness (temporarily) | ciphertext blob 10c7b600 unchanged; repaired (Addendum A) | RECORD_D2 s3 |
| gap_prospective_v1 seal | mapping inferable from public scores | blinding | adjudication proceeds with blinding ABSENT | RULING_GAP_PROSPECTIVE |
| IQ-NULL | table not a partition; code table differs | preregistered status | run is ADVANCE under both tables | RULING_IQ_NULL |
| ASAL budget | port refused 650/1,045 draws | extremal rows over the intended domain | 395 executed, 333 ALIVE | ASAL ruling header + A4 rule |

---

## 4 Rulers (main question: which rulers cannot observe their targets; which are shared)

### 4a Rulers that cannot observe (or could not observe) their target

| Ruler | Target it was read for | Why it cannot see it | Evidence | Pointer |
|---|---|---|---|---|
| EC void-miner (pairwise integer rel) | novel EC laws | hypothesis class covers 4/16 known structure; 6 blind axes | in-class 2/2, out 0/12 | AUDIT_20260622 l.28-55 |
| verify() _DISPATCH | Theseus claims | disjoint ontology (0 intersection) | 5 vs 33 kinds | AUDIT_20260819 s3.1 |
| F2 content_aware_promote | Theseus kills | observation mode only (daemon.py:432) | never gated | AUDIT_20260819 s4 |
| Proteus reversible reference | absence of current | "CANNOT FAIL (0.0 on a synthetic kernel too)" | max J 2.168e-19 | RULING_PROTEUS s1; AUDIT_20260918 row 2.168e-19 |
| Proteus occupancy TV | marginal shift | statistic 0.019747 on a quoted floor ~0.019 | V-008 | VACUOUS_READINGS V-008 |
| C3-2 success criterion | H2 via D3 | every acquired rule 0.000 on every IC (support 1, f 0.000) | STRUCTURALLY_VOID | VACUOUS V-001 |
| H1 relevance at 3 bits, K=4 | relevant vs random packs | 8 possible witnesses, pool < 2K | V-003 | VACUOUS V-003 |
| H5 reach readout | learned-encoding evolvability | at analytic bound; learned 11.7305 = random perm 11.72 | V-005 addendum | VACUOUS V-005 |
| particles claim (c) | scheme ordering of variance ratio | needs ~11,700 seeds/arm; 50-seed 0.51 vs 400-seed 1.16 conflict | V-007 | VACUOUS V-007; AUDIT_20260918 |
| D3 on live corpus | fires as findings | i.i.d.-calibrated nulls; 23/40 regions EXCHANGEABILITY_VIOLATED | V-006 | VACUOUS V-006 |
| Hecate gravity detector v1 | UNFAMILIAR mechanisms | 0 UNFAMILIAR calibration items | "zero UNFAMILIAR" | EVIDENCE_AUDIT B; RULER_QUALITY s3 R1 |
| Hecate NOVELTY_DETECTOR rule | novelty | passed by lookup-table baseline | AUC 0.844-0.852 | RULER_QUALITY s2 |
| Tyche H1 | lens evolution | PASS unreachable from fixed seeds | 3 valid < 4 | RULER_QUALITY s1 |
| Tyche H3 negative arm | planted residual shift | ecology size alone moves err 0.04-0.13 | 0/20 pass | RULER_QUALITY s1 (agent sim only, not HV) |
| Odysseus S3 quality clause | non-inferiority | ceiling (S3 10.0, control 9.1, margin 1) | could fail only < 8.1 | EVIDENCE_AUDIT D |
| K3 founder-snapshot (BEE) | descent | founder content turns over in every arm incl. ZERO | 0/93 | SAMPLE4 C-2; STANDING_RULES F8 |
| Kp[7] swap (Ananke W-Y) | carrier status | slot constant 0: swap is identity | structural | SAMPLE4 I |
| P-11 | heredity | certifies painters; C2 unreachable for bytewise copiers at 96-byte/slice 360 | Z1 20/20 vs Z3u96 0/20 | p11 RESULT s4 |
| BEE SR criterion (pc < L) | self-replication from self-copied code | measures code LOCATION not MATERIAL | r038751: 27,083 own / 21 foreign / 1,059 unresolved by material | comms #741 (Archaeon); R-11 s5 |
| Campaign 6 detectors 1-2 | population jumps | at frozen population thresholds fire 3/12 and 0/12 | 744/744 only at single-edit threshold | R-11 s3, s5 |
| Aether content-transport metric | content transport | failed its own positive control in the soup (fwd 3.1% vs bar 5%) yet clears 3 laws | R-11 s3 | R-11 REPORT |
| PTE-C1 packet ablation (M3) | timing-locked transport | window can never contain the current cue (delay = delta = 4) | VACUOUS | SI ANOMALIES 09-26T04:40Z |
| WTP-03 worlds for FR-081 | learning-time/lifetime ratio | 0/181 admitted worlds have lifetime <= 600 | UNDECIDED | D004 RESULT D004-09 |
| Accessibility rulers (foothold, d_flat, rho) | arm ranking on a 2nd substrate | wrong direction on stdlib proxy; valued only on Crius | .421 vs .437 etc. | D004-01; comms #1129 |
| PROTEUS-46 3-step cliff design | crossability | could not see a 5-edit neutral path | 4 neutral steps then 6/6 | D002-03q |
| D8 history-beyond-diversity | .05 effect | needs ~669 tasks; had 7/6 discordant | p = 1.0 | D002-09; UNOWNED U-03 |
| ASAL CLIP OE score | open-endedness | garbage frames score 0.8303 (cheat), turbulence cheaper than life; observer-stable (HARM-56) but validity unaddressed | 49/105 crossers METRIC_EXPLOIT | ASAL ruling s1-s3; HARM55/56 Admissibility |
| Artemis CONSEQUENTIAL outcome | sharpening yield | saturated at 34/36 | cannot detect 0.3 | selftest RESULT s2 |
| gap_prospective_v1 blind | method-blind adjudication | blind never effective | VOID_BY_CONSTRUCTION | RULING_GAP_PROSPECTIVE |

Program-wide census (OBSERVED, Artemis R-11): of 94 absence-read gates, 37 (39.4%) never shown to fire, 42 (44.7%) counting
failed-on-substrate positives, 58 (61.7%) no FLOOR, 12 (12.8%) fired on a same-substrate plant; among 57 with any positive,
56 are single analyst-known plants, 1 curve, 0 blind; substrate 13 same / 28 partial / 16 different. The August Harmonia figure
54.5% was a keyword proxy (R-11 s4-s5 @e7b630113).

### 4b Rulers shared across many experiments (non-independence) -- ATLAS_DERIVED unless marked

| Shared ruler | Experiments that depend on it | Known defect | Consequence for independence |
|---|---|---|---|
| NPE P-11 construction assay | Nestor S1-C (1,031 admissible / 57 survivors), C9/c9x verdicts, X-PAIR-NORECOMB, donor corpora (P2 q1, bridge, czs), "competent" labels in C-SWAP / X-DONOR lines (per #802, #891, R-11 row list) | construction != heredity; state-dependent (41/57 never pass fresh); cell-conditional (same genome 0.955 vs 0.0 in ten cells, R-11 s5) | every Nestor heredity claim shares one failure mode; Nestor accepted "competent donor claims are construction claims" (comms #894) |
| BEE SR / own-code criterion (pc < L) and BEE lineage/material labels | Bellerophon coupling campaign (11,657 runs), grounding round, E-003 BEE leg, E-BEL-REPL-01/02, Archaeon attribution v0 / TH-014, FR-091 re-derivation (D004-02), Odysseus recert of BEE SR | location-based; BEE 33% births UNRESOLVED for byte provenance (9,578,442 / 28,964,089; comms #1130) | E-003, REPL-01, attribution and FR-091 are one measurement family; the recount is "still open" (R-11 s5) |
| CLIP ViT-B/32 ASAL OE score (Techne numpy Lenia port = a DESCENDANT, B9) | ASAL-LEGIT-SEARCH-001, HARM-55/56, Nyx MECH-ASAL-OE-SCORE, Techne 39 capsules, planned full-domain replication | rewards drift/turbulence; Flax scorer omits self_check/static_control blocks (TECHNE-131 successor scorer pending) | observer-stability (torch = Flax to 4.8e-7) is the SAME model twice; it cannot separate artifact from phenomenon at the metric level |
| Claude-family model as author / executor / scorer / auditor | Artemis self-test executors and scorers ("same model family as Artemis", RESULT s3); Fabric S3/D00x workers (claude-opus-5-5, #1006); Hecate LLM gravity detector and Claude subject; Harmonia's "three independent audit agents"; Odysseus audit replicas | authorship-independence never tested: "These two hypotheses are currently observationally identical ... It cannot be closed at one author" (REVIEW_20260812 s3 item 3) | "independent" replication across seats may be one prior sampled many times |
| Theseus generators as their own verdict | 47 generators, 658M records | self-verdict at emission | kills are class-relative; no cross-check existed |
| "survive a gate -> promote" (sigma_kernel.PROMOTE) | NSGA-III, binary gate, tier ladder, bandit, kernel CLAIM (stall map s2) | never re-runs battery | "one selection principle" camouflaged as five |
| D3 band [1/3, 3] detector + i.i.d. calibration | C3-2, C3-3, live dossier, H2 lane | exchangeability violated in 23/40 regions | shared calibration population (12/5/23 is a fired-neighbourhood count, AUDIT_20260918 row 3) |
| Zero-parameter definition rule (Cosmos) | Cosmos C3 certificate classes | reproduces 104/120 (RECORD_D2 Addendum Q) | the coordinate restates the P2 definition -- ruler and target coincide |
| Fabric script executor + comms/evidence_wiki connection pool | every Fabric Task (D002: 3/11 timeouts lost all stdout); comms and EW | U-05 common-mode hang; U-08 F1-F4 | infrastructure failures correlate across seats' results (0-byte outputs) |

---

## 5 Repairs (what changed, did the outcome move)

| Repair | Before -> after | Outcome moved? | Pointer |
|---|---|---|---|
| Detector-band audit added emission-path check | 36.4% "blind-band SUPPORTED" -> blind-band FAILS | YES: the first version of the tool printed the opposite verdict | AUDIT_20260819 s7 |
| Cheat control a3 (predicate_kind) | naive cross-tab 44% representable -> 36.4% | YES (7.6 pp) | AUDIT_20260819 s2 |
| DEF-HARM-D2-001 SEAL rule (refuse merge only if blob differs) | SEAL unpassable -> PASS on real history | YES (gate) | RECORD_D2 s3, Addendum A |
| D2 v2 -> v13 (12 rounds; S1 resolved by MWO-0004 D2-1 anchor) | FAIL -> PASS | YES; then unused (C3 rejected) | RECORD_D2 Addenda B-Q |
| Adjudication-layer rule Addendum J (presumed exposure after `open`) | VOID option after exposure -> FORFEIT | closes optional stopping | RECORD_D2 Addendum J |
| HARM-56 input assembly (anchors merged) | VIEW 2 not computable -> A_OBSERVER_STABLE | YES (from UNRESOLVED) | RECORD_HARM55 deviation |
| Artemis P-11 panel repair (AMENDMENT b) | pre-repair Z2/TV-1/TV-2 failures -> all 17 pass | panel only | p11 RESULT s1 |
| P-11 -> CVT-2 / CVT-R companion certificate | 57 survivors -> 6 recertify; 19 certified fail CVT-R | YES for heredity reading | p11 RESULT s6; #891 |
| Odysseus accumulation v0 -> v0.1 (A8 "nest tag" cheat) | fooled -> re-gated 13/13 with three cheats | YES | EXPEDITION s0 item 8, s1 |
| WTP-LM01 R-c (same-optimizer reservoir refit) after D6 optimizer confound | L-R > S -> headline moved to reservoir curve | design changed before rows | SI EXPERIMENTS 09-26T02:49Z |
| PTE-C1b per-carrier resets after D-A/D-B | C1 M3 nulls -> VACUOUS | C1 labels unchanged by rule | SI ANOMALIES |
| C1 hostile adjudication HA-1.0.0 -> 1.0.1 (relabel set of 5) | 11/12 -> 12/12 caught | YES | journal 2026-09-29 tick 1 |
| Evolving-baseline amendment to F1 | H4 "sanity" -> real test | YES (Harmonia self-correction) | STANDING_RULES F1 AMENDED |
| E-003 errata | VALIDATED -> ALTERED confirmatory, verdict of record OPEN (operator) | YES | SAMPLE2 addendum; CENSUS operator_decisions |
| Artemis method change after self-test | full sharpening + priority labels -> stopped | process changed | selftest RESULT s4 |

---

## 6 Primitive-level interventions

| Primitive | Intervention | Outcome change | Pointer |
|---|---|---|---|
| heredity / copying | CVT-2/CVT-R single-byte parental perturbation over 2 generations | separates painters (TB2 0) from copiers (TB2 5.95-12.85) where P-11 could not | p11 RESULT s2 |
| copying (encoding) | remove copy primitive (ldir_off) in BEE | spontaneous SR 8/300 -> 0/300 | D004-02; UNOWNED U-04 |
| copying (encoding) | Z80 affordance ladder L0-L3t on BEE | 2.7e-5 -> 1.4e-5 -> 5.1e-9 -> impossible in 256 steps; generic write 2.1e-10; no reset pointer 1.7e-14 | EXPEDITION s4 |
| selection (scalar objective) | remove scalar objective in BEE | copy summaries change (99/100 pairs) but SR origin not (1 vs 1) | comms #1132 |
| memory / erasure | reversible vs irreversible learner, W sweep | irreversibility not required at W >= 2 or full replay; forced at W = 1 bounded | comms #798 |
| memory (retention budget) | BufferALS exact-record budget B | never-seen AC .2 / 1.2 / 2.0 / 2.6 at B 216 / 864 / 1728 / full | SI ANOMALIES 09-26T02:49Z (dev) |
| reset / initialization | PTE-C1b per-carrier resets (reset_En, flush sham) | defined; runs held | SI EXPERIMENTS 09-26T00:35Z |
| write authority / locality | pc < L vs material attribution | 27,083 of 28,163 location-foreign births are own-material | comms #741 |
| admission | P-11 fresh-state re-assay | 57 -> 6 recertify | p11 RESULT s6 |
| admission (custody) | D2 anchor + deliver receipts | protocol PASS; nothing run | RECORD_D2 |
| time / gating | ENVGATE-02 blocking the window | window-rescue model fails (cond 6) | SI EXPERIMENTS 09-26T08:00Z |
| error correction / observer | torch vs native Flax observer | no change (4.77e-7) | RECORD_HARM55 |

---

## 7 Buried signals

1. **A coherent living pattern crosses the ASAL garbage band.** 3G3an (coh 0.938) at 0.8122 in the raw catalogue, and S2_135
   GENUINE_DYNAMICAL_NOVELTY at 0.7933 below the 2-sd threshold; 9 GENUINE among 105 crossers. The headline "best crosser is a
   metric exploit" (I3) buries them (ASAL ruling s2-s3).
2. **Theseus 367M kills are sound, not blind** -- a positive statement buried under the "stall" narrative: class-relative
   falsification at 658M-record scale (AUDIT_20260819 s5).
3. **CAPABILITY space still emitted signal in June** (near-miss +11/+32 pp, co-solve +0.075 AUC, traces +0.16 transfer) while
   claim space was mined out (AUDIT_20260622_stall s2). Not revisited in anything I read.
4. **Apollo crossover**: 0/8000 single-step improving walks vs 6.1%/pair recombinant; `crossover_frac` default 0.0 (stall map
   s3b). The flag flip was prescribed; I found no record it was done.
5. **The prescribed re-execute-battery audit of PROMOTED symbols** ("the single most consequential check available", stall map
   s4 item 2) -- not found executed in this group's files.
6. **E-003 amendment-independent observation**: Q8c 0.00115 [0.00098, 0.00134] and P2 native-label disagreement 0.504 / 0.448
   survive the verdict dispute (SAMPLE2 H + addendum).
7. **E-BEL-REPL-01**: LCS median 2 vs random null 1 -- weak above-chance content continuity dropped when "chance-level" was
   withdrawn (SAMPLE4 C-2 item 3).
8. **CVT-R**: 19 P-11-certified genomes are "competent constructors whose children do not carry variation forward"; 11 fail at
   generation 2 -- a distinct phenotype (construction without transmissible variation), not just a ruler defect (#891).
9. **P-11 painting is not confined to BYTEWISE**: 3 of 4 recertified near-homopolymers are in BLOCK cells (p11 RESULT s6).
10. **Unowned findings** (ops/fleet/UNOWNED.json @7d373ac02): U-01 370/423 Gemini prompts never fired; U-03 D8 needs ~669
    tasks; U-04 copy primitive necessary for SR origin (no owner); U-07 NPE board_eligible accepts any non-empty cheat string.
11. **Artemis self-test side-finding**: a random harvested question with ~1-2 agent-hours produced a consequential finding
    ~9 times in 10 -- the backlog is defect-rich; throughput, not curation, binds (selftest RESULT s2-s3).
12. **Harmonia's own 06-22 "falsifiable next step"** -- run the coverage diagnostic on a3/knot miners, Apollo primitives, Icarus
    rungs -- never found executed; the program-wide monoculture claim remains a hypothesis by its author's own label.
13. **WTP-LM01 dev: both declared eviction policies lose to random** on the eviction positive-control world (SI EXPERIMENTS
    09-26T03:48Z) -- Odysseus Y04 lists "random eviction beats declared policies" as FALSIFIED-CLAIM (S2 reversed the delegate).
    Unreconciled (see s8).
14. **SI freeze never delivered.** HYPOTHESIS.md holds only the request (no frozen artifact); #603/#608 were held then CANCELED
    under MWO-0002 s2a (journal 09-29); Artemis #798 attacked the law "before the s12 freeze" that never happened.

---

## 8 Contradictions and cross-engine hooks

- **B1 vs B2 on EC** (ceiling vs exhaustion): resolved by scope, never by the prescribed test (add one real-valued invariant or
  one cross-object pairing). OPEN in practice (stall map s3a, s4 item 4).
- **Theseus nulls**: 06-22 monoculture audit says ceiling; 08-19 detector audit says emission-side ceiling, detection not binding.
  Consistent once "which side" is named; META_SYNTHESIS s5 fact (2) flagged stale (AUDIT_20260819 s8 item 5).
- **Random eviction** (see s7 item 13): SI dev finding vs Odysseus FALSIFIED-CLAIM Y04. Different worlds or stages; not reconciled in text read.
- **P-11 tier**: Nestor graph note "all tier L" vs R-11 claim "P-11 fires only at tier L" vs Nestor reply "fires at tier M, 4 of 57
  are tier M" (comms #894). Resolved by erratum; X-PAIR-NORECOMB downgraded INVALID.
- **Odysseus S1 vs recert**: "BEE's self-replicator label is unreliable" retracted as too broad (1,414/1,425 hold in grounding); the
  failure is specific to coupling-campaign control arms (EXPEDITION s0 item 7). Bears on Bellerophon's coupling analyses.
- **E-003 verdict of record** ALTERED vs VALIDATED-as-amended: OPEN with the operator (CENSUS operator_decisions).
- **Hooks to other engines named in the text**: Nestor (P-11, C-CORE, X-MAT, C-SWAP), Bellerophon/BEE (SR criterion, E-003,
  REPL-01/02), Archaeon (causal lens pc<L, TH-014 G2 hole, ENVGATE-02), Cosmos (C3 zero-parameter rule, D2), Hecate (gravity detector,
  novelty rule), Tyche (H1/H3/H4), Aether (content-transport metric fails its positive), Ananke (PTE-C1/C1b vacuous nulls, W-O/W-Q),
  Ensorain (LM01 margin, FR-081 blindness), Aphrodite (S4 conditions hard-coded True at run_s3s4.py L391/L420, per R-11 s5; positive arm
  identical to treatment), Proteus (MDC 1e-4), Apollo (crossover), Icarus (R6 leak).

---

## 9 Five things a cross-engine synthesist must know about this group

1. **The dominant failure is ruler-target mismatch, not missing effects.** Harmonia's rules F1-F8 (all dated 2026-09-30) each come
   from a verified case where the verdict was predetermined, unreachable, gameable or at ceiling; Artemis R-11 finds ~40% of
   absence-reading gates never fired and only ~11-13% fired on a same-substrate plant (0 blind, 1 curve). Treat every NULL,
   CLEAN_NULL, DISAPPEARS or "zero X" in other digests as UNRESOLVED unless a same-substrate positive fired.
2. **Several engines share one ruler, so their results are not independent**: P-11 (all Nestor heredity/competence), the BEE
   SR/lineage/material labels (Bellerophon, Archaeon, E-003, FR-091), the CLIP OE score (ASAL line, Nyx, Techne), and the Claude
   model family as author, executor, scorer and auditor. Count convergent evidence by ruler, not by seat (ATLAS_DERIVED).
3. **Heredity is the most contested primitive, and its rulers disagree.** P-11 certifies construction (painters pass), founder-snapshot
   K3 cannot reach SURVIVES under turnover, pc<L measures location not material, and CVT-2/CVT-R is the only ruler shown adequate on a
   ground-truth panel. Z80/BEE copy-primitive removal is the cleanest primitive-level effect (8/300 -> 0/300; ~2.4 decades per copy-loop byte).
4. **Observer-stability is not validity.** HARM-56 shows the ASAL phenomenon survives observer reconstruction; the ASAL ruling shows the
   score is won by turbulence (49/105 exploit) and even garbage (0.8303). Nine GENUINE crossers are the buried positive.
5. **Selective Irreversibility has no frozen hypothesis and its strongest test says "not required".** The s12 freeze was never
   delivered; Artemis's model shows exact prediction with zero erasure whenever the environment keeps its past (W >= 2 open), with
   cost moved to compute (12x-2064x). Nestor/Ananke/Ensorain results logged in the SI record are explicitly "NOT SI evidence" or
   circular (C-CORE), and two C1 nulls are vacuous by physics.
