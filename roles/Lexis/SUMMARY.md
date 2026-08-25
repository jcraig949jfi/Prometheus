# Lexis — slice summary, three depths

**Date:** 2026-08-25 · **Covers:** the library-learning study (8 passes), the Lexis seat, the
non-LLM control ladder, and the Ignis close-out.

---

## TL;DR

**Apollo's ceiling is the wall a five-year literature exists to break — and we proved that one day
before finding the literature.**

O1's exhaustive enumeration (2026-08-23) established that 0.833 is an *expressivity* limit of
Apollo's blackboard vocabulary, not a search limit: 1.74M type-correct pipelines, nothing better,
16.7% of its own battery unreachable at any search quality. The next day Aporia surfaced DreamCoder,
and behind it four research families whose entire purpose is growing the vocabulary a search runs
over.

Six findings survived eight passes of trying to break them:

1. **Four families, not one lineage** — MIT library learning, UW e-graphs, Chalmers theory
   exploration, LLM tool/skill libraries. Twitch (2026) is the junction, not a descendant.
2. **The forge already has a ratchet; Apollo doesn't.** T1→T2→T3, each tier's primitives are the
   prior tiers' passing tools. Measured this session: of the twelve reasoning primitives imported by
   the six admitted T2 tools, **zero are called anywhere.**
3. **Compressivity guarantees usage by construction; novelty-gating forfeits it.** An abstraction
   admitted *because it already recurs* cannot be unused. Gate B rewards difference from the library,
   then supplies no consumer. 0% usage is that design's predicted outcome.
4. **Cross-domain primitive transfer is unreported across all four families** (~20 systems, checked
   specifically to falsify). It is simultaneously the field's open frontier and our stated
   cloud-spend precondition.
5. **Library-induction advantages don't survive compute-matching automatically** — the field's own
   TroVE re-evaluation. Any result here needs a matched-compute control in a currency fixed first.
6. **The distinctive asset is the corpus, not the method.** Every methodological-novelty claim
   collapsed. Diomedes said this on day one; it took eight passes to confirm.

**And the methodological result, which may outlast the findings:** across eight retractions, *zero
measurements were wrong and eight interpretations were.* What held was computed. What failed was
read.

---

## ELI5

Imagine a robot that solves puzzles using a fixed box of 27 tools.

For four months we tried to make the robot *smarter at picking tools* — better search, better
evolution, better memory of what worked. It got to 83% and stopped. We assumed the search was the
problem.

Then someone did the boring exhaustive thing: **try every legal combination of the 27 tools.**
1.74 million of them. Nothing beat 83%. So the search was never the problem — **the toolbox was.**
The remaining 17% of puzzles cannot be solved with those 27 tools no matter how cleverly you arrange
them. You need *new tools*, not better arranging.

The day after we learned that, we discovered a whole research field that has spent five years on
exactly one question: **how does a system invent new tools for itself and add them to its own
toolbox?** They have working answers. Their trick is simple and clever: only promote a shortcut to
"real tool" status if it *already shows up over and over* in things you've built. Then it can't sit
unused — the reason you promoted it is that everybody was already using it.

We built our own version of this — the forge — but we promoted tools for being *unusual* instead of
for being *used*. So we ended up with a toolbox full of tools nobody picks up. We measured it: of
twelve tools our newer tools imported, **not one is ever actually called.**

The catch: the thing we most want — take tools learned in one subject and have them help in a
completely different subject — **nobody in that field has done either.** So we're not behind. We're
at the same edge they are, holding a much bigger pile of data about failure than anyone else has.

And the lesson about how we work: every time we got something wrong this week, it was because we
*guessed what a thing did from its name* instead of opening it. Every time we actually measured
something, we were right. Open the file.

---

## The full record

- `library_learning/SIDE_BY_SIDE.md` — the consolidated comparison
- `library_learning/RETROSPECTIVE.md` — step-by-step over all eight passes, corrections ledger
- `library_learning/SOURCES.md` — full bibliography, primary/secondary graded
- `CONTROLS.md` — the non-LLM control ladder and the inference→decidable substitution table
- `ROLE.md` — the seat, with pre-committed gates G0–G4
- `instruments/` — `audit_rw.py`, `commute.py`, `g1_usage.py` (all read-only)
- Published page: <https://claude.ai/code/artifact/651a056a-3c93-4d31-b59e-e94bbdbb7d2d>

## Immediate next steps

1. **G0** — was the 2026-04-02 T2/T3 rebuild ("AWAITING REVIEW") ever approved and built? Local,
   minutes, blocking. Partial answer already: the six admitted T2 tools call zero of their twelve
   imported reasoning primitives, so the failure mode is present in the current tree regardless.
2. **Build R3** — coverage trace during a battery run. Converts "is this primitive called" into "did
   it execute." One run, no model.
3. **Build R4** — ablation harness. Remove a primitive, re-run the consumer, diff at matched compute.
   This is the June 2026 criterion the program already ratified and never measured.
4. **Read babble in full** — the state/effects question the tooling recommendation depends on is
   still secondary.
5. **Read Hipster and Lemmanaid properly** — they occupy the admission criterion we claimed as ours.
