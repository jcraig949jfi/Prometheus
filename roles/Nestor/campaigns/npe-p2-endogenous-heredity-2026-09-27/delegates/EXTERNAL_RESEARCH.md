# EXTERNAL_RESEARCH: prior art on self-reproducing programs and the barrier from random variation to sustained heredity

Delegate report for Nestor, NPE P2 (endogenous heredity). Written 2026-09-27. Not committed.

## How claims are marked

- **[V]**: I opened the primary source this session and the claim is taken from its text (abstract, body, or config file).
- **[V-abs]**: verified from the abstract or listing only. The body was not read.
- **[M]**: from memory of the literature. I did not re-open the source this session. Treat these as leads, not facts. The URL/DOI is given so the claim can be checked.
- **[I]**: my own inference, applying a source to NPE. The source does not say it.

Everything here is about integer programs on virtual machines. Where I use a biological word I give its computational meaning.

---

## 0. Decision-relevant summary (read this first)

1. **Every published program soup in which copying emerges resets execution state before each interaction, and the reset values do real work.** In BFF the instruction pointer and both heads start at 0. The 2024 Z80 soup "reset[s] the Z80 emulator" before each 256-step run. The 2026 Z80 soup sets HL, BC, E and PC to 0 and A, F and SP to 0xFF; SP=0xFF resolves modulo the tape to the partner's last byte, so PUSH writes into the partner [V: Agüera y Arcas et al. 2024; Cicala et al. 2026]. The reset constants therefore supply (a) self-location (HL=0 is the start of the executing program) and (b) a pointer into the partner. **NPE's carried registers remove machinery that every successful comparable system gets free from the environment.** [I] This fits NPE's self-poisoning hypothesis. It also means "fresh registers" and "supplied self-location" are confounded in NPE's 0.33 to 0.81 result. Section 4 gives the experiment that separates them.

2. **Contradicting evidence on encoding: the 2-byte LDIR (ED B0) is not prohibitive in a Z80 soup when registers are reset.** In the 2024 Z80 soup (16-byte programs), stack-based replicators appear first and are "eventually" replaced by LDIR/LDDR replicators. In the 2026 Z80 soup (32-byte programs, 512-step budget, 100 seeds), LDIR replicators displace Load-Push replicators and are the most mutation-robust class [V]. NPE's ~1% donor baseline with 2-byte LDIR therefore cannot be blamed on the 2-byte encoding alone. [I] Likely co-factors are carried registers (no HL=0 self-location), 64-96-byte genomes, NPE's step budget, and NPE's stricter certified-copy criterion.

3. **Contradicting evidence on the role of pair interaction.** Knierim, Versari, Obryk, Agüera y Arcas and Saurous (July 2026) used a direct self-replicator detector. With it, a mutation random walk from a tuned byte distribution finds BFF self-replicators faster than the pair-interaction soup: 9.4e4 programs versus 5e6 programs tested. Uniform random 64-byte strings take about 2.9e7 [V]. Their conclusion: pair interaction "is not an unusually powerful search operator". Interaction is needed for spread, not for first appearance [V]. **NPE has not reported a no-interaction random-walk baseline for donor appearance** [I]. Without one, NPE cannot say pair tapes help donors arise.

4. **Establishment failure is normal even with fresh state.** A hand-written BFF self-replicator seeded into a random soup took over in only 22% of 128-epoch runs. The authors name two causes: in half of its interactions the replicator is the right-hand program and "may be irreversibly destroyed by the left-hand-side code", and mutation can destroy it [V]. NPE's 0.33 baseline sits in the same range. **Self-poisoning may be one of several establishment barriers, not the barrier** [I]. The environment-dependence NPE saw (0.33 to 0.81 in one environment, no gain in another) is what you would expect if a second mechanism, such as destruction by the partner or position asymmetry, dominates in the other environment.

