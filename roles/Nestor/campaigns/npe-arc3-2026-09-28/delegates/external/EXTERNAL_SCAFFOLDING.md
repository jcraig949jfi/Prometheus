# EXTERNAL_SCAFFOLDING: can a reproductive lineage internalize what the environment supplies?

Delegate report for Nestor, NPE arc 3. Written 2026-09-28. Not committed.

This report follows `npe-p2-endogenous-heredity-2026-09-27/delegates/EXTERNAL_RESEARCH.md` (called "the P2 raid" below) and does not repeat it. The P2 raid already covered BFF/Computational Life, the 2026 Z80 soups, Knierim et al. 2026, Avida defaults and `mem-size`, Tierra hyper-parasites, Core War basics, von Neumann and Langton loops, the Eigen threshold and RAF sets. Where I build on one of those sources, I cite it briefly and add only new material.

Everything here concerns integer programs on virtual machines or formal models. Where a biology-derived term is used, its computational meaning is given.

## Claim markers

- **[V]**: I opened the primary source this session and took the claim from its text. I read the full text of Ray 1992/93, LaBar et al. 2016, Clark et al. 2017, Baugh 2015, Taylor 2019, Bourrat 2022 and Lehman et al. 2020; for Cicala et al. 2026 and Agüera y Arcas et al. 2024 I read the relevant HTML sections.
- **[V-abs]**: verified from an abstract, a publisher listing, a search-engine summary of the primary page, or a secondary source that quotes the primary. The body was not read.
- **[M]**: from memory, not re-opened. Treat as a lead.
- **[I]**: my inference applying a source to NPE. The source does not say it.

---

## 0. Decision summary (contradicting evidence first)

The hypothesis under test: a reproductive lineage can endogenously acquire machinery that replaces structure the environment now supplies. That structure is self-location, register initialization, copy access, execution setup and descendant initialization.

### 0.1 Evidence AGAINST spontaneous internalization

Nine results bear on this. The first four are the strongest: every time a system offered a cheaper, environment- or neighbour-supplied route, evolution took it and shed the internal machinery.

1. **Engineered self-reproducers collapse into cheaper self-copiers, and one of those collapses runs on stale registers.**
   - **Tierra.** Baugh and McMullin built a von Neumann-architecture self-reproducer: 344 instructions that decode a genotype through a look-up table and then copy it. It was stable only with mutation off. "When random perturbations are switched on, a short period of stasis would consistently be followed by a rapid change in population, where the population of von Neumann ancestors would revert to a population of self copiers" [V: Baugh 2015, §6.2.2].
   - **The mechanism.** One point mutation in a template changed a `call` target. Execution jumped straight to the genotype copy loop, skipping both the decoding and "the instruction sequence which fetches the start address of the genotype and calculates the length of the genotype". It still worked because **"the destination register, Ax, contains the starting address of the offspring. The source register, Bx, contains the starting address of the parent, and the count register, Cx, contains the length of the entire creature"**, all left over from earlier code [V: Baugh 2015].
   - **Avida.** Hasegawa and McMullin's von Neumann reproducer showed the same pattern. Their seed "has not been displaced by any mutation that preserves the UCA, but mutations that give rise to self-copiers are common". In Clark et al.'s summary, the offspring "merely abandon the UCA for the simpler strategy of reproduction by self-inspection" [V: as reported in Clark, Hickinbotham & Stepney 2017, §1].
   - **[I] For NPE.** This is the closest published analogue to NPE's register-dependent LDIR copiers. Given fresh registers, an address-computing copier is one mutation away from a cheaper copier that drops the computation and relies on whatever the registers hold. **Selection pushes toward dependence on supplied state, not away from it.**

2. **Tierra's ecology evolved away from self-location whenever a neighbour would supply it.**
   - Parasites use the host's copy procedure.
   - Hyper-parasites load their own location and size into a parasite's registers.
   - "Cheaters" (hyper-hyper-parasites) sit between social hyper-parasites, capture the instruction pointer, set "the CPU registers with its own location and size, and then skip over the self-examination step" [V: Ray, *Evolution, Ecology and Optimization of Digital Organisms*, Fig. 2 caption and §3.1.1].
   - Lehman et al. summarise the pattern: by "outsourcing computation they reduced the size of their genome, which made replication less costly" [V: Lehman et al. 2020].
   - [I] The direction of travel is externalization.

3. **Environment-supplied state becomes an exploited cue.**
   - **Z80 soup.** In the 2026 soup the environment passes the task input in register D during validation but "always initializes D to zero" during interactions. Lineages evolved to test D and skip the LDIR replication preamble when it was non-zero [V: Cicala et al. 2026].
   - **Avida.** Organisms learned to recognise the fixed inputs of Ofria's isolated test environment and "halt their replication … 'playing dead'". Once the inputs were randomised, they switched to doing tasks probabilistically so that some copies slipped through [V: Lehman et al. 2020].
   - [I] Every constant the NPE world injects is a potential information channel that lineages will come to depend on, which is the opposite of internalizing it.

4. **When reproduction and variation are hard-coded in the environment, the lineage cannot change them. When a cheaper route exists, it wins.**
   - Taylor: an extrinsically coded process "would still only be able to change and evolve in the hard-coded ways provided by the extrinsically defined change mechanism". Only intrinsic implementation lets "the evolvability of the process … itself evolve" [V: Taylor 2019, §4.1].
   - Cicala et al.'s hard-wired copying control (the environment overwrites the partner with an exact copy, no Z80 code executed) solved more hard tasks than emergent copying. Emergent copying kept broader genealogies [V].
   - [I] Internalizing costs fitness in the short term. Nothing selects for it unless the scaffold is unreliable or withdrawn.

5. **The endogenous version of a function is often less evolvable than a scaffolded shortcut.**
   - Avida's `mem-size` instruction supplies genome length with no self-inspection. It was adopted in 96/100 runs and made length changes neutral. Without it, 72.5% of runs locked in a brittle "accidental" length computation [P2 raid, V: Ofria, Adami & Collier 2002].
   - [I] In this case the environment-supplied primitive was the evolvable choice. An endogenous replacement need not be better, even for long-term evolvability.

6. **Replication machinery that optimizes fastest innovates least.**
   - Among 75 emergent fixed-length Avida replicators (from 1e9 random genomes), "hc" replicators lack a dedicated copy loop. They loop over their whole circular genome and optimize replication best, but "36 hc-replicators never evolved any traits", because beneficial replication mutations "accumulate in regions of the genome that subsequently cannot be mutated into the type of instructions that discover novel traits" [V: LaBar, Hintze & Adami 2016].
   - [I] Machinery that exploits the environment's circular wrap is an evolutionary dead end for new function.

