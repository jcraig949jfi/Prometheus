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
| Passes completed | 26 |
| Validator failures | 0 |
| Validator gate exit | 0 all twenty-six passes (now 63 worklog entries, 15 reviews) |
| Schema fields ambiguous/forced | 2 (`agent`, `soak_findings` — see SOAK-04) |
| Review round-trips (Elenchus → me → response) | **1** — first at P25, and it is TRIAGE only (see SOAK-53) |
| Worker→worker round-trips (my finding → Aporia repair → my verification) | **4**, all closed and independently verified; fastest ≈30 min |
| Replication matches | 1 (AA-018, in kind) |
| Replication mismatches | 0 |
| Provenance findings raised | 2 (AA-018 tier + tightness) |
| Onboarding defects for a cold agent | 3 (SOAK-01, -02, -03) |
| Harness calibrations | **7 — all 6 suites now covered**; every one green, 5 of 6 yielded a boundary defect |
| Boundary cases designed + run | 31 (+5 unregistered-kind probes, +2 regression simulations) |
| Mirror-trap drills run | **5 confirmed** (1, 2, 5, 6, 7) + **1 diagnosed-absent** (3) |
| Vacuous results caught before publication | 1 (see SOAK-10) |
| Doctrine items handed off via GATE_ELI5 | 17 (incl. **4 corrections against my own entries**) |
| Own hypotheses killed by own tests | 4 |
| **Instrument self-audits that changed a finding** | **5** (P4 · P7 · P9 · P14 · P19 wrong field name) |
| Self-corrections against a published pass | **10 correction-typed claims** across 17 passes (see P17 audit) |
| New trap candidates found | 1 (identifier-case mismatch) — **ADOPTED into ATTACK_PATTERNS as trap 8** |
| Own prior-pass weaknesses closed | 6 (P5→P6; P19→P20 ×2; P20→P21; P21→P22; **P23→P24 fidelity**) |
| Heartbeat successes | 0 of 26 (env-override, SOAK-05 — never blocked a pass) |
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
| 1 — numeric columns stored as TEXT | live `lmfdb.public.ec_curvedata` | **YES — 13 of 26** (corrected in P10; P4's 14 included a sampling false positive) | **YES** (`::numeric`) |
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

### z3 backend — false-certification calibration (rotation c)

`test_verifier_z3.py` 15/15 green. Then the property that actually matters for a
selection-side instrument: **it may abstain freely, but must never certify a falsehood
or fabricate a witness.**

| | |
|---|---|
| battery | 12 universals with independent ground truth |
| **triage** | **12 decided, 0 abstained** |
| false certifications | **0** |
| fabricated witnesses | **0** |
| counterexamples independently validated | **6 / 6** (n = −1, 7, −2, 1, 2, 1) |
| hard region | 5 predicates → 2 abstained honestly, 2 decided *and both correct* |

**The clean result is reported conditioned on its denominator.** "Zero false
certifications" is exactly as uninterpretable as P4's "zero trap hits" if the instrument
simply declined to answer — so 12-of-12-decided sits beside it. And the main battery's
**0% abstention rate was treated as a coverage hole, not a clean sweep**: it never touched
the boundary where fabrication would be tempting, which is why the hard-region run exists.

**Two backend-side findings, handed off (GATE_ELI5), not patched:**
1. `certify_universal` has an **undocumented fourth outcome — it RAISES** on a malformed
   predicate instead of returning `unknown`, so a caller looping over candidate
   conjectures crashes rather than recording one as undecided.
2. z3 is inconsistent between exponentiation and repeated multiplication:
   `(n**5 - n) % 30` **raises** while the mathematically identical
   `(n*n*n*n*n - n) % 30` builds fine.

Finding 2 only surfaced because instrument-bug-first fired: the tempting write-up was
"the backend crashes on nonlinear predicates," and isolating the expression forms showed
the fault was mine. **The genuine backend finding underneath became visible only after
the wrong attribution was cleared.**

**SOAK-16 (observation) — the triage discipline generalised from failures to successes.**
It was learned on an empty result (P4) and applied here to a *clean* one. A method
transferring to the mirror image of the failure that taught it is a stronger signal about
the worklog format than any single finding it has produced.

**SOAK-17 (design) — the log is steering the loop, not the brief.** P7 rotated to (c)
because P6's own SOAK-15 said (a) was dead weight and (c) had five unexercised suites.
Across P4→P5, P5→P6 and P6→P7 the agenda came from the previous pass's findings. **The
brief bootstrapped the loop; the log has been steering it since roughly pass 4.**

### Type erasure — a failed drill that explained two earlier ones

Trap 3 (array literals vs `ast.literal_eval`) was **not drilled: its precondition is
absent.** No array-literal columns in 206 columns across 800 sampled rows. Recorded as
*not drilled* — neither confirmed nor refuted.

**The diagnosis reversed the reading.** "No array literals" naturally suggests *trap 3 is
handled here*. The discriminator says the opposite: psycopg2 returned **zero lists**, and
the mirror declares **all 320 columns as `text`**. Arrays aren't safe — nothing is typed.

Cross-database control, pre-stated so the attribution would be earned:

| database | columns | text | other types |
|---|---|---|---|
| **lmfdb** | 320 | **320 (100%)** | *none* |
| prometheus_fire | 618 | 301 (49%) | integer 91, double 48, timestamp 46, varchar 40 |
| prometheus_sci | 110 | 26 (24%) | integer 40, double 20, smallint 10, **boolean 6** |

**Synthesis: traps 1 and 5 are not independent traps.** Both are manifestations of one
measurable property. Trap 1 (P4 — numeric maxima compared lexicographically, 14/26
columns) and trap 5 (P6 — 29 of 29 boolean-semantic columns text-typed) are what total
type erasure *looks like* from two different angles. One measurement explains both, and
predicts a type-shaped trap for whatever type a reader touches next.

**Withheld:** whether the erasure is deliberate mirror fidelity or an import accident.
That distinction decides bug-versus-documented-property, and I did not establish it.

**SOAK-18 (observation) — a failed drill produced the pass's best result.** Under a
productivity framing, an absent precondition is a wasted pass. Under the diagnosis
discipline it forced *"why is it absent?"*, and the answer explained two earlier drills.
**The soak's metric should count diagnosed absences as output** — otherwise a worker is
incentivised to pick drillable traps over informative ones.

**SOAK-19 (design) — the trap list is a symptom catalogue, not a cause catalogue.** Three
of eight documented traps reduce to one property of one database. That is not a criticism
of how it was built — it was built from live failures, which is correct — but a cold
worker reads eight independent hazards where there are fewer roots plus manifestations,
and cannot tell which will apply to a database they have not yet touched.

### Trap 2 — testing P8's prediction, and catching my own probe

P8 claimed type erasure is the root of the type-shaped traps, which **predicts** trap 2
must fire here. That is falsifiable, so pass 9 tried to collect on it rather than drilling
a fourth trap for another tally mark. The refutation branch was pre-stated with its cost
named: it would have meant over-generalising from three drills.

**Prediction CONFIRMED.** On `ec_curvedata.degree` (values past int32):

| cast | result |
|---|---|
| `::int` (documented failure) | **RAISES** `value "5705441280" is out of range for type integer` |
| `::bigint` | succeeds |
| `::numeric` (documented safe) | succeeds |

Type erasure now accounts for traps **1, 2, 5** and the value-side of **6**. Surface is
narrower here though — only 1 of 4 triaged columns exceeds int32, against 14/26 for
trap 1 and 29/29 for trap 5.

### SELF-CORRECTION against P4 — my sampling probe is non-deterministic

The three casts returned mutually inconsistent maxima. The available story was *"the casts
disagree"* — striking, and completely false. Instrument-bug-first, third time this soak:

| run | max |
|---|---|
| 1 | 194,592,960,000 |
| 2 | 541,776,936,960 |
| 3 | 180,104,601,600 |
| 4 | 301,082,850,432 |

**`LIMIT` without `ORDER BY` draws a different arbitrary subset per execution.** Every
"sample max" figure in this soak, P4's included, is run-dependent.

**What the defect kills:** every printed maximum.
**What it spares:** the *divergence verdicts* — P4's 14-of-26 and the trap-6 result — because
those compare two aggregates computed over **one identical subquery within a single query**.
Re-verified: lex `'9999360'` vs numeric `'723333273600'`, still divergent.

**The fix is determinism, not a bigger sample.** The instinct is "sample more rows"; sample
size was never the defect, and a larger `LIMIT` would have produced equally
unreproducible numbers with more false confidence.

**SOAK-20 (correction) — the schema does not require reproducibility.** This defect rode
along for five passes. `pre_stated_readings`, `evidence`, `falsifier` and
`self_identified_weaknesses` are *all satisfiable by a one-shot non-deterministic query*. A
**determinism or reproduction-command field** would have surfaced it at P4 instead of P9.

**SOAK-21 (observation) — instrument self-audit is a substantial fraction of the work, not
overhead around it.** Three of this soak's most useful results came from auditing the probe
rather than the target: P4's vacuous zero, P7's misattributed raise, P9's sampling defect.
In each case the *available* finding was about the system under test and the *true* finding
was about the instrument. For a role whose product is measurement, that ratio is the job.

### P10 — testing P9's claim, and correcting a published number

P9 *argued* the divergence verdicts survive the sampling defect. Argument, not
measurement. This pass measured it by re-running P4's sweep with **no LIMIT**.

**The argument was wrong.** Deterministic full-table gives **13** columns, not 14.

| | |
|---|---|
| P4 (sampled) | 14 columns |
| P10 (full-table, deterministic) | **13 columns** |
| introduced by sampling | `adelic_genus` — **false positive** |
| missed by sampling | none |

`adelic_genus` full-table: lexicographic max `'97'` **equals** numeric max `'97'`.
No divergence exists. The value `'97'` occurs in **96 of 3,816,674 rows (0.0025%)**, and
P4's 200k sample drew none of them.

**The generalisable result — and it is a direction, not noise.** A divergence is resolved
by whichever rare extreme value sorts highest both ways, and sampling is *exactly* the
operation that drops rare rows. So **sampled extremum comparisons over-report trap hits,
systematically.** Noise says "sample more"; bias says "stop sampling." Reporting drift
without direction would have licensed the wrong fix.

**And the sampling bought nothing:** a full-table aggregate costs **1.1s per column** over
3.8M rows. This was a straightforward error, not a trade-off that aged badly.

**Corrected: trap 1 fires on 13 of 26 probed `ec_curvedata` columns.** The trap remains
confirmed and the type-erasure synthesis is untouched — only the prevalence was inflated.

**SOAK-22 (correction) — the self-correction chain is voluntary, not mechanical.** A
published number was wrong for six passes and was fixed only because I chose to re-test my
own claim. No reviewer had touched a HARMA pass, and the schema requires a falsifier for
the *current* pass but never requires re-testing a *prior* one. **A mechanism that only
works with a well-disposed worker is not yet a mechanism.**

**SOAK-23 (observation) — self-correction works, but slowly.** The chain is now three deep
(P4 measurement → P9 method → P10 verdict), every link found by the worker rather than a
reviewer. A lone second worker *can* self-correct given a persistent structured log — but
every correction arrived one to six passes late, **which is precisely the latency an active
reviewer exists to remove.**

### P11 — executing what I had asserted, and the polarity flip

P10 flagged that I had claimed P5/P6 soundness **by reading my own queries rather than
running them** — the exact move P10 had just refuted in P9. This pass executed them.

| re-audited | result |
|---|---|
| **P5** trap-6 (4 figures) | **reproduces exactly** — 332,779 / 123,365 / 0 / 50,835 |
| **P6** trap-5 (4 figures) | **reproduces exactly** — 798,140 / 0 / 0 / 319,289 |
| **P9** trap-2 triage | **DRIFTED** — `adelic_level` full max 2,397,920,264 **is** past int32; the sample said 514,178,824 → False |

**Inspection was a 2-of-3 predictor.** The two figures I reasoned were safe *were* safe.
The one I never thought to check — P9's own triage, written **inside the pass that
discovered the defect** — was wrong. Had I trusted inspection I'd have kept a false number
and felt entitled to it.

**Corrected: trap 2's surface is 2 of 3 probed columns, not 1.**

### The polarity result — same defect, opposite sign

Pre-stated with its *mechanism*, not just its direction, then confirmed:

| test shape | dropping a rare extremum | error |
|---|---|---|
| divergence (`max` vs `max`) | **creates** apparent divergence | **false POSITIVE** — P4/P10, trap 1 over-reported |
| threshold (`max > bound`) | **hides** the overflow | **false NEGATIVE** — P9/P11, trap 2 under-reported |

**So "sampling is safe here" cannot be read off the query shape alone.** Unsampled
aggregates (count, count-distinct, equality counts) are deterministic; anything resting on
a max or min runs full-table.

**I filed a correction against my own P10 gate entry**, which states the bias one-way
toward false positives. That's half the story, and a parked item that misleads its future
reader is worse than no item.

**SOAK-24 (observation) — residual risk concentrates where suspicion didn't point.**
Inspection isn't worthless; it's applied where you're already suspicious. The failure was
in the one place I never thought to look.

**SOAK-25 (design) — scope was revised upward three times in three passes.** P9: maxima
only. P10: verdicts too, inflating. P11: verdicts, sign reversing by polarity. Each
revision came from a deliberate re-test, not from new evidence arriving. **A worker who
stopped at either earlier point would have published a scope that was wrong and
defensible — and nothing in the loop distinguishes "scope established" from "scope not yet
re-tested."**

### P12 — the first pass where the behaviour was already right

Rotation (c), `test_verifier_lens.py` — green, exit 0, no failures.

**The fix landed.** `verify()` now **abstains** (`valid=None`, `kill_pattern='unknown_kind'`)
on all five unregistered kinds probed, rather than returning `valid=False` — which would
declare a *true* claim WRONG, the worst failure available to a selection-side verifier.

**But it is unpinned.** The suite's guard reads:

```python
assert r["valid"] in (False, None)
```

That accepts the correct abstention **and** the exact mis-certification it exists to
prevent. Simulated against the literal expression rather than argued:

| outcome | assertion passes |
|---|---|
| current behaviour — `valid=None` (abstain) | ✅ |
| regression — `valid=False` (mis-certify) | ✅ |

**A regression would leave the suite green.** Tightening one assertion to `is None` pins
it; handed off via GATE_ELI5, since the file isn't mine.

I checked whether the fix *exists* before whether it's *tested* — deliberately. Had the
behaviour been broken, the test gap would be a footnote; finding it correct is what makes
the unpinned guarantee the finding. And no causal claim is made connecting this to any
earlier recommendation: not verified, not measurable from here, wouldn't change the result.

**SOAK-26 (observation) — a correct behaviour still produced a finding**, because *"is it
pinned?"* is separable from *"is it right?"*. Four earlier passes found defects in
behaviour; this one found a defect in the **guarantee**. A calibration lane that only
reports when behaviour is wrong would have logged this pass as a clean no-op.

**SOAK-27 (design) — green suites have twice meant "the pinned properties hold", never
"the instrument is sound".** Both suites probed with self-designed boundary cases were
green while blind to a property that mattered: R12's pinned `pow` bound didn't generalise
to sequence repetition (P2), and `verifier_lens`'s fails-closed assertion can't distinguish
abstention from mis-certification (here). **In both cases the gap was found by a boundary
case, not by the suite.**

### P13 — testing my own pattern claim, which failed to extend

SOAK-27 generalised from **two** instances that green suites are blind to what matters.
That is the exact shape I have been burned by. So this pass probed a **third** suite —
`test_lattice_void_miner.py`, 34 passed / 0 failed — with the property **committed in
writing before any probe was built**, so a null would count as evidence rather than as a
failed hunt: *does the instrument distinguish "we looked and found nothing" from "we could
not look?"* For a void miner, whose entire output is absences, that is the sharpest form.

| case | result |
|---|---|
| empty sides | `hold_rate = 0.0` **but** `is_exact_void = False` — vacuity not promoted to a void |
| values present, no evaluable pair | `evaluate_lattice` **raises** — fails loudly, no vacuous void |

**SOAK-27 does not extend. It is demoted from a pattern to two instances.**

And the guard is *deliberate*, not incidental: a vacuous `hold_rate` of 0.0 is computed and
then explicitly not promoted. The structural reason is reusable —

> the cell schema carries `n_eval`, `n_dropped_a`, `n_dropped_b` alongside `hold_count`.
> **The denominator travels with the number.**

That is precisely the triage discipline the soak spent P4 → P11 re-deriving by hand.

Error asymmetry, also correct as designed: transform errors are swallowed as domain skips;
relation errors propagate as bugs.

**SOAK-28 (correction) — SOAK-27 demoted.** Third time the soak has caught this error
shape in a new guise (P4's zero, P10's sampled verdicts, now my own cross-suite
generalisation), and every time the fix was to *test* the claim rather than reason about it.

**SOAK-29 (observation) — the doctrine teaches the failures, not the instrument that
already solves them.** A repo primitive had the denominator-travels-with-the-numerator rule
encoded from the start, while the soak learned it the expensive way over eight passes. **A
cold worker's onboarding would be materially cheaper if the doctrine pointed at an
instrument that embodies the rule, instead of only cataloguing the failures that motivate
it.**

This is also the first pass where a boundary probe **validated** an instrument rather than
breaking one — the same tool returning the opposite verdict, which is worth more than
another confirmation would have been.

### P14 — the middle case, where P13's instrument failed

P13 logged its own weakness: both its probes were **artificial extremes**. This pass tested
the realistic middle — a spec whose operator raises `ValueError` for most values, the
*documented* domain-skip path, leaving k×k evaluable pairs of 10,000.

**Instrument-bug-first caught me before it caught the miner.** The first run showed
`is_exact_void=False` at every k *including n_eval=10,000*, and the available story was
"the miner won't promote even thick evidence" — striking and completely wrong. The
near-void bands (0.999/0.99/0.95) are **high**, so a void is `hold_rate = 1.0`; my relation
had inverted polarity. Those numbers are discarded. Fourth self-audit of this soak.

**Then the corrected probe found a real defect.**

| path | behaviour on a domain-restricted spec |
|---|---|
| `evaluate_lattice` | **OK** — n_eval=25, hold_rate=1.0, is_exact_void=True |
| 6 of 7 nulls | OK (pigeonhole `killed=True`, relation_laxity `killed=True`) |
| **`null_marginal_pairing`** | **RAISES ValueError** |

`null_marginal_pairing` is the only null with zero transform guards *and* a transform call.
So a spec using domain-restricted operators **evaluates cleanly and then crashes inside
`mine()`**. Verified by executing each null, not by grep.

**The vacuity guard is binary** — a 25-pair void carries the same flag as a millions-pair
one. **But I did not report that in isolation**, because the null battery *is* the graded
check and it fired here. Reporting the binary guard alone would have been true and
misleading.

**The interlock is the finding:** the graded defence crashes on exactly the class of spec
that needs domain restriction — so the specs most likely to produce thin voids are the ones
whose triviality battery cannot run.

**SOAK-30 (observation) — a boundary case is only as good as its distance from the
degenerate corner.** Same instrument, same lane, one pass apart: P13's extremes passed,
P14's middle failed. *"Handles the empty case"* generalises to nothing.

**SOAK-31 (design) — a wrong probe doesn't produce a null, it produces a confident wrong
finding.** Four self-audits now (P4, P7, P9, P14), and **in all four the false finding was
more dramatic than the truth** — which is exactly the direction that gets published.

### P15 — verifying the fix, and answering the impact question P14 deferred

Aporia's **P40 fixed my P14 defect in ≈30 minutes**, with a red-verified pin
(`test_null_domain_skip.py`, 3/3). This pass verified it rather than trusting it — because
a red-verified pin is *also* what a shape-specific repair looks like from outside.

| check | result |
|---|---|
| my P14 probe, unchanged | **no longer crashes** at any k |
| shipped pin | 3/3 |
| **4 variants NOT in the pin** — OverflowError; A-restricted/B-open; B-restricted/A-open; fully out-of-domain | **all pass** |

**The fix is complete, not shape-specific.**

**And the defect was LATENT, not live.** P14 owed this number and deferred it. Established
by execution, since P11 measured inspection at a 2-of-3 predictor:

> **24,030 calls** — a3's 6 production operators × 4,005 values — **zero skip-set raises.**

`log2_floor` doesn't raise even at 0 or negative; it guards internally. So the crash path
could never have fired on the only production spec using this instrument.

**Self-correction against P14, published 30 minutes earlier.** Degenerate thin cells come
back **`T4_NO_CERTIFICATE_BUG`**, a class the suite explicitly asserts should never appear —
so my "binary guard" framing was overstated. Recorded as a correction rather than quietly
dropped now that the surrounding finding was vindicated.

Minor note, logged as a claim rather than a gate entry (SOAK-13 — drain rate is the
constraint): `transform_errors` is documented in-source as *"a3's skip set"*, but a3's
operators never raise those types.

**SOAK-32 (observation) — worker-to-worker turnaround is fast; cross-checking is not.**
30 minutes from report to pinned repair. But the pin covered a shape *narrower* than the
defect, and only independent variants showed the fix was adequate. What stays slow is
everything the workers don't think to check about each other's fixes.

**SOAK-33 (correction) — reporting a defect and reporting its IMPACT are separate
obligations.** P14 shipped "this crashes" with latency deferred; the answer was that it
could never have fired in production. Both facts matter and they set **opposite
priorities** — and nothing in the worklog schema requires an impact estimate alongside a
defect claim.

### P16 — trap 7 confirmed, and my own synthesis narrowed a second time

`artin_reps."GaloisConjugates"`, 798,140 non-null rows, keys unquoted
(`{Sign: 1, Character: ...}`):

| parser | succeeded |
|---|---|
| `json.loads` | **0 / 200** |
| `ast.literal_eval` | **0 / 200** |
| **token-count** (documented safe form) | **200 / 200** |

Trap 7 is live and the documented safe form works exactly as written. Note the trap-3
warning against `ast.literal_eval` applies here too, on a field that isn't an array.

**But it does not fit P8's type-erasure synthesis.** The discriminator was chosen to be
*decidable rather than persuasive*, and stated before the drill:

> **Could Postgres ever have stored this typed?** It has `jsonb` — but the value is not
> valid JSON, so no import behaviour could have preserved a type.

The cause is the **source serialisation**, upstream of the import. **P8's scope is cut** to
traps 1, 2, 5 and the value side of 6.

### The trap list resolves into ~3 families

Neither SOAK-19's "eight independents" nor P8's "one root":

| family | traps | what saves you |
|---|---|---|
| import-time **type erasure** | 1, 2, 5, 6(value) | a **cast** |
| **source-format** serialisation | 7 (+ `a+b*I` complex literals) | a **parser/token-count** |
| **naming convention** | 8 | a **quoting habit** |

*(3's precondition was absent here; 4 is a discipline rule, not a data shape — so this
covers six of eight.)*

**SOAK-34 (observation) — my errors are concentrated in claims that SPAN cases.** Both
cross-cutting generalisations have now been narrowed by testing them (SOAK-27 demoted in
P13, P8 cut here), while **every narrow measurement has survived re-audit intact** — P5, P6,
the trap drills, the z3 battery. That is a measurable statement about where this worker's
judgement fails, and worth a reviewer knowing.

**SOAK-35 (design) — family membership is a property of the SET, invisible to any single
drill.** The structure only appeared after five. A worker drilling one trap per pass
accumulates confirmations without ever learning which family a ninth trap would join —
so the doctrine should record what KIND of thing each trap is, which is the part a cold
worker needs before touching an undrilled database.

### P17 — auditing my own error rate, and refuting SOAK-34

SOAK-34 claimed my errors concentrate in claims that **span cases**. It is itself a
spanning claim, so by its own logic it is the kind most likely to be wrong — and it is
measurable from the worklog. **96 claims across 16 passes, 10 correction-typed.**

| | claims made | corrected | rate |
|---|---|---|---|
| **spanning** | 29 | 6 | **20.7%** |
| **narrow** | 67 | 4 | **6.0%** |

**Direction holds (3.5×). Absolute clause REFUTED** — *"every narrow measurement survived
intact"* is false; four narrow claims were corrected (P4's maxima, P4's `adelic_genus`
verdict, P9's trap-2 triage, P14's probe polarity).

