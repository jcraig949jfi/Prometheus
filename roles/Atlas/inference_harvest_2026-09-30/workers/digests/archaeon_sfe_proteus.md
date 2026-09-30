# Atlas digest -- GROUP archaeon_sfe_proteus (Archaeon + SFE + Proteus)

Reader: fresh-context Atlas reader, 2026-09-30. Repo F:/Prometheus-worktrees/atlas-base-role @ origin/main 1da3130d3.
Tags: **RAN** = executed; **OBS** = instrument output; **CON** = a seat's conclusion (quoted, author named); **ATLAS** = my inference, a hypothesis.
Pointer form: `path` (heading or :line) @sha, where sha = `git log -1 --format=%h -- path`. `#N` = comms_since_0925.txt message id. BRANCH:<name>@<sha> = unmerged material.
Two helper sub-digests were produced first and folded in here: `digests/_part_proteus.md` and `digests/_part_sfe.md`. They hold more Proteus and SFE rows than this file carries.

---------------------------------------------------------------------------------------------------------------------
## 0 Coverage

**Read on main:**
- roles/Archaeon: ENGINE_LANDSCAPE_2026-09-25 @95fff9111, CALIBRATION_LEDGER @7c89a7199, BLOCKED_ON_OPERATOR_INPUT_2026-09-27, H0H5_STATUS (head only, @6fc3ea619).
- archaeon/:
  - campaign1-3 CAMPAIGN_REPORT (heads);
  - campaign4 and campaign5 CAMPAIGN_REPORT (in full), plus C4-02 DESIGN;
  - frontier: DEEP_FRONTIER_CHARTER, DECISIONS DF-001..016 @c7610ea19, digest 2026-09-21T2054Z @939e4f39e, suppressions/PROTEUS-46.json @16799b8bd;
  - z80atlas: CAMPAIGN_PACKET @d50f5710a, POSTCAMPAIGN_ADJUDICATION @18772241e (sections A-G), census and denovo RESULTS;
  - envgate: ADJUDICATION_ADDENDUM @16111cf50;
  - envgate2: VERDICT, CLOSURE @13cdec715, OPERATIONAL_INCIDENT;
  - causal_lens: PORTABILITY01_REPORT and V02_REGRESSION_REPORT @29f06c41a.
- ATTRIBUTION v0 packet: ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/ATTRIBUTION_PACKET.md @f38759992 (merge 6ff2b2f8a).
- Nestor CW01 T-ARCH4 records: BOUNDARY_REPORT_ARCH4 @bdf8c5df4, CYCLE2 @66d964f9a, CYCLE5 @8a01ddede and CYCLE8 @3af735d67, all under roles/Nestor/campaigns/cw01-2026-09-17/loop/. These are where the locality law and the trap-NOP length result actually live.

**Read on branches:**
- BRANCH:archaeon/attribution-arc-2026-09-28@9c8cfed55: E003_SYNTHESIS (all addenda A-I), FIXEDPOINT_RESULT, REVIEW_3..7_ADJUDICATION.
- BRANCH:archaeon/mwo0001-2026-09-28@69e7c5b66: the log only (WORK_STATE/adoption bookkeeping, FP-001, TH-014 G2 hole).

**Comms read in full:** #676, #710, #711, #735, #736, #741, #749, #750, #810-#812, #874, #1003, #1005, #1116, #1130, #1132. Archaeon-related subject lines were scanned from #578 to #1166.

**Not read, with the reason:**
- campaign1-3 per-slot READOUTs, and the C6 observatory, detector and admission packets. These were headline-only, for budget.
- The ANCESTRY_PREREG v1-v5 bodies (the adjudications summarise them), and the RIE code.
- The Deep Frontier EVENTS.jsonl rows (313,119 lines). I used #735 and the digests instead.
- The z80atlas pivot reviews (09-22/23/24) and the REVIEW_PACKET_* files of 09-16 to 09-18.
- SFE D6-D10 (09-01), stackvm and wow. The SFE ledgers are off-repo.
- Proteus v0-v0.2 packets and V0.6 sections C-M. See the part files for those.
- Off-repo evidence (C:\Prometheus-data\...) was not opened.

---------------------------------------------------------------------------------------------------------------------
## 1 Experiment ledger (most recent first)