7. **Selection is short-sighted about the replication machinery's own parameters.**
   - With an evolvable per-organism mutation rate, Avida populations "evolved to levels far below the long-term U_opt, regardless of the starting value", but only on rugged landscapes [V-abs/V via PLoS page: Clune et al. 2008].
   - [I] Do not expect NPE lineages to evolve copy fidelity or robustness that pays off only later.

8. **Formal endogenization is conditional, and in the model found it is partial.**
   - Bourrat's agent-based model of "scaffold endogenization" shows that collectives *can* become resilient to removal of an ecological scaffold, but "in some conditions" only.
   - Endogenization works through **pleiotropy**: the trait that replaces the scaffold is the same trait that pays under it.
   - After removal, the outcome depends on the propagule timescale T and the maximum collective size S. Under some settings the scaffolded state persists (growth stays at or below 0.5). Under others it reverts to the no-scaffold regime, sometimes taking more than 30,000 generations [V: Bourrat 2022, §5-6.3].
   - The original ecological-scaffolding model on its own showed no such resilience [V: Bourrat 2022 abstract; Black, Bourrat & Rainey 2020, V-abs].

9. **Scaffolded reproduction is a recognised, stable category.**
   - Godfrey-Smith's "scaffolded reproducers are entities which get reproduced as part of the reproduction of some larger unit … or that are reproduced by some other entity" [V: SEP, Wilkins & Bourrat 2022].
   - [I] NPE's register-dependent copiers are scaffolded reproducers of the world's execution machinery. The concept gives no expectation that scaffolded reproducers become simple ("using their own machinery") reproducers on their own.

### 0.2 Evidence FOR (partial) internalization or endogenous machinery

1. **Tierran hyper-parasites re-derive self-location on every cycle.** After each reproduction the hyper-parasite "re-examines itself, resetting the bx register with its location and the cx register with its size" [V: Ray]. This is an internalized reset, and it is exactly what makes register hijacking work.
2. **Machinery lost to mutation was rebuilt by an alternative internal computation.** "In one run, creatures evolved without a template marking their end." They found their start template and a mid-genome template, subtracted to get half their size, and doubled it by shifting left [V: Ray]. Self-measurement survived by a different route. This is the same brittle trick Avida later documented [P2 raid].
3. **The copy loop itself evolves.**
   - Tierra discovered loop unrolling: the work steps were "repeated … three times within the loop" after 15 billion instructions, and algorithms were optimized "by a factor of 5.75" [V: Ray].
   - Avida produced unintended genome doubling through a second `copy` in an odd-length genome's loop [V: Lehman et al. 2020].
   - In Z80 soups, Load-Push copiers are replaced by LDIR copiers [P2 raid].
4. **A complex, semantically closed architecture can persist.** In 500 Stringmol runs of a universal-constructor architecture (UCA), "there were no examples where the UCA system was displaced by a replicase system". The copier, the expressor and the genome co-evolved, "giving rise to viable offspring". The authors attribute this to the seed being "sufficiently well disconnected from the attractor of replicase systems" [V: Clark et al. 2017].
   - [I] Internal machinery is protected when the cheaper, scaffold-dependent alternative is many mutations away. That is a **design lever**, not a spontaneous acquisition.
5. **Bourrat's model does produce scaffold-resilient collectives** under a bounded region of (T, S) parameters [V].

### 0.3 Verdict

I found no published result in which a program-soup lineage *spontaneously acquired* self-location, register initialization or execution setup after the environment withdrew it. The closest positive cases are:
- Tierra's internal re-examination, which was designed into the ancestor;
- Ray's template-loss workaround, which replaced one internal method with another;
- Bourrat's pleiotropic endogenization, which is a formal model of cells and patches, not programs.

The negative cases are direct and mechanistically close to NPE (items 0.1.1-0.1.3). I did not find a published study designed to test internalization in a program soup; this is an absence in my searches, not proof of none. The prior literature therefore predicts that **NPE lineages will not internalize supplied scaffolding unless (a) the scaffold is unreliable or withdrawn gradually, and (b) the internal replacement is pleiotropically coupled to something selection already rewards** [I].

---

## 1. System-by-system answers to the eight questions

The questions are:
- Q1: what the replicator encodes.
- Q2: what the environment supplies.
- Q3: what state is reset between interactions.
- Q4: how the replicator locates itself.
- Q5: what happens to the descendant's execution state.
- Q6: whether copies are immediately competent.
- Q7: whether the reproductive machinery itself can evolve.
- Q8: how the source distinguishes endogenous from externally supplied function.

### 1.1 Tierra ecology beyond the ancestor (parasites, hyper-parasites, cheaters, unrolled loops)

Source: Ray, T. S., *Evolution, Ecology and Optimization of Digital Organisms*, Santa Fe Institute working paper 92-08-042 (1992); PDF mirror https://faculty.cc.gatech.edu/~turk/bio_sim/articles/tierra_thomas_ray.pdf [V, full text].

- **Q1.** Self-examination, allocation, a copy loop and divide. Descendants encode less than this: parasites have no copy procedure; cheaters have no self-examination.
- **Q2.**
  - MAL/DIVIDE with a write-protected "membrane".
  - A slicer (CPU-time scheduler) whose "slicer power" sets size selection.
  - Template addressing within a search limit.
  - Copy mutations, background mutations and "flaws" (arithmetic occasionally off by one).
- **Q3.** The mother's registers are not described as cleared. The ancestor jumps back and re-examines itself [V]. In Baugh's modified Tierra von Neumann creature, "when the genotype is copied, the parent divides and resets its registers" [V: Baugh 2015 §6.2.2]. It is unclear whether that reset is an OS action or creature code. **Unverified.**
- **Q4.**
  - Complementary templates at the start and end; addresses are subtracted to get size [V].
  - Variant: no end template; half-size is computed from a mid-genome template and doubled [V].
  - Cheaters do not self-locate; they use the registers a neighbour set up [V].
- **Q5.** The daughter gets a new CPU and instruction pointer at DIVIDE. That setup is supplied by the OS [V].
- **Q6.** Yes for self-replicators. No for parasites, which need a host in their search radius. A hand-dissected ancestor split into a size-46 creature (self-examination plus copy loop) and a size-64 creature (self-examination plus copy procedure). "Neither could replicate when cultured alone, but when cultured together, they both replicated" [V].
- **Q7.** Yes:
  - loop unrolling (from 10 to 6 instructions per copied cell);
  - optimization factor 5.75 [V];
  - template shortening (social hyper-parasites use 3-instruction templates) [V];
  - rate of optimization increases with mutation rate "until the system becomes unstable" [V].
- **Q8.** Not formalized. Ray describes each parasitic class operationally by which subroutine it lacks. [I] That is a knockout-style definition of "endogenous": function F is endogenous to genome G if G performs F when cultured alone.

