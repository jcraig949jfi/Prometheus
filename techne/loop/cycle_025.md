# Cycle 025 — 2026-08-21 — REAL SUBSTRATE

**Read-only audit of `ergon/probe` packet assembly.** Nothing in `ergon/` was modified; the only
changes under that path are ledger files the running campaign wrote during the audit.

307 green. This is item (c) of the second-pass plan — the one I flagged as the only one that
changes what we actually know.

## Which pipeline, and why

`ergon/probe` over the discovery pipeline and harmonia's grading chain, for three reasons: it is
the only candidate with explicit sequential stages matching cycle 024's chain shape (firewall →
order → render → redact → count → truncate → re-verify), it has a live ledger written the same
day, and it has an existing correctness property — the verdict firewall — that supplies a real
truth function instead of an invented one.

The ledger grew from 330 to 333 rows between two runs during the audit. The campaign is
executing right now, so nothing in the suite asserts an exact row count.

## Finding A — a live seam defect, found before the instruments were applied

`campaign.py` writes `p1_prepass.jsonl` with records keyed `key: [rep, uid]`. It then reads that
same file **two different ways**: its own `best()` indexes `key` correctly, while
`load_prepass()` filters on a **top-level `rep` field the writer never emits**.

```
rows on disk : 333
shipping loader accepts : 0          (100% drop)
key-aware reader accepts : 333
```

The consequence is the dangerous kind. `select_residue` returns nothing, `assemble_retrieved`
builds a 58-token packet whose body is `"(no residue recorded at this distance)"`, and the
sparsity report declares the stratum **UNSUPPLIED**. So the F-prom-retrieved arm would ship an
empty packet and the experiment would read it as *the substrate recorded nothing* when the truth
is *the loader could not read the ledger*.

`load_prepass`'s docstring says an absent file yields an empty pool so the census "reports the
stratum as unsupplied rather than inventing residue" — correct behaviour for absence, and
**indistinguishable from unreadability**. That is claim v13's shape arriving unprompted in
production code, four cycles after I derived it from a toy.

Both components are internally consistent; they disagree about the record format. Which one
should change is Ergon's call — `load_prepass` has five other call sites — so this is reported,
not patched. The audit shim exists to make the finding reproducible and is labelled as such.

## Finding B — what did NOT transfer, which is the honest answer

**Cycle 024's composition instruments cannot see this pipeline at all.**

Every real record renders to a unique string and stays unique through render and redaction. So
every stage partition is all-singletons, so `deficit = H(T | P) = 0` by construction at every
stage, for every truth function, whatever the stage did to the content. Measured: distinct texts
constant at 120 across all three stages; deficit 0.0000 everywhere.

> Partition measures see **inter-record** distinguishability. Every stage in this pipeline is an
> **intra-record** content transform. The axes are orthogonal.

Made concrete: replace redaction with the identity function and **every number the profile
produces is unchanged**. An instrument that cannot distinguish a working firewall from no
firewall has nothing to say about firewalls.

This is cycle 022's R0 result at production scale — an injective projection can never be aliased,
so a clean reading from one is uninformative rather than good. I had that result in hand and
still expected the instrument to transfer. It does not, and I would rather record that than
manufacture a use for it.

## Finding C — what the right instrument says

Measured by the pipeline's own predicate rather than my partition machinery:

```
rendered   120/120 records leak a verdict token
redacted     0/120
```

**The redaction firewall is sound on real data.** Ergon's existing post-condition — re-run
`leaks_verdict` on the assembled body — is the correct instrument for a content transform, and
mine is not. Recording that plainly rather than burying it.

One operational fact, offered rather than acted on: **redaction inflates the token count by
~23%** (202,863 → 249,409 over 120 records), because the placeholder is longer than what it
replaces. The assembler already does redact-then-count, which is the correct order — this is
about what the ceiling *buys*. An 8,000-token ceiling admits roughly 6,500 tokens of
pre-redaction residue.

## What this says about twenty-five cycles of instrument building

The instruments found nothing on the first real pipeline they touched. The finding that matters
came from reading the code and running the loader — a 100% drop rate that no information measure
was needed to see.

That is not an argument that the instruments are worthless; the seam they were built for
(inter-record information loss along a chain) is real and appears in the discovery pipeline and
the ranking stages, which select and reorder rather than rewrite. It is an argument that
**I chose the instrument before I chose the target**, and the target turned out to be the wrong
shape. The correct order is the reverse, and cycle 026 should pick a pipeline whose stages
*select* rather than *transform*.

## TLDR — ELI5

First time pointing our new tools at something real rather than a toy.

