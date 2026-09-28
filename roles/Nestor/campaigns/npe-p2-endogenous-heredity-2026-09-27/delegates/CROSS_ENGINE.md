# CROSS_ENGINE -- shared structure between other engines and Nestor's W1 barrier map (Block H input)

Delegate: repository researcher, read-only over worktree `nestor-s1-forensics` at 086801161. Date 2026-09-27.
Everything below cites a committed file (path:line). Labels: **CONFIRMED** = the owning seat's frozen/preregistered
verdict; **SIGNAL / EXPLORATORY** = measured but not confirmed; **HYPOTHESIS** = the seat's own reading, untested.
No experiment was run for this note.

## 0. The Nestor map being compared (W1)

| id | Nestor claim | status | source |
|---|---|---|---|
| N-ACQ | Donor acquisition is limited by ENCODING ACCESSIBILITY of block-copy: one-byte LDIR/LDDR alias 1/64 -> 39/64 (p = 1e-14). Block-copy encodings are PRESENT in 87/96 plain populations. | CONFIRMED (C-DENSE-COPY) | roles/Nestor/FINDINGS.md:437-445; EXPERIMENT_GRAPH.jsonl:149,151 |
| N-EST | In ffa6, establishment is limited by register state the donor's OWN execution leaves (self-poisoning): STATELESS 11/33 -> 34/42. Reset-on-genome-change is a CLEAN_NULL; 7ae3 not confirmed (3/8 vs 4/8). | CONFIRMED in ffa6 only | FINDINGS.md:447-456; EXPERIMENT_GRAPH.jsonl:157,163,165 |
| N-CTX | The one plain-physics spontaneous donor copies with no OP_SELF, via LDIR/LDDR with register values from "incidental arithmetic on the fixed tape layout". | HYPOTHESIS, n = 1 | W1_REPORT.md:65-66 |
| N-ORD | Barrier order: acquisition -> causal copy/establishment (~0.4) -> sustained heredity; with acquisition relieved, establishment limits. | SIGNAL/CONFIRMED mix | W1_REPORT.md:50-62 |

Two sibling facts matter throughout: NPE is the only one of the three Z80-family engines whose registers persist
across executions. BEE's VM starts every execution at `A=B=C=D=S=T=0` (ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/W2_BEE_LENS.md:68-72,
citing 16fc6c2a:vm.py:82-84). Archaeon's frozen VM does the same (`regs = [0, 0, 0, 0]`, archaeon/lineage/taint_vm.py:39, a
differential-tested shadow of archaeon/z80atlas/vm.py). BEE and Archaeon are therefore natural "STATELESS" physics.

---

## 1. ACCESSIBLE VS REPRESENTABLE

### 1.1 Aphrodite slice 4: the result the operator named (GENUINE, strongest match)

**What it showed, exactly** (roles/Aphrodite/pivot/APHRODITE_ENGINE_REVIEW_7_2026-09-22.md; commit 74f857091, AMENDMENT 8 frozen at
026ccc847):
- **Equal expressivity was certified before any search.** 13,824 output comparisons over macro expansions gave 0 mismatches. The
  ORGAN arm (an evolved fold macro transplanted as a search coordinate) falls back to the full G4 grammar, so "capability available
  only to ORGAN cannot occur by construction" (s0, lines 17-22).
- **Search spaces.** ORGAN coordinate 1.2M candidates vs SCRATCH G4 226M (186x).
- **Discovery within a fixed escrow.** Fixed escrow of 1.5M charges, 16 recipients per arm per family, 3 families:
  ORGAN 9/16, 16/16, 16/16; SCRATCH 3/16, 5/16, 5/16; SHAM 9/16, 2/16, 3/16 (lines 43-56).
- **Attribution.** Every ORGAN success came from inside the macro (9/9, 16/16, 16/16). Every SHAM success came from the G4 fallback
  (s2, lines 64-75). SHAM is the macro with its body rewritten so that it ignores the sequence.
- **SCRATCH could reach the same structure.** SCRATCH independently rebuilt fold-equivalent structure in 5-6/16 recipients, and
  those were exactly its successes. "The organ is not supplying something unreachable; it is supplying something findable that is
  usually not found in budget. That is the definition of a search coordinate" (s5, lines 118-129).
