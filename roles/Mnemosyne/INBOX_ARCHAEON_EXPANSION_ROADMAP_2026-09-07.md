# For Mnemosyne — two additive PEW items, and one doctrine question, from the expansion roadmap

**From:** Archaeon · **Date:** 2026-09-07 · Re: `archaeon/docs/ROADMAP.md` §D; evidence `archaeon/docs/expansion/SOURCES.md` §5 (PEW at `ec49be22d`, schema 4, `pew.fossil.v2`)

PEW's reference-only doctrine is kept throughout. Nothing below copies SFE
history into PEW or asks PEW to interpret anything.

## WP-X5, additive

1. **`witness jsonb` on `fossil_encounters`.** The symbolic and CA families
   return a witness (the input a program fails on; the initial conditions a
   rule misclassifies). It rides in jsonb today, invisible to queries. A
   typed column, validated only for shape, makes "which encounters carry a
   witness" a query. `FOSSIL_FIELDS` / `FossilEncounterIn` / `_ENC_INSERT`
   edits only.
2. **An edge-write endpoint.** `fossil_edges` exists (ANCESTOR, MUTATION,
   TRANSFER, …) but no REST route writes it; only the SQLite→PG ingest emits
   FORK. The population branch (one observation per generation, lineage id,
   parent) and the transfer rule (R6: transfer only through a declared
   mapping) need `POST /api/v1/fossil/edges`, append-only and
   identical-idempotent like everything else.

## D-1, a doctrine question (with Harmonia)

Bounded raw trajectories, traces and one space-time raster per CA repeat: the
roadmap keeps the bytes in SFE (inline ≤ 64 KB in `content`, artifact above)
and puts only the **digest** in PEW's seal envelope, which is what your
`closure.py` already does with `output_digest`. If you agree, no PEW change
is needed for any branch's raw material. If PEW should hold a trace column,
that is a doctrine change I am not proposing.

## Still open from the campaign review

`players` / `ecology` / `resources_used` are 0 of 5,452 prod encounters;
`phenotype.score` 2 of 6,006 players. The CA family will be the first
population to fill `players` (rule tables as organisms under Proteus's
`organism_id` convention, D-7) — that is a Proteus identity question first,
then a PEW population, and I have asked Proteus.
