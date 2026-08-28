D-4 SUBSTRATE PHYSICS -- DEEP RESEARCH DISPATCH
2026-08-27. 20 fires, one per daily token. Author: Aporia.

Source: agent_d4_blind/VERDICT-PHASE1.md (frozen 2026-08-27), plus a
frontier-model appraisal of that verdict which asserted both (a) a 30-year
prior-art lineage and (b) methodological novelty. Doctrine says a frontier
model converging on a critique is corpus gravity, not validation, so the
first tier is built to KILL the novelty claim rather than confirm it.

Reports land as aporia/docs/deep_research_batch_2026-08-27/report_D4_NN_*.md

====================================================================
STANDING RUBRIC -- PREPEND TO EVERY FIRE
====================================================================

You are doing an adversarial literature review for a research programme
that assumes its own claims are wrong until proven otherwise. Follow these
rules exactly.

  - Cite PRIMARY literature only: author, year, venue, DOI or arXiv id.
    A textbook, blog, survey or wiki may orient you but may not be the
    anchor for a factual claim.
  - Quote the specific number, figure, or theorem you are relying on, and
    give its location in the paper. If a claim is qualitative in the
    source, say so; do not attach a number that the source does not state.
  - If you cannot find something, write NOT FOUND and say where you
    looked. Do not fill a gap with a plausible-sounding synthesis. A short
    honest report beats a long confident one.
  - Separate: (1) what the source demonstrates, (2) what the field
    believes, (3) what you inferred. Label each.
  - End every report with a section called WHAT WOULD FALSIFY THIS, and a
    section called STRONGEST DISCONFIRMING SOURCE naming the best paper
    that cuts AGAINST the answer you gave.

Background you need, identical for every fire. A programme measured
whether four machine-native computational substrates possess a navigable
"accessibility geometry": whether generic, history-free search can move
through executable behaviour space without designer-engineered ramps. All
metrics were frozen before measurement, and the learner was quarantined --
no learning algorithm existed during the test. The four substrates were a
register machine (S1_REG), a typed stack machine (S2_STACK), a string
rewrite system (S3_REWRITE), and a memory-tape machine (S4_MEM). Distance
between programs was defined purely by intrinsic behavioural fingerprints
(I/O, execution traces, resource profiles), never by human semantic
labels. Headline results, at a 1,200-evaluation budget with a hit
threshold of behavioural distance <= 0.10:

    substrate     viability   phenotype   far-stratum    verdict
                              classes     hit rate
    S1_REG          0.093       3,452       0.00-0.02    NAVIGATION_FAILURE
    S2_STACK        0.500       7,281       0.15         PASS (marginal)
    S3_REWRITE      0.996      11,717       0.00         FRAGMENTED
    S4_MEM          0.593       9,575       0.53         PASS (robust)

An offline oracle that traverses only OBSERVED edges reported far-stratum
reachability of 0.41 for S1, 0.50 for S2, 0.73 for S4, and 0.00 for S3 --
so S1 is a search failure at that budget while S3 is a genuine topology
failure. Roughly 1.5 million metered evaluations total.

====================================================================
TIER 1 -- KILL THE NOVELTY CLAIM (fire these first, 5 tokens)
====================================================================

D4-01  PRIOR ART: FROZEN PREREGISTERED SUBSTRATE COMPARISON

Find every prior instance in artificial life, genetic programming,
evolutionary computation, or machine learning where researchers compared
two or more computational substrates or instruction sets under a metric
suite that was FROZEN AND PUBLISHED BEFORE the substrates were measured,
with an explicit prohibition on modifying the substrate after seeing
results. I expect this to be rare but I want to be proved wrong. Report
the closest five matches even if none is exact, and for each state
precisely which element of the discipline was present and which was
missing. Cover at minimum: Avida and Tierra methodology papers, the
Genetic Programming benchmark-suite reform literature (McDermott et al.
2012 onward), preregistration in ML (the NeurIPS/ICML reproducibility and
preregistration workshop tracks), and any registered-report practice in
ALife. Also report whether the ALife field has a documented norm AGAINST
tuning the environment to make an agent succeed, and cite anyone who has
named that practice as a methodological defect.

