# Techne Substrate Fire Log — 2026-06-15

## Session: network restored, 50 pending commits landed, REQ-028 forged (operator-portability orchestrator)

**Context on entry.** Resumed Techne after the 2026-06-09 session that ended with
~50 commits stuck behind a dead IPv4 WAN path (IPv6 up, github IPv4-only → push
blocked, fix was physical/router). Six days elapsed.

---

## 1. Network + sync

- IPv4 is back (`curl -4 github.com` → 200 in 0.30s). The router/ISP IPv4 path
  was restored at some point in the gap.
- The 50 pending commits **made it to origin** (another machine pushed; remote
  advanced past the local `070a9096` to `00cd93b3`). On entry: **0 ahead, 42
  behind**. Fast-forward pulled cleanly — other roles (Harmonia B/D/E proposals,
  auto portfolio updates) had advanced main. The `pending_50_commits_*.bundle`
  safety artifacts are now redundant but left on disk (not mine to delete; one
  belongs to Aporia).

---

## 2. Forged: TOOL_OPERATOR_PORTABILITY (REQ-028) — the open high-urgency queue item

Picked REQ-028 over the other open item (REQ-008 Khovanov Betti, blocked since
April on heavy native deps JavaKh/KhoHo/Sage). REQ-028's dependencies had **all
shipped since it was filed** (REQ-027 TT_SPLICE, REQ-030 rank-parity null,
REQ-031 tail/bulk) — it was ripe, in-lane, no native-dep risk.

**What shipped** (math-tdd, test-first):

- `techne/lib/operator_portability.py` — the orchestrator. Contract:
  `{effect_size, p_perm, bond_rank_delta, replication_status∈{survived,killed,
  inconclusive}, pattern_flags, audit}`.
- `techne/lib/tt_splice.py` — **two additive public kernels**
  (`splice_score_arrays`, `prime_detrend_arrays`) extracted behavior-identically
  from REQ-027's observed-score path so the orchestrator composes the audited
  kernel in-memory without NPZ round-trips. `tt_splice_compatibility` untouched;
  its 5 tests stay green.
- `techne/tests/test_operator_portability.py` — 11 tests, **A:3 P:3 E:3 C:2**,
  all green.
- `techne/OPERATOR_PORTABILITY_RESULTS.md`, TDD_LOG entry, inventory.json (+1 →
  26 tools), REQ-028 → fulfilled.

**THE finding (assume-wrong → measured before building).** I probed the REQ-027
splice score before designing the null layer and it killed the naive design:

- The bond-rank statistic is **EXACTLY row-permutation invariant** (0.707 →
  0.707). It measures *column-subspace* overlap; row order is irrelevant.
- Therefore the F011/F010 **block-shuffle-within-CONDUCTOR** discipline
  (`harmonia/audit_P028_block_shuffle.py`: plain z=+2.38 "endorsed" → conductor-
  block z=−0.86 "killed") — a **row-pairing** null — **cannot falsify this
  statistic**. A conductor-stratified row-shuffle leaves the score unchanged and
  would report z≈0 ("killed") for everything.
- REQ-028 as written fused two statistically incompatible objects: F011's
  confound lives on **rows** (per-curve conductor); the bond-rank signal lives on
  **columns** (features). Shipping the naive tool would have silently killed
  every real finding.

**The stand.** Nulls act on the axis the statistic sees (feature/value), ordered
by conservativeness: `matched_GUE` (default, null≈0.30) > `block_shuffle`
(feature-strata, ≈0.26) > `permutation` (column, liberal, ≈0.23). Constructed
ground truth: shared rank-2 column factor → 0.707 ≫ null → **survived**;
independent Gaussian → 0.232 ≈ null → **killed**. **Row-axis null requests are
rejected** so the degenerate null can never masquerade as a passed falsification.
`block_shuffle` without `feature_strata` raises (no silent weak-null fallback);
degenerate/zero-variance nulls → `inconclusive`, never quiet survived/killed;
`symbol@version` operator specs raise NotImplementedError (registry out of
scope). conductor/stratify_conductor params accepted for spec fidelity but
flagged orthogonal, never used to stratify.

**Doctrine.** assume-wrong/kills-are-the-output (row-invariance measurement is
the tool's central guard) ✓; narrative-resistance (did not paper over the
row/column conflation to make the spec "work") ✓; backwards-compat +
behavior-preserving (tt_splice additive only) ✓; permutation-null + prime-detrend
mandatory, both flagged ✓; document-as-you-go ✓.

**Regression discipline.** Blast radius proven minimal: tt_splice's only
importers are the new module + the two test files. Targeted surface fully green
(tt_splice 5p/1s, operator_portability 11p). Broader Techne suite: ~78 tests
passed, **0 failures**, before a 150s wall-clock cap hit pre-existing slow
pari/cypari tests (no `pytest-timeout` installed; those tests predate and are
unrelated to this additive change).

---

## 3. Flagged for Aporia (cross-role, filed not actioned)

1. **REQ-028 conflates two statistics.** The 1-D gap-variance F011 row-pairing
   pipeline (where conductor-block-shuffle IS the correct null) should be filed
   as a **separate** tool from this column bond-rank orchestrator. Same name →
   the exact confound this tool dodges.
2. **REQ-027's internal permutation null is row-based** → likely near-degenerate
   for column-structured tensors (its `null_p_value` may be uninformative). Worth
   an audit; not fixing the frozen REQ-027 interface here.

Also still owed (from 2026-06-09, unchanged — coordinated, not solo): the
one-line Walk-Z/PRM reward-site integration of the reasoning-quality emit
primitive touches Ergon's reward pipeline → next cross-role pass.

---

## Git state at session end

`main`. Local commit for the REQ-028 forge created this session. **Push pending
explicit go-ahead** (pull-then-push; remote may advance from the other machine).

— Techne, 2026-06-15
