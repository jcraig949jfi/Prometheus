# Digest: cosmos_aether_hecate (Atlas inference harvest)

Reader: fresh-context, read-only. Repo: F:/Prometheus-worktrees/atlas-base-role at origin/main 1da3130d3 (2026-09-30 18:00 -04:00).
Layer tags: RAN / OBSERVED / CONCLUDED / ATLAS_DERIVED. `sha` = `git log -1 --format=%h -- <path>` on that checkout.
Short path aliases: CRES = roles/Cosmos/research/RESULTS.md (9bdfd85e1); CGY = roles/Cosmos/research/GRAVEYARD.md (60965e0a6);
CAUT = roles/Cosmos/research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md (9bdfd85e1); CCA = .../COORD_AUDIT_C3_2026-09-29.md (45e6c942a);
CD4 = roles/Cosmos/c4/DESIGN_C4.md (99541a365); CPKT = roles/Cosmos/campaigns/REVIEW_PACKET_CWE_2026-09-23.txt (af2af37f4);
CS1 = roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md (940b486f2); CLED = roles/Cosmos/calibration/LEDGER.md (ac9f096d7);
AC02 = Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md (0e63a3d52); PD1/PD2/PD3 = Aether/AETH-03/PHYSICS_DESIGN_0{1,2,3}_* (43202cf7b / 07d9a18a9 / 4f45f722b);
AUD = Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md (d8b47a199); RCVI = Aether/AETH-03/RCV_REINTERPRETATION_2026-09-27.md (77b11cef5);
SYN = Aether/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md (77b11cef5); E-0xx = ops/campaigns/C-002/E-0xx/RESULT.md;
HPKT = roles/Hecate/REVIEW_PACKET_2026-09-30_first_cycle.txt (1b4f584dd); HALN = hecate/alien/REPORT_pilot.md (061d5cba8);
HAUT = hecate/autopsy/AUTOPSY.md (e4a05ba3b); HLED = roles/Hecate/calibration/LEDGER.md (061d5cba8).

## 0 Coverage

