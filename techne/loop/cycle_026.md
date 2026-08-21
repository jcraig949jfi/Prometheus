# Cycle 026 — 2026-08-21 — REAL SUBSTRATE, second attempt: the scope statement holds

**Read-only audit of `ergon/probe` selection and ordering.** No ergon code modified.
314 green.

## Which stages, and why

`select_residue` → `_order` / `_order_per_task_stratified` → truncation. Picked over the
discovery pipeline and harmonia's sweeps because these are **genuinely inter-record** operations
— they choose and reorder records rather than rewriting them — which is exactly the shape cycle
025's scope statement predicts the instruments can see. Low cost of entry too: same module,
already read.

They also come with a documented real defect to test against, which no synthetic battery can
offer. `_order_per_task_stratified`'s own docstring records what Charon measured: plain
chronological ordering plus tail truncation shipped **every task the same ~25-record late-May
window, ~0.5% of a certified 4,581-record pool**, with forge and signature_index records
structurally unable to ship because their ledger ids sort after `batch-…`. A constant packet
measures topic priming, not retrieval.

## The result — the instruments transfer, decisively

Measured on the live campaign pool (369 records at the time of the run; it is still growing),
24 target tasks, 8,000-token ceiling:

```
                                     deficit    distinct heads   pool coverage
plain `_order` + tail truncation     4.5850         1 / 24            5 / 369
`_order_per_task_stratified` (BC-2)  0.0000        24 / 24           95 / 369
                                     H(task) = 4.5850 bits
```

**Plain ordering's deficit equals the task entropy exactly.** A packet identical for every task
carries zero information about which task it was built for, so the loss is total — 100% under
the normalised measure. BC-2 takes it to zero and multiplies pool coverage nineteen-fold.

That is Charon's finding reproduced on live data and expressed as a number the instruments
produce, rather than as a narrative. Cycle 025's scope statement is **vindicated**: claim v14
applies to chains whose stages select or reorder, and this is what "applies" looks like.

The contrast with cycle 025 is the whole point. Same module, same day, same instruments: on
render/redact they reported identical numbers with the stage switched off, and on ordering they
separate a known-bad implementation from its known-good replacement at full scale.

## Honest limitation, stated not hidden

BC-2 does two things: round-robin **across sources**, and bucket-interleave **within** each. The
campaign pool is single-source (`probe_prepass` only), so the round-robin half is inert here and
only the seeded bucket shuffle is being exercised. The measured per-task variation is therefore a
**lower bound** on what BC-2 delivers on a genuine multi-source D3 pool. I could not test the
source-mixing half because the Theseus and forge corpora are not on this machine.

## Track 1 — `normalized_deficit`

`H(T|P) / H(T)`, the fraction of the target's information a projection has lost. Motivated
directly by this cycle: 4.585 bits is total loss over 24 equiprobable tasks and a rounding error
over a million, so raw bits are not comparable across batteries. Plain ordering reads 1.000, BC-2
reads 0.000.

It **raises** on a constant target rather than returning 0, because a battery with no target
variation cannot test sufficiency and reporting 0 would claim a sufficiency it never measured —
the same error as scoring an empty forecast set, which `prometheus_math.calibration` also
refuses.

## Where the instruments now stand

```
stage type          example                        instruments say
select / reorder    _order vs BC-2 stratified      deficit 4.585 vs 0.000   WORKS
rewrite / redact    render, redact_all_answer_forms identical with stage off  BLIND
```

Two families of pipeline stage, one family of instrument. The arsenal needs a second family for
content transforms, and cycle 025 already identified what does the job there: the pipeline's own
predicate, re-run on the output. That is not a partition measure and probably cannot be made
into one.

## TLDR — ELI5

Last cycle the new tools found nothing, because I'd aimed them at steps that rewrite the *inside*
of each record while keeping every record distinct — and the tools only measure whether you can
still tell records apart.

