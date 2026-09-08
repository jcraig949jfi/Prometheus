# WP-X5 design — witness presence index and typed lineage edges

**Status: DESIGN ONLY. Not built.** Build when the symbolic or CA family has a
witness to reference (Tier 4). Owner: Mnemosyne. Handoffs: Daedalus
(observation/artifact identity), Proteus (organism identity), Vivarium (emits).

Requested in `roles/Mnemosyne/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md`
(amendment 2026-09-07 supersedes the original `witness jsonb` copy) and
`archaeon/docs/expansion/WORK_PACKAGES.md` WP-X5. Baseline: PEW schema 4,
`pew.fossil.v2`, `archaeon/v0` at 5191c3383.

## 0. What the amendment changed, and why the design obeys it

The original ask was a `witness jsonb` column carrying the witness itself. It
was withdrawn because it conflicts with reference-only: PEW would have become
a second copy of SFE-owned bytes, with no ownership or version semantics and
no answer to "which copy is authoritative when they differ".

This design therefore **indexes presence and identity, and never stores the
witness**. SFE remains the only holder of the bytes. If bytes are ever to be
duplicated, that is a doctrine ruling first, with ownership and version
semantics attached — not a schema convenience.

## 1. Witness presence index

### 1.1 The question it answers

"Which encounters carry a witness, and where is the authoritative content?" —
mechanically, without opening SFE, and without PEW holding the content.

### 1.2 Proposed table

    ew.witness_refs
      witness_id        text PRIMARY KEY      -- W-<sha256[:12]> content address
                                              -- of the reference tuple below
      encounter_id      text NOT NULL         -- FK -> fossil_encounters
      run_key           text NOT NULL         -- with encounter_id, the run
      witness_kind      text NOT NULL         -- PROGRAM_INPUT | CA_INITIAL_STATE
                                              -- | OTHER  (closed vocabulary,
                                              -- extended only by migration)
      source_kind       text NOT NULL         -- OBSERVATION | ARTIFACT
      source_id         text NOT NULL         -- SFE obs_id or artifact_id
      selector          text                  -- path/field within the source,
                                              -- NULL = the whole source
      content_digest    text NOT NULL         -- sha256:<64hex> of the exact
                                              -- authoritative bytes
      content_bytes     bigint                -- size as reported by the producer
      availability      text NOT NULL         -- PRESENT | EMPTY | TRUNCATED
                                              -- | ABSENT | UNAVAILABLE
      availability_note text                  -- why, for TRUNCATED/UNAVAILABLE
      sfe_engine_instance_id text              -- which engine's ledger (010)
      producer          jsonb                 -- who asserted it, versions
      namespace         text NOT NULL DEFAULT 'prod'
      created_at        timestamptz NOT NULL DEFAULT now()
      revision          bigint NOT NULL

      UNIQUE (encounter_id, run_key, witness_kind, source_id,
              coalesce(selector,''))
      INDEX on (encounter_id, run_key), (source_id), (availability)

`witness_id` is the content address of
`(encounter_id, run_key, witness_kind, source_kind, source_id, selector,
content_digest)`. Identical re-assertion yields the identical id: idempotent
by construction, like every other PEW write.

### 1.3 The five availability states (test X5-a)

`NULL` cannot distinguish these, which is why `availability` is a required
enum and not an inference from a missing column:

    PRESENT      the witness exists and content_digest is its digest
    EMPTY        the witness exists and is legitimately zero-length; digest is
                 the digest of the empty string, which is a fact, not a gap
    TRUNCATED    bytes were bounded at the source; content_digest is the digest
                 of WHAT WAS KEPT and content_bytes says how much.
                 A truncated witness is NOT a witness for replay purposes and
                 must never be read as one.
    ABSENT       the family produced no witness for this run (a normal outcome
                 for a run that did not fail)
    UNAVAILABLE  a witness exists in principle but PEW could not obtain a
                 reference — eviction, permission, engine unreachable.
                 UNKNOWN, never ABSENT: the distinction between "there is none"
                 and "I could not look" is the whole point.

### 1.4 Resolution (test X5-a, second half)

PEW returns the reference; the consumer resolves it against SFE. Resolution is
"exact" when the bytes fetched from `source_id`/`selector` hash to
`content_digest`. PEW asserts the digest it was given and never recomputes one
it cannot see — an unverifiable digest stays an unverified producer claim, the
same treatment `sfe_session_key_fp` gets today.

### 1.5 Failure modes (test X5-b)

    digest mismatch on readback  the consumer detects it; PEW records the
                                 reference, so the mismatch is attributable to
                                 a named (source_id, selector, digest) rather
                                 than to "somewhere in the run"
    wrong organism/source id     UNIQUE key is per (encounter, run, kind,
                                 source, selector); a reference naming a source
                                 that the encounter does not reference is
                                 refused 422 witness_source_not_in_encounter
    unauthorized readback        unchanged: PEW's existing per-machine token +
                                 namespace model. PEW discloses a reference and
                                 a digest, never content, so a reader who
                                 cannot open SFE learns nothing about the
                                 witness beyond its existence and size

## 2. Typed lineage edges

### 2.1 Are existing mechanisms sufficient?

**No.** `ew.fossil_edges` exists with the right relation vocabulary
(ANCESTOR, FORK, MUTATION, CROSS, TRANSFER, TRANSPLANT, EXTINCTION, SURVIVAL)
but:

