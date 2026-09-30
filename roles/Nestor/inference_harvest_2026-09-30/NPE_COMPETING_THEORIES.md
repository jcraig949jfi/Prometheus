# NPE competing theories: mechanistic accounts of what the pair-tape world is doing

**Inference harvest, 2026-09-30 (Nestor).** The inputs are:
- the reader dossiers A–G;
- two independent adversaries, a deflationary one (ADV1) and an ontology one (ADV2), who were not shown any Nestor theory;
- the functional-core forensic (FOR);
- Nestor's own checks, recorded in NPE_UNMINED_EVIDENCE.md with codes U-xx.

Nestor's pre-adversary draft is frozen at `drafts/THEORIES_DRAFT_NESTOR.md`. Section 9 records how the adversaries changed it.

The seven theories below are **mutually distinguishable**: each has at least one prediction that another contradicts. Some
predict the same headline outcome; I keep them apart anyway, because they disagree about *mechanism*, and mechanism
decides what the next experiment should be.

Notation: **Φ** is the single-interaction pair map; **W** is the world's write-back rule (BASE or ATOMIC); a **family** is a
set of contents closed under Φ's images; **occupancy** is the share of sites held by a family.

---

## T1. Reachability: mutational supply × exposure (a search theory)

**Mechanism.** Every NPE transition is a first-passage event in genotype space. Its rate is the density of functional
genotypes within reach of the current population, times the number of trials: occupied sites × epochs × effective mutation
supply. Selection decides what persists. It does not decide what appears.

**Explains**
- **Acquisition**, as a base rate.
  - Random 64-byte genomes are competent on the dense VM at about 2e-4 (FOR Q3).
  - That rate predicts dense acquisition at the first checkpoint (about 7% vs 7/96 observed) and by the end of the run
    (about 64% vs about 55%) with no free parameters.
  - Planting the motif (32/96) and the SHAM null (0/96) are the same arithmetic.
- **Internalization rate.**
  - The hazard is about 1 per 140k lineage organism-epochs in ffa6 and about 1 per 1,150k in 7ae3, a ratio of about 8x.
  - The effective-mutation-supply ratio is about 7x. No fitting was needed (U-T5).
- **Timing and scale.**
  - State-freedom appears only after takeover (8/8), because takeover is what supplies the trials.
  - P(any state-free genome) rises with the number of competent genomes: 0.08, then 0.25, 0.71, 0.78 (U-C2).
- **Generic occurrence.** Any large, sustained competent population becomes state-free: 8/8 L-dominated and 17/21 non-L
  compartments (U-C2).
- **Drift.** Within runs, the state-free share drifts from 28% to 62% (16 runs up, 0 down; FOR Q5).

**Struggles with**
- **Distributed paths.** The 16000006 path needed coordinated multi-step change (single knock-ins 0/5, reverts 0/8, grafts
  0/12). T1 allows it as a sequential walk, but has no account of why the walk ended at `LD DE,3200`.
- **Non-appearance.** It does not explain why some large lineages never produce a state-free genome:
  - 7ae3 27000008 at depth 86 with 381k exposure;
  - ffa6 27000053, which took over but stayed at depth 11.
  T1 needs copy turnover, not presence, as the supply term.
- **Transience.** Half the events do not persist. T1 has no persistence account unless selection is added.

**Unique prediction.** The internalization hazard per unit of (occupied sites × copy events × effective mutation rate) is the
same across cells, worlds and payoff regimes. State-free genomes appear at that rate **even when state-freedom earns
nothing**, for example in an always-scaffolded ZERO world. Payoff affects only whether they sweep.

**Decisive falsifier.** Two results would kill T1:
- (a) State-free genomes appear at a much higher per-exposure rate under demand (CARRIED) than without it (ZERO), so their
  appearance is driven by demand.
- (b) Swapping the mutation operator between cells does not move the hazard ratio.

**Existing test.** Partial.
- U-T5 is consistent with T1.
- BEE's ZERO arm produced state-free genomes with no payoff (18/100, transient) [D:F 5.2]. That is a different engine, but
  it is what T1 predicts.