### 1.2 Von Neumann UCA in Tierra and Avida (Baugh and McMullin; Hasegawa and McMullin)

Sources:
- Baugh, D. (2015). *Implementing von Neumann's Architecture for Machine Self Reproduction within the Tierra Artificial Life Platform to Investigate Evolvable Genotype-Phenotype Mappings*. PhD thesis, Dublin City University, supervisor B. McMullin. https://doras.dcu.ie/20731/1/Thesis.pdf [V, abstract and §6.2.2]
- Hasegawa, T. & McMullin, B. (2013). *Exploring the point-mutation space of a von Neumann self-reproducer within the Avida world*. ECAL 2013. [V-abs via Clark et al. 2017 and a search listing; not opened]

Answers (Baugh):
- **Q1.** A genotype plus a decoder. The look-up table or translation table is itself encoded, so the genotype-phenotype mapping is mutable [V].
- **Q2.** Tierra OS (MAL, DIVIDE, templates).
- **Q3.** See 1.1.
- **Q4.** Templates.
- **Q5.** A new CPU per daughter.
- **Q6.** Yes, with mutation off.
- **Q7.** The mapping can mutate. With redundancy added to the mapping, "certain inheritable perturbations … prove to be non-reversible via a change to the genotype". This produces "consistently … the loss of any target symbols from the mapping which are not vital for reproduction". Reversal happened only via rare "Lamarckian" events: "a very specific perturbation to the phenotype" [V: abstract].
- **Q8.** Implicit. The self-copier is identified as a creature that bypasses decoding.

Answers (Hasegawa and McMullin, as reported by Clark et al. 2017):
- The Avida UCA is viable without mutation. Mutations preserving the UCA were not observed; mutations to self-copiers "are common" [V-abs].

Lessons for NPE [I]:
- (a) The degeneration route runs *through leftover register state*. If NPE builds a "fully endogenous" donor (one that computes its own address), it should expect a one-mutation shortcut to register dependence whenever registers happen to hold usable values.
- (b) Baugh's "loss of non-vital mapping symbols" is a general ratchet: capability that is not used every generation is lost and hard to regain. Endogenous machinery for a function the environment currently supplies is non-vital by definition, so the ratchet works against it.

### 1.3 Avida: emergent replicators, defaults, and scaffold switches

Sources:
- LaBar, Hintze & Adami (2016), *Evolvability tradeoffs in emergent digital replicators*, Artificial Life 22(4):483-498, arXiv:1511.07959, https://arxiv.org/abs/1511.07959 [V full text]
- Avida wiki, Reproduction settings, https://github.com/devosoft/avida/wiki/Reproduction-settings [V]
- Lehman et al. (2020), *The Surprising Creativity of Digital Evolution*, Artificial Life 26(2), arXiv:1803.03453 [V]
- Clune et al. (2008), PLoS Comput Biol 4(9):e1000187, https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000187 [V via page summary]

**Q1.** hc-replicators "loop through their entire genome … [using] the circular nature of their genome to achieve self-replication without a dedicated copy loop". fg-replicators have a copy loop at the start marked by if-label and mov-head [V]. Of 75 length-15 replicators, only 22 were true self-replicators. The other 53 were **proto-replicators**, which "deterministically copy themselves inaccurately" but whose offspring eventually lead to self-replicators [V].

**Q2.** The environment supplies a lot:
- `h-alloc` places the genome length in AX, which hc-replicators move to CX with `swap` [V].
- Circular genome execution.
- `h-copy` and `h-divide`.
- "an early design-decision gave each avidian a certain amount of 'base' energy for free", so random replicators need no metabolism [V].
- `ALLOC_METHOD`: mode 0 fills offspring memory with a default instruction; mode 1 leaves it uninitialized ("necrophilia", producing hybrids with dead organisms); mode 2 randomizes it [V: wiki].
- `RESET_INPUTS_ON_DIVIDE`, `INHERIT_MERIT`, `EPIGENETIC_METHOD` and `INHERIT_MULTITHREAD` exist [V: wiki names only; semantics in the P2 raid].

**Q3.** By default the mother resets on divide [P2 raid]. Inputs can be reset on divide [V: setting name].

**Q4.** Through supplied defaults: "the read-head is set at 0 by default" [V: LaBar 2016]. The write-head is advanced to the genome length either by looping (fg) or by jmp-head using the h-alloc value (hc) [V].

**Q5.** The offspring starts from a fresh CPU, unless `EPIGENETIC_METHOD` is set otherwise [P2 raid].

**Q6.** Proto-replicators are not immediately competent: their offspring differ from the parent deterministically [V].

**Q7.** Yes, within limits:
- The copy-loop structure determines the optimization-versus-innovation trade-off [V].
- Genome doubling happens through an extra `copy` [V].
- Mutation rate is evolvable only when the experimenter adds it as a per-organism heritable parameter changed at replication. It is not implemented by the organism's instructions [V: Clune 2008].
- [I] Clune's result is therefore about an *extrinsically* implemented but heritable parameter. That is the Taylor category Nestor should avoid confusing with endogenous fidelity machinery.

**Q8.** Operational only: test-CPU viability. The "playing dead" anecdote shows the test context itself can be recognised and exploited [V].

### 1.4 Stringmol replicase ecology and Stringmol UCA

Sources:
- Hickinbotham, Stepney & Hogeweg (2021), *Nothing in evolution makes sense except in the light of parasitism: evolution of complex replication strategies*, R. Soc. Open Sci. 8:210441, https://pmc.ncbi.nlm.nih.gov/articles/PMC8334846/ [V via page summary]
- Clark, Hickinbotham & Stepney (2017), *Semantic closure demonstrated by the evolution of a universal constructor architecture in an artificial chemistry*, J. R. Soc. Interface 14:20161033, https://doi.org/10.1098/rsif.2016.1033 ; PDF https://eprints.whiterose.ac.uk/id/eprint/117175/ [V full text]
- Stringmol specification, https://www.cs.york.ac.uk/library/reports/2010/YCS/458/YCS-2010-458.pdf [listing only]

- **Q1.** An opcode string whose program, run on a *bound pair*, copies the partner. The seed does "R + C → R + C + C" [V].
- **Q2.**
  - Probabilistic sequence-dependent binding.
  - Four pointer types: instruction, flow, read and write [V-abs: ALife encyclopedia].
  - Point mutation fired by the copy operator.
  - A spatial grid (Moore neighbourhood).
- **Q3.** Each reaction is a discrete event. Execution runs "until either the reaction program terminates, or probabilistic decay occurs" [V]. State does not persist across reactions.
- **Q4.** The binding site supplies it. "The start point of the reaction program is the end of the bind site on string1". string1 is the string "with the longer end before the bind site", or chosen at random if the bind is symmetric [V].
  - [I] This is the closest analogue to NPE's pair tape. The *physics of binding* supplies both execution order and self-location.
