# PA -- Origin of replication, copy primitives, heredity, error thresholds, lineage (Artemis, charter Block D)
- Domain: D2 (plus D1 H-D1-01, 08, 13, 14, 35, 47, 49, 50). Compiled 2026-09-27 by an Artemis prior-art worker. Read-only on the repo.
- Inputs read: roles/Artemis/backlog/harvest/D2_replication.md (all 52), D1_program.md (the 8 ids above), ops/threads/TH-001.md.
  Also read-only, to settle H-D2-01: roles/Bellerophon/prompts/2026-09-19_z80_atlas_campaign/00_OPERATOR_DIRECTIVE_verbatim.md (main),
  roles/Atlas/catalog/ECOSYSTEMS.jsonl rows 76-78 (main, commit 98972f55a, 2026-09-19), roles/Bellerophon/TOOLBOX_RESEARCH_2026-09-18.md:218.
- Verification: "VERIFIED" = title/authors/venue and the quoted claim checked on the source page (arXiv HTML or publisher/abstract page)
  on 2026-09-27. "BIBLIO-VERIFIED" = citation checked, specific claim from the reviewer's own knowledge. "UNVERIFIED" = not checked.

## 1. The internal questions

Three Z80-like byte-program worlds built on 2026-09-19 (Nestor NPE, Bellerophon BEE z80atlas, Archaeon z80atlas) all show
self-replicators arising from random tapes. The harvest asks whether that convergence is evidence of a law or of a shared design
(H-D2-01). It also asks whether every heredity result is really the result of a designer-supplied block-copy opcode such as
LDIR or COPY (H-D2-02, H-D2-08, H-D2-33, H-D2-34, H-D1-35, H-D1-47, H-D1-50). Other open questions:
- whether origins are a lottery or are built by other organisms (H-D2-06, -07, -25, -28, -43);
- whether replication is reproduction or only copying, and who the parent or author is (H-D2-05, -24, -37, H-D1-01, -08, -13, -49);
- whether conserved copy cores with eroding cargo are a law, and whether hidden effective mutation rates explain erosion
  (H-D2-04, -09, -17, -23, -45);
- whether the lineage, establishment and depth rulers measure heredity or instrument luck (H-D2-14, -18, -20, -21, -22, -31, -52, H-D1-14);
- whether host-mediated and context-dependent replication is a confound or the object of study (H-D2-10, -25, -29, -30).

## 2. Terminology map (Prometheus term -> literature term(s))

| Prometheus term | Literature term(s) |
|---|---|
| copier / self-replicator on random tapes | spontaneous emergence of self-replicators; "state transition" (Aguera y Arcas 2024); spontaneous generation (Pargellis) |
| LDIR / COPY / vmcopy32 primitive | block-copy instruction (Cicala 2026); h-copy (Avida); mov-iab (Tierra); '.'/',' head-copy (BFF); MOV (Core War / coreworld); templating reaction rules (Squirm3) |
| byte-loop copier (LDI / LD (T),A loop) | LDD-loop replicator (Cicala 2026); Load-Push / stack replicator (Aguera y Arcas 2024, Cicala 2026) |
| encoding accessibility / copier prior | density of replicators in program space; minimal replicator length (Aguera y Arcas s4, SUBLEQ); tuned byte distribution (Knierim 2026) |
| origin by construction vs lottery | self-modification / interaction-driven emergence vs random-walk discovery (Aguera y Arcas 2024 vs Knierim 2026) |
| host-mediated reproduction, context-dependent copier | scaffolded reproducer (Godfrey-Smith 2009); parasite / hyperparasite (Ray 1991; Hickinbotham et al. 2021); collective autocatalysis / organisation (Fontana & Buss; Dittrich COT) |
| "reproduction transmits capacity to reproduce" | reproducer vs replicator (Griesemer 2000; Szathmary & Maynard Smith 1997) |
| cargo erosion vs conserved copy core | error threshold (Eigen 1971); survival of the flattest (Wilke et al. 2001); mutation-selection balance / purifying selection |
| effective mutation (tape-write erosion) | effective per-site error rate; copying fidelity q |
| glin / anc / parent chain / material ids | phylogeny tracking, systematics manager; hereditary stratigraphy (Moreno et al.); tracer tokens (Aguera y Arcas 2024) |
| per-unit FLOW ancestry under recombination | ancestral recombination graph (ARG); tree-sequence / pedigree recording (Kelleher et al. 2018) |
| FLOW vs DIFFERENCE (B8) | identity by descent vs identity by state; production vs dependence causation (Hall 2004) |
| establishment | invasion / fixation probability; persistence; "take-over" of soup (Knierim 2026) |
| fixed interpreter (H-D1-47) | fixed vs evolvable genetic code / interpreter (Pargellis 2003 Amoeba codon map; Stringmol) |

