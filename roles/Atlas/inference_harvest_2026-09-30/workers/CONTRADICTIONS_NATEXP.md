# Atlas independent synthesis -- CONTRADICTIONS and NATURAL EXPERIMENTS (2026-09-30)

Analyst: fresh-context, read-only. Corpus: the seven digests listed in CORPUS_NOTE.md, all read in full, plus spot
verification in F:/Prometheus-worktrees/atlas-base-role (origin/main 737d9209b at read time).
Layer tags: [RAN] executed; [OBS] instrument output; [CON] a seat's words (seat named); [AD] = ATLAS_DERIVED, my
inference, a hypothesis only. Every number carries the tag of its source row; I never promote a layer.
Digest short names: NPE = nestor_npe.md; ENS/BEE = ensorain_bellerophon.md; PTE = ananke_pte_tyche.md;
CAH = cosmos_aether_hecate.md; ASP = archaeon_sfe_proteus.md (+ _part_proteus, _part_sfe); HAR =
harmonia_rulers_and_satellites.md; IDX = atlas_index_and_history.md. Repo pointers are path@sha as the digests give them.

Three facts I verified in the repo myself, because several items below turn on them:
- V1. Archaeon's "z80" is NOT the BEE VM. archaeon/z80atlas/vm.py decodes op = byte & 31; opcode 20 COPY
  (mem[C]=mem[B]; B++; C++) "is NOP unless copy_prim"; registers are set to [0,0,0,0] at the start of every execute().
  So Archaeon stratum "z80" = no copy instruction at all; "vmcopy" = a one-byte-per-step COPY that must be looped.
  BEE's prometheus/z80atlas/vm.py has LDIR (block copy, ablatable ldir=off/cost4) and undefined opcodes execute as NOP
  (ablatable undefined=HALT). [OBS, code read]
- V2. BEE's "ATOMIC" (prometheus/z80atlas/world.py:49 `scoring: str = "ATOMIC"`) is a TASK-SCORING mode. NPE's ATOMIC
  (C-ATOMIC) is a WRITE-BACK rule for pair tapes. Same word, unrelated primitives. [OBS, code read]
- V3. BEE REPL PREREG (roles/Bellerophon/repl_2026-09-30/PREREG.md s1, s3 D2): BEE's historical physics is ZERO registers
  on every execution; the CARRIED axis was added for the rebuild; "Under plain CARRIED in BEE, zero-dependent founder
  lineages die out: PILOT 2 gave 0/24 ... ZERO gave 10/24". ENVGATE-02 VERDICT: R128 = "128 only" restored, 5
  establishments vs BAND0 (all blocked) 5 vs U 24; "Something outside the frozen window model carries establishment when
  the window is closed." [OBS]

---------------------------------------------------------------------------------------------------------------------

## TASK A -- CONTRADICTIONS (16)

Format per item: EVIDENCE (both sides) / THEORY predicting agreement / RECONCILIATIONS / CLASSIFICATION (primary,
secondary, with reasons) / SMALLEST SEPARATING TEST.

### A1. "Random Z80 tapes do not copy" (Archaeon) vs "unmodified random Z80 tapes replicate" (BEE)   [cross-engine]
- Side 1 [OBS]: COPIER-CENSUS-01, isolated VM, empty neighbour window, all 256 inputs: z80_32 0 exact / 0 near in 1e7;
  z80_64 0 in 2e6; vmcopy32 96 exact per 1e7 (gated share 0.9896); vmcopy64 9 exact. [CON Archaeon] random-tape
  replication is a property of the supplied primitive. (ASP row 7; z80atlas/census/RESULTS.json@c5067fac6)
