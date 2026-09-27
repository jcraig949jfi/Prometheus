# Nestor backlog -- endogenous heredity and reproductive machinery (P2, opened 2026-09-27)

Living document (Block O): Threads are killed, split or added as evidence arrives; the change log is at the
bottom. Evidence pointers are graph node ids (`roles/Nestor/EXPERIMENT_GRAPH.jsonl`) or files in this campaign.
Inputs: W1 (`../npe-w1-donor-discovery-2026-09-26/W1_REPORT.md`), P2 delegates
(`delegates/EXTERNAL_RESEARCH.md`, `delegates/CROSS_ENGINE.md`, `delegates/corpus/CORPUS_ANALYSIS.md`).
Resource classes (descriptive, for dispatch): REPO (repo/literature only), LIGHT (<= 2 processes, minutes-hours,
existing data or VM assays), LEASED (world runs on a leased CPU pool), GPU, MULTI (multi-host), LENS (new engine or
instrument work).

The working decomposition (Block M; only stages an experiment can separate are kept):

    variation -> machinery ACCESSIBLE -> candidate donor exists (fresh-start competent)
      -> copying happens IN CONTEXT (entry state, side, partner) -> causal copy certified
      -> descendant competent -> descendant copies in context -> lineage persists -> machinery adapts

---

## A. Acquisition of reproductive machinery

**T-ACQ-1 Alias attribution + sham (XE-ACC-1).**
- Question: Is C-DENSE-COPY's gain carried by the 1-byte copy alias itself, or by density/neighbourhood effects of
  adding any 1-byte opcode?
- Why: Block A. Aphrodite slice 4 used exactly these two controls; W1 lacks both.
- Evidence: 1,251/1,278 competent dense-origin genomes use ONLY the alias (corpus Q1). That is attribution by
  content; causal attribution is not yet done.
- Prior art: Aphrodite slice 4 (74f857091); Avida mem-size.
- Uncertainty: high for the sham.
- Cheapest discriminator: (i) re-assay dense donors on the stock VM (LIGHT); (ii) a SHAM arm with the same 1-byte
  density where the alias decodes to a non-copy op (LEASED, ~100 runs).
- Lens: NPE. Resource: LIGHT then LEASED.

**T-ACQ-2 Presence vs encoding (X-P2-PLANT).**
- Question: Does planting a 2-byte block copy in every initial genome recover the dense effect?
- Evidence: queued (P2).
- Discriminator: X-P2-PLANT, paired seeds with W1 PLAIN/DENSE.
- Resource: LEASED.

**T-ACQ-3 Byte-distribution tuning instead of re-encoding.**
- Question: Keep ED B0 but raise P(ED), P(B0) until the pair's per-program probability matches the alias. Do donor
  rates match? (Information cost vs "one instruction".)
- Prior art: Adami & LaBar 2015; Knierim et al. 2026 (tuned distributions up to 25x).
- Discriminator: an initial + mutation distribution arm. Resource: LEASED.

**T-ACQ-4 Appearance hazard baseline.**
- Question: Is the pair-tape soup a better or worse SEARCH for donors than a random walk / uniform sampling scored
  by the same certified test?
- Prior art: Knierim 2026 (mutation walk ~9.4e4 programs vs soup ~5e6 in BFF).
- Discriminator: programs-tested-to-first-donor under uniform bytes, the empirical soup distribution, and mutation
  walks. Resource: LIGHT (no world; assay only).

**T-ACQ-5 Mutational reachability of the encoding (cell topology).**
- Question: In Z8_SLOTTED with an OPERAND mutation operator, opcode bytes at slot starts are never mutated; can
  an ED prefix ever be created there? Does that make 2-byte block copy unreachable in ffa6 but not in 7ae3 --
  and is the 1-byte alias's advantage partly a mutation-topology effect?
- Evidence: world.py _mutate (SLOTTED branch); W1 L1c presence 87/96 in PLAIN.
- Discriminator: exact per-generation probability of creating ED B0 / E5 by one mutation under each topology
  (analytic + LIGHT census).
- Resource: REPO/LIGHT.

**T-ACQ-6 Which primitive's accessibility limits: copy vs self-location.**
- Question: Add a 1-byte SELF alias instead of a 1-byte copy alias. Which raises donor acquisition more?
- Prior art: Avida mem-size.
- Evidence: corpus -- 95.7% of competent donors are SELF-free, which predicts a SELF alias does little.
- Resource: LEASED.

**T-ACQ-7 Report hazards, not horizon probabilities.**
- Question: Re-express 1% -> 60% and 0.33 -> 0.81 as per-execution / per-program hazards.
- Why: pitfall 6 in EXTERNAL_RESEARCH.md.
- Resource: REPO (reanalysis).

## B. Establishment