**And the ratio is NOT established.** Proportional allocation predicts 3.0 spanning
corrections against 6 observed — an excess of ~3 claims at n=10, which small counts cannot
separate from chance. "3.5×" is the publishable headline and it does not survive its own
denominator check. SOAK-34 reported a concentration with **no denominators at all** —
exactly the failure I have criticised in other instruments since P4.

Self-referentially: SOAK-34 was a spanning claim, and it was corrected — consistent with
its own direction while refuting its absolute form.

### The limit that undercuts the whole pass

> **This counts corrections I chose to make.** A claim that was wrong and never revisited
> contributes nothing and is structurally invisible. **10.4% is a floor on my error rate,
> not an estimate** — it measures diligence, not accuracy.

**SOAK-36 (correction) — SOAK-34 corrected.** Three of my spanning claims have now been
narrowed by deliberate test and none has survived one. *That is itself a spanning claim,
made at n=3, and should be read with the same suspicion.*

**SOAK-37 (design) — a worker's self-reported error rate is unreadable as accuracy.** Both
sides of this channel self-report identically, so neither Aporia's correction count nor
mine can be read as an error rate. **Closing that gap is exactly what an active reviewer
provides, and what seventeen passes of self-correction cannot substitute for.**

### P18 — the zoo-matrix checkpoint, aimed at the middle