D4-02  PRIOR ART: QUARANTINING THE LEARNER FROM THE ENVIRONMENT

Find prior work that measured the topology or navigability of a search
space using ONLY blind, history-free processes, and deliberately withheld
any learning or history-conditioned algorithm until the topology result
was established. The distinguishing feature is treating environment
topology as the primary object of study rather than as a backdrop for an
agent. Search fitness-landscape analysis, local optima network analysis
(Ochoa, Tomassini, Verel), landscape metrics such as autocorrelation and
fitness-distance correlation, and the "algorithm-agnostic landscape
characterisation" literature. For each, state whether the landscape
analysis was performed BEFORE or AFTER an optimiser was applied, and
whether any paper enforced that ordering as a rule rather than an
accident. Report how large the largest such purely-blind study was, in
number of evaluations.

D4-03  PRIOR ART: CAUSAL ABLATION OF MUTATION OPERATORS

The programme tested "designer privilege" by removing one mutation
mechanism at a time and measuring whether navigability collapsed, with a
z-guarded threshold, rather than by showing a balanced histogram of
operator usage. Find prior work that performed single-operator causal
ablation on a variation operator set and reported the resulting change in
reachability, solve rate, or landscape connectivity. Cover the operator
contribution literature in genetic programming (crossover-vs-mutation
ablation studies), the "is crossover useful" debate, and any ALife study
that removed an instruction or mutation type and measured the effect on
evolvability. Critically: report whether anyone has argued that operator
USAGE FREQUENCY is a tautological measure of operator importance, since
that is the specific claim the programme makes. If nobody has said it,
say so plainly.

D4-04  PRIOR ART: BEHAVIOUR-ONLY DISTANCE WITH HUMAN LABELS AS RED TEAM

The programme defines all distances by intrinsic behavioural fingerprints
and forbids human semantic categories in the positive metric, then
reintroduces human taxonomy ONLY as an adversarial red team that can
weaken a result but never strengthen it. Find prior art for each half.
For behavioural distance: novelty search (Lehman and Stanley), behavioural
diversity in GP, phenotypic distance measures, and program-trace
similarity metrics. For the red-team half: any methodology in any field
where a secondary measurement is admitted with WEAKEN-ONLY authority --
it can invalidate a positive result but cannot create one. That
asymmetric-authority pattern is the part I most suspect is genuinely
unusual; look for it in clinical trials, adversarial evaluation, and
mechanistic interpretability as well as in ALife.

D4-05  PRIOR ART: OBSERVED-EDGE ORACLE AND NAVIGATION REGRET

The programme separates "the landscape is broken" from "the search
algorithm is weak" using an offline omniscient oracle that performs
reverse breadth-first search over ONLY the edges actually observed during
the run, yielding a navigation-regret quantity (for example S4: oracle
0.73 far-reach versus achieved 0.53). Find prior art for measuring the
gap between achieved search performance and what was reachable in the
observed transition graph. Cover local optima networks, search trajectory
networks (Ochoa et al. 2021 onward), regret formulations in bandits and
RL as an analogy only, and any ALife or GP work that reconstructed a
post-hoc reachability graph from logged transitions. State clearly
whether the observed-edge restriction (as opposed to a ground-truth or
sampled graph) has a precedent, since that restriction is what makes the
quantity a lower bound rather than a model.

====================================================================
TIER 2 -- SUBSTRATE PHYSICS (7 tokens)
====================================================================

D4-06  AVIDA AND TIERRA: WHAT THE PRIMARY SOURCES ACTUALLY SHOW

Verify or correct these attributions with primary sources. (1) Ray's
Tierra (1991-1992): what exactly was reported about mutation lethality,
dead code, and infinite loops, with numbers if the papers give them.
(2) Avida's design changes relative to Tierra: confirm whether Avida uses
total instruction decoding such that every genome is syntactically valid,
and cite where that design decision is stated. (3) Lenski, Ofria,
Pennock and Adami, "The evolutionary origin of complex features", Nature
2003: give the exact result on the EQU logic function, including how many
of the 50 populations evolved EQU, what happened when simpler functions
were not rewarded, and precisely what the paper claims about neutral and
deleterious intermediate steps. Quote the figures. State explicitly
whether the paper supports the claim that complex features are reachable
from random starts VIA NEUTRAL NETWORKS, or whether it supports a weaker
or different claim, because that distinction matters to us.

