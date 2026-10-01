# ATL evidence digest: Atlas inference harvest, ecosystem catalogue, mechanism/fossil catalogues, Phase 3 challenges

Reader: read-only evidence reader for EPIMETHEUS (OPUS-5.5), 2026-10-01. Worktree C:/prometheus-worktrees/epimetheus-phase3
(HEAD c9b18697b). No experiments run; only file reads and small python tabulations over committed JSON/JSONL.
Independence: nothing under docs/phase3/design/ other than this file's own directory was opened; nothing under
roles/Dionysus/ was opened; no holdout/secret path was opened.

Tags: IMPL = I read it in code/data; HIST = historical claim in the record; REPORTED = a seat's or Atlas's result I did
not re-derive; CORR = later correction in the record; INFER = my inference from code/data; INTENT = stated design
intent; UNK = unknown. "Atlas" below = Atlas[m1-a5680f90], whose harvest is itself a Claude-authored synthesis of
Claude-authored digests of Claude-authored seat records. Atlas is a locator, not ground truth.

---------------------------------------------------------------------------------------------------------------
## 0. Bottom line for the architect

1. The Atlas harvest is the best available cross-engine map, and its main conclusion is about the APPARATUS, not
   about organisms: every candidate cross-engine convergence traced to a shared ruler, one design family, one seat's
   citation chain, a single-originator comms term, or one model family (REPORTED, roles/Atlas/inference_harvest_2026-09-30/
   ATLAS_CROSS_ENGINE_SYNTHESIS_2026-09-30.md s4). I spot-checked 9 load-bearing claims against artifacts; the numbers
   held in all 9, but 4 carry scope limits or confounds that Atlas did not state or stated weakly (s2 below).
2. What the historical worlds actually DEMANDED, where a demand can be read off the record, is at most a 1-bit latch,
   a short FSM, a constant/echo lookup, or a self-copy loop. A 4-instruction hand latch beat the evolved PTE HOLD
   champion (.999 vs .755) (IMPL roles/Ananke/research/workers/W-H/REPORT.md:42). The SFE C3 "delay-general"
   organisms that read untrained delays 8 and 16 at 1.0 are, by Nestor's own perturbation census on that lineage,
   start-anchored (fail only with an idle tick before the first PUT) (IMPL roles/Nestor/campaigns/cw01-2026-09-17/
   loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md:57-60). NPE C9 competence was "carried entirely by answer-before-read
   guessers and no reader ever evolves" (IMPL roles/Nestor/FINDINGS.md, E-9). Nothing in this group's evidence shows a
   world that required hidden-state inference, maintained alternatives, or composition, AND an organism that met it.
3. The strongest within-world facts are primitive-level manipulations with matched controls in the Z80 design family
   (copy primitive presence/encoding cost; zero-register addressing; write-back atomicity). They are real facts about
   those worlds (IMPL for the Archaeon census and NPE/BEE source lines) and say little beyond that family: three
   "Z80" worlds came from one directive and share LDIR-style copy, zero-init and offset/neighbour-base addressing.
4. Ruler validity is the binding constraint, measured: of 94 absence-reading gates, 37 were never shown to fire, 12
   fired on a same-substrate plant, and among the 57 with any positive there were 56 single analyst-known plants,
   1 graded curve and 0 blind injections (IMPL roles/Artemis/selftest/runs/R-11/REPORT.md s3).
5. Search policy was routinely the unmeasured variable that produced "physics" negatives. PROTEUS-46's probe
   could not, by construction, see any path longer than 3 edits or any neutral step (IMPL proteus/round2/
   falsifier_46.py:31-32,114-127). Budgets were uniformly small (GA 96 x 36 gens; C5 9k-36k evals) (REPORTED).
6. The only curriculum-versus-direct-search control I found in this group (SFE C3 delay ladder vs matched-budget
   direct search) produced what looks like a latch, not memory. It is the single most instructive fossil for
   Phase 3 Challenge 4: a curriculum can "work" by teaching a trivial mechanism that passes an out-of-distribution
   readout.
