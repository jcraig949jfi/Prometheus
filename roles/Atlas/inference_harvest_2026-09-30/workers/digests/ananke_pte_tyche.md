# Atlas inference harvest -- digest: GROUP ananke_pte_tyche

Reader: fresh-context, read-only. Repo F:/Prometheus-worktrees/atlas-base-role (origin/main ~2026-09-30 22:00Z).
Layer tags: RAN / OBSERVED / CONCLUDED / ATLAS_DERIVED. Short sha after a path = `git log -1 --format=%h -- <path>`.
Abbrev: RA = roles/Ananke, RR = roles/Ananke/research, W-x = RR/workers/W-x/REPORT.md, RT = roles/Tyche, TY = tyche/.

## 0 Coverage

READ (main): RA/{STATUS.md a90dede19, RESUME.md, TODO.md, WORK_STATE.json 4a97f97fa, calibration/LEDGER.md c34cbb463};
RA/pte/{REVIEW_PACKET_PTE_C1.txt, C1_REPORT.md (both e35fb9704), C1_ERRATA.md cc98596dd, c1_a0/A0_FINDINGS.md c2f81c273,
c1b/REVIEW_PACKET_PTE_C1b.txt cc98596dd, c1b/CORRECTIONS_2026-09-27.md c34cbb463}; RR/SYNTHESIS_2026-09-27 (c34cbb463),
_ARC2 (a4d054ea0), _ARC3 (93e2e544b), _2026-09-29 (cf94415d9); CROSS_ENGINE_THREADS (46dc8f25a); CROSS_THREAD_COMPRESSION
(d8ef2dc5b); CORRECTIONS_2026-09-29_SWAP_AUDIT (017259a48); PTE_ENGINE_CARD (46dc8f25a, first 60 lines); THREADS.md;
worker REPORTs W-A..W-Z (W-G,H,I,J,K,L,M,N,O,P,Q,U,V,W,X,Y,Z read in substance; W-A,B,C,D,E,F,R,S,T heads + key lines);
W-C/X4_RESULT.md a4d054ea0; designed_echoes/RESULT.md head; prompts/2026-09-30_inference_harvest (4a97f97fa).
RT/{STATUS, TODO, WAKE, WORK_STATE 4dbbc07d0, RESPONSIBILITIES, BACKLOG_H0H5, calibration/LEDGER 4dbbc07d0, journal/2026-09-29,
2026-09-30 (4dbbc07d0), REVIEW_PACKET_v0 (bdeba9865), _v1 (6a28fc49e), design/V2_PRESSURE_MAP_DESIGN (ad5e912e6, first 80 lines),
prompts charter (01c53f64e), v1 directive (b18c2e189), v2 directive (1f4153975)}; TY/{README, residuals/README (8cb8d804a),
residuals/catalogue.py (3c7b9783e), residuals/v0_1/{SUMMARY, CLUSTERS (8cb8d804a), CATALOGUE rows for Ananke/Tyche},
runs/v2_blockR/REPORT_BLOCK_R.md + PHASE_DIAGRAM.json head (4dbbc07d0), runs/v0_2026-09-30/REPORT.md OPEN ANOMALIES}.
Comms: grepped comms_since_0925.txt for Ananke|Tyche|residual; read bodies of #870, #1032, #1039, #1047, #1061, #1121, #1124,
#1133 (+ headers of all Ananke lease msgs #753-#787 and SI01 thread #605-#733).

BRANCHES: origin/ananke/base-role-adopt-2026-09-24 @ab2fc8a4b and origin/tyche/base-role-adopt-2026-09-29 @40f45980e have
ZERO commits not on origin/main (`git log origin/main..<branch>` empty). No BRANCH-only material in this group.
Tyche WORK_STATE names branch tyche/dark-ecology-v0-2026-09-30; it is not on the remote, but its commits (through 4dbbc07d0) are on main.