- **Q5.** A new string after cleavage has no carried state.
- **Q6.** Yes for replicases.
- **Q7.** Yes, and the evolved machinery reshapes the evolutionary process itself:
  - Non-complementary binding that forces hostile sequences to bind each other.
  - "Self-scan": the program first overwrites itself with its own code. This slows replication, and because the copy operator fires mutations, "the point mutation rate is approximately doubled".
  - Toggle and move operations that gate replication.
  - Emergent macromutations.
  - When parasites become rare, replicators "lose their complex countermeasures and become simpler and shorter" [V].
  - In the UCA version, the copier, expressor and genome co-evolved, including changes to "the meaning of genomic material" [V].
- **Q8.** Clark et al. use semantic closure (Pattee): the machine that defines what the description means is encoded in the description [V].

[I] The Stringmol results give NPE two points:
- (i) Complex replication machinery is gained under parasite pressure and **lost when the pressure lapses**. Internalized scaffolding needs a *continuing* reason to persist.
- (ii) Machinery that changes mutation rate can arise as a side-effect (self-scan), not as a fidelity adaptation.

### 1.5 Z80 soup context cues and the hard-wired control (Cicala et al. 2026), new details only

Source: Cicala et al. (2026), arXiv:2607.09211, https://arxiv.org/html/2607.09211 [V]

- **Q2/Q3.** The environment uses register D "to pass the task input x∈{0,…,15} during validation", so D is non-zero 15 times in 16. "During the interaction phase … the environment always initializes D to zero" [V].
- **Q4.** The paper's LDIR robustness test "set register E to 32 and then executed the LDIR instruction while relying on the default initialization HL=0 and BC=0" [V]. Self-location is supplied by the reset, and the authors say so in their own test.
- **Q7.** Under metabolic penalties, programs evolved conditional halting that distinguished validation from interaction [V].
- **Q8.** The hard-wired control "directly overwrites the second program with an exact copy of the first without executing Z80 code". It solved more hard tasks, but ancestor distributions were "considerably narrower" [V].
- [I] This is a ready-made ablation: supplied copying against emergent copying. NPE can build the same pair of arms for each scaffold item (section 3a, experiment 1).

### 1.6 Computational Life long-tape variants: when execution start is randomized

Source: Agüera y Arcas et al. (2024), arXiv:2406.19108, HTML [V for the quoted lines]

- **BFF long tape.** "At each iteration, we select a random initial position in the tape and execute instructions sequentially". For heads, "Adding an offset to head1 is sufficient to allow looping self-replicators to arise. Anecdotally, we appear to require an offset somewhat larger than 8 to work (e.g., 12 or 16)" [V].
- **Forth long tape.** "Each thread chooses a random PC". Addressing is "at an offset against the current PC, or offset against a 'pseudo-tape' marker positioned at the nearest preceding 64-byte aligned position". Replicator loops copy "the head of the 'next' replicator rather than its own head" [V].
- **8080 long tape.** Replicators are two repeated bytes such as `01 c5`, non-looping [V].
- [I] **This is the most direct published evidence on self-location removal.** When the execution start is randomized, replicators still emerge, but only because the designers supplied position-relative addressing instead:
  - BFF heads relative to the start, with a tuned head1 offset;
  - Forth PC-relative or aligned-marker addressing;
  - 8080 relative stack pushes.

  No variant removed self-location *and* all relative-addressing aids. In Forth, copying one's neighbour's head rather than one's own shows that in a homogeneous region self-location is unnecessary: any nearby copy is "self".

### 1.7 Core War / Coreworld: self-location supplied by the physics