- **Verdict.** STRUCTURAL_SEARCH_LEVERAGE = YES (roles/Aphrodite/STATUS.md:14).
- **Qualifications the seat attached** (lines 150-154, 170-184):
  * gcd_times_first is weak (SHAM ties ORGAN on M2);
  * the 186x ratio is a design choice;
  * the success-conditional median favours SCRATCH (survivorship);
  * D3: the deterministic witness ranks favoured SCRATCH on 2 of 3 families, so the advantage "comes from space density under
    randomised search, not from a conveniently placed witness".
  * Wall-clock figures are contaminated; charge-based endpoints are not (APHRODITE_ENGINE_REVIEW_9_2026-09-22.md:187-190).

**Contrast inside Aphrodite, just as relevant.** Slice 3 first read as leverage but was relabelled CAPABILITY SUPPLY. SCRATCH_B's
grammar could not express the fold at all (0/16 vs ORGAN 16/16), so "the organ did not help a search go faster. It supplied a
mechanism class the substrate could not express" (APHRODITE_ENGINE_REVIEW_6_2026-09-22.md:78-90). Aphrodite then required an
expressivity-equivalence certificate before any leverage claim (REVIEW_7 s7, lines 166-172). Separately, its REACHABILITY
certificate (AMENDMENT_4_2026-09-21.md:48-70; REVIEW_4) found a target that was representable only through a helper and therefore
outside the reachable set. Aphrodite thus has three separate categories: unexpressible, expressible but unreachable in budget, and
reachable.

**Evidence strength.** Confirmed under a frozen amendment, 3 families x 16 paired recipients, with sham control and per-success
attribution. It is a toy arithmetic DSL.

**Shared structure (genuine).** N-ACQ is formally the same experiment. The one-byte alias leaves semantics and ops-mask gating
unchanged, and the original encoding stays legal, so the alias arm's expressible set equals the plain arm's. The effect is a
change in how easily the copier is found by blind variation (1/64 -> 39/64), not a change in what can be expressed. Both engines
measured the same thing: the probability of discovery at fixed expressivity, under randomised generation.

**What Aphrodite has that W1 lacks, and a discriminating comparison.**
1. **Attribution (repo-only, cheap).** For each of the 39 C-DENSE-COPY donors (and the 49 X-DD-DENSE-COPY donors), does the
   competent genome's copy instruction use the ONE-BYTE alias or the original multi-byte encoding? Aphrodite's prediction, if the
   structure is shared: close to 100% alias (as ORGAN 9/9, 16/16, 16/16).
   - Falsifier: a substantial share of DENSE-arm donors copy with the ORIGINAL encoding. The alias would then act on acquisition
     through something other than the encoding's own reachability, for example instruction density or a neighbouring-byte effect.
     That is exactly the Block A alternative.
2. **Sham alias (light CPU).** Add a one-byte alias with the same density but broken semantics: the same byte-frequency footprint,
   decoding to a non-copy op or to LDIR with a corrupted operand register. Aphrodite's SHAM separated "carrying a macro" from
   "carrying the right macro".
   - Prediction if the effect is accessibility: SHAM ~ PLAIN (~1/64).
   - If SHAM raises acquisition, then density or mutation-structure changes carry part of the effect.
3. **Reachability certificate before search.** Aphrodite certified reachable sets by enumeration. Nestor can compute the prior
   exactly: the fraction of random k-byte windows that form a working copy loop under each encoding (see 1.3). This separates "easy
   to discover" from "more effective once discovered", the distinction Block A asks for.
   - If the alias raises the per-tape prior by roughly the observed acquisition ratio, the effect is discovery.
   - If the prior barely moves while acquisition rises about 40x, a post-discovery effect (effectiveness or establishment in
     population) must be at work.

### 1.2 BEE (Bellerophon z80atlas): a second, weaker accessibility coordinate, plus an ablation Nestor lacks

Source: roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md. Preregistered grounding round, 12,130 runs, frozen at a1b066309.
- **G1 acquisition by representation** (line 45-47): VM_COPY (L = 64, adds COPYALL, a whole-tape copy in ONE instruction, per
  W2_BEE_LENS.md:81-83) 8/200 = 4.0% [2.0, 7.7] vs COPY/Z80_64 5/400 = 1.25% [0.54, 2.89]. BYTECODE32 is 1.0%. This is a single
  unpaired contrast inside a descriptive lane, not a preregistered test: an EXPLORATORY ~3x difference with nearly touching CIs.