**T-EST-1 ffa6 vs 7ae3: which cell axis (X-P2-BRIDGE).**
- Question: representation (slot-aligned, no frame shift) or structure (niches, migration)?
- Evidence: the two cells differ in exactly these two axes; C-STATELESS 7ae3 3/8 -> 4/8, ffa6 8/16 -> 19/21.
- Discriminator: X-P2-BRIDGE (2 x 2 cells x state, implanted donors). Resource: LEASED.

**T-EST-2 What in the fresh state rescues establishment (X-P2-REGSTATE).**
- Question: carried vs zero vs other constant vs random registers.
- Why: the literature says every soup resets to useful values, and W1's competence ruler assays from zeros.
- Discriminator: X-P2-REGSTATE. Resource: LEASED.

**T-EST-3 Position (side) dependence.**
- Question: 1,052 of 1,154 side-specific copiers work only on side 0 (corpus Q4). Is establishment limited by how
  often a donor is paired on side 0 with a usable entry state?
- Discriminator: log the side of each founder execution and its outcome; compare with a world where the donor is
  always side 0 (fixture). Resource: LEASED (small).

**T-EST-4 R0 decomposition (XE-EST-1).**
- Question: Is establishment = P(first copy in context) x (children per copier) x (child copy capacity)? Which
  factor does STATELESS move?
- Discriminator: branching-process estimate from X-P2-BRIDGE stage records. Resource: LIGHT.

**T-EST-5 Who inherits the state (maternal-provisioning analogue).**
- Question: The victim/offspring keeps its OWN old registers when it is overwritten by a copy. Arms: offspring
  gets the donor's post-run registers / keeps its own / zeroed; parent keeps / zeroed.
- Why: separates "parent poisoned" from "offspring inherits unusable state" (Block E).
- Prior art: Avida EPIGENETIC_METHOD / inherit-registers settings (no published study found).
- Resource: LEASED.

**T-EST-6 Hijack via carried state (Tierra hyper-parasite analogue).**
- Question: Can a partner that leaves registers pointing at itself get copied by a donor that trusts carried or
  zero state? Is carried state an exploitation channel?
- Resource: LIGHT (fixture) then LEASED.

**T-EST-7 Implanted-donor establishment baseline vs published 22% (BFF).**
- Question: Under matched conditions, does NPE establishment sit near the BFF reference once side and mutation
  are matched?
- Resource: LEASED.

## C. Descendant competence

**T-DC-1 Stage chain S1-S5 (X-P2-BRIDGE records).**
- Question: accepted copy -> certified copy -> competent descendant -> descendant's certified copy -> runaway.
  Where does each arm fail?
- Resource: LEASED (running).

**T-DC-2 The child starts from the victim's registers.**
- Question: Under persistence, a child's first execution uses the overwritten organism's old state. Does child
  competence in context depend on that inherited slot state?
- Discriminator: T-EST-5 arms, plus the child's copy rate from the victim state measured at birth.
- Resource: LEASED.

**T-DC-3 Knockout and lesion scans of first donors.**
- Question: all 255 substitutions per byte (lethal, neutral, beneficial for certified copying). Compare self-
  addressing vs zero-borrowing donors, and 1-byte vs 2-byte copiers.
- Prior art: Ofria 2002; Lenski 2003; Cicala 2026 robustness hierarchy.
- Resource: LIGHT (assay only, ~50 donors x 64 x 255).

**T-DC-4 Evolvability / sterility of certified donors.**
- Question: monoclonal evolution from each donor; do descendants gain new certified behaviour or change length,
  or are some donors evolutionary dead ends?
- Prior art: LaBar et al. 2015; C G et al. 2017.
- Resource: LEASED.

## D. Architecture: self-location and environment as machinery

**T-CTX-1 SELF-free, zero-borrowing copiers are the norm (corpus Q1, Q4).**
- Status: established descriptively. 95.7% of competent donors are SELF-free; offset-64 block copy; addresses
  from never-written zero registers or aligned immediates; side-0 only in 1,052 cases.
- Next: publish as a finding; hand to T-CTX-2 and T-END-1.

**T-CTX-2 Copy-operand provenance (XE-ENV-1).**
- Question: For each copy event, did HL/DE/BC come from the genome's own writes, from never-written zero state,
  from carried state, or from tape layout? Does the environment's share fall in established lineages?
- Instrument: register taint labels (z8taint extension).
- Resource: LENS + LIGHT.

**T-CTX-3 Side-1 copiers (102 in corpus).**
- Question: What do side-1-only copiers exploit? Is it the partner's writes, which would make them
  partner-scaffolded?
- Resource: LIGHT.

**T-CTX-4 Built-by-copy origins (XE-ENV-2).**
- Question: Are first donors written by another organism's copying (BEE: all 160 first replicators were), i.e. is
  acquisition itself partly an ecological product?