| # | id / date | question | substrate | ruler / detector | controls | n | OBSERVED | CONCLUDED | status | pointer |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | E-003 BEE+NPE ancestry replay, 09-28..30 | does byte-level ancestry validate, alter or break attribution v0? | BEE r022153; NPE T-003 (11 runs) | owner tracer + Archaeon + independent reference tracer; flip/intervention arms; Q8c | sealed fresh sets 1 and 2; 7 reviewer kills of the prereg (R3-R7) | BEE 32,827 births; NPE 29 distinct births | BEE Q8c (transmission) 0.00115 [0.00098, 0.00134]; flip "other" 0.543; P2 0.504 [0.456, 0.552]; production agreement 0.974 < 0.995 before C11. NPE 1% sample label agreement >= 0.9984 | Archaeon, as amended: "ALTERED (confirmatory, pre-exposure rules); VALIDATED only as amended after exposure"; NPE "uninformative BY CONSTRUCTION" | inconclusive / conditional; operator ruling pending | BRANCH attribution-arc@9c8cfed55 E003_SYNTHESIS s0, s2, addenda G-I; #1044, #1048, #1050 |
| 2 | Fixed-point census + block-15 replay, 09-28 | is the first copier the replicator? | Archaeon z80atlas vmcopy32 | copy map orbit to depth 3 | census and ENVGATE founders | 176 census hits; 475 founders; block 15 U: 3,419,189 births | 12/63 (19%) of near-copiers and 5/22 (23%) of near-copier founders are ONE copy from an exact self-copier (shift + 0x00 fill); block-15 takeover founder is ALREADY exact (fp_depth 0) | Archaeon: withdrew the 3-engine synthesis to "BOTH routes occur; per-lineage empirical question" | partially confirmed, generalisation falsified | BRANCH@698e86124 FIXEDPOINT_RESULT s1, "Attempt 2" |
| 3 | ATTRIBUTION v0 + TH-013/015/item 8, 09-28 | turn the lineage lens into an instrument | block 13 replay to epoch 20,000 (655,307 births) | taint VM; 17 validator rules; knockouts | 2 adversarial reviews | 24 tapes x K=40 backgrounds (TH-015) | executed path + data (mean 21/32 loci) transfers copying at 0.89, vs a size-matched random graft 0.057 and knockout-necessary loci 0.028; aligned founder share 0.90 at 14,000 -> 0.09 at 17,500-19,900 while exact self-copy stays at median 0.83; non-copier children 72% dead on arrival, 0 alive at 20,000 | Archaeon: "reproduction boundary is NOT found"; "the founder was NOT the replicator" | confirmed (instrument); single-engine | ATTRIBUTION_PACKET s0, s3, s5, s11 @f38759992 |
| 4 | Contract v0.2 regression / PORTABILITY-01, 09-26..27 | can the lens leave the Z80 VM? | Archaeon, BEE (845 runs, 28,964,089 births), NPE (34 births), PTE | material-provenance lens vs native labels | frozen adapters before reading native verdicts | as stated | BEE: 847,000 AUTONOMOUS births where the native label credits the TARGET; 9,578,442 (33.1%) NOT_IDENTIFIABLE. B6: r038751 28,163 "location-foreign" births = 27,083 own material / 21 foreign. PTE: mask-majority continuity matches behaviour in 3/48 | Archaeon: B6 "governing code has three referents" (WHO/WHERE/WHAT) | confirmed as a differential | causal_lens/PORTABILITY01_REPORT s3; V02_REGRESSION_REPORT s3-5 @29f06c41a; #741 |
| 5 | ENVGATE-02, 09-25..26 | does restoring window bytes rescue establishment? | Archaeon z80atlas, 24 blocks x 5 arms | GENETIC establishment (taint lineage) | U / BAND0 / R128 / RRIGHT / RWEAK; Page's L; Holm | 24 blocks | U 24, BAND0 5, R128 5, RRIGHT 3, RWEAK 2; U>BAND0 12+/2-, p = 0.0065; parent-chain counts 8x-42x the genetic counts | Archaeon: "WINDOW_NOT_SUPPORTED"; blocking REPLICATES | falsified (rescue); confirmed (blocking) | envgate2/VERDICT_2026-09-26 @13cdec715; #710 |
| 6 | ENVGATE-01, 09-24 | does input-window gating causally control establishment? | same VM | frozen analysis; parent-chain host labels | sham, BLOCK_128, RESCUE_128 | as stated | C4 significance came from ONE takeover world (block 15) and from host-labelled non-independent lineages; block-level p = 0.5 | operator R1: frozen GATING_CAUSALLY_SUPPORTED -> adjudicated **GATING_PARTIALLY_SUPPORTED**; R2 host-mediated reproduction = "amplification, not origination" | partially confirmed | envgate/ADJUDICATION_ADDENDUM_2026-09-24 @16111cf50 |
| 7 | COPIER-CENSUS-01, 09-23 | density of self-copiers in uniform random tapes | z80 and vmcopy, G = 32/64 | isolated VM, 256 inputs | none (blind) | 24 M tapes | vmcopy32: 96 exact per 1e7, **gated share 0.9896** (94 gated to ONE input); z80_32 and z80_64: **0 exact, 0 near** in 1.2e7; vmcopy64 9 exact | Archaeon (prereg question) | confirmed (descriptive) | z80atlas/census/RESULTS.json @c5067fac6 |
| 8 | DENOVO-01, 09-23 | can a random population make a self-sustaining replicator? | vmcopy32 held at the 84616 world's factors | repaired spontaneous predicate | 6 positive controls, all PASS | 80 | 0/80, CI [0, 0.0451] | Archaeon: "NO_DETECTABLE_DE_NOVO_REPLICATION" | negative | z80atlas/denovo/RESULTS.json @18772241e |
| 9 | Z80 x Atlas post-campaign adjudication, 09-23 | re-score the 72 h campaign | 101,003 runs | repaired predicate; instrumented replays | replays of 26 flagged + 19 named + 40 sampled runs | 101,003 | spontaneous_replication 26 -> **0** (all were transplants of seeded material); 27,140/27,141 random-init endogenous worlds went extinct; the 1 survivor (84616cf8257b) is an **input-gated self-copier** (exact only at input 121); 39/39 transplants persist, **0/39 retain task competence** | Archaeon: "transplanted-lineage persistence ... not a de-novo result, not a competence-transport result" | invalidated headline; survivors stated | z80atlas/postcampaign/..._ADJUDICATION_2026-09-23.md s A-G @18772241e |
| 10 | Z80 x Atlas campaign, 09-19..22 | grammar-wide combinatorial search | z80 + vmcopy byte VMs, 31,522 families | 12 mechanical flags | positive controls 5/5 PASS | 101,003 runs, 0 errors | moat_crossed 70,315; spontaneous_replication 26; exploit 0 | packet "code-generated; no interpretation" | superseded by row 9 | z80atlas/campaign/CAMPAIGN_PACKET.md s0-1 @d50f5710a |
| 11 | Deep Frontier scheduler, 09-18..22 | autonomous lineage loop over C4/C5/C6 residues | v0 / graph / repb_fizzle profiles; composed worlds | 7 detectors (5 structurally UNABLE) | seed, replay and audit controls | 119 runs, 3,719,136 evals, 13 lineages | C5-flat N-family at 60,000 evals: median first->last 0.167->0.354 ... 0.396->0.375, max 0.479-0.562 on every N (50/100/200/400); graph fires about 100x less than v0 | Archaeon: flat elite "may be a compute/population-size artefact" [PROVISIONAL] | running then parked; interpretations provisional | frontier/digests/DIGEST_2026-09-21T2054Z @939e4f39e; DECISIONS DF-012 |
| 12 | P-boom (DF-013..015), 09-19 | does evaluation order cause boom-bust spikes? | c6.composed world | spike rate per 100 generations | A/B/C/D/F arms, then shared-stream K_ arms | 8 + 13 runs | spike rate A 0.17/2.83/5.67 vs B 1.67/3.00/3.33; "within-arm spread dwarfs" between-arm | Archaeon: "no order reading" | inconclusive; instrument defect found (hidden seed) | DECISIONS DF-015 |
| 13 | T-ARCH4 tranche (Nestor on Archaeon C4/C5), 09-18 | deformations of C4 | Proteus foundry VM, grammar v0.4, 57 parents | D0-D7 loss | frozen prereg per run | 6 runs, 2 min compute | P-C15: blind scattered deletion loses more than contiguous at the same k (.564/.761/.878 vs .463/.652/.795). P-C04: block .569 vs distributed .630. P-C03: trap-NOP walk length +1.80 vs +0.30. P-C16: length-balanced proposals grow length MORE (+2.35) | Nestor: "locality law is emerging"; "growth is driven by the acceptance filter, not the proposal mix" | see rows 14-15 for the later reread | BOUNDARY_REPORT_ARCH4 s5-6 @bdf8c5df4 |
| 14 | P-D01 dose surface, 09-18 | locality law as a dose surface | same | fixed k, contiguous windows | paired band | 57,536 rows, 126 programs | loss per doubling of k +.145 vs of sites +.024; at k=8, 1 site .66 vs 8 sites .77 (+.05); operand .36 vs delete/opcode/move .72-.75 | Nestor: "mostly a dose in units with a small locality term" | narrowed | BOUNDARY_REPORT_CYCLE2 s2 @66d964f9a |
| 15 | P-G01/G08/G02 ruler audit, 09-19 | do the damage claims survive a fraction-fixing ruler? | same | Bernoulli(f) scattered, qualified | exact-count and contiguous variants | 122-126 programs | 4 of 7 fixed-count claims DISAPPEAR (length protects; depth effects), 2 SHRINK (set/selection), operand softness SURVIVES (-.19); exact-count and contiguous rulers reproduce the artefacts | Nestor: count-fixing rulers "manufacture 'length protects' and 'selected tops are robust'" | ruler artefact confirmed | CYCLE_REPORT_CYCLE5 lines 187-202; BOUNDARY_REPORT_CYCLE5 s3 @8a01ddede |
| 16 | Campaign 5, 09-18 | escape the neutral cliff with a local failure boundary | repb (FAIL/FIZZLE) vs v0.4 | D0-D7; held-out reward | equal compute; world screen (9/25 eligible) | 10 slots | recovery 229 vs insulation loss 154 (replicated); opcode faults recover 209 vs 15, register faults lost 142 vs 25; 0 held-out gains in 96 cells; FIZZLE final populations carry faults in .46-.80 of members | Archaeon + operator: "BOUNDARY_CREATED_NO_DISCOVERY_GAIN"; Phase A "OLD_SUBSTRATE_EXHAUSTED" | closed | campaign5/CAMPAIGN_REPORT s3-6 @cdb55e152 |
| 17 | Campaign 4, 09-18 | does a region of bounded variation exist and help discovery? | Proteus VM v0.4, 57 parents | D0-D7 displacement taxonomy | CRN; replays digest-verified | 1,255 engine records; 5,472 + 2,280 edits | D7 (improve) 0/5,472 and 0/2,280; loss .52 -> .99 over radii 1-16; neutral walk exaptation .016 -> .043; C4-08 loss .42 -> .13 with genome length 19 -> 62 | Archaeon: "cliff in behaviour, not a slope"; C4-08 "ROBUST_WITHOUT_MECHANISM"; C4-10 NO_CONDITION_SELECTED | closed; the cliff premise is challenged (rows 15, 19) | campaign4/CAMPAIGN_REPORT s0-1 @8f1a82ced |
| 18 | PROTEUS-46 falsifier, 09-18 | does a connectivity (graph) grammar remove the cliff? | v0.4 vs graph_organism.v1, hand-written parents | two_key probe 0..6; greedy 3-step walk | 2 seed batches as noise floor | 4,267 / 4,881 children | USEFUL 0 vs 0; destroyed .70 vs .36; neutral .27 vs .64; greedy walks 0/100 | Proteus: "CLIFF_SURVIVES -> FALSIFIER_FAILED ... SAFER ... not more GRADED" | falsifier failed; later challenged (row 19) | proteus/round2/PROTEUS-46_FALSIFIER.md @6a98ef0bb (see _part_proteus) |
| 19 | Artemis D002-03q, 09-30 | can neutral steps cross the PROTEUS-46 cliff? | graph_grammar.v1, quick mode | two_key | control drift | 50 walks x 300 steps | a 5-edit duplicate-and-diverge path: 4 NEUTRAL steps (3/6), then 6/6; the greedy rule never accepts a neutral child (falsifier_46.py:117-131); the full run timed out | Artemis: "crossable by a neutral path in principle"; drift benefit NOT shown | partial | #1116; roles/Artemis/dispatch/D002/RESULT.md |
| 20 | Odysseus S3, 09-27 | is C4-01's 0/5,472 a cliff? | C4-01 a02 children | eligible-edit filter | -- | 1,568 eligible | 0 improved, 61.7% neutral, 4.7% deleterious, 33.6% lethal; rule-of-3 upper bound .0019 | Odysseus: "neutral plateau ... not a cliff" | reinterpretation | #750 |
| 21 | CMP3 (C3-SFE-01..10), 09-17 | shelf -> summit on W2_K2 | WSE + Proteus organisms, SFE as ledger | held-out reward | positive controls repaired and re-preregistered | 10 slots | 0 summits in 24 + 54 K=2 runs; delay ladder 11/12 seeds read d8/d16 at 1.0; import takeover by incompetent controls 12/12 = by competent 12/12 | Archaeon: "IMPORT TAKEOVER IS MECHANICS, NOT CAPABILITY" | closed; delay claim challenged (R-22, section 3) | campaign3/CAMPAIGN_REPORT s0 @cb9135104 |
| 22 | CMP1/CMP2, 09-17 | transfer of prior search material | same | common random numbers (CMP2) | shuffled controls | 10 + 10 slots | CMP1 transfer positives "DIED at n >= 10 under common random numbers (effects +0.009 and +0.002)" | Archaeon: stop the fragment-transfer programme | falsified | campaign2/CAMPAIGN_REPORT s0 @4d80d4b1d |