**Missing diagnostic data.**
- A ZERO-world arm in NPE, using C-A3's instrument.
- A mutation-operator swap.
- Copy-event counts per checkpoint. Current records hold depth, not copy events.

---

## T2. Scaffold tracking: the world defines reproduction (an ecological theory)

**Mechanism.** The world supplies most of what "reproduction" means:
- placement at offset 0;
- HL = 0 as the address;
- BC = 0 as a long periodic count;
- the 64/128 geometry;
- the pairing schedule;
- the write-back rule;
- and, decisively, **the newborn's registers, which are the victim body's leftovers** (`world.py:812/877`, U-W7).

Organisms are adapters to the world's schedule. A lineage takes over precisely those supplied functions that the world
supplies *unreliably*: the address becomes unreliable because newborns start from noise. It never takes over reliable ones:
placement is always supplied, so it is never internalized.

**Explains**
- **Zero-specialization.** It is the geometry of HL = 0 (C-ZERO-SPECIFIC 26/48 vs 2/48). It tracks the world supplied:
  X-A3-FAIR finds K_ONLY genomes in the 5A world and ZERO_LITERAL behaviour elsewhere.
- **What is and is not internalized.**
  - Self-location is never internalized: 280/280 SELF-free copiers are tape-anchored, and only 2 of 332 are locators.
  - Register addressing is internalized. Its source moves from entry registers to constants: 27% vs 56% world-dependence
    in state-free vs other genomes (FOR Q2).
- **Self-poisoning** is the copier's own pointer advance destroying the supplied address (D Q3). ADV2 D4 shows it can be
  pure phase arithmetic.
- **World rules that change outcomes.** Each of the following is a world rule that changes reproductive outcomes directly:
  - the energy "wall", which is an asymmetry between two birth paths (U-F4);
  - the splice (U-F3);
  - erosion versus ATOMIC.

**Struggles with**
- **Timing.** Why internalization waits for takeover (8/8), when the entry noise exists from epoch 0. T2 needs T1's supply
  term, or occupancy (T6), to explain the delay.
- **Transience.** Under steady demand, T2 predicts that state-freedom persists. Half the events lose it (U-C3).

**Unique prediction.** Internalization is ordered by how uninformative the newborn's entry state is: RANDOM ≥ VICTIM >
DONOR > ZERO. It appears for exactly the unreliable supplies and never for reliable ones. If placement is made unreliable,
by rotating the tape, then either locators internalize (if reachable) or reproduction collapses.

**Decisive falsifier.** State-freedom sweeps as often and as far in a world whose newborns inherit ZERO registers as in the
current VICTIM world. That would show the lineage is not tracking entry-state unreliability.

**Existing test.** Indirect only.
- In X-A3-WITHDRAW, CONTROL_ZERO keeps a standing 10-33% robust fraction that never sweeps, whereas ABRUPT sweeps to 0.96
  within 100 epochs (U-C5). This is consistent with T2.
- The newborn-register policy has never been varied.

**Missing diagnostic data.**
- A factorial of the newborn-register policy (VICTIM / DONOR / ZERO / RANDOM).
- A tape-rotation world (WP-7), with positive and negative controls.

---

## T3. Compact copy instruction: the representation does the work (a representation theory)

**Mechanism.** The instruction set supplies a half-duplicator. On a 128-byte wrapped tape, LDIR with DE − HL ≡ 64 and a long
count leaves a period-64 tape [ADV1 §1.1]. A competent genome is that instruction plus a short chain that computes its
operands modulo 128. Everything called organization is a handful of setter bytes:
- **Size of the core.** A median of 8 necessary bytes (IQR 6–10), about 5 beyond a minimal motif; the chain is mostly
  incidental moves (FOR Q1).
- **State-freedom.** It relocates the address source from entry registers to constants. It needs no extra bytes: the core
  is 8 bytes either way (FOR Q2).
- **The conserved core.** It is the copy op plus its register interface: SELF/LDIR, then 48 LD E,A, 42, 33 (C-CORE; U-L3).
- **Painters.** They are degenerate fixed points of the same semantics, `LD (HL),0x36` whose operand equals its opcode.
  None appears among 128 dense competent genomes (FOR Q4). All BYTEWISE P-11 survivors are painters (U-X5).