- **P8 substrate ablations**, preregistered (line 78-86): LDIR off 0/300; **LDIR cost x4 0/300**; undefined-opcode -> HALT 0/300,
  vs base 8/300. "Replication is reachable ONLY through LDIR plus the neutral undefined-byte slide."
- **HISTa** (line 99-110): NOPing every copy byte in 345 historical copiers still lets 36.5% self-replicate. In 124/126 cases a copy
  instruction reappears at a NEW position 1-18 bytes away: "a copier ONE mutation away at many positions ... the replication basin is
  shallow and wide around any tape that already has the setup."

**Shared structure.** BEE also has an acquisition coordinate that is not presence: the execution COST of the same primitive
(x4 -> 0) and the NOP slide (a mechanism for reaching the copy code) each abolish acquisition. BEE therefore shows accessibility
controlled through at least two routes, encoding and cost, of which Nestor manipulated only one.

**Tension with N-ACQ (see s5).** BEE's one-instruction COPYALL raised acquisition only about 3x, not about 40x. BEE's HISTa says
that once the setup exists, the copy opcode is not what limits. In BEE the binding step seems to be the SETUP (pointer registers
aimed at the window), not the copy opcode's encoding.

**Discriminating comparison.** A paired BEE run, COPY/Z80_64 vs VM_COPY on identical seeds (n >= 400 each), with the P8 LDIR-cost
arm added. Nestor adds the mirror arm: DENSE alias with copy cost x4.
- If both engines show "cheaper or shorter primitive -> higher acquisition" with a dose response, accessibility is a shared
  coordinate.
- If BEE's COPYALL effect stays near 1x once paired, the NPE effect depends on how NPE's copy setup is encoded, and the shared
  claim must narrow to "the binding sub-step's reachability". The discriminator is which sub-step: the setup or the copy op.

### 1.3 Archaeon: the per-tape prior method (GENUINE method link)

Archaeon measured the random-tape prior of copiers directly: 33,554,432 arrivals per arm; EXACT_GATED 265, EXACT_UNGATED 0; 7.9 per
million (census 9.6, CI 7.8-11.7) (archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md:148-156). Its lens records "copier incidence is
lottery-consistent (lambda 6.86 vs 1 survivor)" (ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/A0_ARCHAEON_LENS.md:50) and recommends
censusing about 10^7 random tapes without worlds (archaeon/z80atlas/pivot/Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.md:329-334).

**Experiment X-PRIOR (light CPU, no world).** Apply Archaeon's census design to NPE: execute 10^6-10^7 random pair-tape genomes
against a fixed partner and fresh state, under PLAIN vs DENSE, and count fresh-start-competent copiers (the L2 assay).
- This gives the prior ratio DENSE/PLAIN directly and settles 1.1 item 3.
- Run the same census under BEE's representations to put three engines' priors on one axis: copiers per million random tapes.

### 1.4 Ensorain LM01: HYPOTHESIS only

ensorain/PREREG_WTP_LM01.md:26 defines "Accessible" as "operationally accessible to the acting system within its per-query budget",
tested by index ablation. That is stored-but-not-reachable-in-budget memory. The prereg is frozen and NOT LAUNCHED
(roles/Ensorain/STATUS.md:5-8), so there is no result. Record it as a future comparison only.

---

## 2. GENOME VS EXECUTION STATE

### 2.1 Aether: a hidden carried flag breaks a bytes-only causal predicate (GENUINE, measurement-level)

Aether/AETH-03/PROPAGATION_ASSAY_AUDIT.md:35-42:
- Twins with identical five-byte site state but different `rcv` flags can occur.
- "A flag-only difference produced visible differences" in 20/20 trials.
- A BYTES-ONLY predicate records 32 locality violations; the full predicate records 0.
- The predicate now compares "every carried state generically (`World.extra`)".
- Status: an audited instrument result (synthesis at Aether/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:10-14).

**Shared structure.** In Aether and in NPE, state that is not part of the nominal "material" (Aether's template bytes, NPE's genome
bytes) causes later visible behaviour. An instrument that keys on bytes alone misattributes the cause. Nestor's own W1 lesson,
"measure competence from the state the organism actually runs from, not only from a fresh state" (W1_REPORT.md:93-94), is the NPE
form of Aether's `World.extra` repair.

