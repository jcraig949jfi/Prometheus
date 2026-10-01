# A1: Defect-discovery episodes in Prometheus, 2026-08-20 to 2026-09-30

Question: is Prometheus getting better at catching its own errors, and who catches them?

Sources: `gitlog.tsv` (non-merge commits on main, attributed by subject prefix or touched paths), `comms_messages.json` (1198 messages, 09-11 to 09-30), the repo at origin/main 38e323c0c (`roles/Aphrodite/engine/AMENDMENT_*`, `roles/Harmonia/STANDING_RULES.md` s.F, `roles/Harmonia/audits/*2026-09-30*`, `ops/threads/TH-021.md`).

Scope and method: a keyword sweep produced about 550 git subjects since 08-15 and 111 comms subjects. I read them and kept 92 episodes, each with a commit, message id or file:line I checked. Where one commit records a batch of defects, I counted it as one episode. The main case is Ensorain's LM01 D1 to D11: I kept D4, D6, D8 and D11 and folded the rest in. Each counted episode is a decision that a piece of work, an instrument or a verdict was wrong. A defect that was disclosed in advance and designed around is not an episode. Neither is a gate that worked as intended, for example Aphrodite A12 S1_FAIL.

Codes:
- class: RULER = ruler/metric/instrument; GATE = gate or decision-rule logic (vacuous, unreachable, constant, decided by construction); LEAK = data leakage/holdout/custody; BASELINE = missing or contaminated control or baseline; STAT = statistics or count error; INFRA = infrastructure; PROV = provenance/state/freeze/exposure; CONFOUND = design confound.
- discoverer: SELF-S = same session; SELF-L = same seat, later session or later cycle; OTHER = another seat, a sibling instance, or Fabric reviewer workers (these are Claude workers dispatched by a seat); OPER = operator; AUTO = a test, fixture, control or self-check that fired; EXT = external model. No EXT case in the 09-11 to 09-30 window was well enough evidenced to code.
- stage: DESIGN = pre-run design; SCREEN = pre-run fixture, dry run or audit; POSTRUN = after the run, before the report; POSTREPORT = after the report or comms claim; POSTMERGE = after it was on main, accepted, or used downstream.
- periods: P0 = 08-20 to 09-10, git only, a sparse baseline sample of 7. P1 = 09-11 to 09-19. P2 = 09-21 to 09-27. P3 = 09-28 to 09-30. There are no comms on 09-20 or 09-22.
- unc column: `disc` means the discoverer coding is uncertain; `lat` means the latency is a guess.

## Episode table