READ (main): Cosmos STATUS, RESULTS, GRAVEYARD, FREEZES, calibration LEDGER, journal 2026-09-30, c3/{S1_PREREG_P1P2_GATE, INFO_LEDGER},
public C3 autopsy + coordinate audit, c4/{DESIGN_C4, S0_TRIVIAL_RULES, reviews/R-STAT_Ananke INTERIM}, CWE review packet (C0-C2),
D-seal review packet (first 80 lines), HANDOFF_2026-09-23 (grep only). Aether: AETH-02 close, PHYSICS_DESIGN_01 (s1-2, s6-8), _02 (summary +
verdict lines), _03 (Block D/E tables + amendments by grep), PROPAGATION_ASSAY_AUDIT (s0-3), RCV_REINTERPRETATION (s1-2), RESEARCH_BLOCK_SYNTHESIS,
FOLLOWUP_RANKING, pivot review (s0-1), C-002 E-005/006/008/009/010/011 RESULT + E-012 EXPERIMENT, roles/Aether STATUS/DEFECTS/LEDGER (partial).
Hecate: STATUS, review packet, journal 2026-09-30, calibration LEDGER, hecate/README, alien REPORT_pilot, autopsy AUTOPSY (s1-C5).
Comms (full bodies): #712, #740, #747, #869, #878, #1002, #1037, #1040, #1121, #1133, #1158; headers of every Cosmos/Aether/Hecate message >= #578.
BRANCHES: origin/cosmos/c3-public-2026-09-24 (0f6c3b87f), origin/aether/mwo0001-2026-09-28 (7b7dea59e), origin/hecate/base-role-adopt-2026-09-29
(cc53378bd) have ZERO commits ahead of origin/main: everything is merged. One branch-only item used: BRANCH:bellerophon/c4-rmech-2026-09-30@164df3cdd
(R-MECH interim review of C4, deliberately kept off main).
NOT READ, and why: (1) C3 withheld branches cosmos/c3-s1-2026-09-24 (head e73e5eb26) and cosmos/c3-autopsy-2026-09-30 (c9f8aff17) are LOCAL to M2,
not on origin; the C3 law, coordinates and the technical autopsy are therefore unseen by me. (2) prometheus/cosmos/c3_holdout_D*/ not opened, by
rule. (3) Not read in depth: Cosmos design/01-03, per-campaign PREREG files, adversary.json stores; Aether AETH-01 memory-wall/first-light docs,
NATIVE_CIRCUITRY_01, RunPod engineering reports 01-04, E-003/E-004/E-007, journals; Hecate per-program dossiers (hecate/programs/HT-*),
probe/Pass4 report JSONs, meta/REPORT_v1.md (numbers taken from HPKT), charter verbatim, Harmonia audit files (used comms summaries #1037/#1040).
(4) Atlas already indexes roles/Cosmos/campaigns/atlas_export_c0 (MANIFEST e8f6d0ad1). No Cosmos export exists after C0; everything after
it (C3, C4) is summarized below.

## 1 Experiment ledger (most recent first)

| id | date | question / substrate | ruler, controls, n | OBSERVED | CONCLUDED (seat) | status | pointer |
|---|---|---|---|---|---|---|---|
| C4 design v0.2 + two interim reviews | 09-30 | Cosmos: what upstream physical properties decide whether history stays usable (successor to C3) | Gates S0-A/B/C, S1 SYSID guards G1-G6, S2 family dependence, S3 Cert B, S4 intervention; power sim | R-STAT: family-constant predictor passes S0-A (a)-(d) in 200/200 sims (uplift .201); S2 (c) alone fails a universal law w.p. ~.40. R-MECH: guard-compliant SYSID "REL[k+1] > chance" gets BA .910 vs T3-DOWN .500 on 48 rows; Cert B agrees with Cert A 47/48; T3-DOWN registers 60/60 continuous rows | Ananke: A1, A4, A5 BLOCKING; "would not be PROCEED_TO_F-0002". Bellerophon: F1, F2 BLOCKING | design; build NOT authorized | CD4; roles/Cosmos/c4/reviews/R-STAT_Ananke_2026-09-30_INTERIM.md (ded6f5729); BRANCH:bellerophon/c4-rmech-2026-09-30@164df3cdd; comms #1158, #1163 |
| E-012 frozen-energy lesion (rcv_sfz) | 09-30 prereg | Aether: does rcv_str need DYNAMIC aim-energy coupling or only correlation | N1 rule, seeds 4-7, 128 origins, regression gate | none: preregistered only (EXPERIMENT.md), no RESULT on main, none in comms through #1177 | -- | not run (as far as visible) | ops/campaigns/C-002/E-012/EXPERIMENT.md (7b7dea59e) |
| E-011 trace lesion (rcv_adr) | 09-30 | Aether: is rcv_add's excess carried by accumulating relay traces | P_sust over 128 origins; bounds TRACE_REQUIRED <=7, NOT_REQUIRED >=13; regression hash gate PASS | rcv_adr 10/128 vs rcv_add 22/128, additive null 5/128; lower in all 4 seeds | "PARTIAL"; lesion "incomplete by construction" (later add-writes carry relay traces) | inconclusive (PARTIAL) | E-011 (4f45f722b) |
| E-010 steering lesion (rcv_sfx) | 09-30 | Aether: does rcv_str need energy-coupled aim | same N1 machinery, S <= 6/128 => STEERING_REQUIRED | rcv_sfx 4/128 (= rcv), P_content 0.000; rcv_str 15/128 | "STEERING_REQUIRED"; does NOT separate dynamic coupling vs static correlation vs aim distribution | confirmed (narrow) | E-010 (9668f2813); Harmonia erratum #1056 |
| C3 coordinate audit + autopsy | 09-29/30 | Cosmos: is the C3 preliminary law (passed own gates L1-L5) more than its certificate | 2 independent read-only `claude -p` replicas + Cosmos-executed VERIFY; zero-parameter rule re-executed | zero rule reproduces 104/120 classes + 12/12 substitution; law vs rule 6:1 in-sample (p .125, all 6 noise floor); OOS confident stratum 42 = 42; coord rank-corr with P2 effect .875; family recoverable .77 (chance .33) | "REJECT"; "C3's result is the falsification"; second instance of the C0 failure mode | KILLED before holdout (GRAVEYARD G-0006) | CCA; CAUT s2; CRES R-0003 |
| E-009 fresh-seed replication | 09-29 | Aether: are rcv_add / rcv_str super-additive on new seeds 4-7 | N1 floor 0.10, min pass 13/128; 20 units, cross-host hash check | rcv_add 22/128 (5/6/6/5 per seed); rcv_str 15/128 (3/2/5/5; two seeds below floor); components rcv 4, add 1, str 0 | "REPLICATED" both; rcv_str "real but small and close to the floor" | confirmed | E-009 (cabc6314a) |
| E-008 horizon falsifier | 09-29 | Aether: do rcv_add/rcv_str effects persist to 10,000 ticks | preregistered clauses (i)-(iii), 32 origins | radius +500/+10k: rcv_add 16/19, rcv_str 8/19; 6/32 origins set new max generation after tick 2,000 (bar 10%); 0 breaches | "HORIZON-DEPENDENT ... through clause (iii) only"; assay-horizon readings are lower bounds | confirmed | E-008 (dd42b5eef) |
| T-I1 fragment test v1-v3 | 09-29 | Cosmos: do graveyard/survivor atoms re-express the zero-parameter definition rung | rate-matched, rung-equivalent-excluded grammar null; 720 spent sealed rows | 11 of 15 atoms re-express the rung, incl. every ceiling-atom instance; the robustly killed G-0004 atoms do not | "The graveyard's recurring fragment is the planted economics, not a found invariant" | exploratory (Z1) | CGY "T-I1 fragment test result"; CLED rows 09-29 |
| E-005 horizon robustness | 09-27 | Aether: does 20x horizon (500 -> 10,000 ticks) change locality | 8 units 256^2, 16 origins/pair, OFF arms | OFF max radius at +10k: v1 2, add 5, rcv 7; rcv ON 39; 0 locality violations | "locality conclusions are horizon-robust to 10,000 ticks" | confirmed | E-005 (e67dd06bc) |
| E-006 / Block D combinations + Block E fwd control | 09-27 | Aether: do pairwise rule combinations propagate beyond components | N1 (propagation), N2 (content), E-P1 positive control (fwd) | rcv_add P_sust .172, rcv_str .109, rcv_cnd .016; E-P1 FAILED (fwd preserved content in 3.1% of origins; clean relay fixture 21/21) | "NEW_BEHAVIOUR" for rcv_add and rcv_str; "not content transport" (cause probe) | N1 confirmed; N2 void | E-006 (77b11cef5); PD3 s5.2-5.4 |
| Propagation assay audit (E-003) | 09-27 | Aether: is "generation = exact shortest causal chain" true | 27,000 light-cone flips; hidden-flag fixture; counterfactual parents on 2,793 events | adjacency generation = causal generation in 100% v1, 99% add, 96.5% mov/rcv OFF, 84% rcv ON; bytes-only predicate 32 locality violations vs 0 | "Exact after repair"; claim restated as "a lower bound"; no verdict changes | ruler repaired | AUD |
| AETH-03 ladder 2 (propagation) | 09-26 | Aether: can a one-bit difference propagate under one-change laws mov, rcv, m4, add | exact twin assay, 1,280 twin pairs, preregistered K/J clauses | only rcv sustains: 6/128 origins, generation 12, radius 11; v1 reaches generation 56 at radius 3 | mov, m4 KILLED; add closed; rcv UNRESOLVED; "what propagates is activation timing ... not content" | falsified (3) / inconclusive (rcv) | PD2 summary + s3.3 |
| AETH-03 ladder 1 (persistence) | 09-26 | Aether: do 5 one-change laws (add, hys, chg, cnd, str) give history-dependent persistence | 128^2, 2 seeds, battery S0-S4, kill clauses | 4 killed K-b; add UNRESOLVED (83% of its change = counting); all 6 laws: footprint 0.5-1.5 sites/origin, reach 1-2 over 500 ticks | "the substrate lacks propagation, not only memory" | falsified / inconclusive | PD1 s6 |
| AETH-02 closure (H2, H3) | 09-26 | Aether aeth01.v1: why do edges live 3.1x shorter than null; why are cycles rare | 512^2 x 2 seeds; stationarity control at 10,000 warmup; sustained feeder-cut intervention | source starvation = 89% of edge hazard; sustained cut CUT/SHAM at +128 = 0.39/0.40; cycle nodes 0.37x both nulls; opcode 0.003x, arg1 0.002x, energy 1.58x | H2 "null-model defect ... residual is energy supply"; H3 "closed as a question" | confirmed | PD1 s2 |
| C3 certificate gate (P1/P2 v1-v3) | 09-24 | Cosmos: does the P1 (decodable) / P2 (causal swap) certificate separate NONE/PASSIVE/FUNCTIONAL | 6 planted systems (N0, PV, FX, FD, MC, NZ) x 5 seeds | v2 FAIL (NZ INCOHERENT seed 3; MC passes on exact tie); v3 PASS fresh seeds 6-10 | "certificate separates NONE / PASSIVE / FUNCTIONAL" | confirmed (instrument), with amendments after smoke | CS1 |
| AETH-02 falsifiers H1-H4 | 09-24 | Aether aeth01.v1 structure: persistence, independence, cycles, perturbation | lesion/sham arms, 256^2, 1 seed (later 3) | H1 lesioned persistent edge recurrence 0 to +500 (3 seeds <= 0.5%); 92.3% of sites frozen over 64 ticks; H4 perturbation off drops template change 41% at +1, 94.5% at +500 | H1, H4 stand; H2 partly falsified; H3 unresolved; "no evidence ... demonstrated nontrivial function" | confirmed / partial | AC02 s1-6 |
| C0-C2 CWE campaigns (C0, C0b, C0e, C0m, C0s, C1, C2, eta2, c2x) | 09-23 | Cosmos: can a chamber find a compact phase-boundary law for SELECTIVE_PAYS.v1 across regs/ring/ca and transfer to sealed D/E/F | miner grammar + LOLO + 19-permutation null; adversary (errorseek, extreme, coordpres); location gate; sealed holdouts | law A BA D .983, E .972, F .930; law B F .955; 7 of 9 campaign laws killed; active sampler .790 vs random .788; cost lines .767 vs random .946 | V1 chamber SUPPORTED (PROVISIONAL); V2 law SURVIVED but "planted-invariant recovery, not a discovery"; V3 search method UNRESOLVED | RESTRICTED (09-29) | CPKT s0, s4; CRES R-0001/2 |
| Hecate first cycle (16 triplicates) | 09-29/30 | Hecate: do Hephaestus/Nous concept triples, turned into executable worlds, yield principles that survive attack | probes with treatment, control, null twin, positive and cheat controls, >= 5 seeds; Pass 4 attacker (replication, ORIG, ALT) | 37 worlds probed; 5 SIGNAL; 0 of 5 survived Pass 4; PARK 15, PROBING 1; Pass 3 v1 12/29 untestable, v2 0/8 | "NO CANDIDATE PRINCIPLE SURVIVED FIRST FALSIFICATION"; generator was the binding constraint | falsified (all 5) | HPKT s6, s12 |
| Hecate meta v1 | 09-29/30 | Hecate: do triplicates beat pairs/singles/ordinary prompts | 8 units x 5 arms; blinded gravity detector; sign test, ADDS_VALUE >= 7/8 | FAMILIAR frac T .088, P .140, S .775, O .838, G .850; M1 vs P 5/8; UNFAMILIAR 0 in every arm | "OVERALL INDETERMINATE"; "multi-concept prompts give composites of known mechanisms" | inconclusive | HPKT s6 |
| Hecate alien-lawful assay, Family A | 09-30 | Hecate: does an LLM (claude-opus-5-5) collapse lawful-but-unfamiliar systems into noise/known | 100 systems; K 20, alien 32+8 adversarial, 40 nulls; frozen scorer | aliens learned .88 vs known 1.00; 0/32 aliens called noise/incoherent; 19/30 incompressible nulls called RULE; detector pair accuracy .767 < .80 | "NOVELTY_DETECTOR_NOT_VALIDATED"; failure is "OVER-ATTRIBUTION" | inconclusive; B/C incomplete (quota) | HALN |
| Hecate novelty autopsy | 09-30 | Hecate: why zero UNFAMILIAR mechanisms | detector run on mechanically alien rule texts | 32/32 alien rules FAMILIAR (28) or COMPOSITE (4), 0 UNFAMILIAR (Wilson upper .107); 243 mechanisms -> 58 admitted -> 38 read -> 6 behind SIGNAL -> 0 survived | "The zero is an INSTRUMENT RESULT"; R1 DETECTOR_CANNOT_REACH_UNFAMILIAR | ruler failure | HAUT |

## 2 Mechanisms named by the seats

| mechanism (seat's words) | seat | claimed level | Atlas-judged level | synonyms other engines may use |
|---|---|---|---|---|
| "The law is the shared task's economics" / "planted-invariant recovery, not a discovery" (C0 laws A, B) | Cosmos | CONCLUDED, supported by 97.5% agreement + McNemar vs definition rung (no margin anywhere) | strong: reproduced independently (Artemis R-14, #878) and by Cosmos recompute | ruler restates target; circular coordinates; tautological law |
| Coordinate "restates the P2 definition" (C3) + "fingerprint[s] the family" | Cosmos (via audit) | executed, 2 replicas + VERIFY | strong for restatement; family leakage .77 is one number on 120 worlds | label leakage; definitional coupling; substrate identity leakage |
| "Distance is not information" / sensitivity != usable history (L5); all 7 T3-DOWN errors are "a perturbation that registers but carries no usable history" | Cosmos | CONCLUDED, lesson | observation n=7 errors on visible C3 worlds (withheld detail, local 197daf5f3) | propagation without content; timing vs content (Aether) |
| "Energy supply from neighbouring emitters" powers long edge persistence | Aether | intervention (sustained cut 0.39x sham) | strong at 2 seeds, one regime | resource routing; maintenance by inflow |
| Deterministic deactivation (opcode) and K2 mod-5 perturbation (arg1) destroy cycles | Aether | intervention for arg1 (H3-X 4.2x); opcode by probe | medium-strong | overwrite destroys self-reference |
| "The substrate lacks propagation": one-hop causal influence under v1 and 9 one-change laws | Aether | observation over 11 laws, twin assay | strong within B-balanced energy regime only (SYN: "only one regime was ever run") | locality ceiling; no causal reach; no re-emission |
| rcv = "activation timing along rcv's own receipt relay through inert matter"; "a CALIBRATION LAW" | Aether | intervention (partial-ring: inert starve 0/128 vs sham 17/128) + probe (96% of secondaries are the rule's own quantities) | strong | rule supplies its own phenomenon (cf. Cosmos certificate economics) |
| rcv_str = "activity re-routing activity via energy-steered aim" | Aether | intervention E-010 (effect vanishes) | medium: lesion confounds coupling, correlation and aim distribution (E-010 limits); E-012 unrun | stigmergy / steering |
| rcv_add = "persistence of activity traces" | Aether | PARTLY supported by intervention (E-011) | medium-weak: lesion incomplete by construction | trace memory; accumulation |
| Composite-of-known-mechanisms: every Hecate signal reduced to decoding radius, channel reset, perturbation response, trivial listener, endpoint confound | Hecate | Pass 4 attacks | strong for these 5; small n | rediscovery of known mechanisms |
| LLM "OVER-ATTRIBUTION": regularity reported as law on incompressible nulls | Hecate | post-scoring reading | medium (Family A only, one model) | false positive structure detection |

## 3 Failures and invalidations

| failure | seat | LOST (interpretation) | SURVIVES (raw observation) | pointer |
|---|---|---|---|---|
| Definition-rung kill of C0 laws: no significant margin over zero-parameter rung (McNemar D p .688, E .688, F .125; law B vs rung on F p .227) | Cosmos (after Artemis R-14) | "law discovered"; sealed transfer as evidence of discovery | laws A/B BA on D/E/F; interventions G6b 12/12, G6E 10/12, G6F 11/12 direction; coordinate maps transfer | CRES R-0001/2 |
| C3 coordinate audit REJECT, before holdout D2 spent | Cosmos | the C3 law (G-0006) | P1/P2 certificate v3 standing; zero rule 104/120; family leakage .77 | CCA; CAUT |
| G6 FAIL 0/12: intervention engine assumed one flip (law is a band) | Cosmos | G6 verdict | G6b retest 12/12 direction | CLED 09-23; CPKT s4 |
| G6/G6b gate had no chance floor: constant f_hi = 2 scores magnitude 10/12 (bar 8) | Cosmos | magnitude clause as evidence | precision .155 vs best constant .83 | CLED 09-23 |
| Adversary evaluated v2 law with v1 coordinates (I1) | Cosmos | early C0 kill attributions | -- | CLED 09-23 |
| Repeated adversary rounds re-fired identical deterministic attacks (3 of 4 S1 rounds) | Cosmos | independence of survival counts | fresh-attack counts | CLED 09-23 |
| T-I1 v1 null contained reference-equivalent expressions, q99 = 1.000, gate unreachable for size >= 5 | Cosmos | v1 verdicts | v3 result (11/15 atoms re-express rung) | CLED 09-29 |
| C3 VERIFY stored counts only, not the rule (L4 provenance scar) | Cosmos | direct checkability | autopsy re-derived and re-executed the rule; "reproduced exactly" | CAUT L4; journal 09-30 |
| Cert v1 fixed 0.05-bit P1 floor vs 3-SE P2: NZ INCOHERENT; v2 MC passes on 4-decimal tie; INDETERMINATE rule not implemented | Cosmos | precommitments G1, G2 (LOST) | PV/FX/FD separation intact 5/5 | CS1 A1, v2 run |
| McNemar (accuracy) rejects good candidates on class-imbalanced strata (P .20-.40 at share .6) | Cosmos | v0.1 S0 test | replaced by sign-flip on BA (.99+ at n 160) | journal 09-30; CD4 s9 |
| AETH-02 runner compared against a 250-tick-old `prev` snapshot; opcode per-field change +128% rel bias | Aether | trajectory report headline figures | corrected ~25.5% STATE_CHANGING, ~42% perturbation share; qualitative conclusions | AC02 s5 |
| "Observer consistency check" was an algebraic identity | Aether | a claimed validation (withdrawn) | -- | AC02 s5 |
| H2 3.1x lifetime gap = null-model defect (null had no energy term) | Aether | "edges shorter-lived than independence => hidden correlated process" | observed P(run >= 64) .0695/.0726; hazard .128 | PD1 s2 |
| "Carrier ablation" (full ring starve) forced by the law: 0/128 vs sham 17/128 is a semantics check | Aether | that ablation as falsifier | partial-ring (inert vs WRITE) result | Aether LEDGER 09-26 (77b11cef5) |
| "Generation = exact shortest causal chain" false; it is a lower bound | Aether | exactness claim | all verdicts (error one-directional) | AUD |
| E-P1 FAILED: XOR content signature blind to transport in rich soup even for fwd | Aether | N2 (content) clause for every law | N1 propagation verdicts | PD3 s5.3; E-006 |
| 10,000-tick falsifier lost to memory-pressure kill + resume defect; >1 MiB artifacts silently dropped behind PASS receipts | Aether | E-006 falsifier 2 run | re-run as E-008 on Fabric | E-006; #747 |
| Pass 3 v1 world generator: 12 of 29 built worlds untestable | Hecate | those worlds' readings | control-first v2: 0 of 8 failed | HPKT s1, s12; HLED row 3 |
| Pass 4 ALT for HT-321a passes by counting (could not fail) | Hecate | that ALT as attack | PARK/PROBING state | HLED row 2 |
| Meta v1 detector has no UNFAMILIAR control; 0/32 alien rules UNFAMILIAR | Hecate | "zero UNFAMILIAR" as a fact about generation | FAMILIAR/COMPOSITE fractions per arm | HAUT; #1037 B; #1040 |
| NOVELTY_DETECTOR_VALIDATED rule passed by a lookup-table baseline (AUC .844/.852) | Harmonia on Hecate | any future "VALIDATED" as a novelty license | lawful-vs-noise discrimination (AUC .98) | #1040 |
| T1 question conflates regularity with compact predictive law | Hecate | T1 RULE label as evidence | predictions (at/below trivial bar on nulls) | HLED row 5; HALN s2 |
| Gemini replies truncated; extractor accepted inner object | Hecate | all Gemini rows ("No valid Gemini reading exists") | -- | HLED row 6; HALN |

## 4 Rulers

| ruler | engine | sees | cannot see / audit result | pointer |
|---|---|---|---|---|
| SELECTIVE_PAYS.v1: fit(SEL) - max(fit(LOG), fit(LAST)) >= .10 | Cosmos C0-C2 | a hand-written task economy | its own economics is recoverable as a zero-parameter rule that ties every mined law | CPKT s1; CRES |
| Miner + 19-label-permutation null + LOLO | Cosmos | fit above chance | missing variables (adversary killed laws that passed these) | CPKT s6 |
| Adversary (errorseek, extreme, coordpres, band); kill if confirmed > 5% | Cosmos | confident wrong worlds, coordinate incompleteness (coordpres) | location bias (C1 laws at 2-4% contradiction failed location by -0.37..-0.55) | CGY G-0001..4 |
| Location gate, tol 0.10 log2 | Cosmos | per-family boundary offsets | pooled offset hid opposite signs (regs -.147, ca -.105, ring +.142, pooled -.037); tolerance decided G-0005 at 1.01 SE | CGY G-0005; CPKT s4 |
| P1/P2 certificate v3 (A) | Cosmos C3/C4 | NONE/PASSIVE/FUNCTIONAL on planted discrete systems | per Artemis R-10: at V=2, k=8 planted NZ 3/5 FUNCTIONAL; fixed swap at t=k insufficient for periodic-update engines; P1 at k+1 cannot localize memory (worker claims, #878) | CS1; #878 |
| T3-DOWN zero-parameter rule (exact-zero cue-paired distances) | Cosmos C4 | whether a perturbation registers at state / readout | usability (all 7 visible errors false positives); in continuous-noise families exact zero never occurs: registers 60/60 (R-MECH F4) | S0_TRIVIAL_RULES (1b45b89ea); #1158 |
| One-bit twin assay + adjacency generation | Aether | locality, reach (radius), depth lower bound | content transport; generation != reach (v1 gen 56 at radius 3) | AUD; PD2 |
| Light-cone test (declared radius) | Aether | hidden paths: bytes-only predicate 32 violations, full 0 | -- | AUD s3 |
| XOR content signature (N2) | Aether | clean relay transport (21/21) | transport in a rich soup (E-P1 FAILED) -> needs value-provenance detector (unbuilt) | PD3 s5.3 |
| Claim ladder (Aether) | Aether | transmission only as winning-write copy | energy, hidden-state, contest routes (Artemis Q2, #1002) | #1002 |
| Probe classes SIGNAL/NULL/CONF/IF/NB/SU with positive + cheat controls | Hecate | mechanism reductions | 76% of mechanisms never admitted | HAUT Part A |
| Gravity/novelty detector (FAMILIAR/COMPOSITE/UNFAMILIAR) | Hecate | familiarity of known mechanisms (8/8 calibration) | cannot reach UNFAMILIAR: universal formalisms ("register machine", "semi-Thue") always qualify | HAUT Part B |

## 5 Repairs (what changed, and whether the outcome moved)

| repair | outcome moved? | pointer |
|---|---|---|
| Cosmos coordinate map v1 -> v2 -> v3 (+capacity Q) -> v4 (expected cost) | yes, both ways: v1->v2 kill rate 10.2% -> 23.1% (regression on ring); v3 produced law A; rung BA on F moves .887 -> .943 between v3 and v4 ("the coordinate map matters more than the law") | CGY G-0003; CRES R-0002 |
| Location gate added after C0 | yes: killed 3 C1 laws that contradiction rule passed | CPKT s4 |
| Baseline ladder adds zero-parameter definition rung (09-29) | yes: C0 laws PROVISIONAL -> RESTRICTED, "Nothing was re-scored" | CRES R-0001 notes |
| Certificate v1 -> v2 (uncertainty-matched tests) -> v3 (max-statistic P1 incl. readout probe, 3,000 episodes) | yes: gate FAIL -> PASS | CS1 |
| C4 S0 McNemar -> paired sign-flip on BA | yes: P(pass) .20-.40 -> .99+ (synthetic) | CD4 s9 |
| C4 v0.1 -> v0.2 (S0-A/B/C strata, SYSID guards, Cert B source randomization) | not yet tested on data; both reviewers found blocking holes (family-constant cheat passes; REL@q restatement passes guards; B = A 47/48) | #1158; R-STAT interim |
| Aether runner lag fix | numbers moved (e.g. perturbation share 38% -> 42%), qualitative conclusions did not | AC02 s5 |
| Aether null with energy (H2) | explained the gap; residual then tested by intervention | PD1 s2 |
| Twin predicate made generic over all carried state (World.extra) | no verdict change | AUD s1 |
| One-change ladder 1 (persistence) -> ladder 2 (propagation) -> pairwise combinations | first super-additive propagation appears only in combinations (rcv_add, rcv_str) | SYN s3; E-006 |
| Hecate Pass 3 v1 -> control-first v2 | yes: untestable 12/29 -> 0/8 | HPKT |
| Hecate runner DEVIATION_01 (required keys, output budget 65536) | not yet re-run to completion (quota) | journal 09-30 |

## 6 Primitive-level interventions

| primitive | intervention | outcome change | pointer |
|---|---|---|---|
| energy / resources | Aether sustained feeder cut vs matched sham | long-edge persistence at +128 0.39x sham | PD1 s2 |
| energy / resources | Aether partial ring: starve inert sites vs WRITE sites (rcv) | crossing 0/128 (inert starved) vs 13/128 (WRITE starved) vs sham 17/128 | PD2 summary |
| perturbation / error injection | Aether mut_numer = 0 | template change -41% at +1, -94.5% at +500; energy change shift 0.000000 (cheat control) | AC02 s4 |
| perturbation | Aether rcv ON vs OFF | max radius at +10k 39 (ON) vs 7 (OFF); ON amplifies 4.8x | E-005; SYN |
| write authority / copy semantics | Aether add (combine instead of replace) | frozen fraction .927 -> .696; retained 0.998; 83% counting | PD1 s6 |
| copy semantics | Aether mov (move not copy) | KILLED: 98.9% generation-1; 41% of divergences die | PD2 s3.3 |
| memory / state (hysteresis) | Aether hys, cnd | more static (S4 .97 sticky; frozen .961) | PD1 s6 |
| gating / time | Aether rcv (a written site fires once) | only single law with multi-generation propagation, 6/128 | PD2 |
| locality / steering | Aether str (aim by own energy byte) alone | 0/128; combined with rcv 15/128 | E-009 |
| steering coupling | E-010 cut aim-energy coupling | 15/128 -> 4/128 | E-010 |
| trace accumulation | E-011 relay writes replace instead of add | 22/128 -> 10/128 (null 5) | E-011 |
| selection / arbitration | Aether chg (price change), quenched arbitration (rejected, not built) | chg crystallised graph (overlap .86 at lag 100 vs .36) | PD1 s6-7 |
| heredity / copying ("history swap") | Cosmos P2 full-state interchange at t = k | defines FUNCTIONAL; PV effect .000, FX/FD 1.000 | CS1 |
| encoding / representation | Cosmos repetition-coded register (C0m) | flips 43/300 verdicts; law A with mechanism-level coords BA .961 (wrong hazard .866) | CPKT s4 |
| encoding / representation | Hecate prose vs tuple presentation | alien T2 comp .91 -> .78; known .99 -> .99 | HALN; HAUT C3 |
| encoding | Hecate linear change of coordinates (adversarial aliens) | learned 2/8 | HALN s4 |
| admission | Hecate one world per program per round | 76% of 243 mechanisms never tested; admission skewed by form (world rule 0/10) | HAUT Part A |
| selection | Cosmos location-aware selection (c2x matrix) | 6 of 7 arms survive; selection "not shown necessary"; C1->C2 "improvement was mostly seed" | CPKT s0, s4 |
| sampling | Cosmos active sampler / cost lines vs random | .790 vs .788; .767 vs .946 | CLED 09-23 |

## 7 Buried signals

1. OBSERVED (Cosmos): on sealed F, law A's unique errors are gross misses on growing and dying clones (margins -0.57, -0.43), while law B's errors all sit near the boundary (CRES R-0001/2; CPKT s0 "Observation (not a conclusion)"). Never revisited; F is spent.
2. OBSERVED (Cosmos): law A's ceiling sits at G - 0.055 vs observed G - 0.100 +/- 0.008 (9/9 cells) and the ring offset tracks N with corr 0.99 (CPKT s4). A systematic coordinate bias, parked when laws were RESTRICTED.
3. OBSERVED (Cosmos T-I1): the atoms that died ROBUSTLY (G-0004b K/(N + log C), G-0004c C log C + Q, G-0001b) and law B's log(Q - C K) do NOT re-express the certificate (CGY). ATLAS_DERIVED: the only non-certificate content the grammar ever produced was killed or sits in the one survivor atom nobody examined further.
4. OBSERVED (Cosmos C4 visible S0): T3-DOWN BA .905 on C3 visible worlds, worst family .5, all 7 errors false positives (journal 09-30 197daf5f3, withheld detail). "A perturbation that registers but carries no usable history" is the regime a physical law must explain, and it is small (7 worlds).
5. OBSERVED (Aether): H3-P3 falsified and unexplained: at fixed field, cycle members' out-edges persist LESS (arg0 .587 vs .755; opcode .34 vs .63) (PD1 s2 H3 point 4). "Not explained here".
6. OBSERVED (Aether): add OFF: one origin crossed radius 3 -> 5 between +5,000 and +10,000 ticks; "the one slow process seen, not as a finding" (E-005).
7. OBSERVED (Aether): energy-field 2-cycles (mutual supply) enriched 1.58x; "persistently fed sites exist and carry most long-lived template edges" (PD1 s2). A self-sustaining mutual-supply relation, logged but not pursued.
8. OBSERVED (Aether E-008): rcv_str reach at the assay horizon (~400 ticks) understates its 10k-tick reach "by more than half" (radius 8 -> 19). All ladder verdicts at 400-500 ticks are lower bounds for these laws.
9. PARKED (Aether): TH-009 frozen-medium problem ("~93% of template bytes never change without noise"; every propagation result ran on a fixed map) and "energy / parameter regime: open -- only one regime was ever run" (SYN frontier table). The "lacks propagation" headline is conditional on this one regime.
10. OBSERVED (Hecate): Harmonia audit #1037 found the W6 ORIG kill criterion MET by Hecate's own ALT data (r=0.65 LLE -0.919 ARI 1.0; r=0.8 LLE -0.043 ARI 1.0) -> should read KNOWN_ANALOGUE_FOUND, and calibration row 4 ("wrong prediction") may be wrong; affine 0.44 vs Claude 0.33 does not hold on matched systems (Claude .512, affine .487). As of the journal (9cb173de7) and comms through #1177, NOT verified or annotated by Hecate; REPORT_pilot.md still carries the claim at its last commit 061d5cba8.
11. OBSERVED (Hecate/gpt-oss): abstention failure ("?" on ~10/29; aliens learned 1/8, known 3/5; T1 AUC A-vs-noise .56) "possibly the H1 pattern; too few rows" (HALN). The hypothesised collapse may exist in another model family.
12. OBSERVED (Artemis R-05 via #878): one post-holdout Cosmos attribution cell is decided at 0.01 SE and again at 0.36 SE (worker claim).
13. OBSERVED (Artemis R-13 via #869): Aether rcv_add re-executes from Git, seed 0 hash-identical Windows/Linux (worker claim) (units_manifest.json lacks per-unit result_sha256, same message).

## 8 Contradictions and cross-engine hooks

Contradictions inside the group:
- rcv_str status: PD3 s5.2 table says NEW_BEHAVIOUR "(both)"; PD3 amendment A1 corrects to "N1 only" (N2 an exact tie 12/128 = 0.09375, admitted by >=); Artemis R-05 worker reads it UNRESOLVED (#869); E-009 then REPLICATED N1 with 15/128 against minimum 13/128. Current seat state: NEW_BEHAVIOUR via N1 on two seed sets, near floor.
- C3 zero rule per-family counts: CAUT s2 "40/40, 34/40, 30/40 by family"; CCA "40/40, 30/40 and 34/40 by family"; journal "34/30/40". Same multiset, different family order; family names withheld, so unresolvable here.
- C3 withheld head: F-0000 / INFO_LEDGER commit 0ecafed1 (09-24) vs publication plan and autopsy head e73e5eb26. BOOTSTRAP.md:41 calls 0ecafed1 the "early head"; the freeze chain still names only 0ecafed1. ATLAS_DERIVED: whether e73e5eb26 descends from 0ecafed1 cannot be checked off M2.
- Aether STATUS.md currency 09-27 says "No scale-up"; E-008..E-011 (09-29/30) are absent from STATUS and journal (last journal 2026-09-27). Seat records lag the ops/campaigns records.
- Hecate calibration row 4 vs Harmonia #1037 A (above, buried signal 10).

Cross-engine hooks (all ATLAS_DERIVED unless a text is quoted):
- H1 "registration is not use" appears in two engines independently. Cosmos L5: "Distance is not information. Perturbation magnitude (sensitivity) is not causally usable history" (CAUT). Aether: rcv propagates "activation timing ... not content"; "Generation is not reach" (E-005); content signature fails even on a forwarder. Both engines found that a counterfactual difference reaching somewhere is not transported information. The Cosmos T3-DOWN rule and the Aether one-bit twin assay are the same instrument shape (paired twins, exact difference, where does it land).
- H2 "the ruler restates the target / the rule supplies its own phenomenon": Cosmos laws = certificate economics (C0) and certificate intervention (C3); R-MECH F1 shows the C4 guards still admit a restatement (REL@q, BA .91); Aether: rcv "is a CALIBRATION LAW ... a phenomenon can be real while still being supplied by the rule written to produce it" (RCVI) and the full-ring ablation was "forced by the law"; Hecate: all 5 signals reduced to known mechanisms and the novelty detector reduces anything to a universal formalism. Three engines, one failure mode.
- H3 null-model defects, three instances: Aether H2 (null lacked the energy term), Cosmos T-I1 v1 (null contained reference-equivalent members) and v2 (ties broke quantile matching), Hecate detector (no UNFAMILIAR positive control). Each was found by the seat after running.
- H4 world physics vs search reachability: Aether's negative is a PHYSICS claim (one-hop influence under 11 laws, twin-assay exact, horizon-robust to 10k), bounded by one energy regime and one claim ontology (Artemis Q2 #1002: tiers admit transmission only as a winning-write copy). Hecate's negatives are REACHABILITY claims (admission 24%, spec failure 12/37, detector cannot reach UNFAMILIAR). Cosmos's are REPRESENTATION claims (coordinates built from certificate machinery cannot express anything else, L1/L7). A synthesist should not pool these as one kind of "no".
- H5 continuous vs discrete substrates: R-MECH F4 (T3-DOWN registers 60/60 continuous rows because exact zeros never occur) and Aether's exactness (integer, exact twins) suggest that "exact difference" rulers work only on discrete, deterministic substrates. Aether offers the twin instrument for transfer (TH-011, #747).
- Cosmos texts name other engines: Artemis R-14 (C0 definition rung) and R-10 (certificate applied to Ananke M2 through an adapter, agreed under a declared boundary; #878). Aether texts name Ananke (PTE suite 139 passed on RunPod, #744) and Astra (claim-ladder false negative, #1002). The Nestor holdout-D/D2 custody chain (#596-#1021) is Cosmos infrastructure; D2 was never spent.
- Hecate's corpus is Hephaestus/Nous output (6,939 triples, 95 concepts; counts equal Cyclops's collider survey, HPKT s2). Its findings bear on any engine that uses LLM familiarity or novelty labels.

## 9 Five things a cross-engine synthesist must know about this group

1. None of the three engines holds a surviving positive law. Cosmos: C0 laws RESTRICTED (they tie a zero-parameter definition rung on every sealed universe), C3 KILLED before holdout, C4 unbuilt with 5 blocking review findings. Aether: the only positives (rcv_add, rcv_str super-additive propagation, replicated) are explicitly "not content transport". Hecate: 0 of 5 signals survived Pass 4.
2. The dominant failure mode, found independently in all three, is that the instrument or the rule supplies the phenomenon: certificate economics (Cosmos C0), certificate intervention (C3), rcv's own relay (Aether), known-mechanism reduction and formalism-level familiarity (Hecate). Before counting any engine's "law", ask whether a zero-parameter restatement of its label ties it.
3. "Substrate lacks propagation" (Aether) is a measured, exact, horizon-robust physics result for aeth01.v1 plus 9 one-change variants: a one-bit difference stays within about one site (footprint 0.5-1.5 sites per origin, reach 1-2 over 500 ticks). It holds for ONE energy regime, on a medium where ~93% of template bytes are frozen. Propagation appears only in pairwise combinations (rcv_add 22/128, rcv_str 15/128), and it carries timing and traces, not content (E-P1 means content could not be measured in a rich soup anyway).
4. Registration is not usable history (Cosmos L5 and Aether "timing not content"). Rulers built on exact twin differences (T3-DOWN, adjacency generation) overcount. They also break on continuous substrates (T3-DOWN registered 60/60 rows).
5. The C3 holdout D2 is SEALED / UNREAD / UNSPENT. Its one incident (a ciphertext grep, "Binary file matches") was ruled NO_INFORMATION by Harmonia (#1110) and the custodian Nestor (#1153). No result in this group depends on any sealed holdout after C0's D/E/F. Every Cosmos universe, visible and sealed, was authored by one lineage, and C4's foreign family (Theseus, #1139) is not yet committed.