**Discriminating comparison: one-bit/one-register twins in NPE (TH-011 transfer).** Take a stalled ffa6 donor at its self-poisoned
state and make twins that differ in ONE register (all genome bytes identical). Measure which single-register differences flip
"copies in-world" from 0 to 1.
- If a small, specific register subset carries the poisoning, NPE has a hidden-state carrier in Aether's sense.
- If no single-register twin flips the outcome but the full reset does, the poison is a joint state. That is Ananke's "CHANCE =
  needed but not carrying" class (2.3).
- The same twin design on 7ae3 donors tests the Block B question directly. Prediction if the structure explains the split: 7ae3
  donors show no register whose twin flips copying.
Aether owns the instrument (ops/threads/TH-011.md), so coordinate with that seat.

### 2.2 Ananke PTE: evolved machinery that normalizes execution state (GENUINE, and the most useful for Block F)

roles/Ananke/research/C1B_REVIEW_AND_MECHANISMS.md:28-33,94-105:
- In PTE-M3 "every site converges onto rule 0 during trial 0 and never changes again. Freezing SETRULE after two trials changes
  nothing. Freezing it from the start leaves sites on random rules, cuts emissions 4x and kills transport. SETRULE is a one-time
  population bootstrap."
- Rule state r is initialized at random (engine.World.__init__; roles/Ananke/research/threads/T-M3-1_setrule_bootstrap.md:3-5).
- Evidence strength: SPIKE-level, a few champions, not preregistered. The seat itself suspects an init-escape artefact (C-3, lines
  118-122; thread T-M3-1).

**Shared structure.** The evolved program's competence depends on execution state outside its rule "genome", and selection found
code that DRIVES that state to a working value before the function runs. This is the evolved answer to the problem N-EST describes.
In ffa6 the donor's own execution leaves bad state; in PTE the population evolved a state-reset bootstrap. It is a direct precedent
for Block F's question "CAN EVOLUTION DISCOVER STATE ROBUSTNESS?". The caveat: PTE is a GA with explicit selection on the task, and
NPE has no such outer selector.

**Discriminating comparison: the state-robustness census.**
- **NPE side.** Take DENSE (not STATELESS) runs that did establish (23/60 in X-DD-STATELESS's DENSE arm, EXPERIMENT_GRAPH.jsonl:161).
  For each established donor, test whether its genome contains a prefix that writes the registers the copy loop reads before the
  loop runs (a "bootstrap"), vs donors whose copy loop is simply insensitive to those registers. Count with Ananke's T-M3-1
  classes: BOOTSTRAP, INSENSITIVE, DEPENDENT.
- **PTE side.** T-M3-1 step 2.
- **Shared-structure prediction.** Where persistent state matters, established lineages are enriched for state-normalizing
  prefixes relative to stalled donors.
- **Falsifier.** Established and stalled ffa6 donors do not differ in any state-normalizing code. Establishment then escaped the
  poison by luck of state (for example, which partner was executed first), not by machinery. That would favour an
  execution-order/partner reading (Block A).

### 2.3 Cosmos C3 and Ananke's carrier swap: the instrument for "present vs used" state (GENUINE method link)

- **Cosmos P1/P2** (roles/Cosmos/c3/S1_PREREG_P1P2_GATE.md:13-27): P1 decodability vs P2 causal utility, tested by a full-state
  swap at a chosen time. A planted passive register carries 1.96 bits with effect 0.000 in 5/5 seeds (lines 71-73). The gate run
  FAILED on a weak-history system, and v3 was amended; this is an instrument under construction, not a science result.
- **Ananke's mirror-pair carrier swap** (SYNTHESIS_2026-09-27.md:45-51): FLIP = carries, NO-EFFECT = irrelevant, CHANCE = needed but
  not carrying.

**Use for NPE.** Swap the full register file between a poisoned ffa6 donor and its fresh-state twin at the start of an in-world
execution.
- Poisoned registers into a fresh donor should kill copying (FLIP).
- Fresh registers into a poisoned donor should restore it.
- Doing this per register family tells "state carries the failure" apart from "state is needed but the failure lives elsewhere".
This is a sharper form of X-DD-SELFSTATE.

### 2.4 The two STATELESS siblings: a built-in control Nestor has not used

BEE and Archaeon reset registers every execution (s0), yet both still fail to establish most of the time:
- BEE: only 39.4% of spontaneous origins are SUSTAINED, and 95-100% of RANDOM runs in LOCAL/NICHES/GRAPH cells go extinct
  (GROUNDING_REPORT.md:56-59).
- Archaeon: 128-gated lineages "fail because they cannot GROW" (ENVGATE01_REVIEW_2026-09-24.md:206).
- Reading: register persistence is ONE cause of establishment failure, specific to a physics that has it. It is not the general
  establishment barrier. This agrees with the 7ae3 null and argues against generalizing N-EST (see s5).

### 2.5 Archaeon causal lens: register state is invisible to the heredity contract (instrument gap)

The contract types MATERIAL as "immutable carried state at a declared granularity"
(archaeon/causal_lens/CAUSAL_LINEAGE_CONTRACT_v0.2.md:37). It has no field for mutable execution state that decides whether a
genome reproduces. Under the lens, an ffa6 self-poisoned donor and a competent one are identical HUs.

Proposed FALSE_FRIENDS entry: "fresh-start competence (NPE L2) != competence in the state the organism actually runs from". Offer
it to Archaeon as the execution-state analogue of FF-20 (non-material but causally load-bearing, which Ananke already made for PTE
channel state: roles/Ananke/research/CROSS_ENGINE_THREADS.md:30-37). Repo-only work.

---

## 3. ENVIRONMENT AS MACHINERY

### 3.1 Archaeon: every random-origin exact copier is environment-gated (GENUINE, strongest match to N-CTX)

- Of 33.5M random arrivals, EXACT_GATED 265 and EXACT_UNGATED **0** (ENVGATE01_REVIEW_2026-09-24.md:153): a random tape that
  copies exactly does so only when the environmental input byte takes a specific value.
- "Exact copies occur iff the gate is in the arm's alphabet ... the gate controls exact copying, not reproduction" (lines 144-147).
- Blocking the viable input band suppresses establishment. This is CONFIRMED and replicated under genetic identity: U 24 vs BAND0 5,
  12+/2- blocks, Page's L p = 0.001 (archaeon/envgate2/VERDICT_2026-09-26.md:27-33,53-56;
  archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md:12).
