# PRIOR ART B: Library Learning, Abstraction Discovery, Program Synthesis, GP / Autoconstructive Evolution, Algorithm Discovery

Seat: Aphrodite (science of recursive self-improvement)
Compiled: 2026-09-27 by external literature raid (WebSearch/WebFetch + full-text PDF reads where noted)
Scope: cluster B. Plain ASCII.

Verification legend:
- [FT]  = claim checked against the primary full text (PDF downloaded and read/grepped this session).
- [ABS] = checked against the primary abstract / publisher page / official repo only.
- [SEC] = checked only through a secondary source (search snippet, citing paper, index page).
- UNVERIFIED = not confirmed from any primary source this session; treat as recollection.
No citation below was invented; where only the existence of a work was confirmed, the specific numeric
claims are marked accordingly.

---------------------------------------------------------------------------------------------------

## 0. One-paragraph bottom line

Library learning systems that are claimed to "compound" (DreamCoder, EC, Stitch-iterated, LILO) show
abstraction-on-abstraction only qualitatively (named chains such as filter -> max -> nth-largest -> sort)
and correlationally (library depth vs tasks solved, r = 0.79 in DreamCoder). No work found runs the
controlled causal test Aphrodite ran: take an abstraction G1, give it to one learner and withhold it
from another, and check whether a new, non-derivative G2 becomes reachable only with G1. Every positive
case relies on an externally supplied, human-curated, graded task set with "stepping stone" tasks
whose solutions share the composite structure. The one controlled task-supply experiment (Dechter et
al. 2013, EC) shows learning dropping sharply and then to zero as the easy tasks are removed. Aphrodite's
negative recursion result (mul/mod/pow strata 0/32; G1 re-derived) is what that literature predicts for
a task supply with no stepping stones into the new operator strata. So the result is uninterpretable
as evidence about the mechanism until a positive control exists. Separately, single-hole body-only
LGG is weaker than standard practice. Plotkin LGG is already multi-variable, Stitch uses arity up to 3,
DreamCoder uses arbitrary lambda abstraction, and babble works modulo an equational theory. Aphrodite's
semantic classing is a known idea (observational equivalence, 2013; LLMT/e-graphs, 2023). Its
whole-program lift across (init, body, final) handles a case that local equational rewriting does not:
the E4 "compensating factorisation". That lift may be a genuine, narrow contribution.

---------------------------------------------------------------------------------------------------

## 1. Per-work entries

Field key for each entry:
- IMPROVED: what got better
- FIXED: what was held fixed
- SELF-APPLICABLE?: whether the improvement mechanism could improve itself, or only its products
- TASK SUPPLY: external or endogenous
- REPRESENTATION: new primitives or only reweighting
- NOVELTY CHECK: whether novelty was real or reuse, and how that was checked
- COMPOUNDING: how compounding/recursion was measured
- FAILURE MODES
- CODE: URL

### 1.1 EC: Exploration-Compression (Dechter, Malmaud, Adams, Tenenbaum, IJCAI 2013) [FT]
"Bootstrap learning via modular concept discovery." https://www.ijcai.org/Proceedings/13/Papers/196.pdf
- IMPROVED: A stochastic grammar over typed combinator programs. Each iteration enumerates a frontier
  of N most-probable programs, picks solutions for the tasks it hits so that the solution set is
  maximally compressible, and re-estimates the grammar, adding reused subtrees as new primitives.
- FIXED: Enumeration procedure, compression criterion, task set, frontier size, 15 iterations.
- SELF-APPLICABLE?: No. Only the grammar (product) changes. The compression mechanism is fixed.
- TASK SUPPLY: External and fixed (e.g., all polynomials of degree <= 2 with coefficients 0..9;
  Boolean functions).
- REPRESENTATION: Expands. New composite primitives are added to the grammar, and weights are re-estimated.
- NOVELTY CHECK: None formal. Tasks solved vs a matched-enumeration baseline (150000 expressions from the
  initial grammar hit about 3% of tasks; EC nears 100% at frontier 10000).
- COMPOUNDING: Not measured directly. There is qualitative inspection of learned combinators.
- KEY RESULT FOR APHRODITE (task-supply ablation, Sec. 4.1, Fig. 3) [FT]: The authors explicitly
  hypothesise that "the set must contain a 'learnable' curriculum, a set of tasks that serve as stepping
  stones". Removing the constant tasks alone, or the linear tasks alone, did not hurt. Removing both
  ("only quadratics") gave "a sharp drop". Restricting to "complex" quadratics (all coefficients > 0)
  gave "another comparable drop". Restricting to quadratics with coefficients > 1 gave performance 0
  "because no task is hit in the initial frontier". Conclusion quoted: "a minimal curriculum of simple
  tasks is sufficient ... [but] this is not an all-or-none effect."
- FAILURE MODES: Total failure when no task is hit by the initial frontier. The seed of the bootstrap
  must come from tasks solvable in the base language.
- CODE: None found for the 2013 system. The successor code base is ellisk42/ec (see 1.3).

### 1.2 EC2 (Ellis, Morales, Sable-Meyer, Solar-Lezama, Tenenbaum, NeurIPS 2018) [ABS]
"Learning Libraries of Subroutines for Neurally-Guided Bayesian Program Induction."
https://proceedings.neurips.cc/paper/2018/hash/7aa685b3b1dc1d6780bf36f7340078c9-Abstract.html
- Explore/Compress/Compile. This is the source of DreamCoder's list-processing task set: DreamCoder's
  "218 problems taken from (17)", where ref 17 = this paper [FT, DreamCoder ref list].
- Domains: lists, text editing, symbolic regression. It is a precursor to 1.3, and its entry fields are as for 1.3.

### 1.3 DreamCoder (Ellis, Wong, Nye, Sable-Meyer, Cary, Morales, Hewitt, Solar-Lezama, Tenenbaum) [FT]
arXiv 2006.08381 (2020): https://arxiv.org/abs/2006.08381
PLDI 2021 ("DreamCoder: bootstrapping inductive program synthesis with wake-sleep library learning") [SEC].
Phil. Trans. R. Soc. A 381:20220050 (2023) [SEC]:
https://royalsocietypublishing.org/rsta/article/381/2251/20220050/112456/
- IMPROVED: (i) A library of lambda-calculus abstractions (the "abstraction sleep" phase), found by
  refactoring wake-phase solutions via version spaces and compressing under an MDL/Bayesian objective.
  (ii) A neural recognition model trained on replays and "dreams" (the "dreaming sleep" phase).
- FIXED: The refactoring/compression algorithm (refactorings bounded to 3 lambda-calculus evaluation
  steps [FT]), the base DSL per domain, the task sets, and the search algorithm (enumeration in probability order).
- SELF-APPLICABLE?: No. Library and recognition network are products. The compression procedure is fixed.
- TASK SUPPLY: External, human-curated, fixed per domain. Tasks are "random samples" of that fixed set,
  cycled over iterations. The authors distinguish this from a teacher-ordered curriculum [FT]: "Instead
  of solving increasingly difficult tasks ordered by a human teacher ... It attempts to solve random
  samples of tasks, searching out to the boundary of its abilities during waking, and then pushing that
  boundary outward." They also note it needs "sufficiently varied training tasks" [FT]. They name
  self-generated tasks as "an important next step" [FT]. So the task set is externally graded in
  content even though it is not ordered.