- **Informative heredity.** It exists only where the supplied block copy sits in a working register context: 57 P-11
  survivors reduce to 3 copiers.

**Explains**
- Copy_primitive has a 5x effect on P-11 (U-X5).
- Dense encoding (C-DENSE-COPY).
- The core composition (FOR).
- Function is conserved while bytes are regenerated (U-I5). Any chain that yields the right operands will do, and the copy
  direction is neutral.
- The absence of any genuinely larger organization in the sampled genomes: only 6 of 128 have no necessary bytes beyond the
  motif, and the median extra is 5.

**Struggles with**
- **The destination fix.** The 16000006 path needed distributed change, and single knock-ins did not confer robustness.
  T3 says robustness is a few constants. The adapted graft, DE = HL + 0x40, reached full robustness in only 1 of 12 genomes,
  so something in the background mattered.
- **Transmission.** Heritable variation is transmitted (CVT-R 83/100 and 8/8). T3 attributes this to the instruction.
- **Persistence.** It does not say why evolved genomes persist or fail. That needs T6/T7.

**Unique prediction.** Implant two genomes with the same computed conversion kernel κ and the same context set:
- a synthetic minimal copier (explicit pointer loads, random passengers);
- an evolved state-free genome.
They perform the same, in establishment, persistence, and head-to-head competition. Scrambling every non-necessary byte of
an evolved genome, replacing it with *random* bytes rather than NOPs, costs nothing.

**Decisive falsifier.** Either result would kill T3:
- evolved genomes beat κ-matched synthetic minimal copiers, or their own passenger-scrambled versions, by a frozen margin;
- the passengers carry function, for example robustness to erosion or to hijack.

**Existing test.** The static half is done: FOR's knockout maps support T3. The in-world half, competition and persistence,
has never been run.

**Missing diagnostic data.**
- A reconstitution test: evolved vs core-only (random passengers) vs synthetic.
- A register-free supplied-copy control (ADV1 K4).

---

## T4. Reproductive organization: a self-maintaining lineage process (the program's positive candidate)

**Mechanism.** The hereditary unit is a lineage process, not a byte string. Four properties would make it one:
1. It regenerates its own material. Founder bytes fall to 3–33%, and most bytes are computed or copy-made by the lineage
   (U-I1).
2. It keeps function while material turns over (U-I5).
3. It maintains a core by purifying selection.
4. When the scaffold becomes unreliable, it reorganizes its reproductive setup by distributed, multi-site change (16000006).

Establishment is a takeoff into a self-sustaining regime. "Endogenous" means the organization is carried and rebuilt by the
lineage's own activity, not supplied.

**Explains**
- The 16000006 walk: 49–54 bytes changed; single knock-ins gave 0/5 and grafts 0/12. It is the strongest single residue
  [ADV1 R2].
- Material turnover combined with function conservation.
- CVT-R transmission of organism-authored setup variation [ADV1 R1].
- The regeneration of the copy primitive in foreign cells (U-I5).

**Struggles with**, and this is now substantial:
- **No enrichment in the founder lineage.** State-freedom is not enriched in the founding lineage (ratio 1.009). The
  founding lineage also holds it *less* stably than replacement populations: 4/8 vs 16/18 at epoch 2000 (U-C3).
- **Generic, not lineage-special.** Any large competent population internalizes (U-C2).
- **No extra structure.** State-free genomes carry no extra organization: the core is 8 bytes either way (FOR Q2).
- **Establishment is predicted by Φ alone.** The Galton-Watson prediction 0.49–0.52 matches the observed 0.52 (U-S1). No
  lineage-level property is needed.
- **Bistability is not a takeoff.** It is explained as extinction versus saturation-plus-turnover (U-N4).
- **ATOMIC runs every post-09-25 result.** ATOMIC is the world's own fidelity-gated germline (U-X2). "The lineage maintains
  its heredity" is partly the world doing it.

**Unique prediction.** Evolved lineages show *lineage-level* reproductive properties that Φ computed on their genomes does not
predict:
- (a) evolved genomes outperform their own computed P_est in their home population but not in a naive one; kin-context
  benefit;
- (b) organization arises as a monophyletic sweep, heritable by CVT-R and the transmission Jacobian, not as recurrent de novo
  origins;
