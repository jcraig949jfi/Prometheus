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
| Passes completed | 3 |
| Validator failures | 0 |
| Validator gate exit | 0 all three passes (now 18 worklog entries, 7 reviews) |
| Schema fields ambiguous/forced | 2 (`agent`, `soak_findings` — see SOAK-04) |
| Review round-trips (Elenchus → me → response) | **0** (see SOAK-08 — the untested half) |
| Worker→worker round-trips (my finding → Aporia repair → my verification) | 2, both closed and independently verified |
| Replication matches | 1 (AA-018, in kind) |
| Replication mismatches | 0 |
| Provenance findings raised | 2 (AA-018 tier + tightness) |
| Onboarding defects for a cold agent | 3 (SOAK-01, -02, -03) |
| Harness calibrations | 2 (R12 suite, 17/17 green both times) |
| Boundary cases designed + run | 7 (1 gap probe + 6 escape variants) |
| Safety gaps handed off via GATE_ELI5 | 1 |
| Own hypotheses killed by own tests | 3 (AA-018 staleness; integer-magnitude vector; expected-incomplete-fix) |
| Heartbeat successes | 0 of 3 (env-override, SOAK-05 — never blocked a pass) |
| Self-corrections caught before logging | 2 |

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

**SOAK-06 (mechanism).** Rotation (c) is well-supplied where rotation (a) was not: six
harness suites exist under `harmonia/experiments/`, each admitting boundary cases of the
worker's own design. **The cadence problem (SOAK-03) is specific to the anchor-replication
item, not to the role.** A second worker can sustain the cadence by rotating away from (a).

**SOAK-07 (observation).** The write-scope boundary held under pressure and produced a
*better* outcome than editing would have. Finding a safety gap in `r12_grader.py` — a file
this role may not touch — forced it through `GATE_ELI5.jsonl`, where its owner and James
can see it, instead of being silently patched by a soak worker. The constraint improved
the result rather than merely limiting it.

## Harness calibration ledger

| Suite | Result | Boundary case designed | Outcome |
|---|---|---|---|
| `test_r12.py` | 17/17 green | sequence-repetition vs the pinned `pow` bound | **GAP FOUND** |

**R12 sandbox finding.** `Pow` carries both a parse-time and an eval-time bound
(`r12_grader.py:156-164`, `:275-280`) with a test pinning it. `Mult` at `:269` is an
unguarded `return a * b`. Consequence: `'a' * (10 ** 8)` **compiles and is accepted**,
while the semantically parallel `pow` form is rejected. Measured scaling (10^4/10^5/10^6)
projects ~100 MB and ~41 ms per evaluation, and `extension()` invokes the predicate once
per universe object.

Two honest limits: **exhaustion was projected, not demonstrated** — the payload was
deliberately not executed — and **real-world reachability is unmeasured**, since I never
checked whether the emitter grammar can produce string literals. My first hypothesis
(integer magnitude blow-up) was **killed by my own test**: 12 chained factors reach ~10^96
in 0.01 ms, because bigint multiplication is cheap at every reachable magnitude.

A green 17/17 suite says the pinned properties hold. It says nothing about properties
nobody pinned — which is precisely where this boundary case landed.

**SOAK-08 (design) — the untested half.** After three passes the channel has demonstrated a
**worker-to-worker** round-trip (Aporia metabolized both soak findings in P28, verified
independently in P3) and **zero reviewer-to-worker** round-trips. Elenchus has filed no
review against any HARMA pass_id. The soak is therefore stressing the worklog, validator
and gate mechanisms thoroughly and the **review mechanism not at all** — so the headline
question can only be half-answered on current evidence.

**SOAK-09 (observation) — the channel out-produced the finding.** HARMA-P1 reported *one*
defective anchor (AA-018). P28 generalized it to a defect **class**, found 3 instances
registry-wide, and corrected all 3 — independently confirmed in P3 (0 of 72 entries now
pair `verified_against_primary=True` with a tertiary citation). A single-instance finding
from a second worker propagated into a class-level repair. That is the strongest argument
yet for a second worker existing at all.

## Repair-verification ledger

| Repair claimed (P28) | Verification | Result |
|---|---|---|
| R12 sandbox rejects sequence repetition | 6 escape variants + 4 regression cases + full suite | **COMPLETE, no regression** |
| AA-018 corrected, class of 3 all fixed | independent regex audit of all 72 entries | **CONFIRMED** |

**Repair completeness.** All six escape variants I designed — reverse operand order
(`(10 ** 8) * 'a'`, the classic incomplete-fix signature), bytes literal, tuple, list,
dynamic feature-valued multiplier, nested pre-multiplied string — are rejected at parse.
All four legitimate arithmetic forms still compile and evaluate, and the pinned suite
stays 17/17. **My prior was that at least one variant would slip through, because fixes to
reported shapes usually are shape-specific. None did; the repair is better than my
skepticism predicted, and that is recorded rather than quietly dropped.**

**One half-verification, not laundered into a full one.** Aporia claims rejection at parse
*and* eval. Every shape I can construct hits the parse gate first, so the eval-layer
defence-in-depth is an **unreached** claim component — logged as `withheld`, not confirmed.

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

Withheld — three passes is not a soak. The mechanisms have generalized to a second worker
without modification (validator green, schema accommodating, namespacing clean). The
strain is not in the mechanisms but in the **work supply** of one rotation item:
rotation (a) was exhausted after a single pass and rotation (b) remains blocked on the
same host defect that blocks the heartbeat — but rotation (c) is deep enough to carry the
cadence alone, so the role itself is not cadence-limited.

Pass 2 produced the first finding that matters to someone other than this soak: a
resource-exhaustion gap in a sandbox whose sibling property is test-pinned. That is the
role working as intended — a second, independent worker found something the first worker's
own test suite did not pin.

Pass 3 closed both loops and verified them adversarially rather than on trust. The
mechanisms are now well-evidenced. **The open risk is no longer whether the worker role
generalizes — it is that the REVIEWER half has never engaged** (SOAK-08). A soak that ends
with 0 reviewer round-trips will have answered "can a second worker use this channel?" and
left "can the channel review a second worker?" untouched.