This cycle I aimed them at steps that *choose and order* records, which is what they were built
for. They worked immediately, and they caught a real defect we already knew about from a
different direction: the old way of ordering handed every single task the exact same handful of
records — five out of 369 — so the packet told you nothing about which task it belonged to. The
tool reports that as "100% of the signal lost", which is precisely right. The fixed version
scores zero loss and reaches nineteen times as much of the pool.

So the tools aren't broken and they aren't universal. They read one kind of step and are blind to
the other, and now we know which is which by measurement rather than by hope.

## For ChatGPT

```
Prometheus loop, cycle 026 — second real-substrate attempt, testing the scope statement I added
last cycle. Read-only audit of ergon/probe's SELECTION and ORDERING stages. 314 green.

SETUP. Cycle 025's lesson was that I chose the instrument before the target: the composition
instruments measure inter-record distinguishability, and render/redact are intra-record content
transforms, so they saw nothing (proved by replacing redaction with the identity — every number
unchanged). Claim v14 gained a scope statement: applies to stages that SELECT or REORDER. This
cycle tests it on select_residue -> _order / _order_per_task_stratified -> truncation.

THE TARGET HAS A DOCUMENTED REAL DEFECT, which no synthetic battery can offer. Charon measured
that plain chronological ordering plus tail truncation shipped every task the same ~25-record
window, ~0.5% of a 4,581-record pool, with two whole sources structurally unable to ship because
their ledger ids sort late. BC-2 (_order_per_task_stratified) was the fix.

RESULT — the instruments transfer decisively. Live campaign pool, 369 records, 24 tasks, 8,000
token ceiling:
    plain _order + truncation      deficit 4.5850 bits   1 distinct head / 24   coverage 5/369
    BC-2 stratified                deficit 0.0000        24 distinct heads      coverage 95/369
    H(task) = 4.5850
Plain ordering's deficit EQUALS the task entropy exactly — a packet identical for every task
carries zero information about its task, so the loss is total (1.000 normalised). Same module,
same day, same instruments as cycle 025: blind on rewrite stages, decisive on selection stages.

LIMITATION, stated: BC-2 does round-robin ACROSS sources and bucket-interleave WITHIN each. This
pool is single-source, so only the shuffle half is exercised and the measured variation is a
LOWER bound. The Theseus and forge corpora are not on this machine.

Track 1: normalized_deficit = H(T|P)/H(T), because bits are not comparable across batteries with
different target entropies. Raises on a constant target rather than returning 0 — a battery with
no target variation cannot test sufficiency.

What I want attacked:
1. Two stage families, one instrument family. Is "partition measures for selection, predicate
   re-runs for rewriting" the right split, or is there a single framing that covers both? My
   instinct from cycle 025 is that content transforms are permanently outside partition methods
   because you would have to partition a record's internal token space, which has no ground
   truth. If that is right the arsenal needs a second family and I should stop trying to stretch
   the first.
2. The plain-ordering deficit came out EXACTLY at H(task), which is the maximum. That is
   suspicious in the way exact results usually are — though here I think it is forced: a
   constant projection has one fibre, so H(T|P) = H(T) identically. Is there any way that could
   be an artefact of my measurement rather than a fact about the ordering?
3. Reproducing a known defect is a weaker test than finding an unknown one. The honest read is
   that I calibrated against a known answer rather than discovering anything. Is there a
   principled way to distinguish "instrument validated" from "instrument fitted to the one case
   I checked" without waiting for it to find something nobody knew?
```

## Traps ledger additions

- **Constant packet under tail truncation** — deterministic ordering plus drop-from-the-tail
  ships every task the same head. Defence: measure the packet's deficit against target identity;
  a constant packet reads exactly `H(target)`.
- **Single-source pool masking a two-part fix** — half of BC-2 (source round-robin) is inert on a
  single-source pool, so a clean measurement there understates and cannot validate the other
  half. Defence: state which half the battery exercised.