- Resource: LIGHT (replay with birth provenance).

**T-CTX-5 Shorter evolutionary path.**
- Question: Is "borrow the environment's addressing" a shorter path than explicit self-location?
- Discriminator: minimal donor length / count under zero-state vs random-entry-state certification.
- Prior art: C G et al. 2017 (914 of 26^8).
- Resource: LIGHT.

## E. Endogenous transitions (North Star, Block N)

**T-END-1 Endogenous state robustness.**
- Question: Does a lineage founded by a zero-borrowing (poisoned) donor evolve self-addressing machinery?
- Evidence: X-P2-ENDOSTATE CLEAN_NULL for multi-genome early populations (already robust); 13 runs go from poisoned
  early genomes to robust late ones. Lineage identity is unresolved -> X-P2-LINEAGE.
- Resource: LEASED.

**T-END-2 Endogenous accessibility.**
- Question: On the stock VM, do lineages find alternative copy mechanisms (stack-based copiers, as in the 2024/2026
  Z80 soups; LD/INC loops) or byte-frequency shifts that make ED B0 easier to reach?
- Discriminator: long plain-VM runs with a copy-mechanism classifier. Resource: LEASED/MULTI.

**T-END-3 Evolution of evolvability of the copier.**
- Question: Do established lineages become more mutationally robust at the copy core (C-CORE's SELF+LDIR
  conservation plus T-DC-3 lesion profiles over time)?
- Resource: LIGHT on existing lineages, LEASED for new.

**T-END-4 Environment-dependence decay.**
- Question: Along a lineage, does dependence on zero-state / layout addressing fall (T-CTX-2 over time)? This is
  the direct test of "the system modifies the context-dependence of its machinery".
- Resource: LENS + LEASED.

## F. Instruments and rulers

**T-INS-LINEAGE Longitudinal lineage-tagged genome capture.**
- Question: Hamming distance cannot separate within-lineage turnover from replacement (X-P2-ENDOSTATE).
- Discriminator: capture genomes with anc / lineage labels and z8taint material. Resource: LENS (small).

**T-INS-ENTRY Certify from the life state.**
- Question: The COMPETENT ruler assays from zeros, so donors are selected to work from zeros. Record, and sweep, the
  entry register state in every certification.
- Resource: LENS.

**T-INS-HAZARD Hazards over horizons.** Same as T-ACQ-7, for all endpoints.

**T-INS-5GEN Chained-generation detector.**
- Question: Require stability over >= 5 chained generations and >= 10 noise partners (Knierim 2026) as a
  secondary ruler; check whether it changes any W1/P2 verdict.
- Resource: LIGHT.

**T-INS-SHADOW Neutral-shadow persistence control (Bedau).** Resource: LIGHT.

**T-INS-STEP LDIR step accounting.**
- Status: checked. LDIR is charged per byte against the budget (z8.py). BC = 0 means 0x10000, capped by the
  remaining budget. The alias uses the identical code path.
- Next: confirm the alias did not change step accounting (it cannot: same op2 branch).

## G. Parameters of the world

**T-WLD-1 Error threshold.** A mutation-rate x genome-length sweep for certified lineages (q^L sigma > 1;
survival of the flattest). Resource: LEASED.

**T-WLD-2 Step budget / metabolic penalty.** Does penalising steps select conditional halting and reduce stale
state? Resource: LEASED.

**T-WLD-3 Spatial structure.** Grid niches with migration in {0, 0.05, 0.5} (Cicala 2026). Relevant to the ffa6
structure axis. Resource: LEASED.

## H. Cross-engine (from delegates/CROSS_ENGINE.md)

- **XE-ACC-1:** see T-ACQ-1.
- **XE-ACC-2:** copiers per 10^6 random tapes under each encoding and cost (with BEE, Archaeon). LIGHT.
- **XE-STATE-1:** one-register twins / carrier swap on stalled donors. Partly done by corpus Q3. LIGHT.
- **XE-STATE-2:** evolved state normalization -- BOOTSTRAP / INSENSITIVE / DEPENDENT census of established vs
  stalled donors (with Ananke PTE T-M3-1). REPO/LIGHT.
- **XE-ENV-1:** see T-CTX-2. XE-ENV-2: see T-CTX-4.
- **XE-EST-1:** see T-EST-4.
- **XE-LENS-1:** register "fresh-start competence" as a FALSE_FRIEND in Archaeon's lens (a material-only heredity
  ruler is blind to execution state). REPO.

---

## Change log
- 2026-09-27 opened (P2): 40 Threads from W1, delegates, and P2 early results.
- 2026-09-27 T-END-1 narrowed after X-P2-ENDOSTATE CLEAN_NULL (establishment sorts founders in multi-genome early
  populations); lineage-identity question split out as T-INS-LINEAGE / X-P2-LINEAGE.