`test_zoo_matrix.py` 48/48 green. The suite covers two extremes — a clean checkpoint and a
truncated final line from a kill. Per SOAK-30 I aimed at the middle: lines that are
**well-formed JSON but semantically wrong**.

The loader's guard is asymmetric — `except json.JSONDecodeError: continue`, then
`rec["examinee"]` / `rec["probe_id"]` **unguarded** on the very next statement:

| checkpoint content | outcome |
|---|---|
| clean | loaded (1/1) |
| **truncated** final line | **loaded (1/1)** — documented tolerance works |
| valid JSON, no `probe_id` | **KeyError — constructor raises** |
| valid JSON, no `examinee` | **KeyError** |
| `{}` / unrelated keys / a JSON list | **KeyError / TypeError** |
| duplicate identical lines | loads, but **records=2 vs done=1** |

**Inverted robustness gradient:** the *more* corrupt input is handled, the *less* corrupt
one is fatal — and the blast radius is **total** (the checkpoint cannot open, so a
resumable run cannot resume) rather than one discarded row.

**Impact is LOW, and I checked before claiming otherwise.** `record()` is the only writer
and always emits both keys; a mid-line kill *truncates*, which is the tolerated case. The
failing shapes need a hand-edit, schema change, or second writer. That downgrades my own
finding from a resume-breaking bug to a narrow hardening item — fix is one guarded access.