## 3. Key works (16)

W1. Aguera y Arcas B, Alakuijala J, Evans J, Laurie B, Mordvintsev A, Niklasson E, Randazzo E, Versari L (2024).
"Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction." arXiv:2406.19108.
https://arxiv.org/abs/2406.19108 -- VERIFIED.
Relevance: this is DIRECT PRIOR ART for all three builds. Section 3.3 runs Z80 on "a 2D grid of 16-byte programs". Adjacent
pairs are "concatenated in random order", run for 256 steps, and addressed modulo 32 bytes. "Early generations use stack-based
copy mechanism" (the Z80 initialises SP at the end of the address space, so PUSH writes into the partner tape). These are then
"replaced with self-replicators that exploit 'LDIR' or 'LDDR'". In BFF, replicators arise even at zero background mutation.
SUBLEQ/RSUBLEQ4 soups never produce replicators, which is attributed to a longer minimal replicator (60 / 25 bytes).
SUPPORTS H-D2-08 (encoding length sets discoverability). CONTRADICTS the strong form of H-D2-02: in a real Z80 soup, heredity
first arises WITHOUT a block-copy opcode (PUSH). REFRAMES H-D2-01 (the three builds reimplement a published design).

W2. Cicala F, Niklasson E, Randazzo E, Boukortt S, Basti A, Etcheverry M, Saurous RA, Laurie B, Manyika J, Aguera-Arcas B,
Richards B (2026). "Coevolution of self-replication and function in a digital primordial soup." arXiv:2607.09211 (v1 10 Jul
2026, v2 2 Sep 2026). https://arxiv.org/abs/2607.09211 -- VERIFIED.
Relevance: THE design ancestor of the 2026-09-19 directive. It uses 32-byte Z80 programs, pairwise concatenation into 2L memory,
32 niches with "cross-niche pollination" (pi = 0.05), competence-gated interaction probability (p_succ 1.0 vs p_base 0.3), a
metabolic step cost, and polynomial tasks with no native multiply. There are three replicator families: Load-Push (uses the
whole tape), LDIR (a few bytes, "leaving the rest of memory free for task-solving code") and LDD loops. Robustness:
"LDIR >> LDD >> Load-Push". Ablation: with block copy absent, "we observe the consistent emergence of a different replication
mechanism based on the LDD instruction", but "only under task pressure; without it, the transition from Load-Push ... fails to
complete within ten million epochs". A hard-wired-copy control solves more hard tasks, while emergent replication keeps a higher
ancestor entropy.
SUPPORTS H-D2-01's worry (shared design prior; see s7). DIRECTLY ANSWERS the H-D2-02 question in one Z80 world: heredity without
block copy exists, via byte-loop and stack routes, but its success is task-pressure dependent. REFRAMES H-D2-04 / H-D2-45: the
compact LDIR core frees cargo space, and task coupling (not LDIR) is what pays for cargo. Compare BEE coupling v3.
Code availability: not stated (UNVERIFIED).

