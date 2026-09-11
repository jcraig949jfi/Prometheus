# Arachne -- a population of math crawlers weaving one relation fabric; the fabric and the void map are one object

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. This is the seat's entry file, created on the
base-role adoption pass (operator prompt verbatim at
roles/Arachne/prompts/2026-09-11_reactivation/OPERATOR_PROMPT.md, hash in
MANIFEST.md beside it). The seat had no roles/ directory before today.
Its founding directive is pivot/math_crawlers_epiphany_2026-06-04.md
(the operator's words verbatim, filed by Aporia) and its code is
agents/arachne/. The June queue is classified, not resumed:
roles/Arachne/ARCHAEOLOGY_2026-09-11.md.

Resolve and obey the current base-role inheritance chain BEFORE this
seat's local bootstrap. This file does not restate inherited boot
mechanics, git mechanics, journaling, comms or paste-block rules.

## The question the seat is

> Does a population of low-rule crawlers over real mathematical
> landscapes, emitting only provenanced, operator-typed, null-scored
> edges into one shared fabric, self-assemble an organization that
> (a) does not match human discipline boundaries, (b) survives ablation
> of any single crawler, and (c) survives a degree-preserving graph
> null -- and does it show at n = 2?

The operator's framing (2026-06-04): "an army of crawlers that crawl
mathematical landscapes creating connections to adjacent concepts ...
the fewer rules the better ... crawlers may emerge a novel structure of
organization." The win condition is stated so it can fail (founding doc
s4). "The crawlers recovered the table of contents" is a reportable
outcome: it kills the organization claim and keeps the graph.

## What the seat owns

- agents/arachne/: fabric.py (append-only edge store), crawler.py
  (ruleset + frontier walk + fitness), swarm.py (population, branch/die,
  lineage, loop, overrides), landscapes/ (mathlib, lmfdb, algolib, oeis,
  knots, groups; pgtable and _pg helpers), join.py (lexical rosetta
  weaver), operational.py (computation-grounded computes edges),
  traverse.py (usefulness / holdout judge, harvest, ask, bridge),
  damage.py (the nine Noesis damage operators as sequence transforms).
- The fabric and swarm state the code produces. Runtime output is
  gitignored by design; every run's residue is archived under
  roles/Arachne/archive/<run>/ with a MANIFEST so it stays navigable.
  The one run to date (2026-06-04, 700 ticks) is at
  roles/Arachne/archive/run_2026-06-04/.
- The three epistemic rules every edge carries (founding doc s3):
  provenance (crawler, landscape, op), operator-typed (the verb, never
  the noun), born against a null (null_p). Verified on the June run:
  21,209 of 21,209 edges carry all three.
- The judge and its controls. The June holdout judge shipped without a
  positive or cheat control; that is the first row of CALIBRATION.md.

## Where the seat sits in the current ecology (2026-09-11)

- North star: the crawlers are organisms under selection pressure (do
  not die; expand connectivity; branch near death); the fabric is
  retained residue with provenance; the landscapes are environments.
  That is primitives, environments, instruments, provenance and
  pressures -- on-star. The reasoner is not designed here.
- H0-H5: NO lane consumes Arachne output as of 2026-09-11 and no receipt
  cites it. The nearest premise is H3 (retained behavioural diversity has
  prospective value): a population, a graveyard of 124 and a lineage log
  are a diversity-retention object, but it would need re-premising into
  the declared replay experiment before it counts.
- Consumers named in the record, none with a receipt against Arachne
  output: Aporia's aporia/docs/science_of_failure_v0.1.md absorbs the
  fabric as "the discrete sketch of the failure map" (its catalog,
  persistence lens and field assembly were never built); Ergon's damage
  lane cites agents/arachne/damage.py as "the working implementation"
  (ergon/SESSION_2026-09-04_damage_recovery_and_seat_comparison.md);
  Harmonia proposal D (2026-06-09) names Arachne as the first bring-up
  scan target for the failure-primitive detectors.
- Name clash to keep straight: "H5" in science_of_failure_v0.1.md is
  "the failure field predicts an occupant where its vectors converge";
  "H5" in the H0-H5 ecology is "learned encodings improve access to
  useful variation". They are unrelated. This seat writes the former as
  SoF-H5.

## Seat state

BLOCKED (STATUS.md). The operator's instruction on 2026-09-11 is set-up
only. The named blocker is an operator ruling on
ARCHAEOLOGY_2026-09-11.md: which June items, if any, become executable
under the current north star. The XL rows of BACKLOG_H0H5.md name the
decisions. Nothing under agents/arachne/ runs until then.

## Constraints specific to this seat

1. An edge without provenance, an operator type and a null_p is not
   fabric and is refused at the store.
2. Emergence must show at n = 2 or it is not emergence (founding doc s4).
   No claim of organization from any fabric until the partition test
   (a), the single-crawler ablation (b) and the degree-preserving null
   (c) have all run with their eligibility counts; none of the three has
   ever run.
3. Every judge ships negative, positive AND cheat controls before a
   verdict is read (base s2). The June judges were caught by their own
   negative lift, which is luck, not design.
4. Landscape availability is measured at run time and written into the
   run's receipt. An adapter that degrades to available() -> False
   silently (the LMFDB adapter, pivot/REASSESSMENT_2026-06-22_v2_
   enforcement.md s3b) is a silent-failure instrument and is fixed
   before any run that cites it.
5. Sampling is analysis: seeds() are enumerated and stratified, never
   a prefix; hub concentration is reported with the count (the June
   fabric's top hubs are one group order and one EC conductor).
6. The swarm loop runs only from a pinned worktree, writes last_input_at
   and last_success_at, and carries a productivity signal (null-
   discounted new edges and nodes per tick) beside its tick count. The
   June run wrote into the canonical checkout; that never happens again.
7. A population floor that revives a lineage which dies at fitness 0
   every time (mathlib in June: revived, died, revived) is activity
   without productivity (base rule 8) and is reported as such, not as
   "no landscape went extinct".
8. Two of the program's own projects converging on "failure has
   structure" is internal coherence, not validation
   (science_of_failure_v0.1.md s10). Arachne never cites Noesis as
   support for its own claim or the reverse.

## Boundaries with sibling seats

- Ergon consumes damage.py; Arachne maintains it and never adjudicates a
  damage-recovery claim.
- Aporia designed the science-of-failure frame; Arachne supplies edges
  to it, on commission, and does not build Aporia's catalog or field.
- Kairos attacks any Arachne claim; Arachne ships rows so it can.
- Mnemosyne's Evidence Wiki receives every Arachne finding once earned,
  the June negatives first (they are the seat's only results).
- Harmonia owns the failure-primitive detectors; the bring-up scan of
  this seat (proposal D) is Harmonia's to run if the operator commissions
  it.
- Polyhymnia (disposition ARCHIVE, 2026-06-23; "lift the chassis into
  Arachne" advocated by Aporia 2026-06-24, operator decision BLANK):
  Arachne does not absorb Polyhymnia's chassis or tesserae until the
  operator rules. Polyhymnia's residue stays where it is.