5. **Designers of long-running systems built the fresh-register fix in on purpose, and made inherited state a switch.** Avida's default `DIVIDE_METHOD 1` "resets state of mother (effectively creating 2 offspring)". `EPIGENETIC_METHOD 0` means no "inheritance of state information other than genome"; other values let the offspring and/or parent keep registers and stacks. `INHERIT_MERIT 1` means the offspring inherits the parent's merit (CPU-time allocation), which is a non-genetic maternal effect (fitness depends on the parent's state) [V: avida.cfg]. I could not find a published Avida study of the `EPIGENETIC_METHOD` variants. That is a gap NPE could fill.

6. **Stale registers are a known hijack channel.** In Tierra, a hyper-parasite (a program that captures another program's execution) seizes a parasite's instruction pointer. It then re-examines itself and writes its own location and size into the bx and cx registers, so "the CPU of the parasite contains the location and size of the hyper-parasite and the parasite thereafter replicates the hyper-parasite genome" [V: Ray 1991]. The Tierran ancestor re-derives its own address every cycle and does not trust leftover registers. **NPE's copier that uses leftover registers (finding 3) is the opposite design choice.** Tierra's history predicts it is exploitable by whichever program last set those registers [I].

7. **Accessibility of a primitive changes more than the emergence rate.** In Avida, adding a single `mem-size` instruction, which returns genome length without self-inspection, led 96 of 100 runs to use it, and made later length changes easy. Without it, 72.5% of standard-set runs "locked in" a brittle "accidental" length computation that blocked later growth [V: Ofria, Adami & Collier 2002]. **Making LDIR one byte may also change which copy algorithms lock in, and therefore the evolvability of descendants.** Measure it; do not assume it [I].

---

## 1. Line-by-line review (eight questions each)

The eight questions are: Q1 what counts as a reproducer; Q2 machinery supplied by the environment; Q3 what the reproducer must encode; Q4 state outside the nominal genome; Q5 establishment barriers; Q6 how descendant competence is measured; Q7 known stepping stones; Q8 which assumptions NPE violates.

### 1.1 Agüera y Arcas et al. 2024, "Computational Life" (closest prior art)

Agüera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson, Randazzo, Versari (2024). *Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction.* arXiv:2406.19108 (v1 27 Jun 2024, v2 2 Aug 2024). https://arxiv.org/abs/2406.19108 ; HTML https://arxiv.org/html/2406.19108 [V]

**Setup [V].** A soup of 64-byte programs. Random ordered pairs are concatenated into a 128-byte tape and executed for up to 2^13 instruction reads or until the program ends. The tape is then split back ("split(exec(AB)) = A' + B'"). In BFF, the instruction pointer and two data heads (head0, head1) live on the same tape as the code, and the instruction pointer starts at zero. Copy operations are `.` (tape[head1] = tape[head0]) and `,` (the reverse). The default background mutation rate is 0.024%. Other substrates:

- **Forth.** A dedicated `COPY` opcode writes `*(top+64) = *top`. "Executing 0C on an empty stack will copy itself", which is a 1-byte trivial replicator.
- **SUBLEQ.** The smallest hand-written self-replicator the authors managed was 6060 bytes. Nothing emerged in "billions of executions". An RSUBLEQ4 variant has a 25-byte hand-written replicator, and the fetched text says the soup "remained in almost complete random uniformity". I could not confirm from the text I saw whether that sentence refers to RSUBLEQ4 specifically or to SUBLEQ generally; check the PDF.
- **Z80.** A 2D grid of 16-byte programs. Adjacent pairs are concatenated in random order; then "we reset the Z80 emulator and run 256 instruction steps". "Z80 sets the stack pointer at the end of the address space, so pushing values onto stack gives tape A a simple mechanism of writing to tape B." Addresses are taken modulo the tape.
- **8080 long tape.** Replicators "seem to always be two bytes repeated, for example, 01 c5" (load BC with an immediate, then PUSH BC). The text notes: "If execution starts on c5, then BC will be 0 for the first push, and so 00 00 will be written."

**Q1. Reproducer.** Operationally, a soup-level "state transition": high-order entropy (Shannon entropy minus compressed size, using brotli) jumps and the number of unique tracer tokens falls. Tracer tokens are (epoch, position, char) tuples. Replicators are then inspected by hand. The authors concede that a program copying itself "with a specific offset different from 64" is functional but not detected as a perfect self-copy [V].

**Q2. Environment-supplied machinery.** Pairing, concatenation and splitting. Reset of the instruction pointer and heads, or of the whole CPU, before every interaction. Modular addressing. In Z80, the initial SP points into the partner. In Forth, COPY has a built-in +64 offset, so the destination address is supplied.

**Q3. Encoded by the reproducer.** A loop or straight-line sequence that moves bytes from its own half to the partner's half. The source address is usually free because heads or registers start at 0. [I] In no substrate does the replicator have to compute its own address; the reset makes "I am at 0" true.

**Q4. State outside the genome.** None across interactions: execution state is reset [V for BFF and Z80]. For long-tape Forth and 8080 the text does not say whether stacks or registers are cleared per thread [V: absence in the text I fetched].

**Q5. Establishment barriers [V].** Seeded replicator takeover was 22% in 128 epochs. The causes: the replicator is the right-hand partner half the time and can be destroyed, and mutation. In "short" runs (random initialization, 128 epochs), transitions happened 3 in 1000. In "long" runs (16k epochs), about 60% fail. A transient "zero-poisoning" period follows emergence, before a new replicator family takes over.

**Q6. Descendant competence.** Measured only indirectly, as soup-level takeover. There is no per-lineage assay. The 2026 follow-up (1.2) explicitly calls this a limitation.

**Q7. Stepping stones [V].** Self-replicators "arise mostly due to self-modification". With zero background mutation, transitions occur at "roughly the same frequency". With no noise and a fixed interaction schedule, about 50% of runs transition. In Z80, a stack-based (PUSH) replicator ecosystem comes first and is then replaced by LDIR/LDDR block-copy replicators.

**Q8. Assumptions NPE violates [I].**
- (a) NPE carries registers across executions, whereas all of these systems reset them.
- (b) NPE's 64-96-byte genomes are larger than the 16-byte Z80 programs.
- (c) NPE requires a certified causal rebuild of a randomized victim, which is far stricter than a takeover signal. NPE's rates are therefore not comparable to their 40% BFF transition rate without translation.
- (d) NPE altered the ISA encoding (LDIR as 1 byte). Their Z80 used the real 2-byte ED B0.

### 1.2 Follow-ups, 2025-2026

**Knierim, Versari, Obryk, Agüera y Arcas, Saurous (1 Jul 2026). *BFF: Simple explanations for complex phenomena.* arXiv:2607.01483. https://arxiv.org/abs/2607.01483 [V, full text]**

- **Q1.** They introduce a direct detector (Algorithm 1). A candidate P is run in the right half of 10 tapes. Each tape runs a chain of 5 executions; at each step the previous right half moves to the left and the right half is refilled with noise. Per position, they count bytes that match P in at least 3 of the final tapes, for each half, and take the minimum of the two halves. The score runs 0-64 and the threshold is 48 (results are "not significantly" different for thresholds of at least about 20). The chain length is odd so that self-inverting replicators are caught. Documented false positive: a program of alternating bytes 128, 130 with a 4-byte copier shifts itself by 2 each run and scores highly until the copier wraps and dies.
- **Q5/Q7.** "Emergence of self-replicators is quite robust to merger blocking". A merger is a consecutive copy of at least two bytes not previously copied together. Blocking deep or wide mergers "merely stops self-replicators from taking over the soup". With depth 0 (no copying at all) the first replicator still appears in 40% of runs after 50M epochs.
- **Search-rate numbers.** First replicator after about 2.5e6 interactions (5e6 programs tested). Uniform random sampling needs 2.9e7 programs. Tuned byte distributions need 1.7e6, 4.5e5 and 9.4e4 programs. Mutation walks at p=1/100 need 9.9e5 [V].
- **Q8 [I].** This is the strongest contradiction of any claim that pair interaction is what creates donors. It supports treating byte-level accessibility (distribution or encoding) as a first-order variable.

**Cicala, Niklasson, Randazzo et al. (2026). *Coevolution of self-replication and function in a digital primordial soup.* arXiv:2607.09211 (v2, 2 Sep 2026). https://arxiv.org/abs/2607.09211 [V, HTML]**

The closest substrate to NPE: Z80, pair tapes.
- **Setup.** 32-byte programs concatenated into a 64-byte memory. Execution begins at the first byte of the first program, with a budget of B=512 instructions. "Registers HL, BC, and E, and the program counter PC are set to zero; registers A and F, and the stack pointer, are set to 0xFF". SP=0xFF resolves modulo 2l to the last byte, so stack writes grow backwards into the partner. There are 2,097,152 programs in 32 niches of 128x128 grids, run for 1M epochs. Each program has a 1/64 per-epoch chance of one random byte being reinitialized.
- **Q1.** Replication is detected by byte-pattern matching of known families: Load-Push, LDIR (0xED 0xB0) and LDD. [I] This is a weaker criterion than a causal test.
- **Q2/Q3.** "Setting HL to the start of parent P1, DE to the start of partner P2, and BC to 32 copies the entire program". Because HL and BC reset to 0, the program must set at least DE and BC, but self-location (HL=0) is free.
- **Q5/Q7.** Load-Push replicators dominate early and are displaced by more compact LDIR replicators. The robustness ranking after 8 random byte mutations is LDIR >> LDD >> Load-Push. A step penalty ("metabolic constraint") selects for conditional halting. Moderate cross-niche migration (π=0.05) beats isolation and high connectivity.
- **Q6.** Task competence is checked on 3 validation inputs. A hard-wired copying control (the copy is made without executing Z80 code) solves more hard tasks, but emergent copying keeps "broader genealogies".
- **Q8 [I].** NPE differs in carried registers, genome length, the 1-byte LDIR re-encoding, and the causal copy test.

**Jha, Cicala, Agüera y Arcas, Richards, Jaques, Kleiman-Weiner, Niklasson (9 Sep 2026). *Tapes Together Strong: The Co-evolution of Computation and Cooperation.* arXiv:2609.10817. https://arxiv.org/abs/2609.10817 [V-abs]** On Z80 with endogenous energy, "parasitic stealing destroys shared energy, slows execution, and can prevent reliable replication". This is another establishment barrier: a partner's code interfering with replication.

**Hintze & Bohm (11 Aug 2025). *Rethinking Self-Replication: Detecting Distributed Selfhood in the Outlier Cellular Automaton.* arXiv:2508.08047. https://arxiv.org/abs/2508.08047 [V-abs]** They detect replicators by causal-ancestry tracing. Replicators are often "multiple disjoint clusters working in coordination". [I] This is a warning that the unit that reproduces may not be one 64-96-byte genome.

**Cotler, Hongler, Hudcová (9 Oct 2025). *Self-replication and Computational Universality.* arXiv:2510.08342. https://arxiv.org/abs/2510.08342 [V-abs]** They construct a Turing-universal cellular automaton (CA) that supports "transcription and translation but cannot instantiate replication". Universality is not sufficient for replication. SUBLEQ (1.1) is the empirical counterpart.

**Yin (26 Mar 2026). *The Self-Replication Phase Diagram.* arXiv:2603.25239. https://arxiv.org/abs/2603.25239 [V-abs]** A census of all 262,144 outer-totalistic binary CA: 7.69% support proliferation. The paper uses a three-tier detector to separate causal self-replication from pattern proliferation. The same distinction appears as a pitfall in section 2.

### 1.3 Avida (Ofria, Lenski, Adami and colleagues)

Sources:
- Ofria & Wilke (2004), *Avida: a software platform for research in computational evolutionary biology*, Artificial Life 10(2). https://dl.acm.org/doi/10.1162/106454604773563612 [V-abs]
- Avida configuration file, https://raw.githubusercontent.com/devosoft/avida/master/avida-core/support/config/avida.cfg [V]
- Default ancestor tour, https://github.com/devosoft/avida/wiki/Default-Ancestor-Guided-Tour [V]

**Q1.** An organism reproduces by executing `h-divide` after copying. Divides are subject to environment checks: `MIN_COPIED_LINES 0.5` (fraction of code that must be copied before divide), `MIN_EXE_LINES 0.5` (fraction that must be executed), `OFFSPRING_SIZE_RANGE 2.0` and `REQUIRE_ALLOCATE 1` [V]. In landscape studies a genotype counts as a replicator if a test CPU gives non-zero fitness and marks it viable (C G et al. 2017) [V].

**Q2.** Heavy. `h-alloc` allocates the offspring's memory, `h-copy` copies one instruction from the read head to the write head and advances both, `h-divide` splits off the region between the heads, and `h-search` places the flow head by template. The CPU provides three registers, two stacks and three heads. A per-copy mutation rate (`COPY_MUT_PROB 0.0075`) is applied by the environment. The parent is reset after divide (`DIVIDE_METHOD 1`) [V].

**Q3.** A copy loop: h-search, h-copy, if-label, mov-head, plus alloc and divide. The default ancestor is 15 instructions [V]. The minimum replicator is 8 instructions. None exist at length 7 (exhaustive search), and 914 of 26^8 ≈ 2.09e11 length-8 genomes replicate. That is about 5.9 "mers" of information (log base 26) [V: C G, LaBar, Hintze, Adami 2017, arXiv:1701.03993, https://arxiv.org/abs/1701.03993]. Every one of the 914 contains h-copy, h-alloc and h-divide [V].

**Q4.** By default none, since the mother's registers and stacks are cleared on divide. Exceptions: `INHERIT_MERIT 1`, where the offspring's CPU speed comes from the parent (a maternal effect: fitness set by the predecessor's state). `EPIGENETIC_METHOD` values 1-3 let the offspring inherit, or the parent keep, "registers and stacks of first thread". `DIVIDE_FAILURE_RESETS 0` means a failed divide does not reset the CPU [V]. I found no paper studying `EPIGENETIC_METHOD` [V: absence in searches, not proof of absence].

**Q5.** Emergence is rare because replicators are informationally costly. The paper estimates that a 15-instruction hand-written ancestor, "were it the only replicator among sequences of that length", would take 1000 processors at 1e6 sequences/s about 50,000 years to find [V, C G 2017]. Replicators are clustered, not uniform: two families (fg- and hc-motif) and 41 genotype clusters. Progenitors of the eventual winners come from "a small region" of replicator space [V].

**Q6.** Test-CPU fitness. Knockout and one-step-mutant scans: every single-point mutant is classified as fatal, deleterious, neutral or beneficial [V: Ofria, Adami & Collier 2002]. Line-of-descent reconstruction [V: C G 2017]. Evolvability assays: 170 random replicators from 3e9 sampled sequences; "evolvability is a likely—but not a guaranteed—property", and some replicators are "evolutionarily sterile" [V-abs: LaBar, Adami, Hintze 2015, *Does self-replication imply evolvability?*, ECAL 2015, arXiv:1507.01903, https://arxiv.org/abs/1507.01903].

**Q7.** Only fg-replicators evolved computational tasks in the C G 2017 experiments [V]. Complex functions build on simpler rewarded functions, and deleterious mutations sometimes served as stepping stones [V-abs: Lenski, Ofria, Pennock, Adami 2003, *The evolutionary origin of complex features*, Nature 423:139-144, https://www.nature.com/articles/nature01568]. The specific counts (EQU in 23 of 50 populations; none when only EQU was rewarded) are [M]. Small populations grew genomes via "slightly deleterious insertions", large ones via "rare beneficial insertions" [V-abs: LaBar & Adami 2016, arXiv:1604.06299, https://arxiv.org/abs/1604.06299].

**Q8 [I].** NPE supplies no alloc or divide, no heads, and no per-copy mutation hook, so its donors must encode what Avida gives as three opcodes. NPE's certified test roughly plays the role of Avida's divide checks. But Avida's reset-on-divide is exactly the "fresh registers" condition NPE found helpful, and Avida makes it the default.

**Instruction-set design (encoding accessibility) [V].** Ofria, Adami & Collier (2002), *Design of evolvable computer languages*, IEEE TEC 6(4):420-424, https://langev.com/pdf/ofria02ieee.pdf (full text read).
- The added `mem-size` instruction "will return the genome length without complex self-inspection". It was used in 96/100 runs and made insertions and deletions "more neutral".
- In the standard set, organisms replaced template-based size calculation with an "accidental" computation, for example doubling the address of the copy loop. This is "brittle", and 72.5% of runs locked in a non-robust algorithm by 20,000 updates (44.5% within 2,000 updates).
- Removing templates (the no-nop set) made the chemistry "extremely inflexible".
- A larger instruction set (84 instructions) "lags in fitness".

Bryson & Ofria (2013), *Understanding Evolutionary Potential in Virtual CPU Instruction Set Architectures*, PLOS One, arXiv:1309.0719, https://arxiv.org/abs/1309.0719 [V-abs]: of six ISA features, only multiple-argument specification and separated I/O helped in most environments.

**Information-theoretic emergence [V-abs].** Adami & LaBar (2015), *From Entropy to Information: Biased Typewriters and the Origin of Life*, arXiv:1506.06988, https://arxiv.org/abs/1506.06988. The probability of spontaneous emergence "depends exponentially on the amount of information that is necessary for replication". A biased monomer distribution (here, a biased instruction-frequency distribution) "can exponentially increase" it. There "may be an optimum sequence length".

### 1.4 Tierra (Ray)

Ray, T. S. (1991). *An approach to the synthesis of life.* Artificial Life II, 371-408. Full text from the author: http://tomray.me/pubs/alife2/Ray1991AnApproachToTheSynthesisOfLife.pdf ; LaTeX http://tomray.me/pubs/alife2/tierra.tex [V, full text]

**Q1.** A program that allocates a daughter block (MAL), copies itself into it and executes DIVIDE, producing a daughter with its own instruction pointer.

**Q2.** Memory allocation with write protection ("semi-permeable membrane": others can read and execute but not write). A scheduler ("slicer") allocates CPU time. Template addressing: jumps and searches find complementary NOP patterns within a search limit of 200-400 instructions. The CPU has two address registers, two numeric registers, flags and a stack. A 32-instruction set with no numeric operands. Background mutation (about 1 bit per 10,000 instructions executed), copy mutation (about 1 bit per 1,000-2,500 instructions moved), and "flawed" instruction execution (results off by ±1 at a low rate) [V].

**Q3.** Self-examination: the ancestor finds its start and end templates, computes its size, allocates, runs a copy loop and divides. The ancestor is 80 instructions, 48 of which are NOPs [V].

**Q4.** The mother's CPU is not described as reset after divide. It loops back and re-examines itself. The daughter gets a new instruction pointer [V]. Registers matter across organisms: the hyper-parasite hijack described in section 0, point 6 [V].

**Q5.** 80% of mutations in a template destroy it. A single bit change in instruction 42 turns the 80-instruction ancestor into the 45-instruction parasite 0045aaa, which cannot replicate alone [V]. Size-79 hosts resisted parasites [V].

**Q6.** Competence is measured by culture tests: grow a genotype alone versus in mixed culture with a host [V].

**Q7.** The observed ecological sequence: parasites, then host immunity, then parasites that circumvent it, then hyper-parasites, then "social" hyper-parasites that replicate only when a similar neighbor catches their jump, then cheaters (hyper-hyper-parasites) that sit between social programs and capture the instruction pointer. One lineage also evolved "novel self-examination": half the genome length, then doubled [V]. That is the same brittle-length trick Ofria et al. 2002 later documented in Avida.

**Q8 [I].** NPE has no write protection, since pair tapes are mutually writable. Ray argues protection is what stabilises Tierra, and Ofria et al. 2002 [V] argue the same about Avida's separate cells versus Coreworld overwriting. NPE has no template addressing; self-location must come from registers or absolute addresses.

### 1.5 Core War and Coreworld

Rasmussen, Knudsen, Feldberg, Hindsholm (1990). *The coreworld: emergence and evolution of cooperative structures in a computational chemistry.* Physica D 42:111-134. https://doi.org/10.1016/0167-2789(90)90070-6 (via https://dl.acm.org/doi/10.1016/0167-2789(90)90070-6) [V-abs]

- **Setup [V-abs].** One-dimensional core, parallel update, local communication only, continuous noise, local computational resources. "Extremely viable cooperative structures" emerged, and the authors identify seven evolutionary epochs.
- **Emergence claims [M].** A secondary source says simple two-instruction MOV-SPL self-replicators "often take over" [V-abs: secondary]. Cicala et al. 2026 cite Rasmussen 1990/1991 as demonstrating spontaneous replication [V]. My recollection is that Rasmussen and colleagues reported the soup was fragile because programs overwrite each other. That is also Ofria et al.'s 2002 reading: "organisms cannot corrupt the genome of other organisms by overwriting, as happens in coreworld" [V].
- **Q8 [I].** Coreworld's unprotected shared core is the closest older analogue of NPE's mutually writable pair tape. Its reported fragility is prior evidence that establishment, not appearance, is the hard part when every program can write over every other.

Modern Core War work (for example, the LLM-driven "Digital Red Queen", arXiv:2601.03335, https://arxiv.org/abs/2601.03335 [V-abs listing]) is adversarial program search, not spontaneous emergence. I found no modern study of spontaneous replicator emergence in Redcode from random cores. I could not verify that none exists.

### 1.6 Amoeba (Pargellis) and other spontaneous-emergence worlds

- Pargellis (1996), *The evolution of self-replicating computer organisms*, Physica D, https://dl.acm.org/doi/10.1016/0167-2789(96)00089-9 [V-abs via search listing]. Random sequences from a 16-opcode basis "with a probability of about 10^-4 ... spontaneously generate large and inefficient self-replicating 'organisms'" (quoted from the search summary; [M]-level confidence on the exact figure).
- Pargellis (2001), *Digital life behavior in the Amoeba world*, Artificial Life 7(1):63-75 [M].
- Greenbaum & Pargellis (2017), *Self-Replicators Emerge from a Self-Organizing Prebiotic Computer World*, Artificial Life 23(3):318-342, https://direct.mit.edu/artl/article/23/3/318/2891 and https://pubmed.ncbi.nlm.nih.gov/28786722 [V-abs]. Amoeba has "no write protection" and a "computationally universal opcode basis". After adding pattern-based addressing and entropy injection, it "shows a far richer emergence, exhibiting a self-organization phase followed by the emergence of self-replicators".
- **Q7 [I].** A pre-replicative self-organization phase in which the byte statistics shift before copying appears. This matches Knierim's finding that a tuned byte distribution accelerates discovery 25x. Together they suggest the soup's first job is to bias its own "typewriter" (its byte-frequency distribution).
- Chou & Reggia (1997), *Emergence of self-replicating structures in a cellular automata space*, Physica D 110:252-276, https://www.sciencedirect.com/science/article/abs/pii/S0167278997001322 (PDF mirror https://gwern.net/doc/cs/cellular-automaton/1997-chou.pdf) [V-abs]. The first CA in which a replicator emerges from a random initial state. It uses 256 states per cell with a rule set designed to support replication of structures of different sizes. [I] Here the environment (the rule table) supplies most of the machinery.

### 1.7 von Neumann and self-reproducing cellular automata

- von Neumann (1966, ed. Burks), *Theory of Self-Reproducing Automata*, https://archive.org/details/theoryofselfrepr00vonn_0 [V-listing; content M]
- Sayama & Nehaniv (2024), *Self-Reproduction and Evolution in Cellular Automata: 25 Years after Evoloops*, Artificial Life 31(1), arXiv:2402.03961, https://arxiv.org/abs/2402.03961 [V, full text]

**Q1 [V: Sayama & Nehaniv].** Three criteria are in use. Moore's criterion counts exact copies. Langton's criterion: "a system must blindly copy instructions to the offspring (genome), and these instructions must be executed to generate a phenotype". von Neumann's criterion: "A self-reproducer must have capacity for inheritable mutation". The review separates self-replication (identical copies) from self-reproduction (heritable variation). Langton's loop satisfies Langton's criterion but not von Neumann's. Evoloops satisfy both. Langton's criterion does not recognise reproduction by self-examination.

**Q2.** The transition table is the environment. von Neumann's 29-state CA supplies a universal constructor architecture. Codd (1968) reduced it to 8 states. Langton's loop (1984; Physica D 10:135-144, https://doi.org/10.1016/0167-2789(84)90256-2 [M]) dropped universal construction. Byl's (1989) loop is smaller still (Physica D 34:295-299 [M]). In the review's words, the progressively simplified loops raise doubt about whether "the resulting minimal replicators are really non-trivial... their complexity is in the eyes of the observer" [V].

**Q3.** A tape (description) plus, in von Neumann, a constructor that builds from the tape and a copier that copies the tape uninterpreted. In loops, a circulating sequence of signal states.

**Q4.** None in principle; all state is in the cells. [I] But loops depend on an intact sheath and on particular neighbourhood configurations, which is spatial context.

**Q5.** Before Sayama, dead loops clogged space. Structural dissolution (Sayama 1998/1999, "dissolving" states that erase debris) freed space and allowed generational turnover. Evoloops (Sayama 1999, Artificial Life 5(4):343-365 [V as cited]) made the rules robust to collisions, so variation did not immediately kill loops [V].

**Q6.** Genetic sequencing of every loop that ever appears: Salzberg & Sayama (2004), Complexity 10(2):33-39, https://philpapers.org/rec/SALCGE [V-abs]. They found "long-lasting genetic and behavioral diversity and complex genealogy". Yinusa & Nehaniv (2011) showed that mutations to von Neumann's tape yield lethal, neutral and complexity-increasing heritable variants, but the variants were "genetically engineered", not produced by an intrinsic process [V as cited].

**Q7.** Evoloops evolve toward smaller loops, which reproduce faster. [M] This is the standard account; Salzberg & Sayama show diversity persists after the minimum size is reached [V].

**Q8 [I].** NPE's copy is by self-inspection: a donor reads its own bytes with LDIR. In von Neumann's taxonomy this is "Mech. 1", which Langton's criterion does not recognise. It also means that a byte the donor never reads cannot be inherited, and the copy is only as general as the address range the donor happens to cover.

### 1.8 Quines and self-reference

- Kleene's recursion theorem guarantees fixed points (programs that output their own source) in any acceptable programming system [M].
- Sarkar (2020), *Quines are the fittest programs*, arXiv:2010.09646, https://arxiv.org/abs/2010.09646 [listing only]: under nested universal priors, self-replicating fixed points are attractors.
- Moss (2023), *Algebra of Self-Replication*, arXiv:2309.09931, https://arxiv.org/abs/2309.09931 [listing only].

[I] A quine prints its text; it does not need its address. A memory-copy replicator needs a source address, a destination address and a length. That is exactly the information that register resets (BFF, Z80) or a +64 offset (Forth) supply. NPE's finding 3 (a copier that uses leftover registers) is a replicator that obtains those three numbers from the machine's history instead of from its text or from the environment. It is not a quine in the computability sense, because its output depends on a state that is not a function of its text.

### 1.9 Error threshold, hypercycles and maternal effects in formal models

- Eigen (1971), *Selforganization of matter and the evolution of biological macromolecules*, Naturwissenschaften 58:465-523, https://doi.org/10.1007/BF00623322 [M]
- Eigen & Schuster (1977-78), the hypercycle, Naturwissenschaften 64:541 ff., https://doi.org/10.1007/BF00450633 [M]

Content [M]: a master sequence of length L copied with per-symbol fidelity q and relative advantage σ is maintained only if q^L·σ > 1, roughly L < ln σ / (1 − q). The maximum heritable length therefore scales inversely with the per-symbol error rate. Hypercycles were proposed to escape the limit through cooperation between short replicators, and are known to be vulnerable to parasites.

Wilke, Wang, Ofria, Lenski, Adami (2001), *Evolution of digital organisms at high mutation rates leads to survival of the flattest*, Nature 412:331-333, https://doi.org/10.1038/35085569 [M]. At high mutation rates, Avida genotypes with lower replication rate but greater mutational robustness outcompete faster, fragile ones.

Wilke (2002), *Maternal effects in molecular evolution*, Phys. Rev. Lett. 88:078101, arXiv physics/0106093, https://arxiv.org/abs/physics/0106093 [V-abs]. In a model where "the fitness of an individual depends both on its own and on the parent's genotype", parental effects vanish from mean fitness at equilibrium but persist in sequence distributions. "For smaller populations, parental genotype effects substantially shift the error threshold location." The paper explicitly mentions "self-replicating computational systems".

**Q8 [I].** NPE's register carry-over is formally a maternal effect: the performance of execution n depends on the state left by execution n−1, which in NPE is the same organism's previous run or its partner's. Wilke's result predicts that the effect matters most in small populations and in transients such as establishment, and less at equilibrium. That is exactly where NPE sees it.

### 1.10 Autocatalytic sets, RAF theory, chemical organization theory, AlChemy

- Kauffman (1986), *Autocatalytic sets of proteins*, J. Theor. Biol. 119:1-24, https://doi.org/10.1016/S0022-5193(86)80047-9 [M]
- Hordijk & Steel (2004), *Detecting autocatalytic, self-sustaining sets in chemical reaction systems*, J. Theor. Biol. 227:451-461 [V-abs via search]. Defines RAF (reflexively autocatalytic, food-generated) sets and gives a polynomial-time detection algorithm. Formal definition: arXiv:2303.01809, https://arxiv.org/abs/2303.01809 [listing].
- Hordijk, Steel & Kauffman (2012), *The Structure of Autocatalytic Sets: Evolvability, Enablement, and Emergence*, Acta Biotheoretica 60:379-392, https://link.springer.com/article/10.1007/s10441-012-9165-1 [V-abs]. RAF sets decompose into sub-RAFs, which are candidate heritable units.
- Dittrich & Speroni di Fenizio (2007), *Chemical organisation theory*, Bull. Math. Biol. 69:1199-1231, https://doi.org/10.1007/s11538-006-9130-8 [M]. An organization is a set of species that is closed (produces nothing outside itself) and self-maintaining.
- Hordijk, Steel & Dittrich (2018), *Autocatalytic sets and chemical organizations*, New J. Phys., https://iopscience.iop.org/article/10.1088/1367-2630/aa9fcd [V-listing]

**Contradicting evidence for inheritance without a copied genome [V-abs].**
- Vasas, Szathmáry & Santos (2010), *Lack of evolvability in self-sustaining autocatalytic networks constraints metabolism-first scenarios for the origin of life*, PNAS 107:1470-1475, https://www.pnas.org/doi/10.1073/pnas.0912628107
- Vasas, Fernando, Santos, Kauffman & Szathmáry (2012), *Evolution before genes*, Biology Direct 7:1, https://link.springer.com/article/10.1186/1745-6150-7-1 : "autocatalytic sets of organic polymer molecules could not undergo evolution by themselves"; some accumulation of adaptations is possible under specific conditions.
- Szathmáry & Maynard Smith (1997), *From replicators to reproducers*, J. Theor. Biol. 187:555-571, https://pubmed.ncbi.nlm.nih.gov/9299299/ [V-abs via search]. Distinguishes limited heredity (few possible heritable states) from unlimited heredity (indefinitely many forms, modular replication).

**Q4/Q8 [I].** Register state (a handful of 8/16-bit registers) is a limited-heredity channel in Szathmáry and Maynard Smith's sense. Even if carried registers help a lineage, they cannot carry open-ended information. They can carry only a small number of attractor states, which is the compositional-inheritance problem Vasas et al. identified.

**Fontana & Buss AlChemy** (1994), *"The arrival of the fittest"*, Bull. Math. Biol. 56:1-64, https://link.springer.com/article/10.1007/BF02458289 [V-listing].
- Level-0 organizations: in a lambda-calculus chemistry, the copy function (λx.x) "emerge[s] easily and quickly take[s] over". The number of unique expressions tends to one. This description comes from the re-analysis by Mathis, Patel, Weimer & Forrest (2024), *Self-organization in computation and chemistry: Return to AlChemy*, Chaos 34:093142, arXiv:2408.12137, https://arxiv.org/abs/2408.12137 [V-abs]. That re-analysis also finds complex organizations "more frequently than previously expected" and robust against collapse, but hard to combine.
- **Q8 [I].** A trivial 1-byte copier in NPE (see Forth's `0C`) is the program analogue of AlChemy's identity function: very accessible, and it homogenises the population. Accessibility of the copy primitive trades against diversity.

### 1.11 Automata chemistries with bound pairs (Stringmol) and parasite ecology

Hickinbotham, Stepney & Hogeweg (2021), *Nothing in evolution makes sense except in the light of parasitism: evolution of complex replication strategies*, R. Soc. Open Sci. 8:210441, https://royalsocietypublishing.org/rsos/article/8/8/210441/96415 [V-abs via search]. In Stringmol, "molecules" are opcode strings. A binding pair executes as a reaction whose product depends on both sequences, which is conceptually close to NPE's pair tape. The system is seeded with a hand-designed copier ("replicase"). Parasites arise, and complexity evolves only where "spatial pattern formation prevents global extinction". I did not verify how Stringmol initialises execution state (pointers) per binding.

### 1.12 Open-ended evolution (Packard, Taylor, Bedau)

- Packard, Bedau, Channon, Ikegami, Rasmussen, Stanley & Taylor (2019), *An Overview of Open-Ended Evolution*, Artificial Life 25(2):93-103, https://doi.org/10.1162/artl_a_00291 ; arXiv:1909.04430 [V-listing]
- Taylor (2015), *Requirements for Open-Ended Evolution in Natural and Artificial Systems*, arXiv:1507.07403, https://arxiv.org/abs/1507.07403 [V-abs]. Five requirements, the first being "robustly reproductive individuals" and the fourth "mutational pathways to other viable individuals".
- Bedau, Snyder & Packard (1998), evolutionary activity statistics (ALIFE VI) [M]: a lineage's "activity" accumulates while it persists; the shape of activity waves is compared against a shuffled neutral model.

[I] For NPE: Taylor's requirement 1 ("robustly reproductive") is exactly NPE's establishment problem. Bedau's neutral-shadow method is a ready-made control for "descendant persistence exceeds what drift gives".

---

## 2. (a) Failure modes and measurement pitfalls NPE should check itself against

1. **Appearance confounded with spread.** Takeover or compression signals time the moment a replicator dominates, not the moment it appears. The 2026 BFF paper built a direct detector specifically because of this. It showed that appearance happens under mutation alone and under interaction alone, whereas spread needs interaction [V: Knierim et al. 2026]. NPE should report per-program appearance hazards separately from establishment probabilities.

2. **Detector false positives from shifting or partial copies.** A program that shifts itself by 2 bytes each run scored 56/64 until its copier wrapped and died [V: Knierim et al. 2026]. Checks for NPE:
   - Require stability over a chain of at least 5 generations.
   - Test against at least 10 independent noise partners.
   - Use an odd chain length, to catch self-inverting copiers.
   - Score per position, not by overall similarity.

3. **Test context differs from the life context.** Avida analyses genotypes in a reset test CPU [V]. If NPE carries registers in the population but certifies donors with fresh (or specific) registers, the certified phenotype is a different program behaviour from the one that must establish [I]. Certification should record, and ideally sweep, the entry register state.

4. **Hidden environment constants acting as machinery.** Reset values (HL=0, SP=0xFF, head=0) silently supply self-location and a destination [V: 2024, 2026]. NPE should list every constant the harness injects: initial PC, SP, flags, tape offset of each genome, and wrap behaviour. Each counts as environment-supplied machinery when comparing to prior work [I].

5. **Position asymmetry.** Only the program that executes first acts. A seeded replicator is destroyed about half the time as the right-hand partner [V: 2024]. NPE's establishment numbers should be split by execution order [I].

6. **Probabilities over a fixed horizon are not rates.** "1% to 60% of runs" and "0.33 to 0.81" are probabilities within a horizon. Knierim et al. report programs tested to first replicator. [I] Convert to a per-execution hazard (for example, −ln(1−p)/N) before comparing effect sizes, or the saturation near 60-80% will understate the true factor.

7. **Brittle lock-in.** Early-winning algorithms may block later evolution. Avida: 44.5% of standard-set runs locked in a brittle length computation within 2,000 updates [V: Ofria et al. 2002]. A donor that relies on leftover registers is structurally the same kind of brittle, accidental computation [I].

8. **Replication without evolvability.** Some random replicators are "evolutionarily sterile" [V-abs: LaBar et al. 2015]. hc-type Avida replicators never evolved tasks [V: C G 2017]. A certified donor is not evidence of a heritable-variation-capable lineage (von Neumann's criterion [V: Sayama & Nehaniv 2024]).

9. **Similarity is not copying; convergence is not heredity.** This is the same trap as NPE's internal feedback memo. The prior-art version: high-order entropy falls whenever the soup converges, including during "zero-poisoning" [V: 2024]. AlChemy's L0 collapse also reduces diversity without complex heredity [V-abs].

10. **Non-determinism and approximate counters.** The 2024 long-tape runs skip locking, "which also means that all counters are approximate" [V]. If NPE runs parallel lanes, verify that counts are exact.

11. **PRNG artefacts.** With a PRNG, "Kolmogorov complexity is by definition bounded by program size" [V: 2024]. Compression-based complexity measures can be fooled by structure the generator itself introduces.

12. **Block-copy step accounting [I, not from a source].** On a real Z80, LDIR with BC=0 copies 65,536 bytes. Whether a repeating instruction counts as one step or as BC steps changes the effective budget. Under modular wrap, it also changes whether a copy overwrites its own source. Check how NPE's VM counts LDIR steps, and whether the 1-byte re-encoding changed step accounting as well as encoding length.

13. **Genome-unit ambiguity.** Replicators may be distributed across disjoint pieces [V-abs: Hintze & Bohm 2025]. A pair-tape "donor" may need bytes from the partner to work. Certify with randomized partners, which NPE already does. Also check whether competence survives when the partner is a copy of the donor.

---

## 3. (b) Concrete experiments the literature suggests that NPE has not done

Each experiment names its motivating source. "NPE has not done" rests on the context brief I was given; verify against NPE's ledger.

1. **Reset-value decomposition (the key experiment).** Four arms for register state at each execution:
   - (i) carried (current),
   - (ii) fresh to fixed constants chosen like Cicala et al. (HL=BC=0, SP=last byte of tape),
   - (iii) fresh to constants that do *not* point at self or partner (for example HL=SP=0x40 off-tape, or random but fixed per run),
   - (iv) random per execution.

   Arm (ii) versus (iii) separates "clean state" from "free self-location/destination". Motivation: Cicala et al. 2026 [V] and Agüera y Arcas et al. 2024 [V]. Predicts which environment gave 0.33 to 0.81 and which did not.

2. **A random-walk and uniform-sampling baseline for donor appearance**, using the same certified test. Count programs tested to first certified donor under (a) uniform bytes, (b) the empirical byte distribution of NPE soups, and (c) mutation walks at p=1/100 and 1/200. Compare with the pair-tape soup. Motivation: Knierim et al. 2026 [V].

3. **Byte-distribution tuning instead of re-encoding.** Keep LDIR as ED B0, but raise P(ED) and P(B0) in the initial and mutation distributions until the per-program probability of the ED-B0 pair matches the 1-byte encoding's single-byte probability. If donor rates match, the effect is information cost, not "one instruction versus two" per se. Motivation: Adami & LaBar 2015 [V-abs]; Knierim et al. 2026 [V].

4. **Exhaustive or large-sample landscape of minimal donors.** Find the minimal donor length under each encoding, as C G et al. 2017 did (914 of 26^8). Cluster the donors by one-mutation connectivity. Record which clusters the progenitors of established lineages come from [V: C G 2017].

5. **Seeded-establishment assay with a branching-process readout.** Insert one certified donor. Record fixation or loss by execution order (left/right), by register mode (experiment 1), and with mutation on or off. Estimate establishment probability with confidence intervals against the BFF 22% reference [V: 2024].

6. **Merger depth/width blocking.** Forbid copies of previously unmerged byte runs above depth or width k. Test whether donors arise compositionally and whether blocking hits appearance or only spread [V: Knierim et al. 2026].

7. **Knockout, lesion and robustness scans of first donors.** For each byte of the first donor in each lineage, test all 255 substitutions. Classify each as lethal, neutral or beneficial for certified copying. Compare 1-byte-LDIR donors with 2-byte-LDIR donors, and register-dependent donors with register-independent ones [V: Ofria et al. 2002; Lenski et al. 2003 abstract; Cicala et al. 2026 robustness hierarchy].

8. **Evolvability assay of certified donors.** Evolve monoclonal populations from each donor. Measure whether descendants acquire any new certified behaviour or length change. Flag sterile donors [V-abs: LaBar et al. 2015; V: C G 2017].

9. **Who inherits the state (Avida `EPIGENETIC_METHOD` analogue).** Arms: the victim/offspring starts with the donor's post-run registers; the donor keeps its own registers; both; neither. This isolates whether carried state helps as maternal provisioning (the offspring benefits) or hurts as self-poisoning (the parent suffers) [V: avida.cfg options; no published study found].

10. **Hijack test (Tierra hyper-parasite analogue).** Construct partners that deliberately set registers (HL, DE, BC) to point at themselves before the donor's LDIR executes. Measure whether carried state lets a non-copier get copied by a donor. That would make carried registers an exploitation channel, not only a poison [V: Ray 1991].

11. **Mutation-rate by genome-length sweep (error threshold).** Find the per-byte error rate above which certified lineages cannot persist, for 32, 64 and 96-byte genomes. Check the q^L·σ > 1 scaling. Look for "survival of the flattest" (robust but slow donors winning) [M: Eigen 1971; Wilke et al. 2001].

12. **Step-budget and metabolic penalty sweep.** Penalise executed steps. Test whether it selects for conditional halting, which would limit how much stale state a donor leaves behind [V: Cicala et al. 2026].

13. **A self-location primitive ("mem-size" analogue).** Add a 1-byte instruction that loads the executing genome's base address into a register. Compare with the 1-byte LDIR to see which primitive's accessibility is limiting. Motivation: Ofria et al. 2002 `mem-size` [V].

14. **Spatial structure and migration.** Grid niches with migration rate π in {0, 0.05, 0.5}. Test whether donor establishment improves with local structure [V: Cicala et al. 2026; V-abs: Hickinbotham et al. 2021].

15. **A neutral-shadow control for persistence.** Build a Bedau-style shadow population in which lineage persistence is drawn without regard to copying. Test whether certified-donor lineages persist beyond drift [M: Bedau et al. 1998].

---

## 4. (c) Prior results on "encoding accessibility of a primitive" and "state outside the genome"

### Encoding accessibility

- **Supports the idea that accessibility is first-order.**
  - Forth, with a dedicated COPY opcode that has a built-in +64 offset (a 1-byte trivial replicator), transitions in "almost all" runs within 1k epochs. BFF transitions in about 40% of runs within 16k epochs. SUBLEQ, whose minimal replicator is thousands of bytes, never transitions [V: 2024].
  - Tuned byte distributions accelerate BFF replicator discovery up to 25x relative to the soup and more relative to uniform sampling [V: Knierim 2026].
  - Emergence probability is exponential in the information required, and biased monomer (here, instruction) frequencies raise it exponentially [V-abs: Adami & LaBar 2015].
  - In Avida, the `mem-size` single instruction was adopted in 96/100 runs and made length change neutral [V: Ofria et al. 2002].
- **Complicates it.** In real-encoding Z80 soups, the 2-byte LDIR does emerge and eventually dominates, preceded by stack-based copiers [V: 2024; 2026]. Encoding length is therefore not a hard barrier on Z80 when resets supply addresses. More opcodes can slow evolution (the 84-instruction Avida set lagged) [V: Ofria et al. 2002].
- **Quantitative note [I].** Collapsing a specific 2-byte pair to one specific byte removes about 8 bits of required information. Under the Adami-style exponential model, the per-sample probability could rise by up to about 256x, if the donor needed exactly that one extra byte. NPE's 1% to 60% (run-level) is compatible with this after conversion to hazards. But the effect should be re-measured as a per-program rate (pitfall 6) and compared with the distribution-tuning control (experiment 3).

### State carried outside the genome

- **Blocking.**
  - Avida defaults reset the mother after divide (`DIVIDE_METHOD 1`) and disable register inheritance (`EPIGENETIC_METHOD 0`) [V]. This is a design choice consistent with inherited registers being harmful or unwanted, though the configuration file gives no rationale.
  - The Tierran ancestor recomputes its location and size every cycle [V: Ray 1991].
  - Wilke's maternal-effect model: parental effects shift the error threshold in small populations [V-abs].
  - Stringmol and Z80 energy work: interference from partners "can prevent reliable replication" [V-abs: Jha et al. 2026].
- **Enabling.**
  - Hyper-parasites replicate by leaving their own location and size in another program's registers [V: Ray 1991].
  - The 8080 "01 c5" replicator's first write depends on the initial BC=0 [V: 2024].
  - All emergent Z80 replicators exploit reset register values as free addresses [V: 2024; 2026].
  - Avida's `INHERIT_MERIT` transmits CPU-time allocation non-genetically by default [V].
- **Limit on how much such state can do.** Register state is a limited-heredity channel [V-abs: Szathmáry & Maynard Smith 1997]. Compositional or non-template inheritance showed "lack of evolvability" [V-abs: Vasas et al. 2010, 2012]. Carried registers can therefore make or break individual copying events, but cannot by themselves carry open-ended heritable information [I].

### Honest gaps

I found no published study that:
- (1) runs a program soup with CPU registers deliberately carried across interactions and measures its effect on emergence or establishment;
- (2) runs Avida with `EPIGENETIC_METHOD` 1-3 and reports results;
- (3) re-encodes a real ISA's block-copy opcode to test accessibility.

The absence of results in my searches does not prove none exist. If they do not, NPE's findings (1) and (2), once de-confounded by experiments 1 and 3, would be new.

---

## 5. Source list and verification status

| Source | URL | Status |
|---|---|---|
| Agüera y Arcas et al. 2024, Computational Life | https://arxiv.org/abs/2406.19108 | V (HTML) |
| Knierim et al. 2026, BFF: Simple explanations | https://arxiv.org/abs/2607.01483 | V (full PDF) |
| Cicala et al. 2026, Coevolution of self-replication and function (Z80) | https://arxiv.org/abs/2607.09211 | V (HTML) |
| Jha et al. 2026, Tapes Together Strong | https://arxiv.org/abs/2609.10817 | V-abs |
| Hintze & Bohm 2025, Rethinking Self-Replication | https://arxiv.org/abs/2508.08047 | V-abs |
| Cotler, Hongler, Hudcová 2025 | https://arxiv.org/abs/2510.08342 | V-abs |
| Yin 2026, Self-Replication Phase Diagram | https://arxiv.org/abs/2603.25239 | V-abs |
| C G, LaBar, Hintze, Adami 2017, Origin of life in a digital microcosm | https://arxiv.org/abs/1701.03993 | V (full PDF) |
| Adami & LaBar 2015, Biased typewriters | https://arxiv.org/abs/1506.06988 | V-abs |
| LaBar, Adami, Hintze 2015, Does self-replication imply evolvability? | https://arxiv.org/abs/1507.01903 | V-abs |
| LaBar & Adami 2016, small vs large populations | https://arxiv.org/abs/1604.06299 | V-abs |
| Ofria, Adami, Collier 2002, Design of evolvable computer languages | https://langev.com/pdf/ofria02ieee.pdf | V (full PDF) |
| Bryson & Ofria 2013, ISA evolutionary potential | https://arxiv.org/abs/1309.0719 | V-abs |
| Ofria & Wilke 2004, Avida platform | https://dl.acm.org/doi/10.1162/106454604773563612 | V-abs listing |
| Avida avida.cfg (DIVIDE_METHOD, EPIGENETIC_METHOD, INHERIT_MERIT) | https://raw.githubusercontent.com/devosoft/avida/master/avida-core/support/config/avida.cfg | V |
| Avida default ancestor tour | https://github.com/devosoft/avida/wiki/Default-Ancestor-Guided-Tour | V |
| Lenski, Ofria, Pennock, Adami 2003 | https://www.nature.com/articles/nature01568 | V-abs; counts M |
| Ray 1991, An approach to the synthesis of life | http://tomray.me/pubs/alife2/Ray1991AnApproachToTheSynthesisOfLife.pdf | V (LaTeX full text) |
| Rasmussen et al. 1990, Coreworld | https://doi.org/10.1016/0167-2789(90)90070-6 | V-abs; emergence details M |
| Pargellis 1996, Amoeba | https://dl.acm.org/doi/10.1016/0167-2789(96)00089-9 | search listing; 1e-4 figure M |
| Greenbaum & Pargellis 2017 | https://pubmed.ncbi.nlm.nih.gov/28786722 | V-abs |
| Chou & Reggia 1997 | https://www.sciencedirect.com/science/article/abs/pii/S0167278997001322 | V-abs |
| Sayama & Nehaniv 2024, 25 years after evoloops | https://arxiv.org/abs/2402.03961 | V (full PDF) |
| Salzberg & Sayama 2004 | https://philpapers.org/rec/SALCGE | V-abs |
| von Neumann 1966 (Burks ed.) | https://archive.org/details/theoryofselfrepr00vonn_0 | listing; content M |
| Langton 1984; Byl 1989; Codd 1968; Sayama 1999 | via refs in Sayama & Nehaniv 2024 | cited; content M |
| Wilke 2002, Maternal effects in molecular evolution | https://arxiv.org/abs/physics/0106093 | V-abs |
| Wilke et al. 2001, survival of the flattest | https://doi.org/10.1038/35085569 | M |
| Eigen 1971; Eigen & Schuster 1977 | https://doi.org/10.1007/BF00623322 ; https://doi.org/10.1007/BF00450633 | M |
| Kauffman 1986 | https://doi.org/10.1016/S0022-5193(86)80047-9 | M |
| Hordijk & Steel 2004; Hordijk, Steel, Kauffman 2012 | https://link.springer.com/article/10.1007/s10441-012-9165-1 | V-abs (2012); 2004 via search |
| Dittrich & Speroni di Fenizio 2007, COT | https://doi.org/10.1007/s11538-006-9130-8 | M |
| Hordijk, Steel, Dittrich 2018 | https://iopscience.iop.org/article/10.1088/1367-2630/aa9fcd | listing |
| Vasas, Szathmáry, Santos 2010 | https://www.pnas.org/doi/10.1073/pnas.0912628107 | V-abs via search |
| Vasas et al. 2012, Evolution before genes | https://link.springer.com/article/10.1186/1745-6150-7-1 | V-abs via search |
| Szathmáry & Maynard Smith 1997 | https://pubmed.ncbi.nlm.nih.gov/9299299/ | V-abs via search |
| Fontana & Buss 1994 | https://link.springer.com/article/10.1007/BF02458289 | listing; L0 via Mathis et al. |
| Mathis, Patel, Weimer, Forrest 2024, Return to AlChemy | https://arxiv.org/abs/2408.12137 | V-abs |
| Hickinbotham, Stepney, Hogeweg 2021, Stringmol parasites | https://royalsocietypublishing.org/rsos/article/8/8/210441/96415 | V-abs via search |
| Packard et al. 2019, OEE overview | https://doi.org/10.1162/artl_a_00291 | listing |
| Taylor 2015, Requirements for OEE | https://arxiv.org/abs/1507.07403 | V-abs |
| Bedau, Snyder, Packard 1998, activity statistics | (ALIFE VI proceedings; no URL opened) | M |
| Sarkar 2020 (quines); Moss 2023 (algebra of self-replication) | https://arxiv.org/abs/2010.09646 ; https://arxiv.org/abs/2309.09931 | listing only |