---------------------------------------------------------------------------------------------------------------------
## 2 Mechanisms (seat words; claimed vs judged evidence level; synonyms)

| mechanism (who) | claimed | judged (ATLAS) | synonyms other engines may use |
|---|---|---|---|
| **Host-mediated reproduction**: an inert host executes a resident copier and emits the resident's genome (Archaeon; operator R2) | stands as a mechanism | strong: taint VM, fixture tests 02/09/10, PORTABILITY A2-A4. One engine only | scaffolded reproduction, HOST_EXECUTION, co-execution, Tierra parasite, CAPTURE, "host-conditioned" (NPE AN3) |
| **Heritable parasite lineage**: the writer's pc falls through into the occupant, whose absolute-addressed loop copies bytes 0..63 over itself (Archaeon via Review 7, BEE r022153) | "most important result so far" | moderate: 13.1% of births, 88% parasite-born, but dry run only; relational capability post-hoc (other class 0.733) | host-performed copy, occupant-performed, DEF-BEL-004 |
| **Founder -> fixed-point child**: an imperfect copy map shifts the genome and 0x00-fills it, and the image is invariant (Archaeon) | one route among two | strong mechanistically (17/17 depth-1 fixed points share the form); prevalence per lineage unknown | quine as fixed point, "first replicator is a product of copying", BUILT_BY_COPY (BEE, corrected to 103/160) |
| **Environmental gating of establishment** (window 120..135) (Archaeon) | blocking REPLICATED; window-rescue NOT SUPPORTED | ATLAS: likely an ADDRESSING constant, not an environment law. The census gives 94/96 exact copiers gated to one input byte; R-26 (#874) says 89/96 are triggered by inputs 125-129 "around the hardcoded neighbour base 128"; 84616's copier loads its destination register from the input (`IN C ... COPY`) | input-gated copier, neighbour-window addressing, "moat" |
| **Cliff not slope** (Archaeon C4-01/02) | SUPPORTED map | weak as geometry. The 0 is robust, but (a) the radius ruler is a COUNT ruler (C4-02 DESIGN: "delta successive grammar.mutate() calls" on genomes of 19-64 words), the artefact family of row 15; (b) S3 reframes it as a plateau | fitness cliff, valley, "no uphill neighbour", neutral plateau, FP-003 |
| **Locality law**: damage spread over more sites hurts more than the same k in one place (Nestor on Archaeon substrate) | "emerging" -> "mostly a dose in units, small locality term" | weak-moderate. +.05 at k=8 (P-D01). The count-ruler audit (P-G08) also shows contiguous windows lose less than Bernoulli at f .10 (.389 vs .461, first field of the tuple; ATLAS reading of an unlabelled tuple). The most robust sub-claim is **word kind**: opcode edits 2.3x more lethal than operand edits (P-C05, cycle 8), and operand softness SURVIVES the ruler change | scattered vs contiguous, block vs distributed, dose in units, operand softness, locality coordinate |
| **Length growth by acceptance, not proposal**: under trap-to-NOP decode, walks accept more and grow 6x more length; balancing length in the proposal mix grows length MORE (Nestor, P-C03/P-C16) | stated mechanism for C4-08 "robustness as length" | ATLAS: coherent with row 15 once the mutation operator is seen as a count-fixed ruler. A single edit hits a smaller fraction of a longer genome, so the neutral-acceptance filter favours length. Length therefore really protects against THIS operator, but not as structural robustness under a fraction ruler (P-D01 length DISAPPEARS) | bloat, neutral padding, introns, "robust without mechanism", C5-08 "LENGTH + behavioural neutrality" |
| **Local recovery vs insulation loss** (C5-06): skipping a faulted opcode acts as a NOP and saves function; skipping a faulted register destroys it | REAL_LOCAL_RECOVERY | strong, replicated on held-out episodes | FIZZLE vs FAIL, trap-and-continue, fault tolerance |
| **Import takeover is mechanics** (C3-SFE-10) | concluded | strong: incompetent controls take over 12/12 like competent ones | takeover without improvement (C4-09, C5-02), establishment is not competence |
| **Governing code has three referents** WHO/WHERE/WHAT (Archaeon B6) | new break | strong: measured on BEE's own traced VM, 27,083/28,163 | own code, pc < L, executor, authorship, write governance |
| **Positional fidelity is shift-blind** (Review 7 on r022153) | accepted | strong in r022153 (183/191 frame-shifted); contradicted on r000001 (section 8) | frame-shifted copy, IBS-as-IBD, resemblance lineage |

---------------------------------------------------------------------------------------------------------------------
## 3 Failures and invalidations (what was LOST / what SURVIVES)

| failure | LOST | SURVIVES | pointer |
|---|---|---|---|
| Z80 x Atlas `spontaneous_replication` predicate counted transplanted seeded tapes | 26 "spontaneous" runs; top-3 family scores 17 -> 14 (the top-30 is now an uninformative tie) | 0 de novo; transplant persistence 39/39 with 0/39 competence; the 84616 input-gated self-copier | ADJUDICATION s A-C, G |
| Seeded worlds insert a hand-written task witness (`task_then_replicate`) | moat_crossed in seeded worlds: 98.2% cross, 77.3% of them at epoch 0; 34/35 top-tier families are seeded | random-init crossings (45.8%, mostly late epochs) | ADJUDICATION s F |
| Recombination matched control drops recombination and explicit_fitness by construction (0/1,829 controls keep recombination) | "3-5x recombination pressure" (all runs .2534 vs .0454) | exploration-only draws .1308 vs .1192 | ADJUDICATION s E |
| Niches topology coupled to migration/reservoir by the 1/(1+coverage) sampler | "niches effect" | niches exploration moat_advantage .0171 vs .0002-.0013 elsewhere, as an association only | ADJUDICATION s D |
| family_table pairs runs with the wrong control (Artemis R-03, workers' claim, unverified) | 40% pressure-changing figure (969/3,351 = 29% for the fixed sampler) | -- | #874 R-03 |
| ENVGATE-01 frozen verdict rested on one takeover world plus host-labelled pseudo-lineages | GATING_CAUSALLY_SUPPORTED | U > BAND and sham specificity; BLOCK_128 copier-founded 47 -> 18 | envgate/ADJUDICATION_ADDENDUM |
| ENVGATE-02 analyze.main() KeyError 'blocks' | nothing: a wrapper changed only the lookup, and the hashes held | verdict | VERDICT "Deviation" |
| ENVGATE-02 first launch killed by the memory reaper (co-tenant load) | 0 results (none had completed) | relaunched unchanged, 6 workers | OPERATIONAL_INCIDENT |
| CW01 count-fixing damage rulers (fixed k, contiguous, round(f n)) | P-D01 length, P-E05 depth x3 (DISAPPEAR); set/selection effects (SHRINK) | operand softness; the qualified Bernoulli ruler | CYCLE5 s3 |
| Deep Frontier: segment streams keyed by run_id (a hidden seed per experiment) | "one thing changes per arm" in P-boom v1 | v1 arms as independent-stream data; fixed by stream_key | DF-015 |
| Deep Frontier: an unvalidated structural_reuse ruler drove FULL freezes | 5,853 FULL freezes in one 16,000-evaluation run | EVENT_RECORD rows | DF-011 |
| Controls spawned controls, 11 deep | 11 of 19 runs | -- | DF-012 |
| classifier_failure fired on 100% of subjects: 5 rulers structurally UNABLE | the classifier signal | CALIBRATION_EPOCH-001 | DF-012 |
| PROTEUS-46 suppression re-logged every scheduler tick | 299,991 BLOCKED rows = ONE decision | PROTEUS-46.json; repair e9c032d50 (500 ticks -> 1 event) | #735, #736 |
| E-003 BEE: 4 post-exposure amendments (C4.2, C4.4, NO_MATERIAL-not-gated, C11) | VALIDATED as a confirmatory label | Q8c 0.00115 in both pipelines; parasite finding; P2 as a native-label finding | E003_SYNTHESIS s0, H, I |
| E-003 Q4 host arm kept "own stores" (owner defect DEF-BEL-004) | frozen host-assisted 0.007 | post-hoc relational 0.733 (labelled) | addendum A |
| Archaeon dry-run Q8c used max-over-groups and an all-draw denominator | the 0.0003 value "is NOT an R2 value" | the owner's 0.00115 | addendum F |
| NPE leg: R3 needs >= 30 transmission births; the unit has 29 | any NPE verdict | 1% sample agreement PASS (label >= 0.9984); 2,818 mutation-shaped residue loci, undiagnosed | addenda G |
| Unauthorized NPE run 3 (stale schtask) | 10/11 sample files | 2 run-1 candidate copies later VERIFIED | #943, #952, addendum G |
| ATTRIBUTION assay v1 read BEE source ADDRESS and value match as descent | "23% label contradicts descent" (BEE) | descent identifiable only from Archaeon's taint record | ATTRIBUTION_PACKET s8 |
| 0x00 knockout is blind to essential NOP loci (Review 2) | essential-locus sets (undercount 5-7 vs 14-17, per R-01) | random-value and full-substitution scans | ATTRIBUTION_PACKET F14; #874 R-01 |
| Item-8 tracking inside the TH-013 replay | its fates are "void" | re-tracked sample: 300 + 300 | ATTRIBUTION_PACKET s11 |
| Block-15 replay chose a 30,000 horizon without reading the takeover dates | Attempt 1 (uninformative) | Attempt 2 (full length) | FIXEDPOINT "Attempt 1" |
| BEE G6 "160/160 BUILT_BY_COPY" (birth_class never set for initial organisms) | 160/160 | 103/160; then a pseudo-replication claim (about 20/160 copies, #1005, unverified) | FIXEDPOINT dated notes; #919 |
| CMP1 transfer positives | SFE-01, SFE-07 | died under CRN at n >= 10 | CMP2 s0 |
| SFE state machine labels a null WEAK_POSITIVE when min_effect <= 0 (Artemis D001/D002) | the WEAK_POSITIVE labels of C3-SFE-03, C4-08, C4-10, C5-03, C5-06 | only C4-01 .379, C4-02 .408 and C5-01 .082 are real effects blocked by an empty battery | #1116 |
| C5-03 a01 failed its own statistic; a02 used a post-hoc change (D5-008) | confirmatory status of representation B | exploratory reading (operator D5-015) | CAMPAIGN_REPORT C5 s3.1 |
| C5-09 a01 determinism control compared wall_s | a01 | a02, same numbers | C5 s3.7 |

---------------------------------------------------------------------------------------------------------------------
## 4 Rulers

| ruler | can observe | cannot observe / audit | pointer |
|---|---|---|---|
| Taint VM (archaeon/lineage): per-byte MATERIAL labels, 4 identities per birth | descent per locus; host vs contributor; WHAT code governs | implicit/control flow (Review 3 CX-A/B); only Archaeon has it, so BEE/NPE descent is "not identifiable from the preserved record" | ATTRIBUTION_PACKET s8; REVIEW_3_ADJ |
| Genetic establishment vs parent-chain label | real lineage counts | the parent-chain label inflates 8x-42x and "would have manufactured a rescue gradient" | envgate2 VERDICT |
| D0-D7 damage taxonomy + displacement (C4-01) | edit-outcome classes | D1 "cannot fire" (932/932 words out of table; interpreter total); the radius ruler is count-fixed | C4 report s0; C4-02 DESIGN |
| Bernoulli(f) scattered ruler (Nestor P-G01) | length-independent damage | qualified: Binomial fit, no clustering, sham clean on 126/126 | CYCLE5 |
| two_key probe (0..6) + greedy 3-step walk (Proteus) | USEFUL/GRADED/NEUTRAL | quantised (no 4/5 seen); greedy rejects neutral ties, so it is structurally blind to neutral paths | _part_proteus; #1116 |
| C6 / Deep Frontier detectors (7) | firings, freeze tiers | 5 structurally UNABLE on every run; the graph profile fires about 100x less at v0 thresholds (operator: do not recalibrate); detectors 1-2 fire 3/12 and 0/12 at frozen thresholds (R-11) | DF-012; #874 R-11 |
| Saturated-ruler guard (attribution/guards.py) | ties at the maximum | retroactively annotated only the v0.2 "3/48" record | ATTRIBUTION_PACKET s7 |
| BEE native `is_sr` / own code (pc < L) | location of code | material; SR run from self-copied code is not counted | #741; PORTABILITY B6 |
| BEE positional fidelity / resemblance label | IBS | IBD; blind to frame shifts | REVIEW_7_ADJ |
| Z80 x Atlas `moat_crossed` in seeded worlds | crossing | who crossed (witness vs evolved) | ADJUDICATION s F |
| WSE held-out battery (C3) | delay generalisation | PUT always at tick 0, so "delay-invariant readers" are first-tick latches (R-22, workers' claim, unverified) | #874 R-22 |
| TH-014 validator | leaks whose channel was recorded | a leak mis-logged with a non-infrastructure via (provenance_log, by_construction, taint) is ACCEPTED (G2 hole) | #1130; BRANCH mwo0001 68fa8800e |
| SFE ledger | prediction-before-observation ordering; losers kept | computes no statistics; replay PARTIAL; a stale client guide names M1/schema 4 | _part_sfe |

---------------------------------------------------------------------------------------------------------------------
## 5 Repairs (what changed; did the outcome move?)

| repair | outcome moved? |
|---|---|
| Label-based -> genetic establishment (ENVGATE-02) | YES. A rescue gradient in labels (194/126/59/139/108) vanishes genetically (24/3/2/5/5) |
| spontaneous_replication predicate repaired + instrumented replays | YES, 26 -> 0 |
| Count ruler -> Bernoulli(f) (CW01 P-G02) | YES. 4/7 claims disappear |
| Representation v0.4 (total, modulo decode) -> repb FAIL/FIZZLE (C5) | damage map moved (the crossing share .386 -> .055; TRAP drawn equally from lethal and neutral); discovery did NOT move (0/96 cells) |
| Flat genome -> connectivity graph (PROTEUS-43/46) | neutral .27 -> .64, destroyed .70 -> .36; USEFUL did not move (0 -> 0) |
| Trap-to-NOP decode (P-C03) | acceptance .602 -> .673; length +.30 -> +1.80; exaptation .043 -> .032 |
| Contract v0.1 -> v0.2 (+J21 proposed) | NPE host-conditioned count 8 -> 16 (v0.1 used the wrong test); BEE AN1 inverted by B6 |
| Prereg ANCESTRY v1 -> v5 (+C1-C11) after 5 reviewer kills | each version was killed before execution; the verdict moved ALTERED -> VALIDATED only through post-exposure amendments |
| Suppression logging one event per state transition | bookkeeping only; verdicts unchanged |
| stream_key in the segment (DF-015) | arms now comparable; P-boom still showed no order effect |
| CRN in the harness (CMP2) | YES: CMP1 positives died |
| Tiered freeze requires an ADMITTED ruler (DF-011) | FULL freezes collapse (5,853 in one run before) |

---------------------------------------------------------------------------------------------------------------------
## 6 Primitive-level interventions

| primitive | intervention | outcome | pointer |
|---|---|---|---|
| copying (supplied op) | z80 (no copy op) vs vmcopy (COPY op 20) | random-tape copiers 0 / 1.2e7 vs 96 exact / 1e7. ATLAS: replication here is a property of the supplied primitive (BEE LDIR off 0/300 vs 8/300, #1132; R-26) | census RESULTS |
| heredity / copy fidelity | fixed-point orbit | 19-23% of near-copiers become exact self-copiers in ONE copy, without mutation | FIXEDPOINT s1 |
| heredity (transplant) | move seeded lineages across world, env and physics | persistence 39/39; self-replication 27/27; task competence 0/39 | ADJUDICATION s C |
| write authority / execution locus | host executes a resident | amplification of the resident genome, not origination | ENVGATE-01 R2 |
| encoding | total modulo decode -> narrow in-table + FAIL/FIZZLE | opcode faults recover, register faults lost; no discovery gain | C5 s3.4 |
| encoding | flat -> graph | safer, not more graded | PROTEUS-46 |
| encoding | trap-to-NOP / trap-HALT on the degenerate stratum | inert under every decode (D7 = D6 = 0 in 839 children per rule) | ARCH4 P-C13 |
| locality | scattered vs contiguous deletion, same k | scattered loses more (.564/.761/.878 vs .463/.652/.795) | ARCH4 P-C15 |
| locality (word kind) | opcode vs operand edits | opcode 2.3x more lethal; survives the ruler change | BOUNDARY_REPORT_CYCLE8:34 @3af735d67; CYCLE5 s3 |
| environment / input | block input window 120..135 | establishment 24 -> 5 | ENVGATE-02 |
| environment / input | restore 128 / 128..131 / 125..128 | 5 / 3 / 2 (no rescue) | same |
| selection | 100 generations on 188 drifted lineages | robustness .42 -> .13, via length 19 -> 62; D7 10 -> 0 | C4-08 |
| selection / population size | N 50..400 at 60,000 evals (Deep Frontier) | every N climbs above the best starting parent (.382) to max .479-.562 | DIGEST 2026-09-21 |
| recombination | mate-splice | 8 points less viable; no novelty | C4-06 |
| memory / state | persist_shared on vs reset (W-artifacts) | ATLAS: medians first->last are IDENTICAL persist vs reset in all 12 worlds shown (e.g. w50053 .067 -> .069 both). The knob looks inert, or the worlds carry no state (DF-012 names "no persistent state" as a structural UNABLE) | DIGEST 2026-09-21 |
| admission / suppression | falsifier gates a transformation | blocked forever unless neighbourhood_exhausted -> retirement_candidate_A (no path to "runnable") | PROTEUS-46.json |
| resources / time | ENVGATE-02 non-U establishments sit in the slowest blocks 11/13/14 (5.9/3.3/5.9 h vs median 1.0 h) | 3 of the 5 BAND0 establishments are the same arrivals across arms | #749 |

---------------------------------------------------------------------------------------------------------------------
## 7 Buried signals (observation kept apart from any failed interpretation)

1. **Deep Frontier falsifies the C5 "flat elite" as a compute artefact, and nobody promoted it.** At equal 60,000 evaluations every N climbs (max .479-.562 vs best parent .382). C5's arms had 9,000-36,000 evaluations. The interpretation is PROVISIONAL. C5's operator-accepted "selection under the frozen grammar does not climb these worlds at all" was never revisited (DIGEST 2026-09-21; DF-012; C5 s2).
2. **The "environmental gate" may be the VM's neighbour base address.** The census has 0.9896 of exact copiers gated to one input. R-26 puts 89/96 on inputs 125-129 around base 128. The 84616 copier takes its copy destination from the input. The ENVGATE window 120..135 surrounds 128. ATLAS: "environment controls reproduction" and "input byte is a pointer into the neighbour" are the same observation. R-33 adds that 0 of 5,200 single-byte mutants widen gating, so the staged RIE cannot answer liberation vs acquisition.
3. **Transplant = persistence without competence** (0/39). Seeded-derived lineages keep copying in every swap and lose every task. It is a clean dissociation of heredity-of-copying from heredity-of-function.
4. **The only random-origin survivor fails the frozen fidelity threshold** (late fidelity 0.482; exact only at input 121). It is a real reproducer that the ruler excludes (ADJUDICATION s G).
5. **FIZZLE hidden load**: .46-.80 of final population members carry executed faults, with nothing bought (C5-09). It fits Nestor P-G09: load is unpurged initial junk.
6. **C5-06 asymmetry**: insertion is "the rescued operator", with 102 recoveries and 0 losses. Nobody followed it up.
7. **Exaptation gradient under neutral walks**: .050 -> .082 at depths 16 -> 64 (C5-01). It is real but was killed on a yield rule. As an observation it still stands.
8. **The five BAND0 establishments**, decomposed as 3 cross-arm takeovers plus 2 residual near-copiers (blocks 4, 15) that established ONLY with the window closed (#749). They are retained as fossils and not pursued.
9. **Parasite class**: 0/120 isolated-capable vs 117/120 in the self-performed class. Material and capacity split totally by class. The average (85% capable) hid it (REVIEW_7_ADJ).
10. **E-003 per-class Q8c "none" = 0.242 [0.162, 0.330]**, above 5%. Pooling in R3 hides it (E003_SYNTHESIS s2 Q2).
11. **B6 code-material reading**: BEE r016299 has 8,166 truly foreign-governed births by material. Host-executed copying exists in BEE at a small scale (PORTABILITY s5).
12. **Deep Frontier graph profile**: C6-blind.T1 graph runs reach max .375-.500 with almost no firings. It is an unobserved regime rather than an empty one.
13. **P-boom spikes** (max reward up to .979 in single runs with median ~.1) were never explained. Spread within an arm dominates.
14. **NPE 1% sample residue**: 2,818 label-only loci (9.6% of interactions), mutation-shaped, undiagnosable because the discrepancy records omit label values (addendum G).

---------------------------------------------------------------------------------------------------------------------
## 8 Open contradictions and cross-engine hooks

| A | B | status / note |
|---|---|---|
| C4 "cliff at every radius" (count ruler) | CW01 P-G08: count rulers manufacture length and set effects; S3 "plateau" | ATLAS: the C4-02 curve has not been re-read under Bernoulli(f). The cliff premise still feeds PROTEUS-46, HEPH-32 and FP-003 |
| PROTEUS-46 "no intermediate the probe can see" | Artemis D002-03q 5-edit neutral path | search reachability (greedy tie rule, 3 steps) read as landscape. Proteus inactive since 09-18 |
| PROTEUS-46 graph "SAFER" | C3-SFE-02 evolved v0 shelf parents already .64 neutral / .36 destructive (_part_proteus) | ATLAS: the representation contrast may be a parent-choice contrast (hand-written vs evolved) |
| BEE frame-shift (Review 7: 183/191 on r022153) | V0.2 regression on r000001: frame-shift "NOT supported", 65/66 NOT_IDENTIFIABLE | different runs; unresolved |
| "Founder is not the replicator" (block 13) | block-15 takeover founder IS exact (fp_depth 0) | resolved as "both routes occur" |
| Nestor W1 (#742): heredity fails in carried register state; NPE "certificate certifies an EVENT, capability lives in the host's register state" | Archaeon TH-015: the transferable object is the executed path + data (0.89), not knockout loci (0.028) | cross-engine convergence on "capability != material". Both say the copy capacity lives partly outside the minimal genome |
| ENVGATE-01 frozen CAUSALLY_SUPPORTED | operator R1 PARTIALLY_SUPPORTED | "frozen analysis verdict != final scientific adjudication" is now a program norm |
| E-003 BEE VALIDATED (Bellerophon f9a93eb6d) | Harmonia #1044: ALTERED under pre-exposure rules | owner, auditor and author concur ALTERED; operator verdict pending |
| C3 "delay ladder builds delay invariance" (11/12 at d8/d16 = 1.0) | R-22: first-tick latches, fall to 0.00 with one pre-PUT noise tick; CW01 P-D02: a NOISE tick makes silent W0 drift loud | ATLAS: the held-out battery could not see the target. Treat the delay-invariance claim as unverified |
| C3 "shelf is a one-value memory" | R-25: 3/19 hold both values in fixed registers; 2/19 answer by ask position; the missing primitive is key binding | refinement, unverified |
| The Z80 world triplicated (NPE, BEE, Archaeon) from one directive | ENGINE_LANDSCAPE: "As a WORLD: NOT distinct"; R-34: the lens pair recovers only 23-34% of the known convergence | Atlas indexes none of z80atlas, envgate or envgate2 (ENGINE_LANDSCAPE s4; #874 R-34) |
| "3 independent worlds make replication a design law" (D_Z80_SYNTHESIS) | R-26: every recurrence vanishes when the supplied copy op is removed | withdrawn by Archaeon |
| Archaeon C4-04 "addressing damage": insertion +.215, movement +.193 | Proteus design rationale: "a flat genome has no PART" | same observation, two seats; motivated graph_organism |
| SFE provenance (prediction before observation, losers kept) | Artemis: "orphaned, not decided"; no successor since 09-18 | ATLAS: Archaeon's post-09-18 work (frontier receipts, sealed hashes, fresh sets) re-implements SFE's ordering guarantees without SFE |

---------------------------------------------------------------------------------------------------------------------
## 9 Five things a cross-engine synthesist must know about this group

1. **Most "physics" findings here turned out to be about the instrument or the search, and the corrections are in the record.**
   - The damage "cliff" and "length protects" come from count-fixing rulers (C4-02; CW01 P-G08). The mutation operator itself is a count-fixed ruler. That is also why neutral walks grow length by acceptance, not proposal.
   - PROTEUS-46's "no intermediate" came from a greedy 3-step walk that cannot accept neutral steps.
   - C5's "flat elite" did not survive equal-compute N scaling.
   - When another engine reports a cliff, valley or flat elite, check its ruler's count-vs-fraction geometry and its search policy's tie rule first.
2. **Reproduction in these byte worlds depends on a supplied copy primitive and on addressing constants.**
   - Real-Z80 random tapes contain 0 copiers in 1.2e7. vmcopy (with COPY) contains 96 per 1e7.
   - 99% of those are gated to one input byte, near the hardcoded neighbour base 128.
   - The ENVGATE "environmental gate" is plausibly that addressing geometry (ATLAS).
   - De novo replication: 0 of 101,003 campaign runs and 0/80 in DENOVO-01. The 26 campaign hits were transplants.
3. **Heredity decomposes: material, state, production, dependence and capability dissociate.**
   - Transplants persist and self-copy but lose all task competence (0/39).
   - Parasites carry material with 0/120 isolated capability.
   - The first apparent copier is often not the replicator (a fixed point of an imperfect copy map). Direct routes also exist.
   - "Own code" has three referents: WHO, WHERE and WHAT. BEE's pc < L is WHERE.
   - Any engine claiming heredity or SR from a location or resemblance label is at risk. Archaeon's taint VM is the only preserved per-byte descent record in the program.
4. **Labels inflate lineages, and genetic identity deflates them.**
   - Parent-chain host labels ran 8-42x the genetic establishment counts. They manufactured a rescue gradient and ENVGATE-01's causal verdict.
   - Establishment, takeover and import takeover are not competence: incompetent imports take over 12/12, and lateral rescue takes the population without moving the elite.
5. **Governance lessons are load-bearing for cross-engine comparison.**
   - Suppressions can only lift toward retirement, and 299,991 rows were ONE decision.
   - The frozen verdict and the adjudicated verdict differ (ENVGATE-01).
   - Post-exposure amendments make E-003 BEE's VALIDATED conditional (confirmatory = ALTERED).
   - SFE's WEAK_POSITIVE labels include nulls (min_effect <= 0).
   - SFE has been dormant since 09-18. The last Proteus commit is 6a98ef0bb (09-18). Archaeon has been on HOLD under MWO-0004 since 09-30 (BRANCH mwo0001@69e7c5b66).
   - Several key challenges (R-01..R-34, D002-03q) are Artemis workers' claims, some unverified, and neither Proteus nor any successor has answered them.