- **no REST route writes it.** Verified: no `fossil/edges` route exists in
  `ew/service.py`. Only the SQLite→PG ingest emits edges, all FORK — 31 rows
  live, one relation kind.
- **no idempotency or conflict semantics.** `PRIMARY KEY (edge_id)` alone; the
  ingest mints `edge_id` as `FE-fork-<dst>`, a convention, not a content
  address. Two different edges asserting the same identity would either
  collide or silently coexist depending on how the id was formed.
- **no mapping or provenance fields**, which R6 requires: transfer only
  through a *declared mapping*.

So WP-X5 needs the route, plus additive columns.

### 2.2 Additive columns

    ew.fossil_edges
      + mapping_id       text    -- the declared mapping a TRANSFER goes through
      + mapping_digest   text    -- sha256 of the mapping definition
      + producer         jsonb   -- who asserted the edge, component versions
      + evidence_ref     text    -- optional witness_id / encounter_id backing it
      + sfe_engine_instance_id text  -- which ledger (consistent with 010)

`edge_id` for new writes becomes `FE-<sha256[:12]>` of
`(src_kind, src_id, dst_kind, dst_id, relation, coalesce(mapping_id,''),
namespace)`. Existing `FE-fork-*` rows keep their ids untouched — the scheme
changes for new writes only, and the ingest's rows are not rewritten.

### 2.3 Route

    POST /api/v1/fossil/edges          single
    POST /api/v1/fossil/edges/batch    all-or-nothing, like encounters

Semantics, identical in shape to the encounter path so there is one rule to
learn (test X5-c):

    200 inserted              committed and readable
    200 duplicate_identical   same identity, byte-identical -> no second row
    409 conflict_existing_row_differs:<field(stored=..submitted=..)>
                              same identity, different content. Nothing written.
    422 unknown_edge_endpoint          src or dst not present in PEW
    422 transfer_requires_mapping      relation=TRANSFER without mapping_id +
                                       mapping_digest (R6)
    422 unknown_relation               outside the closed vocabulary

Reads:

    GET /api/v1/fossil/edges?src_id=|dst_id=|relation=|mapping_id=
    GET /api/v1/fossil/lineage/{node_id}?direction=ancestors|descendants&depth=N

`lineage` walks `fossil_edges` transitively with a bounded depth and returns
the path, so a chain is *mechanically* traversable rather than reconstructed by
the caller (test X5-c, third clause). Cycles are detected and reported as a
named error, never silently truncated.

## 3. Delayed design projections (third amendment)

A projection arriving after the terminal observation and attestation is
recorded **against the existing run identity**:

- it writes to the existing `(encounter_id, run_id)`; it does **not** mint a
  new envelope, and it does **not** create a second encounter;
- it is idempotent on identical replay and 409 on a differing one — the
  existing `_classify_encounter` rule, unchanged;
- it **never** triggers re-execution: PEW has no execution path and will not
  gain one here;
- the sealed record, if one exists, is not rewritten. A projection that would
  change a sealed slot is a 409, because the seal is the tamper-evidence.

No new mechanism is required for this: it falls out of the existing
append-only identity rules, which is the point of stating it explicitly.

## 4. Eviction and read-index changes (test X5-d)

PEW holds references, so eviction upstream changes **availability**, never
history:

- an evicted witness moves `availability` PRESENT -> UNAVAILABLE by writing a
  **new** row (new `witness_id`, because availability is part of neither the
  identity tuple nor the digest — see note below) or, preferably, by an
  append-only `witness_availability_events` record. The original reference is
  never deleted or edited.
- **Design note / open decision:** availability is deliberately *not* part of
  the content address, so that the same witness reference keeps one identity
  across availability changes. That means an availability change cannot be
  expressed by re-writing the row (which is immutable). The clean form is a
  separate append-only availability log keyed by `witness_id`, with the
  current state derived as the latest event. I prefer the log; it is one more
  table but it keeps "what was referenced" and "whether it is reachable today"
  as different questions.
- read-index or query changes never reinterpret SFE history: PEW indexes, SFE
  interprets. Rebuilding an index is not an evidentiary act.
- back-filled records keep **original attribution**: `producer`,
  `submitted_by`, `machine` and `created_at` record who asserted it and when,
  and a back-fill is a new row with its own attribution, not a rewrite of an
  old one carrying today's identity. The LEGACY rule from migration 010 applies
  unchanged — nothing synthesizes a binding that did not exist.

## 5. Acceptance, restated as what would be run

One program-witness and one CA-witness round trip:

    write encounter -> write witness_ref (PRESENT, digest, source_id)
    -> GET witness by encounter -> resolve against SFE -> digest matches
    -> repeat identically -> duplicate_identical, no second row
    -> assert a TRUNCATED and an UNAVAILABLE witness, confirm they are
       distinguishable from ABSENT and from each other

plus a small typed chain:

    ANCESTOR a->b, MUTATION b->c, TRANSFER c->d through a declared mapping
    -> GET lineage descendants from a returns a..d in order
    -> re-writing any edge identically is idempotent
    -> re-writing one with a different mapping_digest is 409

Reference-only is satisfied: no witness bytes enter PEW at any step.

## 6. What this design does NOT license

It does not make PEW a witness store, a trace store, or an interpreter. It
does not decide whether a witness is scientifically meaningful. It adds no
ability to re-execute anything. And it does not settle D-1 (raw trajectories
and rasters): this design assumes the roadmap's answer — bytes stay in SFE,
digests ride in PEW — and if that assumption is ever reversed, this document
is not the authority for it.
