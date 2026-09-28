# Accumulation measurement v0 -- "does anything build on anything?"

Currency: 2026-09-28. Odysseus. Status: v0 DEFINITION, not yet validated;
the known-answer apparatus is expedition/sandbox/ (the world-record toy).
Directive: roles/Odysseus/prompts/2026-09-28_expeditionary/ s2, s4, s15.
Pure ASCII. Attack this file; every rule below is a hypothesis about how to
measure, and several were changed from the directive's draft on purpose.

## 0. Why a measurement first

Prometheus has optimisation, adaptation, copying, search and competence.
None of those is accumulation, and the program's recurring failure is to
award a property because a label implies it (raw/I6: 21 rows). So nothing
here is decided by what a thing is called. Every rung is decided by an
INTERVENTION on a replayable world, against a matched counterfactual.

## 1. Objects are identified by intervention, not by name

An ACQUIRED OBJECT X is a declared subset of world state at time t (bytes,
record cells, couplings, a tape region) such that:

  (h) HISTORY-SPECIFIC: X's content differs between otherwise identical
      worlds whose earlier events differ (twin worlds forked before the
      producing events, different event streams). A component that every
      history drives to the same value is a property of the physics, not
      an acquisition.
  (n) NOT INITIAL: X's content is not present at t=0 and not produced at
      matched time by a HISTORY-ABLATED twin (same world, producing events
      removed or replaced by matched-rate irrelevant events).

The declaration of X is part of the preregistration. If X must be found by
search, the search is declared and its multiplicity is corrected (the
habituation assay showed searching readouts inflates false passes 10-30x;
spikes/S5).

## 2. The five draft criteria, attacked

The directive's draft: (1) arises during the system's history; (2) a later
process consumes it; (3) the consumer gets behaviour it could not get
equivalently from the original substrate at matched budget; (4) it survives
a change of individual, episode, context or generation; (5) removing or
scrambling it removes the advantage.

- (1) is necessary but too weak: in a dynamical system everything "arises
  during history". Replaced by (h)+(n) above.
- (2)+(5) conflate two claims: that the consumer DEPENDS on X (deletion
  removes the benefit) and that it depends on X's CONTENT (a capacity-
  matched record from another history does not give the benefit). A
  system that uses "any record" as a trigger passes (5) with deletion and
  fails with permutation. Split into R1 (dependence) and R3 (content).
- (3) hides two different gains. SPEED: the consumer reaches the same
  behaviour sooner. CEILING: the consumer reaches behaviour that the
  substrate does not reach at a tested budget without X. They must be
  reported separately, with a RECOMPUTE ARM: a consumer without X but given
  the budget it cost to produce X. If the recompute arm matches, X is a
  cache (speed), not an accumulation of reach.
- (4) conflates PERSISTENCE and INHERITANCE. Persistence: the same carrier
  keeps X. Inheritance: X is transferred to a new carrier and the benefit
  remains after the ORIGINAL carrier is destroyed. Only the second
  licenses "survives a change of individual/generation".
- Missing from the draft: SEMANTICS NOT INSTALLED. If the experimenter's
  encoding gives X its meaning, the ecology did not invent anything. Test:
  CONVENTION INVARIANCE -- randomly relabel the record alphabet / address
  map per world at t=0 (a symmetry the physics does not see). An invented
  convention works under any relabeling; an installed one breaks or must
  be re-engineered.
- Missing: COMPOSITION vs REDISCOVERY. A later object Y "builds on" X only
  if Y's production causally used X (provenance/taint), not if every
  lineage re-derives Y at the same cost. Test: the rate of producing Y with
  X available vs in independent X-free worlds, plus provenance of Y's
  content.

