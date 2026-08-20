# Shadow-worker role — soak test tally

**Worker:** Harmonia-A (second, independent worker on the shadow channel)
**Machine:** M2 / SPECTREX5 · **Repo root:** D:\Prometheus
**Soak start:** 2026-08-20T12:40:36Z · **Final pass due by:** 2026-08-21T12:40Z
**Question under test:** do the shadow-worker mechanisms (schema, validator, review
loop, gates) generalize beyond the agent they were built around?

Rough edges are the product. Nothing here is worked around silently.

---

## Running tally

| Metric | Value |
|---|---|
| Passes completed | 1 |
| Validator failures | 0 |
| Validator gate exit | 0 (14 worklog entries, 7 reviews, both valid) |
| Schema fields ambiguous/forced | 2 (`agent`, `soak_findings` — see SOAK-04) |
| Review round-trips (Elenchus → me → response) | 0 (no review yet references a HARMA pass_id) |
| Replication matches | 1 (AA-018 computational basis, in kind) |
| Replication mismatches | 0 |
| Provenance findings raised | 2 (AA-018 tier + tightness) |
| Onboarding defects for a cold agent | 3 (SOAK-01, -02, -03) |
| Heartbeat successes | 0 of 1 (env-override, see below — never blocked a pass) |
| Self-corrections caught before logging | 1 |

## Soak findings

**SOAK-01 (onboarding).** The brief directs the worker to `aporia/anti_anchors/`. That
path does not exist; the registry is `techne/registry/anti_anchors.jsonl`. A cold worker
following the brief literally finds nothing.

**SOAK-02 (onboarding).** The brief says to select anchors "graded A3-A4", but `grade`
is not a top-level field — it is nested at `attestation.grade`, and absent on 15 of 72
entries. I nearly logged "the registry has no grade field" as a defect before checking
the nested object. That would have been a false finding; it was caught pre-log. The
discovery path is fragile for a cold agent, which is the actual defect.

**SOAK-03 (design).** Rotation item (a) presumes a population of anchors with local
computational bases. Of 23 A3/A4 anchors, 4 mention computation and exactly **1**
(AA-018) is locally replicable in bounded form — AA-013's own attestation states its
proof is algebraic, "not exhaustive computational search". **Rotation (a) exhausts in
roughly one pass and cannot sustain a 24-hour cadence as written.** This is the most
consequential finding so far: the role's work-rotation is under-supplied for a second
worker, even though it was adequate for the agent it was designed around.

**SOAK-04 (mechanism) — RESOLVED THIS PASS.** `WORKLOG_SCHEMA.md` v1 defines no `agent`
field, though the brief mandates one for namespacing, and no field exists for soak
findings — the very product this soak generates. Both were carried as extra keys.
**The validator tolerates extra keys (exit 0),** so the mechanism generalizes; but the
schema doc and the worker brief disagree about what a record contains, and the doc is
the one a cold agent reads.

**SOAK-05 (infra, pre-existing, not caused by this soak).** The heartbeat fails on M2.
`scripts/resolved_config_probe.py` reports the cause precisely:

```
AGORA_POSTGRES_HOST     192.168.1.176   source: ENV-OVERRIDE
AGORA_POSTGRES_PASSWORD prom…           source: ENV-OVERRIDE
agora_persist_resolves  host=192.168.1.176 user=lmfdb
heartbeat_write         false
```

This is a **host** defect (persistent env vars on M2), not a repo defect, and no commit
can fix it. Per the brief a dead heartbeat never blocks a pass, and it did not. Noted
here because a soak worker that cannot heartbeat is invisible to the orchestrator, so
any liveness-derived metric will under-count this worker for the whole 24 hours.

Worth recording as a loop success: this probe is exactly the per-machine resolved-config
instrument recommended in the Elenchus cycle-2 feedback, and it now exists and works.

## Replication ledger

| Anchor | Grade | Basis replicated | Result |
|---|---|---|---|
| AA-018 COLLATZ | A3 | independent 3x+1 implementation, calibration + bounded sweep | **MATCH (in kind)** |

**AA-018 detail.** Calibration passed on 7 published total stopping times before any
sweep ran (mechanically enforced: the script exits nonzero on a calibration miss). Sweep
over [2, 10^7] found 0 counterexamples in 7.5s. That range is **4.24e-15** of the cited
bound and therefore contributes nothing to it — recorded as such, not as support.

Two provenance findings, neither an error in the anchor's truth value:
1. AA-018 carries `verified_against_primary: True` while citing **Wikipedia**, a
   tertiary source. The primary is Barina, *J Supercomput* 81, 810 (2025).
2. The anchor's `2.36e21` is **true as written but not tight**: it equals 2^71, while the
   current verified bound is 2075 × 2^60 = 2.3923e21 (milestone 2025-01-15). The anchor
   understates the record by **1.30%**.

A staleness hypothesis was formed (a 2025 paper titled "Improved verification limit"
suggested the number was superseded) and **killed** — the improved limit *is* ≈2^71.02,
so 2^71 sits just under it rather than a generation behind.

## Verdict so far

Withheld — one pass is not a soak. The mechanisms have generalized to a second worker
without modification (validator green, schema accommodating, namespacing clean). The
strain is not in the mechanisms but in the **work supply**: rotation (a) is nearly
exhausted after a single pass, and rotation (b) is blocked on the same host defect that
blocks the heartbeat.
