# CENSUS B -- competence acquisition in the non-Z80 engines

Currency: 2026-09-28. Odysseus research worker (disposable), ubu001, worktree odysseus-base-role
(HEAD 02800d2b5; origin/main 7720539d4). Directive:
roles/Odysseus/prompts/2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md s5 ("Produce a table of the
strongest surviving cases, not a rhetorical claim that there are none. If you find one real counterexample,
the census succeeds."). Ladder: roles/Odysseus/expedition/accumulation/ACCUMULATION_v0.md. Brief:
roles/Odysseus/frontier/poi/ready/R5_acquisition_census.md. Companion: CENSUS_A_z80.md (same directory; same
test and codes, reused here verbatim so the two tables can be merged).

Engines: Aphrodite, Cosmos/CWE, Ensorain/WTP, Ananke/PTE (incl. ARC3 workers W-G..W-L), Aether/AGE, Ares,
the historical line (Apollo, Hephaestus, Proteus VM, Archaeon WSE campaigns 1-6), Lexis.
Builds on, does not repeat: Artemis FR-043 / FR-044 (fresh-receiver ceiling; S4 speed-vs-ceiling),
FR-001 (construction landscape), FR-118 (W16), ENGINE_LENS_CARDS "How it has lied" fields.
Pure ASCII. Read-only census: no campaign, no host, no verdict of any seat changed. Numbers marked
COMPUTED-HERE are stdlib re-reads of committed rows made for this file (seconds each).

## 0. The test (identical to part A s0)

Q1 already encoded in primitives?        Q5 selection among pre-existing affordances only?
Q2 task installed (the paid task)?       Q6 a new reusable object generated?
Q3 solution template seeded (byte/func)? Q7 did the object change the CEILING for a FRESH receiver?
Q4 representation authored for it?       Q8 could a pristine system reproduce it at matched compute?

Codes: Y yes, N no, P partly, ? not in the record, - not applicable.
SURVIVES = absent from every seed/fixture by a functional check (Q3 not Y), not the named solution of a
paid task (Q2), more than one supplied primitive (Q1 not Y), not shown to be mere sampling of material
present at t=0 (Q5 not Y), no pristine/random baseline in the record reproduces it (Q8 not Y), and the
representation was not authored for it (Q4 not Y). R5's (d) replication is reported; weak replication =
"provisional".
FAILS(Qn) = the record decides Qn against the claim. UNDECIDABLE = the record cannot decide the deciding Q;
the single cheap check is named.
RUNG: no row in part B has had ACCUMULATION_v0's full controls (history-ablated twin, record deletion AND
permutation, producer destroyed, convention relabeling). "~" = the record's own control is analogous, not
the ladder's. A rung is the highest whose FALSIFIER the record's controls address. Speed-only transfer
can reach R2~/R3~ (the ladder does not require ceiling below R5); R5 needs (a)-(c) of s3 of the ladder.

Rows that are self-reported nulls (no competence claimed) are listed in s2.2, not scored.

## 1. Search log (mandatory prior-work search)

Commands (read-only). The first all-refs, all-paths pass (73 origin refs x 10 terms, unscoped) did not
finish in 600 s and was abandoned; it was replaced by:
(a) one-pass scoped grep on origin/main:
    git grep -I -i -o -E "acquire|acquisition|de novo|novel|emerged|endogenous abstraction|transfer|
    discovered|generalis|leverage" origin/main -- roles/Aphrodite roles/Cosmos prometheus/cosmos
    roles/Ensorain ensorain roles/Ananke roles/Ares ares Aether roles/Aether apollo agents/hephaestus
    roles/Proteus archaeon roles/Lexis roles/Artemis roles/Odysseus
    -> 171,480 occurrences. Per term (occurrences / distinct files):
       acquire 558/121; acquisition 503/132; "de novo" 66/25; novel 115,315/9,978 (dominated by
       "novelty" fields in ensorain and agents/hephaestus data); emerged 198/30; "endogenous abstraction"
       11/8; transfer 52,244/1,086 (dominated by field names in ensorain JSON and Aphrodite transfer arms);
       discovered 1,000/277; generalis 1,240/110; leverage 345/90.
       Per engine (top terms): ensorain 98,726; agents(hephaestus) 35,343; roles/Aphrodite 16,682;
       roles/Lexis 7,740; archaeon 6,706; apollo 4,808; Aether 370; roles/Ananke 343; roles/Ares+ares 65;
       roles/Cosmos 37; roles/Proteus 29.
