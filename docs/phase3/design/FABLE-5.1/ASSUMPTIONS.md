# Prometheus Phase 3 -- assumptions

Architect: FABLE-5.1 (seat Dionysus). Every major assumption the proposal
depends on, what breaks if it is wrong, and how early that would show.
Terms are defined in REQUIREMENTS.md section 1.

The assumptions are ordered by how much of the design falls with them.

> Provenance note, 2026-10-01. This file is not part of the freeze commit
> (a0e3a4d03, 14:50Z). It was first committed 28 minutes later in
> f98efbc33, the commit that also holds the first salvage worker's report.
> I wrote it from the frozen requirements and architecture, but git cannot
> show that it was written before I read that report. Blocks marked
> "Annotation" are later additions.

## A. Assumptions about the science

**A1. Small-scale relocations are informative about larger systems.**
The design studies HOLD through RECURSE in worlds that are small on purpose.
It assumes that where information sits and how it is reused are governed by
relations that do not depend on the amount of knowledge involved.
- If wrong: the transition map describes toy systems only. Everything above
  the kernel loses its point.
- How it would show: the construct-validity test (WLD-12) fails; profiles
  measured in certified worlds do not predict behaviour in richer ones.
- When: months 4 to 8.
- This is the assumption I am least sure of. Nothing in the record tests it.

**A2. The six relocations can be told apart.**
The design assumes an organism can be at different levels on different
relocations, so that six axes carry more information than one.
- If wrong: every organism that has one has all, the axes collapse into a
  single score, and the knockout matrix is uninformative.
- How it would show: profiles across organisms are almost perfectly
  correlated in P2 and P3.
- When: by day 60.

**A3. The within-lifetime gap is real.**
I argue that a learner with only fast state cannot BUILD, and that this is
where the current paradigm stops. Tool-using systems with an external
memory do build, but by design (scaffold level S5 or S3), not by a
mechanism of their own.
- If wrong: H1 fails, and the choice of BUILD-and-above as the target loses
  its sharpest justification. The apparatus is unaffected.
- When: by day 60 (P2).

> Annotation, 2026-10-01. H1 has since been split (RSE_ARCHITECTURE.md
> section 13.5). H1a is true by construction and tests nothing about A3.
> A3 now stands or falls with H1b: its retention half is read by day 60,
> its compression half needs RECOMBINE and is read by month 6.

**A4. Emergence has a null model.**
I assume that "it pays" and "search can reach it" are the two main factors,
and that both can be measured before the run.
- If wrong: the transition map does not factorise. That is a finding, and
  the residual is where to look. The design survives; hypothesis H2/H3 does
  not.
- When: day 90 for ADAPT, months 4 to 8 for BUILD and COMPRESS.

**A5. Reach measured on planted targets says something about unknown
targets.**
The search-power curve is measured on designed organisms. An unknown
mechanism for the same capability may be nearer or farther.
- If wrong: certified nulls are weaker than they look. They remain true as
  stated ("targets of this size were found at rate p") and say less about
  mechanisms nobody designed.
- How it would show: search finds a capability by a route much shorter or
  longer than the plant's needle size predicts.
- Mitigation: several different plants per capability; report the spread.
- This is a real limit and it is carried in OPEN_QUESTIONS.md.

**A6. Payoff computed from a designed organism's cost approximates the
payoff of whatever is found.**
- If wrong: H2 mislocates the boundary by the difference in cost.
- Mitigation: recompute payoff from the found organism's measured cost
  after the run and report both.

**A7. Class exclusion against a designed reference is adequate for COMPOSE
and RECURSE.**
T1 to T4 have exact or information-theoretic bounds. T5 and T6 are excluded
against designed organisms, which proves less.
- If wrong: claims at T5 and T6 are open to "a cheaper class does it too".
- Mitigation: an attack round is required at C2; the claim wording carries
  the weaker basis.