- (c) distributed epistasis: the reproductive function tolerates any single non-core knockout but collapses under
  combinations beyond the measured core.

**Decisive falsifier.** Three results would kill T4:
- (i) Φ-computed P_est and persistence predict the evolved genomes' outcomes as well as those of synthetic κ-matched
  genomes;
- (ii) state-free genomes within event runs arise recurrently and polyphyletically;
- (iii) passenger scrambling is free.

**Existing test.** Items (i) and (iii) are partly tested statically, and the results lean against T4:
- the 7ae3 GW prediction matched;
- the core is small.

Item (ii) has not been measured; the flicker in 27000020 (1 → 0 → 10 → 0 → 42 …) hints at recurrence.

**Missing diagnostic data.**
- A per-site content genealogy of state-free origins in C-A3 replays.
- A Φ-prediction test on evolved vs synthetic genomes.
- A multi-knockout (pairwise) map of evolved genomes.

**Current standing.** T4 is **no longer the default reading.** It survives only in the form: "a lineage's organism-authored
copy setup evolves under selection, sometimes by multi-step walks". That is weaker than "reproductive organization".

---

## T5. Public machinery: reproduction is executed by whoever reaches the code (a collective / field theory)

**Mechanism.** On the pair tape, code is data and data is code. A copy routine is **not owned**: it is executed by whichever
context's program counter reaches it. Measured case (U-W1, verified by Nestor):
- 7ae3 at side 0 is overwritten by the partner's content in 200/400 random pairings;
- the count is 0/400 when only its SELF+LDIR bytes are zeroed;
- the partner's context authored 12,485 changed bytes against 64 by 7ae3's own;
- the overwrite falls to 1/400 when the partner is confined to its own half.

A copier is therefore a public good. It copies itself at one side and copies its partner over itself at the other. The
record assigns birth, authorship and lineage label to the executing context.

**Explains**
- The victim-magnet effect: 100/240 founder overwrites, against 0/320 for a random implant (U-W1).
- Much of the founder loss at epoch 1 (28%).
- Single-sidedness (U-W2).
- Founder-less runaways (U-X6) and the spread of the founder label with 0 certified founder edges in 9cba (U-W6): candidates.
- AN8, where the victim ends up donor-like even when the donor's writes are blocked.
- Symmetric erosion.
- The Artemis side-1 hijack.
- It also predicts that "who reproduces" is a frequency-dependent field property. A copier benefits its partners in
  proportion to how often they reach its code.

**Struggles with**
- **Magnitude.** It predicts large frequency dependence. X-STALL-F0 shows no size dependence of erosion up to 15 members
  (U-W5), and X-DOSE-CURVE fits independent founders.
- **Internalization.** It has no account of internalization.

**Unique prediction.** Confining execution to the owner's half (pc may not cross into the partner half; writes still may)
would:
- abolish hijack births;
- raise founder survival at epoch 1;
- *change which genomes win.* Genomes whose success came partly from being executed by others should lose, and genomes
  that were being hijacked should gain.

On the existing record, a large share of certified and predecessor "births" will classify as EXEC ≠ owner.

**Decisive falsifier.** Either result would kill T5:
- execution containment changes establishment and persistence only by the amount a recomputed Φ predicts;
- an EXEC-motif audit finds hijack in under 5% of recorded births.

**Existing test.** The mechanism is shown in one genome (7ae3). The EXEC-motif prevalence across recorded births is unmeasured.

**Missing diagnostic data.**
- EXEC traces per recorded birth: the owner of executed code vs the executing context.
- An execution-containment world rule.

---

## T6. First principles: a stochastic rewrite field (deliberately avoiding program vocabulary)

**Mechanism.** The system is a fixed field of 256 **sites** [ADV2 §2]. Each holds a **content** (L bytes) and a **context**:
a register file that stays with the site, of which only the low 7 address bits matter on a 128-byte tape. Each epoch a
random matching applies the map Φ to site pairs. A world rule W (BASE or ATOMIC, plus noise and the splice) then decides
what is written back.

Nothing is born and nothing dies on the pair tape. "Birth" is a relabelling when a 0.9 threshold is crossed. "Organism",
"lineage" and "descent" fuse site, context and label, and every major correction in the record is those three coming apart.