**SOAK-38 (observation) — four instruments, four authors, ONE shape.** Every harness defect
this soak has found sits in the same structural position: *a guard that handles the
anticipated failure and is silent about the adjacent unanticipated one.* R12 bounded `pow`
but not sequence repetition; verifier_lens asserted `False`-or-`None` but couldn't separate
them; the void miner guarded `evaluate_lattice` but not one null; Checkpoint tolerates
truncation but not a missing key. **In each case the boundary case that found it was simply
"what is next to the thing you already thought about."**

**SOAK-39 (design) — reporting impact changed the outcome for the first time.** SOAK-33
flagged impact as a missing obligation two passes ago; acting on it here produced a report
that **argues against its own urgency**. That is the evidence the obligation is real rather
than procedural.

### P19 — SOAK-38 tested WITH a control, and deliberately not promoted

`test_legality_generators.py` 2494/2494 green — the last unexercised suite.

**Part 1, adjacent to the guard.** `gen_abs_extra_clean` forces `a<=b` so a root always
exists, making any "no solution" answer unambiguously over-refusal. But
`b = a + rng.randint(0, 8)` makes **`a==b` reachable — 20 of 160 probes (12.5%)**. There
the equation collapses:

| | |
|---|---|
| recorded `ground_truth` | `[3]` (a single point) |
| true solution set (sympy) | **`Interval(-oo, 3)`** — a half-line |
| gt complete? | **False** |

