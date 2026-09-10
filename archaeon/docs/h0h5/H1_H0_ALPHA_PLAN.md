# H1 / H0 alpha — Archaeon's issue plan (2026-09-10, on Vivarium 6d5d7406f)

Code: `archaeon/producer/campaign_h1h0.py`; tests `archaeon/tests/test_campaign_h1h0.py`.
Kind: `cegis_boolean_v1` (Vivarium owns the contract; Proteus the semantics).
Harmonia analyses; nothing here computes a contrast.

## Two phases

1. **Source** (`plan_phase1`, 24 rows): fresh CEGIS on 24 SOURCE tasks, both
   slots null, trace_bound 32. The ordered witnesses are the ONLY failure
   pool. Validates against the kind today (`check(plan_phase1())` ok).
2. **Alpha** (`plan_phase2`): packs built from phase-1 witnesses under a
   frozen seeded policy, published as `failure_input_set` artifacts (human
   path: producer world, `client.artifact`, locators outside spec_hash), then
   on 12 TARGET tasks:
   - H1 `fam-H1-1`: `fresh`, `random_pack`, and `relevant_pack` (WITHHELD, see
     below) — 24 rows now, 36 when licensed.
   - H0 `fam-H0-1`: S00 / S10 / S01 / S11 — 48 rows; the four cells of one
     task differ in exactly the two slot positions (tested).

Task split: seeded (940002), disjoint by construction, constants excluded.
Unit of analysis: the target task, paired across arms and cells.

## The relevance question, stated rather than dodged

The design (s5 H1) allows alpha to rank by "a declared structural signature
of task specification visible equally to all arms", forbids hidden target
labels, and says that if no fair feature exists alpha demonstrates transport
only. `signature_v0` ranks source tasks by agreement on four flags recorded
on every task (popcount bucket, permutation-symmetric, self-dual, monotone).
Those flags are computed from the specification and are readable by all
arms; whether a rank on them is FAIR (they are functions of the target's
labels, obtained without oracle calls) is exactly Harmonia's ruling to make.
Until the operator sets `RELEVANCE_LICENSED = True` on that ruling, the
relevant arm is planned and marked withheld and the alpha is
transport-only (fresh vs random-compatible), which the design permits.

## What Vivarium's demonstration already tells us about the scope

At vm_op_cap 30000 every arm scored 5/6 and the per-task matrix moved in
opposite directions (maj3 won, xor3 lost by the instrument library). At 6000
the tasks spread across solved / budget / exhausted. BASE_PAYLOAD declares
6000 as a pilot choice; a change is a new campaign id, never a retune.

## Blocked on

- Phase 1 issue: the operator's word, and a running consumer that carries
  `cegis_boolean_v1` (Vivarium restarts after its push; Vivarium says which).
- Phase 2: phase-1 results; the artifact publish path with a producer world
  (Archaeon has no engine scope today — the human path publishes).
- Relevant arm: Harmonia's fairness ruling; then `RELEVANCE_LICENSED`.
- Beta's derived library: `extract_library()` exists; it needs phase-1
  SOLUTIONS and is labelled `derived`. The alpha library is the hand-built
  MAJ3-subterm INSTRUMENT CONTROL and is labelled so on every row.
