# Prometheus Phase 3 -- open questions

Architect: FABLE-5.1 (seat Dionysus). Written 2026-10-01. What the proposal
does not settle. Terms are defined in REQUIREMENTS.md section 1.

Each question has: why it matters, what would settle it, and what happens
by default if nobody settles it. Questions are ordered within each group by
how much of the design depends on them.

----------------------------------------------------------------------

## A. For the operator to rule

These are decisions, not research. The design runs under the stated default
until ruled.

**A1. Publication framing (doctrine HARD-1).**
Tracked doctrine forbids paper and publication framing. The architect
prompt's section 18 asks for externally legible artifacts. I did not adopt
section 18.
- Why it matters: it fixes what Phase 3C aims at.
- My proposal if HARD-1 is lifted or narrowed: externalise instruments
  first (the certified world suite, the qualification harness, the failure
  fixtures), each when it reproduces from a clean clone; effects at C2,
  mechanisms at C3, principles at C5 (PUB-01, PUB-05).
- Default: no external artifact. Clean-clone reproduction on a second host
  is still required from C2 (REPR-02), and the pack an outsider could run
  is still built at C4 (REPR-07), for internal use.

**A2. Prior art (doctrine HARD-2).**
HARD-2 says to suppress the reflex of literature comparison. ANTI-06 asks
for prior-art retrieval after a result reaches C2, recorded as an outcome,
with recall measured on planted known mechanisms.
- Why it matters: the record erred both ways. It listed "no precedent" from
  searches nobody logged, and it counted known results as anomalies.
- Note: I already ran a prior-art check on this design itself
  (process/PRIOR_ART_CHECKED.md, 29 references, 22 logged searches). That
  was about the method, not about a result, but it leans against HARD-2 and
  I flag it.
- Owed if HARD-2 is narrowed: a proper prior-art pass on this design's own
  method, with recall measured on planted known references. The check I
  ran measured no recall.
- Default: retrieval stays optional and "novel" is never said.

**A3. Fixed measurement axes against the North Star.**
The North Star says Prometheus supplies primitives and pressures, "not a
predetermined reasoning architecture or ladder". The six relocations are
predetermined axes of measurement.
- My reading: they fix what is measured, not what must be built or in what
  order. MINED worlds and open arms exist so that the axes are not the only
  thing visible.
- The real cost: an organism that develops along an axis nobody defined is
  measured only in uncertified worlds. See B3.
- Default: the axes are used and this tension is printed in every summary.

**A4. The operating model.**
Campaigns instead of seats; three roles; one queue, one lease, one ledger,
one digest; retirement of three services and at least eight parallel queues
(SALVAGE_MATRIX I-10).
- Why it matters: Ixion measured the alternative.
- Default: the kernel works with the fleet as it is; INF-01, INF-07 and
  HUM-01 to HUM-04 are then not met, and the yield table will show the cost.

**A5. A second model family reachable from code.**
Independence level I3 needs a ruler and a world re-implemented from the
specification by a different author, where possible a different model
family, without the operator carrying text between them.
- Default: independence stops at I2 and claims stop at C2. Every report
  says so (FALSIFIERS F-D4).

**A6. Custody of sealed worlds.**
Where sealed material lives (another host, an encrypted store), who can
read it, and what logs the reads.
- Why now: on 2026-10-01 a search pattern in my own brief let workers'
  searches reach holdout-named files, and one search printed a line of one
  (salvage_reports/00_SEARCH_RULE_INCIDENT.md).
- Default: Phase 3 sealed sets are generated from a secret seed that is
  never committed, held outside the working tree on M1, with a commit-reveal
  hash in the repository. That is weaker than a broker with an access log.

**A7. Credentials in tracked files.**
Every store reads its database credential from one tracked file, and three
more tracked places hold credentials (salvage report 06). Separate write
authority for generation, reality and interpretation cannot be built on a
shared credential.
- Default: Phase 3 stores use new credentials from the environment only,
  and the old stores are left as they are.

**A8. The tracer specification on a side branch.**
The strongest dependence-tracing semantics in the tree, with its fixture
pack, exists only on a branch 85 commits ahead of main (SALVAGE_MATRIX
C-08). Whether to merge it is not mine to decide.
- Default: the WM tracer is specified fresh from the Archaeon record format
  that is on main (C-06).

**A9. Ninety days of instruments before any claim about reasoning.**
The first 90 days produce a qualified kernel, a reference arm, a knockout
matrix and two first maps. They produce no claim about reasoning.
- Why it matters: this is the trade the whole design makes. If it is not
  acceptable, the pressure to observe and interpret returns, and the record
  shows where that leads.
- Default: none. This one needs a yes or a no.

**A10. One plug-in power meter, once per host.**
Nothing has ever measured wall power on any host. The energy figures in
this package are assumptions (200 W and 350 W).
- Default: energy is reported as an estimate from utilisation, flagged
  uncalibrated.