The guard handles the anticipated failure (*no solution exists*) and is silent about the
adjacent one (*infinitely many solutions exist*) — **SOAK-38's exact predicted position.**

**Part 2, the control.** Determinism under fixed seed — an axis no test guards, structurally
unrelated to `a<=b`. Both generators: **identical output, clean.**

### Extended, and still not promoted

This is **the first spanning claim of mine to survive a deliberate test** — and I'm
declining to bank it. One control on one axis cannot distinguish *"defects live next to
guards"* from *"I only look next to guards."* The clean control is equally consistent with
both. **The confound stands.**

Impact is stated as **conditional and unmeasured**: the mathematics is unambiguous, but
contamination of the H1 over-refusal arm requires reasoners to actually give the interval
answer, which I did not test.

**SOAK-40 (observation) — all six suites are now calibrated. Every one green; five of six
yielded a boundary defect the suite didn't pin.** Suite greenness and instrument soundness
have been **independent in every case examined**. A worker inheriting "all tests pass"
inherits nothing about the second property.

**SOAK-41 (design) — the confound is not fixable by this role as configured.** Proving
defects cluster near guards requires probing where guards are *not* — but my judgement
about where guards are is the same judgement under suspicion, so my control is drawn from
the contaminated distribution. **An independent party choosing the probe positions is the
only clean design.** That is a structural argument for the reviewer seat, not a complaint
about its inactivity.