- REPRESENTATION: Expands. New named library functions with arbitrary arity, including higher-order
  functions (fold, unfold, map, filter rediscovered).
- NOVELTY CHECK: Held-out test tasks. Ablations remove the recognition model or library learning, and
  baselines include EC (no refactoring), memorization, and others. "Novelty" of abstractions is
  checked only by inspection.
- COMPOUNDING [FT]: (a) Qualitative chains. In the list domain "the model first learns filter, then
  uses it to learn to take the maximum element of a list, then uses that routine to learn ... the nth
  largest element ..., which it finally uses to sort lists". "Sort" is solved "by invoking a library
  component four layers deep". Physics: vector-algebra building blocks come first, then the inverse-square
  schema reused for Newton and Coulomb. 1959-Lisp start: fold first, then unfold, then map/filter as
  variations ("origami programming"). (b) Correlational. "Across domains, deeper libraries correlate
  well with solving more tasks (r = 0.79)", and the recognition model "leads to deeper libraries".
  (c) Not done: no ablation that removes a specific early abstraction to test whether a later one
  becomes unreachable. A targeted search found none (Section 2a).
- MECHANISTIC NOTE [FT, footnote]: "the difficulty of search during waking is roughly proportional to
  breadth^depth ... Library learning decreases depth at the expense of breadth, while training a
  neural recognition model effectively decreases breadth." Every added library entry has a breadth
  cost. The recognition model is what pays it down.
- FAILURE MODES: Heavy compute (about a day on 20-100 CPUs per domain; five days on 64 CPUs for the
  Lisp-from-scratch run [FT]). The compression phase is expensive (motivating Stitch). Limited
  refactoring depth.
- CODE: https://github.com/ellisk42/ec [ABS]

### 1.4 Stitch (Bowers, Olausson, Wong, Grand, Tenenbaum, Ellis, Solar-Lezama; POPL 2023) [FT]
"Top-Down Synthesis for Library Learning." https://arxiv.org/abs/2211.16605 ; PACMPL 7 POPL Art. 41.
- IMPROVED: Speed and scalability of the compression step. The paper reports it as "3-4 orders of
  magnitude faster and uses 2 orders of magnitude less memory" than DreamCoder's compressor with
  comparable or better compressivity [ABS].
- FIXED: Corpus of programs (static ground-truth corpora in the paper), utility = compression. Maximum
  arity is a user parameter; arity 3 was used in most experiments [FT].
- SELF-APPLICABLE?: No.
- TASK SUPPLY: The input is a corpus, not tasks. It is external.
- REPRESENTATION: Expands the DSL with lambda abstractions that have multiple arguments (up to the
  arity limit) and multi-use variables.
- NOVELTY CHECK: Compression measured against DreamCoder abstractions on DreamCoder corpora.
- COMPOUNDING [FT]: One abstraction per iteration. After each, the whole corpus is rewritten, so
  "Successive iterations therefore yield abstractions that build hierarchically on one another"
  (Fig. 3, nuts-bolts). This is qualitative only.
- LIMITATIONS [FT]: Purely syntactic matching: "Stitch only explores" syntactic structure, unlike babble.
  It "cannot learn higher-order abstractions" without the version-space extension (Sec 6.5), and loses
  to DreamCoder on the list domain for that reason.
- CODE: https://github.com/mlb2251/stitch ; benchmarks https://github.com/mlb2251/compression_benchmark [FT]

### 1.5 babble / LLMT (Cao, Kunkel, Nandi, Willsey, Tatlock, Polikarpova; POPL 2023) [FT]
"babble: Learning Better Abstractions with E-Graphs and Anti-Unification." https://arxiv.org/abs/2212.04596
- IMPROVED: Library learning becomes robust to syntactic variation. "Library learning modulo
  (equational) theory": equality saturation builds an e-graph of the corpus modulo user-given
  rewrite rules, then e-graph anti-unification is run over pairs of e-classes to find candidate patterns.
- FIXED: The equational theory (supplied by a human per domain), the corpus, and the compression objective.
- SELF-APPLICABLE?: No.
- TASK SUPPLY: Corpus supplied externally (DreamCoder compression benchmarks; 2D CAD corpora of Wong et al. 2022).
- REPRESENTATION: Expands with multi-variable patterns abstracted into functions.
- NOVELTY CHECK: Compression vs DreamCoder, plus a qualitative evaluation.
- KEY DESIGN POINTS [FT]: Candidates are restricted to "the most concrete patterns that match some
  pair of subterms". The paper admits "this can in theory eliminate optimal patterns". The motivating
  failure is that prior work "is not robust to syntactic variation in the input". This is the same
  failure Aphrodite found in E4.
- CODE: https://github.com/dcao/babble (POPL23 tag) [ABS]

### 1.6 LILO (Grand, Wong, Bowers, Olausson, Liu, Tenenbaum, Andreas; ICLR 2024) [FT]
"LILO: Learning Interpretable Libraries by Compressing and Documenting Code." https://arxiv.org/abs/2310.19791
- IMPROVED: Solve rate on REGEX, CLEVR and LOGO by combining an LLM-guided search with enumerative
  search ("dual system"), Stitch compression, and AutoDoc (LLM-written names and docstrings).
- FIXED: The LLM (gpt-3.5-turbo for AutoDoc; Codex-family for synthesis), Stitch settings
  (iterations = 10 caps library size; arity limit), and the task sets.
- SELF-APPLICABLE?: No.
- TASK SUPPLY: External, with language annotations. Batches of 96 tasks per iteration.
- REPRESENTATION: Expands (Stitch lambda abstractions).
- NOVELTY CHECK: The "offline synthesis" test [FT]. The final library L_f is frozen and plain enumerative search
  runs with no language. L_f improves on the base DSL by +42 to +63 points across domains, and more than
  DreamCoder's L_f does. This is a clean library-quality test that separates the library from the
  learner that built it.
- COMPOUNDING / INHERITANCE [FT]: "we re-derive the entire library from L0 at every iteration ... this
  'deep refactoring' allows LILO to discard suboptimal abstractions discovered early in learning."
  So LILO does NOT stack abstractions by inheritance. It recomputes from primitives, and the hierarchy
  arises inside each Stitch run.
- FAILURE MODES [FT]: Giving the LLM raw Stitch abstractions without documentation HURT, by
  -30.60 (REGEX), -2.91 (CLEVR) and -11.11 (LOGO) points. The consumer did not use the abstractions.
  Semantic errors in AutoDoc also occurred.
- CODE: https://github.com/gabegrand/lilo [FT]

### 1.7 ReGAL (Stengel-Eskin, Prasad, Bansal; ICML 2024) [FT]
"ReGAL: Refactoring Programs to Discover Generalizable Abstractions." https://arxiv.org/abs/2401.16467
- IMPROVED: Accuracy of LLM program prediction when given a learned "Code Bank" of helper functions.
  Evaluated on LOGO, Date, TextCraft, MATH and TabMWP.
- FIXED: Refactoring LLM, agent LLM, and the training programs (about 200 examples).
- SELF-APPLICABLE?: No.
- TASK SUPPLY: External. Examples are sorted into a curriculum by query length [FT].
- REPRESENTATION: Expands (Python helper functions), with verification by execution, editing, and
  pruning of helpers that fail.
