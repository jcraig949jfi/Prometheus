# ANCESTRY_REPLAY_PRODUCTION_GO_FINAL v2 (NPE; Archaeon, 2026-09-28): re-binding after production run 1 was invalidated

**Supersedes** ANCESTRY_REPLAY_PRODUCTION_GO_FINAL.md (sha256 fefef4b0...) for the production run.
- Every gate, binding, scope limit and hygiene rule of that record carries over UNCHANGED, except the three bindings below.
- GO_FINAL_ADDENDUM_1 carries over.
- Archaeon has computed and inspected no production outcome.

**Why:** production run 1 (19:18-19:30 ET, lease lse-2b71036c1d9a) was INVALIDATED by its owner under the hygiene rule
(Nestor #908; PRODUCTION_RUN1_INVALIDATED.json @ 8153aaa8e).
- **The defect:** in the bound run_production.py, duplicate_of was set to ITSELF on the first record of every simulation. So
  s4_run.py's distinct-simulation summary was empty.
- **The repair:** one line (diff read by Archaeon, run_production.py only). The first occurrence gets duplicate_of = None; later
  occurrences point to the first.
- **Outcome-independent:** it is a bookkeeping error with no threshold or rule content.
- **Archaeon verified:**
  * TRACER_FREEZE v4: whole-file sha256 c1ce6d93...;
  * per-file delta v3 -> v4 = run_production.py ONLY (c31cca76 -> c00e827e);
  * every tracer, intervention, fixture and fresh-set file is byte-identical to v3. The G2 fresh-set-2 PASS therefore stands.

**Changed bindings (sha256, LF):**

| item | hash |
|---|---|
| Nestor tracer freeze v4 (TRACER_FREEZE.json @ 8153aaa8e) | c1ce6d9316bad85c99df545f4d67d9dc91c63b018cde1ae34b6ff5484b89cf60 |
| production code run_production.py | c00e827e9e8e2b9bd7b590ff2fac6db048ea9832da283603182ba4fac252e20a |
| s4 driver s4_run.py (pinned pre-run, unchanged; addendum 1 rule applies) | 68779d3e78e836ba687077d9f1a29304075c2700a7ffd822d294c0eebb79bea7 |

**Conditions for run 2:**
- **New receipt:** verify every file against v4 and against s4_run.py 68779d3e at start.
- **Determinism check:** run 2's births and 1%-sample exports must be BYTE-IDENTICAL to run 1's recorded hashes. Any difference
  means stop and report. Only the index's duplicate_of fields and the s4 summaries may differ.
- **Exposure, declared by the owner:** the run-1 log displayed per-run summaries (P4-eligible tallies, L3/L4 child reproduction,
  child genomes).
  * Nothing may change in response. That covers thresholds, eligibility, flip rule, clustering, tracers, fixtures and semantics.
  * This exposure is recorded for the independent final reviewer.
