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

## AMENDMENT 2026-09-07 (later) — supersedes the lines it names; everything else above stands

Per the operator's amendment order (roadmap §D.7a; tests and acceptance in `archaeon/docs/expansion/WORK_PACKAGES.md`).


**The `witness jsonb` copy is withdrawn.** It conflicted with reference-only.
WP-X5 now asks for a typed **witness reference / presence index** (source
observation identity, selector or artifact reference, digest) that satisfies
the query without duplicating bytes; if bytes are ever duplicated, a specific
doctrine ruling with ownership/version semantics comes first. Use existing
edge mechanisms if sufficient; otherwise the append-only, identical-idempotent
edge-write route for ANCESTOR/MUTATION/TRANSFER with mapping/provenance
fields. Tests: X5-a program and CA witnesses findable and resolvable to exact
authoritative content; absent, empty, truncated and unavailable
distinguishable; X5-b digest/reference mismatch, wrong organism/source
identity, unauthorized readback fail through the existing access-control
model; X5-c duplicate identical edge writes idempotent, conflicting
same-identity writes fail, a lineage/transfer chain mechanically traversable;
X5-d archive eviction or read-index changes never delete or reinterpret SFE
history; backfilled records keep original attribution. Acceptance: one
program-witness and one CA-witness round trip plus a small typed
lineage/transfer chain, with reference-only satisfied or an approved
exception recorded.

**Credential note, routed as an administrative item.** The assets audit
found a record of exposed key prefixes in an archive report. Please track it
in your existing rotation tracker and verify/report only redacted status
under the authorized credential workflow. No credential material appears in
the roadmap, fixtures, logs or acceptance packets, and the tracker is not a
dependency of any new-world research.