D4-07  INSTRUCTION-SET ERGONOMICS AND MUTATIONAL ROBUSTNESS

Collect the quantitative literature on how instruction-set design affects
mutational robustness in linear program representations. Specifically:
what fraction of single-instruction mutations are lethal, neutral, or
graded in (a) register machines with jumps and halts, (b) stack machines,
(c) tape or pointer machines of the Brainfuck family, (d) rewrite systems.
Give measured numbers where they exist. The programme measured viability
of 0.093 for its register machine versus 0.593 for its tape machine and
0.996 for its rewrite system, and I want to know whether those orderings
are consistent with, or contradicted by, published measurements. Cover
Banzhaf and Brameier on linear GP, work on Brainfuck or Turing-tape
genetic search, and any study that explicitly measures a "halting cliff"
or discontinuity caused by control-flow instructions.

D4-08  PUSH AND PUSHGP: TOTAL EXECUTION VERSUS FUNCTIONAL NAVIGABILITY

Report what Spector and collaborators actually demonstrated about the
Push language. Confirm the design claims: separate typed stacks, no-op
semantics on empty stacks, absence of syntax errors. Then find the
evidence on the SECOND half of the claim -- that eliminating syntactic
invalidity does not by itself produce functional navigability, and that
diversity-preserving selection such as lexicase selection was required.
I want the specific results showing PushGP performance with and without
lexicase selection, with numbers. Also report any published discussion of
structural or I/O bottlenecking in Push program spaces. This maps onto a
substrate that passed marginally at far-stratum hit rate 0.15 while
achieving 0.500 viability, so the question is whether total execution
semantics are known to be necessary but insufficient.

D4-09  REWRITE SYSTEMS: HIGH VIABILITY WITH DEAD ACCESSIBILITY

The programme's most surprising result: a string rewrite substrate with
0.996 viability and 11,717 distinct phenotype classes in which not one
observed viable path led from any start to any remote target across
roughly 1.5 million evaluations. Find the literature on evolutionary
search in term-rewriting, string-rewriting, lambda-calculus and
combinator spaces. Cover Fontana and Buss on AlChemy and lambda-calculus
algorithmic chemistry, Fontana's work on RNA folding landscapes for
contrast, and any measured result on fragmentation, chaotic sensitivity,
or unbounded divergence under syntactic perturbation in rewriting
systems. The precise question: is there published evidence that rewrite
systems combine HIGH validity with LOW accessibility, and does anyone
give a mechanism for that combination? Report any counterexample where a
rewrite substrate was successfully navigated by generic search.

D4-10  CELLULAR AUTOMATA RULE SPACES AS THE NEAREST NEIGHBOUR

A random rule table that is almost always viable and enormously diverse
yet unnavigable resembles the cellular-automata rule-space literature.
Report what is known quantitatively about the structure of CA rule space
under evolutionary search: Mitchell, Crutchfield and Hraber on evolving
CA for density classification and synchronisation, the "edge of chaos"
and lambda-parameter work and its subsequent critiques, and any measured
statement about whether CA rule space contains connected paths between
functionally distinct rules. I specifically want to know whether the
field has a name for, and measurements of, a space that is simultaneously
high-validity, high-diversity, and low-connectivity, and whether the
observed one-off "lottery phenotype" pattern -- a behaviour that appears
during a random walk and is then never reachable again -- has been
documented and named anywhere.

D4-11  BUDGET DEPENDENCE: WHEN IS A NAVIGATION FAILURE A REAL FAILURE