W3. Knierim C, Versari L, Obryk R, Aguera y Arcas B, Saurous RA (2026). "BFF: Simple explanations for complex phenomena."
arXiv:2607.01483. https://arxiv.org/abs/2607.01483 -- VERIFIED.
Relevance: a deflationary control. A mutation random walk finds BFF self-replicators about as easily as paired interaction:
~5e6 programs tested under BFF dynamics vs 2.9e7 by uniform sampling, and 9.4e4 under a tuned byte distribution. Capping the
ancestry tree does not stop emergence, "but rather prevents them from taking over the soup". It uses a noise-paired detector
(9 runs, score >= 48/64).
REFRAMES H-D2-07 and H-D2-06: origin rate is dominated by replicator density under the byte distribution; interaction mainly
affects take-over (establishment). SUPPORTS H-D2-08 (the byte distribution is an accessibility coordinate) and H-D2-21 (it
separates emergence from take-over).

W4. Ray TS (1991). "An approach to the synthesis of life." Artificial Life II, SFI Studies XI, 371-408.
http://life.ou.edu/pubs/alife2/ -- BIBLIO-VERIFIED (URL UNVERIFIED).
Relevance: in Tierra the ancestor is hand-written (a copy loop over mov-iab, plus mal/divide). Parasites that borrow a host's copy
loop and hyper-parasites arise within hours. This is the canonical precedent for host-mediated reproduction and for authored
replication.
SUPPORTS H-D2-29 (host dependence is the phenomenon) and H-D1-35 (every classic precedent authored its replicator).

W5. Ofria C, Wilke CO (2004). "Avida: a software platform for research in computational evolutionary biology." Artificial Life
10(2):191-229. Plus C G N, LaBar T, Hintze A, Adami C (2017). "Origin of life in a digital microcosm." Phil Trans R Soc A
375:20160350; arXiv:1701.03993. https://arxiv.org/abs/1701.03993 -- 2017 paper VERIFIED (abstract); the Avida paper is BIBLIO-VERIFIED.
Relevance: Avida replication requires the supplied h-alloc / h-copy / h-divide instructions. The 2017 study exhaustively enumerates
short random genomes for self-replicators and finds that progenitors "are clustered in a small region of the replicator space".
This is the best precedent for a census of copier priors over the whole genome space (Archaeon 9.6e-6 per tape). The exact
replicator frequencies are UNVERIFIED.
SUPPORTS H-D2-02 (all classic spontaneous-origin numbers are conditional on a supplied copy instruction) and H-D2-28 (which founders
win is non-random).

W6. Pargellis AN (1996). "The spontaneous generation of digital 'Life'." Physica D 91:86-96; Pargellis AN (2003). "Self-organizing
genetic codes and the emergence of digital life." Complexity 8(4); Greenbaum B, Pargellis AN (2017). "Self-Replicators Emerge from a
Self-Organizing Prebiotic Computer World." Artificial Life 23(3):318.
https://www.sciencedirect.com/science/article/abs/pii/0167278995002685 -- VERIFIED (abstract/biblio).
Relevance: this is Tierra-derived (Amoeba). Self-replicators emerge from random opcode sequences, and the probability depends on
sequence length. The 2003/2017 work makes the codon->opcode assignment itself self-organise, so the interpreter is not fixed.
SUPPORTS H-D2-08 (length sets the prior). It is the only precedent for H-D1-47 (a mutable interpreter) inside a spontaneous-origin
world.

W7. Rasmussen S, Knudsen C, Feldberg R, Hindsholm M (1990). "The coreworld: emergence and evolution of cooperative structures in a
computational chemistry." Physica D 42:111-134. https://doi.org/10.1016/0167-2789(90)90070-6 -- VERIFIED (abstract).
Relevance: a Core War (Redcode) chemistry with local resources and noise, with seven successive epochs of cooperative structures.
Redcode's MOV makes a one-instruction self-copier (the "Imp", MOV 0,1) trivially available. Whether the paper frames this as an
artifact is UNVERIFIED.
SUPPORTS the pitfall behind H-D2-02: a powerful copy primitive can make "replication" nearly trivial.

