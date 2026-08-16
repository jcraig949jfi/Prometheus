"""F-generic — the specificity control arm for the Metabolization Probe.

Spec `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` v2.0-FINAL §2; prereg
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §4.5 (±5% per-task token matching) and §10
(open item: "F-generic final text and its ±5% token-matching tolerance — Charon's contract").

ARM ROLE. F-generic answers exactly one question: *is Prometheus's residue better than a
sophisticated "think harder" prompt?* It replaced v1.x's F-format because F-format was too
weak to be a real control. A weak F-generic inflates the specificity margin
(`F-prom-retrieved − F-generic`) in Prometheus's favour, so the authoring standard is
adversarial-to-us: this text is meant to be the strongest general reasoning guidance that can
be written **without** any access to the tasks, the residue, or the answers.

CLEAN-ROOM. Authored by Charon before opening any packet sample, residue census, D3 pool, or
task manifest. Attestation with the exact read-set:
`charon/probe/F_GENERIC_CLEANROOM_2026-08-16.md`.

TWO AUTHORING CONSTRAINTS, both mechanically tested (`tests/test_f_generic.py`):

1. **Domain-general, not task-general.** The text is calibrated to the *modality* — a solver
   reasoning without tools toward a checkable verdict — and carries no procedure, heuristic,
   or vocabulary specific to any problem domain. Tailoring it to the task families would make
   it a partial oracle rather than a control, and would destroy the meaning of the specificity
   margin in the opposite direction from a weak control.
2. **Zero verdict tokens.** `ergon.probe.extract._VERDICT_TOKEN` is `\\b(true|false)\\b`,
   case-insensitive. No whole-word `true`/`false` appears anywhere below, so F-generic can
   never collide with the frozen extractor or hand a binary task its answer vocabulary.

TOKEN MATCHING. Deterministic greedy fill over a fixed priority order, whole units first, then
whole sentences from the next unit. Never pads by repetition: repeated advice is not stronger
advice, and repetition would weaken the control exactly on the tasks carrying the most residue
— an arm-correlated bias pointing in Prometheus's favour. Where the pool cannot reach the
window, the task is reported `SATURATED` and excluded from the specificity-margin comparison
rather than matched dishonestly. Non-`MATCHED` statuses never affect the primary endpoint
(`F-prom-retrieved − F-null`), which does not involve this arm.

— Charon, 2026-08-16.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ergon.probe.assemble import count_tokens

ARM = "F-generic"
VERSION = "f-generic-v1.0"
DEFAULT_TOLERANCE = 0.05  # prereg §4.5: ±5%

# --------------------------------------------------------------------------- the text

PREAMBLE = (
    "Guidance for reasoning carefully toward a verifiable answer. These are the failure "
    "patterns that most often decide the outcome, ordered by how often they decide it. They "
    "are general: nothing here describes this problem, its subject, or its answer."
)

# Ordered by decisiveness for a solver working without tools toward a checkable verdict.
# The order is preregistered: the strongest material is always included, so growth in length
# adds progressively weaker material and never dilutes the top of the prompt.
PRINCIPLES: list[dict[str, str]] = [
    {
        "headline": (
            "Compute; do not recognize. A statement that resembles the kind of statement "
            "that usually holds is not thereby established. If the claim reduces to an "
            "arithmetic or structural fact, carry that work out explicitly, in steps you "
            "could show someone."
        ),
        "note": (
            "Surface familiarity is the cheapest and most confident-feeling signal available, "
            "and it is uncorrelated with correctness on any problem built to sit near a "
            "boundary. The cases engineered to defeat pattern-matching are exactly those "
            "where the pattern is nearly right: a quantity just off the value that would make "
            "the claim work, a structure matching a canonical one in every visible respect but "
            "one. Recognition answers 'what family is this?'; the question asked is 'what is "
            "the value?'"
        ),
        "signature": (
            "your justification, written out, contains no line in which a specific quantity is "
            "produced. You have named a rule, cited a resemblance, or appealed to what is "
            "typical, and then stated a conclusion. If deleting every numeral from your "
            "reasoning leaves it intact, you did not compute."
        ),
        "check": (
            "point at the single line where the answer is decided. If no such line exists, the "
            "work is not finished. Write the decisive quantity down and carry it forward "
            "explicitly rather than holding it in mind."
        ),
    },
    {
        "headline": (
            "Restate the claim before working on it, fixing its quantifier, its direction, and "
            "its scope. Solve the claim in front of you, not the one it resembles."
        ),
        "note": (
            "Most avoidable errors are answers to a slightly different question: the converse "
            "in place of the claim, 'some' read as 'every', a strict bound read as inclusive, "
            "a condition on one object silently transferred to another. The restatement is "
            "cheap, and it is the only step that catches this class before the effort is spent."
        ),
        "signature": (
            "your conclusion is defensible but does not address the asserted relation — you "
            "established something adjacent and stopped. Re-reading the claim after finishing "
            "feels like it changes the problem."
        ),
        "check": (
            "write the claim as an explicit assertion with its quantifier in front — 'for every "
            "X, P' or 'there is an X with P' — and confirm each symbol refers to what you think "
            "it does. Then confirm the direction: which side implies which."
        ),
    },
    {
        "headline": (
            "One counterexample settles a universal claim; any number of confirming instances "
            "does not. To overturn, hunt a single bad case; to establish, an argument covering "
            "all cases is required."
        ),
        "note": (
            "This asymmetry decides how a limited budget should be spent. If the claim is "
            "universal, the cheapest decisive outcome is one violating instance, and it is "
            "worth hunting deliberately where the claim is under most strain. If no violation "
            "appears after a genuine search, that is not establishment — it is a failed "
            "refutation, and the two must not be merged."
        ),
        "signature": (
            "you have checked three or four instances, they all behaved, and your confidence "
            "rose sharply. Confidence that rises with instance count on a universal claim is "
            "tracking effort spent, not evidence gathered."
        ),
        "check": (
            "name the region where the claim is most likely to break — extreme magnitudes, "
            "degenerate configurations, the boundary of a stated condition — and test there "
            "first, rather than at a convenient middle."
        ),
    },
    {
        "headline": (
            "Order checks by decisiveness per unit of effort. Before committing to a long "
            "derivation, ask whether a short computation could settle the question outright."
        ),
        "note": (
            "There is frequently a single quantity whose value determines the outcome, "
            "reachable in a few operations, while the obvious route is a full construction. "
            "Necessary conditions are the usual source: a parity, a magnitude comparison, a "
            "residue, a count that must match. Any of them, violated, ends the problem at once; "
            "satisfied, it cost little and it constrained the remaining space."
        ),
        "signature": (
            "you are deep in a construction and have not yet produced any quantity that could "
            "have ended the problem early. Long uninterrupted derivations without a decision "
            "point are where errors accumulate unobserved."
        ),
        "check": (
            "list two or three necessary conditions the claim implies, cheapest first, and "
            "evaluate them in that order before starting the main line of work."
        ),
    },
    {
        "headline": (
            "The assumptions that cause errors are the ones never stated, because they were "
            "never noticed. List what you are taking for granted, then ask which of it the "
            "problem actually grants."
        ),
        "note": (
            "Assumptions imported from the typical case are the dangerous class — that a "
            "quantity is positive, that a decomposition is unique, that an operation commutes "
            "here as it does elsewhere, that a stated condition holds throughout rather than at "
            "one point. Each is usually harmless, which is precisely why it stays invisible "
            "when it is not."
        ),
        "signature": (
            "a step has no justification you could give if challenged beyond 'that is how it "
            "normally works'. Or: your argument would read identically if a condition stated in "
            "the problem were deleted — meaning you never used it, and either it is decorative "
            "or you have missed its role."
        ),
        "check": (
            "for each condition given in the problem, point at the step that consumes it. An "
            "unconsumed condition signals that your reading is wrong or your argument is "
            "incomplete."
        ),
    },
    {
        "headline": (
            "Test the edges: the smallest admissible case, the largest, zero, one, equality at "
            "a bound, the empty or trivial configuration. Rules are written for the interior "
            "and break at the rim."
        ),
        "note": (
            "Boundary behaviour is where definitions stop agreeing with intuition, and where an "
            "argument sound in general quietly requires a quantity to be nonzero, a collection "
            "to be nonempty, or a comparison to be strict. A claim built to be difficult will "
            "often sit exactly at such a rim, differing from a clean case by one unit."
        ),
        "signature": (
            "your argument silently divides, inverts, takes an extremum over a possibly empty "
            "collection, or assumes a strict comparison where equality is admissible."
        ),
        "check": (
            "instantiate the smallest and the most degenerate admissible case and run the claim "
            "on them by hand. If a case is excluded, confirm the problem excludes it rather "
            "than assuming it does."
        ),
    },
    {
        "headline": (
            "When a result comes out wrong, find the earliest step that is already wrong, not "
            "the last one you looked at. Errors propagate, so the visible symptom is usually "
            "far downstream of its cause."
        ),
        "note": (
            "The efficient method is bisection: take a point midway through the work, evaluate "
            "the state there independently, and determine whether it is already corrupted. That "
            "halves the search each time and terminates quickly. Re-reading forward from the "
            "start instead tends to re-endorse the original error, because it re-runs the "
            "reasoning that produced it."
        ),
        "signature": (
            "you have found and patched something wrong near the end, but the result is still "
            "wrong, or is now right for a reason you cannot articulate. Patches applied at the "
            "point of symptom are how one error becomes several."
        ),
        "check": (
            "name the last step you can confirm was correct and the first you can confirm was "
            "not. The fault lies between them; work only there."
        ),
    },
    {
        "headline": (
            "To verify, re-derive by a different route; do not re-read. Reading your own work "
            "re-runs the reasoning that produced the error and reliably reproduces it."
        ),
        "note": (
            "Two derivations that share a step share its failure, so a check is worth only its "
            "independence. A second route reaching the same result by different operations — a "
            "different decomposition, a different order, an approximation compared against an "
            "exact form — is evidence. A careful second reading is very nearly none."
        ),
        "signature": (
            "your verification passed quickly and comfortably, and consisted of confirming that "
            "each line follows from the one above it. That checks transcription, not the choice "
            "of method or the reading of the problem."
        ),
        "check": (
            "before verifying, name the route you will use and confirm it does not share the "
            "step you are least sure of. If every available route shares that step, say so — "
            "the uncertainty is real and belongs in the answer."
        ),
    },
    {
        "headline": (
            "Distinguish what you established from what you merely failed to overturn. A search "
            "that found no problem is a weaker statement than an argument that no problem "
            "exists, and it must be reported as the weaker one."
        ),
        "note": (
            "The two are easy to conflate under pressure, because from the inside they feel "
            "alike: in both cases nothing is currently objectionable. They differ in what would "
            "have to happen for them to be wrong. An established result is wrong only if a step "
            "is wrong; an unrefuted one is wrong whenever the search missed a case — which "
            "depends entirely on where you looked."
        ),
        "signature": (
            "asked why the claim holds, your best answer describes your search rather than the "
            "claim's structure — 'I tried a number of cases and nothing broke'."
        ),
        "check": (
            "state which of the two you have. If it is the weaker one, state the region your "
            "search covered, because that is the actual content of the finding."
        ),
    },
    {
        "headline": (
            "Check that the size of your answer is possible before checking that it is right. A "
            "quantity off by orders of magnitude signals a structural error that no amount of "
            "local checking will surface."
        ),
        "note": (
            "Order-of-magnitude estimation is cheap, independent of the detailed route, and "
            "catches whole classes of error at once: a dropped or duplicated factor, an exponent "
            "misread, a sum treated as a product, a rate confused with a total. It also "
            "calibrates expectation before the work, so a surprising result is recognizable as "
            "surprising."
        ),
        "signature": (
            "the answer is a quantity you cannot roughly justify — you could not say within a "
            "factor of ten what it ought to be, independently of the computation that produced "
            "it."
        ),
        "check": (
            "estimate the answer's scale by an independent crude argument before finishing, and "
            "compare. A mismatch is a finding, not a nuisance."
        ),
    },
    {
        "headline": (
            "Identify what must be preserved and check that it was. An invariant is the most "
            "economical error detector available: one violated quantity condemns every step "
            "that could have broken it."
        ),
        "note": (
            "Useful invariants are usually simple — a total that must be conserved, a parity or "
            "residue that the operations cannot change, a monotone quantity, a count of objects, "
            "a dimension or a degree. Choosing one before the work makes it a running check "
            "rather than a post-hoc rescue, and it costs almost nothing to carry."
        ),
        "signature": (
            "you cannot name any quantity your operations were supposed to preserve. Then no "
            "cheap check is available to you, and every error has to be found by inspection."
        ),
        "check": (
            "name one invariant before starting and evaluate it at the start, at the midpoint, "
            "and at the end. Where it first changes is where the error is."
        ),
    },
    {
        "headline": (
            "Separate 'I cannot express this' from 'I cannot solve this'. They feel identical "
            "from the inside and call for opposite responses: a better encoding, versus more "
            "work inside the current one."
        ),
        "note": (
            "A representational obstruction shows up as an inability to write the question down "
            "in a form that admits a decision procedure — the objects are of a kind your method "
            "does not handle, or the claim concerns a structure you have no notation for. "
            "Further effort inside a representation that cannot express the problem produces "
            "confident wrong answers, because the version you can express is a different "
            "problem."
        ),
        "signature": (
            "you keep re-approaching and each attempt stalls at the same place, at the point of "
            "setting the problem up rather than inside the work. Or: you have quietly "
            "substituted a simpler object for the one asked about, and are now solving the "
            "substitute."
        ),
        "check": (
            "ask whether the object you are manipulating is the object in the claim. If it is a "
            "proxy, name the gap between them and decide whether that gap changes the answer."
        ),
    },
    {
        "headline": (
            "Fix conventions before computing: base and units, indexing from zero or one, "
            "inclusive or exclusive bounds, orientation and sign, which argument comes first. "
            "Convention errors survive every check that assumes the convention."
        ),
        "note": (
            "These are not pedantry; they are the errors that leave an otherwise correct "
            "derivation one unit or one factor away, and they are invisible to review because "
            "reader and writer supply the same default. Notation inherited from different "
            "sources inside one problem is the usual entry point — two conventions, silently "
            "mixed."
        ),
        "signature": (
            "your answer is off by exactly one, by a factor equal to a count you used, or by a "
            "sign. Small structured discrepancies are convention errors far more often than "
            "they are arithmetic ones."
        ),
        "check": (
            "state each convention explicitly once, at the top, and confirm every expression "
            "obeys the stated convention rather than the one it was originally written in."
        ),
    },
    {
        "headline": (
            "When an approach fails, state why it failed before choosing the next one. A retry "
            "that does not name the obstruction tends to reproduce it in new clothing."
        ),
        "note": (
            "The diagnosis is what makes the next attempt different in the respect that matters. "
            "Without it, subsequent attempts vary on the wrong axes — different arrangement, "
            "same blocking step — and the budget is spent re-encountering one obstruction "
            "repeatedly. With it, the next approach can be chosen precisely for not sharing "
            "that step."
        ),
        "signature": (
            "your second and third attempts stall at the same point as the first, and you can "
            "describe what you tried but not what stopped you."
        ),
        "check": (
            "write one sentence naming the step that could not be completed and the reason. "
            "Then require the next approach to avoid that step, and confirm it does before "
            "starting."
        ),
    },
    {
        "headline": (
            "Decide in advance what would tell you the current approach is dead, and honour it. "
            "Effort spent past that point is not persistence; it is budget the remaining "
            "approaches needed."
        ),
        "note": (
            "End a line of work when the obstruction has recurred without change, when the cost "
            "of the next step exceeds what remains, or when a cheaper route has become visible. "
            "Say which of the three ended it, because the reason determines whether the "
            "approach is wrong or merely expensive — and record where it stopped, since a "
            "partial result with a known stopping point is usable and an abandoned one is not."
        ),
        "signature": (
            "you cannot say what would make you abandon the current line. Then no evidence can "
            "end it, and it will end only when the budget does."
        ),
        "check": (
            "before committing to a long route, name its kill condition. On reaching it, stop "
            "and report the state honestly rather than continuing past it."
        ),
    },
    {
        "headline": (
            "Break the claim into subclaims that can each be checked on their own, and check "
            "them separately. A conclusion resting on one long undivided argument has no "
            "checkable interior."
        ),
        "note": (
            "Decomposition converts one hard verification into several easy ones and localizes "
            "any error to a single part. The useful cut is where the parts are independent — "
            "each stands or falls without reference to the others — rather than merely "
            "sequential. Parts that cannot be stated without each other are not a decomposition; "
            "they are the original problem rewritten."
        ),
        "signature": (
            "you cannot point at any intermediate result that would still be meaningful if the "
            "rest of the argument were removed. Everything depends on everything, so nothing "
            "can be checked."
        ),
        "check": (
            "write down each subclaim as a standalone statement and confirm it makes sense in "
            "isolation. Then confirm that the conjunction of the subclaims actually implies the "
            "original claim, which is a separate step and is often the one skipped."
        ),
    },
    {
        "headline": (
            "Work the smallest nontrivial instance completely before attempting the general "
            "case. A fully worked small case exposes the structure the general argument needs."
        ),
        "note": (
            "The small case is cheap, it is checkable by inspection, and it usually reveals "
            "which features of the problem are doing the work and which are decoration. It also "
            "produces a concrete object to test the general argument against: an argument that "
            "does not reproduce the known small case is wrong, and you find that out early "
            "rather than at the end."
        ),
        "signature": (
            "you moved directly to the general statement, and when it produces something "
            "surprising you have nothing concrete to compare it with."
        ),
        "check": (
            "solve the smallest instance that is not degenerate, by hand, completely. Keep the "
            "result. Every later claim must be consistent with it."
        ),
    },
    {
        "headline": (
            "Keep exact and approximate quantities apart, and never let an approximation decide "
            "a strict comparison. An estimate can suggest an answer; it cannot settle a "
            "boundary."
        ),
        "note": (
            "Approximation is the right tool for scale and the wrong tool for decisions near "
            "equality, which is exactly where difficult problems are placed. The danger is that "
            "an approximate value silently acquires the authority of an exact one after being "
            "carried through a few steps, and the final comparison is then made against a "
            "quantity whose error bar was never tracked."
        ),
        "signature": (
            "your decisive comparison is between two quantities that are close, and at least "
            "one of them arrived by rounding, truncation, or estimation."
        ),
        "check": (
            "mark every approximate quantity as approximate and carry that mark. If the "
            "decision depends on one, either bound the error explicitly or redo that part "
            "exactly."
        ),
    },
    {
        "headline": (
            "A 'without loss of generality' step is a claim that requires justification. "
            "Symmetry that is assumed rather than established is one of the most productive "
            "sources of confident error."
        ),
        "note": (
            "The step is legitimate when there is an actual transformation carrying the general "
            "case to the special one while preserving everything the claim depends on. It is "
            "illegitimate when the special case merely feels representative. The failure is "
            "hard to see afterwards, because the remaining argument is usually correct — about "
            "the smaller problem you substituted."
        ),
        "signature": (
            "you reduced to a convenient case and cannot name the map that performs the "
            "reduction, or the map exists but does not preserve a condition the claim uses."
        ),
        "check": (
            "name the transformation, name what it preserves, and confirm that what it "
            "preserves includes everything the claim relies on."
        ),
    },
    {
        "headline": (
            "Keep three things separate: what is given, what you have assumed, and what you "
            "want. Merging them is how a goal becomes a premise."
        ),
        "note": (
            "Circular reasoning almost never looks circular from the inside; it looks like "
            "progress, because the desired statement was quietly admitted as available several "
            "steps earlier and then used. Maintaining the separation explicitly is the cheapest "
            "structural defence, and it also makes visible the moment an assumption was "
            "introduced to make a step work."
        ),
        "signature": (
            "the statement you are trying to establish, or something equivalent to it, appears "
            "as a justification somewhere above. Or an assumption entered exactly where the "
            "argument was blocked."
        ),
        "check": (
            "list the given conditions, the added assumptions, and the goal in three separate "
            "places, and confirm no item from the third list appears in support of the argument."
        ),
    },
    {
        "headline": (
            "Consider what would have to hold for the claim to fail. The shape of the failing "
            "case is often easier to characterize than the claim itself, and it directs the "
            "search."
        ),
        "note": (
            "Negating the claim turns a universal statement into an existence statement, which "
            "is concrete: some object, with stated properties, must exist. Those properties are "
            "usually restrictive enough to search directly, and sometimes restrictive enough to "
            "be immediately impossible — which settles the original claim. Either outcome is "
            "progress, and both are cheaper than a direct assault."
        ),
        "signature": (
            "you have been trying to establish the claim head-on for some time and cannot "
            "describe what a violating instance would even look like."
        ),
        "check": (
            "write the negation explicitly as 'there exists an object such that…', list the "
            "properties that object must have, and check whether any of them conflict."
        ),
    },
    {
        "headline": (
            "Generate a second reading of the problem before committing to the first. The first "
            "interpretation arrives with unearned confidence because it arrived first."
        ),
        "note": (
            "Ambiguity in a problem statement is usually invisible to the reader who resolved it "
            "instantly. Deliberately constructing an alternative reading costs a few seconds and "
            "either confirms the original or reveals that the whole effort was about to be spent "
            "on the wrong question. Where two readings survive, say which one you took."
        ),
        "signature": (
            "you never considered a second reading, and your answer depends on a resolution you "
            "cannot remember making."
        ),
        "check": (
            "state one alternative reading of the claim and give the reason you rejected it. If "
            "you cannot reject it, answer under the reading you chose and say which it was."
        ),
    },
    {
        "headline": (
            "Reusing a result requires re-checking its preconditions in the new context. A "
            "result imported without its conditions is a guess wearing the authority of an "
            "established fact."
        ),
        "note": (
            "Standard results are stated with hypotheses, and those hypotheses are exactly the "
            "part that gets dropped in transit — because the result is remembered as a formula "
            "and the conditions are remembered as fine print. The transplant usually works, "
            "which is why the case where it does not is so rarely caught."
        ),
        "signature": (
            "you invoked a general fact and cannot immediately state the conditions under which "
            "it holds, or you can state them but did not verify them here."
        ),
        "check": (
            "for each result you invoke, write its conditions and tick each one against the "
            "current objects before using the conclusion."
        ),
    },
    {
        "headline": (
            "Prefer structural reasons to numerical coincidence. Agreement in several cases is "
            "the weakest form of evidence and the most persuasive one."
        ),
        "note": (
            "A structural reason explains why the relation must hold and thereby predicts where "
            "it would fail; a coincidence explains nothing and predicts nothing. Coincidences "
            "are common in small samples and in constructed problems, and a claim engineered to "
            "be difficult may agree on every case a person would naturally try."
        ),
        "signature": (
            "your entire support is that the relation held on the instances you happened to "
            "examine, and you cannot say what mechanism would produce it."
        ),
        "check": (
            "state the mechanism in one sentence. If you cannot, treat the pattern as a "
            "hypothesis to be attacked rather than as a result to be reported."
        ),
    },
    {
        "headline": (
            "Order the work by dependency and evaluate only what is needed. Computing "
            "everything available is not thoroughness; it is a way of running out of budget "
            "before the decisive quantity."
        ),
        "note": (
            "Most problems have one decisive quantity and several quantities that are merely "
            "obtainable. Working the obtainable ones first feels productive and can consume the "
            "whole budget, and it also lengthens the chain in which an error can hide. Identify "
            "what the answer actually depends on, and compute towards that."
        ),
        "signature": (
            "you have produced several correct intermediate values and none of them has changed "
            "what you believe about the answer."
        ),
        "check": (
            "before each computation, say which decision its result will change. If it changes "
            "none, do not perform it."
        ),
    },
    {
        "headline": (
            "A precise partial answer is worth more than a vague complete one. Say exactly what "
            "you established and exactly where you stopped."
        ),
        "note": (
            "Precision about the boundary of your result is what makes it usable by anyone "
            "afterwards, including you. A vague complete-sounding answer cannot be built on, "
            "cannot be checked, and cannot be corrected, because there is no statement sharp "
            "enough to be wrong. Sharpness is worth more than coverage."
        ),
        "signature": (
            "your answer would be difficult for someone else to disagree with specifically. "
            "Unfalsifiable phrasing usually indicates uncertainty being smoothed over rather "
            "than reported."
        ),
        "check": (
            "state the result as a sharp assertion, then state the conditions under which you "
            "established it. If those conditions are narrower than the question, say so plainly."
        ),
    },
    {
        "headline": (
            "Watch for symbols that change meaning mid-argument. A reused name is the quietest "
            "error available, because every individual step remains locally correct."
        ),
        "note": (
            "Rebinding happens when a symbol is introduced for one role, released, and picked up "
            "again for another, or when the same letter names two objects in two sources being "
            "combined. Because each step reads correctly on its own, the error is invisible to "
            "line-by-line checking and is found only by asking what each symbol denotes at each "
            "point."
        ),
        "signature": (
            "the same letter appears in two places where it must denote different objects, or "
            "an index is reused inside the scope where it is already bound."
        ),
        "check": (
            "list every symbol with its meaning and its scope, once. Rename anything that serves "
            "two roles before continuing."
        ),
    },
    {
        "headline": (
            "Distinguish necessary from sufficient conditions, in both directions. Establishing "
            "a necessary condition does not establish the claim, and refuting a sufficient one "
            "does not refute it."
        ),
        "note": (
            "This is the most common structural error in otherwise careful work: a condition is "
            "verified, and the verification is treated as settling the question in whichever "
            "direction was wanted. A necessary condition can only rule out; a sufficient "
            "condition can only rule in. Which one you have determines what your check is "
            "permitted to conclude."
        ),
        "signature": (
            "you checked a condition, it came out as you hoped, and you stopped — without "
            "asking whether that condition was capable of settling the question in that "
            "direction."
        ),
        "check": (
            "for each condition you test, write whether it is necessary, sufficient, or both, "
            "and state in advance what each outcome would license you to conclude."
        ),
    },
    {
        "headline": (
            "When two methods disagree, locate the disagreement. Do not average them, and do "
            "not adopt the one that is more convenient or arrived more recently."
        ),
        "note": (
            "A disagreement is the most informative event available: one method is wrong in a "
            "way you can now find, and the discrepancy itself points at where. Resolving it by "
            "preference discards that information and keeps an unknown error. The resolution is "
            "always the same shape — find the first point at which the two computations differ, "
            "and determine which is correct there."
        ),
        "signature": (
            "you obtained two answers, chose one, and cannot say what was wrong with the other."
        ),
        "check": (
            "line the two derivations up and find the earliest point of divergence. Settle that "
            "point before accepting either result."
        ),
    },
    {
        "headline": (
            "Choose the representation in which the binding constraint is explicit. Much of the "
            "difficulty in a problem is an artefact of the form it was handed to you in."
        ),
        "note": (
            "The same object can be written so that the decisive property is immediate or so "
            "that it is invisible, and effort spent inside an unhelpful form is usually effort "
            "spent rediscovering the form. Before a long computation, ask whether a different "
            "encoding makes the constraint visible. This is cheap to try and occasionally "
            "collapses the entire problem."
        ),
        "signature": (
            "your work consists largely of manipulation whose purpose is to expose a property "
            "you already know matters."
        ),
        "check": (
            "name the property the answer depends on, and ask which form displays it directly. "
            "If one does, move there before computing."
        ),
    },
    {
        "headline": (
            "Read the question again at the end and confirm you answered that question, in the "
            "form it asked for. The last step of the work is not the answer to the problem."
        ),
        "note": (
            "Work drifts: an intermediate quantity becomes the focus, a stronger statement gets "
            "established than the one requested, or the result is delivered in a form the "
            "question did not ask for. All three are complete work reported as an incorrect "
            "answer, and all three are caught by one final reading with the original wording in "
            "front of you."
        ),
        "signature": (
            "your final line reports the last quantity you computed rather than a response to "
            "the question as worded."
        ),
        "check": (
            "put the original claim beside your conclusion and confirm they address the same "
            "assertion, in the same direction, at the same scope."
        ),
    },
    {
        "headline": (
            "Prefer a check that fails loudly to one that fails quietly. A verification that "
            "cannot visibly go wrong is providing reassurance rather than information."
        ),
        "note": (
            "Checks differ in what they do when the thing being checked is broken. A good check "
            "produces an unmistakable, specific discrepancy; a poor one degrades into agreement, "
            "because it re-uses the suspect quantity, or because its tolerance is wide enough to "
            "absorb the error. The second kind is worse than no check, since it converts an open "
            "question into unwarranted confidence."
        ),
        "signature": (
            "your check has never failed, on anything, and you cannot describe the input that "
            "would make it fail."
        ),
        "check": (
            "for each verification, state what it would look like if it caught something. If "
            "there is no such appearance, replace the check."
        ),
    },
    {
        "headline": (
            "Be suspicious of a result that arrives too easily on a problem posed as difficult. "
            "Ease is evidence about which problem you solved."
        ),
        "note": (
            "Problems are usually posed at some level of intended difficulty, and an answer that "
            "falls out in one step has often fallen out of a simplification introduced without "
            "notice — a dropped condition, an assumed regularity, a substituted object. This is "
            "not a reason to distrust every quick answer; it is a reason to spend one deliberate "
            "step asking which difficulty was avoided and whether it was avoidable."
        ),
        "signature": (
            "the problem's stated conditions include something your solution never used, and the "
            "solution took a fraction of the effort the setup implies."
        ),
        "check": (
            "name the difficulty the problem appears designed to present, and say how your route "
            "handles it. If your route never met it, find out why."
        ),
    },
    {
        "headline": (
            "When arguing by cases, establish that the cases are exhaustive before working any "
            "of them. A missing case is invisible from inside the cases you listed."
        ),
        "note": (
            "Case analysis fails at its seams far more often than inside a case: overlapping "
            "cases are harmless, but a gap is fatal and produces an argument that looks complete "
            "because every case present was handled correctly. Exhaustiveness is a separate "
            "claim from the case work and deserves its own line."
        ),
        "signature": (
            "you can list your cases but cannot state the principle that guarantees there are no "
            "others — the split was made by enumeration of what came to mind."
        ),
        "check": (
            "state the partition rule and confirm that every admissible object falls under at "
            "least one case, including the degenerate ones."
        ),
    },
    {
        "headline": (
            "Distinguish sameness of form from sameness of object. Two things written alike need "
            "not be the same thing, and the same thing may be written unrecognizably."
        ),
        "note": (
            "Matching on appearance is fast and is right often enough to become habitual. It "
            "fails in both directions: distinct objects sharing a form invite an unjustified "
            "transfer of properties, and a single object in two forms invites the conclusion "
            "that two independent facts have been established when one has been stated twice."
        ),
        "signature": (
            "you transferred a property between two expressions because they look alike, without "
            "checking that they denote the same object under the same conditions."
        ),
        "check": (
            "before treating two expressions as interchangeable, confirm they agree as objects — "
            "on a concrete instance if nothing else is available."
        ),
    },
    {
        "headline": (
            "Record your state as you go, in a form you could hand to someone else. Work that "
            "exists only in mind is lost at the first interruption and cannot be checked at all."
        ),
        "note": (
            "Written intermediate state costs little and pays three times: it makes bisection "
            "possible when the result is wrong, it prevents the silent drift of a quantity that "
            "is being held rather than recorded, and it converts an abandoned attempt into a "
            "usable partial result. The habit matters most exactly when effort is high and the "
            "temptation to carry state mentally is strongest."
        ),
        "signature": (
            "asked where a particular value came from, you would have to redo the work to answer."
        ),
        "check": (
            "write each decisive quantity down with the step that produced it, at the moment it "
            "is produced rather than afterwards."
        ),
    },
    {
        "headline": (
            "Confirm the answer is the right kind of thing before asking whether it is the right "
            "value. A response in the wrong category is wrong regardless of the work behind it."
        ),
        "note": (
            "Type errors survive arithmetic checking entirely, because every operation on the "
            "way was valid — a count returned where a proportion was asked for, a set where an "
            "element was wanted, a relation where a decision was wanted. The check is immediate "
            "and is skipped because the answer's category feels too obvious to verify."
        ),
        "signature": (
            "your answer cannot be substituted directly into the question as posed without "
            "rephrasing."
        ),
        "check": (
            "read the question's final clause and confirm your answer is an instance of exactly "
            "what it names."
        ),
    },
]

# --------------------------------------------------------------------------- unit ordering

_TIERS = ("headline", "note", "signature", "check")
_TIER_PREFIX = {
    "headline": "{n}. ",
    "note": "Note on {n}: ",
    "signature": "Failure signature, {n}: ",
    "check": "Check, {n}: ",
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.:;])\s+")


@dataclass(frozen=True)
class Unit:
    uid: str
    text: str
    tokens: int


def units() -> list[Unit]:
    """The preregistered priority order: tier-major, principle-minor.

    Tier-major means every principle's headline is present before any elaboration is, so a
    short packet gets the fifteen strongest statements rather than the first four principles
    in full. Each elaboration self-labels with its principle number, so the grouping stays
    readable at any length. This order is frozen; changing it changes the arm.
    """
    out = [Unit("preamble", PREAMBLE, count_tokens(PREAMBLE))]
    for tier in _TIERS:
        for i, principle in enumerate(PRINCIPLES, start=1):
            text = _TIER_PREFIX[tier].format(n=i) + principle[tier]
            out.append(Unit(f"{tier}:{i}", text, count_tokens(text)))
    return out


def pool_tokens() -> int:
    """Total tokens available if every unit is emitted. The saturation point."""
    return count_tokens(render_all())


def render_all() -> str:
    return "\n\n".join(u.text for u in units())


# --------------------------------------------------------------------------- matching


@dataclass
class GenericPacket:
    """One task's F-generic text plus everything needed to audit the match."""

    text: str
    tokens: int
    target_tokens: int
    status: str
    unit_ids: list[str] = field(default_factory=list)
    partial_unit: str | None = None
    version: str = VERSION

    @property
    def matched(self) -> bool:
        return self.status == "MATCHED"

    def header(self) -> dict:
        return {
            "arm": ARM,
            "version": self.version,
            "target_tokens": self.target_tokens,
            "tokens": self.tokens,
            "status": self.status,
            "units": len(self.unit_ids),
            "partial_unit": self.partial_unit,
        }