## B. Assumptions about the apparatus

**B1. Exact bounds are obtainable at sizes that still discriminate.**
Analytic bounds exist for RECALL, RETAIN and RECOMBINE by construction.
TRACK, IDENTIFY and DOUBT need enumeration or dynamic programming, which
only works for small instances.
- If wrong: some families have no certificate at interesting sizes and
  become uncertified exploration worlds.
- When: first month.

**B2. Designed organisms can be written for every relocation in every
substrate.**
Positive controls for HOLD to COMPRESS are short programs. The positive
control for RECURSE is a designed learner whose procedure adapts, which is
harder.
- If wrong for a relocation in a substrate: every null there is labelled
  NOT_SHOWN_EXPRESSIBLE, and no ruler for that relocation can be qualified
  there.
- When: RECURSE positive control by month 6. If it cannot be built at toy
  scale, the RECURSE ruler cannot be qualified and no RECURSE claim is
  possible. That is stated now so that it is not discovered later.

**B3. The harness controls the stores.**
Relocations are defined by where information sits. That requires that an
organism cannot carry information across a reset through a channel the
harness does not know about.
- If wrong: BUILD certificates are forgeable.
- Mitigation: the reset-equivalence test (ORG-02), and an impostor in the
  P1 calibration set built to smuggle.

**B4. A state partition is meaningful in every substrate.**
In a program store or a weight matrix, components are obvious. In a lattice
or a message-passing medium they may be coarse.
- If wrong: interchange and lesion instruments have low resolution in some
  open arms, and mechanism claims (C3) are unavailable there. Behavioural
  claims (C1, C2) are unaffected.

**B5. Integer kernels reproduce bit for bit across hosts and versions.**
- If wrong: REPR-01 fails; replay becomes tolerance-based and weaker.
- When: week 2 (golden trace on a second host).

**B6. The reference arm is tuned fairly.**
A weak reference arm would make every other substrate look good. The record
shows the same-class tuned baseline arriving after the data more than once.
- Mitigation: the BREAKER role owns tuning the reference arm, with a budget
  at least equal to the search budget of the substrate it is compared with.

**B7. Staircase thresholds exist.**
The adaptive staircase assumes performance falls monotonically as a demand
dial rises.
- If wrong for an organism: its threshold is not defined; the full curve
  is reported instead.

## C. Assumptions about resources

**C1. M1-class hardware is enough for T1 to T4, and probably T5.**
Measured: about 5 billion toy-machine instructions per second on M1
(process/vm_throughput_bench.md). Assumed: a factor of 10 lost to a real
kernel, giving on the order of 4 x 10^8 lifetimes of 10^5 instructions per
day. That is two to four orders of magnitude above the budgets the crawlers
report for v2 campaigns.
- If wrong: campaigns take weeks, and the maps are sparse.
- When: week 1 (the first deliverable is a real benchmark).

> Annotation, 2026-10-01. Measured once since this was written: the P1
> prototype kernel with a world in the loop ran 1.70 billion organism
> instructions per second on 12 threads, about a factor of 3 below the toy
> figure. The prototype machine is far smaller than WM, so C1 stays an
> assumption. Two planning figures are in the package and they differ by a
> factor of five: C1 above assumes 5 x 10^8 instructions per second (4 x
> 10^8 lifetimes a day); COMP-01's starting target and every budget in
> ENGINE_PORTFOLIO.md use 10^8 (8.6 x 10^7 lifetimes a day). Budgets use
> the lower figure. The salvage also showed why old budgets were
> small: the largest lifetime-scale search on record is about 2 x 10^7
> evaluations, mostly in pure Python (salvage report 07, section A).

**C2. Lifetimes of 10^4 to 10^6 instructions are long enough to show BUILD,
COMPRESS and COMPOSE.**
- If wrong: longer lifetimes cut the number of lifetimes per day in
  proportion.