Contents are operators. What spreads is:
- whatever converts other contents into itself, over a large enough share of partners and contexts (κ);
- whatever keeps its own site (ρ);
- whatever re-establishes its own working context (closure).

The observable dynamics are the attractors of this field: a soup state, and single-family occupancy states.

**Explains**, from Φ and W alone:
- **Establishment.** Φ-computed GW survival for 7ae3 under ATOMIC is 0.49–0.52, against 0.52 observed. BASE is subcritical
  (m 0.98), which explains cessation (U-S1).
- **Bistability.** No attractor sits between extinction and saturation (U-N4).
- **Segregation.** It follows from single-family occupancy (U-C4).
- **Label/content divergence.** It appears in a toy built from Φ alone (U-I6).
- **Self-poisoning.** It is phase advance Δ = count mod 128 (U-F2).
- **"Internalization".** It is growth of the closed context set, and it has traction only after takeover, because only then
  does the family set the contexts its own content meets.
- **Zero padding.** It inflates the rulers, as FOR Q3 also found.
- **cb7f.** "Takeover without depth" (U-N2).

**Struggles with**
- **Which family wins** when several coexist (k ≥ 2).
- **Frequency dependence.** Φ is computed against random partners, so the theory will fail where partners are relatives
  before takeover.
- **Adaptive walks.** It has no account of why an adaptive walk like 16000006 takes the path it does. It describes the
  landscape; it does not describe the walk.

**Unique prediction.** A *quantitative, label-free* one: establishment, persistence and poisoning are predictable from
single-interaction statistics computed genome by genome (κ over the full phase grid, ρ, the offspring law m and P_est, and
closure), with no lineage history. Changing the **slice budget** or the **tape length** moves poisoning and establishment in
a **non-monotone, modular-arithmetic** pattern: robust when the copy count ≡ 0 mod 128. No other theory predicts that
pattern.

**Decisive falsifier.** Either result would kill T6:
- Φ-computed P_est fails to predict per-donor establishment in the implanted panels, where donor identity dominates the
  outcome (D U4);
- a slice-budget dose shows a monotone effect, or no effect.

**Existing test.** 7ae3 GW (agrees). Phase arithmetic on synthetic donors (agrees). Real donors and the per-donor panel are
untested.

**Missing diagnostic data.**
- A map atlas of the 51k-genome corpus.
- `carried_states` phase orbits.
- A slice-budget or tape-length dose.
- One occupancy-logged replay of cb7f.

---

## T7. Demography: finite-population birth–death with a world-set offspring law (a deflationary quantitative theory)

**Mechanism.** Separate from T1, which concerns which genotypes are reachable. T7 claims that the quantitative regularities
are properties of a supercritical or subcritical branching process in a finite, well-mixed population of 256, read at a
fixed horizon. Those regularities are:
- the lottery;
- independent founders;
- bistable depth;
- transience;
- persistence differences;
- the horizon effect.

**Explains**
- X-DOSE-CURVE independence (LRT p = 0.42).
- The win-given-size figures (7/9 at ≥ 8 members; 5/5 at ≥ 16).
- The horizon effect (U-T6).
- The depth gap: extinction against saturation plus turnover.
- Transient events: a small selective advantage near drift balance.
- The splice as an offspring-mean reducer that cuts the tail only (U-F3).

**Struggles with**
- **The k = 4 excess.** Pooled depth ≥ 5: 98 observed vs 76 expected (p = 0.0013) [A 6.1].
- **Persistence ordering.** Why the founding lineage holds state-freedom *less* stably than replacements (U-C3). Plain
  demography gives no reason.

**Unique prediction.** It is distinguished from T6 by what it says about the world rule. The same demographic signatures
(independent tickets, a depth gap, splice tail suppression, BASE ≪ ATOMIC) reappear unchanged with a **register-free
supplied copy op** (ADV1 K4) that has no organization to evolve.

**Decisive falsifier.** With a register-free SELFCOPY op, the dose curve, the depth gap or the BASE/ATOMIC contrast changes
qualitatively, beyond what the op's own offspring law predicts.