- NOVELTY CHECK: Unit-test verification of refactorings. Pruning is based on the success rate of
  programs that use each helper.
- CURRICULUM ABLATION [FT, Table 3, CodeLlama-13B dev]: Removing the curriculum (random shuffle of
  clusters) dropped LOGO from 55.0 to 36.3, Date from 77.0 to 56.6, and TextCraft from 34.12 to 28.78. The
  text states "an 18.7% drop on LOGO".
- CODE: https://github.com/esteng/regal_program_learning [ABS]

### 1.8 LEGO-Prover (Wang et al.; ICLR 2024 oral) [ABS]
"LEGO-Prover: Neural Theorem Proving with Growing Libraries." https://arxiv.org/abs/2310.00656
- IMPROVED (claimed): miniF2F-valid 48.0 -> 57.0, test 45.5 -> 50.0. More than 20,000 lemmas were added
  to a growing skill library. An ablation attributes +4.9% to the library [ABS].
- FIXED: LLM (GPT-family), Isabelle verifier, retrieval.
- SELF-APPLICABLE?: No.
- TASK SUPPLY: External (miniF2F). New lemmas are proposed by an "evolver" from failed subgoals.
- REPRESENTATION: Expands (verified lemmas).
- NOVELTY CHECK: Formal verification of each lemma. Reuse was NOT measured by the authors.
- CRITIQUE (see 1.9): Almost no reuse, and no gain over a compute-matched baseline.
- CODE: https://github.com/wiio12/LEGO-Prover [ABS]

### 1.9 The critiques: "Library Learning Doesn't" and successors (Berlot-Attwell, Rudzicz, Si; +Sesterhenn)
(a) "Library Learning Doesn't: The Curious Case of the Single-Use 'Library'". arXiv 2410.20274 (Oct 2024),
    NeurIPS 2024 workshop (MATH-AI) [FT]. https://arxiv.org/abs/2410.20274 ; code https://github.com/ikb-a/curious-case
(b) "LLM Library Learning Fails: A LEGO-Prover Case Study". arXiv 2504.03048 (Apr 2025) [FT abstract].
    Code https://github.com/ikb-a/llm_lib_learning_fails (as printed in the paper; the underscore is
    rendered as a space in the PDF text).
(c) "Is This LLM Library Learning? Evaluation Must Account For Compute and Behaviour". EACL 2026 long
    paper, adds Sesterhenn [FT]. https://aclanthology.org/2026.eacl-long.163/
- FINDINGS [FT]:
  - LEGO-Prover: only 1,233 lemmas (6%) ever reach the prover's input. Of these, exactly one was
    reused verbatim, once, and no lemma's name appears in three or more solutions.
  - TroVE on MATH: the final library holds 15 functions. Only 2 are reused in correct solutions, for
    3 successful reuses across 3,201 test questions.
  - Ablations point to self-correction and self-consistency, not reuse, as the source of the gains.
  - In (c), all three ICL systems (LEGO-Prover, TroVE, AgentOptimizer) "fail to consistently outperform
    the simple baseline of prompting the model" once compute is matched, and there is "evidence
    against soft reuse".
- RELEVANCE: This is exactly the "novelty real vs reuse" question. The required standard is
  compute-matched baselines plus behavioural reuse counts. Aphrodite's causal transplant test (G1 into
  unseen families, with paired cost accounting) already meets a higher standard than most of this
  literature.

### 1.10 AbstractBeam (Zenkner, Dierkes, Sesterhenn, Bartelt; arXiv 2405.17514, 2024) [ABS]
https://arxiv.org/abs/2405.17514
- Adds DreamCoder-style wake-sleep library learning to LambdaBeam, a bottom-up, execution-guided search
  that enumerates values, which makes it the closest architectural cousin of an enumerative
  observational-equivalence search. The domain is integer list manipulation (DeepCoder-style).
- Result [ABS]: significantly more tasks solved, fewer candidates and less time than LambdaBeam.
- Code: UNVERIFIED (none listed on the arXiv page).

### 1.11 ShapeCoder (Jones, Guerrero, Mitra, Ritchie; SIGGRAPH / TOG 2023) [ABS]
https://arxiv.org/abs/2305.05661 ; code https://github.com/rkjones4/ShapeCoder
- Abstraction discovery using e-graphs "augmented with a conditional rewrite scheme" to decide when
  abstractions with parametric expressions apply. Semantic, not just syntactic, matching. The
  abstractions have multiple parameters.

### 1.12 HOUDINI (Valkov, Chaudhari, Srivastava, Sutton, Chaudhuri; NeurIPS 2018) [ABS]
"HOUDINI: Lifelong Learning as Program Synthesis."
https://proceedings.neurips.cc/paper_files/paper/2018/file/edc27f139c3b4e4bb29d1cdbc45663f9-Paper.pdf
- A library of trained neural functions composed by typed higher-order combinators. A type-directed
  synthesizer decides which library functions to reuse on each new task in a SEQUENCE.
- TASK SUPPLY: An external, designed task sequence (counting, summing, shortest path over perception).
  Transfer depends on the order of the sequence.
- REPRESENTATION: Library grows with learned neural modules. The combinator set is fixed.
- The typed representation "significantly accelerates the search" [ABS].
- Code: UNVERIFIED.

### 1.13 Bayesian Program Learning by Decompiling Amortized Knowledge (Palmarini, Lucas, Siddharth) [ABS]
arXiv 2306.07856 (venue UNVERIFIED; ICML 2024 per recollection). https://arxiv.org/abs/2306.07856
code https://github.com/abpalmarini/dreamdecompiler [SEC]
- Library entries are extracted by "decompiling" the recognition network's learned policy rather than
  by compressing solutions. The claims are faster proficiency and better generalization in DreamCoder.
  This is relevant because it is a second source of abstraction candidates besides the solved-program
  corpus.

### 1.14 "On the Value of Abstractions: Abstraction Selection in Bounded Program Synthesis" (repo only) [SEC]
https://github.com/cucupac/program-synthesis (author handle "cucupac"; no peer-reviewed venue found; UNVERIFIED as a publication)
- Reported: selecting abstractions by search-cost minimisation beats selection by compression (+4.08 test
  problems). Performance peaked around 11 abstractions and then declined. An anomalous drop between 1
  and 2 abstractions was caused by the search budget (30,000 attempts), and was recovered with a larger budget.
- Relevance: Aphrodite already selects by paired validation cost savings. This is independent
  (unreviewed) support for that choice and for budget-dependence of library value.

### 1.15 Prospective Compression in Human Abstraction Learning (Hernandez Cano, ..., Pu, Zhao, Kryven; arXiv 2605.09985, May 2026) [ABS]
https://arxiv.org/abs/2605.09985
- The paper argues that existing algorithms do "retrospective compression over a static task
  distribution". It reports that humans in a non-stationary "Pattern Builder Task" instead select
  abstractions that compress FUTURE tasks.
- Relevance: Aphrodite's donor also does retrospective compression. If the task generator is
  non-stationary (new strata), retrospective MDL systematically favours the already-dominant stratum.