| id | date | per | owner seat | class | discoverer | stage | latency | consequence | recurrence of | evidence | unc | defect |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D01 | 08-20 | P0 | Harmonia | STAT | SELF-L | POSTREPORT | ~hours (P9->P10) | claim REFUTED: sampling manufactured a false positive | - | 64bba4111 |  | Soak P10: P9's claim refuted; sampling made a false positive in P4 |
| D02 | 08-21 | P0 | Ergon | CONFOUND | SELF-L | POSTREPORT | unknown | P1 KILLED as truncation-confounded; gate had been flattered | - | 959165882; a7d9bb2d8 |  | Truncation defect flattered the leveling gate |
| D03 | 08-21 | P0 | Aporia | STAT | SELF-L | POSTREPORT | unknown | P63 4.6-bit headline RETRACTED; honest number is the null | - | 6d0a76641 |  | P63 information-gain story retracted |
| D04 | 08-31 | P0 | Harmonia | STAT | SELF-L | POSTREPORT | unknown | action-divergence excess WITHDRAWN | D01 (stat, same seat) | 1be87a0fe |  | Published a chance floor that was actually a ceiling |
| D05 | 08-31 | P0 | Techne | RULER | SELF-L | POSTREPORT | ~1 cycle | hole proposals blocked; 43 cells re-classified | - | fa84da2e4; b100162ba |  | Cartography hole count was measuring Techne's own tagger (3.3% classification) |
| D06 | 09-03 | P0 | Lexis | STAT | OTHER | POSTREPORT | unknown | HC-T01 verdict downgraded; wider-literature claim withdrawn | - | 62f7a1a1e; a22792dc6 | disc | Kill condition scored with the wrong statistic; premise obsolete |
| D07 | 09-05 | P0 | Harmonia | STAT | SELF-L | POSTREPORT | unknown | SE-1b RETRACTED (winner's curse: best of 12 draws) | D01, D04 (stat, same seat, 3rd time) | 28d58afbb |  | Surviving claim was the highest of twelve draws |
| D08 | 09-11 | P1 | Hephaestus | RULER | SELF-S | POSTRUN | same session | 5 instrument defects corrected before any verdict | - | comms #28 |  | Specimen 3: five instrument defects caught before readout |
| D09 | 09-11 | P1 | base-role (shared) | PROV | OTHER | POSTMERGE | days (unknown) | journals/results re-included in .gitignore; fixed centrally | - | comms #71; 2b79c140a; dcafe3047 |  | Ignored-output defect: five seats (Atalanta, Eos, Coeus, Clymene, Hermes) found it independently |
| D10 | 09-11 | P1 | Lexis | PROV | OTHER | POSTREPORT | same day | 13 manifest rows re-hashed; calibration row | - | 8600edd68 (per Diomedes f08c81c66) |  | Archaeon manifest report: all 13 rows CRLF-hashed, not blob-hashed |
| D11 | 09-11 | P1 | Techne | RULER | OTHER | POSTREPORT | unknown | MOSEK struck; Elenchus METHOD-FLAW, invalidates-claim | - | 1912d823e; d3ce43c24 |  | TECHNE-38 fixture badly posed (ill-conditioned case) |
| D12 | 09-11 | P1 | Hermes | PROV | OTHER | POSTREPORT | unknown | claim corrected; calibration row 10 | - | b026db8cc; comms #108 |  | Asserted agora tables 'not fed' from a label, without measuring |
| D13 | 09-11 | P1 | Nous/PipelineOrchestrator | STAT | OTHER | POSTMERGE | months (est.) | reported to an unbooted owner; NOT fixed | - | comms #85 (Coeus) | lat | nous.py: 11/16 concepts at 2.5x sampling weight rest on n<=5 |
| D14 | 09-11 | P1 | Nyx | STAT | SELF-L | POSTREPORT | ~1 day | scope claim in #190/#191 corrected | - | comms #198 |  | pass_to_descendant zero calls is strategy-wide, not the discriminator |
| D15 | 09-14 | P1 | Nestor (lane C) | RULER | OTHER | POSTRUN | unknown | C7 correction rows + journal retractions | - | d1f73fc3c; fe8616884 |  | Charge-column indexing bug in C7 harness, found by sibling lane B |
| D16 | 09-14 | P1 | Nestor (lane B) | BASELINE | OTHER | POSTREPORT | hours | C1 bounty RETRACTED (1.43x was vs pessimistic baseline; recheck 0.93-1.01) | - | cc1699b0e; db523bfac; 04ee00aa6 |  | Speedup claimed against a pessimistic baseline |
| D17 | 09-16 | P1 | Nestor (R8) | RULER | SELF-S | SCREEN | same session | checker and C3 probe rewritten behavioural | - | e5aa8d269; 6c02b89a9 |  | Own gate checker was wrong; C3 probe was grepping for its own defect |
| D18 | 09-16 | P1 | Nestor-H | GATE | SELF-S | POSTRUN | same session | MDD80 rule read VACUOUS; disclosed | - | f81464458; da7582650 |  | Preregistered MDD80 rule vacuous because of its own grid defect |
| D19 | 09-16 | P1 | Techne | PROV | AUTO | POSTMERGE | days | 11 DRIFT bodies classified as RECORD defects | D10 (CRLF hashing) | 6434fbb65 |  | M2 rematerialize census: 11 drifts all CRLF/record defects |
| D20 | 09-17 | P1 | Daedalus | INFRA | SELF-S | POSTREPORT | hours (#345->#347) | own mechanism falsified; SFE 9.0.1 repair | - | comms #347; 3e8893a8c |  | No-reader control showed the real cause: new SQLite connection per request |
| D21 | 09-17 | P1 | Vivarium | INFRA | SELF-S | POSTRUN | same day | 4xx classifier fixed with tests; unparked | - | comms #355 |  | Misclassified a correct 409 as ENGINE_TRANSPORT and paged Daedalus |
| D22 | 09-17 | P1 | Nyx | RULER | OTHER | POSTREPORT | unknown | recurrence reading retracted from ASAL packet plan | - | comms #384; 5beb6bff3 |  | Techne: CLIP open-endedness score ranks garbage above living Lenia |
| D23 | 09-18 | P1 | Archaeon | RULER | AUTO | POSTRUN | same run | C5-09 a01 INSTRUMENT_INVALID; numbers preserved; control fixed for a02 | - | 0b0a75d5d |  | Determinism control compared volatile wall_s |
| D24 | 09-18 | P1 | Bellerophon | GATE | AUTO | SCREEN | same night | suite strengthened (3/20 plausible wrong implementations survived) | - | 958e8be8e |  | Mutation ledger: test suite too weak to kill 3 of 20 wrong implementations |
| D25 | 09-18 | P1 | Aporia | PROV | OTHER | POSTREPORT | ~1 d to find; 5 d to withdraw | E3 WITHDRAWN; audit headline 5->4 errors | - | comms #421, #548; d1d877b39 |  | RSI audit E3 wrong (DGM is ICLR 2026), found by Aphrodite |
| D26 | 09-19 | P1 | Nestor (CW01) | RULER | SELF-L | POSTREPORT | ~1 cycle | 4 of 7 fixed-count claims attributed to the ruler | - | 8a01ddede; ce97fbcc4 |  | Damage ruler dilution: length-robustness was a ruler artefact |
| D27 | 09-21 | P2 | Aphrodite | CONFOUND | SELF-L | POSTREPORT | ~1 slice | label kept ADVERSARIAL with dated correction | - | roles/Aphrodite/engine/AMENDMENT_3_2026-09-21.md:11 |  | Slice-2 true solution (depth 4) was never in the depth-3 search space |
| D28 | 09-21 | P2 | Aphrodite | INFRA | SELF-L | POSTRUN | unknown | cap removed as instrument repair (ruled not a parameter change) | - | AMENDMENT_5_2026-09-21.md:17 | disc | Hidden HELPER_CANDIDATE_CAP truncated the declared search space |
| D29 | 09-22 | P2 | Aphrodite | BASELINE | SELF-S | DESIGN | 0 (before any arm) | run both controls, report both | - | AMENDMENT_7_ADDENDUM_1_2026-09-22.md:10; 341ad9f38 |  | SCRATCH control contained the fold space: the no-organ control carried the organ |
| D30 | 09-22 | P2 | Aphrodite | GATE | AUTO | SCREEN | 0 (before any arm) | family excluded, design reported weakened | - | AMENDMENT_9_ADDENDUM_1_2026-09-22.md:9; 6e602dffc |  | Positive control (known-correct witness) fails tribunal: value ceiling makes family unsolvable |
| D31 | 09-22 | P2 | Aphrodite | BASELINE | SELF-L | POSTRUN | ~1 run | PRIMARY_CAUSAL_INFERENCE = INCONCLUSIVE_CONTROL_INVALID | D29 (control contaminated, same seat, same day) | AMENDMENT_10_2026-09-22.md:15; 169dc6c67 |  | Tier 3A SHAM arm contained a semantically correct solution |
| D32 | 09-22 | P2 | Aphrodite | RULER | SELF-L | POSTRUN | 1 tier | zero-FP guarantee not transferred (4.688 FP/recipient); Tier 3C adds generator qualification | - | AMENDMENT_11_2026-09-22.md; 13fd1d9b9 |  | Tier 3B discrimination guarantee failed on fresh draws |
| D33 | 09-23 | P2 | Aphrodite | CONFOUND | SELF-L | POSTRUN | ~1 d | S2 re-run under common random numbers; earlier result not re-scored | - | AMENDMENT_13_2026-09-23.md:10; 4a6bbf55d | disc | RNG seeded with library NAME: byte-identical libraries scored 13,479 vs 51,018 |
| D34 | 09-23 | P2 | Cosmos | RULER | SELF-S | POSTRUN | same run | S2 LOST as scored; S2b preregistered | - | 14d4a4522; e25a0d7cd |  | Ladder resolution defect; frozen law's cost ceiling biased +0.045 (explains D/E false positives) |
| D35 | 09-23 | P2 | Ensorain | CONFOUND | SELF-L | POSTREPORT | unknown | E1 s4 reading and F7 SUPERSEDED (originals kept) | - | aae4dd71e; 2caf43ff3 |  | Order-search confound in E1 |
| D36 | 09-24 | P2 | Nestor | LEAK | SELF-S | POSTRUN | same run | X-DENSE-OPS INVALID; repaired rerun declared | - | 21a1bf04b |  | VM module leaked across reused pool workers; control contaminated |
| D37 | 09-24 | P2 | Nestor | CONFOUND | SELF-L | POSTREPORT | unknown | X-POSITION WITHDRAWN (lesson 11) | - | 901040263 |  | Effect was partner sabotage, not register dependence |
| D38 | 09-24 | P2 | Ananke | STAT | SELF-S | POSTRUN | hours | PREREG s8 defects annotated post-data; labels unchanged | - | 016e8885a |  | Prereg s8 analysis defects (categorical, SE0, dips) |
| D39 | 09-25 | P2 | Ananke | RULER | SELF-L | POSTREPORT | ~35 h (freeze 09-24 08:01) | C1b built to test it; blind spot confirmed; C1 errata | - | comms #639, #640; cc98596dd |  | PTE-C1 packet-ablation window never ablates the readout tick (D-A); Aporia re-derived it independently |
| D40 | 09-25 | P2 | Nestor | PROV | OTHER | POSTREPORT | hours | C-CORE relabelled THEORY-AWARE | - | comms #621, #622 |  | Called 'theory-blind' but frozen 56 min after exposure to the directive |
| D41 | 09-25 | P2 | Aporia | CONFOUND | OTHER | DESIGN | hours | transplant falsifier WITHDRAWN; Ananke ANTI-MERGE adopted | - | comms #606, #624; 4adbbba8a |  | Plant-to-specimen transplant off-manifold, inseparable from generic damage |
| D42 | 09-25 | P2 | Cyclops (steward) | RULER | AUTO | DESIGN | ~3 h (#627->#651) | steward ruling replaced (relative-to-reference); ledgered against Cyclops | - | comms #627, #651, #652, #653 |  | Steward's HR2-gap 'selectivity readout' certified a blind random merge (Ensorain fixture D4) |
| D43 | 09-25 | P2 | Ensorain | CONFOUND | SELF-S | SCREEN | hours | nothing frozen until repaired (R-a) | - | comms #664; 1279cb217 |  | D6: replay-SELECTIVE arm never built, so L-R > S is the optimizer confound |
| D44 | 09-26 | P2 | Ensorain | RULER | AUTO | SCREEN | hours | store_read counter added | - | comms #709; e94fe0d5e |  | D8: R1d full-read check blind to a subsample cheat (timestamp reads masked it) |
| D45 | 09-26 | P2 | Ensorain | GATE | SELF-S | SCREEN | hours | option (i) proposed; prereg v0.3.1 frozen before any campaign row | D18 (gate decided by construction) | comms #727; 00cdbf846; 768ea8ce9 |  | D11: IM-rate swap is a lookup table, so the arm is decided by construction |
| D46 | 09-26 | P2 | Aporia (steward) | STAT | OTHER | DESIGN | hours | rule recorded defective; Aporia-only proposal OPEN | - | comms #715, #717; b3ed9785c |  | Equivalence margin derived from noise inflates EQUIVALENCE (surfaced by Ensorain D10) |
| D47 | 09-26 | P2 | Ananke | GATE | SELF-S | SCREEN | 0 (before any row) | guard fixed, code re-frozen v2; Aporia release-token rule | - | 4f7836be3; 5bd6c3945 | disc | C1b launch guard used substring match; 2 non-release posts would have launched under HOLD |
| D48 | 09-26 | P2 | Aether | INFRA | AUTO | SCREEN | same flight | durability path repaired | - | b27834319; 162c7b7c9 |  | RunPod ladder flights found container-restart and durability defects |
| D49 | 09-26 | P2 | Nestor (W1) | RULER | SELF-S | SCREEN | 0 (pre-launch) | two ruler repairs before launch | - | 50458ad0c |  | X-DD-NOCOPY-CONTEXT ruler needed two pre-launch repairs |
| D50 | 09-27 | P2 | Aether | INFRA | SELF-S | POSTRUN | same day | refuse spec mismatch; artifacts kept outside repo | - | fd7ca4fde; 3bd6f82b4 |  | Artifacts >1 MiB verified then silently discarded; --resume used wrong spec |
| D51 | 09-27 | P2 | Aphrodite | RULER | SELF-L | POSTREPORT | days (ruler in use since Tier 3) | novelty verdict split into V1-V5; ruler v2 | D32 (discrimination) | roles/Aphrodite/STATUS.md (UPDATE 09-27); APHRODITE_FRONTIER_SYNTHESIS s109 |  | Novelty ruler false positives: R-a conjugate, R-b abs()/junk |
| D52 | 09-27 | P2 | Ananke | RULER | SELF-L | POSTREPORT | unknown | carrier-swap F7 corrected; designed-echo mixture claim retracted | - | efca2cfee; a6dcde8d2 |  | Carrier swap reads presence as content; sum~1 was a mirror-pair identity |
| D53 | 09-28 | P3 | Aphrodite | CONFOUND | SELF-L | POSTRUN | 1 assay | C1 = UNTESTABLE stands; A19 repairs supply | D27 (supply/search-space) | AMENDMENT_19_2026-09-28.md:1-9 |  | No task-domain screen on the supply; shams junk-prone and unmatched (seat's own design flaw) |
| D54 | 09-28 | P3 | Aphrodite | GATE | SELF-S | POSTRUN | same session | C3R = INVALID_DESIGN_DEFECT; transfer stopped; A22 corrected | D31 (sham passes like genuine) | 29453b20c; AMENDMENT_22_2026-09-28.md:6 |  | Motif rule admitted inert wraps: genuine G1 2/8 = SHAM_0 2/8 |
| D55 | 09-28 | P3 | Aphrodite | GATE | OTHER | POSTMERGE | ~5 d (A14 code 09-23) | verified by Aphrodite 09-29; historical labels NOT altered; recorded for review | D30 (gate that cannot fail) | comms #871; ops/threads/TH-021.md |  | Gate conditions hard-coded True (run_s3s4.py L391/L420, a16.py:490); POSITIVE_CONTROL = donor schema |
| D56 | 09-28 | P3 | Nestor | RULER | OTHER | POSTREPORT | days | old results preserved; P-11 recast as dependence | - | comms #793; 0396bd78f |  | P-11 certifies construction, not heredity (painters pass) |
| D57 | 09-28 | P3 | Nestor | BASELINE | OTHER | POSTREPORT | days | CLEAN_NULL downgraded | D31 (no positive arm) | afb25f9ad |  | X-PAIR-NORECOMB: floor-vs-floor, no positive arm |
| D58 | 09-28 | P3 | Nestor | CONFOUND | OTHER | POSTREPORT | ~4 d (C9 09-24) | no verdict change (stats were unpaired); wording errata | D33 (RNG design, cross-seat) | comms #834, #840, #846; c3415b21b |  | C9-D24: implant arms share RNG draws (RANDOM_MATCHED == in situ); found incidentally by Archaeon |
| D59 | 09-28 | P3 | Nestor | RULER | SELF-L | POSTREPORT | unknown | forensic KILLED as single change; cycle-aware ruler; ENDOSTATE-R | D26 (ruler, same seat) | df0964ef3; 4b3e75782 |  | Self-state ruler defect (cycling state) |
| D60 | 09-28 | P3 | Archaeon | PROV | OPER | POSTRUN | hours | G2 CLEARED and production GO WITHDRAWN (C9); raw agreement required | D40 (post-exposure) | comms #849, #851 |  | A1/A2 canonical equivalences adopted after seeing discrepancies |
| D61 | 09-28 | P3 | Archaeon | RULER | OTHER | POSTREPORT | hours | D7 uniqueness WITHDRAWN; near->exact claim withdrawn; block-13 retraction | - | 617c1217d; a7781b857; 98c8d728c | disc | Attribution v0 reviews: definitions/claims not supported |
| D62 | 09-28 | P3 | Nestor | INFRA | SELF-S | POSTRUN | minutes | production run 1 INVALIDATED; repaired; freeze v4; re-bind requested | - | comms #908; 8153aaa8e |  | run_production.py marked every record duplicate_of itself; all births excluded |
| D63 | 09-28 | P3 | Nestor | GATE | OTHER | POSTRUN | hours | s4_run.py DOES NOT CONFORM; s4 v2 held UNUSED until reviewed | - | e7af96c47; fc99923ec |  | Two Fabric replicas: s4 runner non-conformant + L3/L4 construction-chain erratum |
| D64 | 09-28 | P3 | Nestor (D2 holdout for Cosmos) | LEAK | OTHER | SCREEN | 12 FAIL rounds over ~25 h | v1-v12 FAIL, v13 PASS 09-29; no holdout data exposed | D64 recurs within itself (DEF-ODY-011 x3) | comms #855, #921, #925; 6f5ac3192; 67e05df12 |  | Holdout firewall audit by Odysseus: key spent before validation, sender-field trust, import control |
| D65 | 09-28 | P3 | Bellerophon | STAT | OTHER | POSTREPORT | days | G6a 160/160 -> 103/160 (errata) | - | b006dd708; comms #919 |  | BUILT_BY_COPY count wrong (Artemis R-26) |
| D66 | 09-28 | P3 | Artemis | RULER | AUTO | POSTREPORT | unknown | priority labels WITHDRAWN; full sharpening stopped | - | b8f97ce00 |  | Own frozen self-test fired against the prioritisation |
| D67 | 09-28 | P3 | Cosmos | RULER | SELF-S | POSTRUN | same session | v3 declared before running | - | fe9cc4ed2; ac9f096d7 |  | T-I1 fragment test v2 tie defect |
| D68 | 09-29 | P3 | Bellerophon | STAT | OTHER | POSTREPORT | ~4 d | G2 39.4% -> 28.7%/25.3%; no gate flips; task-independence NOT_ADJUDICABLE | D33, D58 (seed design) | comms #1005, #1017; 2159c2e06 |  | Pseudo-replication: 160 origins from 83 seeds, 45 exact duplicates |
| D69 | 09-29 | P3 | Bellerophon | GATE | OTHER | POSTREPORT | ~1 d | DEF-BEL-004; arm re-read post hoc | D45 (decided by construction) | comms #980, #983 |  | Q4 host arm kept 'own stores' condition: a host copy fails by construction |
| D70 | 09-29 | P3 | Odysseus | STAT | OTHER | POSTREPORT | ~20 h | coordination 4/12 -> 8/12 (gate still MET) | - | comms #1019; 6f5ac3192 |  | S3 RESULT counted only actions committed at submission (Artemis) |
| D71 | 09-29 | P3 | Odysseus | INFRA | SELF-S | POSTRUN | recurred 3x | DEF-ODY-011 stop-gap | - | 102569d24; 8efddb4b7 |  | Shared worker checkout between same-agent instances; add race burns an Attempt |
| D72 | 09-29 | P3 | Hecate | STAT | SELF-L | POSTREPORT | hours | 12 of 29 worlds unattainable, not 11; ledger row | - | 42169bad6 |  | Count error in probe round report |
| D73 | 09-30 | P3 | Bellerophon | PROV | OTHER | POSTMERGE | ~43 h (C4.2 09-28 10:39) | BLOCKING; confirmatory label ALTERED; VALIDATED conditional only | D60 (post-exposure, same arc) | comms #1044, #1050; d06059735 |  | E-003 VALIDATED rested on post-exposure C4.2 that removed the frozen 'P2 -> ALTERED' route; merge reviews were told to accept it |
| D74 | 09-30 | P3 | Hecate | GATE | OTHER | POSTREPORT | ~5 h | MAJOR; disposition stands | - | comms #1037; EVIDENCE_AUDIT_2026-09-30.md:39 |  | Pass 4 r2: W6 ORIG kill condition met by own ALT data but reported 'not fired' |
| D75 | 09-30 | P3 | Hecate | RULER | SELF-L | POSTREPORT | ~5 h | 'zero UNFAMILIAR' relabelled an instrument result; F2 | D57 (absence without positive control) | e4a05ba3b; comms #1037 | disc | Detector never calibrated on an UNFAMILIAR item; autopsy (operator CWO) and Harmonia found it within 6 min |
| D76 | 09-30 | P3 | Hecate | BASELINE | OTHER | POSTRUN | ~1 h | construct MAJOR; F3; ruler withdrawn | D16 (shortcut baseline) | RULER_QUALITY_2026-09-30.md:50; cf70bbb05 |  | NOVELTY_DETECTOR_VALIDATED passable by a lookup baseline |
| D77 | 09-30 | P3 | Tyche | GATE | OTHER | POSTRUN | ~0 (audit before report) | BLOCKING; labelled UNREACHABLE_BY_DESIGN; F1 | D30, D55 (unreachable/cannot-fail gate) | comms #1039, #1047; e72508448 |  | H1/H6 PASS unreachable: 3 valid worlds against a >=4 rule |
| D78 | 09-30 | P3 | Tyche | RULER | OTHER | POSTRUN | ~0 | H3 negative arm labelled NON_DISCRIMINATING | - | RULER_QUALITY_2026-09-30.md:29 |  | Ecology growth alone moves the residual 0.04-0.13 |
| D79 | 09-30 | P3 | Harmonia | GATE | OTHER | POSTREPORT | ~40 min | C-1: F1 amended (evolving baselines in attainable set) | D77 (auditor commits the class it audits) | comms #1047; 68c6e7f68 |  | Auditor's own H4 'nearly unattainable' rating wrong (Tyche) |
| D80 | 09-30 | P3 | Odysseus | RULER | OTHER | POSTREPORT | ~15 h | MAJOR -> F4 SANITY_CHECK_ONLY; RESULT corrected | - | comms #1038; 3eb8af06b |  | S3 quality non-inferiority clause at ceiling (9.1/10, margin 1); saturation disclosed by owner, classified by Harmonia |
| D81 | 09-30 | P3 | Ananke | PROV | OTHER | POSTMERGE | ~24 h | MAJOR; F6 (freeze must be an earlier commit) | D40, D60 (exposure/freeze) | comms #1045; EVIDENCE_AUDIT_2026-09-30_SAMPLE2.md:91 |  | W-O PLAN.md first committed together with results |
| D82 | 09-30 | P3 | Ananke | GATE | OTHER | POSTMERGE | ~21 h | MAJOR; headline overclaims | D45 (by construction) | comms #1045; SAMPLE2.md:99 |  | W-Q 'certifies all 42' was guaranteed by construction (own P3) |
| D83 | 09-30 | P3 | Ananke | RULER | SELF-S | POSTRUN | same run | deviations and plan-rule defects recorded | - | 478c9ec6f |  | W-Y MAJ readout Kp[7] is not a carrier (always 0) |
| D84 | 09-30 | P3 | Aether | STAT | OTHER | POSTREPORT | unknown | erratum; verdict unaffected | D72 (count/text) | comms #1056; 9668f2813 |  | RESULT text: lesion lower in all four seeds, not three |
| D85 | 09-30 | P3 | Harmonia | PROV | OTHER | POSTREPORT | ~11 d (HARM-55 09-19) | ERRATUM E-1; blob hashes listed; no score affected | D10, D19 (CRLF hashing; lesson ledgered 09-11) | 646cbcda8; comms #1072, #1076 |  | Two artifact hashes were host-written CRLF, not blob hashes (Techne) |
| D86 | 09-30 | P3 | Bellerophon | GATE | OTHER | POSTREPORT | ~1.5 h (#1078->#1113) | reading relabelled UNRESOLVED; 5 claims WITHDRAWN; F8 | D77 (unreachable kill; frozen 07:17 AFTER F1 04:50) | comms #1078, #1113; 6879b2236 |  | REPL-01 K3 founder-snapshot ruler could not PASS (content turns over in every arm); blinding honour-system |
| D87 | 09-30 | P3 | Harmonia | GATE | OTHER | POSTREPORT | ~2 h | C-2: audit J downgraded to SUPPORTED_WITH_DEFECTS | D79, D86 (auditor misses own F1) | comms #1123; d3f99cfdc |  | Audit J rated REPL-01 SUPPORTED and missed K3 reachability; Harmonia commit subject carried embargoed verdict |
| D88 | 09-30 | P3 | Tyche | CONFOUND | SELF-L | POSTREPORT | ~1 run | v1 F1 corrected; survival mechanism UNRESOLVED | - | 6a28fc49e |  | V0 included the 14-slot novelty/random reserve (membership unlogged) |
| D89 | 09-30 | P3 | Theseus | LEAK | SELF-L | POSTRUN | ~1 run | v0 FAIL stands; v0_1 corrected replication | - | 308330aaf | disc | Lens leak into DEEP lanes; set-order nondeterminism |
| D90 | 09-30 | P3 | Mnemosyne | LEAK | OTHER | POSTMERGE | unknown | custody defect routed to Harmonia/Aporia; no sealed artifact opened | - | comms #1128; 0b0759dba | lat | evidence_wiki gap_prospective_v1 sealed slate method inferable from public scores |
| D91 | 09-30 | P3 | Odysseus | INFRA | OTHER | POSTMERGE | unknown | DEF-ODY-020..022 recorded; NOT implemented (CWO-B) | D71 (fabric) | comms #1119; bcb7a4d73 |  | Fabric script executor: timeouts lose all output; deterministic retries; head-of-line |
| D92 | 09-30 | P3 | Ananke | GATE | OTHER | POSTMERGE | days | 5 neutral fixes + 15 regression tests; C1 errata; no result changed | D45 (vacuous clause) | 41e386ccd; cc44f5903 | disc | Harvest H-IMPL: handoff clause (b) passes vacuously on unscanned offsets; MAJ/XOR reach from sensor 0 only |

## Counts

92 episodes; 27 owner seats (sibling instances counted under the parent seat). Most episodes are owned by Nestor (16, incl. Nestor-H), Aphrodite (11), Ananke (8), Harmonia (6), Bellerophon (6), and Aporia, Ensorain, Odysseus and Hecate (4 each).

Stage found, by period:

| period | n | DESIGN | SCREEN | POSTRUN | POSTREPORT | POSTMERGE | early share (DESIGN+SCREEN) |
|---|---|---|---|---|---|---|---|
| P0 (08-20..09-10, sample) | 7 | 0 | 0 | 0 | 7 | 0 | 0% |
| P1 (09-11..09-19) | 19 | 0 | 2 | 5 | 9 | 3 | 11% |
| P2 (09-21..09-27) | 26 | 4 | 7 | 8 | 7 | 0 | 42% |
| P3 (09-28..09-30) | 40 | 0 | 1 | 12 | 20 | 7 | 3% |

Discoverer, by period:

| period | SELF-S | SELF-L | AUTO | OTHER | OPER | self+auto share |
|---|---|---|---|---|---|---|
| P0 | 0 | 6 | 0 | 1 | 0 | 86% |
| P1 | 5 | 2 | 3 | 9 | 0 | 53% |
| P2 | 9 | 10 | 4 | 3 | 0 | 88% |
| P3 | 5 | 6 | 1 | 27 | 1 | 30% |

Who found the 27 OTHER episodes in P3:
- Harmonia: 9, all from the operator's CWO evidence and ruler audits on 09-30.
- Artemis: 8, from the challenge and dispatch role set up on 09-28 at the operator's instruction.
- Fabric reviewer replicas, merge reviews and harvest workers: 5.
- Archaeon: 2.
- Odysseus, Tyche and Techne: 1 each.

At least 18 of the 27 came from review lanes the operator commissioned in the last three days.

Class, by period:

| period | RULER | GATE | BASELINE | CONFOUND | STAT | LEAK | PROV | INFRA |
|---|---|---|---|---|---|---|---|---|
| P0 | 1 | 0 | 0 | 1 | 5 | 0 | 0 | 0 |
| P1 | 7 | 2 | 1 | 0 | 2 | 0 | 5 | 2 |
| P2 | 8 | 3 | 2 | 6 | 2 | 1 | 1 | 3 |
| P3 | 9 | 11 | 2 | 3 | 5 | 3 | 4 | 3 |

## 1. Trend in stage found

There is no monotone shift toward earlier detection, and P3 runs the other way. P2 has the most early catches (42% at DESIGN or SCREEN). Almost all of them come from two local practices:
- Aphrodite's freeze-amendment-before-code discipline: D29 and D30 were caught before any arm ran.
- The Ensorain/Aporia/Cyclops LM01 prereg loop, which used planted fixtures, cheat fixtures and a steward checklist: D42 to D46. The fixtures even caught a defect in a steward's own ruling (D42).

P3's early share falls to 3%. P3 is dominated by post-report and post-merge findings from the new adversarial review lanes.

What else could produce this pattern, apart from a real change in practice:
- Detection effort shifted, not detection timing. The 09-30 audit, the 09-28 Artemis challenge role and the Fabric merge reviews read finished, merged work by design, so their finds are necessarily post-report or post-merge. More reviewers looking at finished work adds late-stage catches no matter how good pre-run discipline is.
- Collapsing undercounts early catches. Ensorain's D1 to D11 and the D2 firewall's 12 rounds each collapse many SCREEN-stage catches into a few rows. Counted per defect, P2 and P3 SCREEN would both rise. P3 would rise by about 12 from the D2 rounds alone. The early-share figures depend on this counting rule.
- The kind of work changed. P2 was heavy on preregistration (Aphrodite A7 to A22, LM01). P3 was heavy on closing, merging and reviewing the attribution arc and ARC3.
- Recording style. Seats that write freeze amendments (Aphrodite) or prereg-defect ledgers (Ensorain) leave a visible trace of pre-run catches. Seats that fix silently before a freeze leave none. This favours a few seats.
- P0 is a 7-row sample picked from loud retraction subjects, so it is biased toward post-report finds.

Defensible statement: some seats can demonstrably catch defects before a run. This depends on the seat and the process, not on the fleet or the date. There is no evidence that the fleet-wide stage-found distribution moved earlier.

## 2. Discoverer mix over time

P0 to P2 are mostly self-discovered (86%, 53% and 88% self plus automated). P3 flips to 30% self, 68% other-seat. The flip coincides with new roles: Artemis challenge and dispatch from 09-28, Fabric merge reviews under MWO-0001 and MWO-0004, and the Harmonia CWO audit on 09-30. It does not coincide with any change in how seats check their own work.

Who catches what:
- Self or automated catches are mostly RULER and INFRA problems that show up while running: D23, D34, D36, D62, D71.
- Other seats catch most GATE-reachability, post-exposure and overclaim defects: D55, D73, D77, D81, D82, D86. Owners rarely caught these themselves; the exceptions are D18 and D54.
- The operator appears directly once (D60). Indirectly, the operator commissioned most of P3's reviews.
- Auditors are not immune. Harmonia made the class of error it audits for twice within hours of writing the rule (D79, D87). Both were caught by the audited seat or by Fabric reviewers.
- Fabric reviewers can be steered. In D73, both merge reviews were told to check "P2 treated as engine-native" and passed the post-exposure change. That review layer inherits the framing of whoever writes the prompt.

## 3. Recurrence and transfer

Classes that recur across seats after a lesson was written down somewhere:

| class | episodes (date found) | where the lesson was recorded | transfer verdict |
|---|---|---|---|
| CRLF vs blob hashing | D10 Lexis (09-11), D19 Techne (09-16), D85 Harmonia (09-30) | Lexis calibration row, 09-11 | Partial. Bellerophon and Nestor later cite "LF-normalised sha256" (74f72e805, #850), but Harmonia repeated the error 19 days after the first ledger row. |
| Gate unreachable, constant, vacuous or decided by construction | D18 (09-16), D24, D30 (09-22), D45 (09-26), D54, D55 (introduced 09-23, found 09-28), D69, D77, D79, D82, D86, D87, D92 | Seat-local only (Aphrodite A9 Add1; Ensorain D11) until Harmonia F1 at 09-30 04:50 | Fails. This is the most frequent class (14 episodes). Aphrodite caught one in A9 Add1 on 09-22 and then shipped constant-True gates in A14 code on 09-23 (D55). Bellerophon REPL-01 was frozen at 07:17, about 2.5 h after F1, with an unreachable K3 (D86). F1's author missed the same thing in audit J (D87). Caveat: 2.5 h is too short to expect adoption, and nothing shows Bellerophon had read F1. |
| Missing or contaminated control or positive arm | D29, D31 Aphrodite (09-22); D42 Cyclops (09-25); D57 Nestor (09-28); D75, D76 Hecate (09-30) | Aphrodite A7 Add1 and A10 (seat-local); fleet rules F2/F3 on 09-30 | Fails across seats before 09-30. No cross-seat channel carried Aphrodite's lesson. |
| RNG, seed or pairing design | D33 Aphrodite (09-23), D58 Nestor (introduced by 09-24), D68 Bellerophon (found 09-29), D89 Theseus (09-30) | Aphrodite A13 (common random numbers), seat-local; no fleet rule found | Fails. No standing rule exists. Each seat rediscovers it. |
| Post-exposure rule change, or freeze not provable | D40 Nestor (09-25), D60 Archaeon (09-28 12:16), D73 Bellerophon (introduced 09-28 10:39), D81 Ananke (plan and results committed together 09-29 05:17) | Aporia note #621 (09-25); operator "CLOSE THE INDEPENDENCE GATES" (09-28); F6/F7 (09-30) | Mixed. D73 was introduced before D60's lesson, so it is not a transfer failure. D81 came after D60, in a different seat and arc, so it is weak evidence of non-transfer. |
| Ruler saturation, dilution or ceiling | D26 Nestor (09-19), D59 Nestor, D51 Aphrodite, D80 Odysseus, D76 Hecate | Aphrodite worker W3 fleet saturation survey (cb3828f52, 09-27); F4 (09-30) | Unknown. The class appears again after 09-27, but the instruments involved predate the survey. |

Same-seat recurrence:
- Harmonia: D01, D04 and D07, all statistical retractions in P0. P3 adds D79, D85 and D87.
- Aphrodite: D29, D31, D53, D54 and D55. TH-021 records the seat's own rate as 3 of 4 consecutive assays failing on design or supply.
- Nestor: D26 and D59 (rulers); D36, D62 and D63 (run integrity).
- Bellerophon: D65, D68, D69, D73 and D86, five errata in three days.

The lesson system (calibration ledgers, standing rules) is seat-local until 09-30, and nothing shows that seats read each other's ledgers. Harmonia's section F (F1 to F8) and the executable AP-1.0.0 primitives were the first fleet-level mechanism. They are less than one day old, so their effect cannot be tested in this corpus.

## 4. Confounds

- **Detection effort rose sharply in P3.** Three new adversarial lanes (Artemis challenge, Fabric merge reviews, Harmonia CWO audit) and an operator-ordered "inference harvest" were all added within 72 h. P3 has 40 episodes in 3 days, against 19 in 9 days for P1. That rate measures review capacity, not error rate. There is no denominator: no count of experiments, verdicts or merges per period.
- **The window is short.** Comms only cover 09-11 to 09-30, with gaps on 09-15, 09-20 and 09-22 (1 message or none). P0 is git-only, small and hand-picked. Three weeks cannot show learning curves for seats that were mostly created or re-chartered within that window (Tyche, Theseus, Hecate, Achilles and others).
- **Survivorship and recording.** Episodes appear only if someone wrote CORRECTION, ERRATA, DEFECT or similar in a subject or message. Seats with a strong confessional style dominate: Nestor and Aphrodite own 27 of 92. Silent fixes, and seats that do not narrate, are invisible. Parked or unbooted seats cannot record defects (for example D13's owner never booted). Defects nobody has found yet are, by construction, absent.
- **The definition of "defect" drifted.** It moved from "my claim was wrong" (P0 retractions), to infrastructure and record defects (P1 base-role era), to "the ruler cannot discriminate, or the gate cannot fail" (P2 and P3, formalised on 09-30 as F1 to F8). In P3, ruler-quality defects that would not have been named in P1 count as episodes. GATE rising from 2 to 11 partly reflects new vocabulary (UNREACHABLE_BY_DESIGN, NON_DISCRIMINATING), not new errors.
- **Attribution is noisy.** Git author is always the operator, so seats are attributed by subject prefix or path. Instance siblings (Nestor-A/B/C/H) are folded into the parent seat. In about 9 rows the discoverer is uncertain (marked `disc`).
- **Coding granularity.** Batch commits were collapsed, as described in the method note. Changing this rule changes the stage and discoverer shares by up to about 15 points.
- **"OTHER" includes Claude Fabric workers.** These are the same model family as the seats. "Other-seat" here means different context and a different prompt, not an independent epistemic source.

## What CANNOT be concluded

- That Prometheus's error rate fell or rose. There is no denominator of work per period.
- That detection is moving earlier fleet-wide. P2's early share is two seats' processes, and P3 reverses it.
- That the 09-30 standing rules (F1 to F8, AP-1.0.0) work. There is less than one day of exposure, and the only post-rule observations are two recurrences in the first hours.
- That adversarial review is better than self-review in general. Review targeted finished work in P3, so its stage distribution is late by construction. No same-work comparison exists.
- That lessons do not transfer at all. Partial transfer is visible for CRLF hashing, and the corpus cannot show defects that were prevented.
- Per-seat defect rates or rankings. Counts reflect narration style, workload and activity window more than quality.
- Latency trends. Introduction time is known for only about 15 episodes, mostly short-lived same-session ones.
- Whether any defect changed a published scientific conclusion beyond the cases where a verdict label changed. Those are D16, D25, D31, D36, D37, D53, D54, D60, D62, D73 and D86. Several other episodes explicitly kept the original labels, for example D55, D58 and D68.

## CSV

```csv
id,date_found,period,owner_seat,defect_class,discoverer,stage_found,latency,consequence,recurrence_of,evidence,uncertain,defect
D01,2026-08-20,P0,Harmonia,STAT,SELF-L,POSTREPORT,~hours (P9->P10),claim REFUTED: sampling manufactured a false positive,-,64bba4111,,Soak P10: P9's claim refuted; sampling made a false positive in P4
D02,2026-08-21,P0,Ergon,CONFOUND,SELF-L,POSTREPORT,unknown,P1 KILLED as truncation-confounded; gate had been flattered,-,959165882; a7d9bb2d8,,Truncation defect flattered the leveling gate
D03,2026-08-21,P0,Aporia,STAT,SELF-L,POSTREPORT,unknown,P63 4.6-bit headline RETRACTED; honest number is the null,-,6d0a76641,,P63 information-gain story retracted
D04,2026-08-31,P0,Harmonia,STAT,SELF-L,POSTREPORT,unknown,action-divergence excess WITHDRAWN,"D01 (stat, same seat)",1be87a0fe,,Published a chance floor that was actually a ceiling
D05,2026-08-31,P0,Techne,RULER,SELF-L,POSTREPORT,~1 cycle,hole proposals blocked; 43 cells re-classified,-,fa84da2e4; b100162ba,,Cartography hole count was measuring Techne's own tagger (3.3% classification)
D06,2026-09-03,P0,Lexis,STAT,OTHER,POSTREPORT,unknown,HC-T01 verdict downgraded; wider-literature claim withdrawn,-,62f7a1a1e; a22792dc6,disc,Kill condition scored with the wrong statistic; premise obsolete
D07,2026-09-05,P0,Harmonia,STAT,SELF-L,POSTREPORT,unknown,SE-1b RETRACTED (winner's curse: best of 12 draws),"D01, D04 (stat, same seat, 3rd time)",28d58afbb,,Surviving claim was the highest of twelve draws
D08,2026-09-11,P1,Hephaestus,RULER,SELF-S,POSTRUN,same session,5 instrument defects corrected before any verdict,-,comms #28,,Specimen 3: five instrument defects caught before readout
D09,2026-09-11,P1,base-role (shared),PROV,OTHER,POSTMERGE,days (unknown),journals/results re-included in .gitignore; fixed centrally,-,comms #71; 2b79c140a; dcafe3047,,"Ignored-output defect: five seats (Atalanta, Eos, Coeus, Clymene, Hermes) found it independently"
D10,2026-09-11,P1,Lexis,PROV,OTHER,POSTREPORT,same day,13 manifest rows re-hashed; calibration row,-,8600edd68 (per Diomedes f08c81c66),,"Archaeon manifest report: all 13 rows CRLF-hashed, not blob-hashed"
D11,2026-09-11,P1,Techne,RULER,OTHER,POSTREPORT,unknown,"MOSEK struck; Elenchus METHOD-FLAW, invalidates-claim",-,1912d823e; d3ce43c24,,TECHNE-38 fixture badly posed (ill-conditioned case)
D12,2026-09-11,P1,Hermes,PROV,OTHER,POSTREPORT,unknown,claim corrected; calibration row 10,-,b026db8cc; comms #108,,"Asserted agora tables 'not fed' from a label, without measuring"
D13,2026-09-11,P1,Nous/PipelineOrchestrator,STAT,OTHER,POSTMERGE,months (est.),reported to an unbooted owner; NOT fixed,-,comms #85 (Coeus),lat,nous.py: 11/16 concepts at 2.5x sampling weight rest on n<=5
D14,2026-09-11,P1,Nyx,STAT,SELF-L,POSTREPORT,~1 day,scope claim in #190/#191 corrected,-,comms #198,,"pass_to_descendant zero calls is strategy-wide, not the discriminator"
D15,2026-09-14,P1,Nestor (lane C),RULER,OTHER,POSTRUN,unknown,C7 correction rows + journal retractions,-,d1f73fc3c; fe8616884,,"Charge-column indexing bug in C7 harness, found by sibling lane B"
D16,2026-09-14,P1,Nestor (lane B),BASELINE,OTHER,POSTREPORT,hours,C1 bounty RETRACTED (1.43x was vs pessimistic baseline; recheck 0.93-1.01),-,cc1699b0e; db523bfac; 04ee00aa6,,Speedup claimed against a pessimistic baseline
D17,2026-09-16,P1,Nestor (R8),RULER,SELF-S,SCREEN,same session,checker and C3 probe rewritten behavioural,-,e5aa8d269; 6c02b89a9,,Own gate checker was wrong; C3 probe was grepping for its own defect
D18,2026-09-16,P1,Nestor-H,GATE,SELF-S,POSTRUN,same session,MDD80 rule read VACUOUS; disclosed,-,f81464458; da7582650,,Preregistered MDD80 rule vacuous because of its own grid defect
D19,2026-09-16,P1,Techne,PROV,AUTO,POSTMERGE,days,11 DRIFT bodies classified as RECORD defects,D10 (CRLF hashing),6434fbb65,,M2 rematerialize census: 11 drifts all CRLF/record defects
D20,2026-09-17,P1,Daedalus,INFRA,SELF-S,POSTREPORT,hours (#345->#347),own mechanism falsified; SFE 9.0.1 repair,-,comms #347; 3e8893a8c,,No-reader control showed the real cause: new SQLite connection per request
D21,2026-09-17,P1,Vivarium,INFRA,SELF-S,POSTRUN,same day,4xx classifier fixed with tests; unparked,-,comms #355,,Misclassified a correct 409 as ENGINE_TRANSPORT and paged Daedalus
D22,2026-09-17,P1,Nyx,RULER,OTHER,POSTREPORT,unknown,recurrence reading retracted from ASAL packet plan,-,comms #384; 5beb6bff3,,Techne: CLIP open-endedness score ranks garbage above living Lenia
D23,2026-09-18,P1,Archaeon,RULER,AUTO,POSTRUN,same run,C5-09 a01 INSTRUMENT_INVALID; numbers preserved; control fixed for a02,-,0b0a75d5d,,Determinism control compared volatile wall_s
D24,2026-09-18,P1,Bellerophon,GATE,AUTO,SCREEN,same night,suite strengthened (3/20 plausible wrong implementations survived),-,958e8be8e,,Mutation ledger: test suite too weak to kill 3 of 20 wrong implementations
D25,2026-09-18,P1,Aporia,PROV,OTHER,POSTREPORT,~1 d to find; 5 d to withdraw,E3 WITHDRAWN; audit headline 5->4 errors,-,"comms #421, #548; d1d877b39",,"RSI audit E3 wrong (DGM is ICLR 2026), found by Aphrodite"
D26,2026-09-19,P1,Nestor (CW01),RULER,SELF-L,POSTREPORT,~1 cycle,4 of 7 fixed-count claims attributed to the ruler,-,8a01ddede; ce97fbcc4,,Damage ruler dilution: length-robustness was a ruler artefact
D27,2026-09-21,P2,Aphrodite,CONFOUND,SELF-L,POSTREPORT,~1 slice,label kept ADVERSARIAL with dated correction,-,roles/Aphrodite/engine/AMENDMENT_3_2026-09-21.md:11,,Slice-2 true solution (depth 4) was never in the depth-3 search space
D28,2026-09-21,P2,Aphrodite,INFRA,SELF-L,POSTRUN,unknown,cap removed as instrument repair (ruled not a parameter change),-,AMENDMENT_5_2026-09-21.md:17,disc,Hidden HELPER_CANDIDATE_CAP truncated the declared search space
D29,2026-09-22,P2,Aphrodite,BASELINE,SELF-S,DESIGN,0 (before any arm),"run both controls, report both",-,AMENDMENT_7_ADDENDUM_1_2026-09-22.md:10; 341ad9f38,,SCRATCH control contained the fold space: the no-organ control carried the organ
D30,2026-09-22,P2,Aphrodite,GATE,AUTO,SCREEN,0 (before any arm),"family excluded, design reported weakened",-,AMENDMENT_9_ADDENDUM_1_2026-09-22.md:9; 6e602dffc,,Positive control (known-correct witness) fails tribunal: value ceiling makes family unsolvable
D31,2026-09-22,P2,Aphrodite,BASELINE,SELF-L,POSTRUN,~1 run,PRIMARY_CAUSAL_INFERENCE = INCONCLUSIVE_CONTROL_INVALID,"D29 (control contaminated, same seat, same day)",AMENDMENT_10_2026-09-22.md:15; 169dc6c67,,Tier 3A SHAM arm contained a semantically correct solution
D32,2026-09-22,P2,Aphrodite,RULER,SELF-L,POSTRUN,1 tier,zero-FP guarantee not transferred (4.688 FP/recipient); Tier 3C adds generator qualification,-,AMENDMENT_11_2026-09-22.md; 13fd1d9b9,,Tier 3B discrimination guarantee failed on fresh draws
D33,2026-09-23,P2,Aphrodite,CONFOUND,SELF-L,POSTRUN,~1 d,S2 re-run under common random numbers; earlier result not re-scored,-,AMENDMENT_13_2026-09-23.md:10; 4a6bbf55d,disc,"RNG seeded with library NAME: byte-identical libraries scored 13,479 vs 51,018"
D34,2026-09-23,P2,Cosmos,RULER,SELF-S,POSTRUN,same run,S2 LOST as scored; S2b preregistered,-,14d4a4522; e25a0d7cd,,Ladder resolution defect; frozen law's cost ceiling biased +0.045 (explains D/E false positives)
D35,2026-09-23,P2,Ensorain,CONFOUND,SELF-L,POSTREPORT,unknown,E1 s4 reading and F7 SUPERSEDED (originals kept),-,aae4dd71e; 2caf43ff3,,Order-search confound in E1
D36,2026-09-24,P2,Nestor,LEAK,SELF-S,POSTRUN,same run,X-DENSE-OPS INVALID; repaired rerun declared,-,21a1bf04b,,VM module leaked across reused pool workers; control contaminated
D37,2026-09-24,P2,Nestor,CONFOUND,SELF-L,POSTREPORT,unknown,X-POSITION WITHDRAWN (lesson 11),-,901040263,,"Effect was partner sabotage, not register dependence"
D38,2026-09-24,P2,Ananke,STAT,SELF-S,POSTRUN,hours,PREREG s8 defects annotated post-data; labels unchanged,-,016e8885a,,"Prereg s8 analysis defects (categorical, SE0, dips)"
D39,2026-09-25,P2,Ananke,RULER,SELF-L,POSTREPORT,~35 h (freeze 09-24 08:01),C1b built to test it; blind spot confirmed; C1 errata,-,"comms #639, #640; cc98596dd",,PTE-C1 packet-ablation window never ablates the readout tick (D-A); Aporia re-derived it independently
D40,2026-09-25,P2,Nestor,PROV,OTHER,POSTREPORT,hours,C-CORE relabelled THEORY-AWARE,-,"comms #621, #622",,Called 'theory-blind' but frozen 56 min after exposure to the directive
D41,2026-09-25,P2,Aporia,CONFOUND,OTHER,DESIGN,hours,transplant falsifier WITHDRAWN; Ananke ANTI-MERGE adopted,-,"comms #606, #624; 4adbbba8a",,"Plant-to-specimen transplant off-manifold, inseparable from generic damage"
D42,2026-09-25,P2,Cyclops (steward),RULER,AUTO,DESIGN,~3 h (#627->#651),steward ruling replaced (relative-to-reference); ledgered against Cyclops,-,"comms #627, #651, #652, #653",,Steward's HR2-gap 'selectivity readout' certified a blind random merge (Ensorain fixture D4)
D43,2026-09-25,P2,Ensorain,CONFOUND,SELF-S,SCREEN,hours,nothing frozen until repaired (R-a),-,comms #664; 1279cb217,,"D6: replay-SELECTIVE arm never built, so L-R > S is the optimizer confound"
D44,2026-09-26,P2,Ensorain,RULER,AUTO,SCREEN,hours,store_read counter added,-,comms #709; e94fe0d5e,,D8: R1d full-read check blind to a subsample cheat (timestamp reads masked it)
D45,2026-09-26,P2,Ensorain,GATE,SELF-S,SCREEN,hours,option (i) proposed; prereg v0.3.1 frozen before any campaign row,D18 (gate decided by construction),comms #727; 00cdbf846; 768ea8ce9,,"D11: IM-rate swap is a lookup table, so the arm is decided by construction"
D46,2026-09-26,P2,Aporia (steward),STAT,OTHER,DESIGN,hours,rule recorded defective; Aporia-only proposal OPEN,-,"comms #715, #717; b3ed9785c",,Equivalence margin derived from noise inflates EQUIVALENCE (surfaced by Ensorain D10)
D47,2026-09-26,P2,Ananke,GATE,SELF-S,SCREEN,0 (before any row),"guard fixed, code re-frozen v2; Aporia release-token rule",-,4f7836be3; 5bd6c3945,disc,C1b launch guard used substring match; 2 non-release posts would have launched under HOLD
D48,2026-09-26,P2,Aether,INFRA,AUTO,SCREEN,same flight,durability path repaired,-,b27834319; 162c7b7c9,,RunPod ladder flights found container-restart and durability defects
D49,2026-09-26,P2,Nestor (W1),RULER,SELF-S,SCREEN,0 (pre-launch),two ruler repairs before launch,-,50458ad0c,,X-DD-NOCOPY-CONTEXT ruler needed two pre-launch repairs
D50,2026-09-27,P2,Aether,INFRA,SELF-S,POSTRUN,same day,refuse spec mismatch; artifacts kept outside repo,-,fd7ca4fde; 3bd6f82b4,,Artifacts >1 MiB verified then silently discarded; --resume used wrong spec
D51,2026-09-27,P2,Aphrodite,RULER,SELF-L,POSTREPORT,days (ruler in use since Tier 3),novelty verdict split into V1-V5; ruler v2,D32 (discrimination),roles/Aphrodite/STATUS.md (UPDATE 09-27); APHRODITE_FRONTIER_SYNTHESIS s109,,"Novelty ruler false positives: R-a conjugate, R-b abs()/junk"
D52,2026-09-27,P2,Ananke,RULER,SELF-L,POSTREPORT,unknown,carrier-swap F7 corrected; designed-echo mixture claim retracted,-,efca2cfee; a6dcde8d2,,Carrier swap reads presence as content; sum~1 was a mirror-pair identity
D53,2026-09-28,P3,Aphrodite,CONFOUND,SELF-L,POSTRUN,1 assay,C1 = UNTESTABLE stands; A19 repairs supply,D27 (supply/search-space),AMENDMENT_19_2026-09-28.md:1-9,,No task-domain screen on the supply; shams junk-prone and unmatched (seat's own design flaw)
D54,2026-09-28,P3,Aphrodite,GATE,SELF-S,POSTRUN,same session,C3R = INVALID_DESIGN_DEFECT; transfer stopped; A22 corrected,D31 (sham passes like genuine),29453b20c; AMENDMENT_22_2026-09-28.md:6,,Motif rule admitted inert wraps: genuine G1 2/8 = SHAM_0 2/8
D55,2026-09-28,P3,Aphrodite,GATE,OTHER,POSTMERGE,~5 d (A14 code 09-23),verified by Aphrodite 09-29; historical labels NOT altered; recorded for review,D30 (gate that cannot fail),comms #871; ops/threads/TH-021.md,,"Gate conditions hard-coded True (run_s3s4.py L391/L420, a16.py:490); POSITIVE_CONTROL = donor schema"
D56,2026-09-28,P3,Nestor,RULER,OTHER,POSTREPORT,days,old results preserved; P-11 recast as dependence,-,comms #793; 0396bd78f,,"P-11 certifies construction, not heredity (painters pass)"
D57,2026-09-28,P3,Nestor,BASELINE,OTHER,POSTREPORT,days,CLEAN_NULL downgraded,D31 (no positive arm),afb25f9ad,,"X-PAIR-NORECOMB: floor-vs-floor, no positive arm"
D58,2026-09-28,P3,Nestor,CONFOUND,OTHER,POSTREPORT,~4 d (C9 09-24),no verdict change (stats were unpaired); wording errata,"D33 (RNG design, cross-seat)","comms #834, #840, #846; c3415b21b",,C9-D24: implant arms share RNG draws (RANDOM_MATCHED == in situ); found incidentally by Archaeon
D59,2026-09-28,P3,Nestor,RULER,SELF-L,POSTREPORT,unknown,forensic KILLED as single change; cycle-aware ruler; ENDOSTATE-R,"D26 (ruler, same seat)",df0964ef3; 4b3e75782,,Self-state ruler defect (cycling state)
D60,2026-09-28,P3,Archaeon,PROV,OPER,POSTRUN,hours,G2 CLEARED and production GO WITHDRAWN (C9); raw agreement required,D40 (post-exposure),"comms #849, #851",,A1/A2 canonical equivalences adopted after seeing discrepancies
D61,2026-09-28,P3,Archaeon,RULER,OTHER,POSTREPORT,hours,D7 uniqueness WITHDRAWN; near->exact claim withdrawn; block-13 retraction,-,617c1217d; a7781b857; 98c8d728c,disc,Attribution v0 reviews: definitions/claims not supported
D62,2026-09-28,P3,Nestor,INFRA,SELF-S,POSTRUN,minutes,production run 1 INVALIDATED; repaired; freeze v4; re-bind requested,-,comms #908; 8153aaa8e,,run_production.py marked every record duplicate_of itself; all births excluded
D63,2026-09-28,P3,Nestor,GATE,OTHER,POSTRUN,hours,s4_run.py DOES NOT CONFORM; s4 v2 held UNUSED until reviewed,-,e7af96c47; fc99923ec,,Two Fabric replicas: s4 runner non-conformant + L3/L4 construction-chain erratum
D64,2026-09-28,P3,Nestor (D2 holdout for Cosmos),LEAK,OTHER,SCREEN,12 FAIL rounds over ~25 h,"v1-v12 FAIL, v13 PASS 09-29; no holdout data exposed",D64 recurs within itself (DEF-ODY-011 x3),"comms #855, #921, #925; 6f5ac3192; 67e05df12",,"Holdout firewall audit by Odysseus: key spent before validation, sender-field trust, import control"
D65,2026-09-28,P3,Bellerophon,STAT,OTHER,POSTREPORT,days,G6a 160/160 -> 103/160 (errata),-,b006dd708; comms #919,,BUILT_BY_COPY count wrong (Artemis R-26)
D66,2026-09-28,P3,Artemis,RULER,AUTO,POSTREPORT,unknown,priority labels WITHDRAWN; full sharpening stopped,-,b8f97ce00,,Own frozen self-test fired against the prioritisation
D67,2026-09-28,P3,Cosmos,RULER,SELF-S,POSTRUN,same session,v3 declared before running,-,fe9cc4ed2; ac9f096d7,,T-I1 fragment test v2 tie defect
D68,2026-09-29,P3,Bellerophon,STAT,OTHER,POSTREPORT,~4 d,G2 39.4% -> 28.7%/25.3%; no gate flips; task-independence NOT_ADJUDICABLE,"D33, D58 (seed design)","comms #1005, #1017; 2159c2e06",,"Pseudo-replication: 160 origins from 83 seeds, 45 exact duplicates"
D69,2026-09-29,P3,Bellerophon,GATE,OTHER,POSTREPORT,~1 d,DEF-BEL-004; arm re-read post hoc,D45 (decided by construction),"comms #980, #983",,Q4 host arm kept 'own stores' condition: a host copy fails by construction
D70,2026-09-29,P3,Odysseus,STAT,OTHER,POSTREPORT,~20 h,coordination 4/12 -> 8/12 (gate still MET),-,comms #1019; 6f5ac3192,,S3 RESULT counted only actions committed at submission (Artemis)
D71,2026-09-29,P3,Odysseus,INFRA,SELF-S,POSTRUN,recurred 3x,DEF-ODY-011 stop-gap,-,102569d24; 8efddb4b7,,Shared worker checkout between same-agent instances; add race burns an Attempt
D72,2026-09-29,P3,Hecate,STAT,SELF-L,POSTREPORT,hours,"12 of 29 worlds unattainable, not 11; ledger row",-,42169bad6,,Count error in probe round report
D73,2026-09-30,P3,Bellerophon,PROV,OTHER,POSTMERGE,~43 h (C4.2 09-28 10:39),BLOCKING; confirmatory label ALTERED; VALIDATED conditional only,"D60 (post-exposure, same arc)","comms #1044, #1050; d06059735",,E-003 VALIDATED rested on post-exposure C4.2 that removed the frozen 'P2 -> ALTERED' route; merge reviews were told to accept it
D74,2026-09-30,P3,Hecate,GATE,OTHER,POSTREPORT,~5 h,MAJOR; disposition stands,-,comms #1037; EVIDENCE_AUDIT_2026-09-30.md:39,,Pass 4 r2: W6 ORIG kill condition met by own ALT data but reported 'not fired'
D75,2026-09-30,P3,Hecate,RULER,SELF-L,POSTREPORT,~5 h,'zero UNFAMILIAR' relabelled an instrument result; F2,D57 (absence without positive control),e4a05ba3b; comms #1037,disc,Detector never calibrated on an UNFAMILIAR item; autopsy (operator CWO) and Harmonia found it within 6 min
D76,2026-09-30,P3,Hecate,BASELINE,OTHER,POSTRUN,~1 h,construct MAJOR; F3; ruler withdrawn,D16 (shortcut baseline),RULER_QUALITY_2026-09-30.md:50; cf70bbb05,,NOVELTY_DETECTOR_VALIDATED passable by a lookup baseline
D77,2026-09-30,P3,Tyche,GATE,OTHER,POSTRUN,~0 (audit before report),BLOCKING; labelled UNREACHABLE_BY_DESIGN; F1,"D30, D55 (unreachable/cannot-fail gate)","comms #1039, #1047; e72508448",,H1/H6 PASS unreachable: 3 valid worlds against a >=4 rule
D78,2026-09-30,P3,Tyche,RULER,OTHER,POSTRUN,~0,H3 negative arm labelled NON_DISCRIMINATING,-,RULER_QUALITY_2026-09-30.md:29,,Ecology growth alone moves the residual 0.04-0.13
D79,2026-09-30,P3,Harmonia,GATE,OTHER,POSTREPORT,~40 min,C-1: F1 amended (evolving baselines in attainable set),D77 (auditor commits the class it audits),comms #1047; 68c6e7f68,,Auditor's own H4 'nearly unattainable' rating wrong (Tyche)
D80,2026-09-30,P3,Odysseus,RULER,OTHER,POSTREPORT,~15 h,MAJOR -> F4 SANITY_CHECK_ONLY; RESULT corrected,-,comms #1038; 3eb8af06b,,"S3 quality non-inferiority clause at ceiling (9.1/10, margin 1); saturation disclosed by owner, classified by Harmonia"
D81,2026-09-30,P3,Ananke,PROV,OTHER,POSTMERGE,~24 h,MAJOR; F6 (freeze must be an earlier commit),"D40, D60 (exposure/freeze)",comms #1045; EVIDENCE_AUDIT_2026-09-30_SAMPLE2.md:91,,W-O PLAN.md first committed together with results
D82,2026-09-30,P3,Ananke,GATE,OTHER,POSTMERGE,~21 h,MAJOR; headline overclaims,D45 (by construction),comms #1045; SAMPLE2.md:99,,W-Q 'certifies all 42' was guaranteed by construction (own P3)
D83,2026-09-30,P3,Ananke,RULER,SELF-S,POSTRUN,same run,deviations and plan-rule defects recorded,-,478c9ec6f,,W-Y MAJ readout Kp[7] is not a carrier (always 0)
D84,2026-09-30,P3,Aether,STAT,OTHER,POSTREPORT,unknown,erratum; verdict unaffected,D72 (count/text),comms #1056; 9668f2813,,"RESULT text: lesion lower in all four seeds, not three"
D85,2026-09-30,P3,Harmonia,PROV,OTHER,POSTREPORT,~11 d (HARM-55 09-19),ERRATUM E-1; blob hashes listed; no score affected,"D10, D19 (CRLF hashing; lesson ledgered 09-11)","646cbcda8; comms #1072, #1076",,"Two artifact hashes were host-written CRLF, not blob hashes (Techne)"
D86,2026-09-30,P3,Bellerophon,GATE,OTHER,POSTREPORT,~1.5 h (#1078->#1113),reading relabelled UNRESOLVED; 5 claims WITHDRAWN; F8,D77 (unreachable kill; frozen 07:17 AFTER F1 04:50),"comms #1078, #1113; 6879b2236",,REPL-01 K3 founder-snapshot ruler could not PASS (content turns over in every arm); blinding honour-system
D87,2026-09-30,P3,Harmonia,GATE,OTHER,POSTREPORT,~2 h,C-2: audit J downgraded to SUPPORTED_WITH_DEFECTS,"D79, D86 (auditor misses own F1)",comms #1123; d3f99cfdc,,Audit J rated REPL-01 SUPPORTED and missed K3 reachability; Harmonia commit subject carried embargoed verdict
D88,2026-09-30,P3,Tyche,CONFOUND,SELF-L,POSTREPORT,~1 run,v1 F1 corrected; survival mechanism UNRESOLVED,-,6a28fc49e,,V0 included the 14-slot novelty/random reserve (membership unlogged)
D89,2026-09-30,P3,Theseus,LEAK,SELF-L,POSTRUN,~1 run,v0 FAIL stands; v0_1 corrected replication,-,308330aaf,disc,Lens leak into DEEP lanes; set-order nondeterminism
D90,2026-09-30,P3,Mnemosyne,LEAK,OTHER,POSTMERGE,unknown,custody defect routed to Harmonia/Aporia; no sealed artifact opened,-,comms #1128; 0b0759dba,lat,evidence_wiki gap_prospective_v1 sealed slate method inferable from public scores
D91,2026-09-30,P3,Odysseus,INFRA,OTHER,POSTMERGE,unknown,DEF-ODY-020..022 recorded; NOT implemented (CWO-B),D71 (fabric),comms #1119; bcb7a4d73,,Fabric script executor: timeouts lose all output; deterministic retries; head-of-line
D92,2026-09-30,P3,Ananke,GATE,OTHER,POSTMERGE,days,5 neutral fixes + 15 regression tests; C1 errata; no result changed,D45 (vacuous clause),41e386ccd; cc44f5903,disc,Harvest H-IMPL: handoff clause (b) passes vacuously on unscanned offsets; MAJ/XOR reach from sensor 0 only
```