**Existing test.** The dose curve and win-given-size figures are consistent with T7. The k = 4 excess is unexplained.

**Missing diagnostic data.** The SELFCOPY control world.

---

## 8. What the theories predict for the same observations (the collision table)

| observation | T1 reach | T2 scaffold | T3 instruction | T4 organization | T5 public | T6 field | T7 demography |
|---|---|---|---|---|---|---|---|
| dense acquisition ≈ 2e-4 base rate | **predicts** | neutral | predicts | neutral | neutral | predicts | neutral |
| state-freedom after takeover (8/8) | exposure | needs T1 | neutral | lineage process | neutral | context set becomes family-set | neutral |
| ffa6 ≫ 7ae3 (≈ 8x) | **operator ratio ≈ 7x** | cell ecology | neutral | neutral | neutral | neutral | neutral |
| no enrichment in L; replacements hold it better | predicts | predicts | predicts | **contradicts** | neutral | predicts | neutral |
| core ≈ 8 bytes; state-free needs no more | neutral | predicts | **predicts** | contradicts | neutral | predicts | neutral |
| 16000006 multi-step walk | allows | allows | strained | **predicts** | neutral | allows | neutral |
| GW P_est 0.52 = observed | neutral | neutral | neutral | contradicts (no lineage term) | neutral | **predicts** | predicts |
| victim magnet / 28% founder loss | neutral | neutral | neutral | neutral | **predicts** | predicts (Φ includes it) | absorbs |
| depth gap 22–161 | neutral | neutral | neutral | takeoff | neutral | saturation + turnover | **predicts** |
| transience (4/8) | selection-free appearance | contradicts | neutral | contradicts | neutral | weak closure advantage | drift balance |
| self-poisoning 12/12 vs 3/29 | neutral | supplied address destroyed | pointer advance | neutral | neutral | **phase arithmetic** | neutral |

---

## 9. How the adversaries changed Nestor's draft (collision resolution)

1. **T4 is demoted.** It is no longer the default reading. Four results did this:
   - The deflationary adversary's check: no enrichment in L, and replacements hold state-freedom more stably. Verified: the
     enrichment ratio is 1.009 (U-C1). Its power is low, but it points the wrong way for T4.
   - The functional-core forensic: state-freedom adds no bytes.
   - The ontology adversary's GW prediction from Φ.
   - The generic-internalization count (8/8 and 17/21).
   What survives of T4 is the adaptive walk of an organism-authored copy setup.
2. **T5 is new**, and it came from the ontology adversary's hijack probe, which Nestor verified with independent code. It
   was absent from the draft, except as a kin-pairing Allee idea. That idea is now secondary: U-W5 finds no erosion benefit
   up to 15 members.
3. **T6 was sharpened** from "rewrite-map fixed points" into ADV2's site/content/context ontology, together with its phase
   arithmetic. The draft had the map; it lacked the site/context separation and the 7-bit phase space.
4. **T7 was split off from T1.** The deflationary adversary showed that demography alone accounts for the lottery, the gap
   and independence. The draft had folded these into T1.
5. **T2 was strengthened** by a code fact the draft missed: newborns inherit the victim's registers (U-W7). That turns
   "scaffold tracking" from an analogy into a mechanism with a concrete manipulation, the newborn-register policy.
6. **T3 was strengthened quantitatively (FOR) and corrected in one place.** The NOP-padded `1E 40 E5` assay certifies
   zero-painting. The honest minimal real copier is `LD E/L,0x40|0xC0 ; E5/E7` with random padding: 6 exact 3-byte
   strings, prior 3.6e-7 at offset 0. Competent genomes arise about 500x more often through incidental longer chains
   (2e-4).
7. **Where I disagree with ADV1.** ADV1 reads the 1.009 enrichment ratio as positive evidence of label independence. With
   only 5 mixed checkpoints, it is uninformative. The informative deflationary facts are the persistence ordering and the
   generic 17/21.
8. **Where I disagree with ADV2.** ADV2 treats ATOMIC's individuality as "valid by construction". That is right for the
   *label*. Material turnover under ATOMIC (X-MAT) still shows a population that rebuilds its own bytes rather than
   importing them. The honest reading: ATOMIC makes individuals, and the population makes its material.