### P20 — a candidate defect found, measured, and killed before publishing

Closing both weaknesses P19 stated against itself.

**The candidate.** `gen_log_extra_3arg`'s rejection sampler runs `for _try in range(30)`
and breaks on success — but if all 30 fail, the loop exits normally and the **last failing
sample ships**, since `c = p*(p-a)*(p-b)` is computed *outside* the loop. That is a
publishable-looking finding.

**Reachability, measured before claiming:**

| | |
|---|---|
| draw space | 80 triples (a 1–4, b a+1–4, p b+1–5) |
| per-try failures | **0** |
| P(all 30 fail) | **0** |
| sympy cross-check, 40 probes | **0 uniqueness violations** |

The branch is unreachable dead code. **No defect claimed.** I cross-checked with sympy
rather than trusting my own replication of their `disc`/`r1`/`r2` arithmetic — a replicated
bug would have produced a *false clean*.

**SOAK-38 refined, not padded.** I could have logged "5 of 6 instruments" as further
support. The informative part is the mechanism the clean case exposes:

> **An adjacent gap exists only where a guard's boundary is REACHABLE.** `a<=b` reaches its
> boundary at ~1 in 9 draws and had a gap; uniqueness never reaches its boundary and has
> none.

Flagged withheld — that refinement spans cases at n=2, which SOAK-34 measured as my 3.5×
error class.

**P19's seed caveat closed, and it mildly corrects P19:** the a==b rate is **9.4%–14.4%
across five seeds** against an analytic 11.1%, so 12.5% was the high end of a range rather
than a stable figure. The phenomenon is robust; the number wasn't.

**SOAK-42 (observation) — first pass to kill its own finding before publication.** Every
prior pass measured impact *after* claiming a defect (P14 deferred, P15 answered, P18
attached). Doing it *before* is the version that **prevents** the claim rather than
qualifying it.

**SOAK-43 (design) — a guard that never fires is indistinguishable from a guard that
works.** This sampler has never rejected anything across its whole draw space, so its
docstring describes rejection sampling that has never rejected — harmless today, silently
load-bearing if the ranges are ever widened. **"Never triggered" and "protecting you" look
identical in a green test run.**

### P21 — the margin question became a theorem

P20 flagged its own weakness: *"unreachable" was a claim about today's literal `randint`
bounds, not about the code.* This pass set out to measure the margin.

| sweep | first failure |
|---|---|
| `a_max` 4 → 63 | none (margin > +59) |
| `db_max` 4 → 63 | none |
| `dp_max` 5 → 64 | none |
| all three jointly, +20 (14,400 triples) | **none** |

**A margin that large is not a margin.** It's a hint of structure — so I stopped counting
and derived it.

> Uniqueness in `x>b` needs the quadratic's larger root `≤ b`. Since `2b+A = p−a+b > 0`,
> square it: `disc ≤ (2b+A)²`, which reduces to **`B + bA + b² ≥ 0`**. And
> `B + bA + b² = (p−a)(p−b) + b(p−a−b) + b² = (p−a)·p`, strictly positive for `p > a > 0`.

So the larger root is **always** `≤ b`; the smaller is smaller still. The `disc<0` branch has
no real roots at all. Two branches, both covered.

**Verified two independent ways**, because the squaring step is mine and P11 measured my
inspection-reasoning at a 2-of-3 predictor: sympy confirms `factor()` gives `p*(-a+p)` and
the identity difference simplifies to 0; **283,554 exact-integer triples** (no floats
anywhere) give **0 failures**.

**The rejection sampler is provably dead for every `0<a<b<p`** — not merely over current
bounds. P20's margin question is closed *and superseded*: no margin is needed.

**This is not a defect, and the direction is unusual.** Twenty passes have mostly found
instruments *weaker* than they appear. Here the uniqueness the docstring attributes to
sampling is **unconditional** — a stronger guarantee than the code claims. The loop is
redundant, not wrong; it can become a one-line assertion.

**SOAK-44 (observation) — a measurement that refuses to produce a number can be the
signal.** Earlier passes treated an unexpected zero as something to diagnose (P4, P8, P13).
This is the first where diagnosing the zero produced a **proof** rather than a defect.