NOT READ / NOT FOUND: prometheus/ananke/ and tyche/*.py code (except catalogue.py); PRIOR_ART_temporal_distributed_computation.md
(71 KB); BACKLOG_V2 / MACHINE_WORK / BACKLOG_TEMPORAL_DISTRIBUTED in full; raw rows (cells.jsonl.gz, EVALS, GENEALOGY);
Tyche PREREG v0/v1/v2 texts (H/RH definitions taken from reports); W-J NOTES, W-C NOTES in full; journal 2026-09-24 of Ananke;
SI01 steward directive text. The inference-harvest DELIVERABLES (PTE_CAUSAL_AUDIT_2026-09-30.md, T_SWAP_REL4_INTERPRETATION_TREE.md,
PTE_INSTRUMENT_GAPS_AND_UPGRADES.md, INFERENCE_HARVEST_HANDOFF.md, expected under RR/harvest/) DO NOT EXIST on main or either
branch at snapshot time: WORK_STATE 21:57:31Z says "directive recorded; launching independent attacks". Tyche posted only one comms
message since 09-25 (#1047); no reply to Theseus #1124 or Aporia #1144 found.

## 1 Experiment ledger (most recent first)

| id / date | question | substrate | ruler | controls | n | OBSERVED | CONCLUDED (seat) | status | pointer |
|---|---|---|---|---|---|---|---|---|---|
| Tyche v2 Block R, 09-30 | latent option value under unannounced law switch (gen 20 of 50) | tyche v2 lens chemistry, regime worlds R1-R4 | OV clock = gens to 50% oracle deficit; stored optionality = frac of living lenses functionally carrying an L2 precursor | STRICT/LEX/RES x solo/related/broad x 2 seeds | 36 runs, 72 cells | 2/72 cells adapted (RES related s2 R1 +0.496; STRICT R3 +0.337); stored-any LEX .115 > RES .075 > STRICT .055; stored-ALL precursors <=0.0006 mean, max .007 | "Unannounced regime change to a zero-marginal law is a hard wall ... latent option value near zero for all"; RH1-RH4 FALSE, RH5 held | inconclusive (OV clock gap) | TY/runs/v2_blockR/REPORT_BLOCK_R.md 4dbbc07d0 |
| Tyche v1, 09-30 | can a sense assemble from individually useless precursors (gate 6)? | Z worlds: xor/parity of delays, each precursor zero-marginal | capability deficit D = acc(ecology+oracle)-acc(ecology); replicated test >= 0.10 | arms V0/DE/DENR at equal 6000 eval units; TSD twins; PRF | 6 runs, 2 seeds | Z cells solved V0 3, DENR 2, DE 1 of 10; Z3 parity-3 and Z5 unreached by all; one both-useless fused sensor +0.075 (z 5.6), fresh seeds +0.101/+0.109 | "GATE 6 = FAIL ... counterfactual was false: v0-style selection did NOT kill useless precursors" (later corrected: V0 carried a 14-slot reserve, mechanism UNRESOLVED) | falsified (gate), mechanism open | RT/REVIEW_PACKET_v1 s0,s3 6a28fc49e |
| Tyche v0, 09-30 | end-to-end lens loop without leakage | 32 worlds, 27-op causal lens genomes, lin/tree/tab organisms, R0/R2 | marginal gain vs ecology; err/dis residual; z>=4 admission | TSD twins, PRF, LEAD cheat, 64 matched random lenses | 2368 lenses, 44 admitted | 0/8 negative worlds false gradient; LEAD cheat z 54.9 rejected; P2 count mod 3 +0.675; P1 delayed xor stuck 0.029-0.037 for 40 gens | H1 INDET (UNREACHABLE_BY_DESIGN per Harmonia), H2 PASS, H3 FAIL, H4 FAIL, H5 PASS, H6 INDET; "v0 positives are instrument positives" | mixed | RT/REVIEW_PACKET_v0 bdeba9865 |
| Tyche residual catalogue v0/v0.1, 09-30 | inventory of fleet residuals | text quotes at sha + committed rows | validate(): path@sha, exact quote, raw_rows exist | 10 rejected entries | 122 admitted | 67 with raw rows; 17 cross-engine niches (tag in >=3 engines) | "asserts nothing about any phenomenon's truth" | built, unperturbed | TY/residuals/README.md 8cb8d804a |
| E-ANANKE-W-Z T-SWAP-AUDIT3, 09-30 | re-run CHANCE groups under promoted swap_rel (REL4 H2) | PTE C1 specimens | swap_rel.from_pairs, z_ci transfer class | KA: W-L n1_s3, hold_latch; must-fail | 124/249 groups, 365/733 rows, M=512 | 35 CARRIER-NAMED (28.2%), 61 NO-CARRIER-FOUND; consistency vs W-U 279/301 = 92.7% | Pa, Pb HELD; "consistency fell below its frozen bar (95%) ... reported as a seed-sensitivity finding" | partial | W-Z 2933399c0 |
| E-ANANKE-W-Y T-INS-20, 09-30 | is readout Kp[7] the "site half" of 4781b0a1's joint carrier? | MAJ 4781b0a1 | SINGLE-trial swap arms KP7/KPALL/FLA | Plant A (FAILED its own KA), Plant B, MF-X, MF-SHUF | M=128 | Kp[7] = 0 in all 4224 world-trial-offsets; never differs | "KP7 NOT A CARRIER"; REDUNDANT branch NOT VALIDATED | confirmed (narrow) | W-Y 478c9ec6f |
| E-ANANKE-W-W/W-X REL4/REL5, 09-30 | promote a relative swap verdict with <=1% false certificates | simulation grids | FC rate, Wilson 99% | H0-H3, T90/PCT, ZW must-fail, DEGEN model | 20k-80k per point | H0=H1=H2 FC pass all designs (max .99% P32K12); H2 power 1.000 at p .99 vs H0 .700; H3 fails P32 | H2 promoted -> prometheus/ananke/swap_rel.py (07b463849) | confirmed | W-W 37b3d8bcc, W-X 07b463849 |
| E-ANANKE-W-V T-INS-18, 09-29 | majority vs subset readout in MAJ 4781b0a1 | MAJ 4781b0a1 | per-sensor tagged in-flight swaps, D_piv | PMAJ, PDICT plants, 4 must-fail | M=128 | o2-o8 effect 0.00 though 80-95% of pairs have mirror-different traffic; o12-14 each sensor share .17-.27; D_piv .10-.12 vs 1.00 majority plant | "DISTRIBUTED-NONMAJ"; readout = rectified positive payload-1 evidence in last wake window | confirmed | W-V 3fd53fdd0 |
| E-ANANKE-W-S/W-T T-INS-11/16, 09-29 | what decides S vs C per trial in mixed clock phase | RELAY 2dccdaa5, c16d5231, 8c37f32e | P3 cone (frozen), P8 first-broadcast (post hoc) | fresh ns 0x632 confirm; plants P1/PF/PL | M=256 | P3 frozen H1 NOT SUPPORTED; P8 decisive 1.00 in 4 units both ns; W-T: P8 does not reach 4781b0a1 (22/22), 78f3b0ec, e06701a5 | "one latency-jitter draw on the source's FIRST cue broadcast ... a property of specific cells, not a law" | confirmed narrow | W-S 0c9aaeb84, W-T d38e2aeaa |
| E-ANANKE-W-M..W-U swap-instrument arc, 09-29 | what the mirror-pair carrier swap can say | C1 specimens + plants | lens_swap census (S/C/N), phi, swap_rel REL1-3 | known-answer plants w/ must-fail | 733 CHANCE verdicts re-run | 615/733 stay CHANCE at 512 worlds; 90 -> FLIP; REL2 170 FLIP_REL; 42 low-acc transfers: 19 COMPLETE, 18 PARTIAL, 5 ambiguous | "site_acc + chan_acc ~ 1 ... forced by the mirror-pair design"; relative verdict needed | confirmed instrument | SYNTHESIS_2026-09-29 s1 cf94415d9 |
| E-ANANKE-W-L T-RET-EVO, 09-28 | is retention reachable when the task rewards it? | M2 physics, n-back n=0,1,2 | lo99 > .60 and beats no-memory baseline | plants P1S/P1K/P2S = 1.000 | 10 searches | 4/8 pass; all are integrators (lag profile flat .60-.65); lag-2 selective 0/4; n=0 control also integrator | "a search-reachability limit, not a physics limit" | confirmed | W-L d8ef2dc5b |
| E-ANANKE-W-K intervention reach, 09-28 | minimum evidence an intervention reached its mechanism | 21 PTE fixtures (10 broken, 11 valid) | 16 checks | valid twins, true nulls | 21 | best single K2 (plant through arm's own code) J .70, 0 false alarms; min cover {K2,K4d,K7} | "No single check is universal" -> lens.verify_reach | confirmed (same-author) | W-K 73efed134 |
| E-ANANKE-W-J receiver semantics, 09-28 | do receiver operators shape which mechanisms emerge? | PTE sum/sat/aloha + ARB variant | fresh searches, designed plants | 4 operators x MAJ/RELAY | 32+12 searches | at C1 physics 29/32 presence codes, operator-indifferent; lossless: one SUM count-threshold code .801, =.500 under all other operators | "operator x aggregation gain, filtered by reader invariances" | partial (most frozen P's failed) | W-J 46dc8f25a |
| E-ANANKE-W-H SETRULE, 09-28 | does rule switching expand capability? | 5 cells | fixed-rule hand/searched programs vs A* | CF1/CF2 counterfactuals | 5 | 0/5 EXPANSION; H2 latch .999 vs champion .755; H4b 1.000 vs .590 | "switching COMPRESSES; it does not EXPAND" | confirmed in-bounds | W-H 3aa3caf90 |
| E-ANANKE-W-G T-RET-2 (SI01), 09-28 | any nontrivial retention regime in champions? | 16 specimens | L1-L4 levels, Holm | 5 plants incl. latent Kp store C-AVL | 2 ns | every adjusted p = 1.0 for L3/L4 | "NO nontrivial retention regime"; SI01 CLOSED for current champions | confirmed | W-G b0985cd10 |
| Q2 X4 / T-WC-2 emission cost, 09-27 | does an emission cost select presence (firing) codes? | HOLD at M2 physics | fire share; carrier swaps | A0 no economy vs A1 e_income 2, c_emit 1, e_max 64 | 3 seeds/arm | A1 3/3 competent, fire share 1.0; A0 1/3 communicates (also fire share 1.0) | "UNRESOLVED (rule ambiguity)"; cost changed WHETHER champions communicate, not code class | inconclusive | W-C/X4_RESULT.md a4d054ea0; lease comms #768/#769 |
| ARC2 W-A..W-F, 09-27/28 | M2/M3 mechanisms, carrier census, retention, Aether contrast | C1 specimens | carrier swap, echo model | designed plants | 166 cells census | echo model predicts 46/46 unseen curves (median MAE .02); census HOLD SITE 81/85; SETRULE bootstrap 27/42 | M2 = strict two-hop echo; M3 = transport + one-time SETRULE bootstrap | confirmed | SYNTHESIS_2026-09-28_ARC2 a4d054ea0 |
| PTE-C1b, 09-26 | adjudicate M2 (in-flight memory) and M3 (self-modifying MAJ) | 3 specimens + 12 fresh searches | per-carrier resets, flush, corrected drop window | positive-control eligibility (A3) | 27 cells, 510 s | M3 corrected window 0.501/0.500 vs C1 window 0.697/0.686; M2 mid-gap flush 0.497; M2 reproduced 3/3 SIGNAL | "M3 is TRANSPORT arriving on the readout tick; C1's null was an instrument blind spot" | confirmed | REVIEW_PACKET_PTE_C1b cc98596dd |
| PTE-C1, 09-24/25 | can comm-dependent organisation emerge in a packet substrate? | integer tensor world, 16-op programs, GA pop 96 x 36 gens | held-out 64 worlds, mirror pairs, lo99 > .55 | zero-comm, shuffles, oracle bit-exact | 6596 rows, 12 h 02 m | A1 COMM_DEPENDENT 8/352; RELAY held .837-.883 vs .50 no-comm; N=2304 .882; XOR 0/83, FLIP 0/82 | "Rare, causally verified, reproduced, size-free packet transport ... topology-bound" | confirmed (unreviewed) | REVIEW_PACKET_PTE_C1 e35fb9704 |

## 2 Mechanisms (seat words; seat-claimed level -> my judged level; synonyms)

| mechanism (seat words) | claimed | judged (ATLAS_DERIVED) | synonyms elsewhere | pointer |
|---|---|---|---|---|
| M1 ROUTED RELAY: "depends on WHERE packets go on the lattice, not on when"; topology-bound | CAUSAL_SUPPORT, reproduced 3/4 | strong within PTE; W-C later: 3 of 4 carry the cue as SOURCE PRESENCE (who fires), not content | "transport", "message passing", presence code | C1_REPORT s3; W-C Tests |
| M2 "tuned two-stage echo" / "delay-line memory in packets"; "it schedules, it does not store"; carrier = "channel state" (Chandy-Lamport) | predicted by zero-parameter model 46/46; reproduced 3/3 | strongest mechanistic claim in group (model predicts + designs 7/7) | delay line, channel state, activity-silent memory (rejected by seat for M2), load-bearing non-material state (Archaeon FF-20) | SYNTHESIS_09-27 s2; W-A; designed_echoes |
| M3 "transport + a one-time SETRULE bootstrap"; bootstrap is "a PHYSICS ARTIFACT (registers are 0 at tick 0)" | shown (rule state identical between mirror partners every tick) | solid; M3 itself did not reproduce mechanically (0a23 0/4) | configuration, initialisation escape | CORRECTIONS_2026-09-27 K3; ARC2 s2 |
| SETRULE roles: "event-triggered branch (leaky timer)", "phase-selected write-enable clock (sample/hold)", "one-tick relay specialization" | necessary in 3 cells (CF1) | solid, n=5 | bundled-data clock, hidden state (Buonomano-Maass) | W-H |
| SOURCE-LATCHED REGENERATION (4781b0a1): sensors latch and keep firing; bit at source until deadline, then channel | exploratory then refined | later refined: readout = "rectified positive payload-1 evidence" DISTRIBUTED-NONMAJ; Kp[7] never a carrier | pipeline handoff | ARC2 s3; W-V; W-Y |
| Receiver operator as computable-function table: SUM nomographic, SAT normalized mean, ALOHA erasure, ARB voter process | theory + plants (SUM .823 = SAT, ARB .727, ALOHA .500) | theory solid; behavioural relevance only where "aggregation gain" pays (~.02 at C1 physics, ~.13 lossless) | superposition vs arbitration, over-the-air computation, voter model | W-J |
| Presence-as-content (F7): "a swap verdict names the reader's register, not the physical code" | confirmed on 6 champions | important ruler caveat | observer-relative carrier | W-I s5; W-C Surprise 1 |
| Emission cost -> communication: cost made champions communicate (3/3 vs 1/3) but did not change code class | UNRESOLVED, n=3/arm | anecdote; not a selection law | energy economy, metabolic cost, sparse coding (Levy & Baxter) | W-C/X4_RESULT |
| Energy economy as a physics GATE of the hand relay design: economy low -> high -0.45 / -0.22 (SUPPORTED) | SUPPORTED boundary but of the HAND DESIGN | not a law of evolved competence (seat says so) | resource constraint | C1_REPORT s4 |
| Sign-asymmetric integer decay: "positive memories stall at 2^k-1, negative ones erase" -> HOLD 0.75 dip | predicted in DESIGN s10, observed | solid engine fact | quantisation floor | C1_REPORT s4; LEDGER P2/P8 |
| Integration (search reaches retention as INTEGRATION, "S accumulates the whole cue history") | 4/8 n-back searches + n=0 control | solid; post-hoc lag profile | integrator, accumulation trace | W-L |
| Plastic "scars": frozen signed writes to non-decaying stores; fresh2/3's w scar "IS read, as sign-scrambled interference" | preregistered L2 in f7e62fe3; scars descriptive | real observation, behaviourally inert or chaotic | trace-not-memory, decodable != used | W-E, W-G |
| First-broadcast latency-jitter rule: per-trial S vs C = one jitter draw on the source's first broadcast | post hoc, confirmed on fresh ns | exact in 3 RELAY cells only; does not transfer | delivery randomness | W-S, W-T |
| H6 "SEARCH REACHABILITY, NOT PHYSICS, BOUNDS WHAT PTE SHOWS" | SURVIVES (4 lines) | well supported as a pattern; untested against larger budgets/other search | physics x search, expressible vs reachable gap | CROSS_THREAD_COMPRESSION H6 |
| H1-H5: function != storage form; carrier != location; decodable != used; intervention != causal test; family label != mechanism | SURVIVES (scoped) | heuristics with explicit falsification attempts | -- | CROSS_THREAD_COMPRESSION |
| Tyche: "noisy many-case lexicase" as "an implicit dark ecology"; exaptation (graft from sibling world) + one insertion completes xor | exploratory trace, later UNRESOLVED vs v0 reserve | open; Block R: parent choice by NOISE-level case 395 events vs significant case 280 | neutral drift, exaptation, coalition | RT/REVIEW_PACKET_v1 s3-4; Block R |
| Tyche: "Soft precursors" -- windows/smoothers give graded footholds to 2-way xor | observed once (+0.076 gen 15) | undermines 2-way xor as a zero-marginal needle in this chemistry | partial gradient | REVIEW_PACKET_v1 F2 |
| Tyche: senses assemble as COALITION (+EXAPTATION) 62/92; exaptation in 63/92; "fragments stored, never sets" | Block R natural histories | descriptive; strict-survivable path share .929 | -- | REPORT_BLOCK_R |

No thermodynamic / free-energy / "pressure law" claim is made by Ananke. "Pressure" appears only as operator vocabulary (charter; C2
load axes; SI01 "repeated-task pressure") and in Tyche v2 as "pressure map" axes (selection harshness, diversity, coalition depth,
needle order, chemistry). Energy appears only as the PTE economy dials (e_income, e_max, c_emit, c_op, c_mem; off in every C1 specimen).

## 3 Failures and invalidations (LOST interpretation / SURVIVING observation)

| failure | LOST | SURVIVES | pointer |
|---|---|---|---|
| D-A packet-ablation window [t0, ro) excluded the readout tick; delay == delta = 4 in M3 | "M3 self-modifying, timing-locked, packets irrelevant" | M3 zero-comm 0.50; readout-tick drop 0.511/0.500; latency -1 IMPROVES to 0.741/0.715 | C1_ERRATA E1 |
| frozen_routing vacuous under dest_mode "all" (w never read) | "SETRULE carries it" (partly) | freeze_rule -> 0.52 | C1_ERRATA E2 |
| C1 memory ablation reset only S | "M2 not in any site" under-identified | per-carrier resets: flush -> 0.497, w reset -0.066 (disruption) | C1_ERRATA E3; CORRECTIONS K2 |
| C1b census read only payload component 0 | "signed payload sum is NOT the code" (0.44) | component-1 sign decodes at 1.00; swap of comp 1 FLIPs | CORRECTIONS_2026-09-27 K1 |
| PREREG causal rules encoded the expected mechanism | M2, M3 labelled NOT_SUPPORTED | ablation patterns clean | LEDGER 09-25 row |
| boundary criterion over-fires (categorical dials, zero-variance, one-level dips) | 13 SUPPORTED boundaries partly inflated (4 = one HOLD dip) | RELAY plant gates decay/delta/economy | C1_REPORT s4, F4 |
| wave C HOLD env variants changed dials HOLD never reads | 22 "transfers" | -- | C1 packet s10 |
| absolute swap rule cannot call FLIP when normal ~.57-.62; 64-world designs | many recorded CHANCE read as "needed but not carrying" | 615/733 stay CHANCE at 512 worlds; 42 complete/partial transfers now FLIP_REL | CORRECTIONS_2026-09-29 |
| "site_acc + chan_acc = 1" read as mixture evidence | "all 14 JOINT cells are phase mixtures"; designed-echo mixture signature (retracted) | by phi 3/7 are mixtures; identity holds 100% in some, 62-68% in 369f5a5b | W-I Surprises; W-M |
| absolute thresholds in C1b (kills hi99 <= 0.60) | "M3 not reproduced (mechanical)" | f6b6 fresh champions show specimen fingerprint descriptively; Artemis R-05: relative bar flips it 3/3 | C1b packet s5; comms #870 |
| W-O plan committed with results (93e2e544b) | W-O predictions as frozen | counts reproduce 733/733 (Harmonia) | CORRECTIONS s Harmonia |
| W-Q commit "certifies all 42" | completeness of 42 transfers | 24 z<=-.95, 2 in (-.95,-.75], 16 in (-.75,-.57] | same |
| X4 rule did not define undefined fire share | X4-P1 verdict | A1 3/3 fire share 1.0; A0 1/3 communicates | X4_RESULT |
| W-Y Plant A failed its own KA; REDUNDANT branch has no chance anchor | any REDUNDANT call | Kp[7] = 0 always | W-Y |
| W-S frozen predictor P3 cone | H1 delivery timing (frozen) | P8 first-broadcast 1.00 post hoc, replicated | W-S |
| Tyche v0 H1 VOID controls (P3, P4, P6 accessible to random lenses; 3 valid < 4 needed) | H1/H6 as science | P2 +0.675 replicated; P1 stuck | Harmonia #1039; packet v0 |
| Tyche v0 err/dis residual measured organism decorrelation | H3 residual shift | PRF1 err .261 -> .140, dis .492 -> .735 with flat accuracy | packet v0 F1 |
| Tyche v0 tab 10-feature budget newest-first | H4, much of 28/44 tab admissions | tab K1 baseline 1.000/.995/.547/.998/.518 | packet v0 F2; #1047 |
| Tyche v1 R2 ruler leak (shifts delays by 2) | R2 in v1 | fixed pre-freeze: R0-only | packet v1 s1 |
| Tyche v1 V0 arm included unlogged 14-slot reserve | "survived on noise-level lexicase wins" | trace shows noise-level best cases | packet v1 CORRECTION |
| Tyche Block R OV clock reads population only | OV for coalition-built adaptations (STRICT R3 censored) | 2/72 adapted | REPORT_BLOCK_R "Instrument gap" |

## 4 Rulers

| ruler | sees | cannot see / audit | pointer |
|---|---|---|---|
| Held-out 64-world mirror-pair accuracy, 99% pair bootstrap, lo99 > .55 (constant policy = 0.500 exactly) | behavioural competence | holdouts are seed namespaces, not sealed; lo99 promotion favoured trivial latches | C1 packet s3, s10 |
| zero-comm twin (same law, same worlds) | comm dependence | -- | C1 packet |
| packet ablation window / per-carrier resets / freeze switches | need | window miss (D-A), inert channels; "a reset shows need, a swap shows carriage" (LEDGER) | C1_ERRATA |
| Mirror-pair CARRIER SWAP (FLIP / NO-EFFECT / CHANCE), lens.swap_verdict | which state carries the bit per tick | names the reader's register not the physical code (F7); sum identity; phase mixing on sync period-2; blind at low accuracy | MEMORY_INTERVENTIONS; W-I; W-M; W-R |
| lens_swap SINGLE-trial census S/C/N + phi; truth-table (W-P tt.py) | mixtures vs NEITHER; which sub-arrays and what function | EVERY mode broke identity in 5/7 cells | W-M; W-P |
| swap_rel REL1..REL4 (DF/DN certificates, BOOTT + SD floor, P_FLOOR 32, transfer class COMPLETE/PARTIAL/OVERSHOOT) | certified relative verdicts at low accuracy | FC grid untested for nearly-constant null-side pair statistics (W-W caveat); consistency 92.7% < 95% across seeds (W-Z) | W-N..W-Z |
| lens.verify_reach (REACHED / UNREACHED / NOT_VERIFIED) from W-K | whether an arm touched its pathway | K4d partly vacuous for Controls arms; K7 NA on some; one author for fixtures and checks | W-K |
| Retention levels L1-L4 with cue-blind probes (BLANK, PING, CLEAR_S0, CLEAR_FAST, RELOC) | present / decodable / effective / available | validated on 5 plants incl. latent Kp store | W-G |
| Echo particle model (zero parameter) | interval kernel of M2 | predicts; not an emergence test | W-A; designed_echoes |
| C1b positive-control eligibility (A3): absence counts only where a plant FIRED at specimen physics | protects absence readings | c1b.intact() returns True for NOT_APPLICABLE (W-K says should be NOT_VERIFIED) | C1b packet s3; W-K |
| Tyche marginal gain vs ecology, z>=4 admission, 64 matched random lenses, causality audit (future replaced at 5 cuts) | new usable info; shortcut rejection | per-organism marginal value lets weakest organism make any feature look valuable (Q1 v0) | packet v0 s2 |
| Tyche capability deficit D = acc(ecology+oracle) - acc(ecology) | calibration-world residual | undefined for natural residuals (no oracle) | packet v1 s1; v1 directive |
| Tyche residual catalogue validate() | text exists at sha, rows exist | "a validated quote proves the text exists at that sha, not that the phenomenon is real"; tags model-assigned | TY/residuals/README |
| Tyche OV clock / stored optionality | adaptation speed; fragment storage | misses fused coalitions | REPORT_BLOCK_R |

## 5 Repairs (and whether the outcome moved)

- Corrected drop window [t0, ro] -> M3 reading moved from "self-modifying memory" to "transport on the readout tick" (C1b s4). RELAY/HOLD verdicts did not move (4/4, P6 held).
- Per-payload-component census + carrier swap -> M2 code found on component 1 (moved: code absent -> code decoded 1.00).
- Absolute -> relative swap verdict (REL1 W-N gate; REL2 per-verdict attainability; REL3 BOOTT P_FLOOR 32; REL4 SD floor) -> 733 CHANCE: 170 FLIP_REL under REL2 (W-Q); W-L CHANCE -> FLIP at 512 worlds (W-N). Moved.
- EVERY -> SINGLE-trial swaps -> identity restored at o>=1 in 7/7 cells; classes interpretable (W-M). Moved.
- Phase-indexing by update clock (W-R) -> pooled single letters hold in one phase only (moved).
- Plans committed by principal before worker runs (after Harmonia #1045), first at T-SWAP-REL4 (CORRECTIONS s process change).
- Tyche v1: per-world ecology, tab inputs [candidate, raw], deficit residual, R0-only -> negatives flat (deficit 0.00), no manufactured gaps; Z solves appeared (V0 3/10) that v0 never produced. Moved (instrument), gate still FAIL.
- Tyche v2: STRICT arm makes "would have died" true by construction; membership of every preservation channel logged; memory-bounded caches (amendment 1). Outcome: adaptation ~absent (2/72).
- Leases: host-file fallback (Redis 6390 down) -> Fabric lease cutover 8370083ae (#901, #934).

## 6 Primitive-level interventions (outcome change)

| primitive | intervention | outcome | pointer |
|---|---|---|---|
| communication / transport | zero_comm; max loss; shuffled destinations | RELAY -> 0.50-0.52; shuffled timing 0.73-0.88 (timing tolerated) | C1 packet s8 |
| locality / topology | move RELAY law to random graph | 0.50 in 4/4 (topology-bound) | C1 packet s8 |
| scale | N=400/1024/2304 frozen RELAY law | .875/.893/.882 (size-free) | C1 packet s6 |
| time / gating | latency +1 / -1 on M3 | +1 kills (0.493/0.500); -1 improves (0.741/0.715) | C1b s4 |
| time / clock phase | sync update_period 2 | S/C/N blends split by phase (o4 fN .73 even vs .12 odd) | W-P; W-R |
| memory / state | flush in-flight mid-gap on M2 | 0.883 -> 0.497; flush 1 tick pre-readout 0.853; S/inbox resets no effect | C1b s4 |
| write authority / self-modification | freeze_rule (SETRULE off) M3 | 0.52; freezing after trial 0 no change; from start cuts emissions 4x | C1b; SYNTHESIS_09-27 s3 |
| write authority | forbid switch at readout site (W-H S1) | .500 exactly; same pin at random site 0 | W-H |
| receiver operator (superposition vs arbitration) | re-evaluate champions under SUM/SAT/ALOHA/ARB | C1 physics: indifferent (29/32); lossless SUM count code .801 -> .500 elsewhere; ALOHA destroys dense codes .717 -> .539 | W-J |
| energy / resources | emission cost (e_income 2, c_emit 1, e_max 64) | communicating champions 3/3 vs 1/3 no-cost; code class unchanged | X4_RESULT |
| energy (hand design) | economy low -> high | RELAY plant viability -0.45 / -0.22 | C1_REPORT s4 |
| decay | decay_shift 0 -> >0 | RELAY plant viable 19/245 at 0, 0/755 otherwise; evolved MAJ SIGNAL at decay 3 and 6 | A0_FINDINGS s3; C1_REPORT s2 |
| initialization / reset | registers 0 at tick 0 | SETRULE bootstrap to rule 0 (artifact) in 64% of 42 cells | W-B (27/42) |
| selection / admission | STRICT vs LEX vs RES; reserve 14/48 slots | Tyche: no arm advantage at equal budget; RES produced the one "preserved-useless-until-needed" assembly | packet v1; Block R |
| heredity / recombination | graft (cross-lineage), coalition fusion | 62/92 senses by coalition, 63/92 with exaptation | Block R |
| selection (task incentive) | n-back reward at M2 physics | integrators, not selective stores | W-L |
| search budget / reachability | hand plants vs evolved | plants beat champions (.999 vs .755; 1.000 vs .590); lag-2 plant 1.000 vs 0/4 searches | W-H; W-L |

## 7 Buried signals (observation kept apart from interpretation)

- W-B: HOLD champion 311c465f "falls from 0.76 to 0.55 when distractors are removed. The champion depends on distractor input" -- marked Unexplained, never revisited; also catalogued as R-S016 (tag needs_noise_to_work). W-B REPORT lines 77-78.
- W-J: "One ALOHA champion's code requires collisions to be erased" (0.614 -> 0.467 below chance without erasure). W-J E6.
- W-J: "The only dense MAJ champion in E2 arose under ARB" -- unexplained.
- C1: evolved RELAY SIGNAL at loss 0.6 where the hand design is 0/253; MAJ SIGNAL at decay 3 and 6 where design is 0/755; "L2' and L2 are disjoint in RELAY (0 of 7)". Evolution works outside the designed habitable zone -- never followed up as its own thread. C1_REPORT s2.
- C1: seeding A1 in "living" A0 cells gave no advantage (RELAY 2 vs 2, MAJ 2 vs 1). C1_REPORT s2.
- C1: M3 latency -1 IMPROVES accuracy (0.693 -> 0.741; 0.686 -> 0.715): champions are not at their own optimum on timing. C1b s4.
- C1b: ~1500-1900 packets in flight at every trial onset, uncorrelated with previous target (background channel load always present). C1b s4.
- W-I: cue-dependent state present but unused -- HOLD 7b7b025e twins differ in flight at 9/9 ticks yet channel swaps leave the trace bit-identical; routing w differs between twins in 8/20 panel specimens, w swap never FLIP/CHANCE; "3 of the 4 global HOLD site-latches also emit cue-dependent traffic that nothing reads".
- W-I: panel distractor fragility, median retention .19 (T-CT-5 never run); slack predicts latency tolerance rho .52 (T-CT-3' OPEN, never run).
- W-V: 80-95% of pairs carry mirror-different sensor traffic to the readout at o2-o8, yet swapping it changes nothing, not even raw S0.
- W-G: f7e62fe3 w trace includes actuator-site elements and still no cue-blind probe turns it into an answer; fresh2/3 +8 w scar at the sensor in 32/32 pairs drives chaotic divergence (4-9 answers/trial changed, unsigned). T-SI-SCAR OPEN.
- W-L: the n=0 HOLD control champion is also an integrator ("retention as a side effect").
- W-O: unreadable verdicts FLIP at 21.4% vs readable 7.9% -- the inverse of the prediction (~40% / <=10%).
- X4: A1 seed-0 champion is "the first PTE specimen whose counts swap FLIPs"; firing codes arise without cost too.
- Artemis R-09 (#870): unsupervised fingerprint labeller ranks unremarked MAJ cell 613162a3 second in novelty; never adjudicated.
- Tyche v0 OPEN ANOMALIES: P5/R2/tree lens L-3c1c67ab5c +0.134 (z 12.3) on selection seed, EXACTLY 0.000 on both fresh seeds (TYCHE-26 open); ADV_decoy best val 0.114 transient then 0.036.
- Tyche v1: a zero-value partner lifted a ~0.1 lens to ~0.2 and completed +0.513 (F4 "useless-plus-useful coalitions are common").
- Tyche Block R: stored-any fragment share rises monotonically with world diversity (solo .045, related .079, broad .120) though adaptation did not; lexicase stores more fragments than the explicit reserve.
- Parked: T-REDISCOVER (design flaw: latch confound), T-WC-2b (powered emission cost, >= 8 seeds), T-WJ-1 aggregation-gain sweep, T-H1 expressivity task, T-REACH-GAP (OPEN, top tier), PTE-C2 prereg (ANANKE-26) never written, FLIP zero-comm twin rerun (ANANKE-27).

## 8 Contradictions and cross-engine hooks

Internal contradictions:
- Operator harvest directive (4a97f97fa) calls T-SWAP-REL4 "pending" and asks to "Prepare REL4 as if its eventual result could be the last PTE observation", but REL4 already ran (W-W 37b3d8bcc) and REL5 promoted swap_rel (07b463849). ATLAS_DERIVED: the directive may refer to a planned REL4 on real specimens or be stale.
- Ananke STATUS.md (a90dede19, currency 09-29 03:34Z) says next = T-INS-6/T-SWAP-LOWACC; WORK_STATE says both CLOSED and harvest RUNNING. TODO.md currency 09-25. Tyche STATUS (14:30Z) says "next: v2 design" while WORK_STATE (16:30Z) says Block R DONE.
- W-P says payload-1 Msum is a joint carrier "at every offset"; W-V: for readout-bound traffic only at o10 and later (early role must be sensor-to-sensor).
- W-L CHANCE vs W-N FLIP on the same champions (sample-size), then W-O: the effect does not generalise (84% stay CHANCE).
- Tyche v1 F1 attribution vs its own CORRECTION (reserve unlogged).
- Tyche #1047 vs Harmonia #1039: H4 FAIL "nearly unattainable" vs actually attained (evolving baseline).

Cross-engine hooks named by the seats:
- Aether: content-vs-timing contrast REFUTED (W-C); real axis operator x aggregation gain (W-J); proposals A-J1..4, T-WC-3..5 for Aether's owner (not run). Aether E-011 (#1058) "rcv_adr vs rcv_add" is the Aether-side analogue.
- Cosmos C3 P1/P2 present-vs-used with a deliberately timed full-state swap = PTE carrier swap "reached independently" (X-2); Artemis R-10: Cosmos v3 certificate agrees with Ananke on M2 but "at the tick before readout on odd-phase trials the cue is already in site state". Ananke is now R-STAT reviewer of Cosmos C4 (#1137; interim ded6f5729).
- Archaeon FF-20: M2 is "causally load-bearing, non-material state" (X-3).
- X-4 / W-D fleet "interventions that cannot fire": Nestor C9-D16 unwired switch, Nestor A-3 wrong target, Archaeon SFE-01 tabu never fired (spurious positive via cell-label RNG), SFE-05 dead branch, Aether AETH-03 forced by construction.
- Herakles EvCA step-T vs stable readout = M3 deadline (X-5).
- Tyche v2 / Ananke H6 converge: both find search-reachability (not substrate) is the binding limit; Tyche Block R "hard wall" to zero-marginal laws within 30 gens mirrors Ananke W-L "lag-2 selective 0/4 though a 16-line plant solves it". Also Theseus v0 (#1125): "rulers non-discriminating vs random programs".
- Tyche <- Theseus: 299 DARK_OBJECTs + 8 admitted lenses in Tyche genome format; unanswered interface question (#1124).
- Tyche <- Artemis residuals (#1121, #1133): PROTEUS-46 neutral 5-edit path; Ares co-dependence origin INDETERMINATE; Daedalus D8 history null; stackvm double-solve deflationary; quotient-organism crucibles A/D/E never ran.
- Bellerophon E-BEL-REPL-01/02 addressed to Tyche (#1078, #1113, #1126): residue NOT_REPLICATED / descent UNRESOLVED.

What TYCHE'S RESIDUAL PROGRAM IS (establish, per operator request):
- Two distinct "residual" objects (ATLAS_DERIVED distinction, grounded in text):
  (a) In-world DARK RESIDUAL: "observations or state variation for which the current ecology of lenses and organisms has not yet
      found reproducible exploitable structure" (charter). Operationalised after v0 as capability deficit D (oracle only on
      calibration worlds). "Natural dark residuals ... We genuinely don't know" (v1 directive).
  (b) Natural RESIDUAL CATALOGUE (CWO NEXT/RESERVE, #1032): "Phenomena that Prometheus experiments observed and left unexplained,
      contradictory, weak, unreplicated, parked or instrument-ambiguous, each with provenance" (TY/residuals/README). 122 entries,
      clustered into 17 cross-engine behaviour niches; RESERVE = "turn the best residuals into bounded experiments"; Gate 7 "natural
      122-residual habitat -- ONLY after gate 6 is shown" (WORK_STATE reserve). Currently frozen by operator v1 directive.
- Residual observations that would FEED it (from catalogue.py schema + README + Theseus exchange):
  1. Kind in {unexplained, contradictory, weak, not_replicated, parked, instrument_ambiguity}; one-sentence phenomenon with numbers
     "as written"; an EXACT quote at a pinned sha (validate() rejects paraphrase: 8 of 10 rejections were quote-not-at-sha).
  2. Committed raw rows at the checked ref (67/122 have them; imported entries without rows are weaker habitat).
  3. The observation must be separable from its failed interpretation (31 entries carry a framing_note that the source does not
     support the framing) -- i.e. exactly the "buried signal" format.
  4. For perturbation (RESERVE/Gate 7) a residual must become a WORLD: generate(spec, seed) -> (X, Y) time series with T long enough
     (Tyche worlds T = 12100; Theseus offered T = 128, #1124), a target Y, and a TARGET_STRUCTURE_DESTROYED twin as negative control.
  5. Highest-value niches today: context_dependence (14 engines, 17 entries), measure_disagreement (10), control_shows_effect (9),
     silent_or_null_winner (8), threshold_behavior (7), structure_killed_under_one_representation (6) (CLUSTERS_v0_1.json).
  Ananke entries in it: R-A046 XOR/FLIP null; R-S016 311c465f distractor dependence; R-S017 e79e72df unreplicated; R-S018 SAT/dense-code
  non-replication + ALOHA-needs-erasure; R-S019 W-R phase flags unreplicated. Tyche self: R-S038 seed fragility; R-S039 P1 stuck.
  ATLAS_DERIVED candidates from this group not yet in the catalogue: M3 latency -1 improvement; evolved transport outside the design
  habitable zone (C1 s2); present-but-unused cue traffic (W-I, W-V); fragment storage scaling with diversity (Block R).

## 9 Five things a cross-engine synthesist must know

1. The strongest PTE finding is not a phenomenon but a gap: every evolved mechanism has been hand-reproduced or beaten by a small
   plant (W-H .999 vs .755; W-L plant 1.000 vs 0/4 lag-2; designed echoes 7/7), so Ananke frames results as PHYSICS x SEARCH (H6).
   Tyche independently hits the same wall (zero-marginal needles; 2/72 regime adaptations). Treat "absent in champions" as reach, not law.
2. The main ruler (mirror-pair carrier swap) was repaired five times in 3 days (identity sum, SINGLE vs EVERY, phase indexing, relative
   verdicts REL1-REL4, reader-register F7). Any cross-engine carrier/memory comparison citing pre-09-29 PTE CHANCE/JOINT labels must go
   through CORRECTIONS_2026-09-29_SWAP_AUDIT; 615/733 CHANCE survive, 42 low-accuracy cases are transfers.
3. "Interventions that cannot fire" is a documented fleet-wide failure shape (PTE D-A window, inert routing, Nestor unwired gate, Archaeon
   never-firing tabu, Aether forced-by-construction); W-K: only a plant run through the arm's own code (J .70) reliably separates
   unreached arms from true nulls; identical outputs do NOT imply no reach.
4. Energy/emission-cost evidence is thin: one X4 run (n = 3/arm, UNRESOLVED by rule ambiguity) says cost changes WHETHER champions
   communicate, not which code; the SUPPORTED economy boundary belongs to a hand design. No thermodynamic claim exists in this group.
5. Tyche's natural residual catalogue (122 entries, 17 niches) is the fleet's intended sink for buried signals, but it is gated shut
   until Tyche's calibration gate 6 passes (it FAILED in v1); entries need exact quotes at sha + committed rows + a world form with a
   structure-destroyed twin to be perturbable. Ananke's inference-harvest deliverables did not exist at snapshot; nothing from it can yet be cited.