7. The mechanism/fossil catalogues (Nyx organ atlas, Techne fossil vault, Necropolis) are reading catalogues, not
   validated instruments: Nyx 542/549 organs graded SOURCE_READ, 0 measured dimensions, 0 blind cuts, 0 transplants
   (IMPL nyx/atlas/out/DEPTH_MAP.json, ATLAS_COVERAGE.json, BLIND_CUT_COMPARISON.json); Necropolis 41 recorded
   mistakes, all on fair_test UNFAIR, 0 post-repair behaviours measured, 5 repair "monsters" all PROPOSED
   (IMPL engine/necropolis/COUNTERFACTUAL_HISTORY.jsonl, monsters/*.json).
8. The external ecosystem catalogue (365 rows) has no axis for within-lifetime cognitive development; its
   "development" flag is mostly morphogenesis (CA/NCA/virtual creatures). It is a map of where Prometheus is not,
   not evidence about mechanisms (IMPL roles/Atlas/catalog/ECOSYSTEMS.jsonl tabulation).

---------------------------------------------------------------------------------------------------------------
## 1. What the Atlas apparatus is, and what it could reveal

Pipeline (REPORTED, INFERENCE_HARVEST_HANDOFF.md s3): corpus repair of the Atlas index (333,044 -> 33,054 facts after
collapsing 299,991 suppression echoes), 7 fresh-context reader digests (RAN/OBSERVED/CONCLUDED/ATLAS_DERIVED tags),
3 synthesists (regularities; adversarial common-cause map + attack; contradictions/natural experiments), 2 claim
verifiers (60 claims: 32 confirmed, 25 corrected, 3 contradicted), and a cross-model-family blind re-derivation on a
masked OBSERVED-only packet (Kimi K3, DeepSeek v4.1-flash answered).

Capacity limits of the apparatus (all REPORTED by Atlas about itself, and consistent with what I read):
- Index cannot answer "which primitive combinations precede success": every experiment-level primitive row is
  inherited from the engine; positive and negative experiments carry the same tuples (69/17/4 vs 66/20/4); 649/723
  POSITIVE rows are Vivarium queue completions (ATLAS_ONTOLOGY_GAPS_VNEXT.md s0; confirmed by VERIFY_DRAFTS_1 #16
  via a live SELECT; I did not re-run it). The index models nothing after 2026-09-22 and has no adapters for PTE,
  BEE, Aether, Hecate, Ensorain, Tyche.
- The synthesis ran on digests that summarize seat syntheses, not raw rows; host-local M2 evidence (BEE results.jsonl,
  Cosmos C3 withheld branches, SFE ledgers) was unreadable.
- Brief echo: the reader brief asked for "search/reachability limits" and "any case where the ruler could not see the
  target" and supplied the primitive bins; two regularity families partly return the brief to its author
  (ATLAS_CROSS_ENGINE_SYNTHESIS s0).
- One model family wrote, attacked, verified and reconciled everything except the cross-family check. Hecate is a
  direct measurement of that family's mapping prior (32/32 mechanically alien rules called FAMILIAR or COMPOSITE)
  (workers/ARTIFACT_MAP.md s C; Hecate number IMPL hecate/autopsy/AUTOPSY.md).
- The cross-family check recovered F1 (instruments bound the claims), F2 (world-supplied copy primitive/zero state),
  F3 (copying vs competence) and R6 (labels are not ancestry); it did NOT recover F4, F5, F6; it re-described
  "search, not physics" as landscape facts (flat/neutral/lethal neighbourhoods) (REPORTED handoff s7; I confirmed
  the Kimi K3 response headings match: workers/xfamily/RESP_moonshotai_kimi-k3.md). Row selection was still done by a
  Claude worker; scoring was not blind.

What the apparatus genuinely could reveal: (a) which historical claims share a ruler, substrate lineage, or author;
(b) which numbers survive a re-read of their own source; (c) where seats disagree and what single test would
separate them. It could not reveal any substrate-general regularity, and it says so.

---------------------------------------------------------------------------------------------------------------
## 2. Spot-verification of consequential cross-engine claims (my own artifact reads)

| # | Atlas claim | artifact opened | verdict | what I found beyond Atlas |
|---|---|---|---|---|
| V1 | F2: real-Z80 random tapes 0 copiers in 1.2e7; vmcopy 96 exact per 1e7, 0.9896 gated | archaeon/z80atlas/census/RESULTS.json; archaeon/z80atlas/vm.py:1-40,95-115 | CONFIRMED (IMPL) | z80_32 EXACT 0, NEAR 0, WRITER 35 of 1e7; vmcopy32 EXACT_GATED 95 + UNGATED 1; 94/96 exact at exactly one input; stage2 128/176 offspring heritable. VM: registers zeroed every execute (l.33), NBR = 128 hardcoded, COPY (op 20) is NOP unless copy_prim. INFER: the z80 ISA keeps LD A,(r) / LD (r),A, INC, DJNZ, so a byte-copy loop is expressible without COPY; "0 in 1.2e7" is a needle-density fact, not impossibility. INFER: input gating near 128 is what a zeroed register file plus a fixed neighbour base predicts. |
| V2 | F2: NPE C-ZERO-SPECIFIC ZERO 26/48 vs CONST 2/48 vs CARRIED 6/48 | roles/Nestor/FINDINGS.md P2 block (~l.462-470) | CONFIRMED with confound (IMPL) | Source states "Part of this is by construction: the COMPETENT ruler certifies from zeros." So the ruler and the treatment share the zero state. Also IMPL from the same file: "Nothing dies in these cells: the only selection is being overwritten by a copy"; "competence is a property of genome x cell, not of the genome" (X-DONOR-SWAP). |
| V3 | A1 / B1: BEE carried registers kill zero-dependent founders 0/24 vs ZERO 10/24 | roles/Bellerophon/repl_2026-09-30/PREREG.md s1 D1-D2 | CONFIRMED, but near-definitional (IMPL) | Founders were "certified ZERO_DEPENDENT" by construction (D1). Pilot numbers (n = 24; p-sweep n = 12/arm) inside a design-deviation rationale. Killing zero-dependent founders by removing zeros is selection-by-construction; it is weak independent support for an "initialization regime" primitive. |
| V4 | F2/F4: BEE LDIR off 8/300 -> 0/300; mutation supply 8/3/4 not distinguishable; world-made copies explain extinction 0 vs 148/150 | roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md s1, s3, s6 | CONFIRMED (IMPL) | Report also: seeded lineages' evolutionary activity falls with mutation supply 60 -> 48 -> 11 of 60 (counter to F4's spirit); external vs endogenous 178 vs 2 with offspring quantity unmatched (~95k vs ~15.5k births); "the replication basin is shallow and wide around any tape that already has the setup" (NOP of copy byte is not a knockout). |
| V5 | F3: transplants persist 39/39, competence 0/39 | archaeon/z80atlas/postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.md s C | CONFIRMED with readout caveats (IMPL) | "Competence retained" = final best >= 0.999. Parsed the 39 rows: 30 at 0.0, 9 partial (0.333-0.531). 12 rows changed the task (environment_swap), so "retention" there scores a different task. Source column is best-ever 1.0, transplant column is final best: an ever-vs-final readout asymmetry. Even in the 11 "same" arms (same world, same task) 8/11 are 0.0 and 3/11 are 0.43-0.53. The dissociation survives; its magnitude is threshold- and readout-dependent. |
| V6 | F1: 37/94 absence gates never fired; 12/94 fired on same-substrate plant; 0 blind | roles/Artemis/selftest/runs/R-11/REPORT.md s2-s3 | CONFIRMED (IMPL) | Of 57 absence-read gates with any positive: 56 single analyst-known plants, 1 graded curve, 0 blind injections; missing FLOOR 61.7%; failing >= 1 property 78.7%. Frame is Artemis's chosen engine list; Aphrodite is 20 of 94 rows (REPORTED verifier). One seat, four same-family hand-readers, 10-row second read. |
| V7 | F8/A7: PROTEUS-46 greedy walk cannot accept neutral children | proteus/round2/falsifier_46.py:31-32,100-135 (@6a98ef0bb) | CONFIRMED and stronger (IMPL) | best_key = (cur, 0) vs child key (two, -ops), ops >= 1, so only strict two_key improvements are accepted. Also WALKS, WALK_STEPS = 200, 3 and GREEDY_PATHS, GREEDY_WIDTH = 100, 50: BOTH probes have a 3-step horizon. A 5-edit path with 4 neutral steps is outside the attainable verdict set of both probes. |
| V8 | F6 correction: CW01 "register predicts regime 1.0, unused" withdrawn | roles/Nestor/campaigns/cw01-2026-09-17/DEFECTS.jsonl line 90 (CW01-D089) | CONFIRMED (IMPL) | In-sample lookup over 64 distinct values in 64 asks scores 1.0 trivially; cross-set regime registers []; "the answer is emitted BEFORE the ask tick is read". Status field still "OPEN". |
| V9 | F1: Hecate detector 0/32 UNFAMILIAR; Cosmos C3 zero-parameter rule 104/120 | hecate/autopsy/AUTOPSY.md:1-30; roles/Cosmos/research/reviews/COORD_AUDIT_C3_2026-09-29.md:30-45; roles/Cosmos/research/RESULTS.md:15-40 | CONFIRMED, with a post-harvest CORR (IMPL) | Hecate AUTOPSY carries CORRECTIONS 2026-10-01 (after Atlas's harvest): Part B inputs were scrubbed (rewrite rules erased); R1 still holds on the other 24; R1 is "a property of the definition on fully specified rules". 243 generated mechanisms were never put through any novelty detector; 58 admitted. Cosmos: all 16 misses of the zero-parameter rule are noise-limited boundary cases; ALL six universes authored by Cosmos; C0 laws tie the definition rung (McNemar .688/.688/.125). |

Also IMPL: PTE plant numbers (W-H/REPORT.md:42,85: 4-instruction latch .999 vs champion .755; fixed-rule hand programs
of 4-7 live instructions beat switching champions, S4 1.000 vs .590; W-L/REPORT.md:63 lag-2 plant solves, search 0/4);
NPE C-ATOMIC 46/80 vs 1/80 with C2 1/120 vs 0/120 NOT CONFIRMED and erosion ~5%/byte/epoch ~25x nominal (FINDINGS E-10
block); C9-H1R (FINDINGS E-9 block).

---------------------------------------------------------------------------------------------------------------
## 3. Engines as seen through this group (what was really built)

Descriptions combine Atlas digests (REPORTED) with the files I opened (IMPL where marked). Other evidence readers own
the per-engine depth; this table records only what the Atlas layer exposes.

| engine (seat) | organism actual | world actual | pressure actual | ruler actual | max cognitive demand actually shown |
|---|---|---|---|---|---|
| NPE pair-tape (Nestor) | Z80-like byte genomes on 64-128 byte pair tapes; LDIR/LDDR copy; operand-only mutation in 7ae3/ffa6 (IMPL FINDINGS ARC3 correction) | random populations, pair execution writing both halves back; zero/CARRIED register regimes; nothing dies, selection = being overwritten (IMPL) | implicit overwrite competition; optional EXPLICIT fitness (effect EXTERNAL-only) | P-11 construction (painters pass), CVT-R, dense_taint, depth >= 20 runaway | self-copy loop; C9 cue task solved by guessing; costly reading never evolves (IMPL) |
| BEE Z80 soup (Bellerophon) | Z80_64 byte tapes; LDI/LDIR/COPYALL; undefined bytes NOP (REPORTED verifier code read) | 256-cell grid/soup/pollination topologies, lifespan 40, v2/v3 physics (IMPL PREREG s1) | implicit replication; v3 contingent payment for task output | SR = pc < L (location), G resemblance, causal L, material label, bee_tracer on one run | copy loop; seeded CONST/ECHO tasks maintained under payment; COND_ONE 0/960 never acquired (REPORTED) |
| Archaeon z80atlas / vmcopy | 32/64-byte tapes, 32 opcodes, zeroed registers, neighbour window at 128 (IMPL vm.py) | isolated census (1e7 tapes x 256 inputs); campaign worlds niches/grid/graph | implicit + task competence in campaign | census exactness classifier (two-sided demonstrated), taint VM | copy loop; constant/conditional outputs lost on transplant (IMPL adjudication) |
| Proteus VM family: SFE C1-C6, CW01 T-ARCH4, Deep Frontier | v0.4 grammar programs (19-64 words), graph substrate variant | two_key keyed task; delay ladder; regime ask; shelf worlds | explicit fitness, imports, neutral walks | count-fixed damage ruler (later Bernoulli(f)), two_key quantised probe | 1-bit latch (start-anchored delay readers, IMPL CW01 cycle 5); guess before read (CW01 D089) |
| PTE (Ananke) | small register programs in a periodic broadcast/relay physics; registers 0 at tick 0 (REPORTED) | HOLD, lag-2 retention, RELAY, M2/M3 cells | GA 96 x 36 generations (REPORTED) | mirror-pair carrier swap (repaired 5 times in 3 days), phase-indexed swaps, plants | 1-bit latch (4-instruction plant .999 beats champion .755); 2-step FSM expressible (16-line plant) but unreached 0/4 (IMPL W-H, W-L) |
| Aether | byte-template medium with energy field; rule-by-rule ladders (aeth01.v1 + 9 variants) | no task; ~93% of template bytes frozen; one energy regime | none (physics study) | exact one-bit twin footprint; content signature failed its own positive control (3.1% < 5%) | none (no organism task) |
| Cosmos | no evolving organism; law miner over authored universes | 6 universes, all authored by Cosmos, planted task economy SELECTIVE_PAYS (IMPL RESULTS.md) | none on organisms | certificate P1/P2, zero-parameter definition rung, McNemar | none; laws restate the certificate |
| Hecate | LLM-generated mechanisms and worlds | 243 mechanisms, 58 admitted worlds (IMPL AUTOPSY) | admission gates | LLM novelty detector (cannot reach UNFAMILIAR) | n/a |
| Ensorain / WTP | memory/eviction policies, LM01 frozen never launched (REPORTED) | key-value and drift streams | policy comparison | constant twin, tuned completion baseline (beats all 9 WTP-03 flags) | recall + recency window; "no fixed window works" |
| Tyche | dark-ecology populations (REPORTED) | regime worlds, parity-3 | 30-50 generations | OV clock (population-only), H1 unreachable by design (3 valid worlds < 4) | regime adaptation 2/72; parity-3 unreached |
| NPE GraphWorld (Nestor swarm) | code/policy learners on NK landscapes (REPORTED) | graph worlds r1-r8 | explicit fitness, QD | abstain-floor audit | an abstain policy beats every R2 pass; one 8/8 NK transfer-like result survives |

---------------------------------------------------------------------------------------------------------------
## 4. Result-by-result evidence profiles (Q S W R B Rep M; Y/P/N/U) and reclassification

| id | historical result | historical status | reclassification | Q | S | W | R | B | Rep | M | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ATL-01 | Z80 family: copy primitive necessary for spontaneous self-copying (BEE 8/300 -> 0/300; census 0 vs 96/1e7; NPE alias 1/64 -> 39/64) | Atlas ESTABLISHED within family | instrument_positive (design-family scoped) | Y | Y | P | P | Y | P | Y | Ablation removes, alias restores; SHAM 0/96 density control (NPE). Three codebases, one directive; BEE origins pseudo-replicated (160 origins, 83 distinct seeds, REPORTED ERRATA E2). |
| ATL-02 | NPE establishment rescue is ZERO-specific (26/48 vs CONST 2/48) | CONFIRMED (frozen) | instrument_positive with ruler confound | Y | Y | P | P | Y | N | P | Ruler certifies from zeros (IMPL). Mechanism reading relabelled within 1 day ("register persistence" -> "zero addressing"). |
| ATL-03 | BEE carried registers kill zero-dependent founders 0/24 | buried pilot (Atlas A1, top buried signal) | false_positive as cross-engine support (selection-by-construction) | P | Y | U | P | P | N | N | Founders certified ZERO_DEPENDENT (IMPL). True as a design fact; uninformative about a general primitive. |
| ATL-04 | Transplanted Z80 lineages persist 39/39, self-replicate 27/27, competence 0/39 | Atlas ESTABLISHED | instrument_positive (persistence); competence half = world_insufficiency + ruler_insufficiency (readout) | Y | Y | N | P | P | P | N | World does not require competence to persist; source best-ever vs transplant final; 9/39 partial; task-swap arms mixed in (IMPL). |
| ATL-05 | Incompetent imports take over 11-12/12 like competent ones (C3-SFE-10) | CONFIRMED | instrument_positive (mechanics) = world_insufficiency for competence selection | Y | Y | N | Y | Y | N | P | Opcode-permuted incompetent control is a good matched negative; no-import 0/12. |
| ATL-06 | BEE: endogenous reproduction antagonises task code (EXTERNAL-only 178 vs ENDOGENOUS-only 2) | CONFIRMED_CAUSAL (v2) | instrument_positive; diagnoses pressure_insufficiency under endogenous reproduction | Y | Y | P | P | P | N | P | Offspring quantity unmatched (~95k vs ~15.5k); IMPLICIT cells task-inert (IMPL GROUNDING s6). |
| ATL-07 | BEE contingent payment maintains seeded task code (ON vs YOKED extinction 1 vs 67/150) | strongest surviving BEE mechanism | instrument_positive (maintenance only); acquisition = search_insufficiency/organism_insufficiency | Y | Y | Y | P | Y | N | P | YOKED twin at equal total resource is the cleanest pressure control in the record (REPORTED, verifier-confirmed). COND_ONE 0/960; random soup 0/3,200. |
| ATL-08 | NPE C-ATOMIC: atomic write-back 46/80 vs 1/80 runaway heredity | C1 CONFIRMED; C2 NOT CONFIRMED | instrument_positive (one cell); C2 null = organism_insufficiency (intervention delivered to non-copiers) | Y | P | P | P | Y | N | Y | Scope 7ae3 cell, splice off (IMPL). Twelve panel donors copy at 0.0 from fresh state. |
| ATL-09 | F4: nominal mutation rate is a minor share of effective variation | Atlas SUGGESTIVE-MODERATE (reconciled) | survives_as_anomaly; statistical_insufficiency | P | U | U | N | N | N | N | No variation-source ledger exists; BEE 8/3/4 indistinguishable at n = 300; BEE seeded 60 -> 48 -> 11 and Aether mut_numer cut run the other way. |
| ATL-10 | NPE C9-H1R: answer gate abolishes competence only when reading costs (0.200 -> 0.000; free 0.197 vs 0.197) | COST_INTERACTION_ONLY | instrument_positive (world-demand probe); for "reading evolves": search_insufficiency + world_insufficiency | Y | Y | Y | Y | P | P | P | Positive control: a correct reader scores identically under the gate (IMPL). Ungated competence = guessers. Transplanted to 4 transforms by the same seat. |
| ATL-11 | SFE C3: delay ladder builds delay invariance (11/12 read d8/d16 at 1.0; direct search d8 0/6) | campaign headline | false_positive for "delay memory"; ruler_insufficiency + world_insufficiency | Y | U | N | N | P | P | P | Held-out delays solvable by a first-input latch; CW01 P-F02 on the same lineage: start-anchored, displaced only by an idle tick before the first PUT (IMPL). Artemis R-22 (10/11 latch) is an unverified worker claim. |
| ATL-12 | PROTEUS-46 "coordinated change with no intermediate the probe can see" | CLIFF_SURVIVES / FALSIFIER_FAILED; basis of a 299,991-echo suppression | search_insufficiency + ruler_insufficiency | P | Y | U | N | N | N | N | Probe horizon 3, strict improvement only (IMPL). 5-edit neutral path exists in quick mode; full run timed out; population search never reached 6/6 (REPORTED). |
| ATL-13 | Proteus VM "length protects" / C4 cliff | MIXED / headline | ruler_insufficiency (count-fixed geometry) | Y | U | U | N | P | N | N | 4/7 CW01 damage claims vanish, 2 shrink under qualified Bernoulli(f); operand softness survives (REPORTED, verifier-confirmed). Cliff never re-read. |
| ATL-14 | C5 "flat elite: selection does not climb these worlds" | operator-accepted negative | search_insufficiency (budget) / statistical_insufficiency | P | U | U | P | N | N | N | Deep Frontier at 60k evals: every N climbs (.479-.562 vs .382), but in-sample training reward, 12 runs, some seeds start at .396 (REPORTED). |
| ATL-15 | PTE: plants beat champions (.999 vs .755; lag-2 plant 1.000 vs 0/4 searches) | H6 "search reachability, not physics" | search_insufficiency (S proven by construction) | Y | Y | P | P | P | N | P | Demand demonstrated is latch/FSM sized. Needle size never measured, so "search vs landscape" undetermined. |
| ATL-16 | Cosmos C0/C3 laws | C0 RESTRICTED; C3 KILLED before holdout | false_positive (law restates planted certificate) + world_insufficiency (authored economy) | Y | n/a | N | P | Y | N | N | Zero-parameter rule 104/120; ties are non-significant, power of the attack untested (IMPL RESULTS.md). |
| ATL-17 | Hecate "zero UNFAMILIAR mechanisms" | instrument result | ruler_insufficiency | P | U | U | N | N | N | N | Detector UNFAMILIAR on 0/32 known-alien rules; 2026-10-01 CORR (scrubbed inputs; R1 holds on 24) (IMPL). |
| ATL-18 | Artemis R-11 census of silence-bearing gates (37/94 never fired) | census result | instrument_positive (meta-instrument) | Y | n/a | n/a | P | n/a | N | n/a | One seat, same-family readers; frame chosen by the seat. |
| ATL-19 | Aether "substrate lacks propagation" (one-bit footprint ~1 site) | measured physics negative | true_negative scoped to one energy regime; world_insufficiency for generality | Y | U | n/a | P | P | P | N | Exact twin assay; horizon 500 -> 10,000 ticks robust; content signature failed its positive control; ~93% frozen bytes (REPORTED). |
| ATL-20 | NPE "1,031 spontaneous replicators" -> 57 -> ~2 | FALSIFIED | implementation_defect + ruler_insufficiency | Y | Y | P | N | N | N | N | 910 were splice artefacts (fidelity read after the variation operator); P-11 passes painters (IMPL FINDINGS ARC3 block). |
| ATL-21 | NPE C-A3-INTERNALIZE: 8/144 runs internalize register initialization | CONFIRMED (single originator) | survives_as_anomaly | Y | Y | P | P | P | N | P | No planted-transplant control; BEE rebuild did not reproduce (never measured the same object) (REPORTED; source limits IMPL). |
| ATL-22 | CW01 cycle 7/8 "regime register present but causally inert" | promoted reading | false_positive (in-sample lookup), CORR by CW01-D089 | Y | U | U | N | N | N | P | Only "register transplant changed 0% of answers" stands (IMPL). |
| ATL-23 | ASAL: 9 GENUINE crossers among 105 (best crosser METRIC_EXPLOIT) | buried under negative headline | survives_as_anomaly (observer-bound) | P | U | U | P | N | N | N | CLIP OE score rewards turbulence (garbage 0.8303); 3G3an margin 1.1 sd; executed subset 395/1,045; S2_135 descends from 3G3an (REPORTED verifier). |
| ATL-24 | Nyx MECH-ASAL-OE-SCORE "EVIDENCE_SUPPORTED, OBSERVER_STABLE" | registered mechanism | instrument_positive (reconstruction fidelity only) | Y | n/a | n/a | P | n/a | P | N | Observer stability = native Flax vs torch reconstruction of the same CLIP model (Spearman 1.0); 0 transplants accepted (IMPL MECHANISMS.json). |

---------------------------------------------------------------------------------------------------------------
## 5. Buried signals: informative geometry or artefact? (Atlas BUR A1-A12 and selected B-F)

| Atlas id | observation | my reading | why |
|---|---|---|---|
| A1 | BEE CARRIED 0/24 vs ZERO 10/24 | ARTEFACT as cross-engine support | founders selected ZERO_DEPENDENT by construction (IMPL PREREG D1) |
| A2 | transplants copy but lose competence | INFORMATIVE GEOMETRY (with fixes) | same-world same-task arm still 8/11 at 0.0; needs paired ever/final readout, sham transplant, and copy-path overlap measure (FR-6) |
| A3 | equal-compute N scaling: every N climbs | WEAK, mostly artefact-prone | in-sample reward, 12 runs, seed-start above parent; but the geometry (budget x N with held-out readout) is exactly what Phase 3 needs |
| A4 | 5-edit duplicate-and-diverge path crosses PROTEUS-46 cliff | INFORMATIVE as an existence witness against the probe | probe horizon 3 (IMPL); the witness proves S and shows ruler/search insufficiency; rate unknown |
| A5 | n = 1 SELF-free donor became 95.7% of competent donors | INFORMATIVE calibration specimen | anomaly right, ruler wrong; seat corrected the ruler at once (verifier) |
| A6 | neutral walk reaches competence at ~soup rate (ratio 1.75, p .20) | INFORMATIVE geometry, unrun | soup-vs-random-walk baseline (WP-9, ~9 CPU-h) decides whether "ecology" adds anything to search |
| A7 | 9 GENUINE ASAL crossers | ARTEFACT-LIKELY | CLIP-observer-bound, weak margin, non-independent |
| A8 | PTE present-but-unswapped traffic (80-95%) | ARTEFACT as a law; INFORMATIVE only with a baseline | one champion; readout arithmetic reads only the last wake window (verifier); needs random-program denominator (FR-10) |
| A9 | 34/36 random questions CONSEQUENTIAL | ARTEFACT (saturated measure) | "CONSEQUENTIAL is too permissive" (verifier) |
| A10 | 9% of BEE births written by partner code excluded from SR | INFORMATIVE instrument correction | location ruler vs material; r038751 27,083/28,163 own material vs r016299 17,501/38,825 |
| A11 | Cosmos non-certificate atoms | WEAK | exploratory; authored worlds |
| A12 | Aether energy 2-cycles enriched 1.58x | WEAK candidate | seat says "a resource-transfer mechanism, not a structure-forming process"; never lesioned |
| B4 | X-ACQUIRE 9-15% descendants competent where founder is not; C-SWAP missed by p | INFORMATIVE | descendant acquisition is a developmental-style transition; one event short of frozen bar |
| B6/B7 | E-003 per-class defect 0.242; parasite class 0/120 vs 117/120 | INFORMATIVE | pooling hides class structure; argues for per-class readouts |
| B8 | BEE 26 unmodified random tapes replicate | ARTEFACT-LIKELY | pseudo-replicated origins; ISA differs from census VM |
| C1/C2 | exaptation gradient with walk depth; insertion "rescued operator" 102/0 | INFORMATIVE small signals | operator geometry and walk depth are controllable variables |
| C4 | GW sham beats scratch (+1.40); scale-only +2.10 | INFORMATIVE negative geometry | initialization scale masquerades as transfer; sham controls exposed it |
| C5 | Apollo crossover default 0.0 vs 6.1%/pair recombinant | INFORMATIVE (cheap) | a configuration default suppressed the only improving operator |
| D2/D3 | PTE latency -1 improves; evolution works outside designed habitable zone | INFORMATIVE | champions not at their own optimum; evolution finds regions the hand design cannot |
| D6 | Tyche stored-fragment share rises with world diversity, adaptation does not | INFORMATIVE if instrumented | latent option value possibly stored but unmeasured (capacity vs realization, Challenge 4e) |
| D7 | CW01 e07 raw retention doubled while ratio reads negative | INFORMATIVE ruler lesson | ill-conditioned ratios invert effects |
| F4 | 33 NEGATIVE/NULL experiments carry 30-102 measurements each, never mined | INFORMATIVE | the record's own buried layer |

---------------------------------------------------------------------------------------------------------------
## 6. Natural experiments and contradictions: which geometries are informative

Atlas tally of 16 contradictions by primary cause: ruler 5, world physics 5, search 2, terminology 2, representation 1,
intervention 1; substrate only once as secondary (REPORTED ATLAS_CONTRADICTIONS s0; verifier confirmed tally).
Terminology collisions confirmed in code by the verifier: "Z80" names three ISAs; "ATOMIC" is a BEE scoring mode and
an NPE write-back rule (REPORTED VERIFY_SYNTHESIS_2 #24-#26; the Archaeon half I confirmed, V1).

| nat. exp. | geometry | informative? | key confound |
|---|---|---|---|
| B2 copy primitive remove/cheapen/add | dose over encoding cost: impossible -> 5e-9 -> 1e-5 -> ~0.6 of donor runs, plus SHAM density control | YES, the strongest geometry in the record | one design family; rulers differ (census, SR, P-11) |
| B1 register reset ZERO/CONST/RANDOM/CARRIED | 4-arm separation of "clean state" vs "specific constant" | YES as design; outcome partly built-in | NPE ruler certifies from zeros; BEE founders ZERO_DEPENDENT; PTE zero is a fixed author choice |
| B3 write authority (ATOMIC, add vs replace, freeze, imports) | one switch per engine on who may overwrite | YES | different state in each engine; no variation ledger |
| B4 zero-parameter restatement | definition-as-predictor baseline | YES as a baseline, power UNKNOWN | never given a planted non-certificate law to fail on (FR-3) |
| B5 count vs fraction ruler | within-substrate ruler swap on the same programs | YES (clean, one VM) | only Proteus VM |
| B6 greedy vs neutral-accepting search | tie policy at fixed landscape | YES, never completed | budgets differ by orders; D002 full run timed out |
| B7 horizon extension | ever-state vs final-state readout at 1x and 20x | YES, unnoticed by seats | readout type decided verdicts more than horizon (4 engines) |
| B8 transplant/sham/scratch | moves material, tests competence transport | YES | only graphworld had a sham; Archaeon only had size-matched random graft |
| B9 energy at birth vs maintenance | equal total, different timing/contingency | YES, only BEE ran it cleanly | NPE energy lacks a YOKED twin |
| B10 labels vs material descent | label system vs material tracer on same births | YES (instrument geometry) | material tracers run on one run/campaign each |
| B11 present/decodable/unused | decode vs swap side by side | WEAK so far | one instrument class; CW01 leg withdrawn (D089) |

Cheapest decisive tests Atlas lists (all unrun at harvest; operator-gated; REPORTED costs are Atlas estimates):
C4-02/C4-08 re-score under Bernoulli(f) (< 4 core-h, data committed); greedy vs neutral walk (2-6 core-h); census
classifier on BEE's VM with LDIR on/off and undefined=HALT (2-4 core-h); phase-indexed swaps on PTE M2 (minutes);
restatement attack on a planted non-certificate law (hours).

---------------------------------------------------------------------------------------------------------------
## 7. Instruments with demonstrated (or demonstrated-absent) detectability

| instrument | what it detects | evidence of detectability | tag |
|---|---|---|---|
| Archaeon copier census classifier | exact/near/gated copiers in random tapes | two-sided: 0 on z80, 96/1e7 on vmcopy with same classifier; stage-2 heritability check 128/176 | IMPL archaeon/z80atlas/census/RESULTS.json |
| Qualified Bernoulli(f) damage ruler (CW01) | robustness without count-geometry bias | qualified on 126 programs; removed 4/7 claims and preserved operand softness (could return both outcomes) | REPORTED, verifier-confirmed |
| CVT-R (Artemis) | transmission of parental variation over 2 generations | only certificate validated on a ground-truth panel; 17-28% of P-11-competent donors fail it | REPORTED |
| P-11 | causal construction of a victim half | demonstrated FALSE POSITIVE on painters (certified 0.90-1.00) | IMPL FINDINGS ARC3 block |
| Archaeon taint VM / causal lens; bee_tracer; NPE dense_taint | per-byte material descent | T-003 agreement 1.0 with an independent Z8 shadow tracer; but lens matched behaviour only 3/48 on PTE; bee_tracer ran on one run | REPORTED |
| PTE plants run through the arm's own code (W-K) | separates unreached arms from true nulls | J .70; plants .999-1.000 where champions .59-.755 | REPORTED (plant numbers IMPL) |
| NPE C9-H1R gate positive control | whether a gate penalises correct readers | correct reader scores identically under the gate | IMPL FINDINGS E-9 |
| BEE YOKED twin | contingency vs total resource | 1 vs 67/150 extinction at equal totals | REPORTED, verifier-confirmed |
| Hecate novelty detector on 32 known-alien rules | UNFAMILIAR mechanisms | demonstrated NOT to detect (0/32; Wilson upper .107) | IMPL hecate/autopsy/AUTOPSY.md |
| Zero-parameter definition rung | law restates its label/certificate | fires on C0/C3/WTP-03 cases; power on a non-restating law untested | IMPL Cosmos RESULTS.md (power UNK) |
| Artemis R-11 census method | whether absence gates were ever shown to fire | 120 rows, path@sha evidence, 10-row second read | IMPL REPORT.md |
| ASAL CLIP OE score | embedding novelty of frame sequences | observer-stable across reconstructions, but garbage scores 0.8303 and metric exploits dominate crossers | REPORTED; IMPL MECHANISMS.json |
| Cross-family blind re-derivation | author-family priors in syntheses | recovered F1-F3 and R6, not F4-F6 | REPORTED handoff s7 |
| Nyx recurrence calibration pairs (RC-01 identical by descent, RC-15) | organ identity across fossils | DESIGNED but not run: "SOURCE_READ only. Nothing here has run" | IMPL nyx/atlas/out/RECURRENCE_CANDIDATES.json |

---------------------------------------------------------------------------------------------------------------
## 8. Failure shapes (fossil record of how the apparatus failed)

| class | direction | instance | cite |
|---|---|---|---|
| ruler_insufficiency | false negative | ruler cannot return the opposite outcome (BEE K3 founder snapshot 0/93; Tyche H1 3 valid worlds < 4) | ATLAS_CROSS_ENGINE_SYNTHESIS F1 (REPORTED, verifier-confirmed) |
| ruler_insufficiency | false positive | P-11 certifies construction, so painters pass | roles/Nestor/FINDINGS.md ARC3 (IMPL) |
| implementation_defect | false positive | detector read after the variation operator: 910/1,031 "replicators" were splice products | FINDINGS (IMPL) / nestor digest |
| ruler_insufficiency | inflation and deflation | location label pc < L used as "own code"; parent-chain labels 8-42x genetic counts | ATLAS_CONTRADICTIONS B10 (REPORTED) |
| ruler_insufficiency | false positive | count-fixed damage ruler manufactures "length protects" | CW01 cycle 5 (REPORTED) |
| search_insufficiency | false negative | 3-step strict-improvement probe declares "no intermediate" | proteus/round2/falsifier_46.py (IMPL) |
| ruler_insufficiency | false positive | in-sample lookup over near-unique values scores 1.0 | CW01-D089 (IMPL) |
| implementation_defect | no test | arms never wired (C9-D16: runner never passed gate/cost; four arms identical) | FINDINGS E-9 (IMPL) |
| world_insufficiency | false competence | guessing shortcut carries C9 competence; latch carries delay ladder | FINDINGS E-9; CW01 cycle 5 (IMPL) |
| world_insufficiency | designed-in dissociation | task bolted onto copy loop; tasks inert under IMPLICIT | GROUNDING s6 (IMPL) |
| world_insufficiency | false positive | world-made copies (POLLINATION v1) produced the topology effect | GROUNDING G7P1 (IMPL) |
| world_insufficiency | false positive | authored universes carry planted economics that the law restates | Cosmos RESULTS.md (IMPL) |
| ruler_insufficiency | false negative | novelty detector cannot reach its target class | Hecate AUTOPSY (IMPL) |
| ruler_insufficiency | readout swap | ever-reached vs final-state decides verdicts; source best-ever vs transplant final | ATLAS_CONTRADICTIONS B7; adjudication s C (IMPL) |
| statistical_insufficiency | false negative | origination nulls 3 vs 3 at n = 40 cannot detect 2x | ATLAS synthesis s2 R12 (REPORTED) |
| statistical_insufficiency | false positive | pseudo-replicated origins (160 origins, 83 distinct seeds, 45 duplicates) | BEE ERRATA E2 (REPORTED) |
| provenance_defect | false replication | deterministic replays counted as replications; independent re-measurement moved counts 1,031 -> 57 -> ~2, 26 -> 0, 160 -> 103 | synthesis F7 (REPORTED) |
| provenance_defect | false convergence | vocabulary migrates across seats in 0-2 days; F5 "independent" pairing was one seat's citation chain | VERIFY_SYNTHESIS_2 #19 (REPORTED) |
| ruler design | false negative | frozen bars set before the attainable range was known (>= 20 cases); "DESIGN UNREACHABLE" | ARTIFACT_MAP D2 (REPORTED) |
| ruler_insufficiency | confound | ruler and treatment share a state (COMPETENT ruler certifies from zeros) | FINDINGS P2 (IMPL) |
| organism_insufficiency | false null | intervention delivered to organisms that cannot act on it (C-ATOMIC C2 on non-copiers) | FINDINGS E-10 (IMPL) |
| implementation_defect | false negative | common-mode infrastructure loss (Fabric timeouts with 0 bytes; >1 MiB artifacts silently dropped) | ARTIFACT_MAP A (REPORTED) |
| provenance_defect | no information | engine-level primitive tags make the combination index null by construction | ATLAS_ONTOLOGY s0 (REPORTED, verifier live SELECT) |
| ruler_insufficiency | false positive | statistic with no null (Pollux rank correlation recurs under independence up to 0.94) | engine/necropolis/monsters/FRANK-004.monster.json (IMPL) |
| provenance_defect | false signal | verdict computed over a ledger whose outcome column carried pipeline state (Erebos) | engine/necropolis/monsters/FRANK-003.monster.json (IMPL) |

---------------------------------------------------------------------------------------------------------------
## 9. The external ecosystem catalogue (roles/Atlas/catalog/)

IMPL (tabulated ECOSYSTEMS.jsonl):
- 365 rows: 361 external + 4 Prometheus. README (currency 2026-09-19) says 352/4; the file has grown. Pointers only;
  nothing downloaded. url_status is the surveyors' own.
- Prometheus rows: only Deep Frontier, NPE CW01, NPE GraphWorld, SFE campaigns. BEE, PTE, Aether, Cosmos, the NPE
  pair-tape line and Hecate are absent. All 4 have environment generation fixed or procedural; none co-evolves worlds.
- organism.development: True 72, False 252, null 41. The True rows sit mostly in CA/self-organization (23) and
  embodied morphology (15) clusters: this flag is morphogenesis (growth from a seed), not lifetime cognitive
  development. A crude keyword pass for lifetime learning/plasticity/Hebbian/ontogeny hits 4 rows (project-origin,
  derl, polyworld, revolve2) (INFER, crude).
- environment_generation: fixed 227, procedural 41, none 35, co-evolved 26, learned world model 12, LLM-generated 8.
- open_endedness_evidence parses as "none claimed" in about 233 rows (crude parse, INFER).
- 26 rows carry internal_coverage pointers (techne specimens, aporia dossiers, archaeon template inbox).
- Atlas's 2026-09-19 cross-ecosystem proposal recommended BFF/cubff, Flow-Lenia, JaxUED/ACCEL; its 12 experiments are
  all PROPOSED (IMPL roles/Atlas/proposals/2026-09-19_cross_ecosystem/EXPERIMENTS.jsonl).

What it can and cannot show: it locates analogous systems and code; it cannot show that any external system
demonstrated a mechanism, because key_claims and OE evidence are surveyor summaries (REPORTED). The schema has no
fields for world cognitive depth, ruler validation, development-within-lifetime, or curriculum: precisely the Phase 3
axes. Its densest cells (LLM program search 25; UED grid policies 22; machine-code soups 17) show the field's
mass; the program sat in two cells (program_memory x machine_code/tape, graph x policy).

---------------------------------------------------------------------------------------------------------------
## 10. Nyx organ/mechanism atlas, Techne fossil vault, Necropolis

Nyx (IMPL nyx/atlas/out/*.json, nyx/atlas/gates/MECHANISMS.json):
- 123 fossils available, 122 inspected, 118 decomposed; 549 candidate fragments, 485 accepted organs; cut depth max 1
  for 105 fossils (DEEP 45, COARSE 73).
- Evidence grades: SOURCE_READ 542, METADATA 4, EXECUTED 1, INTERVENED 2. "runnable_organs: UNKNOWN (no organ has been
  run in isolation; 1 fossil-level ablation exists)"; fingerprinted organs 0; behavioral fingerprints n = 2, both one
  Spin priority-inversion ablation.
- All 20 coverage dimensions (input topology ... temporal horizon) have measured = 0; e.g. hidden_state read for 24 of
  549 organs, adaptation read for 32. "a dimension with measured == 0 is UNMEASURED for the whole atlas".
- 0 blind cuts: "the measure of Nyx's human-prior dependence is EMPTY, not zero".
- Scoreboard: 7 mechanisms registered, 3 evidence-supported, 0 falsified, 0 successful independent transplants, 0
  survived transplant. Mechanisms are from ASAL (OE score, frame sampling), particle filters (ESS trigger), POET
  (novelty estimator, minimal criterion, FIFO discard), Avida (ancestry retention). One POET mechanism is
  "EXECUTED_STRUCTURAL_IDENTITY ... zero predictions were tested".
- Residue: EXPLAINED 29, PARTIALLY 58, LARGE_RESIDUE 30, CUT_INSTRUMENT_INSUFFICIENT 5 of 122.
- 15 recurrence candidates include designed calibration pairs (RC-01 identical by descent; RC-15) and cross-domain
  pairs (e.g. lmdb reclamation vs epoch-based reclamation). None ran ("SOURCE_READ only").
Reading: a large, careful taxonomy of human software organs built by LLM reading. It has the right ladder (read ->
wind tunnel -> transplant) but almost no rungs above reading were climbed. Relevance to Challenge 3: an organ
vocabulary derived from human artifacts by an LLM, with no blind-cut measure, is the rear-view-mirror risk in
instrument form.

Techne fossil vault (IMPL techne/fossils/CATALOG.json, README.md):
- 189 fossils (schema techne.fossil.catalog/1, written 2026-09-30); run_status RUNNABLE_CONTAINER 82, NATIVE 14,
  EMULATED 8, HISTORICAL_TOOLCHAIN 2, NOT_ATTEMPTED 69, SOURCE_ONLY 13; oracle_backed yes 84; intervention_ready yes
  66, unknown 123. 39 rows are ASAL rollout specimens (era 2026-09-18). Bodies are host-local (body_present_on_this_host
  null for all 189 in the committed catalogue). Techne acquires and proves runnable; Nyx decomposes.
- Reading: a runnable-machinery foundry with receipts; it demonstrates "runs", not "mechanism".

Necropolis (IMPL engine/necropolis/):
- ROSTER 48 historical v1 agents (tool 25, daemon 9, operator 6, healthcheck 4, pipeline-stage 4): research
  infrastructure, not organisms.
- 7 dossiers: acheron NEEDS_MORE_EVIDENCE, argos ORCHESTRATION_FAILURE, coeus MEASUREMENT_FAILURE, erebos / hephaestus /
  nous / pollux NO_FAIR_TEST_ON_RECORD. ORGANS.jsonl 92 rows: source fair_test UNFAIR 90, UNDETERMINED 2;
  executed_by_necromancer True 39, False 10, unset 43 (README's "13 of 39 executed" is stale).
- COUNTERFACTUAL_HISTORY 41 mistakes, fair_test UNFAIR 41/41; corrected cause DESIGN_ERROR 22, MEASUREMENT_ERROR 11,
  INSTRUMENT_ERROR 8; layers INTERPRETATION 8, DESIGN 6, INSTRUMENTATION 6, MEASUREMENT 6, CONFIGURATION 5, ECOSYSTEM 4,
  IMPLEMENTATION 3, EXECUTION 3; post_repair_behaviour unset 37, PROPOSED 4.
- 5 monsters (FRANK-000 chimera; FRANK-001..004 one-change repairs), all PROPOSED, none run.
- Reading: no Necropolis-examined agent ever received a fair test; the dataset is "why Prometheus killed things
  incorrectly", which corroborates F1 at the v1-infrastructure layer.

---------------------------------------------------------------------------------------------------------------
## 11. PHASE3_CHALLENGES.md against the fossil record

docs/phase3/PHASE3_CHALLENGES.md (IMPL; drafted by Harmonia 2026-10-01; "not a plan or a preregistration") names four
challenges: (1) scientific legitimacy via a per-result Q/S/W/R/B/Rep/M profile, nulls carrying their apparatus, ruler
error rates; (2) cognitive sufficiency: organizational scales, an affordance floor with capacity proofs, worlds whose
optimum is not reactive (reactive-ceiling, surface-memorization baselines, depth certificates), reinterpretation of
old nulls; (3) epistemic escape: LLMs as mutation sources only, Reality-layer authority, the anti-gravity rule with its
guard, calibrated multi-model disagreement; (4) developmental adequacy: capacity vs realization, structural development
affordances, the ladder as curriculum, trajectory measurement (structural diff, retention, reuse, savings, transplant,
divergent mechanisms), developmental controls (same-compute direct, shuffled order, frozen development).

Where this group's evidence supports the document:
- Challenge 1: R-11 census (37/94; 0 blind injections) and the Necropolis UNFAIR-on-every-dossier result support
  "rigorous procedure, inadequate apparatus" directly. The Atlas cross-family check is a working prototype of 1e
  (external validation) at small scale.
- Challenge 2: every task demand visible here is latch/lookup/FSM sized, and plants of 4-16 instructions solve them.
  The document's "depth certificate" and "reactive-ceiling baseline" would have flagged C3's delay ladder (latch
  passes) and C9 (guessers reach 0.2) before running.
- Challenge 3: Hecate is the in-house demonstration of the failure the document fears (LLM detector calls 32/32 alien
  rules familiar; lookup table passes the novelty rule, AUC .844-.852 REPORTED). Nyx's 0 blind cuts means its organ
  vocabulary's human-prior dependence is unmeasured.
- Challenge 4: the record contains exactly one curriculum-vs-direct contrast in this group (C3 ladder vs matched-budget
  direct search, d8 0/6) and its mechanism looks like a latch. The document's 4d trajectory questions (what changed,
  localization by ablation, retention, savings) would have been needed to see that. NPE's "lineages internalize
  register initialization 8/144" and X-ACQUIRE "descendants competent where founder is not" are the closest fossils to
  developmental transitions, both at the heredity layer, not the cognitive layer.

Where the record cautions the document:
- "Substrate capacity proof = a hand-built organism" exists already in PTE (plants) and Z80 (seeded copiers); the
  record shows a plant is necessary but not sufficient: it proves S, not reachability, and it shares author with the
  search ("plants beat champions" compares the author's design skill with the author's budget; ARTIFACT_MAP s C).
  Needle size (density of solvers at plant length) is the missing companion measurement (FR-4).
- Affordance floors interact with conventions the authors do not notice (zero-initialized registers in NPE, BEE,
  Archaeon and PTE; NBR = 128 in Archaeon). A floor needs a convention-swap control (CONST/RANDOM init, moved
  addressing base) or evolved machinery will depend on the convention (B1).
- The anti-gravity rule's guard (behavioural + causal gates) assumes calibrated rulers; 61.7% of absence-read gates
  lacked a floor and only 1 had a graded curve. The guard is only as good as R.

---------------------------------------------------------------------------------------------------------------
## 12. Design implications for Phase 3 (each tied to evidence)

1. Ship every world with a constructive plant AND a needle-density measurement at plant length (census-style random
   sampling plus edit-path sampling). Evidence: Archaeon census separated 0 vs 96/1e7 on one classifier; PTE plants
   beat champions; "search vs physics" stayed undetermined everywhere a density was not measured (FR-4, ATLAS R3).
2. Certify world demand against trivial solvers before running: a guesser baseline, a first-input latch baseline,
   a constant twin, a lookup table, and a perturbation probe (idle/noise tick before first input). Evidence: C9
   guessers; C3 start-anchored delay readers; PTE 4-instruction latch .999.
3. Put the capability on the reproduction/persistence path, or measure the coupling fraction (task bytes on the
   executed copy path). Evidence: transplants persist without competence; imports take over regardless of competence;
   endogenous reproduction antagonises task code 178 vs 2; tasks inert under IMPLICIT.
4. Use contingency-at-equal-total (YOKED) as the standard pressure control. Evidence: BEE ON vs YOKED 1 vs 67/150 is the
   one clean disentanglement of selection from resource in the record.
5. Every verdict-bearing ruler carries an attainable verdict set, a same-substrate planted positive, a matched negative,
   a floor, and preferably a graded curve and blind injection. Evidence: R-11 (37/94; 1 curve; 0 blind).
6. Record search policy (tie rule, horizon, population, budget) as first-class experiment fields and always include a
   neutral-accepting arm and a budget-scaling arm with held-out readout. Evidence: PROTEUS-46 3-step strict probe;
   C5 vs Deep Frontier.
7. Keep a variation-source ledger (operator mutation, partner write-back, splice, world copies) before interpreting
   any "mutation rate" manipulation. Evidence: NPE erosion ~25x nominal; C-ATOMIC 46/80 vs 1/80; splice made ~88% of
   apparent replicators.
8. Report ever-state and final-state readouts together, and compare like with like across arms. Evidence: B7 in four
   engines; transplant source best-ever vs final (V5).
9. Use fraction-geometry damage operators and rulers, or show count/fraction equivalence. Evidence: 4/7 claims vanish.
10. Heredity claims need a material-grade tracer validated against a second tracer; labels inflate 8-42x and 33% of BEE
    births are NOT_IDENTIFIABLE (REPORTED).
11. Count independence per (ruler_id, substrate lineage, author family, originating seat); no convergence counts
    unless all four differ. Evidence: Atlas meta-finding; F5 citation chain; "Z80" triplet from one directive.
12. Include at least one substrate with different addressing and initialization conventions from the start (relative
    or content addressing; noise-initialized registers). Evidence: every copy-dependence and init-dependence fact sits
    on zero-init absolute-address conventions chosen by one author family (ALIEN-2).
13. Curriculum claims need the developmental control set plus mechanism localization; an out-of-distribution score is
    not evidence of depth. Evidence: C3 delay ladder result.
14. Calibrate any novelty or familiarity instrument on mechanically established alien and familiar items before use;
    measure blind-cut dependence for any organ vocabulary. Evidence: Hecate R1; Nyx 0 blind cuts.
15. Treat mechanism labels as provisional until an independent re-measurement (not a replay) holds. Evidence: NPE labels
    turned over in 1-3 days; independently re-measured counts moved several-fold.
16. Tag interventions per experiment arm, not per engine, in any program index. Evidence: Atlas combination table null
    by construction.

---------------------------------------------------------------------------------------------------------------
## 13. Open questions (unresolved in the record)

- Does the copy-primitive/zero-addressing dependence survive a substrate with no absolute addressing? (FR-1/ALIEN-2;
  never run.)
- What is the needle density of PTE lag-2 and Proteus two_key 6/6 at plant length versus evaluations actually spent?
- Does the zero-parameter restatement attack ever fail on a planted non-certificate law (power)? (FR-3; unrun.)
- Are the C3 delay-general organisms latches (Artemis R-22 10/11 is unverified; CW01's census is suggestive)?
- Is task competence ever on the copy path in the 39 transplants (TH-015 executed-path overlap)? (FR-6.)
- Does the soup beat a neutral random walk for first appearance (WP-9 never run)?
- Does "present != used" exceed a random-program baseline (FR-10)?
- How far does the cross-family re-derivation hold when a non-Claude model selects rows from raw seat files (FR-11)?
- The Hecate CORR of 2026-10-01 (scrubbed Part B inputs) postdates the Atlas harvest: has any Atlas statement relying on
  the original Part B been updated? (UNK.)

---------------------------------------------------------------------------------------------------------------
## 14. Files opened (this reader)

roles/Atlas/inference_harvest_2026-09-30/ATLAS_CROSS_ENGINE_SYNTHESIS_2026-09-30.md
roles/Atlas/inference_harvest_2026-09-30/ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md
roles/Atlas/inference_harvest_2026-09-30/ATLAS_CONTRADICTIONS_AND_NATURAL_EXPERIMENTS.md
roles/Atlas/inference_harvest_2026-09-30/ATLAS_ONTOLOGY_GAPS_VNEXT.md
roles/Atlas/inference_harvest_2026-09-30/ATLAS_OPERATOR_FRONTIER.md
roles/Atlas/inference_harvest_2026-09-30/INFERENCE_HARVEST_HANDOFF.md
roles/Atlas/inference_harvest_2026-09-30/workers/VERIFY_DRAFTS_1.md
roles/Atlas/inference_harvest_2026-09-30/workers/VERIFY_SYNTHESIS_2.md
roles/Atlas/inference_harvest_2026-09-30/workers/ARTIFACT_MAP.md (s1, A-C, F-J)
roles/Atlas/inference_harvest_2026-09-30/workers/digests/{ananke_pte_tyche,cosmos_aether_hecate,nestor_npe,ensorain_bellerophon,archaeon_sfe_proteus}.md (s9 only)
roles/Atlas/inference_harvest_2026-09-30/workers/xfamily/RESP_moonshotai_kimi-k3.md (headings only)
roles/Atlas/catalog/README.md, SCHEMA.md, ECOSYSTEMS.jsonl (tabulated)
roles/Atlas/proposals/2026-09-19_cross_ecosystem/ECOSYSTEM_CANDIDATES.md (head), EXPERIMENTS.jsonl (tabulated)
docs/phase3/PHASE3_CHALLENGES.md
nyx/atlas/gates/MECHANISMS.json; nyx/atlas/out/{ATLAS_COVERAGE,DEPTH_MAP,BLIND_CUT_COMPARISON,RECURRENCE_CANDIDATES,UNEXPLAINED_RESIDUE,FOSSIL_ANATOMY,BEHAVIORAL_FINGERPRINTS,PRESSURE_CATALOG,ORGAN_CATALOG}.json (summarized)
techne/fossils/README.md; techne/fossils/CATALOG.json (tabulated)
engine/necropolis/README.md; ROSTER.jsonl, ORGANS.jsonl, ORGAN_NOTES.json, COUNTERFACTUAL_HISTORY.jsonl (tabulated); dossiers/*.dossier.json (disposition fields); monsters/FRANK-00*.monster.json (status/_README)
roles/Nestor/FINDINGS.md (l.250-340, 440-535)
roles/Nestor/campaigns/cw01-2026-09-17/DEFECTS.jsonl (line 90)
roles/Nestor/campaigns/cw01-2026-09-17/loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md (l.50-64)
archaeon/z80atlas/census/RESULTS.json; archaeon/z80atlas/vm.py (l.1-40, 95-115)
archaeon/z80atlas/postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.md (s C)
archaeon/campaign3/CAMPAIGN_REPORT.md (l.36-50, 140-162)
roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md (s1, s3, s4, s6 excerpts)
roles/Bellerophon/repl_2026-09-30/PREREG.md (s1, D1-D3)
roles/Artemis/selftest/runs/R-11/REPORT.md (s1-s3)
proteus/round2/falsifier_46.py (l.31-32, 100-135)
hecate/autopsy/AUTOPSY.md (l.1-30)
roles/Cosmos/research/reviews/COORD_AUDIT_C3_2026-09-29.md (l.30-45); roles/Cosmos/research/RESULTS.md (l.15-40)
roles/Ananke/research/workers/W-H/REPORT.md (grep l.42, 85); roles/Ananke/research/workers/W-L/REPORT.md (grep l.63)