----------------------------------------------------------------------

## B. Scientific questions the design does not answer

**B1. Does small predict large?**
The design studies relocations in worlds that are small on purpose. It
assumes the relations that govern where information sits do not depend on
how much knowledge is involved (ASSUMPTIONS A1). Nothing in the record
tests this, and it is the assumption I am least sure of.
- What would settle it: the construct-validity test (WLD-12), months 4 to 8.
- What is still undefined: the "richer transfer set" itself. It must be
  larger than any certifiable world and must not import human priors through
  language. Candidates are larger MINED worlds and procedurally generated
  games. I have not designed it.
- If it fails twice: the small-world method is the wrong tool (F-T2).

**B2. Does reach on planted targets say anything about unknown targets?**
The search-power curve is measured on organisms I designed. A mechanism
nobody designed may be much nearer or much farther (ASSUMPTIONS A5). The
prototype already shows the gap: the builder found from an empty program
was not the designed one.
- What would help: several unlike plants per capability, and the spread
  between them reported as the uncertainty.
- What would not help: more lineages on one plant.
- Consequence if unsolved: certified nulls remain true as stated ("targets
  of this size were found at rate p") and say less than they appear to.

**B3. Are six relocations the right axes, and are they all of them?**
- Where do planning by internal simulation, active exploration, and change
  of representation sit? I placed exploration inside IDENTIFY and DOUBT and
  the other two inside COMPOSE. That is my prior.
- What an unlisted axis would look like: a capability that pays in a MINED
  world, is certified against that world's own enumerated bounds, and moves
  none of the six levels. The design can detect that. It cannot say what
  the capability is.
- What would show the axes are too many: FALSIFIERS F-T3 (all six levels
  move together).

**B4. Can COMPOSE and RECURSE have exact bounds?**
HOLD to COMPRESS have exact or information-theoretic bounds. COMPOSE and
RECURSE are excluded only against designed reference organisms
(ASSUMPTIONS A7). A counting bound for CHAIN in a restricted model of
computation may be provable: the cost of solving depth D without reuse,
against a step budget. I have not proved one.
- Default: claims at those levels carry the weaker basis in their wording,
  and need an attack round.

**B5. Can a designed positive control for RECURSE be built at toy scale?**
The RECURSE ruler cannot be qualified without a designed learner whose
procedure adapts and gains on families outside the span of earlier ones.
The old record is a warning: a fixed-procedure learner starting from
nothing built no reusable structure in 8 of 8 runs (SALVAGE_MATRIX O-13).
- Settled by: month 6. If it cannot be built, no RECURSE claim is possible
  and P6 reports COMPOSE only. That is stated now so it is not discovered
  later.

**B6. What is a "kind of structure", for H1b and for withheld sets?**
H1b predicts that amortised learners compress only kinds of structure that
their training covered. That needs a generative family of structure kinds
with a way to withhold some, built without the answer in it (XFER-06).
- Not designed yet. A weak choice here would make H1b true or false by
  construction, which is the error I just corrected in H1.

**B7. Where is the line between a generic affordance and a
capability-specific primitive?**
Scaffold levels S3 and S2 differ by exactly this. In the prototype,
store-read and store-write instructions make its from-scratch builder S3.
In the workspace machine, writing a block cell by tag is a generic
affordance, so the same behaviour would count as S2.
- Proposed rule: an affordance in the ORG-03 list is generic; anything else
  is specific. This is a convention, and "emergence" claims move with it.
  Reports therefore give the instruction set beside the level.

**B8. What makes two mechanisms the same?**
P8 and the reference class (ANTI-05) need a signature space: a vector of
responses to qualified probes that is invariant to re-encoding and
sensitive to mechanism. None exists in the tree and I have only sketched
one (ENGINE_PORTFOLIO section 10).
- Risk: a signature that measures coding style. The re-encoding control is
  the guard, and it may show the first design fails.

**B9. Is a common cost model possible across substrates?**
Payoff (H2) needs the cost of a capability. Instructions, stored cells and
joules are not obviously commensurable between a program store and a
network. MEAS-14 reports level per instruction and per estimated joule and
leaves the exchange rate open.

**B10. Is the bottom of the descent reachable, or needed?**
Scaffold level S0 is survival pressure with no task reward. I have not
designed that world, and at this scale it may be out of reach. The North
Star points there. The design reaches it last, or not at all, and says so.

**B11. Are lifetimes of 10^4 to 10^6 instructions long enough?**
ASSUMPTIONS C2. Unknown until COMPRESS and COMPOSE organisms are designed
and their lifetimes measured.

**B12. Several organisms in one world, self-ordered curricula, offline
phases.**
ORG-11, DEV-10, DEV-11 and WLD-13 are EXPERIMENTAL. Each gets a bounded
trial and no plan beyond it.

----------------------------------------------------------------------

## C. Questions about the apparatus

**C1. How large can worlds be and still have exact bounds?**
RECALL, RETAIN and RECOMBINE have bounds by construction at any size.
TRACK, IDENTIFY and DOUBT need enumeration or dynamic programming over
belief states, which grows fast. Whether the sizes that can be solved
exactly still separate the restricted classes by four times the ruler's
minimum detectable effect is unknown (ASSUMPTIONS B1). First month.

**C2. Can the reference arm be honest in integers?**
ORG-08 asks for integer physics. The reference learners are trained in
floating point and deployed as fixed-point networks. Fixed-point gradient
descent inside a lifetime (REF-c) is new work with a known risk: learning
that stalls from rounding. If it cannot be made to work, REF-c runs in
floats, is marked as a tolerance-replay cell, and cannot support a C3
claim.

**C3. Does the adaptive staircase give a threshold?**
It assumes performance falls as a demand dial rises. Where it does not, the
full curve is reported (ASSUMPTIONS B7; FALSIFIERS F-D9).

**C4. Is there a meaningful state partition outside programs and
networks?**
In a message-passing medium the components may be whole arrays. Then
mechanism claims are closed for that arm (FALSIFIERS F-D7).

**C5. Where do token counts and watts come from?**
The job fabric records dollars per model attempt and drops the token
counts. One replay tool logs tokens for its own calls. The shared
model-call layer's log has never been switched on. Windows gives no
direct reading of processor power. GPU power can be sampled. First week.

**C6. Queue workers on Windows.**
Fabric workers are Linux-only as written, and M1 runs Windows. Either a
Windows worker is written or campaigns run under a local runner holding a
Fabric lease. I chose the second for Phase 3A. Whether M1 has a usable
Linux subsystem was not checked.

**C7. A listing that can return a false "absent".**
In this repository `git ls-files` with one positive path of two or more
components plus any exclusion returns nothing
(salvage_reports/00_SEARCH_RULE_INCIDENT.md). I reproduced it and did not
find the cause. Any absence result that rests on such a listing is suspect.

**C8. Does compiled integer code replay bit for bit across hosts and
compiler versions?**
Expected yes. Tested in week 2 by a golden trace on a second host
(ASSUMPTIONS B5).

**C9. Which hosts are the second host?**
The two small Linux nodes can replay golden traces and run clean-clone
tests; they cannot run campaigns. Whether M2 is available as a second
campaign host is the operator's call.

**C10. How does a second implementation actually get written?**
A specification precise enough to implement from; a differential test
harness; a route to the second author that does not pass through the
operator (HUM-03). Not designed beyond the requirement.

----------------------------------------------------------------------

## D. What the salvage left unknown

Five rows of SALVAGE_MATRIX.md are UNKNOWN:

- W-05: the Ludus atlas of worlds (contents are in a database; nobody
  opened them).
- W-16: an Archaeon hidden-bitstring world said to have an exact optimum.
- M-16: a control whose header claims measured error rates. If true it is
  the only one in the old tree.
- C-08: dependence tracers whose specification is on a side branch.
- I-14: state outside the repository, including whether the M2 services
  are alive. No worker was allowed a database connection or a network
  probe.

Also unknown: whether the two workers that finished before my search-rule
correction reached any holdout-named file. Their transcripts are empty on
this host.

----------------------------------------------------------------------

## E. For the comparison across architects

Three architects were asked to work separately. These are the places where
I expect to be wrong, or where another design could reasonably differ.

**E1. Where this design is most exposed.**

1. Small may not predict large (B1).
2. It is instrument-heavy. It could produce a very good measuring device
   for phenomena that turn out not to matter.
3. Designed organisms carry my priors. Each capability is defined by a
   world I authored and calibrated by an organism I designed, and the
   descent starts from my designs. Certificates need no judgement, but the
   choice of what to certify was mine.
4. The first two substrates are familiar. The workspace machine is a
   stored-program machine with tagged memory. The plastic network is a
   recurrent network with local learning. The substrates that are not
   familiar wait until month 9. I chose calibration before strangeness.
   Another architect may weigh that the other way, and the anti-gravity
   section of the prompt gives them grounds.
5. The six axes may be the wrong cut (B3).

**E2. Readings of the charter I did not take.**

- "Physics of intelligence" as statistical physics: order parameters,
  phase transitions, scaling laws. My transition maps are phase diagrams of
  capability against pressure, so the design leans this way, but I did not
  build on energy-based or dynamical-systems substrates.
- Scale first. Soup first. Language-based worlds. A model inside the
  organism. Each is argued against in RSE_ARCHITECTURE.md section 2 or
  ENGINE_PORTFOLIO.md section 13; none of those arguments is evidence.

**E3. Answers that would change my design most.**

- An exact bound for COMPOSE or RECURSE (B4).
- A better null model for emergence than payoff times reach.
- A way to certify demand in worlds too large to solve exactly.
- A substrate in which BUILD and COMPOSE are both cheap to reach.
- Evidence that designed plants mislead about what search finds (B2).