- The window-rescue MECHANISM was NOT supported (VERDICT:56-60), and ENVGATE-01's rescue claim was downgraded to
  GATING_PARTIALLY_SUPPORTED (archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md:5-14).
- **Endogenous escape.** In the block-15 takeover world the resident was "an EXACT_UNGATED copier (exact at all 256 inputs),
  evolved inside the world. Gating DISAPPEARED once a lineage took over" (ENVGATE01_REVIEW:223-225). This is one world, an
  observation and not a test.

**Shared structure.** In Archaeon and in N-CTX, the cheapest copiers random material produces do not encode every copy parameter
themselves; part of the parameter comes from context. In Archaeon it comes from the environmental input byte. In NPE's single
donor it is hypothesized to come from leftover registers plus the fixed tape layout. Archaeon also has one case where evolution
REMOVED the dependence. That is Block F's "can evolution discover state robustness", in the environment-dependence form.

**Discriminating comparison: X-COPY-PARAM-PROVENANCE (light CPU, largely replay).** Archaeon's taint VM labels every register value
by source: ('E', p) own tape, ('N', q) neighbour, ('I',) input, ('K',) constant or zero-initialised register (taint_vm.py:6-12).
Build the same labelling for NPE's copy-loop operands (source pointer, destination pointer, count register at LDIR/LDDR time),
adding a label ('R',) for "register value carried from a previous execution". Then measure, per engine, the fraction of copy
operands whose value originates OUTSIDE the copier's own genome:
- Archaeon: I-labelled share in gated copiers vs the evolved ungated resident.
- NPE: R- or layout-derived share in the SELF-free donors (the 39 + 49 DENSE donors plus the plain-physics one) vs SELF+LDIR donors
  such as 7ae3.
- **Prediction if the structure is shared.**
  * Spontaneous (young) copiers have a high non-genomic operand share in both engines.
  * Lineages that establish and persist show a falling share: the ungated resident; NPE donors that bootstrap their registers (2.2).
  * In NPE, a high R-share predicts sensitivity to STATELESS, in either direction.
- **Falsifier.** NPE's spontaneous donors take their copy operands from their own genome bytes (E-labelled). N-CTX would then be
  wrong, and the Archaeon parallel would fail at the mechanism level.
- **Cross-check on Block B.** If ffa6 donors are R-dependent and 7ae3's SELF+LDIR route is E-dependent, that alone could explain
  why STATELESS matters in ffa6 and not in 7ae3.