**C3. Model sessions can build the kernel correctly within a tolerable
token budget.**
The kernel, the world families and the calibration sets are several
thousand lines of tested code. No number for the token cost can be given
honestly, because nothing in the program has ever measured token use
(Ixion section 7).
- Mitigation: metering from the first session (INF-03); the day-30 gate
  reviews the measured cost.

> Annotation, 2026-10-01. The salvage found two exceptions to "nothing has
> ever measured token use": Fabric's model attempts record the model and a
> dollar cost per attempt and drop the token counts (salvage report 06,
> SURPRISES 2); and one replay tool logs tokens per call for its own calls
> (report 07, sheet 10a). One data point of my own: the seven salvage workers used
> 4,174,516 tokens in total as reported by the harness, for more than
> 143,000 lines of code characterised. That is the only measured inference cost in
> this package.

**C4. A second model family is available for independent implementations.**
The operator has used several vendors. The design needs one of them
reachable from code, so that the operator is not the transport (HUM-03).
- If wrong: independence stops at I2; claims stop at C2. The design says so
  and still runs.

**C5. Token use, CPU time and energy can be metered.**
- If wrong for tokens: the yield table lacks its most important cost
  column.

## D. Assumptions about the institution

**D1. The operator accepts ninety days that produce instruments and two
maps before they produce any claim about reasoning.**
- If not: the pressure to observe-and-interpret returns, and with it the
  record.

**D2. The control model holds still.**
The design assumes one decisions register and no change of regime for at
least the first ninety days.

**D3. The operator rules on three doctrine points.**
HARD-1 (no publication framing) against the prompt's section 18. HARD-2
(suppress literature comparison) against ANTI-06. The North Star's "not a
predetermined ... ladder" against fixed measurement axes.
- If not ruled: Phase 3 runs under current doctrine. No external artifacts.
  Prior-art retrieval stays optional. The axes are used and the tension is
  recorded.

**D4. The fleet can be reduced to campaigns and three roles.**
The operating model in RSE_ARCHITECTURE.md section 10 is a proposal. If the
fleet stays as it is, the kernel still works, and the inference and
attention requirements (INF-01, INF-07, HUM-01 to HUM-04) are not met.

## E. Assumptions about this document's author

**E1. I read the record correctly.**
My account of v1 and v2 comes from four crawler reports written by the same
model family as the program they audit, and from workers of that family
again. Tityos says this about itself. I inherit it.
- Mitigation: every salvage decision that matters was checked against
  source by a worker told to say what it verified itself, and the decisive
  ones I opened myself (SALVAGE_MATRIX.md lists which).

> Annotation, 2026-10-01. What "the decisive ones" came to in practice: ten
> facts, listed in SALVAGE_MATRIX.md section 0, all of which held. That is a
> spot check of the points the decisions lean on, not a re-verification of
> seven reports. The workers also found 14 places where the crawler record
> was wrong (SALVAGE_MATRIX.md section 7); none changed a requirement. A
> later read-only review of the matrix against the worker reports found 22
> places where my rows overstated or misquoted a sheet; those are corrected.

**E2. I am not the independence I ask for.**
I am one model family designing an apparatus to escape one model family's
priors. The axes, the world families and the substrates are my choices and
carry my priors. The design's answer is mechanical, not personal:
certificates that need no judgement, unauthored worlds, blind variation, a
second implementation by another family, and two other architects working
separately. The meta-analysis across architects is the real check.

**E3. The architecture is as good as its first experiment.**
None of this has run. P1 exists to find out quickly whether the central
instrument works, and the day-45 stop rule exists in case it does not.

> Annotation, 2026-10-01. A miniature of P1 has now run
> (prototype/p1_slice/). Its first gate failed on a defect of mine (verdicts
> preregistered without a power check), and the amended gate passed on fresh
> sealed lives. So the central instrument works mechanically at toy size, on
> one host, by one author. E3 still stands for everything larger.