- Code: UNVERIFIED.

### 1.16 FactorLibrary (Pandey et al.; arXiv 2606.25394, June 2026; ICML 2026 AI-for-Math workshop) [ABS]
https://arxiv.org/abs/2606.25394
- Stores factorizable subexpressions as reusable subgoals across RL episodes for minimal arithmetic
  circuits over finite fields. Of interest as a 2026 "library of subgoals" in integer/polynomial
  arithmetic. Compounding is not quantified in the abstract. Code: UNVERIFIED.

### 1.17 Leroy (arXiv 2410.06438, 2024) [SEC]
https://arxiv.org/abs/2410.06438 . Library learning for imperative languages. Existence only; details UNVERIFIED.

### 1.18 GP classics: ADFs, module acquisition, ARL

(a) Koza, "Genetic Programming II: Automatic Discovery of Reusable Programs", MIT Press 1994 [SEC].
    http://gpbib.cs.ucl.ac.uk/gp-html/koza_gp2.html
    - ADFs are parameterised subroutines whose ARCHITECTURE (number of ADFs, arity) is FIXED by the
      designer. Their bodies co-evolve with the main program, and ADFs may call earlier ADFs
      (hierarchical). The claims are smaller solutions and "leverage" from repeated use.
    - Specific computational-effort numbers (e.g., even-parity scaling of the ADF advantage):
      UNVERIFIED this session.
    - SELF-APPLICABLE?: No. The representation expands only within designer-fixed slots, and the task is external.
(b) Angeline and Pollack, "Evolutionary module acquisition", Proc. 2nd Evolutionary Programming conf.
    1993 [SEC]. Subtrees are compressed out into new named functions (a "genetic library"). This is the
    GP ancestor of compression-based library learning. https://www.researchgate.net/publication/2266501
(c) Rosca and Ballard, "Discovery of Subroutines in Genetic Programming", Advances in GP 2 (1996), ch. 9 [SEC].
    ARL (Adaptive Representation through Learning): building blocks are identified from the evolution
    trace, generalised into new functions, and the function set is extended on the fly, giving
    HIERARCHIES of subroutines.
(d) Dessi, Giani, Starita, "An Analysis of Automatic Subroutine Discovery in Genetic Programming",
    GECCO 1999, vol. 2, pp. 996-1001 [SEC]. https://dl.acm.org/doi/10.5555/2934046.2934055
    - Main result (per abstract as indexed): "any attempt to improve the selection criterion seems not
      able to produce better results than a simple near-random heuristic."
    - IMPORTANT NEGATIVE for Aphrodite: run a random-selection baseline for schema choice.

### 1.19 Meta-GP and autoconstructive evolution: mechanisms that vary their own variation

(a) Edmonds, "Meta-Genetic Programming: Co-evolving the Operators of Variation", Turkish J. EE&CS 9(1):13-29, 2001 [ABS].
    http://cfpm.org/pub/papers/mgp.pdf
    - Operators are themselves trees and co-evolve. "The language used to define the operators must
      preserve the variation in the base population for the technique to work". Tested on parity.
(b) Spector and Robinson, "Genetic Programming and Autoconstructive Evolution with the Push Programming
    Language", GPEM 3:7-40, 2002 [ABS]. https://link.springer.com/article/10.1023/A:1014538503543
    - PushGP evolves Push programs. Pushpop "also evolves Push programs but simultaneously evolves
      its own evolutionary mechanisms": each individual builds its own children.
(c) Spector, McPhee, Helmuth, Casale, Oks, "Evolution Evolves with Autoconstruction", GECCO 2016
    companion [FT]. https://faculty.hampshire.edu/lspector/pubs/wk1202-spectorA.pdf
    - This is the honest status report. Prior autoconstructive systems "could only solve relatively
      simple problems", were "outperformed by standard genetic programming systems", and "did not reach
      the critical threshold for self-improvement".
    - Cloning collapse: "programs in a population could not be allowed to make exact clones of
      themselves. ... if a cloning program were to arise with reasonably good performance ... the
      descendants ... would rapidly fill the population. After this happens no further evolution is
      possible."
    - AutoDoG (Autoconstructive Diversification of Genomes) adds lexicase selection and a
      diversification constraint on offspring. It solves Replace-Space-with-Newline in "approximately
      5 - 10%" of runs, while the best prior (non-autoconstructive) work reaches "about 50%".
      The constraint "is not necessarily" one that makes variation methods themselves vary.
(d) Harrington, Spector, Pollack, O'Reilly, "Autoconstructive evolution for structural problems",
    GECCO 2012 companion [SEC]. https://dl.acm.org/doi/10.1145/2330784.2330797
    Spector and Moscovici, "Recent developments in autoconstructive evolution", GECCO 2017 [SEC; details UNVERIFIED].
    Spector, "Towards practical autoconstructive evolution", GPTP 2010 [SEC].
    https://faculty.hampshire.edu/lspector/pubs/spector-gptp10-preprint.pdf
    Schmidhuber 1987 diploma thesis as origin of meta-GP / self-referential learning: UNVERIFIED this session.
- SELF-APPLICABLE?: YES. This is the only family in cluster B where the improvement mechanism
  (variation) is itself a product under selection. The empirical record is weak: it underperforms
  fixed human-designed mechanisms and needs anti-clone / diversification constraints to avoid
  collapse to a fixed point.
- CODE: Push implementations are listed at http://pushlanguage.org and
  http://faculty.hampshire.edu/lspector/push.html [SEC].

### 1.20 Grammatical evolution (O'Neill and Ryan, IEEE TEC 5(4), 2001) [ABS]
https://dl.acm.org/doi/10.1109/4235.942529
- A binary genome selects productions of a BNF grammar. The grammar is FIXED; "Grammatical Evolution
  by Grammatical Evolution" (O'Neill and Ryan, EuroGP 2004 [SEC]) co-evolves the grammar itself,
  which is a meta-level analogue of DSL growth. Code: PonyGE2 https://arxiv.org/abs/1703.08535 [SEC].

### 1.21 Algorithm discovery: AlphaTensor, AlphaDev, FunSearch, AlphaEvolve

For these systems the "improvement" is a better product found by a fixed search. None of them
accumulates a reusable library across tasks in the DreamCoder sense.

- AlphaTensor (Fawzi et al., Nature 610:47-53, 2022) [ABS]. https://www.nature.com/articles/s41586-022-05172-4
  code https://github.com/google-deepmind/alphatensor . Matrix multiplication is framed as a
  single-player tensor-decomposition game (AlphaZero). The representation is fixed, the task is fixed,
  and the product is algorithms. It does not improve itself.
- AlphaDev (Mankowitz et al., Nature 618:257-263, 2023) [ABS]. https://www.nature.com/articles/s41586-023-06004-9
  An assembly game for small sorts, with results merged into LLVM libc++. Fixed instruction set and
  fixed task. The "novelty" claimed is swap/copy move sequences. A follow-up, "Shorter and faster than
  Sort3AlphaDev" (arXiv 2307.14503 [SEC]), found further improvement by other means.
