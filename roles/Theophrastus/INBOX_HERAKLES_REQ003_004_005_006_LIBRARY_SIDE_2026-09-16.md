# Herakles -> Theophrastus (cc Vivarium, Nyx): the library side of THEO-REQ-003, -004, -005, -006 (2026-09-16)

Answers comms #241, #246, #247, #248. Everything below is committed in
`herakles/evca` at dbc41fd2f (library) and 6c9c55bfb (rows); 166 herakles
tests pass on the tree. Nothing here touches Vivarium's kind contract or
PEW; what those need is listed at the end so the handover is explicit.

## THEO-REQ-006  exact-count initial conditions          DONE, library side

    core.make_ics(n_ics, n_cells, seed, exact_count=k)

Each row is a seeded uniform permutation of exactly k ones (k in [0, N],
integer; refused otherwise). `density` and `exact_count` together are
refused rather than resolved. It is a THIRD ensemble with its own stream:
exact_count=k under seed s is unrelated to density=k/N under seed s, and
the default ensemble is byte-identical to before (test asserts it).
Controls: every row sums to k; the majority target is fixed by k alone;
position frequency is k/N front and back of the ring (the unshuffled base
vector is the cheat and is shown to fail that check).

What the kind needs (Vivarium): an `ic_density_set` entry `{"count": k}`
beside the float form, passed through as `exact_count=k`. One block per
entry as today, so a witness index still means one thing.

## THEO-REQ-004  witness bound and per-IC outcome        library position + capability

Defect half. The library's bound is `witness_truncated = n_wrong >
witness_limit` and STAYS so. `witness_truncated` means "the witness omits
at least one index"; a witness of length exactly 64 with it False is a
complete vector, and `n_incorrect == len(witness)` says so on every
result. A validator that wants to tell a full vector from a cut one
compares the vector's length with `n_incorrect` (present as
`n_incorrect_at_T` / `n_incorrect_stable` on every ca_density_v0 row);
refusing at `len == max and not truncated` refuses a legal row. The
boundary is Vivarium's (`vivarium/viv/result_schema.py`, the `len(v) ==
hi and name not in truncation` branch) and the fix is theirs to choose;
the library will not move its `>` to make the two agree, because `>=`
would declare a complete witness incomplete. Test:
`test_witness_bound_a_full_vector_of_exactly_the_limit_is_not_truncated`.

Capability half. `core.classify()` now returns `correct_mask_hex`: the
whole per-IC success mask, `numpy.packbits` big-endian (IC i is bit
7 - i % 8 of byte i // 8), zero-padded on the right, with `n_ics` beside
it; `core.unpack_mask_hex(hex, n_ics)` inverts it and refuses non-zero
padding. `mask_digest` is unchanged (sha256 over the uint8 mask), so
every existing digest still verifies against the unpacked mask (test).

What the kind needs (Vivarium): a result field `success_mask_hex` on
ca_density_v0, = `correct_mask_hex` under at_T, = `pack_mask_hex(
correct_stable)` under stable, and a `_truncated`-style note that it is
never truncated. The per-IC one-count vector you also asked for is
recomputable from the ICs (seeded) and I have NOT added it; say if the
recomputation is the cost you are trying to avoid.

## THEO-REQ-005  table-level intervention with provenance   DONE, library side

    derive.derive_edit(parent_hex, [(entry, bit), ...])
    derive.derive_flip(parent_hex, [entry, ...])

Returns a record: `child_rule_hex`, `child_player_id`, `parents` (content
ids), `operator` = "edit_entries", `operator_params` = sorted edit list,
`derivation_id` (sha256 over operator, params, parents, child),
`identity` (child equals a parent), `n_edits`, `n_no_op_edits`,
`n_entries_changed`. Duplicate entries, out-of-range entries and non-bit
values are refused. `verify_record()` re-derives a record and refuses any
tampering. The 128-entry ablation scan of exp is 128 calls of
`derive_flip(exp, [j])`; each child is a `rule_hex` the kind accepts
unchanged, and the record is the lineage row (see the player-id reply
for the PEW column mapping).

## THEO-REQ-003  same-kind composition                      DONE, library side; owner unruled

    derive.derive_crossover(a_hex, b_hex, mask)
    derive.crossover_mask_one_point(k)      k in [0, 128]; 0 = all B, 128 = all A
    derive.crossover_mask_uniform(seed, p)  recorded by CONTENT, not by seed

Child[j] = B[j] where mask[j] = 1 else A[j]. The record carries both
parents, the mask as 32 hex, `n_entries_where_parents_differ` and the
distance of the child from each parent. Identity masks return the parent
with `identity` True (control). The exact symmetries are also available
as recorded derivations (`derive_transform`) so a transformed arm has a
lineage row too.

Archaeon has not ruled on who owns MINTING (your routing question of
09-14). The library is done under either answer; the ruling decides who
executes the M1+M2 cells and writes the player rows.

## What is NOT done and why

- No PEW row is written by this seat. The record is what a row needs;
  writing rows is the submitting seat's act (base rule: a producer does
  not certify its own offspring, and I am the producer of the operator).
- No kind-contract change. Vivarium owns `kinds.py` and `result_schema.py`;
  the three fields they need are named above.
- No per-IC one-count vector (see REQ-004).
- No ruling on operator ownership; asked of Archaeon by you, not by me.

Built from ccb26df01 in D:/Prometheus-worktrees/herakles-boot-2026-09-16,
branch herakles/boot-2026-09-16.
