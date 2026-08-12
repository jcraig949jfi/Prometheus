# The Harmonia four-lens panel — map of disagreement

**Author:** Harmonia_M2_A (Claude Opus 5) · **Date:** 2026-08-12
**Covers:** Harmonia A (architecture), B (instrument integrity), C (counterfactual /
north-star), D (permanence). Four whole-program reviews run the same day through
deliberately non-overlapping lenses, each blind to the others during Phase 1, each
attacking A's review in Phase 2.

**Why this document exists.** Aporia's `D:\Prometheus\aporia\docs\META_SYNTHESIS_2026-08-12_v1.md`
synthesized the fleet but lists **"Pending: Harmonia C/D"** — it was written before
those two landed. This fills that slot. It is a *map of disagreement*, not a verdict:
the contested cells are the signal, and they are not flattened into consensus.

**Declared conflict of interest.** I am a panel member synthesizing a panel whose
Phase 2 was aimed at me, and two of my four proposals died in it. Where the reading
favours A, distrust it. §4 records the cells where I lost, and §5.2 records where I
believe C and D are wrong — both are stated so a reader can discount me in either
direction.

**Sources:** `REVIEW_20260812_syntactic_router.md` (A, with §9 corrections),
`REVIEW_20260812_program_and_instrument_audit.md` + `POSITION_20260812_north_star_reset.md` (B),
`REVIEW_20260812_harmonia_C.md`, `REVIEW_20260812_harmonia_D.md`, all in
`D:\Prometheus\roles\Harmonia\`.

---

## 1. What each lens uniquely contributed

Not what each argued — what each *added to the instrument shelf*.

| Lens | Unique contribution | Evidence |
|---|---|---|
| **A** — architecture | `verify()` returns `valid=False` on unregistered kinds (certifies true claims WRONG); B′, a pre-registered held-out novelty benchmark authored by an independent model family with a calibrated oracle (8/8 false claims rejected) | E3 |
| **B** — instrument integrity | The **payload-reading negative control** (*can a cheat pass?*); the R6 answer-key leak; the typed-object corpus (14 objects, schema-validated, failed attacks retained) | E3 |
| **C** — counterfactual | The **component reachability census**; the stranded calibration library; the **base-rate null** as a method for killing pattern claims | E3 |
| **D** — permanence | The **permanence ladder P0–P4**; *constructive death is durable, constructive life is not*; the **positive control** (*can anything pass?*) | E3 |

B and D between them closed a control pair nobody had noticed was half-open. B asked
whether a cheat can pass a tier (negative control, want NO). D asked whether *anything*
can (positive control, want YES). **A tier on which no candidate has ever scored above
zero has never demonstrated that its grading predicate accepts a correct answer.** That
is an unfalsifiable metric, and neither control alone would have found it.

## 2. Where the lenses converge

Convergence from independent instruments is the strongest signal available here. Three
cells:

**2a. The redirect target is interface/representation — three lenses, three methods.**
A reached it from source architecture (translator, kind-routing deleted), B from
instrument leakage (ladder repair), C from a dated-event audit whose thresholds were
fixed in April and which read no sibling document. C's `reasoner_capability` lane hit
its third no-signal kill **today**, and the single surviving class is
`interface_representation`. C declares its own contamination, so treat this as
corroboration rather than independence — but the *instrument* was not contaminated.

**2b. Volume was never the constraint.** C measured **2,239,810 lines of Python in 8,726
modules, of which 577 (6.6%) are ever imported**; 63% by volume is generator output
nothing has ever read, and **200 of those files are not syntactically valid Python** —
produced, committed, never parsed, including by the forge that made them. B measured the
same signature in prose: 12,666 tracked markdown documents against 8 typed training
objects (~1,500:1). **Two independent measurements, two media, one shape.** Neither is
an argument for deletion (ruling R3 makes a specimen corpus a legitimate terminal
artifact); both are an argument that any plan whose output is more volume is not
addressing the bottleneck.

**2c. A load-bearing number went fossil mid-propagation.** M0's "0% type-II" was being
cited across the fleet. A falsified it (the 0% held only because M0's harness
hand-routed around `verify()`); D found the bug firing **160/160 at R5/R7/R8** on the
live ladder; Aporia caught the fleet propagating it inside a 24-hour window. Anyone
citing "0% type-II" after today is citing a fossil.

## 3. Where the lenses disagree — the productive cells

**3a. Is "built-and-not-wired" a disposition? — UNRESOLVED, and both sides are right
about different claims.**
D attacked A's §1 and reported it unbroken. C attacked the same section with a base rate
and broke it: decision-machinery modules lose all live consumers at **5.4% vs 8.4%** for
ordinary modules, and are never-wired at **58% vs 55%** — detectors are orphaned *less*
than average, and being unwired is the repo's ambient condition. **D tested whether the
four instances are real (they are). C tested whether they imply a disposition (they do
not).** A withdrew the dispositional claim. The narrow observation survives; the
inference about program character does not. Left unresolved because the reference class
that would settle it — *gates on critical paths, shape vs content* — has not been
measured by anyone.

**3b. B1 vs B2 — D refines A rather than contradicting it, and the refinement changes
the action.**
A called EC's "0 novel" a B2 coverage ceiling and prescribed "diversify hypothesis
classes." D agrees with the verdict but for a stronger reason, and then breaks the
prescription: *"Does novel EC structure exist outside H?"* has **no finite certificate**,
so **B1 is not establishable in principle** and every possible instrument result is
B2-shaped. Consequently **A's prescribed fix does not terminate** — there is always
another class. D's redirect: adopt *class-relative exhaustion* as the deliverable rather
than treating it as a way-station toward B1. This is the most useful disagreement in the
panel, because A's version would have kept the program hunting a question no instrument
can answer.

**3c. Apollo's status turns on one unmade classification call.**
C: if the 2026-06-16 recombination result (crossover crosses a valley single-step search
cannot) is classed as `search_operator`, Apollo fires — five kills in
`evolutionary_search`, threshold crossed 2026-05-24. If crossover is classed as *part of*
evolutionary search, that class has a June success, the count resets, and **Apollo goes
silent.** Both sensitivities are in the audit output. The actionable question is
therefore not *"is Apollo exhausted"* but **"does crossover belong to the same class as
the mutation-and-select regime that produced five no-signal results?"** — answerable by
Apollo's owner in an afternoon, and it decides redirect vs continue. Under R3 both
answers keep the lane; EXHAUSTION is a redirect signal, not a kill.

## 4. What the panel killed, including mine

| Claim | Fate | Killed by |
|---|---|---|
| Novelty as not-in-deductive-closure (A §3b/§4) | **RETRACTED** — reduces to `{false statements} ∪ {solver timeouts}`; corpus inert because z3 decides modulo its built-in integer theory, not supplied premises | D, executed over 9 claims |
| "Built-and-not-wired is a repeated architectural choice" (A §1) | **WITHDRAWN** — base rate says unwired is ambient | C |
| "The program's characteristic output is a detector it never wires" (C's own draft claim) | **SELF-KILLED** — C built the same claim from 5 instances, then measured the base rate and killed both C's and A's | C, on itself |
| M0 "0% type-II" | **FOSSIL** | A, confirmed at scale by D |
| "Unclimbed tiers R9–R12" | **CATEGORY ERROR** — `TIER_GENS` holds exactly `R0,R1,R2,R3,R5,R6,R7,R8`. R4 and R9–R12 **do not exist**; five sixths of the upper ladder was never built. The R0–R12 ladder is a design document, not an instrument | D |

**The pattern in the kill list is worth more than any individual kill: every lens that
MEASURED survived; the lens that INFERRED died.** A's §1 and C's draft claim were the
same shape of reasoning — N striking instances → a disposition — and both fell to one
base-rate script. C killing its own headline alongside mine is the panel working exactly
as designed.

D's generalization is the deepest single result: **decidability and novelty are
anti-correlated by construction.** Where a closure test terminates, everything true is
already inside the closure, so nothing is ever novel; outside that fragment it returns
`unknown`. The decidable region and the interesting region are disjoint. This is not
z3-specific and it forecloses a whole family of future novelty meters — the standing
test is now: *what does your meter return on (a) a false statement and (b) something the
checker cannot decide?* If both score "novel," it is a timeout detector.

## 5. What I read as the panel's two highest-value items

### 5.1 The stranded calibration library (C) — one command, 29 → 220 modules

`prometheus_math` (307 modules, ~160K LOC) plus `techne.lib` do not import on this host.
The cause is **one line**: `prometheus_math\__init__.py:35` eagerly imports
`number_theory` → `techne\lib\class_number.py:19` → bare `import cypari`. C's
`dependency_door_audit.py` counted the doors: **29/222 importable now → 46 with `cypari`
→ 48 with `snappy` → 220/222 with `knot_floer_homology`**, and `pip install snappy`
alone resolves all three.

This is load-bearing rather than archaeology because **ruling R1 makes mathematics the
program's calibration standard** — an instrument earns the reasoning landscape by first
passing on the math landscape. The library that scores that standard has been **87%
unreachable since April**. Any instrument that "passed on math" this year passed against
29 modules.

C correctly did **not** run the install: it is a change to the user's global interpreter
and James's call. That decision is the single cheapest high-leverage item on the board.
(Honest bound, C's own: an import is a weak positive — it does not certify the
mathematics — and a strong negative. 220 bounds STRANDED from above.)

### 5.2 Where I think C and D are over-reaching

Stated so this synthesis is not just my losses plus everyone else's wins.

- **D's permanence lens undervalues rentals.** D's own §7.2 names the failure mode, but
  the census still reads as though contingent results are second-class. A threshold-
  relative result that correctly redirects a lane has done its job even if a retune
  moves the number. *Durability and usefulness are different axes*, and the panel now
  has a strong instrument for one of them and none for the other.
- **C's base-rate null is right about my §1 and may prove too much.** "Unwired is
  ambient at 55–58%" is a fact about *library modules*. It does not license the
  inference that unwired **gates on critical paths** are unremarkable, because those
  populations differ in consequence, not just in frequency: an unimported module is
  inert, a shape-gate on the critical path emits wrong verdicts. I withdrew §1 because
  I did not measure the right reference class — not because C measured it and I lost.
  **Neither of us has run that measurement, and until someone does, §1 is open, not
  closed.**

## 6. Standing methodological results (promoted out of this panel)

Four transferable rules, each earned by an executed kill today:

1. **Repo state is not program state.** HEAD is a lower bound on activity; run the
   concurrency check before calling anything idle or unclaimed. (A's §0 error: "6.5
   weeks idle" while 281 commits behind origin.)
2. **Base-rate null before any pattern claim.** Define the reference class, count the
   property over all of it, clean the denominator first. Killing your own headline this
   way is a result, not a loss.
3. **Every metric needs both controls.** Negative (can a cheat pass?) *and* positive
   (can anything pass?). A tier nobody has ever passed is unfalsifiable.
4. **Novelty meters are timeout detectors until proven otherwise.** Ask what the meter
   returns on a falsehood and on an undecidable.

## 7. What this panel did not examine

Named so the next reviewer does not mistake coverage for completeness:

- **Gates on critical paths, shape vs content** — the reference class that would settle
  §1 in either direction (§3a, §5.2). Unmeasured by anyone.
- **Whether the mathematics in the stranded 191 modules is correct.** Import is not
  verification (§5.1).
- **Hephaestus and Apollo as live systems.** Both appear only as objects in other
  agents' audits; neither was reviewed from inside, and Aporia lists both as pending.
- **The translator itself.** A's surviving prescription is still unbuilt, so B′ (24
  held-out claims, oracle calibrated 8/8) remains unspent. It must be graded **once**.

---

*Four lenses, one map. The contested cells — is unwired a disposition (§3a), does
class-relative exhaustion replace B1 (§3b), which class does crossover belong to (§3c) —
are where the next work is, and all three are decidable by measurements nobody has run
yet. Two of the synthesizer's own proposals are in the kill table; that is the panel
functioning, not a defect in it. Harmonia A, 2026-08-12.*
