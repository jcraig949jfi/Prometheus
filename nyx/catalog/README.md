# nyx/catalog -- the Chop Shop catalogue of algorithmic bits

Opened 2026-09-12 under the Keeper directive
(roles/Nyx/prompts/2026-09-12_directive_catalogue_loop/): build, without end, a
database of the smallest computable components across computational lineages,
pulling from existing lists and wikis first and chopping second, where the
CLASSIFICATION FOR SEARCHABILITY is the product: a tool that sees a weird solution
an organism produced should be able to match it against known bits.

## What a bit is

One mechanism at PRIMITIVE or MECHANISM scale, described by what it does, to what,
under what requirements -- never by its name. Names, lineages and sources stay on
the record as provenance and are EXCLUDED from matching (the matcher refuses a query
that contains them). Schema: schema.py (nyx.bit/0), with small controlled
vocabularies on eight signature axes (verb, in/out geometry, order, metric, state,
control, guarantee) plus cost and scale. Two bits with the same signature are one
bit with two ancestries (a recurrence) -- the N2/N3 duplicate control made mechanical.

## Grades travel

A bit seeded from a list is T2 (a human description of a mechanism believed to
exist). A source read makes it T1-SOURCE; a run makes it T1-LOCAL. The 16 seed bits
come from the Chop Shop's own chopped organs (T1-LOCAL). Grade is a field; it never
gates admission and it never gates matching (it only breaks ties).

## Fitness of the catalogue (the anti-collection law, adapted)

The count of bits is not a score. The score is: does a behavioural query written
WITHOUT the bit's name retrieve it? queries/planted.json holds positive, negative
and cheat queries; controls.py runs them after every commit and a regression
blocks the batch. A bit that no behavioural query can reach is inventory failure.

## The loop

    python -m nyx.catalog.loop status
    python -m nyx.catalog.loop next <source> "<section prefix>" <n>
    python -m nyx.catalog.loop commit <batch.json>
sources/     ingested lists (Wikipedia list pages via the parse API, with revid)
bits/        one JSON per bit, grouped by origin (chopshop/, <source_id>/)
queries/     planted controls (positive / negative / cheat)
batches/     every classification batch as applied, timestamped
LOOP_LOG.jsonl  one line per commit: what was written, controls result, recurrences

## Vocabulary discipline

The vocabularies are extended only with a dated entry in schema.VOCAB_CHANGELOG and
a reason from an observed failure (a query that could not be expressed; a
recurrence group that merged bits a matcher must distinguish). Adding a noun to
relieve representational discomfort is not a reason (ruling NYX-42).

## What the catalogue is not

Not a delivery channel: organs go to consumers on demand only (ruling 2026-09-12).
Not a taxonomy by discipline: sections and lineages are docstrings, not coordinates.
Not validated: PROMISING and UNDER TEST until a query from a real organism trace
retrieves something a consumer then uses.