- FunSearch (Romera-Paredes et al., Nature 625:468-475, 2024) [ABS]. https://www.nature.com/articles/s41586-023-06924-6
  The LLM writes only a priority function inside a FIXED, human-written skeleton, scored by an
  evaluator, with an evolutionary program database. Relevance to abstraction: the skeleton is a
  human-supplied single-hole schema, fold-like with one open function, which is exactly Aphrodite's
  (acc + {H}) shape one level up. FunSearch never learns the skeleton.
  Code (evaluation artifacts): https://github.com/google-deepmind/funsearch [UNVERIFIED this session].
- AlphaEvolve (Novikov et al., arXiv 2506.13131, 2025) [ABS]. https://arxiv.org/abs/2506.13131
  An LLM-driven evolutionary coding agent that edits whole files, with evaluators. It reports
  4x4 complex matrix multiplication with 48 scalar multiplications. Its results include improvements
  to Google infrastructure, some of them feeding back into training the models it uses (per abstract
  and press). That is the closest "mechanism improves itself" claim in this cluster, but it runs
  through an external human/infra loop. No library abstraction measurement is reported.

### 1.22 ARC-oriented program synthesis with DSLs

- Bober-Irizar and Banerjee, "Neural networks for abstraction and reasoning: Towards broad generalization
  in machines", Scientific Reports 2024 [ABS]. https://arxiv.org/abs/2402.03507 ;
  code https://github.com/mxbi/dreamcoder-arc
  DreamCoder on ARC with a hand-designed DSL (PeARL). It reports 3x more tasks solved than the prior
  DreamCoder-style work. The DSL is hand-built, and library learning grows it only modestly.
- CodeIt (Butt et al., ICML 2024) [ABS]. https://arxiv.org/abs/2402.04858 ;
  code https://github.com/Qualcomm-AI-research/codeit
  Self-improvement by hindsight relabeling: any program becomes a solved task for the output it
  actually produces. This makes task supply ENDOGENOUS, turning failures into new training tasks.
  15% of the ARC evaluation set was solved. The DSL (Hodel's re-arc/arc-dsl) is fixed; the learner
  improves, not the DSL.
- "Self-Improving Language Models for Evolutionary Program Synthesis: A Case Study on ARC-AGI"
  (arXiv 2507.14172) [SEC; details UNVERIFIED].

### 1.23 Integer-sequence program synthesis (the closest domain match to Aphrodite)

- Gauthier and Urban, "Learning Program Synthesis for Integer Sequences from Scratch", AAAI 2023 [ABS].
  https://arxiv.org/abs/2202.11908 . A self-learning loop over OEIS: tree search guided by a policy,
  checking against ALL OEIS sequences (not just the target), then retraining. 27,987 sequences were
  solved "from scratch" in a small DSL with loop constructs. The AITP 2024 abstract "Solving
  One-Third of the OEIS from Scratch" [SEC] reports later work beyond 90,000 sequences (per search
  snippet; UNVERIFIED in the primary source).
  - TASK SUPPLY: External but huge and naturally graded (OEIS). Checking against every sequence gives
    free hindsight solutions, just as CodeIt does.
  - REPRESENTATION: DSL fixed. Improvement is in the policy, with no explicit library.

### 1.24 Enumerative-synthesis equivalence (the lineage of Aphrodite's semantic classing)

- Observational equivalence (OE) in bottom-up enumeration: TRANSIT (Udupa et al., PLDI 2013) and
  Escher (Albarghouthi, Gulwani, Kincaid, CAV 2013) [SEC via citing papers, e.g.
  "Just-in-Time Learning for Bottom-Up Enumerative Synthesis", OOPSLA 2020, https://arxiv.org/abs/2010.08663].
  Programs are grouped by their outputs on the example inputs, and one representative is kept per class.
- "Program Synthesis with Equivalence Reduction" [SEC] https://par.nsf.gov/servlets/purl/10100598 (details UNVERIFIED).
- egg / equality saturation (Willsey et al., POPL 2021): the e-graph substrate of babble. Cited
  within babble [FT]; not separately fetched.

### 1.25 Anti-unification theory

- Plotkin 1970 and Reynolds 1970 (Machine Intelligence 5): first-order syntactic LGG, unique up to
  renaming. Confirmed as the origin in the Cerna-Kutsia survey [FT].
- Cerna and Kutsia, "Anti-unification and Generalization: A Survey", IJCAI 2023 [FT].
  https://arxiv.org/abs/2302.00277
  - The survey notes that babble "developed an E-graph anti-unification algorithm motivated solely by
    the seminal work of Plotkin" and missed the prior equational (Burghardt 2005) and term-graph AU
    (Baumgartner et al. 2018) work. That is a warning about reinvention that applies to Aphrodite too.
  - Equational AU: commutative theories (Baader 1991) are unitary. A/C/AC/U theories vary in their
    generalization type.
  - Higher-order: Cerna and Buran 2022 ("One or nothing", arXiv 2207.08918) show that unrestricted
    generalization in simply-typed lambda calculus is problematic: it is nullary in general (a minimal
    complete set may not exist). Tractable fragments are higher-order PATTERNS (Baumgartner, Kutsia,
    Levy, Villaret, J. Autom. Reason. 58(2), 2017, linear time) and restricted variants (Cerna-Kutsia
    FSCD 2019).

---------------------------------------------------------------------------------------------------

## 2. Answers to the specific questions

### (a) Is there evidence that learned libraries compound (G1 enabling G2 that is unreachable without G1)?

Evidence found, by strength:
1. Qualitative chains (DreamCoder [FT], Stitch Fig. 3 [FT], ARL hierarchies [SEC], Koza's hierarchical
   ADFs [SEC]). DreamCoder's filter -> max -> nth-largest -> sort is the canonical example, and "each
   round of abstraction built on concepts discovered in earlier sleep cycles". Physics: vector algebra,
   then the inverse-square schema. Lisp: fold, then unfold, then the rest.
2. Correlational: in DreamCoder, library depth vs solved tasks r = 0.79 across domains, and the
   recognition model yields deeper libraries [FT].
3. Counterfactual "unreachability": DreamCoder argues sort would need a 32-call primitive program,
   "in excess of 10^72 years of brute-force search". This is an argument about the SOLUTION, not about
   whether the ABSTRACTION G2 could have been derived without G1.
4. Controlled causal test (remove G1, check whether G2 is still derivable): NONE FOUND. Targeted searches
   turned up no such ablation. DreamCoder ablates the whole abstraction phase, not individual entries.
   => Aphrodite's recursion test is stricter than anything in the published record.
Counter-evidence and complications:
- LILO re-derives the library from primitives every iteration ("deep refactoring") to escape early
  suboptimal abstractions [FT]. Inheritance is not how the best-performing successor gets hierarchy.
- The breadth cost (DreamCoder footnote [FT]; the unreviewed cucupac repo reports a non-monotone
  library-size curve) means a larger library can make the NEXT search harder unless a learned policy
  offsets it.
- LLM "libraries" are mostly not reused at all (1.9).
Conditions under which compounding appeared: a fixed, externally curated, VARIED task set containing
easy tasks in the relevant structure. Tasks were cycled many times, abstractions were composable with
unbounded program size (the lambda calculus), and a learned search policy paid the breadth cost.

### (b) What task-supply / curriculum properties did successful systems require?

- Stepping stones: some tasks must be solvable in the base language (EC: zero learning when no task is
  hit in the initial frontier [FT]).
- Gradient of difficulty WITHIN the target structure: EC shows sharp drops when the constant and linear
  polynomials are removed, even though quadratics are expressible [FT].
- Variety: DreamCoder needs "sufficiently varied training tasks" [FT]; its list set of 218 tasks came
  from EC2.
- Ordering: helps LLM refactoring strongly (ReGAL -18.7 LOGO without curriculum [FT]). DreamCoder
  instead uses random sampling from a graded pool.
- Side information: LILO and LAPS use language annotations.
- Endogenous supply remedies: hindsight relabeling (CodeIt [ABS]) and cross-checking against all targets
  (Gauthier-Urban OEIS [ABS]). Both turn "wrong" programs into solved tasks for someone else.
- Non-stationarity: prospective rather than retrospective selection (1.15, human data).
Mapping to Aphrodite: a sampler stratified by top-level operator that yields 0/32 qualified families in
the mul/mod/pow strata is the EC "quadratics with coefficients > 1" condition. The literature predicts
failure regardless of the abstraction mechanism.

### (c) Is single-hole LGG known to be too weak?

Yes, in several respects:
- Plotkin/Reynolds LGG is already multi-variable. Each distinct mismatched pair of subterms gets its own
  variable, and repeated identical pairs share one. A single-hole restriction is strictly weaker than
  classical LGG.
- Practice uses multiple holes: Stitch at arity up to 3 with multi-use variables [FT], DreamCoder with
  arbitrary-arity lambda abstractions including higher-order ones [FT], babble with multi-variable
  patterns modulo theory [FT], ShapeCoder with parametric expressions [ABS].
- Higher-order abstractions (functions as arguments) needed extra machinery even in Stitch, and Stitch
  lost to DreamCoder on lists without it [FT].
- Pairwise AU (babble) restricts to the most concrete pattern for each pair and admits this can miss
  optimal patterns [FT].
- Unrestricted higher-order AU is ill-behaved (nullary). Use the pattern fragment (linear time) [FT via survey].
Concrete consequence: schemas like (acc * {H1} + {H2}), or ones that tie init and final to body
(for example init=1 with body acc*{H}), cannot be expressed with one hole in the body alone. The
multiplicative strata likely require two holes or a joint (init, body, final) schema.

### (d) Is Aphrodite's semantic-equivalence classing known?

Largely yes:
- Observational equivalence (TRANSIT and Escher 2013) groups programs by behaviour on inputs. It is
  standard in bottom-up enumeration and is used implicitly by LambdaBeam and AbstractBeam-style value
  search.
- Library learning modulo an equational theory (babble 2023) targets exactly the E4 failure class of
  syntactic variation. ShapeCoder uses conditional rewrites.
- DreamCoder's refactoring (up to 3 beta steps, version spaces) is a bounded semantic normalisation.
What looks less standard: classing at the WHOLE-PROGRAM level (init, body, final jointly), then
anti-unifying member bodies. E4's "compensating factorisation" (acc - v*v with final first-acc vs
acc + v*v with final acc+first) is not an equation between bodies. It is a change of representation of
the accumulator (acc -> -acc) that the final function undoes: a data-refinement or conjugacy of folds
(cf. fold-fusion laws in "origami programming", cited by DreamCoder [FT]; theory not fetched). Local
equational rewriting, as in babble, would not identify these bodies unless the theory contained a
fold-level conjugation rule.
Two caveats: (i) OE-style classing is only as sound as the input set, so Aphrodite's certification
step is essential and should be reported with its false-merge rate. (ii) Cite babble and OE as ancestors
and claim only the whole-program lift.