### 3.2 BEE: every first self-replicator is built by another organism's writes (GENUINE, scaffolded origins)

G6: 160/160 first self-replicators are BUILT_BY_COPY, including all 87 origins at tick <= 41 while the initial organisms were
still alive. "No initial random tape and no mutated initial tape became the first self-replicator in any run"
(GROUNDING_REPORT.md:60-68). Preregistered, and it held.

**Shared structure (partial).** Acquisition in BEE is itself scaffolded by other organisms' copy activity. NPE's donors arise on the
pair tape, where one program executes over another's bytes. Archaeon's cross-engine synthesis states this as "Origins are
scaffolded" across three engines (D_Z80_SYNTHESIS.md:83-92), with the NPE leg explicitly limited to the pair-tape architecture.

**Discriminating comparison.** Run BEE's G6 BUILT_BY_COPY test on NPE: for each first fresh-start-competent donor in C-DENSE-COPY,
was its genome written by another organism's pair-tape execution, or did it arise in place by mutation? Replay-only.
- If NPE donors are also 100% built-by-copy, "acquisition is scaffolded" becomes a three-engine regularity.
- If NPE donors arise by in-place mutation, NPE acquisition is a different kind of event from BEE's, and the shared claim fails for
  NPE.

### 3.3 Archaeon host-mediated reproduction, and the NPE claim that was WITHDRAWN

- Archaeon: an inert host executes a resident copier and emits the resident's genome. This stands on material-typed execution
  accounting (archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md:16-17; A0_ARCHAEON_LENS.md:47-49: 2,570 of 3,594 block-15 births run resident material in place).
  It is genome amplification, not origination.
- The NPE "host-conditioned reproduction" signature (AN3) is **WITHDRAWN**. The 34 events were predecessor-rule births, only 6/34
  pass P-11, and the necessity leg used a diagnostics field (ops/threads/TH-003.md:9-15; D_Z80_SYNTHESIS.md:92-101).
- What survives for NPE: P-11-failing overwrite events are cross-execution-rich (46% vs 11%). Do NOT cite AN3 as NPE evidence for
  "environment as machinery".
- The cross-engine host-conditioned assay is re-assessed as NOT_READY until its NPE arm is restated on P-11-causal events
  (ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/F_FRONTIER.md:16-19).

### 3.4 BEE's harness copy channel: environment supplying heredity outright (cautionary)

- Under POLLINATION v1, migration manufactured copies. Switching the channel from COPY to MOVE took extinction from 0/150 to 148/150
  and spontaneous replication from 20% to 1.3% (GROUNDING_REPORT.md:71-77). CONFIRMED_CAUSAL.
- The same "harness copies credited to organisms" error was made independently by all three teams (D_Z80_SYNTHESIS.md:41-50;
  ops/threads/TH-014.md).
- **Relevance to Nestor.** Before claiming that any context-supplied copier machinery is organismal, enumerate every channel that
  moves bytes in NPE: migration under NICHES_HIGH_MIG in ffa6, reservoir, splice. ffa6 is the HIGH_MIG cell, which makes this an
  untested confound for the ffa6/7ae3 split.

### 3.5 Aether: persistence supplied by a neighbour's energy (WEAK, noted)

- "Edges end mostly because their source runs out of energy (89%). Long edges exist only where a neighbour keeps feeding energy"
  (Aether/AETHER_ENGINE_CARD.md:133-135).
- NPE's own E-7 (newborn starvation fixed by a conserved energy transfer at birth, FINDINGS.md:230-241) is the same "persistence
  paid for by context" shape.
- Recorded, but no experiment is proposed. Aether has no reproduction, and the parallel adds nothing that E-7 does not already test.

---

## 4. ACQUISITION VS ESTABLISHMENT

**Cross-engine statement already on record.** Archaeon's three-lens synthesis says: "Acquisition, establishment and maintenance are
different barriers, and the hard one is not acquisition" (D_Z80_SYNTHESIS.md:75-81), citing NPE W1, BEE, and Archaeon ENVGATE.

