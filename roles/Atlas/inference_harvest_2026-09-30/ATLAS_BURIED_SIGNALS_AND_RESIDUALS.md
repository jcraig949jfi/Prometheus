# ATLAS_BURIED_SIGNALS_AND_RESIDUALS -- observations worth more than their headlines

Atlas[m1-a5680f90], inference harvest 2026-09-30. Read-only toward every seat. Operator-facing.

## How to read this file
- Every entry keeps the **OBSERVATION** (OBSERVED, with numbers and a pointer) separate from the
  **INTERPRETATION THAT BURIED IT** (a failed, weakened or never-drawn reading). The observation stands
  even when the interpretation is dead.
- **Why it matters** is ATLAS_DERIVED: a hypothesis about what the observation could be evidence FOR,
  especially across engines.
- **Tyche** records whether the entry is already in Tyche's natural residual catalogue
  (tyche/residuals/v0_1/CATALOGUE_v0.jsonl, 122 entries, read 2026-09-30), and whether it meets the
  catalogue's admission shape. That shape is: exact quote at a pinned sha; committed raw rows; observation
  separable from interpretation; perturbable only with a world form plus a structure-destroyed twin.
  NEW = not found in the catalogue by phenomenon text. Atlas does not add to Tyche's catalogue; this column
  is for Tyche and the operator. The catalogue is gated shut until Tyche's gate 6 passes (Tyche
  WORK_STATE; roles/Tyche/REVIEW_PACKET_v1 @6a28fc49e).
- Pointer shorthand follows the seven digests (INFERENCE_HARVEST_HANDOFF.md s3). NF = roles/Nestor/FINDINGS.md
  @19ef51610; "#n" = comms message id.

Ranking: A-entries are the strongest candidates. They combine a clean observation, a cross-engine hook, and a
cheap revisit.

---------------------------------------------------------------------------------------------------------
## A. Strongest buried signals (top 12)

