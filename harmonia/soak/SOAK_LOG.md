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
| Passes completed | 6 |
| Validator failures | 0 |
| Validator gate exit | 0 all six passes (now 23 worklog entries, 7 reviews) |
| Schema fields ambiguous/forced | 2 (`agent`, `soak_findings` — see SOAK-04) |
| Review round-trips (Elenchus → me → response) | **0** (see SOAK-08 — the untested half) |
| Worker→worker round-trips (my finding → Aporia repair → my verification) | 2, both closed and independently verified |
| Replication matches | 1 (AA-018, in kind) |
| Replication mismatches | 0 |
| Provenance findings raised | 2 (AA-018 tier + tightness) |
| Onboarding defects for a cold agent | 3 (SOAK-01, -02, -03) |
| Harness calibrations | 2 (R12 suite, 17/17 green both times) |
| Boundary cases designed + run | 7 (1 gap probe + 6 escape variants) |
| Mirror-trap drills run | **3 of 7+** documented traps (1, 5, 6 — all live data, all CONFIRMED) |
| Vacuous results caught before publication | 1 (see SOAK-10) |
| Doctrine items handed off via GATE_ELI5 | 2 (sandbox gap; trap-8 candidate) |
| Own hypotheses killed by own tests | 4 (+ 'trap 1 is stale', killed by my own triage) |
| New trap candidates found | 1 (identifier-case mismatch), now quantified mirror-wide |
| Own prior-pass weaknesses closed | 1 (P5's "trap-8 prevalence unmeasured" → P6 measured it) |
| Heartbeat successes | 0 of 6 (env-override, SOAK-05 — never blocked a pass) |
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

**SOAK-10 (onboarding).** Rotation (b) says to drill traps "against the live local
Postgres". The database the code points at by default (`prometheus_fire`) contains **none
of the trap preconditions** — 255 of 257 text columns have zero numeric-string rows. The
traps are documented against the **lmfdb mirror**, which the brief never names. A cold
worker following the brief literally probes the wrong database and gets a vacuous zero
that looks exactly like *"the trap is stale."* Same defect class as SOAK-01: the brief
names a resource without naming where it lives.

**SOAK-11 (correction, against myself).** Postgres was reachable from M2 the whole time
with `lmfdb/lmfdb`; only the env-supplied credential pair is broken. **I deferred rotation
(b) twice on "Postgres unreachable" without ever testing explicit credentials** — I
inherited that belief from the heartbeat failure instead of probing it. The blocker was
credential-shaped, not availability-shaped. This also narrows SOAK-05: the heartbeat
defect is *entirely* the env-var pair, not database availability.

## Mirror-trap drill ledger

| Trap | Drilled | Failure mode reproduces | Safe form works |
|---|---|---|---|
| 1 — numeric columns stored as TEXT | live `lmfdb.public.ec_curvedata` | **YES, 14 of 26 probed columns** | **YES** (`::numeric`) |
| 2–7 | not drilled | — | — |

**Trap 1 is live, not stale.** The documented case reproduces exactly:
`ec_curvedata.conductor` gives lexicographic max `'5568821'` against numeric max
`55688177`. The widest divergence is `ec_curvedata.degree` — `'999950'` versus
`290094317568`, about six orders of magnitude. Twelve more columns fire
(`adelic_level`, `adelic_index`, `nonmax_rad`, `iso_nlabel`, `sha`, `torsion`, …), and
the documented safe form returned the correct maximum in every case.

**The near-miss is the more useful half.** My first scan covered 257 columns of
`prometheus_fire` and returned **0 hits** — and the write-up I was one paragraph from
publishing said "trap 1 is stale on this mirror." ATTACK_PATTERNS trap 4 says an
all-empty result is a VACUOUS reading demanding diagnosis, never a shrug. Diagnosing it
showed **ACTUALLY PROBED = 0**: the scan had tested nothing. **The doctrine's own trap
caught my own probe.** The triage step should have been in the first scan rather than
added after a suspicious result — that is a weakness in my method, not a win for it.

**SOAK-12 (observation) — the format carries method forward.** P4's vacuous zero taught
that a raw zero needs a discriminator. P5 designed the discriminator *into the pre-stated
readings before any query ran*, rather than reaching for it after a suspicious result. **No
reviewer prompted this — the worker's own prior failure did.** That is weak evidence the
worklog format itself propagates method between passes, which is exactly the property you
want in a role meant to be occupied by cold agents who inherit nothing but the log.

**SOAK-13 (design) — GATE_ELI5 is the binding constraint, not worker throughput.** Two of
the last three passes produced doctrine additions the worker is structurally forbidden to
apply (P2's sandbox gap, P5's trap-8 candidate); both left via `GATE_ELI5.jsonl`. The
channel generates doctrine faster than a write-scoped worker can land it. Not a defect —
SOAK-07 argued the boundary improves outcomes — but it means **GATE_ELI5 drain rate**, not
worker productivity, governs how fast a second worker improves doctrine.

### Trap 6 — cross-table key spelling (attack 0130)

| measure | value |
|---|---|
| distinct keys | artin `"Conductor"` 332,779 · newforms `level` 123,365 |
| **RAW string join** | **0 keys intersect** |
| **NORMALIZED `::numeric`** | **50,835 keys** (41.2% of newform levels) |
| discriminator: numeric ranges | artin [1, 9.99e15] · newforms [1, 999983] — **overlap** |
| verdict | **spelling artifact, not disjoint domains** |

Raw spellings observed directly before measuring: `'12435.0'`, `'78656.0'` against
`'1008'`, `'1023'` — exactly as attack 0130 describes.

**The discriminator is the point.** A raw-join zero has two possible causes — a spelling
artifact or key domains that genuinely never meet — and they demand opposite responses.
Trap 6 as documented does not say how to tell them apart; comparing the numeric ranges
does, and it was written into this pass's readings *before* any query ran.

**Not claimed:** that any of the 50,835 numerically-equal keys is a mathematically
meaningful correspondence. That is a join repair, not a discovery, and it is logged
`withheld`.

**Trap-8 candidate (new, handed off).** `artin_reps` exposes quoted CamelCase columns
(`"Conductor"`, `"Dim"`) while `mf_newforms` uses lowercase. A case-sensitive column filter
over `artin_reps` returns an **empty column list rather than an error** — my own first
query hit exactly this and looked like "the table has no conductor field." Found
incidentally by my own failure, not by systematic scan, so it goes to the doctrine's owner
as a candidate rather than a measured trap.

### Trap 5 — booleans as Python-literal text (attack 0062)

`artin_reps."Is_Even"`, 798,140 rows:

| predicate form | rows matched |
|---|---|
| `= 't'` (natural Postgres) | **0** |
| `= 'true'` (lowercase) | **0** |
| `= 'True'` (Python literal) | **319,289** (40.0%) |
| `::boolean = true` (safe form) | **319,289** |

**The surface is total, not partial: 29 boolean-semantic columns in the mirror, and
0 are actually typed `boolean`.** No boolean-semantic column anywhere here is safe to
query naturally.

The discriminator ran *first* this pass — enumerating stored values before counting
matches — so the zeros arrived already attributable to wrong-literal rather than to an
empty predicate. Every sampled column stores exactly `['False','True']`.

### Trap-8 candidate, now quantified (closing P5's own weakness)

| table | mixed-case identifiers |
|---|---|
| `artin_reps` | **21 / 22** |
| `lfunc_lfunctions` | 10 / 71 |
| `ec_curvedata` | 5 / 52 |
| `mf_newforms` | 1 / 81 |
| `g2c_curves` | 1 / 51 |
| `nf_fields` | **0 / 43** |
| **mirror-wide** | **38 / 320 (11.9%)** |

**The rate is the boring number; the bimodality is the finding.** A worker who learns
"columns are lowercase" from `nf_fields` or `mf_newforms` is silently wrong in
`artin_reps` — and the failure mode is an *empty column list rather than an error*.
Measured, not adjudicated: whether this belongs in the trap list is the doctrine owner's
call, and no second GATE entry was filed because SOAK-13 identified gate drain rate as
the binding constraint.

**SOAK-14 (observation) — the weakness list is a work queue, not a disclaimer.** P5 listed
"trap-8 prevalence unmeasured"; P6 measured it, unprompted. With SOAK-12 (P4's vacuous zero
→ P5's designed-in discriminator), the mandatory `self_identified_weaknesses` field has now
set the agenda for two consecutive passes. **For a role meant for cold agents who inherit
only the log, that is the schema field carrying the most weight — and the brief describes
it in one line.**

**SOAK-15 (design) — rotation (a) is ~1/3 dead weight.** Six passes in, every unit of real
work came from (b) or (c); (a) supplied exactly one pass. The two live items differ sharply
in depth: (b) has 4+ undrilled traps, (c) has 5 unexercised harness suites. A revised brief
should demote (a) to opportunistic rather than an equal third of the rotation.

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

Withheld — six passes in; the shape has been stable for four, and the method is still tightening. The mechanisms have generalized to a second worker
without modification (validator green, schema accommodating, namespacing clean). The
strain is not in the mechanisms but in the **work supply** of one rotation item:
rotation (a) was exhausted after a single pass and rotation (b) remains blocked on the
same host defect that blocks the heartbeat — but rotation (c) is deep enough to carry the
cadence alone, so the role itself is not cadence-limited.

Pass 2 produced the first finding that matters to someone other than this soak: a
resource-exhaustion gap in a sandbox whose sibling property is test-pinned. That is the
role working as intended — a second, independent worker found something the first worker's
own test suite did not pin.

Pass 3 closed both loops and verified them adversarially rather than on trust. Pass 4
drilled the first live mirror trap and, more usefully, caught its own vacuous result
before publishing it. The mechanisms are now well-evidenced. **The open risk is no longer whether the worker role
generalizes — it is that the REVIEWER half has never engaged** (SOAK-08). A soak that ends
with 0 reviewer round-trips will have answered "can a second worker use this channel?" and
left "can the channel review a second worker?" untouched.