W8. Fontana W, Buss LW (1994). "What would be conserved if 'the tape were played twice'?" PNAS 91:757-761; and "The arrival of the
fittest" (Bull Math Biol 1994). Revisited: Mathis C, Patel D, Weimer W, Forrest S (2024). "Self-Organization in Computation &
Chemistry: Return to AlChemy." arXiv:2408.12137. https://arxiv.org/abs/2408.12137 -- 2024 paper VERIFIED; the 1994 papers are BIBLIO-VERIFIED.
Relevance: in lambda-calculus AlChemy, copying functions (Level 0) dominate unless copiers are disallowed. With copying removed,
self-maintaining ORGANISATIONS appear (Level 1/2): heredity without a copy primitive, as collective closure. The 2024 revisit finds
such organisations arise "more frequently than previously expected" but are hard to combine hierarchically.
REFRAMES H-D2-02 and H-D1-49: removing the copy primitive does not remove heritable persistence, but it moves it from individuals to
organisations, which parent-child rulers cannot see. The copier-dominance mechanism is BIBLIO-VERIFIED (standard reading of
Fontana & Buss).

W9. Hutton TJ (2002). "Evolvable self-replicating molecules in an artificial chemistry." Artificial Life 8(4):341-356. Hutton TJ
(2007). "Evolvable self-reproducing cells in a two-dimensional artificial chemistry." Artificial Life 13(1):11-30.
https://direct.mit.edu/artl/article/8/4/341/2413 -- VERIFIED (abstract).
Relevance: Squirm3 replicators "emerge spontaneously from a random soup given the right conditions". However, the templating is
built into the designed reaction rules, so the copy mechanism is in the physics, not in the molecule.
SUPPORTS H-D2-02 (it is a clean example of a supplied copy mechanism being called emergence) and H-D1-50.

W10. Hickinbotham SJ, Stepney S, Hogeweg P (2021). "Nothing in evolution makes sense except in the light of parasitism: evolution
of complex replication strategies." Royal Society Open Science 8:210441 (bioRxiv 2021.02.25.432891).
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8334846/ -- VERIFIED (title/venue). NOTE: the operator's recalled title "... in the
light of" and "BioEssays" are wrong; the paper is "parasitism", RSOS.
Relevance: in Stringmol (automata chemistry) plus a spatial RNA-world model, parasitism drives complex replicators and ecosystems.
Replicases are seeded, not spontaneous, and Stringmol provides a symbol-copy opcode; both of these are BIBLIO-VERIFIED only.
SUPPORTS H-D2-29 and H-D2-25 (context-dependent / parasitic copying is the engine of complexity, not noise). REFRAMES H-D2-46
(partner-code executors as a parasite class).

W11. Kruszewski G, Mikolov T (2022). "Emergence of self-reproducing metabolisms as recursive algorithms in an Artificial Chemistry."
Artificial Life 27(3-4):277; arXiv:2103.08245. https://arxiv.org/abs/2103.08245 -- VERIFIED (abstract).
Relevance: a combinatory-logic chemistry with conservation laws. From a tabula rasa it produces structures "that self-reproduce in
each cycle", with no copy primitive at all. Reproduction arises as autocatalytic recursive rewriting.
CONTRADICTS the generality of H-D2-02 (self-reproduction without a supplied copy op exists). It is a candidate NON-Z80 substrate for
H-D2-01.