def render_f_generic(target_tokens: int, tolerance: float = DEFAULT_TOLERANCE) -> GenericPacket:
    """Build the F-generic packet matched to `target_tokens` within ±`tolerance`.

    `target_tokens` is this task's `F-prom-retrieved` token count, measured with the same
    frozen `count_tokens` every arm uses (prereg §4.5; M1_STATUS §7b — one approximation,
    stamped, shared, so no arm is matched against a different ruler).

    Statuses, all reported, none silent:

    - ``MATCHED``                  — landed inside [0.95T, 1.05T]. The only status admissible
                                     in the specificity-margin comparison.
    - ``SATURATED``                — the whole pool is shorter than 0.95T. Reported and
                                     excluded from the specificity margin; matching upward
                                     would require repetition, and repeated advice is not
                                     stronger advice.
    - ``UNDER-FLOOR``              — the preamble alone exceeds 1.05T. Only reachable for very
                                     small packets.
    - ``UNMATCHABLE-GRANULARITY``  — no whole-sentence prefix of the next unit lands in the
                                     window. Recorded rather than fudged.

    Non-``MATCHED`` statuses never touch the primary endpoint, which is
    ``F-prom-retrieved − F-null`` and does not involve this arm.
    """
    if target_tokens <= 0:
        raise ValueError("target_tokens must be positive; F0 carries no packet (prereg §4.5)")

    lo = target_tokens * (1.0 - tolerance)
    hi = target_tokens * (1.0 + tolerance)

    pool = units()
    chosen: list[Unit] = []
    text = ""

    for unit in pool:
        candidate = f"{text}\n\n{unit.text}" if text else unit.text
        if count_tokens(candidate) > hi:
            break
        text = candidate
        chosen.append(unit)
    else:
        # Pool exhausted without exceeding the ceiling.
        total = count_tokens(text) if text else 0
        status = "MATCHED" if total >= lo else "SATURATED"
        return GenericPacket(text, total, target_tokens, status, [u.uid for u in chosen])

    if not chosen:
        return GenericPacket("", 0, target_tokens, "UNDER-FLOOR", [])

    total = count_tokens(text)
    if total >= lo:
        return GenericPacket(text, total, target_tokens, "MATCHED", [u.uid for u in chosen])

    # Whole units cannot close the gap: add whole sentences from the next unit only.
    nxt = pool[len(chosen)]
    partial = None
    for sentence in _SENTENCE_SPLIT.split(nxt.text):
        candidate = f"{text} {sentence}" if partial else f"{text}\n\n{sentence}"
        if count_tokens(candidate) > hi:
            break
        text, partial = candidate, nxt.uid

    total = count_tokens(text)
    if total >= lo:
        return GenericPacket(
            text, total, target_tokens, "MATCHED", [u.uid for u in chosen], partial_unit=partial
        )
    return GenericPacket(
        text,
        total,
        target_tokens,
        "UNMATCHABLE-GRANULARITY",
        [u.uid for u in chosen],
        partial_unit=partial,
    )