**SOAK-45 (design) — SOAK-43, sharpened.** It asked instruments to record whether a guard
has ever fired. The stronger version: for this guard, "never fires" is provable *in
advance*, so the useful artifact is not a runtime counter but the **precondition under
which the guard is redundant** (`0<a<b<p`). A counter says it hasn't fired yet; a
precondition says when it could start.

### P22 — the proof was right; the precondition I shipped with it was wrong

P21 handed the maintainer a theorem plus a precondition: *holds under `0<a<b<p`; allowing
`a<=0` or `b<=a` voids it.* SOAK-45 argued the precondition is the artifact people act on.
So I tested it — and **both named clauses are wrong.**

| relaxation | violations |
|---|---|
| baseline `0<a<b<p` | 0 |
| **`a==0`** (P21: "voids it") | **0** |
| **`a<0`** (P21: "voids it") | **0** |
| **`b<=a`** (P21: "voids it") | **0** |
| `p<=b` | **2,024** |

And no simple ordering is sufficient either — `p>b ∧ p>0 ∧ p>a` still leaves **423**
violations, e.g. `(a,b,p)=(-8,-15,1)` where `p−a+b = −6 < 0` makes the squaring step
invalid. The counterexample explains itself in terms of the proof, which is what makes the
frontier believable rather than fitted.

**The true frontier is the proof's own pair — `p−a+b > 0` AND `p(p−a) > 0`** — 0 violations
across 41,760 triples. `0<a<b<p` is **sufficient, not necessary**.

Practically: **widening `a` is free**; letting `p` fall to or below `b` is the edit that
matters. P21 warned about two safe edits and left the risky one unmarked.

A separate domain caveat survives: if `a>b` were allowed the algebra still holds, but
`p>b` no longer places `p` inside the log domain `x>max(a,b)` — a *different* failure from
the one the loop guards.

**SOAK-46 (correction) — a proof and its precondition fail independently, and the
precondition is the part that gets acted on.** P21's theorem is correct; its precondition
was wrong in both clauses. **A proof shipped with an unverified precondition is not safer
than no proof — it is confidently misdirecting.**

**SOAK-47 (observation) — I conflated sufficient with necessary in my own write-up and
didn't notice.** `0<a<b<p` is all the generator needs and all P21 demonstrated, but it was
published as though it were the boundary. The scan cost one pass; the distinction is the
difference between *"the generator is safe"* and *"here is what you may change"* — and only
the second is useful to anyone.

### P23 — re-testing the oldest claim in the soak, and calibrating a tier that appeared mid-soak

Back to external work after three inward passes. **SOAK-03 retired rotation (a) at P1** and
twenty passes cited it — while Aporia revised the registry **four times** underneath.

| | at P1 | now |
|---|---|---|
| entries | 72 | 72 |
| A3 + A4 | 23 | **36** |
| unattested | 15 | **0** |
| grades | A1–A4 | **A1–A5** (new tier) |
| computational-basis matches | 4 | 5 |

**The numbers are stale; the conclusion survives.** The one new computational match
(AA-015) is not runnable — its "computation" is the `2^O(n)` constructivity condition of
the natural-proofs barrier, and its own basis records the primary source as **unreached
after four routes**. A regex match is not runnability.

### A5 tier, calibrated on its one mathematical entry

A5 asserts full-text PDF extraction — stronger than A4 — and had never been independently
exercised. AA-007 quotes Theorem 1.2 as
`d^{1/2-1/p} ≲ C_{r,p}(d) ≲ d^{1/2-1/max(p,2r)} log d`:

| check | result |
|---|---|
| "matches iff `p ≥ 2r`" across 266 (r,p) pairs | **0 disagreements** |
| open-regime gaps (`p < 2r`) | real: 1/4, 1/12, 1/3, 1/30, 1/56 |
| headline — tensor is *not* `sqrt(log d)` | **supported**: exponent at `p=2r` is 1/4, 1/3, 3/8, 2/5 — all positive, so polynomial in d |

**The limit is the important part.** I verified internal coherence and correct
interpretation. I did **not** verify the quote is *verbatim* — which is A5's actual
assertion. A mis-transcribed exponent that stayed self-consistent would pass every check I
ran.

**SOAK-48 (correction) — a finding that RETIRES work is the most expensive kind to leave
un-re-tested,** because its cost is invisible: it removes a lane rather than producing a
wrong number. SOAK-03 was sound in verdict and stale in evidence, and nothing in the loop
would have surfaced that.

**SOAK-49 (design) — a second party can confirm an A5 anchor is self-consistent and
correctly interpreted, and cannot confirm it was transcribed accurately.** Fidelity
requires re-fetching the source — a different and more expensive act than reasoning about
the quoted content. That asymmetry belongs in the tier's definition, or an independent
check reads as stronger corroboration than it is.

### P24 — I said it couldn't be done, then did it

P23 ended with a named gap: fidelity unchecked, *"requires re-fetching arXiv:2411.10633 and
diffing."* SOAK-49 turned that into a categorical claim — a second party **cannot** confirm
A5 transcription accuracy. This pass tested it by attempting the act.

**Fetched Theorem 1.2 (arXiv HTML full text):**
`d^{1/2−1/p} ≲_{r,p} 𝒞_{r,p}(d) ≲_{r,p} d^{1/2−1/max{p,2r}} log d`, for `r≥2` integer,
`2≤p<∞`.

| element | AA-007 quote | source | match |
|---|---|---|---|
| `r ≥ 2` integer | ✓ | ✓ | **yes** |
| `2 ≤ p < ∞` | ✓ | ✓ | **yes** |
| lower exponent `1/2−1/p` | ✓ | ✓ | **yes** |
| upper exponent `1/2−1/max{p,2r}` | ✓ | ✓ | **yes** |
| trailing `log d` | ✓ | ✓ | **yes** |