The register substrate was declared a navigation failure at 1,200
evaluations while its own observed-edge oracle said 0.41 of far episodes
had a path. So the failure is attributed to search weakness at that
budget, not proven fragmentation. Report the literature on how search
performance scales with evaluation budget in program spaces, and on how
to distinguish an insufficient budget from an inaccessible topology.
Cover run-length distributions and heavy tails in GP and SAT solving,
restart strategies, the theory of Las Vegas algorithm run-time
distributions (Hoos and Stutzle), and any principled published criterion
for declaring a region unreachable rather than merely unreached. I want
a concrete recommendation: what budget multiplier or statistical test
does the literature support for that inference?

D4-12  GENERIC SEARCH BASELINES: WHAT COUNTS AS UNPRIVILEGED

The programme used multiple generic history-free navigators, including a
random-walk floor which still reached 0.28 far-stratum hits on the tape
substrate. Report the literature on what constitutes a fair
"unprivileged" baseline search process in program spaces: random search,
random walk, hill climbing, (1+1) evolutionary algorithms, and the
theory of when these are provably comparable. Cover No Free Lunch and
its scope conditions and known misapplications, plus any work that
argues a random-walk baseline is the right null for a claim about
landscape structure. State whether a random walk reaching a substantial
fraction of remote targets is normally interpreted as evidence about the
LANDSCAPE or as evidence that the target set is too easy.

====================================================================
TIER 3 -- GENOTYPE-PHENOTYPE MAP THEORY (5 tokens)
====================================================================

D4-13  PHENOTYPE BIAS: IS AN UNPRIVILEGED SPACE POSSIBLE AT ALL

Report the theoretical and empirical results on universal bias in
genotype-phenotype maps. Cover Ard Louis, Sam Greenbury, Iain Johnston
and collaborators on bias in RNA secondary structure, polyomino
self-assembly, Boolean threshold networks and models of gene regulation,
including the arguments connecting phenotype frequency to algorithmic
complexity (the "simplicity bias" and coding-theorem-based arguments,
Dingle, Camargo and Louis). Give the actual functional forms and their
measured exponents. The decision this informs: whether the goal of an
"unprivileged" substrate is achievable in principle or only
asymptotically, and if only asymptotically, what the field's best
statement is of the residual bias that cannot be removed. Report any
dissenting position or failed replication.

D4-14  NEUTRAL NETWORKS AS NAVIGATION INFRASTRUCTURE

Report the quantitative results on neutral networks: the Schuster,
Fontana, Stadler and Hofacker RNA shape-space covering results, the
percolation thresholds for neutral network connectivity, and the claim
that the neutral network of a common phenotype is dense enough that a
small neighbourhood contains most other common phenotypes. Give the
numbers, including how far one must diffuse to encounter a given
fraction of phenotypes. Then report the counterweight: cases where
neutral networks are FRAGMENTED into disconnected components, and what
determines that. The specific question for us: is there a published,
measurable criterion that predicts in advance whether a given
computational substrate will have connected or fragmented neutral
networks, from properties of the substrate alone?

D4-15  ROBUSTNESS AND EVOLVABILITY: THE ALLEGED TRADE-OFF

Report the state of the robustness-evolvability relationship. Wagner's
argument that robustness can ENHANCE evolvability via neutral drift
across a large neutral network, the opposing intuition that robustness
suppresses phenotypic innovation, and the conditions under which each
holds. Give the concrete model results and their parameters. Apply this
to the observed pattern: a substrate at 0.996 viability (extremely
robust in the sense that almost every genotype runs) that is nonetheless
navigationally dead, versus one at 0.593 viability that navigates well.
Does the literature predict that relationship, contradict it, or is the
viability measure used here simply a different quantity from robustness
as the field defines it? Be precise about the definitional mismatch --
that is the most likely source of confusion.

D4-16  PHENOTYPE CENSUS STATISTICS AND UNSEEN MASS