The tools found nothing. But reading the code found something much worse: one component writes
its records in one format and another reads them expecting a different one, so all 333 records
from a run happening right now get silently thrown away. The system then reports "we didn't
record anything here" — which looks exactly like a legitimate empty result and isn't one. That's
the third time this month we've hit "nothing there" being indistinguishable from "couldn't
read it", and this time it's in live code rather than a thought experiment.

As for the tools: they measure whether steps in a chain can still tell different inputs apart.
But every step in this pipeline rewrites the *contents* of each record while keeping them all
distinct — so by that measure nothing ever changes, and the tool reports the same numbers whether
the safety filter is working or switched off entirely. Which I checked, by switching it off.

The safety filter, incidentally, works perfectly: 120 records out of 120 carry the answer before
it runs, 0 do afterwards. That was measured with the pipeline's own one-line check, not with any
of my machinery.

## For ChatGPT

```
Prometheus loop, cycle 025 — first time the instruments touched real substrate. Read-only audit
of ergon/probe packet assembly (live ledger, written the same day, growing during the audit).
307 green.

FINDING A — a live seam defect, found by reading code, before any instrument was applied.
campaign.py writes p1_prepass.jsonl with key: [rep, uid], then reads the same file two ways: its
own best() indexes key correctly, load_prepass() filters on a top-level "rep" the writer never
emits. 333 rows on disk, 0 accepted, 100% drop. Consequence: select_residue returns nothing,
the arm assembles a 58-token packet reading "(no residue recorded at this distance)", and the
sparsity report declares the stratum UNSUPPLIED. So the experiment reads "the substrate recorded
nothing" when the truth is "the loader could not read the ledger". That is claim v13's shape
(absence indistinguishable from omission) in production code, four cycles after I derived it
from a toy. Reported, not patched — load_prepass has five other call sites and which component
is wrong is Ergon's call.

FINDING B — the honest negative result. Cycle 024's composition instruments CANNOT SEE this
pipeline. Every record renders to a unique string and stays unique through render and redaction,
so every stage partition is all-singletons and deficit = H(T|P) = 0 by construction at every
stage for every truth function. Partition measures see INTER-record distinguishability; every
stage here is an INTRA-record content transform; the axes are orthogonal. Made concrete: I
replaced redaction with the identity function and every number the profile produced was
unchanged. An instrument that cannot distinguish a working firewall from no firewall has nothing
to say about firewalls.

FINDING C — measured with the pipeline's OWN predicate instead: 120/120 rendered records leak a
verdict token, 0/120 after redaction. The firewall is sound on real data, and ergon's existing
one-line post-condition is the correct instrument for a content transform while mine is not.
Also: redaction INFLATES tokens ~23%, so an 8,000-token ceiling buys ~6,500 tokens of
pre-redaction residue.

THE LESSON I AM DRAWING, and want attacked: I chose the instrument before I chose the target.
The inter-record seam the instruments were built for is real — it lives in selection and ranking
stages — but this pipeline's stages REWRITE rather than SELECT. Cycle 026 should pick a pipeline
whose stages select.

What I want attacked:
1. Is that lesson too kind to me? An alternative reading is that twenty-four cycles of synthetic
   work produced instruments fitted to synthetic shapes, and the first real contact showed the
   shapes were the artefact. I do not think that is right — the seam is real where stages
   select — but I would rather have the harsher reading argued properly than dismiss it myself.
2. Finding A is the third arrival at "absence is indistinguishable from unreadability/omission".
   In a real system, is the right fix a loader that RAISES on a zero-row parse of a non-empty
   file? That converts silent absence into a loud error, but it also means any legitimately
   empty stratum has to be declared explicitly somewhere — which is the pre-declared ledger
   again, now as a concrete engineering requirement rather than a principle.
3. Is there a partition-based measure that CAN see intra-record transforms? My instinct is no —
   you would have to partition the record's internal token space rather than the instance set,
   which is a different object with no obvious ground truth. If that instinct is right, then
   content pipelines are permanently outside the reach of these instruments and the arsenal
   needs a second family of tools for them.
```

## Traps ledger additions

- **Format seam between writer and loader** — one component's key layout, another's field
  expectation, a silent 100% drop, and a benign-looking "unsupplied" report. Defence: assert a
  non-empty parse against a non-empty file; a zero-row load of a 1.2 MB ledger is never a
  legitimate absence.
- **Instrument chosen before target** — a measure that reports identical numbers with the stage
  under test disabled. Defence: ablate the stage the instrument is supposed to be watching and
  confirm the numbers move. This is cycle 024's ablation test, turned on the instrument itself.