- Side 2 [OBS]: BEE grounding recount E1: of 160 spontaneous origins, the first self-replicating writer was an INITIAL
  organism in 57/160, and in 26 of those "it replicated with its unmodified initial random tape"; G1 pooled 55/2,400
  runs = 2.3% spontaneous SR. Artemis R-26 quotes "null 4.5e-5 per tape" (#877; meaning of that null not stated).
  (BEE ERRATA_2026-09-29 E1; GROUNDING s1)
- Theory predicting agreement: the D_Z80_SYNTHESIS "three independent Z80 worlds" premise and the Atlas primitive
  `copy_mechanism` as one axis; the ENGINE_LANDSCAPE line "As a WORLD: NOT distinct" (ASP s8).
- Reconciliations: (a) different instruction sets: Archaeon z80 has no copy op (V1), BEE has one-instruction LDIR block
  copy; (b) different birth rulers: census = coverage >= 0.9 into an EMPTY window and exact; BEE SR = own-code (pc < L,
  location-based, #741) birth events in-world with partner bytes present, so partial/foreign-assisted births count;
  (c) BEE NOP slide lets random tapes run into LDIR setups the census VM cannot express; (d) BEE origins are
  pseudo-replicated (160 origins, 83 distinct seeds, 45 exact duplicates, ERRATA E2), so "26" overstates independent tapes.
- Classification: PRIMARY terminology -- the word "Z80" names three different VMs, and the contradiction disappears once
  the ISA is named (V1). SECONDARY substrate -- the copy primitive's granularity (none / per-byte / block) is the actual
  varied factor; ruler differences (b) are real but cannot turn 0-in-1e7 into ~1e-5.
- Smallest test: run Archaeon's census classifier (copier_census.py, unchanged) on BEE's vm.execute, G = 64, 2e6
  uniform tapes per arm, arms {ldir on, ldir off, undefined HALT}; also score the same tapes with BEE's COMPETENT_e
  (state_free.py) ruler. Predictions: substrate-only -> ldir on gives exact/near density O(1e-5), off gives 0 under
  both rulers; ruler-only -> census exact ~0 in all arms but COMPETENT_e fires on ldir-on; NOP-slide -> undefined=HALT
  drops density by >10x. Cost [AD]: ~2-4 core-h (Archaeon's input-skip makes most tapes one run).

### A2. Spontaneous self-replication: "CONFIRMED_CAUSAL" (BEE) vs "2 genuine of 57" (NPE) vs "0 de novo" (Archaeon)
- BEE [CON Bellerophon, GROUNDING s8]: "spontaneous own-code self-replication CONFIRMED_CAUSAL"; SR label holds
  1,414/1,425 on recert (Odysseus, HAR row 12).
- NPE [OBS]: 1,031 admissible -> 57 P-11 -> 2 genuine self-copiers (+1 context), 17 painters, 37 inert (NPE s3); 17-28%
  of P-11-competent donors fail CVT-R (#891).
- Archaeon [OBS]: 101,003 runs, spontaneous_replication 26 -> 0 after repair; DENOVO-01 0/80 (CI [0, .0451]).
- Theory predicting agreement: one directive, three Z80 soups; "copying is not heredity" is an Atlas MODERATE
  proposition that should apply uniformly.
- Reconciliations: (a) ruler: BEE SR = a birth by own-LOCATION code; NPE requires causal rebuild (P-11) and then
  transmissible variation (CVT-R); Archaeon requires a self-sustaining population; (b) substrate: BEE has block LDIR +
  NOP slide (A1), NPE LDIR/LDDR multi-byte encodings, Archaeon none/COPY; (c) world physics: NPE pair-tape write-back
  erosion ~25x nominal mutation (NPE C-ATOMIC) destroys copies after they occur; BEE writes children into cells;
  (d) BEE "SR" may include painter-like births that CVT-R would reject -- untested.
- Classification: PRIMARY ruler (three different definitions of "replicator"; no engine has applied another's ruler);
  SECONDARY world physics (write-back policy differs, see A5).
- Smallest test: apply CVT-R (Artemis prereg 77bc0dbce, the only certificate validated on a ground-truth panel) to BEE's
  83 distinct-seed origin genomes and to a 100-genome random sample of BEE SR-labelled births, and apply BEE's SR
  predicate to NPE's 57 P-11 survivors run inside BEE-style cells. Predictions: ruler-dominant -> BEE CVT-R pass rate
  falls well below the SR label's 99% (e.g. to NPE's 72-83%); substrate-dominant -> BEE passes CVT-R >= 95% while NPE
  genomes still fail. Cost [AD]: CVT-R ran on 140 genomes as one Artemis task; < 4 core-h.

### A3. Internalization of register initialization: NPE CONFIRMED vs BEE rebuild UNRESOLVED / NOT_REPLICATED
- NPE [OBS]: C-A3-INTERNALIZE 8 events / 144 runs (7 in ffa6); X-MAT 8/8 ENDOGENOUS_MATERIAL, median XENO share 0.020,
  MUT share 18-56% in 6/8; X-A3-WITHDRAW robust share 0.22 -> 0.94 after scaffold removal. [CON Nestor] "endogenous
  internalization of register initialization". (NPE ledger; XMI)
- BEE [OBS]: REPL-01 EVENT G: ZERO 18, P90 57, P75 36; K1 93/200 vs 18/100 p 6.6e-7; K3 FM 0/93; state-free at tick
  2000 only P90 8/100, P75 17/100, ZERO 4/100; REPL-02 M1 dominance 1/50, RANDOM positive arm 0/50 (42/50 extinct).
  [CON Bellerophon] "descent component is UNRESOLVED in BEE"; "RESIDUE_NOT_REPLICATED". (ENS ledger)
- Theory predicting agreement: "internalisation of world-supplied scaffolding" (Odysseus Y35; NPE's "most portable
  claim", NPE s9 item 3).
- Reconciliations: (a) ruler: NPE X-MAT asks "not imported from outside L" over whole genomes; BEE G is a resemblance
  label and K3 a founder snapshot that could not return SURVIVES (Harmonia F8); neither traced the register-setting
  bytes (ENS s8 [AD]); (b) world physics: NPE ran full ZERO then withdrawal; BEE ran partial scaffold P90/P75 because
  plain CARRIED killed founders (V3); lifespan 40 and transplanted founders (D1) differ from NPE's random populations;
  (c) the BEE event may be transient by nature (K1 scored LAST checkpoint with a state-free genome, not final);
  (d) NPE's 8/144 may itself be a lineage-bookkeeping event at low rate.
- Classification: PRIMARY ruler (the two engines never measured the same object: whole-genome attribution vs founder
  snapshot vs resemblance label); SECONDARY world physics (scaffold schedule and lifespan).
- Smallest test: one ruler, both engines. Knock out candidate register-setting instructions in each event genome (NPE
  8, BEE 93) to locate the bytes whose loss restores ZERO-dependence; then read byte provenance for exactly those loci
  (NPE dense_taint; BEE bee_tracer 823cbef1, already validated on r022153). Add a final-checkpoint persistence readout to
  NPE's 8 (mirroring REPL-02 s4B). Predictions: real shared phenomenon -> in both engines the located bytes are
  lineage-written (copied or mutated in-lineage) and persist to the final checkpoint in >= half of events; BEE-transient
  -> BEE loci present at event, gone at final; bookkeeping -> located bytes are mutation-born in the event generation
  in both. Cost [AD]: knockouts ~100 genomes x ~64 loci x P-11-style assay, < 6 core-h; tracer replay of ~100 runs is
  the expensive part (~1 core-day on BEE).

### A4. ENVGATE: founders copy only at input 128, yet restoring input 128 does not rescue establishment   [within Archaeon, cross-seat]
- Side 1 [OBS]: census 94/96 exact vmcopy32 copiers gated to one input; R-26: 89/96 triggered by inputs 125-129 around
  NBR base 128; R-33: all 13 exact-gated RIE founders copy only at input 128; 84616's copier loads its destination from
  the input (ASP s2, s7 item 2; #874).
- Side 2 [OBS]: ENVGATE-02 genetic establishment U 24, R128 ("128 only") 5, RRIGHT 3, RWEAK 2, BAND0 5; the frozen
  viability map predicted ~0.7 for R128 and BAND0, both came in at ~7x that (V3; envgate2/VERDICT@13cdec715).
- Theory predicting agreement: "environmental gating of establishment" with the gate located at the input byte a copier
  uses as a pointer (Archaeon; ATLAS reading in ASP s2).
- Reconciliations: (a) frequency, not identity: with 120..135 replaced, input 128 still arrives but at a lower share of
  events than under U, and establishment needs repeated births; (b) host-mediated amplification (ENVGATE-01 R2) needs
  other inputs for the host; (c) BAND0's 5 = 3 cross-arm takeovers + 2 residual near-copiers that established ONLY with
  the window closed (#749): a second, window-independent route contaminates every rescue arm; (d) the establishment
  counts are too thin (2-5) to see any rescue.
- Classification: PRIMARY world physics (input distribution/rate is what the arms really manipulate, and a closed window
  opens another route); SECONDARY representation (the "environment gate" may be an addressing constant, NBR = 128).
- Smallest test: vmcopy32, 24 blocks, arms: U; BAND0; R128 x1 (as run); R128 x16 (input 128 at the U-share of all
  120..135 inputs); and NBR base moved 128 -> 96 with U inputs. Endpoint: genetic establishment (never parent-chain).
  Predictions: frequency -> R128x16 ~= U; pointer/addressing -> with base 96 the gated inputs shift to ~93-97 in a
  re-census and U establishment collapses unless inputs shift too; second route -> BAND0 stays at ~5 in every arm.
  Cost [AD]: ENVGATE-02 was ~24 blocks x 5 arms with median 1 h/block -> ~150 core-h; halving blocks gives ~75 core-h.

### A5. Copy fidelity: NPE "6-11% of certified copies exact, ~25x nominal erosion" vs BEE r_cc 0.9987
- NPE [OBS]: X-A3-AUTOPSY exact copies 4/63, 38/340; post-copy loss is child material (0.51/0.63); X-STALL 177/192
  genome-sterile at epoch 100; erosion ~5%/byte/epoch. (NPE ledger)
- BEE [OBS]: coupling P3 heredity gap 0.9987; P5 ceiling ~0.999 both arms (ENS ledger, rulers).
- Archaeon [OBS]: 19-23% of near-copiers become EXACT self-copiers in ONE copy by the fixed-point route (FIXEDPOINT s1).
- Theory predicting agreement: Z80 soups with LDIR copy bytes verbatim; fidelity should be set by the mutation rate.
- Reconciliations: (a) world physics: NPE pair-tape writes back BOTH halves after every interaction (NPE s2: the
  erosion mechanism), BEE births write into a cell while the parent tape changes only by mutation or being overwritten --
  structurally BEE is closer to NPE's ATOMIC world; (b) terminology: BEE's "ATOMIC" is a scoring mode (V2) and is easy to
  misread as NPE's write-back fix; (c) ruler: NPE counts exactness over P-11-certified events (includes partial and
  painter constructions); BEE r_cc is over seeded competent copiers.
- Classification: PRIMARY world physics (write-back policy); SECONDARY terminology (ATOMIC collision, V2).
- Smallest test: in NPE, re-measure exact-copy share for the 7ae3 founder under C-ATOMIC ON vs OFF (80 seeds/arm, the
  frozen C-ATOMIC harness) with BEE's r_cc definition; in BEE, add a "write-back both" option (parent tape overwritten
  by the post-execution window state) for seeded copiers, 60 runs/arm. Predictions: write-back explains it -> NPE ATOMIC
  r_cc rises toward >0.99 and BEE write-back-both falls toward NPE's ~0.1-0.3 exact share; ruler explains it -> NPE ATOMIC
  exactness stays ~10% under r_cc. Cost [AD]: NPE side reuses C-ATOMIC, ~10 core-h; BEE side needs a small VM option.

### A6. Tape-write erosion "is what stops pair-tape heredity" (C1 46/80 vs 1/80) vs no rescue in 15 other specimens (C2 1/120 vs 0/120)   [within NPE]
- Evidence [OBS]: NPE C-ATOMIC C1/C2 (F:328-334); 12/16 panel donors copy at 0.0 from a fresh state; X-H2-7AE3 depth
  ceiling 1-4 in 13/15 specimens "unexplained beyond donor copy competence 0.0" (NPE s7).
- Theory: barrier map "donor acquisition -> causal copy -> sustained heredity" with erosion as THE heredity barrier.
- Reconciliations: (a) barriers in series: ATOMIC only matters where the upstream copy competence exists (7ae3 is a
  genuine copier, most panel specimens are painters/inert); (b) 7ae3's side-1 copying is atypical (P2 copiers are
  side-0-only 1,052/1,154); (c) C2 underpowered (8 seeds x 15 specimens).
- Classification: PRIMARY intervention (ATOMIC was delivered to organisms that cannot copy, so it could not act);
  SECONDARY ruler (P-11 panel "competence" was construction, not copying, #793).
- Smallest test: C2 again restricted to the CVT-R-positive panel members (set c style) plus 2 painters as negative
  controls, 40 seeds/arm. Predictions: series-barrier -> ATOMIC effect in CVT-R-positive specimens comparable to 7ae3,
  none in painters; 7ae3-specific -> null in all others. Cost [AD]: ~15 core-h.

### A7. PROTEUS-46 "no intermediate the probe can see" vs Artemis D002-03q 5-edit neutral path   [within Proteus substrate, cross-seat]
- Side 1 [OBS]: USEFUL 0 vs 0 (v0.4 vs graph); greedy walks 0/100; random walks 0/200; best seen 3/6. [CON Proteus]
  "coordinated change with no intermediate the probe can see". (_part_proteus)
- Side 2 [OBS]: duplicate-and-diverge path: 4 NEUTRAL steps at 3/6 then 6/6; single fixes 0/6; drift 1/50 hit at step
  188 vs control 0/50; population 50x100 gens never 6/6; the full run timed out. Greedy key (two, -ops) vs incumbent
  (cur, 0) means a neutral child with ops >= 1 is never accepted (falsifier_46.py:117-131). (#1116)
- Theory: "cliff not slope" (C4) feeding PROTEUS-46, HEPH-32, FP-003.
- Reconciliations: (a) search: greedy 3-step with tie rejection is structurally blind to neutral paths; (b) ruler:
  two_key is quantised (no 4/5 ever seen) so graded progress is invisible; (c) the path exists but is so rare that
  population search at realistic budget does not find it (1/50 drift).
- Classification: PRIMARY search (the acceptance rule, verified in code); SECONDARY ruler (quantised probe).
- Smallest test: graph_grammar.v1 and v0.4, parents {hand-written 3/6, evolved C3 shelf parent}, walks x 200 per cell,
  300 steps, acceptance {greedy-strict, neutral-accepting (ties accepted), random}. Readout: first-hit 6/6 fraction and
  steps. Predictions: search -> neutral-accepting >> greedy (>= 5/200 vs 0/200) on graph; landscape -> all ~0;
  representation -> graph >> v0 under neutral-accepting. Cost [AD]: D002-03q quick mode was minutes; full 2x2x3x200 walks
  ~2-6 core-h (the timeout was a Fabric wrapper issue, not compute).

### A8. "Cliff in behaviour at every radius" (C4-01/02) vs the C4-02 cliff predicate NO and Odysseus "plateau"
- Side 1 [CON Archaeon]: "cliff in behaviour, not a slope"; D7 0/5,472 and 0/2,280; loss .52 -> .99 over radii 1-16.
- Side 2 [OBS]: C4-02 preregistered cliff predicate reads NO, largest step .170 (IDX s2); Odysseus S3 on 1,568 eligible
  edits: 0 improved, 61.7% neutral, 33.6% lethal, UB .0019 (#750); 606 of 5,472 C4-01 edits could not apply (IDX s4);
  C4-02 radius = delta successive grammar.mutate() calls on genomes of 19-64 words = a count ruler (ASP s2).
- Theory: bounded-variation region (C4) and the locality law both assume the radius ruler is length-neutral.
- Reconciliations: (a) terminology: "cliff" names the bimodal per-edit displacement, not a loss-vs-radius step;
  (b) ruler: count-fixed radius hits short genomes harder (the CW01 D084 artefact family); (c) denominator: non-applicable
  edits inflate the zero's base.
- Classification: PRIMARY ruler (count vs fraction geometry, shown to manufacture 4/7 CW01 claims on this same VM);
  SECONDARY terminology (cliff vs plateau vs bimodality).
- Smallest test: re-run the C4-02 radius curve on the same 57 parents under the qualified Bernoulli(f) ruler, f matched to
  the mean radius/length, applied edits only. Predictions: ruler -> the loss curve flattens and splits by length bin less;
  genuine cliff -> step >= .3 at some f persists. Cost [AD]: T-ARCH4 runs took ~2 min each; < 1 core-h.

### A9. "Robustness is carried by length" (C4-08/C5-08) vs "length protects DISAPPEARS" under Bernoulli (CW01 P-G08)
- Side 1 [OBS]: C4-08 loss .419 -> .125 while length 19.1 -> 62.5; dead-code ablation only .435 -> .409; [CON] C5-08
  "MIXED, length carries it". Also P-C03 trap-NOP length +1.80 vs +0.30 and P-C16 length-balanced proposals +2.35:
  [CON Nestor] "growth is driven by the acceptance filter".
- Side 2 [OBS]: CW01 P-G08: P-D01 length dose DISAPPEARS under Bernoulli(f) (qualified on 126 programs, chi p
  .48-.49); 4 of 7 claims gone.
- Theory: "robustness as structural property" vs "count rulers manufacture length protects".
- Reconciliations: (a) both true: length genuinely protects against the count-fixed MUTATION OPERATOR that selection
  experiences, and is not structural robustness under a fraction ruler (ASP s2 [AD]); (b) C4-08 lineages carry
  unexpressed padding that a fraction ruler hits proportionally; (c) selection built something besides length that the
  CW01 programs lack (different populations).
- Classification: PRIMARY ruler (the robustness readout is count-fixed); SECONDARY search (neutral acceptance under a
  count operator selects length -- bloat).
- Smallest test: take the 188 C4-08 drifted lineages at gen 0 and gen 100; measure loss under (i) fixed-k count and (ii)
  Bernoulli(f) with f = k/mean length. Then re-run 100 generations with a per-site (fraction) mutation operator, 40
  lineages/arm. Predictions: ruler-only -> gen100 advantage vanishes under (ii); bloat-by-operator -> under a fraction
  operator length stops growing and robustness gain disappears; structural -> gen100 advantage survives (ii) and the
  fraction operator. Cost [AD]: < 3 core-h.

### A10. C5 "flat elite" (0/96 held-out gains; elite = starting parent after 36,000 evals) vs Deep Frontier N-scaling (every N climbs, max .479-.562 vs parent .382 at 60,000 evals)
- Evidence [OBS]: C5R l.4-7, 60-143; DIGEST 2026-09-21T2054Z; DF-012 [CON Archaeon, PROVISIONAL] "may be a
  compute/population-size artefact". Never promoted (ASP s7 item 1).
- Theory: C5's operator-accepted "selection under the frozen grammar does not climb these worlds at all".
- Reconciliations: (a) search budget/population (9,000-36,000 vs 60,000 evals); (b) ruler: DF reports training-reward
  max; C5 reports held-out gains -- DF climbs may be overfitting (cf. CW01 e09 3-op chains overfit train8); (c) world
  set differs (DF "C5-flat N-family" composed worlds vs C5's screened 9/25).
- Classification: PRIMARY search (budget/N); SECONDARY ruler (in-sample vs held-out).
- Smallest test: 2 C5 worlds that were flat, N in {50, 400}, evals in {36k, 60k, 120k}, 6 seeds, report BOTH max
  training reward and held-out reward of the final elite. Predictions: budget -> held-out rises with evals; overfit ->
  training rises, held-out flat; world-set -> no climb on C5's own worlds at any budget. Cost [AD]: 2x2x3x6 = 72 runs,
  ~2-3M evals, ~10-20 core-h.

### A11. Task coupling: BEE v3 contingent payment works (P1 40/40, 149 vs 0) vs NPE task gating does nothing under pair execution (d = -0.037)
- BEE [OBS]: ON vs YOKED extinction 1 vs 67/150, competence .77 vs 0; ECHO acquisition 29 vs 6/150; MD LADDER1 58/320;
  but COND_ONE 0/960, random soup 0/3,200; v2 physics: EXTERNAL-only 178 vs ENDOGENOUS-only 2 (antagonistic).
- NPE [OBS]: EXPLICIT_FITNESS +0.30 is EXTERNAL-reproduction-only; under PAIR_EXECUTION TASK_GATED d = -0.037 (32 pairs),
  held >= .75 in 2/45; X-TASK-GATE frozen, not executed (NPE s7).
- Theory: "contingent earning selects FOR task code" (Bellerophon, strongest surviving mechanism).
- Reconciliations: (a) world physics: BEE v3 couples computation to the copy RESOURCE (paid births); NPE gates
  interaction, which does not change who copies; (b) maintenance vs acquisition: BEE's effect is on SEEDED code, NPE had
  nothing competent to maintain; (c) endogenous reproduction overwrites task input regions in both (BEE G4).
- Classification: PRIMARY world physics (coupling channel); SECONDARY intervention (seeded vs unseeded).
- Smallest test: run the frozen X-TASK-GATE (18 seeds/arm, TASK_GATED vs SHUF) and add one BEE-style arm: births paid
  from task-correct outputs (PAID) with a YOKED twin, all seeded with an NPE copier carrying a task witness. Predictions:
  channel -> PAID >> YOKED while TASK_GATED ~ SHUF; seeding -> both null without the witness, both positive with it.
  Cost [AD]: X-TASK-GATE needs an Aporia dispatch; +2 arms ~ +10 core-h.

### A12. Imports take over 12/12 regardless of competence (Proteus/WSE) vs NPE founders are ~13% lottery tickets
- Side 1 [OBS]: C3-SFE-10 mature 12/12, permuted-incompetent 11-12/12, no import 0/12 within 2-8 generations.
- Side 2 [OBS]: X-DOSE-CURVE s(k) = 1-(1-p)^k with p = 0.13, LRT p .42; loss = cessation within ~12 epochs, not
  extinction; X-ATOMIC-RANDOM random implant 0/80 vs genome 46/80.
- Theory: establishment as a branching process with R0 set by the founder (shared frame NPE/Archaeon/BEE, XE-EST-1).
- Reconciliations: (a) world physics: WSE imports enter a selected population whose incumbents are weak, and import is
  population-level write authority; NPE founders must copy through an eroding pair tape; (b) dose: imports are many
  copies at once, NPE k = 1..8; (c) ruler: "takeover" (population share) vs "runaway causal depth >= 20".
- Classification: PRIMARY world physics; SECONDARY intervention (dose and delivery).
- Smallest test: NPE, 7ae3 founder and a permuted (incompetent) 7ae3, doses k in {1, 8, 32, 128} of 256 cells, ATOMIC on
  and off, 32 seeds/cell, two endpoints: 50% population share at epoch 100 and causal depth >= 20. Predictions: mechanics
  -> permuted takes over at high k under ATOMIC as often as real; competence-gated -> only real founders establish;
  erosion -> neither takes over without ATOMIC. Cost [AD]: 2x4x2x32 = 512 runs, ~20-40 core-h.

### A13. Where M2's bit lives: Cosmos certificate "cue already in site state" vs Ananke "it schedules, it does not store" (channel state)
- Ananke [OBS/CON]: M2 flush in-flight mid-gap 0.883 -> 0.497; S/inbox resets no effect; zero-parameter echo model
  46/46 curves; carrier = channel state; phase-indexed swaps (W-R) show pooled letters hold in one phase only.
- Cosmos via Artemis R-10 [CON, worker claim, #878]: the v3 certificate agrees with Ananke on M2 but "at the tick before
  readout on odd-phase trials the cue is already in site state"; fixed swap at t = k insufficient for periodic-update
  engines; P1 at k+1 cannot localize memory.
- Theory: X-2 in CROSS_ENGINE_THREADS: Cosmos P1/P2 full-state swap = PTE carrier swap "reached independently".
- Reconciliations: (a) phase: on odd phases the packet has already delivered (transport arriving at readout, as in M3);
  (b) F7: a swap names the reader's register, so "site" and "channel" are both correct at different ticks;
  (c) the certificate's fixed swap time is a ruler artefact on sync period-2 clocks.
- Classification: PRIMARY ruler (swap time and phase indexing); SECONDARY representation (storage form vs function, H1).
- Smallest test: 3 M2 specimens, 512 worlds, swaps at t in {k-2, k-1, k} split by clock phase; run Cosmos cert v3 through
  the R-10 adapter and Ananke swap_rel (REL4) on identical trials. Predictions: phase -> both instruments agree once
  phase-indexed (channel on even, site at k-1 on odd); genuine disagreement -> they disagree on the same phase/tick.
  Cost [AD]: minutes of PTE compute; adapter exists.

### A14. "Timing, not content" (Aether) vs "presence IS the content" (Ananke)
- Aether [CON]: rcv propagates "activation timing ... not content"; content signature failed its own positive control
  (fwd preserved content in 3.1% of origins, E-P1 FAILED) yet clears 3 laws (R-11).
- Ananke [OBS/CON]: 3 of 4 RELAY champions carry the cue as SOURCE PRESENCE (who fires); relay held .837-.883 vs .50
  zero-comm; W-C "content-vs-timing contrast REFUTED"; F7 "a swap verdict names the reader's register, not the physical
  code".
- Theory: Cosmos L5 "Distance is not information" / H1 "registration is not use" (CAH s8) -- all three seats claim a
  single distinction.
- Reconciliations: (a) terminology: Aether's "content" = value-provenance of bytes; Ananke's "content" = task-relevant
  bit, which can be encoded as timing/presence; (b) ruler: Aether's N2 signature is blind even to a forwarder, so its
  "no content" is unmeasured; (c) substrates differ: PTE has a task-bearing reader, Aether has none.
- Classification: PRIMARY terminology; SECONDARY ruler (N2 failed its positive control).
- Smallest test: apply Aether's XOR content signature and one-bit twin assay to two PTE RELAY champions (task transport
  certified by zero-comm), and apply Ananke's zero-comm-style reader test to Aether rcv_add (does any fixed reader decode
  the origin bit from the far field above chance?). Predictions: terminology -> Aether N2 reads "no content" on PTE
  relays that do transport the bit (N2 is blind), and a reader decodes rcv_add origin bits at some radius; genuine ->
  no reader decodes rcv_add's origin beyond radius 1-2. Cost [AD]: < 2 core-h each side; needs a small adapter.

### A15. Recombination: harmful or null in NPE/SFE/CW01 vs the only improving route in Apollo
- Evidence [OBS]: NPE splice manufactured ~88% of predecessor replicators and prevents runaway (splice off 7/150 vs
  0/150); SFE C4-06 mate-splice 8 points less viable, 0 crossings; CW01 P-I04 splice = mutation; Apollo stall map:
  0/8000 single-step improving walks vs 6.1%/pair recombinant, with crossover_frac default 0.0 (HAR s7 item 4).
- Theory: none stated; IDX s8 item 5 lists it as "three engines, one operator, three readings".
- Reconciliations: (a) representation: positional byte genomes (NPE, Proteus v0) make a splice misalign addresses, while
  Apollo's primitives recombine as modules; (b) Apollo's recombinant rate may be measured on pairs selected for
  complementary parts; (c) NPE's splice is applied to pair tapes during execution -- it is world physics there, not a
  search operator.
- Classification: PRIMARY representation; SECONDARY world physics (NPE splice is part of the interaction).
- Smallest test: Proteus graph substrate, parents = one_value (3/6) x keyed (6/6) partial solvers, operators {point
  splice, homologous subgraph crossover, mutation only}, 4,000 children each, two_key readout. Predictions:
  representation -> subgraph crossover yields graded/useful children at >1% while splice ~0; operator-generic harm -> both
  ~0. Cost [AD]: < 1 core-h.

### A16. Eviction: "both declared eviction policies lose to random" (WTP-LM01 dev) vs "recency beats random at equal capacity" (S1 key-value)
- Evidence [OBS]: SI EXPERIMENTS 09-26T03:48Z (HAR s7 item 13); Odysseus Y04 lists "random eviction beats declared
  policies" as FALSIFIED-CLAIM; Ensorain S1: key-value 64/256/1024 slots, recency beats random because recency correlates
  with query distribution (ENS s7 item 11).
- Theory: Ensorain "discarding is a variance-control device"; "keep + regime-gate >= discard on recall".
- Reconciliations: (a) world physics: the value of recency depends on whether queries are recency-correlated; LM01's
  positive-control world may not be; (b) ruler: LM01 F3 "never_seen" was 87-89% stale recall (lm01 ERRATA E-4), which
  penalises recency-based eviction; (c) optimizer confound D6 in LM01 dev.
- Classification: PRIMARY world physics (query distribution); SECONDARY ruler (never_seen split).
- Smallest test: one world generator with a query-recency correlation dial rho in {0, .5, 1}, capacities {64, 256},
  policies {recency, declared LM01 policies, random}, 16 seeds, scored on (i) fresh-cell recall and (ii) the LM01 split.
  Predictions: world -> recency wins iff rho > 0 under (i); ruler -> random wins under (ii) at every rho. Cost [AD]:
  < 1 core-h on Ensorain dev harness.

---------------------------------------------------------------------------------------------------------------------

## TASK B -- NATURAL EXPERIMENTS (11)

### B1. Register reset / carried execution state
- NPE [OBS]: C-ZERO-SPECIFIC ZERO 26/48, CONST 0x5A 2/48, CARRY 6/48, RANDOM 3/48 (p 2.4e-8); C-STATELESS-FFA6 11/33 vs
  34/42; X-DD-STATE-RESET (reset only on genome change) null .38 -> .43; X-A3-WITHDRAW persistence identical under
  gradual vs abrupt removal, robust share rises to ~.93.
- BEE [OBS]: historical physics = ZERO every execution (V3); plain CARRIED kills zero-dependent founder lineages 0/24 vs
  ZERO 10/24; p = .25/.5/.75/.9 give 0/12, 1/12, 2/12, 5/12; random-population pilot CARRIED 19/100 origins 0 persisting
  vs ZERO 6/100 3 persisting.
- PTE [OBS/CON]: "registers are 0 at tick 0, so every SETRULE goes to rule 0" -- a bootstrap exploited in 27/42 cells;
  freeze_rule -> 0.52 on M3; Ananke calls it "a PHYSICS ARTIFACT".
- Archaeon [OBS, V1]: z80atlas VM zeroes registers every execution; its copiers take destination from the input byte.
- Comparability [AD]: NPE and BEE vary the same axis (ZERO vs CARRIED, BEE even copied NPE's SCHEDULE text) but with
  different readouts (runaway-given-donor vs founder-lineage persistence); PTE varies nothing -- the zero is a fixed
  initial condition that evolution uses as a free constant; Archaeon's zero is fixed too.
- Joint reading [AD]: a zero register file is a supplied constant in all four engines, and in every one where it was
  probed, evolved machinery depends on it (NPE addressing from never-written zeros; BEE ZERO_DEPENDENT founders; PTE rule-0
  bootstrap). Neither NPE nor BEE alone shows that dependence is general; together they show a dose curve (BEE p-sweep)
  and specificity to ZERO rather than to "any clean state" (NPE CONST 2/48). Dependence on a constant is the default
  outcome of search, not a phenomenon of any one engine.
- Matched follow-up: one protocol in three engines -- arms {ZERO, CONST 0x5A, RANDOM-per-execution, CARRIED} with the
  same readout "fraction of evolved competent organisms whose competence drops > 50% when entry registers switch from
  ZERO to CONST". NPE: fresh panel 48 seeds; BEE: grounding cell, 48 seeds; PTE: 12 fresh searches with tick-0 registers
  set to CONST vs 0, measure SETRULE-bootstrap share. Cost [AD]: ~30 core-h total.

### B2. The copy primitive: remove it, cheapen it, or add it
- Archaeon [OBS]: copy_prim off/on: 0 copiers in 1.2e7 vs 96 exact per 1e7 (vmcopy32).
- BEE [OBS]: LDIR off / cost4 / undefined -> HALT: spontaneous SR 8/300 -> 0/300 in each; seeded copier with LDIR cost
  x4 sustained 57/60 -> 1/60; NOP every LDI/LDIR/COPYALL in 345 origins -> still SR in 126 (36.5%), 124/126 by a
  new-position copy op; Odysseus affordance ladder L0-L3t 2.7e-5 -> 1.4e-5 -> 5.1e-9 -> impossible (HAR row 12).
- NPE [OBS]: 1-byte LDIR/LDDR alias: donor acquisition 1/64 -> 39/64; non-pair 1-byte ALLOC/LDIR/BIRTH aliases 0/40 ->
  13/40; SHAM 1-byte random block write 0/96; PLANT 32/96; BYTEWISE 10/500 vs 47/531 (R-26).
- Proteus [OBS]: graph SUBGRAPH_COPY is 100% neutral (dormant attach), yet the only path to 6/6 is duplicate-and-diverge.
- Comparability: the manipulations differ in direction (remove vs add vs cost) and granularity (per-byte COPY, block LDIR,
  1-byte alias); rulers differ (census exactness; BEE SR; NPE P-11). The BEE NOP-ablation and the NPE SHAM are the only
  controls for "any write density".
- Joint reading [AD]: across three VMs, replication rate scales with the ENCODING COST of the copy primitive over at least
  four decades (impossible -> 5e-9 -> 1e-5 -> ~0.6 of donor runs), and density-of-writes alone (SHAM 0/96) does not
  substitute. BEE's 124/126 re-routing shows the primitive is necessary but not location-specific. No engine alone spans
  the ladder.
- Matched follow-up: one "encoding cost" axis in BEE (the only VM with all switches): copy instruction length 1, 2, 3
  bytes and absent, G = 64, 300 runs/arm, BEE SR + CVT-R on origins; mirror 2 levels in NPE (existing alias and stock).
  Cost [AD]: ~40 core-h.

### B3. Write authority / write-back
- NPE [OBS]: ATOMIC write-back 1/80 -> 46/80 (7ae3), 1/120 vs 0/120 elsewhere.
- Aether [OBS]: add (combine instead of replace) frozen fraction .927 -> .696, 83% of change = counting; E-011 relay
  writes replace instead of add 22/128 -> 10/128 (null 5).
- PTE [OBS]: freeze_rule -> 0.52; forbid switch at readout site .500 exactly, same pin at a random site no effect.
- Archaeon/SFE [OBS]: imports take over 12/12 whatever their competence; ENVGATE R2 host-executes-resident =
  "amplification, not origination".
- BEE [OBS]: POLLINATION v1 world-made copies vs v2: extinction 0/150 vs 148/150.
- Comparability: all change WHO may overwrite state and whether writes accumulate or replace, but on different state
  (genome halves, field values, routing rule, population slots).
- Joint reading [AD]: in every engine the write rule, not the organism, set the headline: NPE heredity, Aether
  propagation, PTE M3, BEE persistence and SFE takeover all flip on one write-policy switch. "Write authority" is an
  UNMEASURED Atlas primitive (IDX s6) despite being the most frequently decisive intervention in the corpus.
- Matched follow-up: tag each engine's write policy on three binary features (accumulate vs replace; writer = self vs
  other vs world; post-hoc write-back vs accepted-only), then run the cheapest switch in each (NPE ATOMIC on a second
  genuine copier; Aether add vs replace on rcv_str; PTE freeze at readout on the 3 M2 cells) with the same effect-size
  convention. Cost [AD]: ~20 core-h.

### B4. Zero-parameter restatement attacks
- Cosmos [OBS]: C0 laws tie the definition rung (McNemar D p .688, E .688, F .125); C3 zero rule reproduces 104/120
  classes + 12/12; T-I1 11/15 atoms re-express the rung.
- Ensorain [OBS]: WTP-03 N6 tuned batch completion beats all 9 flags (q0 2.578 vs 4.856).
- Hecate [OBS]: 0/5 SIGNAL survive Pass 4; each reduces to a known mechanism; novelty rule passed by a lookup table
  (AUC .844-.852).
- Bellerophon on Cosmos C4 [OBS]: REL@q rule BA .910 vs T3-DOWN .500; Cert B agrees with A 47/48.
- Aether [CON]: rcv is "a CALIBRATION LAW"; the full-ring ablation "forced by the law".
- Theophrastus [OBS]: 14 of 23 REPRODUCIBLE signals are positive controls.
- Comparability: each seat built a different null (definition rung, tuned completion, known-mechanism library, lookup
  table), found post hoc in most cases.
- Joint reading [AD]: the failure rate of "law" claims to a zero-parameter restatement is ~100% across five seats where
  the restatement was tried; the attacks were independent in construction but shared an author family (HAR s4b). The
  pair says the restatement null must be a PRE-freeze gate, and it is cheap.
- Matched follow-up: a shared "restatement battery" run before freeze on the next claim of each seat: (i) the target's
  definition as a predictor; (ii) a lookup table on the same features; (iii) a tuned known-mechanism baseline. Test it
  first on the already-decided cases (C0, C3, WTP-03, Hecate 5) as known-answer fixtures; each should fail. Cost [AD]:
  hours.

### B5. Fixed-count vs fraction rulers
- CW01 [OBS]: fixed-k/contiguous/round(f n) vs Bernoulli(f): 4/7 claims DISAPPEAR, 2 SHRINK, operand softness SURVIVES
  (-.19).
- Archaeon [OBS]: C4-02 radius = count of mutate() calls; C4-08 length 19 -> 62 with robustness.
- NPE [OBS]: erosion stated per byte per epoch (~5%/byte/epoch) -- a fraction ruler by construction.
- Proteus [OBS]: v0.4 ops act on contiguous k in [1,4]; contiguous-block ops .97-.995 destroyed vs point ops .354.
- Odysseus [OBS]: S3 eligible-edit denominator 1,568 of 5,472.
- Comparability: CW01 and Archaeon C4 ran on the same Proteus VM (T-ARCH4), so this is a true within-substrate natural
  experiment; Proteus's per-op table is the same VM at another level.
- Joint reading [AD]: every length-dependent claim in the Proteus-VM corpus (cliff, length protects, selected tops robust)
  is exposed; only word-kind (opcode 2.3x operand) and operand softness survived a ruler change.
- Matched follow-up: the A8 + A9 tests together (one harness, one ruler swap). Cost < 4 core-h.

### B6. Greedy vs neutral-accepting search; reach vs physics
- Proteus/Artemis: A7 above.
- Archaeon [OBS]: neutral-walk exaptation .016 -> .043 (C4) and .050 -> .082 at depths 16 -> 64 (C5-01, killed on a
  yield rule).
- NPE [OBS]: neutral mutation walk reaches competence at about the soup's rate (pilot ratio 1.75, p .20; WP-9 unrun);
  copiers sit on broad neutral networks (72-80% of 1-step mutants competent); CW01 cycle 8: 0 hits in an exhaustive 1-edit
  census, a single witness fixes 10/12.
- PTE [OBS]: plants beat champions (.999 vs .755; lag-2 plant 1.000 vs 0/4 searches); H6 "search reachability, not
  physics".
- Tyche [OBS]: 2/72 regime adaptations; parity-3 unreached; lexicase noise-level parent choice 395 vs 280.
- Apollo [OBS]: 0/8000 single-step improving walks vs 6.1%/pair recombinant.
- Comparability: all vary or observe the search policy's handling of neutral/zero-marginal steps; budgets differ by orders.
- Joint reading [AD]: five engines report the same shape -- the target is expressible and often one to five edits away,
  but the search used cannot traverse zero-marginal intermediates. No engine has run a matched "same budget, ties accepted
  vs rejected" contrast; D002-03q is the closest and it timed out.
- Matched follow-up: WP-9 in NPE (~9 CPU-h, portable, NPE s7) as the soup-vs-random-walk baseline, plus the A7 test
  in Proteus and a tie-accepting variant of PTE's GA on the lag-2 task (12 searches). Cost [AD]: ~25 core-h.

### B7. Horizon extension
- Aether [OBS]: E-005 (500 -> 10,000 ticks) OFF radius 2/5/7, rcv ON 39, 0 locality violations: "horizon-robust"; E-008
  rcv_str radius 8 -> 19, 6/32 origins set a new max generation after tick 2,000: "HORIZON-DEPENDENT"; one add OFF origin
  crossed radius 3 -> 5 between +5k and +10k.
- NPE [OBS]: X-A3-WITHDRAW robust share .22 -> .94 over the post-removal horizon; C9-D14 identity 0.97 -> 0.00 by epoch 600.
- BEE [OBS]: REPL-01 events at the LAST checkpoint with a state-free genome vs final tick 2000 counts 8/17/4 per 100 --
  most events are transient; multiday 20k ticks; E-003 transmission 0.00115.
- Archaeon [OBS]: block 13 aligned founder share 0.90 at 14,000 -> 0.09 at 17,500-19,900 while exact self-copy stays
  .83; block-15 Attempt 1 horizon too short.
- Comparability: all extend time at fixed physics; readouts are last-state vs ever-state.
- Joint reading [AD]: in every case the readout choice (ever-reached vs final-state) decides the verdict more than the
  horizon itself: Aether's "robust" and "dependent" are both right for different laws; BEE's K1 SURVIVES is an ever-state
  readout. A long horizon without a final-state readout inflates; a short one with it deflates.
- Matched follow-up: report both ever-state and final-state at 1x and 20x horizon for NPE C-A3 events, BEE REPL P75,
  Aether rcv_str. Cost [AD]: mostly re-analysis of stored checkpoints; NPE needs a 20x rerun (~20 core-h).

### B8. Transplant / sham / scratch: does moving material move competence?
- Graphworld [OBS]: R7 graft-scratch +0.738 (p .046), graft-sham -0.662, sham-scratch +1.400; R8 scale-only arm +2.10
  [1.19, 2.98] -- initialisation scale masquerading as transfer (IDX s7 item 7).
- Archaeon [OBS]: transplants persist 39/39, self-replicate 27/27, retain task competence 0/39; TH-015 executed path+data
  (21/32 loci) transfers copying at 0.89 vs size-matched random graft .057 and knockout loci .028.
- SFE [OBS]: CMP1 fragment-transfer positives died under CRN (+0.009, +0.002); controls handicapped by harness-seeded fills.
- NPE [OBS]: X-ATOMIC-RANDOM genome 46/80 vs random implant 0/80; C-SWAP-ACQUIRE 9/240 vs 0/240 (missed rule); X-CONTENT
  runaways carry 13-25% founder bytes.
- BEE [OBS]: REPL-01 transplanted founders; FM founder content ~0.01 by tick 500 in every arm.
- Comparability: graphworld transfers parameters into a learner; Archaeon/NPE transplant genomes into worlds; SFE
  transfers fragments. Controls differ: only graphworld had a SHAM, only Archaeon had a size-matched random graft.
- Joint reading [AD]: copying capacity transfers with executed code (Archaeon .89, NPE 46/80 vs 0/80), task competence does
  not (0/39), and apparent transfer of learned function can be carried by non-specific properties (scale in GW, harness
  fills in SFE). Sham controls are what exposed it in both GW and SFE; Archaeon and NPE transplants lack a sham of matched
  scale/length.
- Matched follow-up: in NPE and Archaeon, add a SHAM transplant (same length, same byte composition, shuffled order) to the
  genome-vs-random contrast; in GW, add Archaeon's "executed-path-only" graft. n: 80 seeds/arm NPE, 24 blocks Archaeon.
  Cost [AD]: ~30 core-h.

### B9. Energy supplied at birth or for maintenance
- NPE [OBS]: half-energy transfer at birth 4/40 -> 20/40 (newborn starvation); not needed for a first copy (C-ABLATE null).
- BEE [OBS]: ON vs YOKED (same total bonus, non-contingent) extinction 1 vs 67 of 150; IMPLICIT base income never
  limiting makes the task inert; "base income alone keeps copiers viable" (K40 ECHO, untested).
- PTE [OBS]: emission cost -> 3/3 vs 1/3 champions communicate, code class unchanged (UNRESOLVED); economy is a gate of
  the hand design only.
- Aether [OBS]: sustained feeder cut 0.39x sham long-edge persistence; inert-site starvation 0/128 vs sham 17/128.
- CW01 [OBS]: length price shrank genomes 44 -> 5-6 instructions at unchanged reward.
- Comparability: NPE and BEE both manipulate energy flow to reproducers; PTE/Aether manipulate maintenance cost/supply.
- Joint reading [AD]: energy matters where it is CONTINGENT (BEE ON vs YOKED at equal totals) or where it bootstraps a
  newborn (NPE); total supply alone is inert (BEE IMPLICIT). No engine has run "equal total, different timing" except BEE.
- Matched follow-up: NPE C-ENERGY with a YOKED twin (same total energy, delivered at a random time rather than at birth),
  40 cells/arm. Cost [AD]: ~5 core-h.

### B10. Lineage labels vs material descent
- Archaeon [OBS]: parent-chain labels 8-42x genetic establishment counts; manufactured a rescue gradient
  (194/126/59/139/108 -> 24/3/2/5/5).
- BEE [OBS]: G ~0.9-0.95 of population at tick 500 while FM ~0.01; native material label wrong vs copy-descent 0.504;
  causal L jumps on 1-byte writes; 33.1% of 28.96M births NOT_IDENTIFIABLE.
- NPE [OBS]: anc marker ~1.0 while founder bytes 13-25%; C9-D14 id kept while bytes replaced.
- Comparability: three independent label systems, one outcome.
- Joint reading [AD]: every slot/id/resemblance label over-reports descent by roughly an order of magnitude against
  material attribution; the one material-grade tracer per engine (Archaeon taint, bee_tracer, dense_taint) has been run
  on one run or one campaign each. Any cross-engine heredity table is currently a bookkeeping table.
- Matched follow-up: publish, per engine, label-vs-material agreement on one common readout (fraction of births whose
  label-parent wrote >= 50% of the child's bytes) for 1,000 sampled births. Cost [AD]: re-analysis where tracers exist.

### B11. Present, decodable, and unused
- CW01 cycle 8 [OBS]: the regime word is read into a register that predicts the regime at accuracy 1.0 and is never used
  (overwriting it changes 0% of answers, D089).
- PTE [OBS]: HOLD twins differ in flight at 9/9 ticks while channel swaps leave the trace bit-identical; 80-95% of pairs
  carry mirror-different sensor traffic that swapping does not change.
- Cosmos [CON]: L5 "Distance is not information"; all 7 T3-DOWN errors register but carry no usable history.
- Aether [CON]: propagation of timing without content; "generation is not reach".
- NPE [OBS]: "encoding accessibility, not presence": block-copy encodings in 87/96 plain runs yet 1/64 donors.
- Tyche [OBS]: fragments stored, never sets; stored-any rises with diversity while adaptation does not.
- Comparability: all six observe information present in state that the organism's computation does not consume; only CW01
  and PTE intervened (overwrite, swap).
- Joint reading [AD]: "present != used" is the corpus's most replicated qualitative law and it is ruler-independent in the
  two engines that intervened. It predicts that any presence-based ruler (decoders, taint presence, carrier presence)
  over-reports mechanism by a large factor.
- Matched follow-up: a common "decode vs swap" pair on one representative state in each engine (CW01 register, PTE
  channel, NPE block-copy encoding, Aether far field): decoding accuracy and swap effect reported side by side. Cost [AD]:
  hours per engine.

---------------------------------------------------------------------------------------------------------------------

## Cross-cutting notes [AD]

- Classification tally over A1-A16 (primary): ruler 5 (A2, A3, A8, A9, A13; ruler is also secondary in A1, A6, A7, A10, A14, A16), world physics 5 (A4, A5,
  A11, A12, A16), search 2 (A7, A10), terminology 2 (A1, A14), representation 1 (A15), intervention 1 (A6). Substrate
  appears only as a secondary cause (A1). The corpus's disagreements are overwhelmingly about what was measured and
  which world rule was active, not about organisms.
- Two terminology collisions should be fixed in Atlas vocabulary before any cross-engine table: "Z80" (three ISAs, V1)
  and "ATOMIC" (write-back vs scoring, V2). Also "competent" (P-11 construction vs BEE COMPETENT_e vs task competence) and
  "content" (A14).
- Cheapest high-value tests: A8 (< 1 core-h), A15 (< 1 core-h), A13 (minutes), A16 (< 1 core-h), A7 (2-6 core-h), A1
  (2-4 core-h). Most expensive: A4 (~75 core-h) and A12 (20-40 core-h).
- Every "law" claim in the corpus that met a zero-parameter restatement lost to it (B4). Every length claim on the Proteus
  VM met a fraction ruler and lost or shrank (B5). Every label-based heredity count met material attribution and fell by
  ~10x (B10). These three are the priors I would apply to any new claim before reading its result.