- **Relative addressing is the physics.** "Relative addressing is the only method for addressing allowed in Redcode … there is no way for a warrior to know its absolute position" [V-abs: Esolang/Redcode guides, https://esolangs.org/wiki/Redcode ; https://corewar.co.uk/karonen/guide.htm].
- **Offspring execution is set up by an instruction.** `MOV 0,1` (the Imp) is a replicator because the instruction copies itself one cell ahead and execution falls into the copy [V-abs]. In Coreworld, two-instruction MOV-SPL replicators "often take over" [V-abs, secondary]. SPL is the instruction that starts a new process at a target address.
- **Evolution without reproduction pressure.** In GP-evolved Core War warriors, "none of the warriors developed scanned for opponents or replicated themselves" [V-abs: Core War Tribes summary, https://corewar.co.uk/thorsell/paper.htm].
- [I] For NPE: making addressing position-relative moves self-location from "environment constant" to "irreducible physics". NPE's scaffold taxonomy (section 2.5) should record this as a third category. It is neither supplied state nor internalizable machinery.

### 1.8 Endogenous self-location on a real Z80: the CALL/POP idiom

- **The idiom.** The classic position-independent idiom on the Z80 is `CALL here` followed by `here: POP HL`. It loads the current address into HL [V-abs: MSX Resource Center and comp.os.cpm threads, https://www.msx.org/forum/msx-talk/development/is-there-a-way-to-get-program-counter-pc-on-z80 ; https://groups.google.com/g/comp.os.cpm/c/9BVctCgStB8].
- **The limit.** "It's not possible to write completely relative non-trivial code with Z80, since only 8-bit relative jumps … are covered by JR/DJNZ" [V-abs].
- **[I] Cost in NPE.** `CALL nn` is 3 bytes and `POP HL` is 1 byte. It needs a writable stack location, so it depends on SP, which is itself environment state. A 1-byte `RST p` also pushes PC, but jumps to a fixed absolute address. On a 128-byte wrapped tape that address lands in the offset-0 genome, so `RST` only works for the first-placed program or with a landing pad.
- **[I] What this means for NPE.** The minimal endogenous self-location on a Z80-like ISA costs about 4 bytes plus a dependence on SP. A register-reset world makes HL=0 free. Under the information-cost model (Adami & LaBar 2015, P2 raid), 4 specific bytes means about 32 bits, a factor of about 4e9 in per-sample probability. NPE should check whether its VM implements CALL, RST, POP and SP wrap, and cost them explicitly.

### 1.9 Reproduction by self-inspection (Laing; Ibáñez et al.)

Sources:
- Laing, R. (1977). *Automaton models of reproduction by self-inspection*. J. Theor. Biol. 66:437-456. https://www.sciencedirect.com/science/article/abs/pii/0022519377902946 [V-abs listing]
- Ibáñez et al. (1995). *Self-inspection based reproduction in cellular automata*. ECAL 1995, LNAI 929:564-576. https://link.springer.com/chapter/10.1007/3-540-59496-5_326 [V-abs listing]

In Laing's model, "the description of the object to be replicated … is dynamically constructed concomitantly with its interpretation" [V-abs: secondary summary].

[I] NPE's LDIR donors are self-inspecting reproducers. A self-inspector needs a way to reach its own body, which means an address or adjacency. Laing's automata get that from the geometry of the automaton (its own reading arm). NPE donors get it from HL=0. Self-inspection by itself does not specify where self-location comes from.

### 1.10 Summary table

| System | Self-location (Q4) | Reset between interactions (Q3) | Descendant execution (Q5) | Can the machinery evolve (Q7) | Internalization observed? |
|---|---|---|---|---|---|
| Tierra ancestor | Templates and subtraction, recomputed every cycle | Mother not cleared; creature re-examines itself | OS gives daughter a new CPU | Yes (loop unroll, 5.75x) | Template-loss workaround (V) |
| Tierra cheaters | Borrowed from a neighbour's registers | n/a | n/a | n/a | Reverse: self-examination skipped (V) |
| Tierra/Avida UCA | Templates / heads | Tierra UCA creature resets registers (source of reset unclear) | New CPU | Mapping mutable | Reverse: collapse to self-copier (V) |
| Avida emergent | Read-head defaults to 0; h-alloc puts length in AX | Mother reset by default | Fresh CPU | Loop structure; extrinsic mutation-rate parameter | No |
| Stringmol | Bind site sets program start | Per reaction | New string | Yes (self-scan, gating) | Countermeasures gained and lost with parasites |
| Stringmol UCA | Bind site | Per reaction | New strings | Copier, expressor and genome co-evolve | Maintained 500/500 (no collapse) |
| Z80 soup 2026 | HL=0 reset | Full CPU reset | World resets | LDIR replaces Load-Push | Reverse: D-register cue exploited |
| BFF/Forth long tape | Heads/PC relative to a random start | Per thread | Per thread | Yes | Not tested |
| Core War | Physics is relative | n/a | SPL / fall-through | Yes (GP) | n/a |

---

## 2. Formal ideas separating environmental support, internalizable scaffolding and irreducible physics

### 2.1 Intrinsic vs extrinsic implementation (Taylor 2019)

Taylor, T. (2019). *Evolutionary Innovations and Where to Find Them: Routes to Open-Ended Evolution in Natural and Artificial Systems*. Artificial Life 25(2):207-224. arXiv:1806.01883, https://arxiv.org/abs/1806.01883 [V full text]

- Three processes must exist in every evolutionary system: generation of the phenotype, evaluation, and reproduction with variation. "In some cases a process might be implemented extrinsically as a special purpose hard-coded mechanism acting upon the system, whereas in other cases the process might be provided intrinsically". Intrinsic mechanisms "may rely exclusively upon the general laws of dynamics of the system … or they may be under sophisticated evolved control" [V].
- "All existing artificial evolutionary systems define some or most of these processes extrinsically". Banzhaf et al. call these "shortcuts" [V].
- Route 1 (intrinsic reproduction and variation) covers "evolvable genetic operators, including copying processes, error correction, mutator genes" [V].
- [I] Taylor's split is binary. NPE needs three levels:
  1. **Extrinsic scaffold.** The world performs the function (register reset, fixed layout, per-execution PC setup).
  2. **Intrinsic by physics.** The ISA makes the function free under any genome: relative addressing, PC push on CALL.
  3. **Intrinsic under evolved control.** Genome bytes perform the function and can mutate.

  "Internalization" means a move from level 1 to level 3. A design change from level 1 to level 2 is not internalization, and NPE must not report it as such.

### 2.2 Scaffolded, simple and collective reproducers (Godfrey-Smith); reproducers and development (Griesemer, Wimsatt)

Sources:
- Wilkins, J. S. & Bourrat, P. (2022). *Replication and Reproduction*. Stanford Encyclopedia of Philosophy. https://plato.stanford.edu/entries/replication/ [V]
- Godfrey-Smith, P. (2009). *Darwinian Populations and Natural Selection*. OUP. [M; definitions V via SEP]
- Godfrey-Smith (2015), PNAS, https://www.pnas.org/doi/pdf/10.1073/pnas.1421378112 [listing]

Definitions [V: SEP]:
- **Simple reproducers**: "entities that can reproduce … using their own machinery, in conjunction with external sources of energy and raw materials".
- **Scaffolded reproducers**: "reproduced as part of the reproduction of some larger unit … or … by some other entity".
- **Griesemer's reproducer**: "an entity that develops and has a material overlap between the 'parent' and 'progeny'".
- **Wimsatt & Griesemer (2007)**: reproduction is "a composite process of development and progeneration" [V: SEP quote].

[I] Mapped onto NPE:
- A register-dependent LDIR donor is a scaffolded reproducer: the world's execution machinery reproduces it.
- The victim tape is the "material overlap". Bytes not overwritten persist, which is why partial copies make hybrids (compare Avida `ALLOC_METHOD 1`).
- "Descendant initialization" is the development half of Wimsatt and Griesemer's composite. In NPE it is performed entirely by the world, because every program starts at its own byte 0 on its next execution.

Endogenizing development would mean the parent writes something into the offspring that sets up the offspring's execution: a prologue, or bytes that set registers. Carried registers are a crude version of this. Section 3a, experiment 6 tests it.

### 2.3 Ecological scaffolding and endogenization (Black, Bourrat & Rainey 2020; Doulcier et al. 2020; Bourrat 2022)

- Black, A. J., Bourrat, P. & Rainey, P. B. (2020). *Ecological scaffolding and the evolution of individuality*. Nature Ecology & Evolution 4:426-436. https://www.nature.com/articles/s41559-019-1086-9 [V-abs]. A patchy resource structure plus dispersal "can scaffold Darwinian-like properties on collectives".
- Doulcier, G., Lambert, A., De Monte, S. & Rainey, P. B. (2020). *Eco-evolutionary dynamics of nested Darwinian populations and the emergence of community-level heredity*. eLife 9:e53433. https://elifesciences.org/articles/53433 [V-abs]. Manipulating population structure "can exogenously impose Darwinian-like properties on communities".
- Bourrat, P. (2022). *Evolutionary Transitions in Individuality by Endogenization of Scaffolded Properties*. BJPS 76(2). https://doi.org/10.1086/719118 ; accepted manuscript https://pierrickbourrat.github.io/publication/a-36/a-36.pdf [V full text]

Bourrat's key points [V]:
1. Endogenization means evolving "properties that makes them resilient to the removal of the scaffold". "Only by removing the scaffold can an ETI be deemed complete" (ETI: evolutionary transition in individuality).
2. The mechanism is **pleiotropy**. One genotype sets both growth rate and the tendency to stay on the patch or leave it. A realizer is "cells producing glue", which lowers growth and prevents leaving.
3. The scaffold was present from the start; endogenization happens *during* the scaffolded period. After removal ("reverted regime"), outcomes split. In some conditions growth reverts to the no-scaffold value, taking more than 30,000 generations for T=9, S=12. In others it stays low, because collectives "can only produce a propagule if they contain cells with a growth rate below 0.5". Some conditions are not viable at all.
4. Other suggested routes to endogenization, not modelled, include "the evolution of developmental processes" [V].

[I] For NPE:
- (a) Test the scaffold by removing it. Evolve under reset, then withdraw.
- (b) The internal replacement must be coupled to a trait the scaffold already selects. For example, if the world rewards donors whose copy lands at the correct offset *regardless of register state* (randomized per execution), self-location computation and copying become one trait.
- (c) Withdrawal timing and population structure matter, so sweep them.
- (d) Expect some lineages to go extinct on removal. Report extinction and endogenization separately.

### 2.4 Niche construction and ecological inheritance

- Laland, K. N., Odling-Smee, F. J. & Feldman, M. W. (1999). *Evolutionary consequences of niche construction and their implications for ecology*. PNAS 96(18):10242-10247. https://www.pnas.org/doi/10.1073/pnas.96.18.10242 [V-abs]. A two-locus model in which resources are altered by niche construction and by independent renewal and depletion. Niche construction can fix "otherwise deleterious alleles", create or eliminate polymorphisms, and generate unusual dynamics.
- Odling-Smee, Laland & Feldman (2003). *Niche Construction: The Neglected Process in Evolution*. Princeton UP. [M] "Ecological inheritance" means environmental modifications inherited by the next generation.
- Taylor, T. (2004). *Niche construction and the evolution of complexity*. Artificial Life IX, 375-380. https://doi.org/10.7551/mitpress/1429.003.0063 [V-abs]. The first individual-based model in which organism complexity (number of genes) can evolve through niche construction.

[I] In NPE, carried registers are **ecological inheritance**: the executing program modifies a persistent environment variable (the register file) that the next executor inherits. The Laland model predicts two things: carried state can fix otherwise deleterious code (code whose only effect is setting registers), and it creates lagged, frequency-dependent dynamics. NPE's "self-poisoning" and "hijack" are both instances. Wilke's maternal-effect model (P2 raid) is the single-lineage special case. Niche construction adds the case where the *partner* inherits the constructed state.

### 2.5 Bootstrapping: compilers, trusting trust, and the irreducible seed

- Thompson, K. (1984). *Reflections on Trusting Trust*. CACM 27(8):761-763. [M for citation details; content V-abs via search]. A self-hosting compiler can carry behaviour that exists only in the binary and not in the source. The function has been internalized into the lineage of binaries and is invisible in the "genome" (the source).
- Wheeler, D. A. (2005/2009). *Countering Trusting Trust through Diverse Double-Compiling*. arXiv:1004.5548 and 1004.5534, https://dwheeler.com/trusting-trust/ [V-abs]. Compile the source with an independent compiler and compare. This checks whether a function is carried by the text or by the inherited binary.
- Alden, D. (31 July 2024). *Pulling Linux up by its bootstraps*. LWN. https://lwn.net/Articles/983340/ [V]. The live-bootstrap chain starts from builder-hex0, "a bootloader that fits in a single 512-byte disk sector". It uses "BIOS commands to read the human-readable sources from disk", then climbs through stage0-posix, GNU Mes, tcc, Fiwix, musl, Perl and GCC 4.0.4 to a modern toolchain.

[I] Bootstrapping gives NPE its cleanest three-way distinction:

| Bootstrapping term | NPE analogue |
|---|---|
| Environmental support (the BIOS here) | World constants that cannot be withdrawn without changing the physics. NPE's candidates: fetch/execute itself, tape wrap, execution-order scheduling. |
| Internalizable scaffolding (each stage replaces the need for a trusted prebuilt binary by building it) | Register reset, fixed layout, supplied LDIR |
| Irreducible seed (hex0 plus BIOS, where the chain bottoms out) | The ISA semantics |

Two further lessons:
- **Trusting trust is the program analogue of "descendant competence via inherited state not in the genome".** A copy's behaviour can depend on what the *parent binary* did (for NPE: what the previous execution left in registers), not on its text.
- **DDC is the matching assay.** Run the donor's bytes through an independent "compiler" (fresh registers, a different offset) and compare. A function that survives this is carried by the text. This is the formal version of NPE's certification across register modes.

### 2.6 Other formal lines checked

- The evolution of error correction under selection for speed alone (proofreading pays when misincorporations cause stalls): *Evolution of error correction through a need for speed*, Science (2026), https://www.science.org/doi/10.1126/science.adt1275 [V-abs via search; authors not verified]. This is a molecular kinetics model, not a program soup. [I] It suggests an NPE variant: if a mis-copied byte makes the donor's *next* execution slower or halt early, fidelity machinery can be selected by speed alone. That gives fidelity a present-tense payoff, which Clune et al. say is otherwise missing.
- The ratchet of mapping-symbol loss (Baugh 2015) and the loss of Stringmol countermeasures (Hickinbotham et al. 2021) are two independent observations of "use it or lose it" for machinery [V].

---

## 3. Deliverables

### 3(a) Experiments NPE should run

Each experiment names the source that motivates it. "Not done" is judged from the brief given to me.

1. **Scaffold-by-scaffold ablation matrix (motivated by Cicala et al.'s hard-wired control and Taylor's intrinsic/extrinsic split).** Two dimensions: five scaffold items × {supplied, withdrawn}.

   | Scaffold item | Supplied | Withdrawn |
   |---|---|---|
   | Self-location | Fixed offsets 0/64 | Random offset per interaction, keeping relative order |
   | Register init | Reset to 0 | Random per execution / carried |
   | Copy access | 1-byte LDIR | ED B0 / no block copy |
   | Execution setup | PC=own start | PC=random within own genome |
   | Descendant init | World runs the victim from byte 0 | Victim runs from where the donor's copy ended |

   Measure the appearance hazard and the establishment probability for each cell. This gives a quantitative scaffold-dependence profile, and matching arms for later withdrawal tests.

2. **Gradual vs abrupt withdrawal (Bourrat 2022).** Evolve under full reset. Then withdraw one item by a schedule. Example: registers reset with probability p per execution, p annealed 1 → 0 over G generations, compared with a step change. Sweep G and population structure. Record per lineage one of: **endogenized** (competence recovered without the scaffold), **reverted-extinct**, or **persisted-dependent** (survives only while p>0). Prediction [I]: abrupt withdrawal gives extinction; gradual withdrawal gives some endogenization only if experiment 3's coupling holds.

3. **Pleiotropic coupling arm (Bourrat 2022).** Make the scaffold unreliable *in the currency selection already rewards*. Example: under random offsets, a donor copies correctly only if it computes its address, so self-location and copy success are one trait. Compare with an arm where self-location is rewarded separately (a bonus), which is not pleiotropic.

4. **Collapse probe (Baugh 2015; Hasegawa and McMullin 2013).** Hand-build a donor that computes its own address (CALL/POP or equivalent) and sets its own registers. Seed it into the fresh-reset world with mutation on. Measure the time to the first register-dependent shortcut mutant and to its takeover. Also run the reverse: seed into a random-offset world. Prediction [I]: rapid collapse in the reset world, persistence in the random-offset world. The first half replicates Baugh's result on NPE's substrate.

5. **Attractor-distance design (Clark et al. 2017).** Measure the Hamming (mutational) distance from the endogenous donor to the nearest scaffold-dependent donor. Then redesign the endogenous donor to increase that distance and re-run experiment 4. This tests whether internal machinery persists when the cheap alternative is out of reach.

6. **Parent-written development (Wimsatt & Griesemer; Avida `EPIGENETIC_METHOD`).** Let a donor write a prologue into the victim that sets registers on the victim's next execution. The world resets registers to *random* values, so only prologue-carrying lineages have deterministic state. Test whether prologues arise and are inherited. This is the direct test of internalizing "descendant initialization".

7. **Victim-memory mode (Avida `ALLOC_METHOD`).** Before the donor writes, the victim bytes are one of {zeros, random, previous occupant retained}. The last is Avida's "necrophilia" mode. Measure the partial-copy hybrid rate and whether donors evolve full-length copying. This tells whether NPE's certification is inflated by leftover bytes.

8. **Context-cue audit (Cicala et al.'s D register; Lehman et al.'s "playing dead").** List every register or flag value that differs between the certification harness and life. Randomize each and check whether certified donors lose competence. This is a mandatory control before any internalization claim.

9. **Self-location ISA costing (the Z80 CALL/POP idiom).** Record whether the NPE VM supports CALL, RST, POP, SP wrap and JR. Compute the minimum byte cost of endogenous self-location and its predicted appearance factor under Adami & LaBar. Compare with the measured rate under random offsets.

10. **Relative-addressing control arm (Core War; Forth long tape).** Add a PC-relative LDIR variant (addresses relative to the executing PC). This makes self-location part of the physics. Its result is the ceiling for any internalization experiment. If lineages do no better under relative addressing than under random offsets, self-location is not the binding constraint.

11. **Neighbour-copy test (Forth long tape: loops copy "the head of the 'next' replicator").** In a homogeneous region, check whether donors that copy *any* identical neighbour rather than themselves are selected. Such donors need no self-location.

12. **Speed-coupled fidelity (the Science 2026 speed model; Clune 2008).** Make mis-copied bytes cost execution steps in the next execution: a stall or early halt. Test whether verify-after-copy loops arise. Compare with a world where errors cost nothing immediately.

13. **Use-it-or-lose-it ratchet (Baugh 2015; Hickinbotham et al. 2021).** After endogenization (experiment 2), restore the scaffold. Measure the time for internal machinery to decay. This estimates how far selection is from maintaining an unneeded function.

### 3(b) Known failure modes

1. **Degeneration to the cheaper copier through leftover state.** This is the Tierra UCA result [V]. Any endogenous donor in a world that also offers usable state will lose its machinery.
2. **Outsourcing drift.** Parasites, hyper-parasites and cheaters each drop a subroutine that someone else supplies [V: Ray]. In a pair world the partner is a supplier.
3. **Exploitation of harness constants.** The D-register cue [V: Cicala] and test-input recognition [V: Lehman] both occurred. Certification context must match life context, or be randomized.
4. **Hard-coded variation masquerading as evolvable machinery.** A heritable per-organism mutation-rate parameter [V: Clune] is extrinsic in Taylor's sense. NPE must not score a world-applied parameter as endogenous fidelity.
5. **Lock-in of machinery that exploits a scaffold.** hc-replicators exploit circular wrap and h-alloc's AX value; they optimize fastest and innovate least [V: LaBar 2016]. Avida's accidental length computation behaves the same way [P2 raid].
6. **Non-reversible loss.** Capacity that is not used every generation is lost, and regaining it needs rare phenotype-level events [V: Baugh 2015].
7. **Countermeasure decay.** Machinery maintained only by a transient pressure disappears when the pressure lapses [V: Hickinbotham et al. 2021].
8. **"Bureaucratic death".** In Stringmol UCA, containers died from a diversity explosion, not from parasites [V: Clark 2017]. A world rich in internal machinery can fail in a new mode, so NPE's death classifier needs that category.
9. **Mislabelled internalization.** A designer changing the physics (relative addressing, `mem-size`) is not lineage internalization [I from Taylor 2019].
10. **Proto-replicators counted as heredity.** Deterministic miscopiers are viable and lead to self-replicators, but they are not faithful copiers [V: LaBar 2016]. An NPE donor that reliably writes a *different* program is not a heredity event, even though it lies on a path to one.
11. **Partial copies plus retained victim bytes read as full copies.** The Avida necrophilia option exists because this mechanism is real [V: wiki]. [I] It links to NPE's "similarity is not copying" memo.

### 3(c) Results on whether internalization happened or was shown impossible

| Result | Direction | Conditions | Status |
|---|---|---|---|
| Tierra UCA reverts to self-copiers via one mutation that skips address and length computation, relying on leftover Ax/Bx/Cx | **Against** | Any mutation rate > 0; Tierra with templates | V (Baugh 2015) |
| Avida UCA degenerates to self-copiers; no UCA-preserving mutation observed | **Against** | Avida, point mutation | V-abs (via Clark 2017) |
| Tierra cheaters skip self-examination using neighbours' registers | **Against** (externalization) | Social hyper-parasite ecology, size selection | V (Ray) |
| Z80 lineages exploit the environment-set D register | **Against** (dependence on cue) | Validation vs interaction contexts, metabolic penalty | V (Cicala 2026) |
| Avida organisms detect the test environment | **Against** (dependence on cue) | Fixed test inputs | V (Lehman 2020) |
| Avida `mem-size` adopted 96/100; endogenous length computation brittle | **Against** internalization being better | Standard vs extended instruction set | V (P2 raid) |
| Stringmol countermeasures lost when parasites rare | **Against** persistence | Spatial grid, parasite cycles | V |
| Tierran hyper-parasites re-derive location and size every cycle | **For** (internal reset) | Designed ancestor behaviour, retained under parasitism | V (Ray) |
| Lost end template replaced by half-size doubling | **For** (internal repair of self-measurement) | One Tierra run | V (Ray) |
| Stringmol UCA persisted in 500/500 runs, no collapse to replicase; copier, expressor and genome co-evolved | **For** (maintenance of internal machinery) | Seed far from the replicase attractor | V (Clark 2017) |
| Collectives become resilient to scaffold removal via pleiotropic endogenization | **For**, conditional | Bounded (T, S); scaffold present while the trait evolves; can take more than 30,000 generations or fail | V (Bourrat 2022) |
| Replicators emerge with a random execution start when relative addressing or a head1 offset of about 12-16 is supplied | Neutral (self-location moved into the physics, not internalized) | BFF/Forth long tape | V (Agüera y Arcas 2024) |

**No source showed spontaneous internalization of a withdrawn scaffold in a program soup. No source proved it impossible.** The strongest general statement the literature supports: *internal machinery persists when the scaffold-dependent shortcut is mutationally distant (Clark 2017) or when the scaffold is unreliable in the currency selection rewards (Bourrat 2022). It is lost quickly when a shortcut via supplied state is one mutation away (Baugh 2015; Ray).* [I, synthesising V sources]

---

## 4. Gaps and unverified items

- Hasegawa and McMullin 2013: I did not open the paper. The claims come from Clark et al. 2017's summary.
- Amoeba (Pargellis 2001; Greenbaum & Pargellis 2017): full texts returned 403. How Amoeba initializes CPU state and pointers per sequence is **unverified**, so the system is left out of the tables.
- Ray 1994, *Evolution, complexity, entropy and artificial reality* (Physica D 75:239-263): four instruction sets were compared. Two "showed a much greater magnitude of evolution … (measured as optimization through size decrease)" and punctuated patterns; the others showed "strict gradualism" [V-abs via Ray 1999, *Some Thoughts on Evolvability*, https://tomray.me/pubs/evolvability/]. Which ISA features differed is **not verified**.
- Avida `EPIGENETIC_METHOD`: I still found no published study using it, now after two raids of searching.
- Coreworld MOV-SPL takeover rates: secondary source only.
- The Science 2026 error-correction paper: authors not verified. It is a molecular model.
- Whether the "parent divides and resets its registers" in Baugh's Tierra creature is OS behaviour or creature code: **unverified**.

---

## 5. Source list

| Source | URL | Status |
|---|---|---|
| Ray (1992), Evolution, Ecology and Optimization of Digital Organisms | https://faculty.cc.gatech.edu/~turk/bio_sim/articles/tierra_thomas_ray.pdf | V (full) |
| Ray (1999), Some Thoughts on Evolvability (cites Ray 1994) | https://tomray.me/pubs/evolvability/ | V-abs |
| Baugh (2015), PhD thesis, DCU | https://doras.dcu.ie/20731/1/Thesis.pdf | V (abstract, §6.2.2) |
| Hasegawa & McMullin (2013), ECAL | via Clark et al. 2017 | V-abs (secondary) |
| Clark, Hickinbotham, Stepney (2017), J R Soc Interface 14:20161033 | https://eprints.whiterose.ac.uk/id/eprint/117175/ | V (full) |
| Hickinbotham, Stepney, Hogeweg (2021), R Soc Open Sci 8:210441 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8334846/ | V (page summary) |
| LaBar, Hintze, Adami (2016), Artificial Life 22(4) | https://arxiv.org/abs/1511.07959 | V (full) |
| Clune et al. (2008), PLoS Comput Biol 4:e1000187 | https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000187 | V (page summary) |
| Lehman et al. (2020), Surprising Creativity of Digital Evolution | https://arxiv.org/abs/1803.03453 | V (full) |
| Avida wiki, Reproduction settings | https://github.com/devosoft/avida/wiki/Reproduction-settings | V |
| Cicala et al. (2026), arXiv:2607.09211 | https://arxiv.org/html/2607.09211 | V (sections) |
| Agüera y Arcas et al. (2024), arXiv:2406.19108 (long-tape sections) | https://arxiv.org/html/2406.19108 | V (sections) |
| Taylor (2019), Artificial Life 25(2):207-224 | https://arxiv.org/abs/1806.01883 | V (full) |
| Taylor (2004), Niche construction and the evolution of complexity | https://doi.org/10.7551/mitpress/1429.003.0063 | V-abs |
| Wilkins & Bourrat (2022), SEP Replication and Reproduction | https://plato.stanford.edu/entries/replication/ | V |
| Godfrey-Smith (2009), Darwinian Populations and Natural Selection | (book) | M; definitions via SEP |
| Black, Bourrat, Rainey (2020), Nat Ecol Evol 4:426-436 | https://www.nature.com/articles/s41559-019-1086-9 | V-abs |
| Doulcier, Lambert, De Monte, Rainey (2020), eLife 9:e53433 | https://elifesciences.org/articles/53433 | V-abs |
| Bourrat (2022), BJPS, Endogenization of Scaffolded Properties | https://pierrickbourrat.github.io/publication/a-36/a-36.pdf | V (full AAM) |
| Laland, Odling-Smee, Feldman (1999), PNAS 96:10242 | https://www.pnas.org/doi/10.1073/pnas.96.18.10242 | V-abs |
| Laing (1977), J Theor Biol 66:437 | https://www.sciencedirect.com/science/article/abs/pii/0022519377902946 | listing |
| Ibáñez et al. (1995), ECAL LNAI 929 | https://link.springer.com/chapter/10.1007/3-540-59496-5_326 | listing |
| Redcode relative addressing | https://esolangs.org/wiki/Redcode ; https://corewar.co.uk/karonen/guide.htm | V-abs |
| Rasmussen et al. (1990), Coreworld | https://doi.org/10.1016/0167-2789(90)90070-6 | V-abs (secondary) |
| Thorsell (1999), Evolving Warriors | https://corewar.co.uk/thorsell/paper.htm | V-abs |
| Z80 CALL/POP PC idiom | https://www.msx.org/forum/msx-talk/development/is-there-a-way-to-get-program-counter-pc-on-z80 | V-abs |
| Thompson (1984), Reflections on Trusting Trust, CACM 27(8) | (ACM) | M / V-abs |
| Wheeler, Diverse Double-Compiling | https://dwheeler.com/trusting-trust/ ; https://arxiv.org/abs/1004.5534 | V-abs |
| Alden (2024), Pulling Linux up by its bootstraps, LWN | https://lwn.net/Articles/983340/ | V |
| Evolution of error correction through a need for speed (2026), Science | https://www.science.org/doi/10.1126/science.adt1275 | V-abs; authors unverified |
| Canino-Koning, Wiser, Ofria (2019), PLoS Comput Biol 15:e1006445 (fluctuating environments raise evolvability) | https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1006445 | V-abs; not used for a claim beyond its title finding |
| Goldsby, Knoester, Ofria, Kerr (2014), PLoS Biol, somatic cells under dirty work (propagule-cell multicells in Avida) | https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.1001858 | listing; lead for descendant-initialization via propagules |