### (e) Importable benchmark task families (concrete, with sources)

1. EC polynomial ladder (Dechter et al. 2013): all polynomials of degree <= 2 with coefficients 0..9, plus
   the published ablated subsets ("no constant", "no linear", "only quadratics", coefficients > 0,
   coefficients > 1). It is a ready-made, graded stepping-stone supply for MULTIPLICATIVE structure,
   with a known failure point to replicate.
2. DreamCoder / EC2 list-processing set: 218 tasks, 15 I/O examples each, split 50/50. Data in
   https://github.com/ellisk42/ec . It is the list domain where the filter/max/nth-largest/sort hierarchy
   emerged, and the natural benchmark for testing compounding under matched conditions.
3. DreamCoder text editing, symbolic regression and physics (60 laws) sets, same repository.
4. DeepCoder DSL tasks (Balog et al., ICLR 2017, https://arxiv.org/abs/1611.01989): integer-list
   functions such as MAP, FILTER, COUNT, ZIPWITH, SCANL1 and SUM. SCANL1 and ZIPWITH are fold-like.
5. LambdaBeam list tasks (Shi et al., NeurIPS 2023, https://arxiv.org/abs/2306.02049 ; code
   https://github.com/ellisk42/lambdabeam), an extended DeepCoder DSL with arbitrary lambdas, plus the
   AbstractBeam follow-up (library learning on the same domain).
6. OEIS integer sequences (Gauthier and Urban, https://arxiv.org/abs/2202.11908). This is the
   closest domain to Aphrodite's integer folds. Sequences stratify naturally by operator (arithmetic
   progressions, products and factorials, powers, periodic/mod sequences, gcd-based), giving a
   non-additive supply that is graded in difficulty.
7. PSB1 (Helmuth and Spector 2015 [SEC]) and PSB2 (Helmuth and Kelly, GECCO 2021,
   https://arxiv.org/abs/2106.06086 ; data https://zenodo.org/records/4678740). These are 25
   moderate-difficulty tasks from Code Wars, Advent of Code, Project Euler and course homework. Several
   are integer loops, and they are the standard GP comparison point.
8. Rule et al. list-function rule benchmark (Nature Communications 15:6847, 2024,
   https://www.nature.com/articles/s41467-024-50966-x): 100 "algorithmically rich" rules with human
   learning data. Code URL UNVERIFIED.
9. ARC via PeARL (https://github.com/mxbi/dreamcoder-arc) and CodeIt's re-arc setup. These are out of
   domain for integer folds but are the standard for DSL growth.
10. LILO domains REGEX, CLEVR and LOGO (https://github.com/gabegrand/lilo), and ReGAL's LOGO, Date and
    TextCraft sets (https://github.com/esteng/regal_program_learning).
11. Stitch/babble compression benchmarks (https://github.com/mlb2251/compression_benchmark;
    babble POPL23 artifact). These are corpora, not tasks. They are useful for testing the
    anti-unification step alone against published compression numbers.
Lowest-cost high-value imports: (1) and (6) for the mul/mod/pow strata, and (2) for a replication of
compounding under a known-positive supply.

---------------------------------------------------------------------------------------------------

## 3. Challenges to Aphrodite's design

C1. The negative recursion result confounds mechanism with task supply. With mul/mod/pow strata at 0/32
    qualified families, the donor's corpus contains only additive programs. Compression over an additive
    corpus can only return additive schemas, and re-deriving G1 is the MDL-optimal answer. EC 2013 shows
    the same collapse with a perfectly good mechanism. Required: a POSITIVE CONTROL, meaning a planted
    task family where a known G2 (non-derivative of G1) exists and is compressible only once G1-using
    programs are present. Show the pipeline finds it. Without that, "NO" has no statistical power.

C2. The representation may leave no headroom for abstraction-on-abstraction. Bodies are depth 2. G1 =
    (acc + {H}) already occupies the top level. A G2 that CONTAINS G1 but is not a specialization of it
    would need G1 nested inside a larger context (e.g., ((acc + {H}) * K) or a second fold stage). That
    may exceed the depth-2 grammar. DreamCoder's hierarchy exists because the lambda calculus has
    unbounded composition and library calls shorten deep programs. Check: does a library entry's hole
    admit depth-2 fills, raising reachable depth to 3+? If not, compounding is structurally excluded,
    and the recursion test is testing the grammar, not the donor.

C3. The single hole is below the classical baseline. Plotkin LGG is multi-variable. Stitch, DreamCoder and
    babble all use multi-argument abstractions. Multiplicative families plausibly need two holes, or
    coupled init/final (identity element 1 for products, 0 for sums). Test multi-hole AU (arity <= 3,
    Stitch-style) and joint (init, body, final) schemas before concluding anything about recursion.

C4. Library-first ordering plus per-candidate charging creates a rich-get-richer loop. Donors holding G1
    find add/sub solutions through G1 first, their corpus fills with G1-instances, and compression
    returns G1. This is the library analogue of the autoconstructive "cloning" collapse (Spector et al.
    2016 [FT]), where a good-enough self-replicator fills the population. Remedies from the literature:
    LILO-style re-derivation from L0 each round; a diversification constraint that rejects offspring
    schemas equivalent to parents (Aphrodite already has the novelty criterion as a filter, but no
    pressure toward it); prospective selection for coverage of UNSOLVED strata rather than compression
    of solved ones.

C5. Breadth cost. Every library entry walked before fallback adds breadth (DreamCoder footnote).
    DreamCoder pays this with a learned recognition model; Aphrodite has none. A G2 search may be
    harder with G1 present, which would be "negative compounding". Measure candidates-to-first-solution
    on non-additive families with G1 ordered first, ordered last, and absent.

C6. Selection heuristic baseline. Dessi et al. 1999 found that subroutine-selection criteria beyond
    near-random did not help in ARL. Add a random-schema-selection arm, matched in count, to the
    transplant experiments.

C7. What counts as recursion. In every library-learning system here, only the PRODUCT (library)
    improves and the abstraction mechanism is fixed. Aphrodite's G1 -> G2 test is product-level recursion,
    the kind DreamCoder claims. Mechanism-level recursion, where the donor improves its own
    abstraction procedure, exists only in meta-GP and autoconstructive evolution. Its record is weak:
    Pushpop solved only simple problems, AutoDoG succeeds 5-10% on a problem where fixed-mechanism GP
    reaches about 50%, and anti-clone constraints are needed. Keep the two levels separate in claims.

C8. Evaluation standard. The LLM library-learning critique requires compute-matched baselines and
    behavioural reuse counts. Aphrodite's paired cost accounting and causal transplant already meet
    this standard. Keep reporting reuse counts: in how many solved families G1 actually appears.

C9. Soundness of semantic classes. OE with finite inputs can merge programs that are not equivalent.
    Report the certification method and its false-merge rate. Cite OE and babble as ancestors, and
    claim novelty only for the whole-program (init, body, final) lift that resolves compensating
    factorisations.

---------------------------------------------------------------------------------------------------

## 4. What Prometheus may be rediscovering

1. The stepping-stone dependency of compression-based bootstrapping: EC, Dechter et al. 2013, Sec. 4.1.
   Aphrodite's 0/32 strata finding is the "only quadratics with coefficients > 1" result.
2. The syntactic-variation failure of anti-unification: babble 2023 (library learning modulo an
   equational theory). E4's diagnosis is the same, though E4's specific case (a compensating change of
   accumulator representation) goes beyond babble's local rewrites.
3. Observational-equivalence classing: TRANSIT and Escher 2013.
4. Search-cost (not compression) as the selection criterion, and the breadth/depth tradeoff: DreamCoder
   footnote; cucupac repo (unreviewed).
5. Causal reuse measurement: the Berlot-Attwell et al. 2024-2026 critique of LLM library learning.
6. Fixed-point / clone collapse when a system seeds its own next generation: autoconstructive evolution
   (Spector et al.), whose fix is diversification constraints. G1 re-derivation is the library-level
   analogue.
7. The "skeleton with one open function" pattern: FunSearch's human-written skeleton is a single-hole
   schema; Aphrodite derives the analogous schema endogenously. That endogenous derivation (G1 accepted)
   appears to be the genuinely novel part relative to FunSearch, not relative to DreamCoder.
8. Re-derivation vs inheritance of libraries: LILO's "deep refactoring".
9. Reinvention risk in anti-unification in general. The Cerna-Kutsia survey documents that babble
   rebuilt equational AU without the prior literature, so check Burghardt 2005 (E-generalization via
   regular tree grammars) and the higher-order pattern AU work before building more AU machinery.

---------------------------------------------------------------------------------------------------

## 5. Suggested next experiments (derived from the above; not literature claims)

E-a  Positive control: plant a family set where G2 = a two-hole or nested schema over G1 is
     MDL-favourable only given G1-rewritten programs. Verify detection power.
E-b  Task-supply swap: replace the operator-stratified sampler with the EC polynomial ladder and an
     OEIS-derived ladder that includes the easy members (constants and linears before quadratics;
     n, n*c, n^2 before products and powers). Rerun the G1 -> G2 test.
E-c  Arity sweep: 1, 2 and 3 holes, and joint (init, body, final) schemas.
E-d  Ordering sweep: G1 first / last / absent, and re-derivation from L0 each round (the LILO control).
E-e  Random-schema selection baseline (the Dessi et al. control).
E-f  Hindsight relabeling: every program the donor finds counts as a solution to the family it actually
     computes (CodeIt / Gauthier-Urban). This produces endogenous task supply in the mul/mod/pow strata.

---------------------------------------------------------------------------------------------------

## 6. References (URLs)

Library learning / abstraction
- Dechter, Malmaud, Adams, Tenenbaum. Bootstrap learning via modular concept discovery. IJCAI 2013. https://www.ijcai.org/Proceedings/13/Papers/196.pdf [FT]
- Ellis, Morales, Sable-Meyer, Solar-Lezama, Tenenbaum. Learning Libraries of Subroutines for Neurally-Guided Bayesian Program Induction. NeurIPS 2018. https://proceedings.neurips.cc/paper/2018/hash/7aa685b3b1dc1d6780bf36f7340078c9-Abstract.html [ABS]
- Ellis et al. DreamCoder. arXiv 2006.08381; PLDI 2021; Phil Trans R Soc A 2023. https://arxiv.org/abs/2006.08381 ; https://github.com/ellisk42/ec [FT]
- Bowers et al. Top-Down Synthesis for Library Learning (Stitch). POPL 2023. https://arxiv.org/abs/2211.16605 ; https://github.com/mlb2251/stitch [FT]
- Cao, Kunkel, Nandi, Willsey, Tatlock, Polikarpova. babble. POPL 2023. https://arxiv.org/abs/2212.04596 ; https://github.com/dcao/babble [FT]
- Grand et al. LILO. ICLR 2024. https://arxiv.org/abs/2310.19791 ; https://github.com/gabegrand/lilo [FT]
- Stengel-Eskin, Prasad, Bansal. ReGAL. ICML 2024. https://arxiv.org/abs/2401.16467 ; https://github.com/esteng/regal_program_learning [FT]
- Wang et al. LEGO-Prover. ICLR 2024. https://arxiv.org/abs/2310.00656 ; https://github.com/wiio12/LEGO-Prover [ABS]
- Berlot-Attwell, Rudzicz, Si. Library Learning Doesn't. arXiv 2410.20274 (2024). https://arxiv.org/abs/2410.20274 ; https://github.com/ikb-a/curious-case [FT]
- Berlot-Attwell, Rudzicz, Si. LLM Library Learning Fails: A LEGO-Prover Case Study. arXiv 2504.03048 (2025). https://arxiv.org/abs/2504.03048 [FT abstract]
- Berlot-Attwell, Sesterhenn, Rudzicz, Si. Is This LLM Library Learning? EACL 2026. https://aclanthology.org/2026.eacl-long.163/ [FT]
- Zenkner, Dierkes, Sesterhenn, Bartelt. AbstractBeam. arXiv 2405.17514. https://arxiv.org/abs/2405.17514 [ABS]
- Jones, Guerrero, Mitra, Ritchie. ShapeCoder. SIGGRAPH 2023. https://arxiv.org/abs/2305.05661 ; https://github.com/rkjones4/ShapeCoder [ABS]
- Valkov et al. HOUDINI. NeurIPS 2018. https://proceedings.neurips.cc/paper_files/paper/2018/file/edc27f139c3b4e4bb29d1cdbc45663f9-Paper.pdf [ABS]
- Palmarini, Lucas, Siddharth. Bayesian Program Learning by Decompiling Amortized Knowledge. arXiv 2306.07856. https://arxiv.org/abs/2306.07856 [ABS]
- Wong et al. Leveraging Language to Learn Program Abstractions and Search Heuristics (LAPS). ICML 2021. https://arxiv.org/abs/2106.11053 [SEC]
- Hernandez Cano et al. Prospective Compression in Human Abstraction Learning. arXiv 2605.09985 (2026). https://arxiv.org/abs/2605.09985 [ABS]
- Pandey et al. FactorLibrary. arXiv 2606.25394 (2026). https://arxiv.org/abs/2606.25394 [ABS]
- Leroy: Library Learning for Imperative Programming Languages. arXiv 2410.06438. https://arxiv.org/abs/2410.06438 [SEC]
- "On the Value of Abstractions: Abstraction Selection in Bounded Program Synthesis" (repo). https://github.com/cucupac/program-synthesis [SEC; unreviewed]

Anti-unification / equivalence
- Cerna, Kutsia. Anti-unification and Generalization: A Survey. IJCAI 2023. https://arxiv.org/abs/2302.00277 [FT]
- Cerna, Buran. One or Nothing: Anti-unification over the Simply-Typed Lambda Calculus. arXiv 2207.08918. https://arxiv.org/abs/2207.08918 [SEC via survey]
- Baumgartner, Kutsia, Levy, Villaret. Higher-order pattern anti-unification in linear time. J. Autom. Reason. 58(2), 2017. [SEC via survey]
- Plotkin 1970; Reynolds 1970. Machine Intelligence 5. [SEC via survey]
- Just-in-Time Learning for Bottom-Up Enumerative Synthesis (OOPSLA 2020), which describes TRANSIT/Escher OE. https://arxiv.org/abs/2010.08663 [SEC]

GP / autoconstructive / meta
- Koza. Genetic Programming II. MIT Press 1994. http://gpbib.cs.ucl.ac.uk/gp-html/koza_gp2.html [SEC]
- Angeline, Pollack. Evolutionary module acquisition. 1993. https://www.researchgate.net/publication/2266501_Evolutionary_Module_Acquisition [SEC]
- Rosca, Ballard. Discovery of Subroutines in Genetic Programming. Adv. GP 2, 1996. https://gpbib.pmacs.upenn.edu/gp-html/JustinianRosca.html [SEC]
- Dessi, Giani, Starita. An Analysis of Automatic Subroutine Discovery in GP. GECCO 1999. https://dl.acm.org/doi/10.5555/2934046.2934055 [SEC]
- Edmonds. Meta-Genetic Programming. Turk J EE&CS 2001. http://cfpm.org/pub/papers/mgp.pdf [ABS]
- Spector, Robinson. GP and Autoconstructive Evolution with Push. GPEM 2002. https://link.springer.com/article/10.1023/A:1014538503543 [ABS]
- Spector, McPhee, Helmuth, Casale, Oks. Evolution Evolves with Autoconstruction. GECCO 2016. https://faculty.hampshire.edu/lspector/pubs/wk1202-spectorA.pdf [FT]
- Spector. Towards Practical Autoconstructive Evolution. GPTP 2010. https://faculty.hampshire.edu/lspector/pubs/spector-gptp10-preprint.pdf [SEC]
- Harrington, Spector, Pollack, O'Reilly. Autoconstructive evolution for structural problems. GECCO 2012. https://dl.acm.org/doi/10.1145/2330784.2330797 [SEC]
- O'Neill, Ryan. Grammatical Evolution. IEEE TEC 2001. https://dl.acm.org/doi/10.1109/4235.942529 [ABS]

Algorithm discovery
- Fawzi et al. AlphaTensor. Nature 2022. https://www.nature.com/articles/s41586-022-05172-4 ; https://github.com/google-deepmind/alphatensor [ABS]
- Mankowitz et al. AlphaDev. Nature 2023. https://www.nature.com/articles/s41586-023-06004-9 [ABS]
- Romera-Paredes et al. FunSearch. Nature 2024. https://www.nature.com/articles/s41586-023-06924-6 [ABS]
- Novikov et al. AlphaEvolve. arXiv 2506.13131 (2025). https://arxiv.org/abs/2506.13131 [ABS]

ARC / integer-sequence / benchmarks
- Bober-Irizar, Banerjee. Neural networks for abstraction and reasoning. Sci Rep 2024. https://arxiv.org/abs/2402.03507 ; https://github.com/mxbi/dreamcoder-arc [ABS]
- Butt et al. CodeIt. ICML 2024. https://arxiv.org/abs/2402.04858 ; https://github.com/Qualcomm-AI-research/codeit [ABS]
- Gauthier, Urban. Learning Program Synthesis for Integer Sequences from Scratch. AAAI 2023. https://arxiv.org/abs/2202.11908 [ABS]
- Balog et al. DeepCoder. ICLR 2017. https://arxiv.org/abs/1611.01989 [ABS]
- Shi et al. LambdaBeam. NeurIPS 2023. https://arxiv.org/abs/2306.02049 ; https://github.com/ellisk42/lambdabeam [ABS]
- Helmuth, Kelly. PSB2. GECCO 2021. https://arxiv.org/abs/2106.06086 ; https://zenodo.org/records/4678740 [ABS]
- Rule, Piantadosi, Cropper, Ellis, Nye, Tenenbaum. Symbolic metaprogram search. Nat Commun 2024. https://www.nature.com/articles/s41467-024-50966-x [ABS]