| engine | acquisition | establishment given acquisition | source |
|---|---|---|---|
| NPE (plain) | 1/64 | (1 case, ran away) | FINDINGS.md:437-445 |
| NPE (DENSE) | 39/64 | 15/39 runaway; ffa6 11/33 -> 34/42 under STATELESS | EXPERIMENT_GRAPH.jsonl:151,165 |
| BEE (v2, random) | 2.3% of fresh runs | 39.4% SUSTAINED (G2a >= 50% FAILED) | GROUNDING_REPORT.md:45-59 |
| Archaeon | 7.9 exact copiers / 10^6 arrivals | set by environment: viable-offspring inputs per copier U 4.10 ... BAND 0; branching R0 ~ 60 x k/256 = 0.96 / 0.73 / 0.23 / 0 | ENVGATE01_REVIEW:26-31 |

**Genuine shared structure.** In all three engines, establishment is a branching problem: a first copier must produce children
that are themselves copiers often enough (R0 > 1). Archaeon measured R0 directly from an offspring-viability map; NPE and BEE have
not. The table also shows the ordering is not fixed. In NPE plain physics, acquisition (1/64) is harder than establishment (~0.4),
which contradicts "the hard one is not acquisition" for that condition. Which barrier dominates depends on which aid is present.

**Discriminating comparison: X-R0 (light CPU, replay plus single-interaction assays).** In each engine, take first-generation
children of newly acquired copiers and measure the fraction that are themselves copiers. This is TH-015's capacity-transmission
measure; Archaeon block 13 already has SELF_COPY 86.7%, HOST_EXECUTION 47.0%, NEIGHBOUR_COPY 35.3%, ORIGINATION 0%
(ops/threads/TH-015.md:11-12). Combine it with children per copier per lifetime to get R0.
- **NPE arms.** DENSE vs STATELESS, ffa6 vs 7ae3. Measure the child's copying capacity both from a fresh state and from its
  realized state.
- **Shared-structure prediction.** Establishment probability is monotone in measured R0 across engines and arms. In NPE, the
  STATELESS effect in ffa6 comes entirely through the child-capacity term under realized state; the fresh-state capacity term is
  unchanged.
- **Falsifier.** In NPE, STATELESS changes establishment without changing measured R0 under either state. Establishment would then
  be governed by something other than offspring viability, such as spatial or ecological displacement, and the branching reading
  would not transfer.

---

## 5. Evidence from other engines that contradicts or limits Nestor's reading

1. **Register persistence is not a general establishment barrier.** BEE and Archaeon run fresh registers every execution and still
   fail to establish most spontaneous copiers (2.4). This is consistent with the 7ae3 null. N-EST must stay scoped to ffa6 or to a
   physics with persistent state, as W1 already scopes it.
2. **The size of the accessibility effect depends on the substrate.** BEE's one-instruction COPYALL gave about 3x (unpaired, CIs
   nearly touching), and BEE's HISTa says the copy opcode is one mutation away once the setup exists (1.2). If NPE's ~40x is real,
   something about NPE's copy setup makes the opcode's encoding binding. This supports Block A's challenge: the alias may act
   through a feature beyond "shorter".
3. **Machinery conservation depends on the encoding.** NPE C-CORE conserves OP_SELF/LDIR as founder MATERIAL. Archaeon's block-13
   dominant lineage keeps founder material at 0.0 at every machinery position, although 82% of its births are exact self-copies
   (ops/threads/TH-013.md:14; D_Z80_SYNTHESIS.md:56-73, attributed to neutral bits in executed opcodes). Nestor should not state
   "the copy core is conserved" as a law of copy-selected worlds.
4. **Aphrodite's D3 caveat applies directly.** Its leverage came from "space density under randomised search", not from where the
   witness sat. The NPE alias raises the density of copy-capable bytes, which is Block A's "changed instruction density" alternative.
   Aphrodite's result therefore does not settle whether NPE's effect is encoding length per se. Only the sham alias in 1.1 item 2
   and the attribution in 1.1 item 1 can.
5. **AN3 is withdrawn.** Do not use "host-conditioned reproduction in NPE" as support for environment-as-machinery (3.3).
6. **"The hard one is not acquisition"** (Archaeon synthesis) holds for NPE only with the DENSE aid present (4).

---

## 6. Candidate connections REJECTED (and why)

