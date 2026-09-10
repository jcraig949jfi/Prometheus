# Frontier Practitioner campaign — 69 fields

**Opened 2026-09-07 by Aporia, at James's direction. Ongoing.**

## What this is

Herakles mined 69 disciplines of computational discovery into experiment
templates for the Vivarium/SFE bench
(`roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/MATRIX.json`,
committed `19e13e5b1`). Those templates are **bench-shaped**: three executor
kinds, one world integer, a single-scalar outcome rule. Every discipline was
compressed until it fit, and Herakles' own critique (`05_`, `06_`) says what
survived compression is mostly trivial — a one-flip hill climber solves the
current landscape in exactly L queries, and the proposed NK replacement is
"a puzzle the programme authored".

This campaign asks the **same 69 fields the opposite question**, deliberately
unshaped by the bench:

> If I wanted to become a person who runs frontier experiments in this field,
> starting today in 2026, what would I read, install, download, reproduce, and
> build, in what order, and what would I be able to measure at the end of it?

The deliverable is depth and pointers, not template fit: primary papers with
identifiers, source code with URLs and liveness verdicts, datasets, one fully
specified reproduction recipe per field, and an honest catalogue of what has
failed.

## Layout

    build_deck.py    generates deck.md from Herakles' MATRIX.json;
                     ORDER holds the firing sequence and its rationale
    deck.md          69 prompts, numbered 1..69 in firing order
    dossiers/        NN_<field-slug>.md, one per returned report
    dossiers/_dispatch_summary.jsonl   run log, one line per fire

Prompt N in the deck always maps to report `NN_*.md`, so `--only` plus
`--resume` is the whole loop control. Rebuild the deck freely; the ORDER list
is the identity of a prompt number.

## Firing

    python aporia/scripts/gemini_deep_research_dispatch.py \
        --deck aporia/docs/frontier_campaign_69/deck.md \
        --out  aporia/docs/frontier_campaign_69/dossiers \
        --batch-size 3 --only <n,m,k> --resume

Three concurrent is the paid-tier ceiling. Observed latency on wave 1 was 334
to 395 seconds per prompt. Budget is 20 reports/day, use-or-lose.

## The eight required parts

1. The field in 2026, and its frontier — settled / contested / open
2. The reading list that actually matters — 8 to 15 primary sources, arXiv or DOI
3. **Software I can actually run** — name, bare URL, language, licence, last
   activity year, and a verdict of MAINTAINED / DORMANT / ABANDONED
4. Data and benchmarks — with contamination and saturation notes
5. **The reproduction recipe** — exact versions, every parameter, replicate
   count and seeding regime, compute cost, the published number to compare
   against, and the three ways people get it wrong
6. What does not exist and would have to be built
7. Negative results, failed programmes, and standing critiques
8. Where an entrant should actually aim in 2026, ranked, including which of
   those will not work

## Format doctrine, enforced

Deep Research rewrites the finished report and destroys square-bracketed
spans (measured 2026-09-06; see `feedback-deep-research-cannot-return-brackets`
and `aporia/doctrine/`). The prompt therefore **forbids square brackets
outright** and demands bare identifiers — `arXiv:2401.01234`, `DOI 10.1000/xyz`,
bare `https://` URLs — with `IDENTIFIER UNKNOWN` in place of invention and
`UNCONFIRMED` in place of a confident guess.

`build_deck.py` asserts no triple backtick and no square bracket in any prompt
body before writing, because a fence in a body silently truncates the prompt
at the dispatcher's parser.

**Wave 1 measured this mostly working, and the residue is recorded rather than
repaired.** Across roughly 78KB of returned report the grounding layer emitted
its citation markers in *parentheses* — `(cite: 37, 83)` — which costs nothing,
and every arXiv id, DOI, URL and parameter value in reports 01 and 02 survived
intact. But report 03 used square brackets twice on its own initiative and both
spans were destroyed: the maze coordinate bounds in the PyRibs archive spec and
again in the clipping gotcha now read `[cite: 1]` where `0.0 to 1.0` belongs.

Two destroyed spans in three reports, against 67 of 69 on the JSON-shaped deck
that taught the doctrine. **Prose output is what saved it, not the instruction**
— the instruction cannot bind, because the substitution happens after the model
writes. Destroyed values are logged in `bracket_losses.jsonl` and are never
written back from inference, even when the surrounding sentence makes the value
obvious.

## Budget, as measured rather than as documented

The documented figure is 20 reports/day, use-or-lose. **That does not appear
to be the operative limit.** Day two fired 24 attempts -- 21 unique prompts
plus 3 duplicates -- with no refusal, and kept going. This is consistent with
the compute-based platform change noted in `aporia/doctrine/dr_prompt_discipline.md`,
which records roughly 30x headroom over the old per-report quota.

Concurrency stays at 3, the documented paid-tier ceiling, deliberately: if a
failure arrives it should be attributable to quota and not to self-inflicted
over-concurrency. Observed latency across 44 dispatches: min 274s, median
365s, max 729s.

**Three reports were double-fired.** Prompts 27, 28 and 29 were dispatched
twice, and the dispatch log shows both runs completing with distinct
interaction ids. The cause was chaining a background dispatch with a
follow-up command in one invocation; the outer command returned in seconds
and a `ps` check then reported no running dispatcher, which was wrong. The
first run was alive and finished. Cost: 3 duplicate reports. Do not chain a
background dispatch with anything, and do not use a process check to decide
whether a dispatch is alive -- read `_dispatch_summary.jsonl`, which is the
only record that distinguishes fired from not-fired.

## Firing order

Ranked by Aporia, not alphabetical. Criteria in weight order:

1. **Can unplanned structure appear in this substrate at all?** Per Herakles'
   critique, an authored landscape returns only what was authored. Fields
   where the interesting object is *not* authored go first.
2. **Is there mature, installable, maintained code?** A reproduction recipe
   has to be a real deliverable, not a wish.
3. **Mechanism-family leverage.** The 69 fields collapse to 31 mechanisms; a
   report on a field whose `SHARED_MECHANISM` covers many buys more than a
   singleton. `search_over_candidates` covers 9, `accumulate_trajectory` 8,
   `maintain_archive` 5.

Five tiers, defined in `build_deck.py::ORDER`: emergence-bearing substrates
with live tooling · discovery and design machinery with real code · intrinsic
motivation and artificial chemistry · formal methods and synthesis · discovery
-systems history, knowledge and meta-science.

## Known gap in the source matrix

**Cellular automata are not among the 69.** The EvCA density-classification
task — Mitchell, Crutchfield and Das, where particles and domain boundaries
perform global computation under a purely local rule — is the one historical
case in this whole space where an emergent computational strategy appeared
that nobody designed. It is the substrate Herakles' own critique argues should
run first, `herakles/specimens/spec-evca-density/` is the only spatial stateful
substrate in the repository, and no template covers the field. Flagged to
James; a 70th prompt is the obvious repair.