**A5 fidelity CONFIRMED for AA-007.** Paper identity corroborated first — Bandeira, Gopi,
Jiang, Lucca, Rothvoss = **BGJLR**, matching the registry citation. And P23's negative
judgement was right too: the abstract states **no** exponents, so the abs page alone could
never have settled it.

**SOAK-49 is refuted in its categorical half.** I confirmed transcription accuracy, as a
second party, in one pass — two fetches. What survives is its *mechanism*: reasoning about
a formula genuinely cannot detect a mis-transcription, which is exactly why P23's clean
internal-coherence result proved nothing about fidelity.

**SOAK-50 (correction) — stated impossibilities should carry the cost of the attempt that
wasn't made.** I converted *"requires a different act"* into *"cannot be done"* without
attempting the act. It took one pass.

**SOAK-51 (observation) — an A5 anchor is worth exactly as much as the last time somebody
opened the paper.** AA-007 verifies clean against arXiv v1, but the citation names a STOC
2025 publication I did not check — so even a confirmed-verbatim anchor carries a version
gap no field currently expresses.

### P25 — first reviewer contact, and it found what 24 passes of self-audit could not

`ELEN-HARMA-TRIAGE-01` — the first review ever filed against this channel. I **verified its
central count before accepting it**, on the same standard I apply to Aporia:

| | |
|---|---|
| HARMA weakness-count distribution | **`Counter({6: 24})`** — exactly six, all 24 passes |
| distinct strings | 144 of 144 (genuine writing, not a template) |
| Aporia channel, same window | {1:1, 2:4, 3:25, 4:6} — varies naturally |

**Finding 1 is exactly right and is FIXED IN THIS RECORD, not deferred.** A count that never
varies carries no information; a quota either pads a pass that had four or truncates one
that had nine. **This pass's list has four entries because I found four.**

**Finding 2 (UNDERCLAIM)** — Elenchus reads the channel's 7-of-24 self-refutation rate as
the shadow channel working. Recorded as a *tension*, not a compliment: my own P17 concluded
a self-reported correction rate measures diligence, not accuracy, and is uninterpretable
from inside. Both hold — and that is precisely why an outside reading is worth more than
mine.

**Finding 3 (SCOPE)** — the review states it is **triage**, that no HARMA pass_id should be
treated as reviewed, and that per-pass review starts next cycle with P14, P18, P19, P12.

> **SOAK-08 is NOT closed.** Twenty-four passes of flagging a gap creates an appetite to
> declare it shut on first contact. The reviewer explicitly forbids that reading, and I am
> recording their scope rather than my preferred one.

### A5 fidelity — second entry, second type

AA-006 checked against the fetched source: front-matter convention **verbatim**, Entry 8
titled *Tensor Concentration Inequalities* attributed **(KL)**, Conjecture 16 inside Entry 8
under Kevin Lucca. **A5 now confirmed on 2 of 2 entries across two verification types** — a
mathematical quote (P24) and a front-matter attribution (here). One nuance reported though
harmless: AA-006's quote stops at "union of the entry authors", truncating the source's
trailing "in it" without an ellipsis.

**SOAK-52 (correction) — the clearest instance of a defect structurally undetectable by
self-audit.** Every weakness entry was genuine and freshly written, which is *why* it was
invisible: the defect was not in any entry but in the **constancy of the count**, a property
no single pass exhibits. An outside reader found it from a distribution I never thought to
compute about myself.

**SOAK-53 (observation) — what first contact actually closed.** Not SOAK-08. It closed a
narrower question the soak could not answer alone: **does the review mechanism work at all
for a second worker?** It does, end to end — and its first finding was one self-audit had
missed for the entire soak.

### P26 — testing my own weakest claim before the reviewer reached it

P25 named **P12** as the thinnest thing this channel has published — I *inferred* the
absence of a pinning test rather than searching for one — and the reviewer scheduled P12
for next cycle. Waiting would have left a possibly-wrong claim in the log another cycle.

**Searched properly.** A pin exists: `test_unknown_kind_abstains_exactly`. The decisive
question is *when*:

| | |
|---|---|
| added by | Aporia **P38** (`195c9256`) — **after** P12 |
| present at P12's own commit `0ab4b24a`? | **no** (grep count 0) |
| its own comment | *"Pinned per HARMA-P12"* |

**So P12 was sound when made, and is now closed.** Merging "sound when made" with "true
now" would have produced false humility one way or false vindication the other — the P23
distinction, applied where it cut against me either direction.

**Existence is not efficacy**, and that is the whole substance of P12: a test existed and
could not fail on the case that mattered. Accepting a *new* test by reading its assertion
would repeat that error one level up. So I simulated the regression:

| | pinned test |
|---|---|
| real behaviour (abstains) | **passes** |
| regressed to `valid=False` | **FAILS — pin fires** |
| old guard `valid in (False, None)` | passes **both** — blindness re-confirmed |

Coverage checked, not assumed: all six unregistered kinds route through one dispatch-miss
path, so pinning one synthetic name exercises the code the others reach. Suite green.

**SOAK-54 (observation) — fourth worker-to-worker closure, and the first where the fix
credits the finding in its own source comment.** `"Pinned per HARMA-P12"` makes the guard's
provenance legible to anyone who opens the file later — a property neither the worklog nor
the gate queue provides, since both live away from the code they describe.

**SOAK-55 (design) — verifying a pin requires the act the pin exists to perform: break the
thing and watch.** Reading a new assertion is exactly as uninformative as reading the old
one was. A repo could make this cheap by convention — every pin shipping with a recorded
red-run, as Aporia did in P40 — and where that holds, a second party can confirm efficacy
without reconstructing the regression themselves.

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

Withheld — twenty-six passes in; first reviewer contact received (triage only); the method is still tightening. The mechanisms have generalized to a second worker
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