(b) every origin ref with commits not on main (git rev-list --count origin/main..<ref> > 0), grep of the
    .md/.txt files that branch changes, terms as above minus novel/transfer (field-name noise):
       aphrodite/a16-campaign (5 ahead, 3 hit files), aphrodite/arc3 (24, 19), aphrodite/compounding
       (15, 14), aphrodite/frontier (7, 11), artemis/challenge (8, 7), bellerophon/multiday (9, 3; part A),
       chiron/base-role-adopt (4, 5), nestor/* (part A), vivarium/v0 (8, 18; SFE-era infra), harm55
       (image frames only). All aether/*, cosmos/*, ananke/*, archaeon/*, lexis/*, hephaestus/* refs are
       ancestors of origin/main (0 ahead), so their content is read from main.
Hits that became rows or were ruled out:
- "endogenous abstraction": roles/Aphrodite/engine/AMENDMENT_14 + APHRODITE_ENGINE_REVIEW_11 @7b2da226b
  (S3/S4) -> P3, P4. raw/I3_laws_rsi_worlds.md (Odysseus harvest; context only).
- "leverage": roles/Aphrodite/STATUS.md "TRANSFERABLE_SEARCH_LEVERAGE YES_LOCAL Tier 3B 47x, Tier 3C 345x"
  -> P1, P2.
- "de novo": apollo/pivot/recombination_findings_2026-06-16.md, archaeon/campaign1/SFE-05/RECORD.md ->
  folded into H1, H6; Lexis hits are prior-art bibliography (ruled out).
- "discovered"/"generalis": archaeon/campaign3/CAMPAIGN_REPORT.md @cb9135104 "THE DELAY LADDER BUILDS
  DELAY INVARIANCE" -> H8 (the strongest case below); roles/Cosmos "discovered law" -> C1, C2 (seat's
  own reversal: "a planted-invariant recovery, not a discovery").
- "transfer": archaeon/campaign2/CAMPAIGN_REPORT.md @4d80d4b1d (C1 transfer died under CRN) -> H6;
  roles/Ananke/pte/c1_report/REPORT.md @e35fb9704 "0 cross-family TRANSFER_SUPPORT" -> N1; Lexis G7
  "survives a change of author" -> L1.
- "acquire": roles/Ananke W-J/W-L notes; Artemis challenge ALIEN_CANDIDATES "what algebra the EVOLVED
  programs acquire" (a proposal, not a claim; ruled out).
- Branch-only: aphrodite/frontier K4_BUDGET_CURVE @282fb9000 (evidence for P4's Q7), aphrodite/compounding
  COMPOUNDING_SYNTHESIS @3c72f4144 (P6, P7), aphrodite/arc3 w3_novelty_reuse REPORT @11c0d44e5 (CON1
  forensics, P7), aphrodite/a16 AMENDMENT16 report @4f937e88f (P5).
- Prior syntheses read and cited, not redone: Artemis FR-043/FR-044 @4ea12f6a9 ("no in-ecology ceiling
  rise found anywhere in git"); FRONTIER.md @4ea12f6a9; ENGINE_LENS_CARDS @0b00e4312; Aphrodite's own
  K4/ARC3 synthesis ("A library in this apparatus is an enumeration-order prior").

## 2. The table (36 scored rows)

    ID  engine     claimed competence                         Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8  rung   verdict
    --- ---------  -----------------------------------------  -- -- -- -- -- -- -- --  -----  ---------------------------
    H8  Archaeon   delay-INVARIANT reader: trained on delays  P  P  N  P  P  Y  P  P   R1~    SURVIVES (provisional;
        WSE        0/1/2/4, reads never-trained d8 and d16                              (R2~   Q8 compute ~1.5x
                   at held-out 1.0 (11/12 seeds)                                         cand.) unmatched)
    H9  Archaeon   corridor delay_general -> W7_K2: imported  P  Y  N  P  P  Y  N  N   R2~    UNDECIDABLE (n=6;
        WSE        organisms speed a fresh population                                   (R3~   speed only)
                   (foothold median gen 20 vs 82; permuted                               hint)
                   control worse, 2/6)
    P4  Aphrodite  S4 abstraction transplant: donor-derived   Y  P  P  Y  Y  Y  P  ?   R3~    FAILS (Q4); ceiling
                   (acc + {H}) takes fresh recipients 0-1/16                            speed  part UNDECIDABLE
                   -> 16/16 on 5 unseen families at 250k                                       (FR-043 check)
    P3  Aphrodite  S3 endogenous abstraction (LGG derivation) Y  P  P  Y  Y  Y  -  P   R0~    FAILS (Q4, Q3~)
    P1  Aphrodite  "47x" Tier 3B search leverage              Y  Y  P  Y  Y  P  N  N   R2~    FAILS (Q7: speed,
                                                                                        speed  both arms 16/16)
    P2  Aphrodite  "345x" Tier 3C search leverage             Y  Y  P  Y  Y  P  N  N   R2~    FAILS (Q7; R3: random
                                                                                               shams 16/16 unseen)
    P5  Aphrodite  bounded RSI (A15/A17 E1)                   Y  Y  -  Y  -  N  -  -   NONE   FAILS (Q6: NEW=0, 8/8)
    P6  Aphrodite  A19 G1 stepping stone                      Y  Y  -  Y  P  N  N  -   NONE   FAILS (Q7: CAPABILITY 0/8)
    P7  Aphrodite  CON1 composed (v - (acc + {H})) solves     Y  Y  -  Y  Y  Y  P  P   R1~    FAILS (Q4 designer move;
                   2 families where L1 and PRISTINE fail                                       R3: SHAM_0 library equal)
                   at 10M
    C1  Cosmos     law A discovered, holds on sealed D/E/F    Y  Y  P  Y  Y  P  P  Y   NONE   FAILS (Q1/Q4: 97.5% =
                                                                                               hand law; Q8 active=random)
    C2  Cosmos     law B (v4), F BA .955                      Y  Y  P  Y  Y  P  P  ?   NONE   FAILS (Q4; 1 world, same author)
    N1  Ananke     routed-relay comm-dependent computation    P  P  N  P  P  Y  N  ?   R0~    UNDECIDABLE (Q8: no
        PTE        (RELAY .875-.893, 8/352 cells)                                              matched random search)
    N2  Ananke     in-flight packet memory for HOLD (M2)      P  Y  N  P  P  Y  N  ?   R0~    FAILS (Q5: a one-site
                                                                                               latch solves HOLD;
                                                                                               physics chose carrier)
    N3  Ananke     self-modifying timing-locked MAJ (M3,      P  Y  N  P  P  Y  N  -   NONE   FAILS (repl. 0/4; K3:
                   SETRULE)                                                                    configuration, not memory)
    N4  Ananke     integration MAJ (M4, .789)                 P  Y  N  P  P  Y  N  -   NONE   FAILS (did not reproduce)
    N5  Ananke W-H SETRULE switching expands capability       P  Y  N  P  P  Y  N  Y   NONE   FAILS (Q8: hand fixed
                                                                                               programs beat; 0/5 EXPAND)
    N6  Ananke W-J receiver operator: SUM champion .801       P  Y  N  P  Y  Y  N  ?   NONE   FAILS (Q5: 29/32 presence
                                                                                               codes identical across ops)
    N7  Ananke W-L n-back retention (n=1,2 pass 2/4 each)     Y  Y  N  P  P  Y  N  ?   NONE   FAILS (Q1: integrator
                                                                                               S0 += SENSE; selective
                                                                                               lag-2 0/4)
    E1  Ensorain   WTP-03 "9 flags = candidate physics"       Y  Y  P  Y  Y  N  N  Y   NONE   FAILS (Q8: N6 tuned ALS
                                                                                               beats all 9; seat: known
                                                                                               tensor completion)
    E2  Ensorain   PKG-F: obsolete history stored and ignored Y  Y  Y  Y  Y  N  N  ?   NONE   FAILS (Q3: "last 20%"
                                                                                               window handed in)
    E3  Ensorain   PKG-S1: learned bounded state reaches      Y  Y  N  Y  P  N  N  -   NONE   FAILS (Q4: HMM state
                   Bayes on Even process                                                       class authored)
    E4  Ensorain   WTP-LM01 learnability / surprise eviction  -  Y  -  Y  -  ?  ?  ?   NONE   UNDECIDABLE (not run;
                                                                                               FREEZE ee8cbe0c8)
    A1  Aether     rcv one-bit propagation (P_sust .047)      Y  -  N  Y  -  N  N  -   NONE   FAILS (Q1/Q4: "supplied
                                                                                               by the rule written to
                                                                                               produce it")
    A2  Aether     rcv_add / rcv_str NEW_BEHAVIOUR (N1/N2)    Y  -  N  Y  -  N  N  -   NONE   FAILS (Q1/Q4: conjunction
                                                                                               of two authored rules;
                                                                                               no content carried)
    A3  Aether     persistent native circuitry (AETH-02)      Y  -  N  Y  -  N  N  -   NONE   FAILS (Q1: out-degree-1
                                                                                               theorem; lesion 0.000)
    R1  Ares       C1 W4 recurrent-activation memory 10/10    P  Y  N  Y  Y  Y  N  ?   R1~    FAILS (Q5: carriers
                                                                                               supplied; portable 1/10)
    R2  Ares       C2 carrier choice (recurrence wins)        P  Y  N  Y  Y  N  -  ?   NONE   FAILS (Q5: NEW_CARRIER 0;
                                                                                               speed not capability)
    R3  Ares       W16 variable delay, plasticity in 5/9      P  Y  N  Y  Y  Y  N  ?   NONE   FAILS (Q5)
    R4  Ares       Gate C transplant into naive hosts         P  Y  N  Y  Y  Y  N  ?   R1~    FAILS (Q7: median
                                                                                               recovery 0.02)
    H1  Apollo     accuracy 0.392 -> 0.833 (5 widenings)      Y  Y  N  Y  Y  N  N  Y   NONE   FAILS (Q4: 5/5 human-
                                                                                               supplied; Q8 exhaustive
                                                                                               1.737M stops at .833)
    H2  Apollo     type bridge assembled by search (3/5)      Y  Y  P  Y  Y  N  -  ?   NONE   FAILS (Q4: bridge op
                                                                                               hand-built in June)
    H3  Hephaestus forged tools (LLM-written)                 -  Y  -  Y  -  Y  N  Y   NONE   FAILS (Q8: yield at or
                                                                                               below random 2.4%)
    H4  Hephaestus +11 / +32 pp reasoning engines             Y  Y  Y  Y  -  N  -  -   NONE   FAILS (Q4: human-written;
                                                                                               "human as inheritance
                                                                                               mechanism")
    H6  Archaeon   Campaign 1-2 transfer (SFE-01, SFE-07)     P  Y  N  P  ?  Y  N  Y   NONE   FAILS (Q8: died at n>=10
        WSE                                                                                    under CRN, 0/10 SUPPORTED)
    H7  Archaeon   import takeover (C3-SFE-10)                P  Y  N  P  -  Y  N  -   R1~    FAILS (R3: permuted
        WSE                                                                                    incompetent import 12/12
                                                                                               = mature 12/12)
    L1  Lexis      frozen "interface pair" survives change    Y  Y  Y  Y  -  N  P  ?   NONE   FAILS (Q4/Q6: LLM-authored
                   of author (+4/6, 24 permutations)                                           halves; nothing mined)

Counts (36 scored rows): SURVIVES 1 (provisional: H8); UNDECIDABLE 3 (H9, N1, E4); FAILS 32.
Highest rungs: R3~ (P4, speed only); R2~ (H9, P1, P2; H8 candidate). No row reaches R4, R5 or R6.

### 2.1 Row evidence (path@sha; all on origin/main unless a branch is named)

H8 -- delay-invariant reader.
- archaeon/campaign3/C3-SFE-03/RECORD.md @fe3c1647c, rows.json (same sha), C3-SFE-04/RECORD.md @e74b2f7aa,
  CAMPAIGN_REPORT.md:41-46,144-183 @cb9135104; precursor archaeon/campaign2/C2-SFE-06/RECORD.md:116.
- Claim: "11 of 12 seeds become general on delays 0/1/2/4 (held-out 1.0), and all 11 read delays 8 and 16
  -- never trained -- at held-out 1.0, while matched-budget direct search reaches d8 in 0/6 runs and d16
  in 1/6. Mature W0 solvers score 0.0 on both."
- COMPUTED-HERE (C3-SFE-03 rows.json): general_survives 11/12 (seed 10 fails; held-out R1 .19, R2 .04,
  R3 .06); gens_run per seed 112-197, mean 150.2, all at N=200, E=16 (PREREG.json). Generation-0 per-rung
  scores 0.00-0.21 in every seed (nothing general at t=0).
- COMPUTED-HERE (C3-SFE-04 rows.json): baseline (pristine direct search, G=100, N=200) W1_d8 foothold 0/6
  (held-out .02-.13); W1_d16 1/6 (seed 2 held-out 1.0, gen 52). So a pristine population DID produce a
  d16 reader once, at ~2/3 of the ladder's mean compute.
- Q1 P: expressible in the frozen 25-op VM (a reader, not a primitive; anatomy only structural:
  tick_budget 267.6 vs 82.1, conditional branch .818 vs .333, proteus/round2/ANATOMY_L0.md @e11e22370,
  uncorrected p). Q2 P: delays 0/1/2/4 were paid; d8/d16 never were. Q3 N: gen-0 is a random wse.gen0
  fill, no solution seeded. Q4 P: curriculum and delay knob authored; nothing authored for invariance.
  Q5 P: "In 5 of 12 seeds the first delay-1 battery promoted an organism the W0 population ALREADY
  contained" -- but that population was itself evolved in-run from random fill, so this is selection over
  in-run variation, not over t=0 affordances. Q6 Y: history-specific genomes. Q7 P: the fresh-receiver
  test (H9) is speed-only; d8/d16 are read by the same organism (generalisation, not transfer).
  Q8 P: the comparator is G100 against a ladder that ran 1.12-1.97x as many generations, n=6.
- Disposition in record: WEAK_POSITIVE, "the campaign's only reproducible positive capability and it is
  unexplained"; "the reader was never dissected" (H-D4-13, 72340f46d).
- Rung: R1~ (a lineage keeps and reuses its product on new cells; no deletion twin); R2~ candidate via H9.

H9 -- corridor to W7_K2 (C3-SFE-04 @e74b2f7aa).
- COMPUTED-HERE: W7_K2 foothold init_mature 5/6 (gens 24,11,20,25,7), baseline 4/6 (61,82,36,83),
  init_control (opcode-permuted, same manifests) 2/6 (95,38). Summits 0 in every arm (0/54 K=2 runs).
- Record: "restricted to W7_K2 ... 5/6 vs 4/6 ... inside noise at n=6"; "The permuted control being WORSE
  than no import is the sharpest capability signal in the campaign."
- Rung: consumer is a fresh population that did not make the genome; the benefit exceeds the no-import
  twin in time (R2~), and a capacity-matched permuted import does not supply it (R3~ hint). Ceiling: no
  arm reaches summit -> not R5. Caveat: the imported organisms are the carriers themselves (persistence
  into a new population), not an object passed to a non-producer after the producer is destroyed.

P4 -- Aphrodite S4 transplant.
- roles/Aphrodite/engine/S4_RESULTS_2026-09-23.json @65edc1251; APHRODITE_ENGINE_REVIEW_11 @7b2da226b;
  AMENDMENT_14 @4a6bbf55d; Artemis FR-043/FR-044 @4ea12f6a9.
- COMPUTED-HERE: DERIVED and POSITIVE_CONTROL are identical in 112/112 cells (charges, program,
  qualified): the derived library is functionally the designer's hand-written positive control.
- COMPUTED-HERE: unseen families, qualified/16 -- DERIVED 16 on all 5; PRISTINE 1,1,0,0,0; SHAM_0..6 0 on
  all 5; SHAM_7 (random schema (acc - {H})) 16,16,0,0,0; MEMORISE 1,1,0,0,0. PRISTINE's only unseen hits
  come from the G4 fallback at 244,880 and 215,960 charges; the earliest g4_fallback hit in ANY arm is
  215,960 -- i.e. PRISTINE's solutions begin just below the 250,000 escrow. The "0-1/16" is a cap edge.
- Branch aphrodite/frontier K4_BUDGET_CURVE.json @282fb9000 (different families, A17 catalog): PRISTINE
  solves 20/20 at 158k-11.9M charges; seat: "Capability gain is budget-relative: at a budget of ~12M it
  vanishes for these families."
- Not run: PRISTINE at larger escrow on the S4 families; recompute arm (PRISTINE + 6,916,141 meta-charges);
  scramble arm; any replicate of S4 (n=1 run, 16 recipients/arm).
- Rung: fresh recipients with no donor state (condition 8) beat the no-library twin (R2~); 7 of 8
  equal-size random libraries do not supply the benefit (R3~ partial; SHAM_7's near-equivalent schema
  does). All in speed at a censored budget. Verdict FAILS(Q4): hole grammar, one-hole LGG rule and G4
  authored; "A counterfactual LGG over the observed bodies alone ALSO yields (acc + {H})".

P3 -- S3 derivation: S3_ARTIFACT_2026-09-23.json @52dad4db7; AMENDMENT_14 @4a6bbf55d; A17 re-derivation
  3/3 (branch aphrodite/a16 @4f937e88f). Content = positive control; derivation rule authored.
P1/P2 -- 47x/345x: APHRODITE_ENGINE_REVIEW_9 @4d87b0bd4 (989 vs 46,105 charges, both 16/16; "a pure
  search-cost effect at identical discovery probability"); REVIEW_10 @4469736ca (167.6 vs 57,923, both
  16/16; SHAM_0/SHAM_5 solve both unseen families 16/16; "The donor never formed an abstraction");
  AMENDMENT_13 @4a6bbf55d (search order seeded from library NAME; 345x never re-run under keyed order).
P5 -- AMENDMENT_15 @aaae70067 ("BRSI = NO"); A17 E1 NEW=0 in 8/8 (branch aphrodite/a16 @4f937e88f).
P6/P7 -- branch aphrodite/compounding COMPOUNDING_SYNTHESIS @3c72f4144 (A19 ladder REACHABLE 8/8, SELECTED
  4/8, SOLVED 0/8, CAPABILITY 0/8; CON1 1 replicate, "L1 and PRISTINE BOTH failed at 10M"); branch
  aphrodite/arc3 w3_novelty_reuse/REPORT.md @11c0d44e5 ("CON1 is a SHAM_0 re-derivation ... solved
  equally by SHAM_0's library (4.7-54.5k)"; composition-OFF control matched or beat G1).
C1/C2 -- roles/Cosmos/campaigns/HANDOFF_2026-09-23.md @94a0efa83, research/RESULTS.md @917edba0a,
  calibration/LEDGER.md @940b486f2 ("active 0.790 vs random 0.788"), c0e/PREREG.md (post-hoc hand law,
  agreement .975 D/E). Sealed D/E/F BA .983/.972/.930 vs 5-NN .84/.77/.84, but "ALL SIX WERE AUTHORED BY
  COSMOS". C3 (P1/P2 memory certificate) is an instrument, not a competence: not scored; Nestor's holdout D
  (a56ef7787, on main) is now EXPOSED; no C3 adjudication exists.
N1..N4 -- roles/Ananke/pte/c1_report/REPORT.md @e35fb9704 (8/352 COMM_DEPENDENT; zero_comm .5 in 4/4;
  0 cross-family transfer; random-graph .500; headline RELAY law bbef66a1 REPRODUCED=False [.572,.506];
  re-evolving at N=400 reaches .619); c1b/REVIEW_PACKET_PTE_C1b.txt @cc98596dd (flush -> .497; 3/3 fresh
  seeds); c1b/CORRECTIONS_2026-09-27.md @c34cbb463 (K1, K3). N1 Q8: the only random comparison is the A0
  census (64 random genomes/cell, "~0.1% reach the readout") against a GA budget of 96 x 36; matched
  random search is backlogged (ANANKE-14).
N5..N7 -- roles/Ananke/research/workers/W-H @3aa3caf90 (hand S2 .999 vs champion .755; champion budget
  reproduces 0/4 seeds); W-J @46dc8f25a; W-L @d8ef2dc5b ("What it reaches is integration ... not selective
  lag-n retention"; 16-line hand plant 1.000); SYNTHESIS_2026-09-28_ARC3.md @7fc642367 ("SEARCH
  REACHABILITY, NOT PHYSICS, bounds what PTE shows"). W-G @b0985cd10 null, W-I descriptive, W-K
  instrument: not scored. Note: the W-G..W-L deposits of 2026-09-27/28 are Ananke/PTE workers under
  roles/Ananke/research/workers/, not Ensorain.
E1..E4 -- ensorain/ENSORAIN_WTP03_REPORT.md @a65d27ced (N6 beats all 9 by .22-2.28 AC; 174/181 admitted
  worlds mutants of 13 founders); ensorain/arc3/RESULTS_PKGF_PROBE.md @844e04d4a; arc3/suff/
  RESULTS_S1_PILOT.md @76ed421b5 (result JSONs not committed); ensorain/PREREG_WTP_LM01.md @ee8cbe0c8.
A1..A3 -- Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md and RCV_REINTERPRETATION_2026-09-27.md
  @77b11cef5; Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md @0e63a3d52; NATIVE_CIRCUITRY_01 @63ec2f56e.
  Aether runs no search, so Q2/Q5/Q8 are "-".
R1..R4 -- ares/ARES_CYCLE1_REPORT.md @8ba05b2c8; ares/ARES_CYCLE2_REPORT.md @3f68be2b9;
  roles/Ares/REVIEW_PACKET_C2_2026-09-23.txt @1dde117f7 (only_recur 10/10, only_plast 10/10, only_keep
  9/10, none 0/10: "a SPEED phenomenon, not a capability one"; Gate C per-pair median recovery 0.02,
  portable 4/9). The "40 vs 33.75" basin comparison is internally inconsistent in the report (FR-001).
H1..H4 -- apollo/pivot/APOLLO_REVIVAL_REVIEW_2026-09-01.md @96ee6fac8 ("5 were agent/human-supplied and 0
  were self-found"; Charon 0.0667 vs home 0.600); apollo/cycles/type_bridge/LINEAGE.md @8d06112b7;
  engine/necropolis/dossiers/hephaestus.dossier.json @c7340a6ad; roles/Hephaestus/ABLATION_CARD_2026-08-19.md
  @11e919e20.
H6/H7 -- archaeon/campaign2/CAMPAIGN_REPORT.md @4d80d4b1d; archaeon/campaign3/C3-SFE-10/RECORD.md
  @9b539dfe4 ("IMPORT TAKEOVER IS MECHANICS, NOT CAPABILITY").
L1 -- roles/Lexis/notes/G7_CHARON_2026-09-01.md @ab0371e7c; handoff/REVIEW_PACKET_CLOSEOUT_2026-09-01.txt
  ("HANDED OFF, NOT ADMITTED"; "Two authors is two, not 'general'").

### 2.2 Self-reported nulls (not scored; no competence claimed)

Aether FIRST_LIGHT (75bc0315b: "No endogenous dynamics"); Ananke XOR/FLIP 0/83, 0/82; Ananke W-G
"NO nontrivial retention regime"; Proteus VM 0/5,472 single edits improved a parent
(archaeon/campaign4/C4-01/READOUT.md @9542fa37a); Archaeon Campaign 6 detectors (6 of 11 never shown to
fire; instrument, FR-059); Cosmos C3 certificate (instrument).

## 3. Strongest surviving cases, ranked by rung

1. H8 -- Archaeon WSE delay-invariant reader. SURVIVES (provisional). Rung R1~, R2~ candidate.
   The one part-B competence that was not seeded, not paid (d8/d16 never trained), not a single primitive,
   not authored, and not reproduced by the record's pristine baseline at the record's budget (d8 0/6).
   It generalises beyond its curriculum by a factor of 4 in delay. What keeps it provisional: the
   comparator had ~2/3 of the ladder's mean compute, n=6, and a pristine run found a d16 reader once;
   nobody has dissected the reader (it may be a delay-blind read that the delay knob never made hard).
   If check 1 below leaves it standing, it is part B's counterexample to "no competence was acquired",
   at the level of an individual lineage -- not yet an accumulated object.
2. P4 -- Aphrodite S4. FAILS(Q4) as acquisition, but it is part B's highest-rung ACCUMULATION case: an
   object produced in-run by a donor, handed to fresh recipients with no donor state, beats the
   no-library twin, and 7/8 equal-size random libraries do not substitute (R3~). Everything is speed at
   a 250k cap; COMPUTED-HERE shows PRISTINE's first solutions sit at 216k-245k, so the "ceiling" is the
   cap edge, and K4 (other families) removes it by ~12M. Its content equals the designer's positive
   control in 112/112 cells.
3. H9 -- WSE corridor to W7_K2. UNDECIDABLE. R2~ with an R3~ hint (permuted import worse than none).
   Speed only; n=6.
4. N1 -- PTE routed relay. UNDECIDABLE on Q8 only; in-task, topology-bound, no transfer (Q7 N), headline
   law not reproduced. Rung R0~ at best.

Pattern (hypothesis, stated once): every part-B object that transfers to a fresh receiver transfers
SPEED inside a representation that already contains the solution (Aphrodite: "a library is an
enumeration-order prior"; WSE: time-to-foothold; Ares: portable 4/9). The one survivor (H8) is a
generalisation inside a lineage, not an object passed on. With part A (A1, N5, N1 at R1~), the program's
frontier sits at R1~ for acquisition and R3~-speed for transfer; R4-R6 are unobserved.

## 4. Decisive cheap checks (ordered by information per CPU)

1. H8 matched-compute recompute arm (minutes). Rerun C3-SFE-04's baseline arm on W1_d8 and W1_d16 at
   G=200 (>= the ladder's max 197 generations), N=200, E=16, 12 seeds each; SFE-04's 66 runs x G100 took
   881 s, so ~24 runs x G200 is ~10 CPU-min. Also probe the one pristine d16 reader (SFE-04 baseline seed
   2) on d0/1/2/4/8 (0.3 s direct probe). Decides Q8: >= 3/12 pristine d8 readers => H8 FAILS(Q8) (the
   ladder is speed); <= 1/12 => H8 SURVIVES at matched compute. Add, in the same session, the never-run
   population-level probe (C4-2 / H-D4-14): evaluate the W0-hold populations' members on d8/d16 before
   the first delay-1 battery (selection vs construction, Q5).
2. H9 n-raise (minutes). Repeat the W7_K2 three-arm corridor (init_mature, baseline, permuted control)
   with 12 more seeds (36 runs x G100, ~8 CPU-min). Decides whether R2~/R3~ hold beyond n=6 (and adds a
   deletion arm by importing mature organisms with the reader block zeroed).
3. P4 ceiling check (FR-043's A0'; CPU-hours, not minutes). PRISTINE on the five S4 unseen families at
   escrow 2.5M and at B + 6,916,141 (the recompute arm), 16 recipients, using the K4 harness
   (k4_budget_curve.py @282fb9000). Prediction from COMPUTED-HERE (PRISTINE hits already begin at 216k):
   >= 14/16 per family at 2.5M, i.e. S4 is speed. 0-1/16 would make P4 the program's first R5-shaped
   candidate.
   Also cheap: N1 matched random search (ANANKE-14): 96 x 36 = 3,456 random genomes per RELAY cell
   through the existing CPU oracle.

## 5. Limits

- No ACCUMULATION_v0 control set (history-ablated twin, deletion AND permutation, producer destroyed,
  convention relabeling) was run on any part-B row; every rung carries "~". R3~ on P4 rests on random
  shams only (no permutation of real libraries between donors, no convention test).
- Q7 in the directive asks for a CEILING change; the record almost never runs the budget sweep that
  separates ceiling from speed. Where only a capped budget exists, Q7 is P or ?, not N.
- The all-refs unscoped grep did not complete (600 s); the scoped main pass plus the branch-diff pass
  cover every engine path named in the brief. "Not found" means a bounded grep.
- Archaeon C3 per-organism genomes for H8 are in rows.json (elite_manifest) but the reader was not
  dissected here; no VM was run.
- Ensorain PKG-F / S1 result JSONs are not committed; those rows rest on the reports.
- Cosmos's withheld C3 session-1 branch is local-only on its host and was not read.
- The COMPUTED-HERE numbers are re-tallies of committed rows (S4_RESULTS json, C3-SFE-03/04 rows.json);
  they check the records' arithmetic and add the DERIVED == POSITIVE_CONTROL identity and the PRISTINE
  cap-edge timing, nothing else.
- No verdict of any seat is changed; this file classifies evidence against a stated test.


## ADDENDUM 2026-09-28 (Odysseus): H8 decided by S7's matched run
H8 FAILS(Q8): at G=200 (matched compute), pristine direct search reaches a
W1_d8 reader in >= 5 of 12 seeds (rule: >= 3/12 => FAILS). The ladder was
speed. Part B now has NO surviving acquisition case (SURVIVES 0,
UNDECIDABLE 3, FAILS 33). See S7_h8_matched/RESULT.md addendum.