W12. Cotler J, Hongler C, Hudcova B (2025). "Self-replication and Computational Universality." arXiv:2510.08342.
https://arxiv.org/abs/2510.08342 -- VERIFIED (abstract).
Relevance: it constructs a Turing-universal cellular automaton that "cannot sustain non-trivial self-replication". Universality
(or having copy-capable instructions) does not imply replicability. This dates back to von Neumann (1966, "Theory of
Self-Reproducing Automata", ed. Burks) and is surveyed by Sipper (1998, "Fifty years of research on self-replication: an
overview", Artificial Life 4(3):237-257; https://fab.cba.mit.edu/classes/865.18/replication/Sipper.pdf, BIBLIO-VERIFIED).
REFRAMES H-D2-02 and H-D1-35: the right question is not "was a copy op present" but "what does the substrate make replication
cost". Von Neumann's split between constructor and description (copied uninterpreted) maps onto copy core vs cargo (H-D2-04).

W13. Eigen M (1971). "Selforganization of matter and the evolution of biological macromolecules." Naturwissenschaften 58:465-523.
Wilke CO, Wang JL, Ofria C, Lenski RE, Adami C (2001). "Evolution of digital organisms at high mutation rates leads to survival of
the flattest." Nature 412:331-333. https://www.nature.com/articles/35085569 -- Wilke is VERIFIED; Eigen is BIBLIO-VERIFIED.
Relevance: maximal maintainable information L_max ~ ln(sigma)/mu per site. At NPE's effective ~5%/byte/epoch, with superiority
sigma in 2-10, L_max is ~14-46 bytes. This holds only if an epoch is ~ a generation, which is UNVERIFIED for NPE. On that
estimate a few-byte LDIR core sits under threshold while 32-64 byte cargo does not. At high mutation, robust (flat) genotypes beat
fast ones in Avida.
SUPPORTS H-D2-04 (core conserved, cargo eroded is the expected error-threshold outcome, not a new law) and H-D2-09 (thresholds
must use effective, not nominal, rates). REFRAMES H-D2-17: "junk" bytes may buy flatness.

W14. Griesemer J (2000). "The units of evolutionary transition." Selection 1:67-80. Szathmary E, Maynard Smith J (1997). "From
replicators to reproducers: the first major transitions leading to life." J Theor Biol 187:555-571. Godfrey-Smith P (2009).
"Darwinian Populations and Natural Selection." OUP. -- Griesemer is BIBLIO-VERIFIED (via SEP "Units and Levels of Selection");
the other two are BIBLIO-VERIFIED from knowledge.
Relevance: a reproducer requires material overlap AND transmission of the capacity to reproduce (a developmental criterion).
Godfrey-Smith separates simple, collective and SCAFFOLDED reproducers (reproduction done by external machinery, e.g. viruses), and
treats paradigm vs marginal Darwinian populations by degrees.
SUPPORTS H-D2-05 / H-D1-13 (a per-birth capacity field). REFRAMES H-D2-25 / H-D2-29 (host-mediated = scaffolded, a recognised
marginal category, not a defect) and H-D1-01 (the separation of carriers is expected: the literature already splits replicator
/ interactor / reproducer).

W15. Moreno MA, Dolson E, Ofria C (2022). "Hereditary Stratigraphy: Genome Annotations to Enable Phylogenetic Inference over
Distributed Populations." ALIFE 2022; hstrat, JOSS 7(80):4866. https://direct.mit.edu/isal/proceedings/isal2022/34/64/112297 ;
https://github.com/mmore500/hstrat -- VERIFIED (title/venue/repo).
Relevance: it gives tunable-cost inheritable annotations that reconstruct phylogeny without central tracking. The recombination
extension ("Methods for rich phylogenetic inference over distributed sexual populations") gives gene-tree-like inference.
SUPPORTS H-D2-18 (reuse, don't invent) and H-D2-20 / TH-006 (it removes full-replay dependence). Caveat: it tracks LABEL descent
(FLOW), not content (H-D2-37).

W16. Lewanski AL, Grundler MC, Bradburd GS (2024). "The era of the ARG: An introduction to ancestral recombination graphs and their
significance in empirical evolutionary genomics." PLoS Genetics 20(1):e1011110. Kelleher J, Thornton KR, Ashander J, Ralph PL
(2018). "Efficient pedigree recording for fast population genetics simulation." PLoS Comp Biol 14(11):e1006581.
https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1011110 -- Lewanski is VERIFIED; Kelleher is BIBLIO-VERIFIED.
Relevance: under recombination, ancestry is "a complex, interwoven collection of genealogies", not a singular parent. Forward
simulations record per-interval edges (a tree sequence) cheaply and simplify them on the fly.
SUPPORTS H-D2-14 (per-unit ancestry is the accepted convention). REFRAMES H-D2-15 (the "which parent" question is ill-posed; report
per-byte-interval parentage).

Also relevant (not counted; verification as marked): Koza JR (1994) "Spontaneous emergence of self-replicating and evolutionarily
self-improving computer programs", Artificial Life III 225-262 (BIBLIO-VERIFIED). Its "ooze" of agglomerating elements already
supplied self-replication as a template-matching step. Dittrich P, Speroni di Fenizio P (2007) "Chemical organization theory",
Bull Math Biol 69:1199-1231 (BIBLIO-VERIFIED): closed + self-maintaining sets as the unit of persistence (H-D1-49). Sayama H,
Nehaniv CL (2024/2025) "Self-reproduction and evolution in cellular automata: 25 years after evoloops", Artificial Life (VERIFIED
via search snippet only). Taylor T et al. (2016) "Open-ended evolution: perspectives from the OEE workshop in York", Artificial Life
22(3):408-423 (BIBLIO-VERIFIED). The operator-named "Taylor, Evolution in artificial life: open-endedness" is UNVERIFIED as a title.
"Mulzer / Sayama" on self-replication: NOT FOUND; treat it as UNVERIFIED / possibly misremembered.

## 4. Prior failures / known pitfalls

P1. Emergence claims that are instruction-set artefacts. SUBLEQ soups produce nothing (W1), while Z80 and BFF produce replicators in
~1e4-1e6 samples. Redcode's MOV 0,1 is a one-instruction replicator (W7). Squirm3 templating lives in the reaction rules (W9).
"Replicators emerged" is always conditional on the minimal replicator length the ISA affords. All three Prometheus builds were
instructed to include "native VM organisms with explicit executable copy primitives" and "copy/memory-write capability"
(directive, main).
P2. A missing ISA route mistaken for impossibility. Real Z80 memory with SP at the top of a 2L-byte modulo space gives a PUSH copier
for free (W1, W2). BEE's finding that replication is "reachable ONLY through LDIR plus the neutral undefined-byte slide" may instead
reflect SP semantics, an ISA subset, or address wrapping in BEE's VM. That is an implementation fact, not a law.
P3. Interaction vs mutation credit. Knierim et al. (W3) show that a headline mechanism (self-modification through interaction) was
not needed for emergence, only for take-over. Prometheus analogue: H-D2-07 lottery vs construction may be the same two-stage
confusion.
P4. Detector fragility. Byte-pattern detectors (Cicala counts tapes containing ED B0) flag non-replicators. Pair-with-noise
detectors (W3) miss context-dependent copiers (H-D2-25). Isolated-tape censuses miss scaffolded reproducers (Godfrey-Smith).
P5. Knockouts rescued by re-creation. W2 finds that removing block copy leads to LDD loops re-evolving. BEE P8 found that NOPing
the copy byte is rescued at a new position (H-D2-44). The literature ablates at the ISA level, not the byte level.
P6. Error thresholds computed on nominal rates. Wilke et al. and Eigen work on per-copy fidelity. Hidden write-back or overwrite
channels raise the effective rate (H-D2-09).
P7. Label descent vs content. Tierra/Avida genealogies and hstrat track labels. After overwrite-dominated dynamics, founder content
can be a minority (NPE 13-25%). The literature separates IBD from IBS; Prometheus rulers mix them (H-D2-37, H-D1-08).
P8. Hard-wired vs emergent reproduction trade-off. W2 shows that hard-wired copy solves more tasks but explores fewer ancestral
routes. Comparisons of EXTERNAL vs ENDOGENOUS arms that ignore this confound yield with path diversity (H-D2-41).

## 5. Existing code / systems usable

| system | URL | licence | use for |
|---|---|---|---|
| cubff (BFF, Forth, SUBLEQ soups; official) | https://github.com/paradigms-of-intelligence/cubff | Apache-2.0 (VERIFIED via GitHub API) | non-Z80 fourth substrate; SUBLEQ negative control; tracer-token lineage |
| zff (8-bit Z80/8080 substrates, Mordvintsev) | https://github.com/znah/zff | MIT (VERIFIED) | reference Z80 soup to run through Prometheus rulers (H-D2-01); PUSH-route check (H-D2-02) |
| Cicala et al. 2026 Z80 coevolution code | not found | UNVERIFIED | closest design; ask the authors if needed |
| gustavsoderstrom/computational-life (pure Python BFF) | https://github.com/gustavsoderstrom/computational-life | UNVERIFIED | cheap CPU BFF reference |
| hstrat | https://github.com/mmore500/hstrat | GitHub reports NOASSERTION (repo states MIT; UNVERIFIED) | H-D2-18 per-birth ancestry |
| phylotrackpy / Empirical systematics | https://github.com/emp-devosoft or devosoft org (UNVERIFIED path) | MIT (UNVERIFIED) | phylogeny tracking with taxon pruning |
| tskit (tree sequences / ARG) | https://github.com/tskit-dev/tskit | MIT (VERIFIED) | per-byte-interval FLOW ancestry (H-D2-14, -37) |
| Avida | https://github.com/devosoft/avida | UNVERIFIED (GitHub API returned none) | h-copy-free ablation precedent |
| Stringmol, Squirm3 | UNVERIFIED URLs (listed as verified in roles/Atlas/proposals/2026-09-21_prior_art_raid) | UNVERIFIED | H-D1-47 mutable interpreter; templating comparison |

## 6. What is genuinely unexplored given the literature (most valuable)

U1. Heredity reachability per ISA route, with ISA-level (not byte-level) ablations, mapped across routes: block copy, byte loop,
stack PUSH, and pairwise write-back. The route is the unit (P5). W2 did one ablation in one world (block copy off -> LDD, which
needs task pressure). Nobody has measured time-to-first-replicator AND time-to-take-over for each route on the same substrate,
with and without task coupling. Three Prometheus engines with different VMs are well placed to do this.
U2. Error-threshold accounting on EFFECTIVE rates in soups with write-back. The soup papers (W1-W3) do not compute Eigen thresholds.
The Avida work (W13) uses clean per-copy rates. A per-position effective-rate x superiority estimate predicting which bytes are
conserved would test H-D2-04 / -23 non-circularly. That test is not in the literature.
U3. Per-birth capacity transmission (reproducer criterion, W14) measured at scale in a program soup. Philosophy defines it, and
W1-W3 detect replicators but do not ask whether each birth yields a fertile child. NPE X-STERILE (75-80% fertile) is already beyond
the literature.
U4. Material (FLOW) vs executor (WHO) vs governing-code (WHAT) attribution of births. The soup literature attributes to "the
program" with tracer tokens (W1) or niche labels (W2), and never separates executor from author. B6 / FF-27 (847k BEE out-of-position
births) has no precedent. This is novel, provided it survives the population-wide sample (H-D2-52).
U5. Carried execution state as a heredity channel (H-D2-10). W1 and W2 reset the emulator per interaction, which by design removes
it. No precedent was found (UNVERIFIED beyond W1-W3).
U6. Context-dependent (scaffolded) origin fraction. Godfrey-Smith names the category. No soup paper reports the fraction of first
replicators that copy only in company (BEE 16%). H-D2-25 would be a first quantitative measurement.
U7. Per-byte-interval ancestry (tskit-style) inside an overwrite-dominated byte soup, giving IBD vs IBS per site. The genetics
methods exist (W16), and no ALife soup uses them.
U8. Collective / organisational heredity detectors run on the same logs as parent-child detectors (H-D1-49). COT and AlChemy (W8)
define the object, and no one has applied both detectors to one program-soup log.

## 7. Cheapest discriminating tests

H-D2-01 (are the three Z80 builds independent?). The literature and the repo answer this largely in the negative, before any run:
- T1 (DONE here, archival, 0 CPU). The single operator directive of 2026-09-19 is a paraphrase of W2. It cites "Digital
  primordial-soup machinery", "the Z80 experiment", "the paper's phenomena", 32-byte bytecode, "competence-gated interaction
  probability", "cross-niche pollination", "no privileged multiplication", "explicit executable copy primitives" and
  "copy/memory-write capability". Atlas catalogued W2 on 2026-09-19 (commit 98972f55a, row bff-z80-coevolution), and Bellerophon
  surveyed W1 on 2026-09-18.
  Verdict: the builds share one external design ancestor and one directive, and they come from one model family.
  "Independent" holds at most at the implementation level. Block D's "design law" should be restated as "three implementations
  of one published design recover that design's phenomena". H-D2-01 status: largely ANSWERED (common cause established). The
  residual question is which details differ between the three VMs.
- T2 (~1 CPU-hour). Run the MIT-licensed zff Z80 soup (or a faithful W1 s3.3 reimplementation) through each Prometheus
  replicator ruler unchanged. If the rulers read zff the same way they read their own engines, convergence is about the design,
  not about the builders.
- T3 (days). Run a deliberately dissimilar substrate with the same rulers: cubff SUBLEQ (expected negative control: no
  replicators), then combinator chemistry (W11, no copy op). A result that recurs there is a candidate law; one that is absent
  there is Z80-design-bound.
- T4 (0 CPU). Build a design-factor diff table (SP init, address wrap, ISA subset, tape size, pairing, copy opcode encoding) for
  BEE / NPE / Archaeon / W1 / W2. Every shared factor is a common cause.

H-D2-02 (is every result a supplied-copy-primitive result?):
- T5 (cheapest, per engine, ~1 CPU-hour each). Is the PUSH route present? Check whether each VM gives SP a default at the top of
  a modulo-2L space so that PUSH writes into the partner. W1/W2 get Load-Push replicators first on real Z80. If BEE/NPE/Archaeon
  never see Load-Push, the "LDIR-only" result is a VM implementation choice (P2). Test: seed a hand-written Load-Push replicator
  (the W2 family [01 C5]-style pairs). Does it replicate in each engine? A yes/no answer per engine discriminates immediately.
- T6 (W2 protocol). ISA-level ablation: remove LDIR/LDDR/LDI (and Archaeon COPY) from the decoder entirely, not by NOPing bytes.
  Run random-tape soups with and without task coupling, and measure time to first byte-loop / stack replicator and to take-over.
  Prediction from W2: LDD-type loops appear, but take over only under task pressure. If Prometheus engines produce zero under both
  conditions, their heredity is primitive-bound, and the operator's worry holds for them specifically.
- T7 (analysis only). Compute the minimal replicator length per route per ISA (W1 s4 logic) and regress the observed copier prior
  on it across engines (H-D2-08). One regression tests "discoverability is set by encoding length" across all three plus W1.

Other cheap tests suggested by the literature:
- H-D2-04 / -09 / -23. Estimate the effective per-byte error rate (including write-back) and superiority sigma. Predict L_max
  (Eigen) and compare it with conserved-core length. Separately, apply single-byte knockouts in isolation (W13 method) to predict
  conservation before looking. This is archival plus about 1 CPU-hour.
- H-D2-07 / -06. Apply the Knierim split (W3): for each engine, estimate replicator density by random sampling of isolated tapes
  vs first-appearance time in the interacting world. If sampling matches the world rate, origin is a lottery and interaction
  matters for establishment only.
- H-D2-05 / H-D1-13. Add a per-birth fertility bit (child placed alone in a fresh partner context: does it produce a grandchild?).
  This is Griesemer's criterion operationalised, at the cost of one extra execution per birth.
- H-D2-14 / -37 / -18. Record tskit edges (parent, child, byte interval) at each write in one short BEE and one NPE run. Compare
  the label-descent depth with IBD-at-informative-sites depth.