The programme reports Good-Turing unseen mass of 0.929 for one substrate
and 0.99 for another, meaning the census sees a small fraction of the
viable phenotype diversity. Report how the ALife and GP literature
handles the statistics of sampling an unbounded or very large phenotype
space: species-richness estimators, Good-Turing and Chao estimators
applied to phenotype counts, and any published warning about comparing
diversity counts between substrates with different unseen mass. The
decision this informs: whether a comparison of 3,452 versus 11,717
observed phenotype classes across substrates is meaningful when the
unseen mass differs, and what the correct estimator or normalisation is.
If the honest answer is that such counts are not comparable, say so
directly.

D4-17  MEASURING ACCESSIBILITY: EXISTING FORMAL FRAMEWORKS

Report any existing formal framework for "accessibility" or "reachability"
of phenotypes under mutation, distinct from fitness-landscape ruggedness.
Cover accessible mutational paths and the Weinreich-style accessibility
literature in empirical fitness landscapes, accessibility percolation
theory (Hegarty, Martinsson, Nowak and others), and any graph-theoretic
formalisation of phenotype accessibility. Give the main theorems,
especially any threshold results on when accessible paths exist with
high probability. The question for us: is there an established formalism
we should be expressing our far-stratum hit rate inside, rather than a
bespoke metric? Name the closest formalism and state honestly how well
or badly our quantity maps onto it.

====================================================================
TIER 4 -- INPUTS TO A PHASE 2 DESIGN (3 tokens)
====================================================================

D4-18  DOES ACCUMULATED HISTORY HELP UNDER A FIXED BUDGET

The next phase would ask whether a learner with accumulated executable
history acquires behaviours more effectively than blind search under
identical metered budgets. Report the experimental designs the
literature uses for exactly this comparison, and their known failure
modes. Cover transfer learning evaluation under matched compute, curriculum
and open-ended learning evaluations, the "amortised search" framing,
program synthesis with learned libraries (DreamCoder and its successors,
library learning and abstraction), and any study that carefully equalised
compute between a history-using and a history-free arm. I want the
specific confounds that have burned people: budget accounting that
charges the two arms differently, and evaluation sets contaminated by the
history. Name each confound and the design that neutralises it.

D4-19  LIBRARY LEARNING: DOES A LEARNED ABSTRACTION CHANGE COMPUTATION

Report the evidence on whether learned reusable abstractions genuinely
change the cost or reachability of subsequent search, as opposed to
merely renaming compositions. Cover DreamCoder (Ellis et al.), library
learning and compression-based abstraction discovery, Stitch and related
efficient abstraction miners, and any ablation showing what happens when
the learned library is replaced by a random or frequency-matched library
of equivalent size. That ablation is the crux: I want every published
instance where a learned library was compared against a
complexity-matched or frequency-matched ARBITRARY library, with numbers.
Also report whether anyone has shown a learned-library advantage
disappearing once an ordinary memoisation or caching baseline is given
to the control arm.

D4-20  OPEN-ENDEDNESS AND THE DANGER OF THE METRIC BECOMING THE TARGET

Report how the open-ended evolution community defines and measures
open-endedness, and the documented cases where a proposed measure was
shown to be gameable or tautological. Cover the ALife open-endedness
workshop literature, novelty search and quality-diversity metrics such as
QD-score and coverage, and the critiques of each. I specifically want
documented instances where a diversity or novelty metric was satisfied by
a system that was doing nothing interesting, and how the field detected
that. The programme's own finding is that validity and diversity are
coordinates rather than objectives -- a substrate maximised both and
failed the only property that mattered. Report whether that lesson has
been stated before, by whom, and in what words, and whether any accepted
metric already encodes it.

====================================================================
CONSUMPTION NOTE
====================================================================

Every returned report must be logged to engine/queues/CONSUMPTION.jsonl
with the behaviour delta it produced, per the standing rule that a
document which changes no behaviour is substrate rot. A report that
returns NOT FOUND for a prior-art fire is a HIGH-value result: it is the
only evidence that can support a novelty claim, and it is worth more than
a report that lists ten loosely-related papers.

Fires D4-01 through D4-05 are attempts to KILL a novelty claim made about
this programme by a frontier model. Convergent praise from a language
model is corpus gravity, not validation. If any of the five returns a
clean prior-art hit, that is the most valuable outcome in the batch and
the claim gets retired the same day.
