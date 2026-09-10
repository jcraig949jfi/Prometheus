# H3 candidate stream — Archaeon's format, v0 (2026-09-10)

For Techne's adapter (`techne/h3_retention/STREAM_CONTRACT_V0.md`), which was
written against a declared fixture and says it will lose to this. The diff
is small and is listed at the end; Techne's five properties are kept as
REFUSALS in `archaeon/producer/h3_replay.py::stream_manifest`.

## One record per candidate (`archaeon.producer.h3_replay.Candidate`)

    stream_id          int     0-based, contiguous, strictly increasing (the order)
    candidate_digest   str     sha256 over the canonical candidate payload
    birth_status       str     "evaluated" | "failed"   (failed rows STAY in the stream)
    assay_ref          str     one value for the WHOLE stream (refused otherwise)
    score              float   None iff failed
    descriptors        tuple   fixed length; binned by declared edges at replay
    byte_size          int     what retention charges against the byte cap
    replay_ref         str     resolves to the full authoritative result
    parent_ids         tuple   stream_ids that must appear EARLIER (empty = seeded)

## The manifest (`stream_manifest`)

    schema, n, n_failed, stream_digest (sha256 over every record in order),
    assay_ref, duplicate_digests (detected and recorded, never refused),
    descriptor_dims

## Where the first real stream comes from

Track B's C3 corpus (`campaign_c3.py`): 132 rows today, one seed_root, four
shared IC samples. Mapping: stream_id = issue order; candidate_digest =
sha256 of the sealed payload (rule_hex + parameters); birth_status =
evaluated iff the run completed with a scored observation, failed otherwise
(error, budget, infrastructure); assay_ref = "ca_density_v0@<kind_version>:
seed_root=930001:n_ic=100:steps=320"; score = accuracy under the declared
criterion; descriptors = (rule-table popcount, output-1 count among centre-1
neighbourhoods) — declared, versioned, never learned; byte_size = the sealed
spec bytes plus the retained result projection; replay_ref =
"sfe:<world_id>/<observation_id>@<event_seq>"; parent_ids empty (C3 has no
lineage; the C3-mut arm later will).

The actual stream size is recorded as what it is (132 or 150 with the null
arm), not silently 1,024; the 1,024-candidate figure is a development-size
proposal for a generated stream.

## Diff against Techne's contract

- `birth.status` vocabulary: Techne has SEEDED/MUTATED/RECOMBINED/REPLAYED;
  Archaeon has evaluated/failed plus `parent_ids`. Lineage kind can be
  derived from `parent_ids` (0 parents = seeded, 1 = mutated, 2+ =
  recombined); "replayed" is a property of the replay, not the candidate.
  Proposal: keep Archaeon's two-valued status for what happened at birth and
  add Techne's lineage kind as a derived field in the adapter.
- `assay_ref`: Techne carries {assay_id, assay_version, digest}; Archaeon a
  single string. Adopt Techne's structured form at the seam; the refusal is
  the same.
- `result_ref` bytes check: Archaeon carries `replay_ref` and `byte_size`;
  the resolver check is Techne's and is kept in the adapter.
- Caps: Archaeon evaluates the byte cap on the delta and refuses full grids
  without evicting other cells; count cap binds on new cells only; three
  bounds reported per policy (count, bytes, grid cells) with none_bound
  stated. This matches Techne's measured coupling.
- Ties: FIRST_WRITER_WINS at both granularities, declared; Archaeon's
  behavioral archive replaces only on STRICTLY greater objective.