| # | OBSERVATION (OBSERVED, pointer) | what buried it | why it matters (ATLAS_DERIVED) | Tyche | smallest revisit |
|---|---|---|---|---|---|
| A1 | **Carried registers kill zero-dependent founder lineages in BEE: 0/24 persist (ZERO 10/24; p=.9 5/12).** roles/Bellerophon/.../repl_2026-09-30/PREREG.md s3 D2 | Used only to justify a design deviation (P90/P75 arms) in REPL-01 | The same direction as NPE's fresh-state rescue (0.33 -> 0.81, C-STATELESS-FFA6; ZERO 26/48 vs carried 6/48, C-ZERO-SPECIFIC) in a second codebase with a different ruler (survival vs P-11 runaway). It is the best cross-engine support for an "initialization regime" primitive. Caveat: NPE and BEE share the Z80 ISA | NEW | Re-run pilot 2 with n = 48/arm and the ZERO / CONST / RANDOM / CARRIED arms matched to NPE C-ZERO-SPECIFIC. Only ZERO should rescue if the NPE mechanism transfers |
| A2 | **Transplanted lineages keep copying but keep NO task competence: persistence 39/39, self-replication 27/27, competence 0/39.** archaeon/z80atlas/postcampaign/..._ADJUDICATION s C @18772241e | Filed as "not a de-novo result, not a competence-transport result" | A clean dissociation of heredity-of-copying from heredity-of-function. It matches BEE (endogenous reproduction antagonises task code: 178 vs 2) and the NPE scope limit (the pressure effect is EXTERNAL-only; X-TASK-GATE was never executed). No engine has yet shown task competence riding on its own replication | NEW (R-A029 covers only the BEE antagonism) | X-TASK-GATE is frozen and unexecuted (roles/Nestor/.../x_task_gate/PREREG.md @62d30e443); it would test this in NPE. Needs an Aporia dispatch; Atlas only points at it |
| A3 | **At equal compute (60,000 evals), EVERY population size N 50-400 climbs above the best starting parent (.382 -> max .479-.562).** archaeon/frontier/digests/DIGEST_2026-09-21T2054Z @939e4f39e; DECISIONS DF-012 | Left PROVISIONAL (the digest lists it only as a provisional mystery; "every N climbs" is ATLAS's reading, and the seed-2 runs start at .396, above .382). C5's operator-accepted "selection ... does not climb these worlds at all" was never revisited (C5 arms had 9,000-36,000 evals) | A Campaign-level negative ("flat elite") is plausibly a compute or population artefact. The same shape recurs: PROTEUS-46 greedy vs neutral path; PTE plants beat champions (.999 vs .755); Tyche 2/72 adaptations. Search reachability read as landscape | NEW (R-A006/R-A065 cover P-boom only) | Re-read the C5-02 worlds at 60k evals for N = 50 and 200, 8 seeds each. Cheap, and Archaeon-owned |
| A4 | **A 5-edit duplicate-and-diverge path crosses the PROTEUS-46 "cliff": 4 NEUTRAL steps (3/6), then 6/6 (a worker quick-mode result, D002-03q; population search never reached 6/6).** #1116; roles/Artemis/dispatch/D002/RESULT.md @ae043e65f | PROTEUS-46 closed as CLIFF_SURVIVES / FALSIFIER_FAILED. Its greedy walk cannot accept a neutral child (falsifier_46.py:117-131). The FULL D002-03 run (500 x 3000) timed out | The suppression that generated 299,991 enforcement echoes rests on a search that could not see neutral paths. The frontier's C4-cliff.T1 remains BLOCKED on it | NEW | Run the neutral-accepting walk to completion (50 walks x 300 steps). If crossing rates exceed the frozen threshold, the suppression's premise changes. The decision is Proteus/Archaeon's |
| A5 | **One spontaneous SELF-free donor (n = 1) in X-DONOR-DISCOVERY turned out to be the dominant architecture: 95.7% of competent donors in the P2 corpus.** W1_REPORT s1 @d63b76a5f; SYNTHESIS P2 s4 @948b3a45f | NOT buried by the seat (verifier correction): W1 itself called the L1 ruler (SELF+LDIR) too narrow, issued a ruler correction and scheduled the SELF-free class. Listed as a calibration specimen, not a buried signal | The n = 1 observation was right and the ruler was wrong, and the seat caught it. It is the program's cleanest known-answer example of "keep the anomaly, distrust the ruler" | NEW | none needed (resolved); cite it as a calibration specimen for Tyche and Harmonia |
| A6 | **NPE ARC3 (a delegate/worker result, not Deep Frontier): a neutral mutation walk reaches donor competence at about the soup's rate (pilot ratio 1.75, p = 0.20).** SYNTHESIS_ARC3 s8 @f443bcef0 | The full baseline (WP-9, about 9 CPU-h, portable) was never run. The seat says "no evidence yet that the soup helps FIRST APPEARANCE" | This is the Knierim 2026 question: is the pair soup a better search than a random walk? If the answer is no, every NPE acquisition result is a statement about search, not about ecology | NEW | WP-9 as designed (~9 CPU-h). Owner Nestor; parked |
| A7 | **A coherent living pattern crosses the ASAL garbage band: 3G3an (coherence 0.938) at 0.8122, and S2_135 GENUINE_DYNAMICAL_NOVELTY at 0.7933; 9 GENUINE among 105 crossers.** Harmonia rulings/RULING_ASAL_LEGIT_SEARCH_001 s2-s3 @2ead5e011. Caveats in the source: 3G3an's 0.8122 is annotated weak near-boundary evidence (1.1 sd); the 49/47/9 split covers only the 395 executed of 1,045 rollouts; S2_135 descends from 3G3an, so the two are not independent | Headline I3: "best crosser is a METRIC_EXPLOIT" (49/105 exploits) | The only genuine open-endedness candidates the CLIP line produced are buried under a correct but negative headline | R-A076 covers the observer only; the 9 GENUINE are NEW | Score the 9 GENUINE crossers with a non-CLIP novelty measure. Harmonia/Techne territory |
| A8 | **PTE: 80-95% of mirror pairs carry mirror-different sensor traffic to the readout at o2-o8, yet swapping it changes nothing, not even raw S0; HOLD twins differ in flight at 9/9 ticks while channel swaps leave the trace bit-identical.** roles/Ananke/research/workers/W-V, W-I | Recorded as instrument detail inside the carrier-swap arc | A USE gap, not a storage gap. The same shape appears in Cosmos (L5 "distance is not information") and Aether ("timing, not content"), but those share the twin/swap instrument class. VERIFIER CORRECTION: the CW01 cycle-8 "register predicts the regime at 1.0, never used" reading was WITHDRAWN by CW01-D089 (a trivial in-sample lookup; under a cross-set test no register predicts the regime), so it is not evidence here | NEW | Random-program baseline: the fraction of swap-effective variables in unselected programs vs evolved champions. Without it, "present != used" may be generic to the instrument |
| A9 | **Random harvested questions produce a consequential finding about 9 times in 10: 34/36 executions scored CONSEQUENTIAL.** roles/Artemis/selftest/RESULT.md s2-s3 @781c11349 | The measure saturated, so "sharpening NOT shown to add yield" | The record is defect-rich: throughput, not curation, binds. For Tyche this means residual mining should prefer volume with cheap attacks over hand-picked residuals | NEW | none (an operational fact) |
| A10 | **2,319,892 births (9% of 25,069,717 in trigger runs) were written by partner code the writer ran into, and were EXCLUDED from self-replication by the own-code (pc < L) criterion.** POST_CAMPAIGN_FORENSICS s3.1 @3efdacf7e | The criterion was later shown to be LOCATION, not material: in r038751, 27,083 of 28,163 location-foreign births are own material (#741); in r016299 only 17,501 of 38,825 are. No recount exists | An unknown share of the excluded 9% may be genuine self-replication. Every BEE SR rate in the record is a location-ruler rate | R-S002 / R-A021 cover r038751 only; the 9% exclusion is NEW | Recount SR by material on the r038751 and r016299 traces (Archaeon's causal lens already has the adapters) |
| A11 | **Only non-certificate content in the Cosmos grammar: the killed G-0004 atoms (G-0004b K/(N+log C), G-0004c C log C + Q; the source calls only G-0004 robustly killed) and law B's log(Q - C K) do NOT re-express the certificate; 11 of 15 atoms in total do. The test is labelled exploratory.** roles/Cosmos/research/GRAVEYARD.md T-I1 @60965e0a6 | C0 laws RESTRICTED as planted-invariant recovery; T-I1 concludes "the graveyard's recurring fragment is the planted economics" | If Cosmos ever mined anything not planted, it is in the atoms it killed or in the one survivor atom nobody examined | NEW | Re-evaluate log(Q - C K) alone against the definition rung on the spent sealed rows (already on disk) |
| A12 | **Aether: energy-field 2-cycles (mutual supply) are enriched 1.58x; "persistently fed sites exist and carry most long-lived template edges".** Aether/AETH-03/PHYSICS_DESIGN_01 s2 @43202cf7b | Logged as mechanism context for AETH-02 H2 (null-model defect) | A self-sustaining mutual-supply relation is the closest thing to an autocatalytic unit in any substrate indexed. It was never tested as an organization-without-inheritance candidate | NEW | Lesion one member of each 2-cycle vs a matched sham, and measure survival of the partner |

---------------------------------------------------------------------------------------------------------
## B. Heredity and reproduction residuals

| # | OBSERVATION | what buried it | why it matters | Tyche |
|---|---|---|---|---|
| B1 | 19 P-11-certified genomes are "competent constructors whose children do not carry variation forward"; 11 fail at generation 2 (#891; challenge/cvtr_nestor/RESULT.md @d050937ec) | Read as a ruler defect of P-11 | A distinct PHENOTYPE: construction without transmissible variation. No primitive names it (ontology file s1) | NEW |
| B2 | "Losing the copy instruction is a trap": 0/144 recovered; copiers sit on broad neutral networks (72-80% of 1-step mutants stay competent); partial copiers become competent in one step 22-27% of the time (NF:495; A3S s1) | Context for the carrier-exposure model | Copying sits on a wide plateau with an absorbing edge. That predicts the fixation pattern the lottery model describes | NEW |
| B3 | X-P2-PLANT: the planted copy instruction decays (carriers ~210 -> <21 per 256), yet donors arise while it is common (A3S s1) | Used only as a basis for the carrier-exposure hazard | Copy material is not selected to persist BEFORE it becomes a donor. Origin draws on a transient pool | NEW |
| B4 | 9-15% of foreign runaway populations carry genomes competent where the founder is not (X-ACQUIRE, lower bound); C-SWAP-ACQUIRE missed its frozen rule by one event (9 vs 10 needed; p 0.0018 vs bar 0.001) (NF:363-367) | Recorded as NOT CONFIRMED | Descendant ACQUISITION of competence the founder lacks. Unrefuted and one event short | NEW |
| B5 | Side asymmetry: 7ae3 copies only from tape side 1; P2 copiers are side-0-only in 1,052 of 1,154 (STATUS RESUME s3; P2S s1) | Named an open child, never run | A frame or addressing asymmetry. Compare Archaeon's input-byte gating around base 128 | NEW |
| B6 | E-003 per-class Q8c for "none" = 0.242 [0.162, 0.330], above 5%; pooling hides it (E003_SYNTHESIS s2 Q2, BRANCH:archaeon/attribution-arc-2026-09-28@9c8cfed55) | Pooled R3 statistic 0.00115 | One class of births carries a transmission defect 200x the pooled rate | NEW |
| B7 | Parasite class: 0/120 isolated-capable vs 117/120 in the self-performed class; the average (85% capable) hid it (REVIEW_7_ADJ, same branch) | Averaged away | Material and capability split totally by reproduction class | R-A022 is adjacent (context-dependent copiers); the class split is NEW |
| B8 | BEE G6: 26 unmodified initial random 64-byte tapes replicated (ERRATA E1); Artemis R-26 null 4.5e-5 per tape (#877) | Folded into the 160 -> 103 BUILT_BY_COPY correction | An unreplicated claim that random tapes self-replicate outright at a nontrivial rate. It contradicts DENOVO-01 0/80 on the vmcopy VM, a different physics | NEW |
| B9 | The only random-origin survivor of the Z80 x Atlas campaign (84616cf8257b) is an input-gated self-copier, exact only at input 121, with late fidelity 0.482: excluded by the frozen fidelity threshold (ADJUDICATION s G) | Below threshold | A real reproducer that the ruler excludes | adjacent to R-A004/R-A023 (BAND0); NEW as stated |
| B10 | REPL-01 post-hoc LCS median 2 vs random null 1; 2/18 ZERO and 1/36 P75 runs had >= 80% founder-like state-free genomes (ERRATA_REPL01 R1 @6879b2236) | "Chance-level" withdrawn; the non-parental-founder null that would decide it was never run | Weak, above-chance content continuity in BEE | NEW |
| B11 | NPE T-003 1% sample: 2,818 label-only loci (9.6% of interactions), mutation-shaped, undiagnosable because the discrepancy records omit label values (E003 addendum G) | "Uninformative by construction" | A record-format defect that hides a possible mutation-labelling bias | NEW |

---------------------------------------------------------------------------------------------------------
## C. Search, landscape and variation residuals

| # | OBSERVATION | what buried it | why it matters | Tyche |
|---|---|---|---|---|
| C1 | Exaptation gradient under neutral walks: .050 -> .082 at depths 16 -> 64 (C5-01, archaeon/campaign5 @cdb55e152) | Killed on a yield rule | Deeper neutral walks reach more exaptive neighbours: the direction A3/A4 predict | NEW |
| C2 | C5-06: insertion is "the rescued operator": 102 recoveries, 0 losses | Never followed up | Insertion is the only operator with an asymmetric rescue profile. Compare the length-by-acceptance result (P-C03) | NEW |
| C3 | GW NK line unaffected by the abstain floor: a 132-byte target-blind policy beats a fixed bitset on 64 unseen landscapes 8/8 (+3.4%); R8 NK corruption +5.5% held (MWU p .0035, post hoc) (GW/P2:242-245; R8_DISPUTES) | Graphworld closed; never revisited | The one graphworld transfer-like result that the floor audit did not kill | NEW |
| C4 | Sham beats scratch: GW R7 sham - scratch +1.400; R8 scale-only arm +2.10 [1.19, 2.98] (GW/P7:127; replay_r8/E-R8-H1.json) | Read as "negative in a useful way" for the graft | Initialization scale masquerading as transfer: the same shape as A1 and the PTE SETRULE bootstrap | NEW |
| C5 | Apollo crossover: 0/8000 single-step improving walks vs 6.1% per pair for recombinants; `crossover_frac` defaults to 0.0 (Harmonia AUDIT_20260622 stall map s3b @3e13f736c) | The prescribed flag flip was never found done | A one-line configuration change with a measured prior of benefit | R-A084 adjacent (Apollo ceiling); the crossover flag is NEW |
| C6 | Operator bundling in the code learner: split moves escape 10/10 vs 0/10 (GW/P2:252-254) | Graphworld detail | An operator_composability datum Atlas has no rule for | NEW |
| C7 | FIZZLE hidden load: .46-.80 of final population members carry executed faults, with nothing bought (C5-09) | "BOUNDARY_CREATED_NO_DISCOVERY_GAIN" | Load is carried, not purged (compare NPE P-G09: unpurged initial junk) | NEW |
| C8 | Deep Frontier graph profile: C6-blind.T1 graph runs reach max .375-.500 with almost no detector firings (DIGEST 2026-09-21) | Detectors UNABLE by design | An unobserved regime rather than an empty one | NEW |

---------------------------------------------------------------------------------------------------------
## D. Memory, state and use residuals

| # | OBSERVATION | what buried it | why it matters | Tyche |
|---|---|---|---|---|
| D1 | PTE HOLD champion 311c465f falls from 0.76 to 0.55 without distractors: it depends on distractor input (W-B l.77-78) | "Unexplained", never revisited | A needs-noise-to-work phenotype | R-S016 (already catalogued) |
| D2 | PTE M3 latency -1 IMPROVES accuracy (0.693 -> 0.741; 0.686 -> 0.715) (C1b s4) | Context for the transport reading | Evolved champions are not at their own timing optimum: search, not physics, set the latency | NEW |
| D3 | PTE: evolved RELAY SIGNAL at loss 0.6 where the hand design is 0/253; MAJ SIGNAL at decay 3 and 6 where the design is 0/755 (C1_REPORT s2) | Never followed as its own thread | Evolution works outside the designed habitable zone. This is the inverse of the "plants beat champions" pattern and deserves its own account | NEW |
| D4 | Ensorain: both declared eviction policies lose to random on the eviction positive-control world (SI EXPERIMENTS 09-26T03:48Z), vs Odysseus Y04 listing "random eviction beats declared policies" as FALSIFIED-CLAIM | Unreconciled across two seats | A live contradiction about selective forgetting | R-A042 (catalogued; the contradiction with Y04 is NEW) |
| D5 | Ensorain LM02: a mid-ramp detector beats the oracle boundary (RAMP20 5/8 vs 1/8) (INSTRUMENT_LINE_REVIEW, BRANCH:ensorain/base-role-adopt-2026-09-23@26a490702) | Parked as a WTP-04 axis | Early detection beats "knowing the true change point": data availability dominates | NEW |
| D6 | Tyche Block R: stored-any fragment share rises monotonically with world diversity (solo .045, related .079, broad .120) while adaptation did not (tyche/runs/v2_blockR/REPORT_BLOCK_R.md @4dbbc07d0) | The OV clock reads the population only and misses fused coalitions (the seat's own instrument gap) | Latent option value may be being stored and not measured | NEW |
| D7 | CW01 e07: raw retention DOUBLED under weather (0.181 -> 0.359) while the frozen ability-adjusted ratio reads NEGATIVE, because the normalizing margin is ~0.003 (CW01-D071) | Neither promoted | An ill-conditioned ratio inverted a doubling | NEW |
| D8 | CW01 e08: TAX+AMP had the highest capability (171.2) at the lowest burden (0.512); scalar burden 1.725 -> 0.834 -> 0.512 (CW e08; BR7 P-J03) | Buried under NOT_VERIFIED competence counts; "not promoted" | R-S030 shows amputation alone also lowers burden; the combination is unexplained | R-S030 adjacent; the TAX+AMP optimum is NEW |

---------------------------------------------------------------------------------------------------------
## E. Physics and law residuals

| # | OBSERVATION | what buried it | Tyche |
|---|---|---|---|
| E1 | Cosmos law A ceiling at G - 0.055 vs observed G - 0.100 +/- 0.008 (9/9 cells); the ring offset tracks N with corr 0.99 (REVIEW_PACKET_CWE s4 @af2af37f4) | Parked when the laws were RESTRICTED | NEW (a systematic coordinate bias) |
| E2 | Cosmos law A's unique errors on sealed F are gross misses on growing and dying clones (margins -0.57, -0.43); law B's errors sit near the boundary | F is spent | R-A039 (catalogued) |
| E3 | Cosmos C4 visible S0: T3-DOWN BA .905; all 7 errors are false positives, "a perturbation that registers but carries no usable history" (journal 09-30 197daf5f3, withheld detail) | Small n (7) | NEW |
| E4 | Aether H3-P3: at fixed field, cycle members' out-edges persist LESS (arg0 .587 vs .755; opcode .34 vs .63) | "Not explained here" | R-A036 (catalogued) |
| E5 | Aether add OFF: one origin crossed radius 3 -> 5 between +5,000 and +10,000 ticks, "the one slow process seen, not as a finding" (E-005 @e67dd06bc) | n = 1 | NEW |
| E6 | Aether: "only one energy regime was ever run", so "substrate lacks propagation" is conditional on it (RESEARCH_BLOCK_SYNTHESIS frontier table @77b11cef5) | Headline stated without the condition | R-A035 (rcv, one regime; catalogued); the general condition is NEW |
| E7 | Hecate: Harmonia #1037 found the W6 ORIG kill criterion MET by Hecate's own ALT data (r=0.65 LLE -0.919 ARI 1.0), which should read KNOWN_ANALOGUE_FOUND; "affine 0.44 beats Claude 0.33" does not hold on matched systems (Claude .512, affine .487). Not acknowledged by Hecate as of #1177 | Unanswered audit | NEW (hecate entries R-S021..S027 are different) |
| E8 | Hecate/gpt-oss: an abstention pattern ("?" on ~10/29; aliens learned 1/8, known 3/5) "possibly the H1 pattern; too few rows" (hecate/alien/REPORT_pilot.md @061d5cba8) | Quota ended Families B/C | NEW. The hypothesised collapse may exist in another model family |

---------------------------------------------------------------------------------------------------------
## F. Fleet-level residuals (instrument and governance)

| # | OBSERVATION | status | Tyche |
|---|---|---|---|
| F1 | Theseus: 367,214,821 kills are SOUND within 33 claim kinds (class-relative falsification at 658M-record scale) (Harmonia AUDIT_20260819 s5 @7ad201fb3) | A positive statement buried under the "stall" narrative | R-A092 adjacent |
| F2 | June: CAPABILITY space still emitted signal (near-miss +11/+32 pp, co-solve +0.075 AUC, traces +0.16 transfer) while claim space was mined out (AUDIT_20260622 stall map s2) | Never revisited | NEW |
| F3 | The prescribed re-execute-the-battery audit of PROMOTED symbols ("the single most consequential check available", stall map s4 item 2) was not found executed | Parked for 3 months | NEW |
| F4 | Comb R06: 33 NEGATIVE/NULL/INCONCLUSIVE experiments carry 30-102 observed measurements each (e.g. C3-SFE-10 102, C3-SFE-07 94, CW01 e05 80) (atlas.signal R06) | None mined. Atlas's own buried layer | NEW |
| F5 | PTE emission cost: A1 3/3 champions communicate vs A0 1/3 (n = 3/arm); verdict UNRESOLVED by rule ambiguity; the powered T-WC-2b (>= 8 seeds) was never run (roles/Ananke/research/workers/W-C/X4_RESULT.md @a4d054ea0) | Parked | NEW |
| F6 | Tyche v0 P5/R2/tree lens +0.134 (z 12.3) on the selection seed, EXACTLY 0.000 on both fresh seeds (TYCHE-26 open) | Open anomaly | R-S038 (catalogued) |
| F7 | The SI freeze (s12) was never delivered, and Artemis #798 attacked a law that was never frozen | Governance gap | NEW |

---------------------------------------------------------------------------------------------------------
## G. What this means for future Tyche work (ATLAS_DERIVED; for the operator and Tyche)

1. **About half of the strongest buried signals are NEW to the catalogue** (A1-A12: 11 NEW, 1 partly
   present). The catalogue was built from Artemis's harvest plus drafted surveys. It under-samples the
   observations a seat recorded in passing while justifying a design choice (A1, B3, D2): the most
   valuable class, because nobody was looking for them.
2. **Three residual shapes recur across engines and would make good Tyche WORLD forms.** Each has a natural
   structure-destroyed twin:
   - initialization-dependence (A1, C4, the PTE SETRULE bootstrap). Twin: randomize the initial state.
   - present-but-unused information (A8, D6). Twin: shuffle the unused variable across trials.
   - search-policy artefacts (A3, A4, A6, D2). Twin: the same landscape under a neutral-accepting search.
3. **Many A/B entries have committed raw rows** (NPE campaign directories; Archaeon causal_lens outputs;
   the BEE traces referenced in R-A021). Several do not: host-local M2 evidence (BEE results.jsonl, the
   Cosmos C3 withheld branches) is not in git. The catalogue's rule that entries without rows are weaker
   habitat applies.
4. **Calibration specimens** (where the anomaly was right and the ruler wrong: A5; ENVGATE-01 frozen vs
   adjudicated; the P-11 painters) are what Tyche's gate 6 lacks: known-answer residuals. Offering them as
   calibration items is a Tyche/operator decision.
