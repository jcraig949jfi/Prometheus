"""Emit the ERGON_AVIDA2003_HISTORICAL_DEEP_DIVE_V0 document set."""
import json, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 'ERGON_AVIDA2003_HISTORICAL_DEEP_DIVE_V0')
os.makedirs(D, exist_ok=True)


def w(name, text):
    open(os.path.join(D, name), 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote', name)


w('A_PRIMARY_SOURCE_LEDGER.md', """# A - PRIMARY SOURCE LEDGER

Every row states what was actually touched. Nothing is promoted to
PRIMARY_SOURCE_READ without an exact locator (gate P3).

## READ

| Source | Locator | Class | What it established |
|---|---|---|---|
| Supplementary Information to Lenski, Ofria, Pennock & Adami, "The evolutionary origin of complex features", Nature 423:139-144 (2003) | doi:10.1038/nature01568 ; ESM file `41586_2003_BFnature01568_MOESM1_ESM.pdf` ; sha256 970b2711762cf61fa87f4a226f46a32f213d06ddad33361e9284fe79a5939e7a | PRIMARY_SOURCE_READ + ARTIFACT_IN_HAND | 26-instruction table; 1- and 2-input logic truth tables with minimum-NAND counts; 32-bit credit rule; shortest hand-written EQU program; COMPLETE line of descent, pd 0-111, with genomes |
| Avida 2.2 `source/support/environment.cfg` | inside avida-src-devel-2.2.tar.gz, sha256 2e5384147bec575602c6b3a271a3d020ee6a9af1a082d2dc578fc0a0cfee960d | ARTIFACT_IN_HAND | nine REACTION lines, reward exponents, type=pow, max_count=1 |
| Avida 2.2 `source/support/inst_set.default` | same tarball | ARTIFACT_IN_HAND | 26 instructions, order identical to the supplementary |
| Avida 2.2 `source/main/landscape.hh` and `landscape.cc` | same tarball | ARTIFACT_IN_HAND | the HISTORICAL mutational-landscape analyzer. Decisive for D. |
| Nature article landing page | https://www.nature.com/articles/nature01568 | ARTIFACT_IN_HAND (landing page only) | title, DOI, supplementary locator, and confirmation that the full text is paywalled |

## NOT READ - and it matters

| Source | Status | Consequence |
|---|---|---|
| Main paper full text (Methods) | PAYWALLED. Landing page carries institutional-access and purchase markers. | Population size, world geometry, mutation rates, replicate count and seeds are all UNSPECIFIED. See E. |
| `myxo.css.msu.edu/papers/nature2003/` - the paper's OWN data repository, named in the supplementary | DEAD. http returns 404, https returns 501. | The line of descent as distributed (345 genotypes), the functional-genomic arrays, the configuration files and any population dumps are not directly retrievable. |
| Wayback snapshot of that repository | EXISTS AND CONFIRMED AVAILABLE: the availability API returns status 200 for timestamp 20211122232656. Retrieval BLOCKED this session by HTTP 429 rate limiting after repeated CDX queries. | This is the single highest-value unblocking action. It is a throttling problem, not an absence. |
| SourceForge CVS repository (`cvs.sourceforge.net:/cvsroot/avida`, tool live at https://sourceforge.net/p/avida/cvs/) | NOT EXPLORED | The only plausible route to 2003-era source revisions. The 2.2 tarball's own `CVS/Root` file names this server, so the linkage is verified, not guessed. |

## Negative results of the artifact hunt - recorded because they bound the specimen

- **GitHub `devosoft/avida` does not contain the 2003 source.** Repository created 2010-11-05; earliest commit 2010-12-22; only tags are 2.12.4 and 2.14.0. It is a later lineage of the same software, not the specimen.
- **SourceForge holds no pre-2005 release.** The project was created 2002-02-15, but the oldest surviving file release is `avida-src-devel-2.2.tar.gz` dated 2005-02-14 - roughly 21 months AFTER the experiment.
- **Software Heritage origin search for "avida" returned unrelated repositories.** No archived 2003-era Avida origin was found by name search.

Consequence: **no artifact recovered in this pass is contemporaneous with the
experiment.** The supplementary is the only primary source, and it is a
description of the experiment rather than the software that ran it.
""")


w('C_HISTORICAL_PHYSICS_SPEC.md', """# C - HISTORICAL PHYSICS SPEC

What the world was, to the precision the evidence supports. Certainty classes
in E; this document states the physics and flags where it is version-skewed.

## Substrate

Self-replicating programs on a 2D grid, competing for CPU time. A genome is a
string over a **26-letter instruction alphabet** (VERIFIED_EXACT: the
supplementary table and `inst_set.default` agree instruction-for-instruction
and in order). Replication is by explicit `h-alloc` / `h-copy` / `h-divide`
head operations, so self-replication is encoded in the genome and can be
broken by mutation.

## The rewarded phenotype

Nine Boolean logic tasks, rewarded once each (`requisite:max_count=1`):

    NOT  NAND  AND  OR_N  OR  AND_N  NOR  XOR  EQU

To be credited with a task an organism must return the correct value for **all
32 bit-wise problems** in the series (supplementary II). Partial credit does
not exist. This is a sharp threshold and it matters for any accessibility
metric: the phenotype is a 9-bit vector with no intermediate states.

**ECHO is describable but not rewarded.** The supplementary lists it among the
one-input operations; it appears in neither the nine-function legend nor
`environment.cfg`. Any reconstruction that rewards ECHO is not this specimen.

## The reward function

`environment.cfg` gives each reaction `process:value=v:type=pow`. The nine
values are

    NOT 1   NAND 1   AND 2   OR_N 2   OR 3   AND_N 3   NOR 4   XOR 4   EQU 5

and they are **exactly** the minimum number of NAND operations required to
compute each function, as published in supplementary II and stated there to
have been proven by exhaustive search. Merit multiplier is therefore 2^v, so
EQU is worth 32x and the nine rewards span a 32-fold range.

This identity - reward exponent equals minimal NAND depth - is the single most
important piece of physics recovered in this pass, because it means the reward
landscape is a **computational-depth ladder**, not an arbitrary bonus schedule.

## Selection

Merit multiplies replication rate; organisms compete for CPU cycles. A genome
that performs a rewarded task replicates faster and displaces neighbours. The
paper's central point is that intermediates on the path to EQU were sometimes
individually deleterious, which is visible directly in the recovered lineage:
of 111 transitions on the line of descent, many carry relative fitness below
1.00.

## Version skew - stated, not hidden

Everything in the two config files above is `VERIFIED_EXACT` **for Avida 2.2
(2005-02-14)**. No 2003-era source or configuration has been recovered. The
supplementary independently confirms the instruction set, the nine tasks, the
32-bit credit rule and the minimum-NAND values, which is why those rows are
promoted to VERIFIED_EXACT for 2003. The functional form `type=pow` and the
`max_count=1` requisite are confirmed only for 2.2.

## What is NOT specified

Population size, world geometry, point/insertion/deletion/copy mutation rates,
replicate count, seeds, and the Avida version itself. See E. A faithful re-run
is therefore not currently possible and any re-run would be
`APPROXIMATE_RECONSTRUCTION`.
""")


w('D_HISTORICAL_DETECTOR_PROFILE.md', """# D - HISTORICAL DETECTOR PROFILE

The historical instrument treated as an artifact. This is the most important
document in the pass, because it contains a finding that inverts the directive's
working assumption.

## THE HEADLINE: Avida already had a mutational-landscape analyzer

`source/main/landscape.hh` / `landscape.cc` in the recovered 2.2 tree define
`cLandscape`, which enumerates a genome's mutational neighbourhood and reports:

    GetProbDead()   fraction of one-step mutants that cannot replicate
    GetProbNeg()    fraction deleterious
    GetProbNeut()   fraction neutral (within an explicit neut_max band)
    GetProbPos()    fraction beneficial
    GetAveFitness() / GetAveSqrFitness()
    pos_epi_count / neg_epi_count / dead_epi_count   two-step epistasis
    Process(int in_distance = 1)   distance is a PARAMETER, so k=2 is supported
    ProcessDelete() / ProcessInsert()   insertion and deletion landscapes

So the original investigators could, and did, instrument the local mutational
neighbourhood - including two-step and indel neighbourhoods. **The directive's
premise that one-step neighbourhood analysis is a modern addition is wrong, and
recording that is worth more than the metric would have been.**

## THE ACTUAL BLIND SPOT, located precisely

`landscape.cc` touches `cPhenotype` at exactly four places, and every one of
them reads a scalar:

    line 136  phenotype.GetFitness()
    line 137  phenotype.GetMerit()
    line 138  phenotype.GetGestationTime()
    line 763+ merit, gestation, fitness for output

`landscape.hh` contains **zero** references to tasks. The historical landscape
analyzer is **fitness-valued, not phenotype-partitioned**. It can tell you what
fraction of your neighbours are dead, worse, the same or better. It cannot tell
you **which logic functions** those neighbours gained or lost, nor how many
distinct phenotypes are reachable, nor how that reachable set is distributed.

That gap - and only that gap - is what P-MED, R1 and H1 add.

## The fourteen observables (directive section 4)

| # | Observable | Class | Evidence |
|---|---|---|---|
| 1 | fitness | HISTORICALLY_MEASURED | `cPhenotype::GetFitness`, reported per lineage step in supplementary IV |
| 2 | gestation time | HISTORICALLY_MEASURED | `GetGestationTime`, used in landscape output |
| 3 | logic-function phenotype | HISTORICALLY_MEASURED | 9-bit vector printed for every genotype on the line of descent |
| 4 | mutation effects | HISTORICALLY_MEASURED | `cLandscape` dead/neg/neut/pos |
| 5 | successful lineage ancestry | HISTORICALLY_MEASURED | the entire line of descent is published with genomes |
| 6 | deleterious/neutral ancestral mutations | HISTORICALLY_MEASURED | relative fitness per step in supplementary IV; the paper's central claim |
| 7 | extinct sibling lineages | HISTORICALLY_MEASURABLE_BUT_NOT_REPORTED | Avida can dump populations; none survives in a recovered artifact |
| 8 | local phenotype reachability around arbitrary contemporaries | REQUIRES_MODERN_RERUN | needs contemporaries (absent) AND phenotype partitioning (absent) |
| 9 | distribution of phenotypes reachable from a genotype | **NOT MEASURED, THOUGH THE MACHINERY EXISTED** | `cLandscape` enumerated the neighbourhood but classified it by fitness only. This is the genuine addition. |
| 10 | future acquisition probability from matched contemporaries | REQUIRES_MODERN_RERUN | no artifact supports it; needs forks |
| 11 | population-wide base rate of apparent stepping stones | REQUIRES_MODERN_RERUN | requires population dumps or reruns |
| 12 | change in the mutational neighbourhood before EQU | RECOVERABLE_FROM_SURVIVING_DATA (lineage only) | the 112 recovered genomes can each be landscaped; contemporaries cannot |
| 13 | acquisition cost of subsequent capabilities | REQUIRES_MODERN_RERUN | |
| 14 | failure trajectories of lineages that approached but did not reach EQU | NOT_IDENTIFIABLE from surviving artifacts | this is the survivorship gap; see K |

## Recovered detector strengths Prometheus should adopt (directive section 24)

1. **Distance-parameterised landscape enumeration.** `Process(in_distance)`
   generalises to k>1 with the same accounting. Prometheus's own Gen-1B
   mutational-redundancy work sampled neighbourhoods ad hoc; Avida had a
   parameterised, reusable enumerator in 2005.
2. **Indel landscapes as first-class.** `ProcessDelete` / `ProcessInsert` are
   separate entry points. Prometheus's D-5 substrate has INSERT-complete
   physics and never separated indel from substitution neighbourhoods.
3. **Explicit neutrality band.** `neut_max` makes "neutral" a declared
   parameter rather than an implicit equality test.
4. **Epistasis counters.** pos/neg/dead epistasis at two steps, already
   aggregated.

These go to O as detector parts.
""")


w('F_LINEAGE_RECOVERY_REPORT.md', """# F - LINEAGE RECOVERY REPORT

## What was recovered

The **complete line of descent of the case-study population through the origin
of EQU**, extracted from supplementary section IV and parsed to
`artifacts/lineage_of_descent.jsonl`.

    records                112
    phylogenetic depth     0 - 111
    fields per record      pd, born (update), functions (9 bits), fit
                           (relative to immediate parent), genome, len
    ancestor (pd 0)        rucavccccccccccccccccccccccccccccccccccccutycasvab
                           50 instructions, 0 of 9 functions
    T_EQU                  pd 111, birth update 27450
    genome length          50 min, 61 max
    functions at pd 111    6 of 9

Every genotype on the successful lineage is therefore available as an exact
string over the verified 26-letter alphabet. For the purposes of a *static*
accessibility analysis this is a complete specimen.

## What was NOT recovered, and it is the binding constraint

**No contemporary genotypes.** The supplementary publishes the line of descent
only. It contains no organism that was alive at the same update and did not
lead to EQU.

The directive's first scientific target (section 5) is a *matched* comparison of
`g_succ(t)` against 3-5 `NON_EQU_DESCENDANT_CONTROL` genotypes at the same
generation with matched fitness, genome length and task count. **None of those
controls exists in any artifact recovered in this pass.**

Three routes to controls, in order of fidelity:

1. **Recover the myxo repository from the Wayback Machine.** The supplementary
   states that the full line of descent and "functional-genomic arrays for all
   345 genotypes" live there. If population dumps or `detail-*.spop` files were
   also posted, contemporaries come with them. Snapshot confirmed to exist
   (timestamp 20211122232656, status 200); retrieval blocked this session by
   rate limiting. **Cheapest and highest fidelity.**
2. **Recover 2003-era source and configuration via SourceForge CVS**, then
   re-run to generate contemporaries. This yields controls but they are
   RECONSTRUCTED, not historical, and every UNSPECIFIED parameter in E becomes
   an assumption.
3. **Use the lineage against itself** - compare `g_succ(t)` to `g_succ(t')` for
   t' far from EQU. This needs no new artifact but it is **not** a matched
   control and would answer a different, weaker question.

## An unexplained discrepancy, recorded rather than resolved

The supplementary says the distributed line of descent contains **345
genotypes**; the table printed in the same document contains **112**, ending at
EQU. The likely reading is that the printed table is truncated at the origin of
EQU (its own title says "through the origin of the EQU function at step 111")
while the distributed file continues past it. That is a plausible reading, not
a verified one, and it is flagged as a live archaeology question rather than
assumed.

## Fidelity caveat on the parse

`lineage_of_descent.jsonl` is a DERIVED artifact: its hash is of our text
extraction, not of a historical file. The regex requires a well-formed row
(depth, update, nine bits, fitness, genome) and silently skips malformed lines,
so a systematic extraction failure would present as missing rows rather than as
an error. 112 consecutive depths 0-111 with no gaps is evidence against that,
but the parse has not been validated against an independent rendering of the
PDF.
""")


w('G_MATCHED_CHECKPOINT_DESIGN.md', """# G - MATCHED CHECKPOINT DESIGN

## The timescale problem, and the choice frozen here

The directive proposes checkpoints at `T_EQU - 100`, `-50`, `-10` and permits
adjustment "if the actual Avida timescale makes them inappropriate", provided
the change is justified and **frozen before examining any accessibility
metric**. This section is that freeze. No accessibility metric has been
computed at the time of writing.

The recovered lineage makes the ambiguity concrete. EQU appears at
**phylogenetic depth 111**, born at **update 27450**. Those are two different
clocks and they are wildly non-linear with respect to each other: the first 17
depth steps span updates 0-1118, while single later steps span thousands of
updates.

Measured in **updates**, `T_EQU - 100` = update 27350, which on this lineage is
well inside the final depth step - all three proposed checkpoints would collapse
onto one or two genotypes. That is inappropriate.

Measured in **phylogenetic depth**, the checkpoints are well separated and each
names a distinct genotype.

**FROZEN DECISION: checkpoints are defined in phylogenetic depth.**

    checkpoint A   pd 101   ( T_EQU - 10 )
    checkpoint B   pd  61   ( T_EQU - 50 )
    checkpoint C   pd  11   ( T_EQU - 100 )

Justification: depth is the unit in which the historical record is published,
it is the unit in which mutations accumulate, and it is the only one of the two
clocks that yields three separated genotypes. Updates remain recorded for every
checkpoint so the wall-clock separation is never lost.

## Focal genotypes

`g_succ(t)` is read directly from `lineage_of_descent.jsonl` at pd 101, 61, 11.
All three are VERIFIED_EXACT strings.

## Controls

`g_dead(t)` - class `NON_EQU_DESCENDANT_CONTROL`, 3-5 per checkpoint, matched
on as many as possible of: same update window, fitness, genome length, task
count, no EQU, not ancestral to EQU within the observation horizon,
genealogically close.

**These do not exist in any recovered artifact.** See F. Until they are
recovered, G is a design and not a runnable protocol.

The class name is deliberate: they are *not* "dead ends" until descendant
history establishes that status, and with a single case-study population that
status may never be establishable.

## The matched-control estimator, frozen now

Per checkpoint, the contrast is

    delta_X(t) = X( g_succ(t) )  -  median over controls of X( g_dead(t) )

**Median, not mean**, frozen before any metric is computed, because control
sets of size 3-5 are small enough that a single lethal-heavy outlier would
dominate a mean. This is recorded here specifically so it cannot become an
analysis degree of freedom later.
""")


w('H_PMED_SPEC.md', """# H - PMED SPEC (phenotypic mutation-effect distribution)

## Neighbourhood definition

For a genome of length L over the verified alphabet of A = 26 instructions, the
one-step substitution neighbourhood is every valid single point substitution at
every site:

    |M1(g)| = L * (A - 1) = L * 25

For the recovered lineage (L between 50 and 61) that is **1250 to 1525 mutants
per genotype**. Exhaustive enumeration is trivially affordable; see L.

**Indels are NOT folded into M1.** The historical mutation operator's
insertion and deletion rates are UNSPECIFIED (see E), so whether indels were
important in 2003 is unknown. Avida's own analyzer treats them as separate
entry points (`ProcessInsert`, `ProcessDelete`) and this spec follows that
precedent: if indel rates are recovered, indel neighbourhoods are reported
**separately**, never silently merged.

## Outcome classes

Each mutant is executed in a faithful analysis environment, yielding viability
and a 9-bit phenotype `P(m)`. Classes are mutually exclusive and exhaustive
over viable mutants:

    LETHAL   cannot complete replication under the historical viability
             criterion (Avida's own test-CPU colony test)
    SILENT   P(m) == P(g).  Fitness, merit or gestation may still differ -
             this is a PHENOTYPIC classification, not a fitness one
    LOSS     P(m) is a strict subset of P(g)         (bits lost, none gained)
    GAIN     P(m) is a strict superset of P(g)       (bits gained, none lost)
    ALT      at least one bit gained AND at least one lost

Exhaustiveness argument over 9-bit masks: for viable m, either P(m) == P(g)
(SILENT) or they differ. If they differ, let `gained = P(m) & ~P(g)` and
`lost = P(g) & ~P(m)`; at least one is non-zero. The three cases (gained only,
lost only, both) are LOSS/GAIN/ALT. The partition is total.

**This must be property-tested exhaustively over the complete 512 x 512 mask
space before any historical genome is classified**, per directive section 21.
Do not trust the argument above; test it.

## Reported quantities

Per genotype: `f_lethal`, `f_silent`, `f_loss`, `f_gain`, `f_alt`, each over
the full L*25 denominator, plus raw counts.

## What P-MED adds over the historical detector

`cLandscape` already reports dead / neg / neut / pos fractions over the same
neighbourhood. P-MED does **not** add neighbourhood enumeration - Avida had it.
P-MED replaces the **fitness-valued** classification with a
**phenotype-partitioned** one. The honest statement of novelty is:

    the historical instrument asked "how good are my neighbours?"
    P-MED asks "what can my neighbours DO that I cannot?"

Those differ whenever fitness is not a monotone function of the phenotype
vector, which under a 2^v reward ladder with nine tasks it is not.
""")


w('I_RPD_SPEC.md', """# I - RPD SPEC (reachable phenotype diversity)

## Definitions

    Omega1(g)  the SET of distinct viable phenotype vectors reachable under one
               point substitution, EXCLUDING P(g) itself
    R1(g)      = |Omega1(g)|                                  reachable richness
    H1(g)      = - sum_j p_j log2 p_j                         reachable entropy

## The denominator, frozen before any comparison

`p_j` is the empirical probability that a random valid one-step point mutant
produces phenotype j. Three denominators are defensible and they answer
different questions:

    (a) ALL mutations          L*25, lethals included as their own outcome
    (b) VIABLE mutations       lethals excluded
    (c) NOVEL VIABLE mutations viable and P(m) != P(g)

**PRIMARY DEFINITION, FROZEN: (b) VIABLE mutations.**

Reason, fixed in advance: (a) makes H1 dominated by the lethal fraction, which
P-MED already reports separately as `f_lethal`, so (a) would double-count the
single largest and least interesting component. (c) discards the silent class,
which is precisely the robustness signal that a precursor hypothesis might turn
on. (b) is the only choice that keeps silence and novelty in the same
distribution while not being swamped by lethality.

All three are cheap, so **all three are reported**; only (b) enters any
preregistered comparison. Denominator choice is hereby removed from the
analysis degrees of freedom.

## Two-step accessibility - bounded, sampled, never exhaustive

Exhaustive k=2 is (L*25)^2 / 2, roughly 1.2 million ordered pairs at L=61 -
affordable in isolation but not across checkpoints x controls x replicates once
each mutant needs a full Avida colony test. It is therefore SAMPLED.

    N2                    frozen sample size, set after the convergence check
    path distribution     uniform over ordered pairs of distinct sites, with
                          the second substitution drawn uniformly from the 25
                          alternatives at its site
    repeated mutation     a site may not be hit twice; same-site double
                          substitutions are excluded and that exclusion is
                          reported as a fraction
    reversions            a second mutation restoring the original instruction
                          is impossible under the above rule and so cannot
                          silently inflate SILENT
    viability             a path whose FIRST step is lethal is still evaluated
                          at step two, because Avida viability is a property of
                          the final genome, not of a trajectory
    seed                  deterministic, recorded per genotype

Estimates `R2*` and `H2*` are reported with bootstrap confidence intervals.

**Convergence is checked BEFORE labels are revealed**, and N2 is frozen for all
genotypes simultaneously. N2 may not be increased for a genotype that "looks
interesting" - that is the specific abuse this paragraph exists to forbid.

## Interpretive discipline

H1 is attractive and dangerous. High entropy is not evolvability: a genotype
with many reachable but useless phenotypes scores high and may go nowhere. R1
and H1 are **local accessibility descriptors**, not fitness proxies and not
evolvability scores. Their only job in H1A is to serve as candidate detectors.
If they show no predictive structure, the correct response is to stop, not to
add a fourth descriptor.
""")


w('J_PROSPECTIVE_BLIND_PROTOCOL.md', """# J - PROSPECTIVE BLIND PROTOCOL

The history already happened, so the analysis cannot be prospective. The
DETECTOR can still be tested against hidden outcomes, and that is the point:
otherwise we tune a microscope to a particle whose coordinates we already know.

## Procedure

1. **Assemble.** Build the genotype pool: focal `g_succ` at the three frozen
   checkpoints plus all matched controls. Assign each an opaque identifier
   (`GT-0001` ...) from a keyed shuffle. Write the identifier-to-label map to a
   sealed file that the analysis stage does not read.
2. **Freeze the metric code.** P-MED, R1, H1, R2*, H2* implementations hashed
   and committed before any historical genome is classified. Property tests over
   the full 512 x 512 mask space green.
3. **Compute.** Produce the metric table keyed only by opaque identifier.
   Commit it.
4. **Convergence check** on N2 against opaque identifiers only.
5. **Unseal.** Join labels. Compute the frozen `delta_X(t)` contrasts.
6. **Report** the metric table and the contrast table as separate artifacts, in
   that order, with the commit of step 3 preceding the commit of step 5 in the
   git history. The ordering is the evidence that step 3 was not tuned.

## Honest limits of this blinding

- The analyst knows the *design*: that some genotypes are precursors and some
  are not, and roughly how many of each. Only the assignment is hidden.
- The genomes themselves carry information. A sufficiently determined analyst
  could recognise the ancestor by inspection, and pd-111 sits one step from EQU.
  Blinding raises the cost of unconscious tuning; it does not make it impossible.
- With one historical population the blind is small: three focal genotypes.
  This is a **CASE STUDY**, and section 14 of the directive requires that label
  unless multiple independent runs are recovered.

Stating these limits is not a formality. A blind protocol described without its
failure modes is theatre.
""")


w('K_SURVIVORSHIP_CONTROL_PLAN.md', """# K - SURVIVORSHIP CONTROL PLAN

The focal lineage is selected precisely because it succeeded. Every winner is
special retrospectively. The question is not "was the winner special?" but
"was the candidate signature enriched in branches with greater future
acquisition probability under controlled rerun?"

## The structural problem for THIS specimen

Only one population is recovered, and only its successful line of descent. That
is the worst possible starting position for survivorship control: the sample is
the survivor, and nothing else survives.

Consequently **K6 of the kill criteria is currently ACTIVE by default**: any
result from today's evidence is dominated by one historical run. This is not a
risk to be monitored; it is the present state.

## Controls, in the order they become possible

| Control | Requires | Status |
|---|---|---|
| N1 fitness-matched contemporaries | population dumps | BLOCKED (no contemporaries) |
| N2 task-profile-matched contemporaries | population dumps | BLOCKED |
| N0 random contemporaries, matched only on generation | population dumps | BLOCKED |
| N3 shuffled phenotype labels after evaluation | nothing - runs on the lineage alone | AVAILABLE NOW |
| N4 temporal label shuffle within run | the lineage alone | AVAILABLE NOW |
| N5 post-EQU lineage members, to confirm the detector is not merely detecting EQU possession | the distributed 345-genotype file (we hold only 112, ending at EQU) | BLOCKED pending Wayback |
| N6 conditions where EQU is unrewarded | a faithful rerun | BLOCKED (parameters UNSPECIFIED) |

Two of seven controls are available today, and both are label-permutation
nulls that test the detector's own noise floor rather than survivorship. **The
controls that actually address survivorship all require artifacts we do not
have.**

## What that implies for sequencing

Running H1A now would produce a metric table on three focal genotypes with no
matched controls and no base rate. It could not distinguish a precursor
signature from an ordinary property of any genome at that depth. That is not a
weak experiment; it is an uninterpretable one.

N5 deserves particular emphasis. Without post-EQU genotypes we cannot check
the most banal failure mode: that the detector fires simply because a genotype
is close to already holding EQU. K9 exists for exactly this and is currently
untestable.
""")


w('L_COMPUTE_MODEL.md', """# L - COMPUTE MODEL

No estimate here is a recollection. Where a number is not benchmarked it is
labelled EST and the reason is given. The directive forbids the phrase "one
CPU-day" surviving without benchmark evidence, and none appears.

## Measured today

    supplementary PDF retrieval + text extraction     < 5 s
    Avida 2.2 tarball retrieval                       1,664,380 bytes, ~4 s
    tarball extraction                                < 3 s
    lineage parse (112 records)                       < 1 s
    provenance gates over 6 artifacts                 < 1 s

## NOT measured, and dominant

**The cost of evaluating one Avida genome is unbenchmarked**, because Avida 2.2
has not been compiled. Every downstream estimate therefore depends on an
unmeasured constant, and the honest statement is that the compute model is
incomplete until that constant exists.

    e = seconds per genome evaluation (colony test to viability + phenotype)
        STATUS: UNMEASURED

## Static analysis scale, in units of e

    mutants per genotype        L * 25, i.e. 1250 (L=50) to 1525 (L=61)
    focal genotypes             3 checkpoints
    controls                    3-5 per checkpoint  -> 9-15 additional genotypes
    genotypes in H1A            12-18
    one-step evaluations        ~1250-1525 each, so 1.5e4 to 2.7e4 total
    k=2 sampled                 N2 per genotype, N2 TBD after convergence

**H1A therefore costs order 10^4 genome evaluations.** Even at a pessimistic
e = 10 ms that is minutes, and at e = 1 ms it is seconds. The static stage is
not compute-bound under any plausible e, which is why the directive is right
to insist on it before any replay forest.

## The build risk, which is the real cost

Avida 2.2 is 2005-era C++ with a CVS-era build system (bjam / autotools
fragments visible in the tree). Compiling it on a modern toolchain is the
single largest unquantified engineering cost in this pass, and it is a
**binary** risk: either the historical evaluator runs, or P-MED must be
implemented against a reimplementation, which immediately raises K8
(reconstruction fails to reproduce the historical phenomenon).

Recommended sequencing: attempt the 2.2 build FIRST, before writing any metric
code, because the outcome determines whether the analysis uses the historical
evaluator or a surrogate. That is a fork in the whole programme, not a detail.

## H1B, for scale only - NOT authorised

Forked descendant populations would multiply by K replicates x B budget x
checkpoints x controls. With population size, mutation rates and run length all
UNSPECIFIED, no credible estimate is possible. Any H1B number quoted today
would be invented. None is quoted.
""")


w('M_FAILURE_COORDINATE_SPEC.md', """# M - FAILURE COORDINATE SPEC

The Historical Collider cares about failures. This spec derives failure
coordinates that Avida's physics actually supports, and refuses to invent
semantics it does not.

## Supported coordinates

| Coordinate | Support | Source |
|---|---|---|
| cannot replicate (lethal) | YES | Avida colony test; `cLandscape` dead_count |
| fitness decrease | YES | `GetFitness` on the mutant vs parent |
| gestation increase | YES | `GetGestationTime` |
| task loss | YES | 9-bit phenotype comparison (LOSS / ALT in H) |
| failed task gain | YES, as the complement of GAIN over viable mutants |
| phenotype unchanged (silent) | YES | SILENT in H |
| phenotype lateral move | YES | ALT in H - gain and loss simultaneously |
| offspring non-viability | PARTIAL | Avida distinguishes an organism that cannot divide from one that produces a non-viable child; the recovered accessors do not expose this split directly and it needs source work before use |

## NOT supported - do not invent

Avida has no notion of "almost solved a task": the 32-bit credit rule is a hard
threshold (see C). There is therefore **no partial-credit failure coordinate**,
and any near-miss metric would be a modern imposition on the specimen rather
than a recovered observable. Prometheus's own D-5 work used bitwise-Hamming
partial credit to restore a gradient; **that move is not available here** and
attempting it would change the specimen.

## The narrow tectonic test

Do not call every neighbourhood difference a failure-landscape bump. The narrow
question is:

    does the geometry of UNSUCCESSFUL neighbouring mutations change before a
    later acquisition transition?

and it must be run against cheap conventional predictors - fitness, genome
length, task count, gestation, total viability fraction. If those predict
future EQU equally well, failure geometry adds nothing and that is the result.

This is K4, and it is the kill criterion most likely to fire, because task
count in particular is a strong and nearly free predictor: a genotype holding
six of nine functions is manifestly closer to EQU than one holding zero. Any
accessibility signal must beat that trivial baseline before it means anything.
""")


w('N_SFE_TRANSLATION_PLAN.md', """# N - SFE TRANSLATION PLAN

Do not port Avida into SFE. First reproduce the specimen faithfully; then state
what SFE would add, and where it cannot represent the specimen honestly.

## Mapping

| Historical primitive | SFE equivalent | Fidelity |
|---|---|---|
| Avida world (grid of CPUs competing for cycles) | world identity | CLEAN, provided population size and geometry are recovered - both UNSPECIFIED today |
| genome: string over 26 instructions | genotype identity | CLEAN. Content-addressed hash of the instruction string. |
| point substitution | mutation event | CLEAN |
| insertion / deletion | mutation event, SEPARATE class | CLEAN, but rates UNSPECIFIED |
| parent -> offspring on divide | lineage edge | CLEAN |
| 9-bit rewarded logic vector | phenotype observation | CLEAN, and the natural SFE observable |
| merit = 2^(sum of reward exponents) | derived scalar on the phenotype | CLEAN once the reward table is pinned |
| colony test outcome (viable / not) | failure coordinate | CLEAN |
| update | compute budget / clock | **LOSSY.** An Avida update is a population-wide CPU allocation, not a per-organism step. SFE budgets in Prometheus are per-organism evaluations. These are not interconvertible without population size. |
| phylogenetic depth | checkpoint | CLEAN, and G shows it is the better clock |
| random seed | replay seed | CLEAN in principle; no historical seed survives |
| population dump | fork point | CLEAN |
| ancestral reversion | ablation | CLEAN |
| artifact hash | artifact hash | CLEAN |

## Where SFE cannot faithfully represent the specimen

1. **The update clock.** See above. Any SFE budget claim about this specimen
   must be stated in evaluations and must NOT be silently relabelled as updates.
2. **Population-level selection.** Avida's selection is spatial and
   CPU-allocation-based. Prometheus's D-5-class consumers use a fixed-size
   population with tournament selection. These are different physics, and a
   translation that quietly swaps them produces a different experiment.
3. **The hard 32-bit task threshold.** SFE substrates in Prometheus have used
   graded distance objectives. Grading this specimen would change it (see M).

## What SFE would genuinely add

Replication at a scale the original could not reach: many independent
populations from a common checkpoint, with per-organism lineage and failure
coordinates retained. That is the whole value proposition, and it is worth
stating that it is a **statistical** addition, not a resolution one - Avida's
own analyzer already resolved the one-step neighbourhood (see D).

## Recommendation

**Do not build an SFE world for this specimen yet.** With seven physics
parameters UNSPECIFIED, an SFE port would encode assumptions as if they were
history. Recover the configuration first.
""")


w('Q_KILL_CRITERIA.md', """# Q - KILL CRITERIA

A killed particle is a successful archaeological result. Each criterion below
is stated so that it can fire.

| # | Criterion | Current status |
|---|---|---|
| K1 | Local accessibility descriptors do not distinguish successful precursors from matched controls | UNTESTED - no controls exist |
| K2 | Any descriptor difference disappears under lineage / task / fitness matching | UNTESTED |
| K3 | The descriptor predicts historical labels but not future acquisition under modern reruns | UNTESTED - reruns blocked, parameters UNSPECIFIED |
| K4 | Cheap conventional metrics (fitness, genome length, task count, gestation, viability fraction) predict acquisition equally well | UNTESTED. **Most likely to fire.** Task count alone is a strong free predictor - a genotype holding six of nine functions is visibly nearer EQU. |
| K5 | Ablation / reversion fails to causally alter the signal | UNTESTED |
| K6 | Results dominated by one historical run / survivorship | **ACTIVE NOW.** One population, successful lineage only. See K. |
| K7 | Historical reconstruction ambiguity is large enough to determine the result | **PARTIALLY ACTIVE.** Seven physics parameters UNSPECIFIED. Static analysis on exact recovered genomes is unaffected; anything requiring a rerun is fully exposed. |
| K8 | Modern reconstruction fails to reproduce the known historical phenomenon | UNTESTED - Avida 2.2 not yet compiled |
| K9 | Signal is merely the direct consequence of already holding a near-EQU task combination | **UNTESTABLE TODAY.** Requires post-EQU genotypes (N5), which are in the 345-genotype distributed file we do not hold. |
| K10 | Compute requirements make adequate replication infeasible | NOT FIRING for H1A (order 10^4 evaluations). Unknown for H1B. |

## The two that matter most right now

**K6 is active, not hypothetical.** With a single recovered population and only
its winning lineage, there is no base rate. Any signal computed today is a
property of one survivor.

**K9 is untestable.** This is worse than a firing criterion, because it means
the most banal alternative explanation - the detector notices that pd 101 is
nearly EQU - cannot currently be excluded. A detector that cannot be checked
against its most obvious confound should not be run.

Together these are the reason the gate packet does not recommend RUN_H1A.
""")


parts = [
 {"detector_part_id":"det-part-avida-landscape","measurement":"exhaustive mutational-neighbourhood enumeration with fitness-valued outcome classification (dead / deleterious / neutral / beneficial), plus mean and mean-square mutant fitness","historical_implementation":"cLandscape in source/main/landscape.{hh,cc}, Avida 2.2 (2005). Entry points ProcessGenome, Process(in_distance), ProcessBase.","causal_question_answered":"what is the local fitness structure around this genome, and how much of it is lethal?","limitations":"classifies by FITNESS only. landscape.hh contains zero task references; landscape.cc touches cPhenotype solely for GetFitness, GetMerit and GetGestationTime. It cannot report which logic functions neighbours gain or lose, nor reachable phenotype richness or entropy.","sfe_integration_opportunity":"adopt the enumerator and its accounting; replace the fitness-valued classifier with a phenotype-partitioned one (P-MED). Prometheus's Gen-1B sampled neighbourhoods ad hoc and had no reusable enumerator.","evidence_source":"ARTIFACT_IN_HAND","locators":[{"type":"file","ref":"ergon/avida2003/artifacts/x22/avida-2.2/source/main/landscape.hh"},{"type":"file","ref":"ergon/avida2003/artifacts/x22/avida-2.2/source/main/landscape.cc"}]},
 {"detector_part_id":"det-part-avida-distance-param","measurement":"k-step mutational neighbourhood via a distance parameter","historical_implementation":"cLandscape::Process(int in_distance = 1) and Process_Body(cur_genome, cur_distance, start_line)","causal_question_answered":"how does local structure change as the mutational radius grows?","limitations":"cost grows combinatorially; the historical code offers no sampling mode, so k=2 is exhaustive or nothing.","sfe_integration_opportunity":"Prometheus's RPD spec needs exactly this generalisation and currently hand-rolls a k=2 sampler. Adopt the parameterisation; add the sampler the original lacked.","evidence_source":"ARTIFACT_IN_HAND","locators":[{"type":"file","ref":"ergon/avida2003/artifacts/x22/avida-2.2/source/main/landscape.hh"}]},
 {"detector_part_id":"det-part-avida-indel-landscape","measurement":"separate insertion and deletion mutational landscapes","historical_implementation":"cLandscape::ProcessInsert(), cLandscape::ProcessDelete()","causal_question_answered":"is the local structure under length-changing mutation different from under substitution?","limitations":"none identified beyond cost","sfe_integration_opportunity":"HIGH. Prometheus's D-5 substrate has INSERT-complete physics and its R==E theorem turns on universal single-edit insertion, yet it never separated indel from substitution neighbourhoods. Avida treated them as distinct first-class analyses in 2005.","evidence_source":"ARTIFACT_IN_HAND","locators":[{"type":"file","ref":"ergon/avida2003/artifacts/x22/avida-2.2/source/main/landscape.hh"}]},
 {"detector_part_id":"det-part-avida-neutral-band","measurement":"explicit neutrality threshold for classifying mutants","historical_implementation":"neut_max member of cLandscape - the fitness band within which a mutation counts as neutral","causal_question_answered":"which mutations are effectively neutral, under a declared tolerance rather than exact equality?","limitations":"a single scalar band; no per-task notion of neutrality","sfe_integration_opportunity":"Prometheus's effective-use credit rule uses a trailing-median comparison with no declared tolerance. An explicit band makes the neutrality decision a preregistered parameter instead of an implicit consequence of floating-point equality.","evidence_source":"ARTIFACT_IN_HAND","locators":[{"type":"file","ref":"ergon/avida2003/artifacts/x22/avida-2.2/source/main/landscape.hh"}]},
 {"detector_part_id":"det-part-avida-epistasis","measurement":"two-step epistasis counters: positive, negative and lethal epistatic pairs","historical_implementation":"pos_epi_count, neg_epi_count, dead_epi_count and their sizes, with GetProbEpiPos / GetProbEpiNeg / GetProbEpiDead","causal_question_answered":"do pairs of mutations interact non-additively, and in which direction?","limitations":"aggregate counts only; no record of WHICH pairs interact, so it cannot identify a specific interacting structure","sfe_integration_opportunity":"directly relevant to the directive's PART-X dependency field ('effect appears only in presence of PART-Z'). Prometheus has no epistasis instrument at all.","evidence_source":"ARTIFACT_IN_HAND","locators":[{"type":"file","ref":"ergon/avida2003/artifacts/x22/avida-2.2/source/main/landscape.hh"}]},
 {"detector_part_id":"det-part-avida-lineage-record","measurement":"complete line of descent with per-step genome, birth time, phenotype vector and fitness relative to immediate parent","historical_implementation":"published as supplementary table IV; produced by Avida's genotype/lineage tracking","causal_question_answered":"which mutations accumulated on the path to the innovation, and was each individually beneficial, neutral or deleterious?","limitations":"successful lineage only. No contemporaries, no extinct siblings, no base rate.","sfe_integration_opportunity":"Prometheus's Gen-1A persistence instrument records library state through time but NOT a per-step relative-fitness column against the immediate parent. Avida's per-step relative fitness is exactly the quantity that made the deleterious-intermediate claim legible.","evidence_source":"ARTIFACT_IN_HAND","locators":[{"type":"page","ref":"nature01568 supplementary section IV"},{"type":"file","ref":"ergon/avida2003/artifacts/lineage_of_descent.jsonl"}]},
]
with open(os.path.join(D, 'O_HISTORICAL_DETECTOR_PARTS.jsonl'), 'w',
          encoding='utf-8', newline='\n') as fh:
    for p in parts:
        p['evidence_source'] = p.get('evidence_source', 'ARTIFACT_IN_HAND')
        fh.write(json.dumps(p, sort_keys=True) + '\n')
print('wrote O_HISTORICAL_DETECTOR_PARTS.jsonl', len(parts), 'parts')

cand = [
 {"part_id":"cand-part-none","status":"NO_CANDIDATE_YET","evidence_source":"ARTIFACT_IN_HAND","causal_computational_description":"No candidate computational part is proposed in V0. Identifying PART-X requires H1A, which is not authorised, and H1B/H1C, which are blocked. Emitting a speculative part here would violate directive section 25, which requires ablation evidence before a part is described as causal.","kill_observation":"n/a - this row exists to record deliberate emptiness rather than to leave the file absent","locators":[{"type":"file","ref":"ergon/avida2003/ERGON_AVIDA2003_HISTORICAL_DEEP_DIVE_V0/R_EXECUTION_GATE_PACKET.txt"}],"notes":"The 112-genotype line of descent contains 111 individual mutations, each a candidate. Naming one before matched controls exist would be exactly the survivorship error K6 describes."},
]
with open(os.path.join(D, 'P_CANDIDATE_COMPUTATIONAL_PARTS.jsonl'), 'w',
          encoding='utf-8', newline='\n') as fh:
    for c in cand:
        fh.write(json.dumps(c, sort_keys=True) + '\n')
print('wrote P_CANDIDATE_COMPUTATIONAL_PARTS.jsonl')