| candidate | why rejected |
|---|---|
| Cosmos C0-C2 phase-boundary law as "environmental coupling" | It is the economics of a memory policy (SELECTIVE_PAYS: selective vs full-log fitness margin, prometheus/cosmos/phenomenon.py:1-14). The seat calls it "a planted-invariant recovery, not a discovery" (roles/Cosmos/campaigns/HANDOFF_2026-09-23.md:31-35). There is no reproducer or heredity; only the C3 swap INSTRUMENT is kept (2.3). |
| Ensorain WTP-03 "learning-time / lifetime ratio decides inhabitability" (ensorain/ENSORAIN_WTP03_REPORT.md:163-170) as acquisition-before-death | The shape looks like establishment, but the objects are online learners, not reproducers. All 9 specimens were adjudicated known completion physics (roles/Ensorain/STATUS.md:30-37). No discriminating joint experiment exists. |
| Ensorain LM01 "accessible" memory | The concept matches, but the prereg is unlaunched and has no result (1.4). Deferred, not rejected on merit. |
| Ananke X-1 content vs timing carriers with Aether | Real, but about signal transport, not heredity or reproduction. It says nothing about genome vs state in a reproducer beyond 2.3's instrument. |
| PTE GA crossover / continuity (archaeon/causal_lens/V02_REGRESSION_REPORT.md:67-78) | The lens rates in-world heredity NOT_APPLICABLE for PTE (archaeon/causal_lens/pivot/PORTABILITY01_REVIEW_2026-09-26.md:185-191). Crossover continuity is an operator property, not an organism's. |
| Aether TH-009 "frozen medium" as an analogue of cargo erosion | A medium that stops changing without noise is not selection eroding non-copied bytes. The mechanisms are opposite (no turnover vs full turnover). Analogy only. |
| Aphrodite Tiers 3A-3C and A15/A16 (bounded RSI) | These concern recursive improvement of the improver; all are NO or UNTESTABLE (roles/Aphrodite/STATUS.md:13-25). Only slice 3/4 and the reachability certificates bear on accessibility. S3 "endogenous abstraction" (a donor derives the schema itself, APHRODITE_ENGINE_REVIEW_11_2026-09-24.md:25-35) is a tempting parallel to "can evolution discover accessibility", but the derivation is a designed anti-unification step, not variation plus selection. At most it is a design reference for Block F. |
| BEE coupling campaign (task competence maintained only under an explicit copy-resource ledger) | It concerns cargo (task code), not copying machinery. It belongs to TH-013 (cargo erosion), not to any of the four structures here. |
| Aether one-bit twin as evidence | The instrument transfers (2.1); Aether's science results (locality, rcv) do not bear on reproduction. |

---

## 7. Proposed cross-engine Threads (only where a comparison discriminates)

| thread | engines | question | cheapest discriminator | resource |
|---|---|---|---|---|
| XE-ACC-1 alias attribution + sham | NPE (Aphrodite design) | Is N-ACQ accessibility of the copy op, or density or neighbourhood? | donor-encoding attribution on preserved genomes; then SHAM-alias arm | repo/replay, then light CPU |
| XE-ACC-2 per-tape prior | NPE, BEE, Archaeon | Copiers per 10^6 random tapes under each encoding and cost | Archaeon-style census, no worlds | light CPU |
| XE-STATE-1 register twins / carrier swap | NPE (Aether + Ananke + Cosmos instruments) | Which registers carry ffa6 self-poisoning; why not in 7ae3 | one-register twins and full swaps on stalled donors | light CPU |
| XE-STATE-2 evolved state normalization | NPE, PTE | Do established lineages carry state-normalizing prefixes (BOOTSTRAP / INSENSITIVE / DEPENDENT)? | census of established vs stalled donors; PTE T-M3-1 | repo/replay |
| XE-ENV-1 copy-operand provenance | NPE, Archaeon | Do spontaneous copiers take copy operands from context (input, carried registers, layout), and does the share fall in established lineages? | taint-label copy operands (add label R) | light CPU |
| XE-ENV-2 built-by-copy origins | NPE, BEE | Are NPE's first donors written by others (BEE G6)? | replay of C-DENSE-COPY donor origins | replay |
| XE-EST-1 R0 decomposition | NPE, BEE, Archaeon | Is establishment governed by child copier capacity x children, and does STATELESS act through it? | first-generation child capacity (TH-015) x children per copier | light CPU |
| XE-LENS-1 false friend "fresh-start competence" | NPE -> Archaeon lens | Register the execution-state blind spot of MATERIAL-only heredity | FALSE_FRIENDS entry | repo only |

Coordination notes: TH-011 belongs to Aether and TH-013/015 to Archaeon, and Bellerophon owns BEE runs. Before any run, confirm
that the ffa6 migration/harness channel (3.4) has been excluded.
