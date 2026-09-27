# I6 -- The graveyard: recurring failure shapes across Prometheus

Currency: 2026-09-27. Author: research delegate for Odysseus (read-only
pass over worktree odysseus-base-role @ 22bfbc966). Pure ASCII.
Paths are repo-relative. "L" means line numbers in that file at this SHA.
Anything not read directly off a file is marked INFERRED. The shape
classification of each row is my own reading (INFERRED as a
classification); the facts in each row are cited.

Sources read: all 40 calibration ledgers (roles/*/calibration/LEDGER.md,
roles/*/CALIBRATION.md, roles/*/calibration/CALIBRATION.md);
roles/Artemis/threads/sfe_retrospective/ENGINE_LENS_CARDS.md and
notes/C_engines.md; archaeon/causal_lens/FALSE_FRIENDS.md,
PORTABILITY01_REPORT.md, V02_REGRESSION_REPORT.md; roles/Nestor/FINDINGS.md;
roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md;
roles/Ananke/pte/C1_ERRATA.md; programs/selective_irreversibility/ANOMALIES.md;
Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md; Aether/AETH-03/PHYSICS_DESIGN_0{1,2};
ensorain/ENSORAIN_WTP03_REPORT.md, WTP02_OPERATOR_RULING.md, PREREG_WTP_LM01.md;
roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt;
roles/Crius/REVIEW_PACKET_C2_TERMINAL_2026-09-23.md; ares/ARES_CYCLE{1,2}_REPORT.md;
archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md; archaeon/envgate2/VERDICT_2026-09-26.md;
pivot/CORRECTION_2026-08-31_action_divergence_withdrawn.md;
pivot/CORRECTION_corpus_signature_claim_2026-08-22.md;
pivot/calibration_v3c_VERDICT_generator_category_error_2026-06-03.md;
SerendipityFoundry/stackvm_admission/VERDICT_CORRECTION.md;
ergon/detector_transfer/08_AVIDA_CORRECTION.md;
aporia/docs/FINDING_2026-08-17_decidability_novelty_correction.md;
herakles/HERAKLES_HISTORICAL_COLLIDER_V0/HC_R01_CORRECTION_2026-09-03.md;
cartography/docs/metric_correction_20260413.md;
roles/base-role/RESPONSIBILITIES.md L30-73; bellerophon multiday branch
(prometheus/z80atlas/*.py @ a3086cece, MULTIDAY_PREREG.md @ 12ce26e23).
NOT read in full: the ~150 review packets under pivot/, SerendipityFoundry/,
ergon/, agent_d*_blind/, evidence_wiki/ (sampled only; see s6 gaps).

-----------------------------------------------------------------------

## 0. Shape codes used below

    SC  STALE / WRONG COMPARATOR -- the reference state, baseline, config
        or population is not the one the claim is about.
    LP  LABEL MISTAKEN FOR PROPERTY -- a field name, status word, arm
        name or certificate is read as the quantity it names.
    LM  LOCATION (or executing context) MISTAKEN FOR MATERIAL -- where a
        thing sits or who ran it is read as what it is / whose it is.
    HG  HOST CREDITED FOR ITS GUEST (or guest for host) -- work done by
        the world, a host, an operator or the probe is credited to the
        organism, or the reverse.
    AS  AUTHOR SMUGGLES THE ANSWER -- the experimenter's construction
        (generator, coordinates, probe set, expected mechanism) already
        contains the result; rediscovery read as discovery.
    WR  WINDOW MISSES THE READOUT -- the measurement is taken at the wrong
        time/phase relative to the causal event, or the intervention is
        never handed to the measurement.
    VC  VACUOUS CONTROL / OUTCOME FORCED BY CONSTRUCTION -- a control,
        ablation, gate or "check" that could not have come out otherwise.
    TB  TRIVIAL OR TUNED BASELINE NEVER RUN -- a constant, running mean,
        random walker, reflex, or tuned same-class estimator matches or
        beats the claim.
    PS  POOLED STATISTICS HIDE PER-GROUP FAILURE -- pooling across
        families, days, blocks or states manufactures or hides the effect.
    SO  SELECTION ON THE OUTCOME -- a conditional rate behind a trigger or
        admission gate read as a base rate; best-of-N read as typical.
    PR  PSEUDO-REPLICATION -- non-independent units (events, seeds,
        attacks, founders, agreeing sources) counted as independent.
    DM  DEGENERATE METRIC -- saturates, is near-constant, has the wrong
        denominator, or rewards abstention.
    SA  SILENCE / ABSENCE READ AS A NULL -- a record that goes quiet when
        the instrument breaks, or a truncated search, read as "nothing".

-----------------------------------------------------------------------

## 1. Table of reversals

Engine names: NPE = Nestor Z80 world; BEE = Bellerophon z80atlas; AGE =
Aether; CWE = Cosmos; WTP = Ensorain; PTE = Ananke; ARC = Archaeon
(ENVGATE + causal lens); SFE = Serendipity Foundry Engine. Non-engine seats
are named directly. Primary shape first.

| id | engine/seat | original claim | what cut it down | shapes | evidence |
|---|---|---|---|---|---|
| R01 | NPE | 1,031 unseeded populations produced spontaneous replicators (all ADMISSIBLE) | all 1,031 were PAIR_EXECUTION; fidelity read after `_mutate`, so the recombination splice made the match in 6,287/6,547 events; P-11 reassay leaves 57, max depth 2 | HG, WR, LP | roles/Nestor/FINDINGS.md L19-41, L192-195, L207, L417-418 |
| R02 | NPE | event counts (>=10 in 308 runs) show replication propagates | events are not lineages: max chain depth 1 in 911/1,031 | PR | roles/Nestor/FINDINGS.md L25-31 |
| R03 | NPE | A-4 endogenous-only accessibility (held 1.0 vs matched control 0.0) | control summary kept per family: 64 of 65 flags judged against a control not run for them; exact matched control crossed first; runtime gap was a frozen population | SC, PR | roles/Nestor/FINDINGS.md L74-82, L197-201, L206 |
| R04 | NPE | FORCED_READ vs ANSWER_BEFORE_READ is a read-order contrast | FORCED_READ passes `v XOR key`: the two arms score different targets | LP | roles/Nestor/FINDINGS.md L60-72 |
| R05 | NPE | C9 H1 four-arm gate test | `world.Runner` never passed output_gate/cue_cost into the task; four arms identical to the last decimal | WR, VC | roles/Nestor/FINDINGS.md L261-263, L422 |
| R06 | NPE | runaways are "founder-descended" (anc share ~1.0) | byte provenance: median 13% founder material; in 17/19 populations no organism is half founder bytes -- lineage descent, not content | LP, HG | roles/Nestor/FINDINGS.md L362-366 |
| R07 | NPE | C-CRITICAL-MASS: 4 founders superadditive (p ~1e-6) | baseline p1=5/80 plugged in as exact; declared dose curve fits independent tickets (LRT p=0.42) | SC | roles/Nestor/FINDINGS.md L301-303, L430-432 |
| R08 | NPE | H3 certificate tracks heredity by id | on the pair tape an id keeps while bytes are replaced (0.97 -> 0.00 by epoch 600) -- certifies identity, not heredity | LP, LM | roles/Nestor/FINDINGS.md L217 |
| R09 | NPE | founder causal depth (>=20) separates kinds of heredity | per-edge certification break rate p caps unbroken chains at ~1/p; depth measured luck | DM | roles/Nestor/FINDINGS.md L383-388 |
| R10 | BEE | 72 h campaign (63,247 runs, 1,629 flags): 5 flag classes; "endogenous not external"; topology/pollination effect | all 5 classes collapsed; EXTERNAL 178 vs ENDOGENOUS 2 (p 2.5e-15); pollination = defect P1, migration spawned world-made copies (extinction 0/150 v1 vs 148/150 v2) | HG | roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md L22, L73-77; roles/Artemis/threads/sfe_retrospective/notes/C_engines.md L452-456 |
| R11 | BEE | 90% of spontaneous origins sustain | 90% came from the trigger-selected subset; unselected 39.4% | SO | GROUNDING_REPORT.md L56-58, L144 |
| R12 | BEE | replication is task-independent (six task cells) | five of six cells run-for-run identical; task causally inert under IMPLICIT pressure; one estimate, not six | VC, PR, LP | GROUNDING_REPORT.md L50-55 |
| R13 | BEE | NOP-ablated seeded tapes stop replicating (HISTa) | 126/345 still replicate; copier usually one mutation away | VC | GROUNDING_REPORT.md L29, L32, L103; notes/C_engines.md L434-436 |
| R14 | BEE | own-code self-replication (SR) criterion: copy ops ran from own code (pc < L) | 38,817 native-SR births are lens-DECOUPLED; by code MATERIAL 27,083 of 28,163 "foreign-governed" births are own-material (B6) | LM, LP | archaeon/causal_lens/V02_REGRESSION_REPORT.md L93-110; FALSE_FRIENDS.md L43, L50 (FF-28, FF-30) |
| R15 | BEE | `material = target` identifies where a child's bytes came from | positional resemblance heuristic; 847,000 births where the writer copied >= L/2 own bytes out of position | LP | archaeon/causal_lens/FALSE_FRIENDS.md L12, L42 (FF-4, FF-27) |
| R16 | AGE | per-field opcode change rate 0.020-0.024; STATE_CHANGING 27.1% | runner refreshed `prev` only at sample emission: every comparison was against state 250 ticks old; opcode rate +128% | SC, WR | roles/Aether/calibration/LEDGER.md L89-109; Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md L225-252 |
| R17 | AGE | "observer consistency check" (changed_by_field == STATE_CHANGING) | algebraic identity: same expression in two functions | VC | AETH-02_CLOSE_2026-09-24.md L256-266 |
| R18 | AGE | full-ring starvation blocks propagation 0/128 vs sham 17/128 (falsifier) | forced by the law: zero-energy sites cannot emit | VC | roles/Aether/calibration/LEDGER.md L136-150; Aether/AETH-03/PHYSICS_DESIGN_02_2026-09-26.md L266-280 |
| R19 | AGE | 3.1x edge-lifetime gap vs null | null model lacked source starvation (89% of terminations) | SC, TB | Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md L22, L100-111 |
| R20 | AGE | template change is intrinsic copy dynamics; H3-P2 field prediction | perturbation supplies ~42% of change immediately, ~95% cumulatively; arg1 mod 5 addressing makes every arg1 flip retarget | HG | notes/C_engines.md L512-515; roles/Aether/calibration/LEDGER.md L124-134 |
| R21 | CWE | law A is a discovered cross-substrate law (sealed D/E/F BA .983/.972/.930) | 97.5% agreement with the hand-derived task economics; one author wrote every substrate incl. sealed ones | AS | roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt L23-26, L122, L168, L196-198 |
| R22 | CWE | G6 intervention FAIL 0/12 | engine assumed a single flip; law is a band; retest 12/12 | LP, VC | roles/Cosmos/calibration/LEDGER.md L15 |
| R23 | CWE | G6 magnitude gate is a test | a constant prescription f=2 scores 10/12 (gate needs 8) | TB | roles/Cosmos/calibration/LEDGER.md L14 |
| R24 | CWE | laws passing pooled residuals | location gate killed 3 laws with 2-4% contradiction | PS | notes/C_engines.md L594; ENGINE_LENS_CARDS.md L143 |
| R25 | CWE | active sampler / cost lines beat random | .790 vs .788; lines 0.767 vs random 0.946 | TB | roles/Cosmos/calibration/LEDGER.md L11, L20 |
| R26 | CWE | repeated adversary rounds = independent survival evidence | 3 of 4 rounds re-fired the same deterministic attacks | PR | roles/Cosmos/calibration/LEDGER.md L18 |
| R27 | CWE | C1->C2 "method improvement" | seed: no-lines/no-selection cells survived | PR | roles/Cosmos/calibration/LEDGER.md L22-23 |
| R28 | CWE | adversary evaluated law v2 | used v1 coordinates (defect I1) | SC | roles/Cosmos/calibration/LEDGER.md L13 |
| R29 | WTP | WTP-01 top 3 replicated anomalies | competence normalised by CURRENT field variance: a catastrophe-zeroed world is "perfect" | DM | roles/Ensorain/calibration/LEDGER.md L21 |
| R30 | WTP | WTP-01 best genuine competence | a 508-float table in a 72-cell world (memory > world) | AS, DM | roles/Ensorain/calibration/LEDGER.md L22 |
| R31 | WTP | WTP-02 EXPAND (mechanical scorer) | a one-float running mean passed replication, structure dependence, autopsy, transfer; V1-V4 never tested a constant | TB, VC | roles/Ensorain/calibration/LEDGER.md L24-25; ensorain/WTP02_OPERATOR_RULING.md L1-12 |
| R32 | WTP | WTP-03 "CANDIDATE PHYSICS FOUND", 9/9 flags | all 9 are bounded online approximations of known completion; post-data tuned N6 beats all 9; admission pre-selects completion-friendly worlds | AS, TB, SO | ensorain/ENSORAIN_WTP03_REPORT.md L22-35, L65-81, L143-159 |
| R33 | WTP | 181 admitted worlds; 358 wave-B crossovers | 174/181 mutants of 13 founders (n_eff 13); 0/12 crossovers replicated (seed noise) | PR | ENSORAIN_WTP03_REPORT.md L151-152; roles/Ensorain/calibration/LEDGER.md L29 |
| R34 | WTP | same-field transfer is informative | near-tautological: 9/12 transfer | VC | roles/Ensorain/calibration/LEDGER.md L31; ENSORAIN_WTP03_REPORT.md L135 |
| R35 | WTP | E1 positive control would pass | it inherited a random-search miss from the tuned arm | SC | roles/Ensorain/calibration/LEDGER.md L13 |
| R36 | WTP | fossil lane 2^4 factorial varied credit delay | specimen's native delay was already 0: both levels identical | VC | roles/Ensorain/calibration/LEDGER.md L27 |
| R37 | WTP | D3 planted control supports the restructuring mechanism | a planted control validates the instrument, not the seat's mechanism story | AS | roles/Ensorain/calibration/LEDGER.md L19 |
| R38 | PTE | C1 M3 "packet ablation: no effect" -> SETRULE/self-modifying MAJ | ablation window [t0, readout) never covered the readout tick; delay == delta == 4 made the null vacuous by construction | WR, VC | roles/Ananke/pte/C1_ERRATA.md L6-15; programs/selective_irreversibility/ANOMALIES.md (2026-09-25T23:45Z, 2026-09-26T04:40Z) |
| R39 | PTE | "frozen routing: no effect" | under dest_mode "all" w is never read | VC | roles/Ananke/pte/C1_ERRATA.md L16-19 |
| R40 | PTE | M2 held bit "not in any site" | memory ablation reset only S; per-carrier resets show in-flight carrier | VC, LP | roles/Ananke/pte/C1_ERRATA.md L20-22 |
| R41 | PTE | exact per-world balance makes every constant policy 0.5 | targets anti-correlated; copy-last 0.346, so opposite-of-last ~0.65 with no adaptation | TB | roles/Ananke/calibration/LEDGER.md L10 |
| R42 | PTE | CAUSAL_SUPPORT defined by the family's expected control | two of the three most interesting mechanisms labelled NOT_SUPPORTED because not the assumed mechanism | AS | roles/Ananke/calibration/LEDGER.md L16 |
| R43 | PTE | 22 HOLD "transfers" | HOLD reads neither varied parameter: the training condition re-ran | VC | roles/Ananke/calibration/LEDGER.md L17 |
| R44 | PTE | boundary criterion applied to every dial | fires on categorical dials, zero-variance metrics, single dips | DM | roles/Ananke/calibration/LEDGER.md L12 |
| R45 | ARC | ENVGATE-01 GATING_CAUSALLY_SUPPORTED (rescue by byte 128) | 69/70 RESCUE establishments are host-labelled lineages in ONE takeover world started by a 255-gated copier; block-level p = 0.5 | HG, PS | archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md L6-40 |
| R46 | ARC | parent-chain lineage = descent | label = executor; parent-chain 8-42x genetic establishments; 23 host labels = one genetic lineage | HG, LP | archaeon/causal_lens/FALSE_FRIENDS.md L9 (FF-1) |
| R47 | ARC (lens) | v0.1 adapters: NPE donor material > 1/2 in 20/34; PTE 11/16 crossovers no majority parent | donor_authored_share is context, not material: 9/34; mask decides provenance: 1/16 | LM, LP | archaeon/causal_lens/FALSE_FRIENDS.md L51-53 (FF-31..33) |
| R48 | Ares | cycle 1 "10 seeds" | seeds 1-3 reproduce cycle-0 lineages byte for byte: 7 independent | PR | ares/ARES_CYCLE1_REPORT.md L29-31 |
| R49 | Ares | cycle-2 arm scores (final.heldout); GATE C median recovery 1.0 | champion argmax over 128 on the held-out set (shuffled controls 4.22/13.47 vs clean 0.00); best donor of 9 (per pair 0.02) -- gate SHUT | SO | roles/Ares/calibration/LEDGER.md L20-21; ares/ARES_CYCLE2_REPORT.md L190-194 |
| R50 | Ares | W4 plasticity 0/10 (replicated) | fresh lineages 4/10; single n=10 coarse instrument | PR | roles/Ares/calibration/LEDGER.md L23 |
| R51 | Ares | "no_state" removes within-lifetime memory | plasticity intact; nostate scored ~33 near cap | LP, VC | roles/Ares/calibration/LEDGER.md L12 |
| R52 | Ares | shuffled W2 floor "cannot exceed 60"; W5 shuffled ~0 | reward reflex reaches 75-80; second binary draw unbalanced (cue reflex 0.59) | TB | roles/Ares/calibration/LEDGER.md L11, L14, L16 |
| R53 | Ares | recurrence = "mechanisms no human conceived" | textbook; defensible claim is "undesignated by the experimenter" | AS | roles/Ares/calibration/LEDGER.md L18 |
| R54 | Ares | GATE B superiority rule | an apparatus that never learns would score as evidence for superiority | VC | roles/Ares/calibration/LEDGER.md L19 |
| R55 | Crius | H count for the typed control | invocation log recorded register R0, not PINVOKE's argument (parg) | LM | roles/Crius/REVIEW_PACKET_C2_TERMINAL_2026-09-23.md L19-22 |
| R56 | Crius | C0_EFFICIENCY orders reuse > brute force > quitting | orders quitting first; rewards abstention | DM | roles/Crius/calibration/LEDGER.md L13 |
| R57 | Crius | seeded arm 20-24/50; brute force impossible on chains | RANDOM stride walkers solve a third of chains by luck | TB | roles/Crius/calibration/LEDGER.md L14-15 |
| R58 | Crius | rung C gate passed | driver read receipt existence, not its verdict field | LP | roles/Crius/calibration/LEDGER.md L22 |
| R59 | SFE | the hash chain records the research act | ledger went silent exactly when the engine broke: a 13-row gap that would read as a property of rule space | SA | ENGINE_LENS_CARDS.md L93-98 |
| R60 | SFE/ARC | Campaign 1 transfer positives | died at n >= 10 under common random numbers (0/10 supported) | PR | notes/C_engines.md L278-280 |
| R61 | Apollo | Lever 1 aggregate falsified; 0.558 plateau = wall; E9 blackboard reasoning; archive coverage 0.172 = differentiation | guard on a field nothing writes; metric structurally capped ~0.56; 0.0476 on Charon's blind battery; MAP-Elites made 19% coverage from a DEAD world | VC, DM, AS, TB | roles/Apollo/CALIBRATION.md L16-17, L19, L22 |
| R62 | Hephaestus | ~1,960 novel reasoning tools; causal_trace is R5; gauntlet exhaustive verification | ~5 mechanisms; keyword match (R1); comparison hard-wired to bool() -- every vector output matches | LP, VC | roles/Hephaestus/CALIBRATION.md L12-16, L39-56 |
| R63 | Nous | self-rating (1-10) and novelty are selection signals | rating near-constant (57.7% one value; z=+1.28 between its own classes); novelty "existing" 4/5,918 | DM | roles/Nous/CALIBRATION.md L14-53 |
| R64 | Harmonia D | closure-novelty meter | scores false and timeout as novel: a timeout detector | DM, LP | aporia/docs/FINDING_2026-08-17_decidability_novelty_correction.md L68; aporia/docs/META_SYNTHESIS_2026-08-12_v1.md L702 |
| R65 | Coeus | concept identity predicts forge outcome (pooled AUC 0.887); "causal graph" | leave-one-forge-day-out AUC 0.461/0.338: the forge calendar; graph was lasso labelled do-calculus | PS, LP | roles/Coeus/CALIBRATION.md L19-44 |
| R66 | Harmonia C | 57.8% action divergence, +7.8pp over a chance floor | unrepresentative sample (corpus 41.1%); 2p(1-p) is a Jensen ceiling, not a floor | SO, PS | pivot/CORRECTION_2026-08-31_action_divergence_withdrawn.md L18-40, L44-55 |
| R67 | Ergon | "132M rows with ~2 bits of signature" | log2 vocabulary ceiling, not entropy (3.119 bits); estimator correct only when the hypothesis holds; "fourth wrong-population error in a week" | DM, AS, SC | pivot/CORRECTION_corpus_signature_claim_2026-08-22.md L20-60 |
| R68 | Techne | v2 corpus contrast ~18.5% | three meta-relational generators answer a different predicate than the null evaluates (claim-shape category error) | AS, LP | pivot/calibration_v3c_VERDICT_generator_category_error_2026-06-03.md L10-40 |
| R69 | SerendipityFoundry | stackvm QUALIFIED_WITH_LIMITATIONS | self-authored suite 13/13 only; steps/halt saturate 44.3%; R1 references not exchangeable; spec menu a selection channel -> NULL_COMPROMISED | AS, DM, SO | SerendipityFoundry/stackvm_admission/VERDICT_CORRECTION.md L1-60 |
| R70 | Ergon | 7 Avida genomes damaged (two extractors agree) | the underscore is a documented deletion marker; agreement = reproducibility, not correctness | PR, LP | ergon/detector_transfer/08_AVIDA_CORRECTION.md L1-50 |
| R71 | Herakles | the MVG line never measured variant distributions | an unscreened 2008 paper did, exhaustively | SA | herakles/HERAKLES_HISTORICAL_COLLIDER_V0/HC_R01_CORRECTION_2026-09-03.md L14-40 |
| R72 | Harmonia D / Aporia | decidability and novelty anti-correlated by construction (internal derivation) | it is Hintikka's Scandal of Deduction; Boolean Pythagorean Triples counterexample | AS | aporia/docs/FINDING_2026-08-17_decidability_novelty_correction.md L15-40 |
| R73 | Agora / Cartography (April) | "NF backbone real", "Megethos is PC3", "battery works"; F33/F34 kills vs TT-Cross structure | tiers withdrawn: no prereg, no controls, same-model agents reviewing each other; two instruments gave opposite answers | PR, VC | roles/Agora/calibration/LEDGER.md L13-15; cartography/docs/metric_correction_20260413.md L1-25 |
| R74 | Cyclops | HR2_signal - HR2 gap reads selectivity; FIFO is a relevance-blind control | a relevance-blind random merge also shows +.06; FIFO is partly selective where the cue is recent | TB, LP | roles/Cyclops/calibration/LEDGER.md L10, L13 |
| R75 | Aphrodite | E3 verifier; campaign-0 pseudoreplication cheat control; E2 cheat arm | probes drawn from training shapes admit 1.165 false rules; control cannot see the defect on an exact null; exploit barely reachable from theta_0 | AS, VC | roles/Aphrodite/calibration/LEDGER.md L12, L14, L20 |
| R76 | Nyx | c23 negative control would fire; P-a5 cheat control true; ASAL catalogue does not cross | closed via hidden simp builtin; all() over empty generator; 5-seed estimated mean frozen as exact threshold, executed subset 395/1,045 | VC, SC, SO | roles/Nyx/calibration/LEDGER.md L12, L16, L28-29 |
| R77 | Arachne | reach vs degree-spread null measures usefulness; emergence gates | statistic rewards spreading; NMI ~0.46 for ANY refinement; STABLE unreachable (p=1/11 per unit) | DM, VC | roles/Arachne/CALIBRATION.md L10, L17-20 |
| R78 | Atlas | 'repeated weak effects'; policy/1 prioritiser; quiet MICRO window | 14/14 were schema fields; novelty 0.000 for all 46; index 4.9 days behind (coverage read as absence) | LP, DM, SA | roles/Atlas/calibration/LEDGER.md L12, L18, L20 |
| R79 | Rhadamanthus | two adversarial passes: census unreachable from code | both read the daemon's log text: one false premise twice | PR | roles/Rhadamanthus/calibration/LEDGER.md L16-18 |
| R80 | base role (Techne, Vivarium, Herakles) | SCS OPTIMAL; fix closed; SHA quoted | 188%-wrong answer (status anti-correlated with accuracy); consumer build 4 h older than fix; SHA not yet an ancestor | LP, SC | roles/base-role/RESPONSIBILITIES.md L30-48 |

Counts (computed by script from the "shapes" column of the 80 rows above;
the classification itself is mine, INFERRED; "seats" = distinct values of
the engine/seat column; "engines" = how many of the ten engines NPE, BEE,
AGE, CWE, WTP, PTE, ARC, Ares, Crius, SFE carry the shape):

    shape  rows  seats  engines  which engines
    LP      21    15      7      NPE BEE CWE PTE ARC Ares Crius
    VC      21    13      7      NPE BEE AGE CWE WTP PTE Ares
    PR      12     9      6      NPE BEE CWE WTP Ares SFE
    TB      10     8      6      AGE CWE WTP PTE Ares Crius
    AS      12    10      4      CWE WTP PTE Ares
    DM      12    11      4      NPE WTP PTE Crius
    SC       9     7      4      NPE AGE CWE WTP
    HG       6     4      4      NPE BEE AGE ARC
    LM       4     4      4      NPE BEE ARC Crius
    SO       6     6      3      BEE WTP Ares
    WR       4     3      3      NPE AGE PTE
    PS       4     4      2      CWE ARC   (+ BEE G1 pooled 7.2%, not a table row)
    SA       3     3      1      SFE

LP and LM together (the "wrong referent" family) cover 22 distinct rows
and 7 engines (LM adds no engine beyond LP).

-----------------------------------------------------------------------

## 2. Taxonomy -- shapes that recur across two or more engines

Ordered by breadth across the ten world/instrument engines, then seats.

### 2.1 VC -- vacuous control / outcome forced by construction
Engines: NPE (R05), BEE (R12, R13), AGE (R17, R18), CWE (R22), WTP (R31,
R34, R36), PTE (R38-R40, R43), Ares (R51, R54); seats: Apollo, Hephaestus,
Nyx, Aphrodite, Arachne, Agora.
Signature: an arm that cannot differ from its partner (identical to the last
decimal: R05, R12), an ablation whose window/scope cannot contain the cause
(R38-R40), an "intervention" the law alone decides (R18), a check that is an
identity (R17: exact 1.0000 over hundreds of samples).
General lesson: every control must be SHOWN to fire on a planted effect
of the size claimed, at the operating point, before its silence is read.
"Identical arms are a defect signature, not a null" (roles/Nestor/FINDINGS.md
L422-425). Nestor's lesson 1 (L402-404), Aether's "ask whether the law alone
forces the outcome" (roles/Aether/calibration/LEDGER.md L146-150) and base
rule 3 (roles/base-role/RESPONSIBILITIES.md L88-90) are three independent
statements of it.

### 2.2 LP / LM -- label (or location) mistaken for property (or material)
Engines: NPE (R04, R06, R08), BEE (R12, R14, R15), CWE (R22), PTE (R40), ARC
(R46, R47), Ares (R51), Crius (R55, R58); seats: Hephaestus, Coeus, Techne,
Cyclops, Atlas, Harmonia D, Ergon, base-role examples.
Physics-of-intelligence form: WHO ran it, WHERE it sits and WHAT it is made
of are different referents (B6: archaeon/causal_lens/V02_REGRESSION_REPORT.md
L93-110). Every engine's native "parent", "lineage", "own code", "material",
"fidelity" and "birth" is a false friend somewhere (FALSE_FRIENDS.md FF-1 to
FF-34). A certificate (P-11, the H3 id-tracker, `self_copy`) is itself a label.
General lesson: name the referent (executor / location / material /
counterfactual author) in the endpoint's definition, and never let a field
name carry it.

### 2.3 AS -- the author smuggles the answer
Engines: CWE (R21), WTP (R30, R32, R37), PTE (R42), Ares (R53); seats: Apollo
E9 (R61), Techne (R68), SerendipityFoundry stackvm (R69), Harmonia D /
Aporia (R72), Aphrodite (R75), Ergon (R67). Pending: WTP-LM01 (ANOMALIES.md
2026-09-26T01:29Z) and NPE C-CORE "theory-aware by date"
(roles/Nestor/FINDINGS.md L376-379).
Sub-forms: (a) the generator's class IS the found law (WTP completion, CWE
economics); (b) the expected mechanism is written into the pass rule (PTE
CAUSAL_SUPPORT, R42); (c) probes drawn from the construction's own
distribution (Apollo E9, Aphrodite E3); (d) internal derivation of a known
result (R72, Ares R53); (e) a self-authored adversary (R69).
General lesson: a substrate-independent claim needs a world, probe or
adversary the claimant did not author, and a "known-physics" null tuned at
least as hard as the specimen (WTP N6).

### 2.4 PR -- pseudo-replication
Engines: NPE (R02, R03), BEE (R12), CWE (R26, R27), WTP (R33), Ares (R48,
R50), SFE (R60); seats: Ergon Avida (R70), Agora (R73), Rhadamanthus (R79),
Metis (greedy-LoRA agreeing channels, roles/Metis/calibration/CALIBRATION.md
L142-153, P-5 -- a seat's reading of greedy-LoRA, INFERRED as a reversal).
General lesson: in evolving or deterministic systems the unit of replication
is not the run -- it is the independent lineage, founder, seed, attack
configuration or evidence source. Hash states/genomes/configs across runs
and report n_eff beside n.

### 2.5 TB -- trivial or tuned baseline never run
Engines: AGE (R19), CWE (R23, R25), WTP (R31, R32), PTE (R41), Ares (R52),
Crius (R57); seats: Apollo (dead-world MAP-Elites, R61), Cyclops (R74),
Coeus ("random noise reorders 99.7%", roles/Coeus/CALIBRATION.md L29-34).
General lesson: before any flag, score the dumbest sufficient explanation on
the claim's own scale: constant, running mean, copy-last, reflex on every
lagged channel, random walker, and the best tuned same-class estimator.

### 2.6 DM -- degenerate metric
Engines: NPE (R09), WTP (R29, R30), PTE (R44), Crius (R56); seats: Apollo,
Nous, Harmonia D, Ergon, stackvm, Arachne, Atlas; plus the lens's B7 (accuracy
vectors saturate at ceiling, FALSE_FRIENDS.md L54) and BEE P5 at 0.999 both
arms (notes/C_engines.md L438-439).
General lesson: check variance, denominator and ceiling of a metric on dead,
constant and saturated inputs before believing it.

### 2.7 SC -- stale or wrong comparator
Engines: NPE (R03, R07), AGE (R16, R19), CWE (R28), WTP (R35); seats: Ergon
(wrong population x4, R67), Nyx, base role (Vivarium stale build), Apollo
(CAL-02/03 formula fossil and stale clone, roles/Apollo/CALIBRATION.md
L14-15).
General lesson: every operand carries its tick, config hash and population;
a comparison is legal only if they match (or the mismatch is the variable).

### 2.8 HG -- host credited for its guest
Engines: NPE (R01, R06), BEE (R10), AGE (R20), ARC (R45, R46).
This is the most physics-laden shape: in four independently written worlds
the WORLD (splice operator, migration, perturbation, takeover host) did the
work that was credited to an organism. Its mirror is real and interesting:
host-mediated reproduction (26/63 inert hosts gave births, all by foreign
execution; ENGINE_LENS_CARDS.md L245-247; NPE AN3, BEE CAPTURE,
PORTABILITY01_REPORT.md L119-124, L153).
General lesson: attribute every copy to executor, material and host
separately; credit the world's own operators (mutation, splice, migration,
perturbation, write-back erosion) with their measured share.

### 2.9 SO -- selection on the outcome
Engines: BEE (R11), WTP (R32), Ares (R49); seats: Harmonia C, stackvm, Nyx.
General lesson: estimate unconditional rates from the whole family including
losers; never select the reported champion on the set it is reported
against (roles/Ares/calibration/LEDGER.md L20).

### 2.10 WR -- window misses the readout
Engines: NPE (R01 fidelity after _mutate; R05 intervention not handed to the
task), AGE (R16 prev cadence), PTE (R38).
General lesson: in a synchronous tick-ordered world the causal event, the
measurement and the intervention live in specific phases of the tick; the
assay must be swept over phase, not assumed.

### 2.11 PS -- pooled statistics hide per-group failure
Engines: CWE (R24), ARC (R45); seats: Coeus (R65), Harmonia C (R66); BEE
G1's 7.2% pooled over topologies including the P1 channel
(GROUNDING_REPORT.md L45-49) is a further instance.
General lesson: leave-one-family / one-time-slice / one-block-out as a gate,
not a robustness footnote.

### 2.12 SA -- silence or absence read as a null (single engine: SFE; many seats)
Recorded mostly as operations (Nous 162-day silent death, Atlas index lag,
Metis/Coeus truncated greps). The research-relevant instance is SFE's
"ledger silent precisely when the engine broke" (R59) and NPE's 400-event
lineage tail that omits migrations (roles/Nestor/FINDINGS.md L84-93).

-----------------------------------------------------------------------

## 3. Research threads implied by the failure record

### T01 Who did the work? A substrate-independent attribution of copying
QUESTION: Is there one definition of executor / material / host / author
that gives the same verdict across NPE, BEE, ARC and PTE, and where must it
be ILL_POSED?
WHY IT MATTERS: every replication headline in the program died on this
(R01, R10, R14, R45, R46). "Self-replication" is not measurable until it is.
WHAT IS KNOWN: B6 three referents (V02_REGRESSION_REPORT.md L93-110);
counterfactual (P-11 C4) and in-situ authorship disagree in both directions on
12/34 NPE births (FALSE_FRIENDS.md L44, FF-29); symmetric crossover makes
continuity ill-posed (B1, V02 L87); lens portable to 3 engines
(PORTABILITY01_REPORT.md L150-161).
WHAT IS UNKNOWN: which referent predicts downstream accumulation (fertile,
competent descendants); whether the 12/34 split is noise or two real kinds.
CHEAPEST DISCRIMINATOR: on already-preserved NPE c9x runaway runs, compute
material share (z8taint) and P-11 status per birth; test which one predicts
X-STALL sterility (roles/Nestor/FINDINGS.md L310-313).
LENSES: ARC causal lens v0.3, NPE P-11, BEE traced replay.
RELATED: T02, T12, section 5 E1/E2.

### T02 What quantity certifies heredity, as opposed to identity or lineage?
QUESTION: Id-continuity, slot lineage (anc), certified causal chains and
material share disagree; which one is the carrier of accumulation?
WHY IT MATTERS: R06, R08, R09 -- three certificates each measured something
else (identity, slot descent, luck of an unbroken chain).
WHAT IS KNOWN: runaway populations are 13-25% founder material yet anc ~1.0
(FINDINGS.md L362-366); only OP_SELF and LDIR are conserved as material
(C-CORE, L370-375); break rate p caps chain depth at ~1/p (L383-388).
WHAT IS UNKNOWN: whether "conserved functional core + turnover elsewhere" is
the general form of heredity in these substrates (C-CORE is theory-aware and
single-cell).
CHEAPEST DISCRIMINATOR: C-CORE's per-position conservation profile on a
second specimen cell and on BEE seeded replicators.
LENSES: NPE z8taint, ARC taint VM, BEE traced replay.
RELATED: T01, T18.

### T03 When does the world generator decide the result?
QUESTION: How much of a "law" or "winning substrate" is the match between
the author's world class and the learner's inductive bias?
WHY IT MATTERS: R21, R32, R68, and the pending LM01 anomaly: "the WINNING
ARM is largely set by the GENERATOR" (ANOMALIES.md 2026-09-26T01:29Z).
WHAT IS KNOWN: law A = 97.5% hand economics (REVIEW_PACKET_CWE L122); WTP
admission selects exactly the worlds where completion works
(ENSORAIN_WTP03_REPORT.md L143-147); Techne's signal lived entirely in three
meta-relational generators (calibration_v3c L10-40).
WHAT IS UNKNOWN: any result on a world authored by someone else except C3's
untested hash-committed law on Nestor's D (notes/C_engines.md L596-597).
CHEAPEST DISCRIMINATOR: run one frozen claim (CWE law A, or an LM01 arm
ranking) on a foreign-authored world family; score agreement vs the
author-family result.
LENSES: CWE sealed holdout broker; WTP N6; Nestor holdout D.
RELATED: T16, T17, section 5 E3/E4.

### T04 Content vs timing: can the substrate carry structured information?
QUESTION: Does anything propagate a structured pattern, or only arrival
timing / who-fired?
WHY IT MATTERS: the only propagation seen in AGE is 92% who-fired/energy, 8%
content (notes/C_engines.md L527-535); PTE sums arrivals so source identity
is lost (ENGINE_LENS_CARDS.md L200-204); PTE C1's M3 "self-modifying"
mechanism may be timing-locked transport (ANOMALIES.md 2026-09-25T23:45Z).
WHAT IS KNOWN: PTE C1b carrier = transport arriving on the readout tick
(ENGINE_LENS_CARDS.md L213-215).
WHAT IS UNKNOWN: any engine in which a content-bearing, addressable message
has been demonstrated.
CHEAPEST DISCRIMINATOR: timing-preserving content-shuffled surrogate (keep
arrival times, permute payloads) on AGE twins and PTE relay champions; a
content channel must lose accuracy, a timing channel must not.
LENSES: AGE twin/light-cone assay; PTE per-carrier resets.
RELATED: T05, POI MAP P2/P6 (roles/Odysseus/frontier/poi/MAP.md L37-60).

### T05 Phase of measurement in tick-ordered worlds
QUESTION: Where in the tick (deliver -> sense -> run -> emit -> trace, or
mutate -> measure) is each causal quantity observable?
WHY IT MATTERS: R01, R05, R16, R38 -- four engines measured at the wrong
phase or cadence.
WHAT IS KNOWN: PTE tick order (ANOMALIES.md 2026-09-25T23:45Z D-A); NPE
lesson 7 (FINDINGS.md L417-418).
WHAT IS UNKNOWN: whether other frozen verdicts depend on phase (PTE rechecked
12 D-wave cells, C1_ERRATA.md L13-14; BEE, AGE not audited for phase).
CHEAPEST DISCRIMINATOR: a phase-sweep harness: repeat each ablation with the
window shifted by -1, 0, +1 tick and require the verdict to be stable or
explained.
LENSES: any deterministic replay (BEE 606/606, AGE CPU oracle, PTE oracle).
RELATED: T13, instrument I2.

### T06 Search strength vs substrate capacity
QUESTION: When nothing is found, did the substrate forbid it or did the
search fail to reach it?
WHY IT MATTERS: Crius "0/36 by search" (notes/C_engines.md L840-848), PTE
"cannot separate GP search strength from substrate capacity"
(ENGINE_LENS_CARDS.md L203-204), Ares "one search regime" (C_engines L807-810),
base rule "failure of one configuration is not falsification"
(RESPONSIBILITIES.md L70-73).
WHAT IS KNOWN: priors on search power were wrong in both directions (Crius
random walkers solved chains, roles/Crius/calibration/LEDGER.md L14-15;
Ares counts too pessimistic, roles/Ares/calibration/LEDGER.md L17).
WHAT IS UNKNOWN: a reachability curve (recovery vs edit distance from a
planted solution) for any engine.
CHEAPEST DISCRIMINATOR: plant a known working program, perturb by k edits,
measure recovery rate vs k per search method.
LENSES: Crius typed transplants, Ares transplant, NPE implant arms.
RELATED: T07, section 5 E6.

### T07 Basin width as the physics of which mechanism wins
QUESTION: Is "what evolution prefers" the measure of the viable parameter
region of each carrier rather than its peak value?
WHY IT MATTERS: Ares recurrence wins by basin (14/23 viable vs keep 3/25)
(roles/Ares/calibration/LEDGER.md L22); BEE origins need one decisive byte
(GROUNDING_REPORT.md L62-68); NPE discovery barrier is encoding length
(FINDINGS.md L241-250). If so, results are about parameterisation, which
the author chose (AS).
WHAT IS KNOWN: reachability is necessary, not sufficient (Ares L22).
WHAT IS UNKNOWN: whether reparameterising a carrier to widen its basin flips
the preference (Ares basin explanation is POST-HOC, C_engines L816-817).
CHEAPEST DISCRIMINATOR: Ares cycle with keep reparameterised to a wide basin;
predict the flip in advance.
LENSES: Ares forbid-arms; NPE X-DENSE-OPS encodings.
RELATED: T03, T06.

### T08 The dumbest sufficient explanation ladder
QUESTION: For each headline, what is the minimal mechanism class that
reproduces it (constant, running mean, copy-last, reflex, random walker,
tuned known-class estimator)?
WHY IT MATTERS: TB rows in six engines (s2.5).
WHAT IS KNOWN: one-float running mean passed the entire WTP-02 chain (R31);
tuned N6 beat all WTP-03 specimens (R32); a constant scored 10/12 on CWE G6 (R23).
WHAT IS UNKNOWN: whether any standing positive (PTE relay, NPE C-ATOMIC,
Crius reuse) survives the full ladder.
CHEAPEST DISCRIMINATOR: run the ladder on stored rows of the three standing
positives; it needs no new world runs for the constant/mean/copy-last rungs.
LENSES: WTP null ladder N0-N6; CWE baselines at PREREG time (Cosmos LEDGER L14).
RELATED: instrument I1.

### T09 Rarity at origination vs rarity at establishment
QUESTION: Are rare phenomena rare because they rarely arise, or because
they rarely establish?
WHY IT MATTERS: WTP "the rarity is at admission, not in the collider"
(ENSORAIN_WTP03_REPORT.md L81); BEE unselected origins mostly die (R11);
NPE founders are independent lottery tickets decided in ~12 epochs
(FINDINGS.md L302-309); ENVGATE R0 ~ 60 x k/256 (ENVGATE01_REVIEW L31).
WHAT IS KNOWN: branching-process readings fit NPE and ARC.
WHAT IS UNKNOWN: a shared estimator of unconditional origination rate
across engines.
CHEAPEST DISCRIMINATOR: fit s(k)=1-(1-p)^k founder-dose curves (Nestor's
X-DOSE-CURVE form) in BEE and ARC from existing rows.
LENSES: NPE, BEE, ARC ENVGATE.
RELATED: T14.

### T10 The unit of replication in evolving systems
QUESTION: What is n when seeds reproduce lineages byte for byte, attacks are
deterministic, and admitted worlds share founders?
WHY IT MATTERS: PR in six engines (s2.4).
WHAT IS KNOWN: "10 seeds" = 7 (R48); n_eff 13 of 181 (R33); events vs lineages
911/1,031 depth 1 (R02).
WHAT IS UNKNOWN: n_eff for BEE's 63,247-run corpus and CWE sealed families.
CHEAPEST DISCRIMINATOR: hash every initial state / genome / attack config in
existing manifests and count distinct.
LENSES: SFE FAMILY_EXTENT_DIVERGENCE (notes/C_engines.md L253-255).
RELATED: I5.

### T11 Observables at the ceiling
QUESTION: What remains informative when performance saturates?
WHY IT MATTERS: accuracy vectors collapse distinct perfect champions (B7,
FALSE_FRIENDS.md L54); BEE P5 0.999 both arms (C_engines L438-439); stackvm
steps/halt saturate 44.3% (VERDICT_CORRECTION.md L37-41); PTE HOLD latches 1.00.
WHAT IS KNOWN: saturation makes tests level-correct but powerless (stackvm).
WHAT IS UNKNOWN: a harder-probe tier per engine.
CHEAPEST DISCRIMINATOR: add a probe tier with known lower ceiling; check that
tied champions separate.
LENSES: PTE probe sets; ARC ARCH criteria.
RELATED: T08.

### T12 Host-mediated computation as a general route
QUESTION: Is "a host executes inert material" a common physics of early
reproduction across substrates?
WHY IT MATTERS: HG's mirror image appears in three independently written
engines (ARC 26/63 inert hosts; NPE AN3; BEE CAPTURE 1.27M)
(PORTABILITY01_REPORT.md L119-124, L153, L174).
WHAT IS KNOWN: host execution amplifies residents, does not originate
(notes/C_engines.md L749-750).
WHAT IS UNKNOWN: whether it ever yields heritable novelty.
CHEAPEST DISCRIMINATOR: the cross-engine prereg the lens proposes
(archaeon/causal_lens/HOST_CONDITIONED_ASSAY_READINESS.md; PORTABILITY01 L174).
LENSES: ARC, NPE, BEE.
RELATED: T01.

### T13 What fraction of each engine is observable at all?
QUESTION: For each recorder, what is recall of planted events?
WHY IT MATTERS: SFE silent when broken (R59); BEE abstains on ~1/3 births
(ENGINE_LENS_CARDS.md L234-236); NPE 400-event tail (FINDINGS.md L84-94); AN1
NOT_IDENTIFIABLE because code material is not persisted (V02_REGRESSION_REPORT.md s6, AN1 row).
WHAT IS KNOWN: NOT_IDENTIFIABLE is representable (PORTABILITY01 L152).
WHAT IS UNKNOWN: recall numbers.
CHEAPEST DISCRIMINATOR: inject N known births/migrations into a replayed run
and count what the record shows.
LENSES: replay harnesses.
RELATED: T05.

### T14 Base rates under open-ended search
QUESTION: How do we estimate the rate of a rare phenomenon when every stage
(trigger, admission, champion selection) conditions on it?
WHY IT MATTERS: SO rows R11, R32, R49, R66, R69.
WHAT IS KNOWN: SFE made best-of-N visible (notes/C_engines.md L252-255) but no
post-SFE engine except CWE/BEE keeps loser families (C_engines L870-874).
CHEAPEST DISCRIMINATOR: re-derive WTP-03 and BEE G2 rates with all losers
from preserved manifests.
LENSES: SFE-style loser-keeping families.
RELATED: T09, I6.

### T15 Pooled cross-substrate laws vs per-family laws
QUESTION: Are cross-substrate regularities real or averages over families
that individually violate them?
WHY IT MATTERS: CWE location gate killed 3 pooled-pass laws (R24); Coeus
calendar (R65); Jensen heterogeneity (R66).
CHEAPEST DISCRIMINATOR: apply the CWE per-family location gate to PTE
routed-relay (topology-tied, 8/352) and BEE WELL_MIXED survival.
LENSES: CWE location gate.
RELATED: T03.

### T16 A rediscovery detector
QUESTION: Can we measure how far a found mechanism is from the author's
design intent and from the literature?
WHY IT MATTERS: R21, R32, R53, R72; C-CORE "exactly what purifying selection
predicts" (FINDINGS.md L376-378).
CHEAPEST DISCRIMINATOR: a pre-registered "known-physics list" per campaign
(WTP did this: ENSORAIN_WTP03_REPORT.md L70) plus a tuned known-class null;
score how many flags are on the list.
RELATED: T03, T08.

### T17 Selectivity vs inductive-bias match (LM01)
QUESTION: Does relevance-selective contraction help, or does a bias that
matches the world's structure help?
WHY IT MATTERS: the SI program's first live test (PREREG_WTP_LM01.md) uses
author-written latent generators (L31-40) and a SELECTIVE arm built from
matching online substrates (L59-60).
WHAT IS KNOWN: winning arm set by generator in dev; competence rises with
exact records kept -- a frontier over retained records (ANOMALIES.md
2026-09-26T01:29Z, 02:49Z).
CHEAPEST DISCRIMINATOR: one mismatch world family (structure outside the
selective arm's class) added before launch.
RELATED: T03, section 5 E3.

### T18 The probe and the world's operators as physics
QUESTION: How much of observed change is supplied by the experimenter's
operators (perturbation, splice, write-back, migration)?
WHY IT MATTERS: AGE perturbation 42%/95% (R20); NPE write-back erosion ~5%/byte/
epoch, ~25x nominal mutation (FINDINGS.md L314-319); splice made 88% of
"replicators" and also prevents runaway (L284-288).
CHEAPEST DISCRIMINATOR: per engine, a table of operator-supplied change share
measured with that operator off.
RELATED: T02, HG.

-----------------------------------------------------------------------

## 4. Candidate cross-engine controls (instruments) and what they would
## have caught

I1 DUMB-BASELINE PREFLIGHT. Score constant, running mean, copy-last, reflex
   on every lagged channel, random walker/random sampler, and a tuned
   same-class estimator on the claim's own scale, at PREREG time.
   Would have caught: R19 (partly), R23, R25, R31, R32, R41, R52, R57, R61
   (dead-world MAP-Elites), R74, Coeus random reorder. ~11 rows, 6 engines.

I2 CONTROL-FIRES HARNESS (vacuity + arm fingerprint). For every control,
   ablation, gate and transfer: (a) inject a planted effect of the claimed
   size and require the control to detect it; (b) assert every arm/level
   pair differs in at least one input the mechanism reads; (c) flag any
   exact identity (ratio 1.0000, byte-identical arms).
   Would have caught: R05, R12, R13, R17, R18, R22, R31, R34, R36, R38, R39,
   R40, R43, R51, R54, R61 (CAL-04), R62 (bool coercion), R75, R76, R77.
   ~20 rows, 7 engines. Precedent: Nestor's injected-defect tests
   (FINDINGS.md L402-404), Ananke's no-op guard (LEDGER L17).

I3 MANDATORY CAUSAL-LENS ATTRIBUTION for any replication / lineage /
   heredity claim (executor, material, host, counterfactual author as
   separate columns). Already portable (PORTABILITY01_REPORT.md L150-161).
   Would have caught: R01, R06, R08, R10, R14, R15, R45, R46. 8 rows, 4
   engines. Has already caught R14/R15 retroactively.

I4 OPERAND CURRENCY STAMP. Every reference/baseline operand carries tick,
   config hash, code SHA and population id; comparisons assert equality.
   Would have caught: R03, R07 (partly), R16, R28, R35, R55, R66 (sample
   population), R67 (wrong population), R80 (stale build). ~9 rows.

I5 n_eff AUDITOR. Hash initial states, genomes, attack configs and evidence
   sources across a campaign; report n_eff beside n; events vs lineages.
   Would have caught: R02, R12, R26, R27, R33, R48, R60 (partly), R70, R79.
   ~9 rows, 6 engines.

I6 LOSER-KEEPING SELECTION LEDGER (SFE FAMILY_EXTENT generalised).
   Would have caught: R11, R32 (admission), R49, R66, R69. 5 rows.

I7 LEAVE-ONE-GROUP-OUT GATE (CWE location gate generalised to family, block,
   day). Would have caught: R24 (it did), R45, R65, R66, BEE G1 pooled 7.2%.

I8 FOREIGN-AUTHOR HOLDOUT (CWE -> Nestor D generalised). Addresses R21, R32,
   R61 (E9), R68, R69, R75; does not detect them automatically.

I9 PHASE-SWEEP of ablation windows (T05). Would have caught R38 and R01's
   measure-after-mutate; R16 (cadence). 3 rows, 3 engines.

-----------------------------------------------------------------------

## 5. Claims still standing that look exposed to a known shape (unchecked)

E1 BEE: spontaneous own-code self-replication CONFIRMED_CAUSAL (1-5% of
   fresh runs) AND the running multi-day campaign's primary endpoint.
   Shape: LM + LP. The SR test is `material == "writer" ... and own_code >=
   0.9 * len(own)` with `own_code = sum(1 for pc in own if pc < L)`
   (prometheus/z80atlas/world.py L586-587 at the campaign pin a3086cece;
   same on main; adjudication.py L64, L72). `material` is the resemblance
   heuristic (FF-4) and pc < L is code LOCATION (FF-30, B6), both recorded
   as false friends; B6 says the criterion "cannot see self-replication run
   from self-copied code" and the frozen output is kept
   (V02_REGRESSION_REPORT.md L105-108). `sr_depth` derives from it
   (world.py L543), and the multi-day endpoint "competent self-replicator"
   reads `sr_depth > 0` (multiday_campaign.py L127-128 @ a3086cece;
   MULTIDAY_PREREG.md s7 @ 12ce26e23). 4,160 runs launched 2026-09-26.
   Direction: unknown in sign -- location undercounts own-material SR run
   from the window; resemblance can credit the wrong party (847k births).
   Check: rerun the lens v0.3 material classifier on the 160 G1 origins and
   on a sample of multi-day checkpoints before the analysis is unblinded.

E2 NPE: the c9x confirmed chain (C-RUNAWAY, C-CRITICAL-MASS, C-ATOMIC C1,
   C-SWAP-ACQUIRE) uses P-11 causal-copy depth as endpoint.
   Shape: LP (certificate as property) + HG. P-11's counterfactual authorship
   and in-situ provenance disagree in BOTH directions on 12/34 pair births
   (FALSE_FRIENDS.md L44, FF-29); the lens audited only C9 H2 reservoir arms
   (36 runs, PORTABILITY01_REPORT.md L14), not the c9x chain; X-CONTENT
   already showed lineage descent != content (FINDINGS.md L362-366) and
   X-CERT-BREAK showed depth is capped by certification breaks (L383-388).
   Check: run the lens on c_atomic_confirm / c_runaway_confirm rows; report
   the confirmed contrasts on a material-share endpoint beside P-11.

E3 WTP-LM01 (frozen at 768ea8ce9, awaiting LAUNCH; notes/C_engines.md
   L620-623). Shape: AS (bias-structure match) + SO. All worlds are the
   author's latent generators (lowrank, cp, tt, pairwise, spectral, sum;
   PREREG_WTP_LM01.md L31-40); the SELECTIVE arm is WTP online substrates of
   those classes (L59-60); dev showed the winner is set by the generator
   (ANOMALIES.md 2026-09-26T01:29Z). GENERATOR_DEPENDENT is a declared
   verdict (L42, L143) but no foreign-authored or mismatch-class family
   exists; WTP-03 already showed its generators admit only
   completion-friendly worlds (ENSORAIN_WTP03_REPORT.md L143-147).
   Check: pre-launch, add one mismatch family or pre-declare that a
   SELECTIVE win reads as "bias matches generator", not as selectivity.

E4 CWE: C0b law A transfer to sealed D/E/F. Shape: AS. The sealed worlds have
   the same author (REVIEW_PACKET_CWE L168); Nestor's foreign D was sealed
   for C3's law, which is "UNTESTED on Nestor's D" (notes/C_engines.md
   L596-597). Acknowledged by the seat, not yet checked.

E5 Crius C2 "ACCESSIBILITY FRONTIER MAPPED": reuse pays but 0/36 runs reached
   it by search (notes/C_engines.md L840-848). Shape: failure of one
   configuration read as a property of the substrate (RESPONSIBILITIES.md
   L70-73) + TB history (Crius's own budget priors were wrong vs RANDOM,
   roles/Crius/calibration/LEDGER.md L14-15). Check: planted-solution
   k-edit reachability curve (T06).

E6 PTE C1 routed relay COMM_DEPENDENT/REPRODUCED at 0.875-0.893 up to N=2304
   (ENGINE_LENS_CARDS.md L211-213). Shapes: SO/PS (8/352 cells, topology-tied)
   and DM-at-ceiling for any architecture claim (B7). The D-A window defect
   was rechecked for RELAY (corrected 0.50 in 4/4; C1_ERRATA.md L13-14), so
   WR is cleared; the per-family location gate (T15) has not been applied.
   INFERRED exposure.

E7 Ares cycle 2 "recurrence wins by basin width": POST-HOC, hand-wired
   (notes/C_engines.md L816-817). Shape: AS via parameterisation (T07).

E8 AGE PHYSICS_DESIGN_02 "only rcv propagates, weakly, by timing": the
   decisive partial-ring arm is post hoc (PHYSICS_DESIGN_02 L282-288) and
   single-bit perturbations are dominated by the arg1 mod 5 addressing
   artefact (notes/C_engines.md L512-514). Shape: HG (probe channel).
   INFERRED exposure; the seat already separated full-ring as VC.

-----------------------------------------------------------------------

## 6. Gaps in this pass

- Review packets were sampled, not read in full (about 150 files under
  pivot/, SerendipityFoundry/, ergon/, agent_d*_blind/, evidence_wiki/,
  techne/loop/). Early-era (April-August) reversals are under-represented;
  pivot/sprint1/* and pivot/erebos_* reviews are unread.
- Counts in s1 are my classification; a second classifier would likely
  merge LP/LM and split VC into "cannot fire" vs "forced outcome".
- The evidence wiki (Mnemosyne) was not queried.