## 3. The ladder (each rung requires every lower rung's tests)

  R0 PERSISTENCE -- X (per s1) keeps its history-specific content for T
     after its producer stopped acting on it (producer halted or removed).
     Falsifier: X decays to the history-ablated twin's distribution before T.

  R1 LATER REUSE (same producer or lineage) -- behaviour at a later
     episode differs between X-intact and X-deleted worlds, beyond the
     no-record twin's noise band. Falsifier: deletion effect inside the band.

  R2 NEW CONSUMER -- the benefit appears in a consumer that did not
     produce X (another individual/lineage), with the producer destroyed
     before consumption (INHERITANCE, not persistence), and exceeds what the
     consumer gets from equal exposure to the environment in the no-record
     twin. Falsifier: benefit confined to producers, or explained by shared
     environment.

  R3 CONTENT DEPENDENCE -- the benefit follows X's CONTENT: permuting
     records between lineages/episodes (capacity-matched, same position
     and format) removes it, and an equal-capacity random record does not
     supply it, and irrelevant-record injection does not change it. Plus
     CONVENTION INVARIANCE (s2) where the rung is claimed for an invented
     code. Falsifier: permuted or random records give the same benefit.

  R4 RECOMBINATION -- two objects X1, X2 acquired INDEPENDENTLY (different
     lineages or episodes, verified by provenance) are used together: in a
     2x2 deletion design the interaction term is positive beyond the null
     band (the pair gives more than the better single object). Falsifier:
     additive or redundant only.

  R5 RATCHET (CEILING) -- with the objects, a consumer reaches a capability
     that (a) no X-free consumer reaches at the tested budget, (b) the
     RECOMPUTE ARM (X-free, given the objects' production budget) does not
     reach, (c) pristine worlds at matched total compute do not reach.
     Falsifier: any of (a)-(c) reaches it -- then it is speed, not reach.

  R6 RECURSIVE -- an acquired object raises the rate or ceiling of
     acquiring NEW objects (not re-acquiring itself): acquisition rate of
     novel objects in worlds with inherited stock vs without, at matched
     budget. Falsifier: no change in novel-object acquisition.

Reported per world, aggregated across >= 20 independent worlds per arm;
rungs are awarded to the ECOLOGY in a configuration, never to an
individual by name.

## 4. The six distinctions, as tests

    accumulation vs optimisation     R2 + R5: optimisation improves a
                                     system; accumulation passes an object
                                     to a new consumer and moves its reach
    inheritance vs persistence       R2's "producer destroyed first"
    reuse vs recomputation           the recompute arm (s2, R5b)
    composition vs rediscovery       provenance + independent-world rate (s2)
    ceiling vs speed                 two numbers, never one: time-to-
                                     criterion AND max-at-budget (R5)
    invented vs installed protocol   convention invariance (s2, R3) and
                                     the frozen-readout control (s5)

## 5. Mandatory controls (the directive's list, mapped)

    record deletion              R1, R2
    record permutation           R3
    writer/reader separation     R2 (producer destroyed; reader never wrote)
    novel receivers              R2
    irrelevant-record injection  R3
    equal-capacity random records R3
    fresh-world transfer         R2/R5 (object moved to a new world instance)
    frozen readout               s2 installed-semantics test: the reader's
                                 mapping cannot change -> any benefit came
                                 from the writer adapting to a fixed code
    no-record twin               the baseline band for every rung
    unreadable storage           same storage, reads return nothing (the
                                 sandbox ruling's first control)

## 6. Known-answer requirement

Before any unplanted run, the apparatus must award the correct rungs in a
world with a PLANTED convention (a known writer/reader code installed by
the experimenter): planted R0-R3 must be detected, and planted-absent R4-R6
must NOT be awarded; then with the plant removed, the same battery is run
and marked EXPLORATORY. expedition/sandbox/ carries this.

## 7. Where the boundary probably is (a prediction, to be wrong about)

R0-R1 are cheap (persistence and reuse are generic; memory without
plasticity is common in random dynamics, raw/E5). R2 is the first hard
rung (inheritance across a destroyed producer). R3 content-dependence with
convention invariance is where "invented meaning" would first be shown,
and where I expect toy ecologies to stall. R4 is unobserved anywhere in the
program. Prediction: the first unplanted boundary sits at R2 or R3.

## 8. REVISION v0.1 (2026-09-28, after the sandbox gate, raid A and census A/B)

Nothing above is silently rewritten; these amendments supersede the
sections they name. Evidence: expedition/sandbox/RESULT.md s4 (three
defects found by the first implementation), expedition/foreign/raid_A/
toy_iterated_learning/RESULT.md (closure), census/CENSUS_A_z80.md and
CENSUS_B_other.md (what the record can and cannot support).

A1 (supersedes s2 "recompute arm", s3 R5b). TWO recompute arms, both
   reported. RC-consumer: an X-free consumer given the consumer's own
   per-decision budget for the same number of decisions -- does X give the
   consumer reach it could not buy itself? RC-ecology: an X-free ecology
   given the full production budget of X -- does accumulation beat
   re-derivation from scratch? R5 is awarded at consumer level when
   RC-consumer fails; "R5-strong" only when RC-ecology also fails. (The
   literal production budget made the recompute arm always succeed in small
   worlds, so R5 was unreachable by construction.)

A2 (supersedes s2 "convention invariance", s3 R3 invariance clause).
   Three outcomes, not two: INVARIANT (benefit survives relabeling),
   INSTALLED (benefit breaks under relabeling), NO-BENEFIT (nothing to
   test). And invariance can hold VACUOUSLY by symmetry when starting
   genomes are uniform over symbols; so every claim of invented meaning also
   needs a SEMANTICS AUDIT of the world's primitives: list each action and
   input and show none maps record symbols to environment features.

A3 (supersedes s3 R0 and "each rung requires every lower rung").
   R0 is defined by intervention: history-specific content is decodable by
   a decoder declared in the prereg and fit on held-out worlds. Rungs are
   awarded INDEPENDENTLY; ladder monotonicity is an empirical claim to
   test, not an assumption (the sandbox's seed 1016 showed per-world R1-R3
   while failing R0).

A4 (new, below s3). R-1 CHANNEL FORMATION. Before any content rung:
   writers and readers co-exist and a reader's action depends on record
   state at all (mutual information between record cells and reader
   actions above the no-record twin). The first unplanted sandbox run
   stalled HERE: readers were selected out (median reader fraction
   0.01-0.02). The boundary predicted in s7 (R2/R3) was wrong; it is below
   R0.

A5 (new, a precheck before any ladder run). RECEIVER CLOSURE: verify the
   receiver class can HOLD a structured code -- a planted structured code
   must survive one transmission through the receiver's rebuilding rule.
   If it cannot, the ladder is capped by construction and a null is
   uninformative (raid A: an associative learner could not keep even a
   perfect compositional code; a one-feature-per-position learner could,
   and then ratcheted).

A6 (new). Worlds must be statistically independent: probe/evaluation seeds
   salted per world (the sandbox's first gate failed on shared probe seeds).

A7 (observed pattern, a hypothesis for v0.2, not a rule). Every census
   survivor (A1, N5, N1; H8 pending) is a lineage INTERNALISING something
   the world or designer supplied (a destination address, register values,
   self-location, a delay-general read). If that holds, the first real
   accumulation in Prometheus is genetic assimilation of scaffolding,
   and s3 needs a rung for it. See expedition/TERRITORY_I_SCAFFOLD.md.

A8 (2026-09-28, from the sandbox cold-start, sandbox/coldstart_A-001/).
   The HISTORY-ABLATED TWIN of s1(n) must be a DIFFERENT-HISTORY twin
   (same world, different earlier event stream), never a NO-WRITE twin. A
   no-write twin measures UPKEEP, not history: the fresh worker's "nest tag"
   cheat (each colony writes the same constant symbol every generation)
   passed R0 and was awarded R3 by the frozen battery. The episode test
   (the producer's own record from an earlier episode) and the
   different-history twin score it 0.000-0.003 vs 0.475 for a genuine code
   and must be DECISIONAL for R0 and R3. Candidate repair checked post hoc
   on the same seeds (keeps every original gate verdict); EXPLORATORY until
   re-gated.
