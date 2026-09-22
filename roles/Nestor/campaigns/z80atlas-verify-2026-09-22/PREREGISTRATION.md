# Z80 x Atlas VERIFICATION campaign - 24 hours - PREREGISTRATION

Status: **DRAFT, NOT FROZEN, NOT LAUNCHED.** Awaiting operator review of this document
and of the repair tests it names. No grammar hash is committed here yet; the hash line is
written only at freeze, and `run_campaign.py` refuses to start without it.

Predecessor: `z80atlas-2026-09-19`, 23,471 runs, closed 2026-09-22, packet and
adjudication frozen. That evidence is **not modified by this campaign**. This is a
separate campaign directory with its own observatory.

---

## 0. Why this campaign exists

The 72-hour campaign produced three results that cannot be closed from its own record,
and one that contradicts prior work. Each becomes a preregistered hypothesis below.

| # | Question the 72-hour run raised | Why it cannot be closed from that record |
|---|---|---|
| H1 | Read order: answer-before-read beat forced read, opposite to CW01 cycle 8 | Two campaigns, two endpoints, two substrates. Neither is wrong yet; they are not comparable as run. |
| H2 | 1,031 evidence-backed replication events, but 911 are ancestry depth 1 | Depth was never a measured endpoint. Nothing selected for or tested propagation. |
| H3 | 124 reservoir flags, all inadmissible | The lineage record keeps a 400-event tail and logs no migration events, so the easy-niche ancestry certificate cannot be built. |
| H4 | One admissible endogenous-only instance, n=1 | A single run at margin 1.0 is an anecdote until it repeats under fresh seeds. |

---

## 1. Repairs required before freeze

These are substrate and instrument changes. Each is a **defect fix in the measurement
apparatus**, made before any data is collected, never during. Each has a test that must
fail on the unrepaired code and pass on the repaired code; the calibration gate runs all
of them and refuses to launch on any failure.

### P-1 Lineage must support an ancestry certificate (closes H3)

Current: `run_cell()` returns `lineage[-400:]`; the observatory thins to `[-50:]` under
disk pressure. Each record is `(child, parent, epoch, niche, fidelity, span)` where
`niche` is the **parent's niche at the moment of birth**. Migrations increment a counter
and are never logged as events.

Required:
- Log a migration event `(oid, from_niche, to_niche, epoch)` into the lineage stream.
- Retain the **full** parent map for any run whose structure is `RESERVOIR`, independent
  of the tail budget. The tail may continue to thin for other runs.
- Record, per run, whether the lineage stream is complete or truncated, as a boolean the
  adjudicator reads. A truncated stream must make an ancestry claim **inadmissible by
  construction**, not silently weaker.

Test `T-P1`: construct a world where a known organism is born in niche 0, migrates to
niche 2, and reproduces there. The reconstructed certificate must name niche 0 as the
birth niche and niche 2 as the crossing niche. On the unrepaired code the certificate
cannot be built at all; the test must fail there.

### P-2 Ancestry depth becomes a first-class measured endpoint (closes H2)

Current: depth is recoverable only by post-hoc reconstruction, and only because the
admissible set happened to be small enough to escape truncation.

Required: `summary` carries `max_ancestry_depth`, `n_lineages_depth_ge_2`, and
`n_lineages_depth_ge_5`, computed in-run from the full parent map, plus
`propagating_replicators` = the count of distinct organisms that both replicated with
evidence AND have at least one descendant that also replicated with evidence.

Test `T-P2`: a seeded star replicator (one parent, many children, no grandchildren) must
report `max_ancestry_depth == 1` and `propagating_replicators == 0`. A seeded chain
replicator must report depth equal to the chain length. Both are positive controls; the
star case is the negative control that the 72-hour campaign lacked.

### P-3 Separate the historical event from the final state (closes Z80A-D01)

Current: `crossed` is historical, `held_max` is final-state, and the flags mix them.

Required: `summary` carries `crossed_ever`, `crossed_at_final`, `held_max_final`, and
`held_max_ever` as four distinct fields. Every flag declares which pair it fires on. No
flag may report one as evidence for the other.

Test `T-P3`: a run whose best lineage crosses and is then reaped must report
`crossed_ever=True, crossed_at_final=False`, and any flag naming a final-state claim must
not fire on it.

### P-4 Reservoir flag must check the reservoir contributed (closes Z80A-D02)

Required: `RESERVOIR_CROSSED_A_MOAT` fires only when the crossing lineage's certificate
shows an ancestor resident in the easy niche, a migration event out of it, and the
crossing in a hard niche. Seeded-instrument populations are excluded at the flag, not at
adjudication.

Test `T-P4`: the flag must not fire on a run where all four niches are occupied uniformly
and no migration precedes the crossing. On the 72-hour code this run fires the flag; that
is the defect.

### P-5 Index carries the replication evidence (closes Z80A-D03)

Required: add `replication_events`, `births_similar_no_write`, `max_ancestry_depth`, and
`lineage_complete` to the index whitelist. This is a schema change and is therefore made
**now, before freeze**, never mid-campaign.

Test `T-P5`: an index row round-trips every field the adjudicator reads; the adjudicator
run against the index alone must reach the same verdicts as against the per-run records.

### P-6 Report integrity (already built, carried forward)

`report_audit.py` and `test_report_audit.py` from the predecessor campaign apply
unchanged in principle: any human-readable report of this campaign declares its claims in
a machine-readable block, every named admissible instance cites the adjudication record,
and the negative control proves each check can fire. **A report that does not pass its own
audit is not published.**

---

## 2. Preregistered hypotheses and decision rules

Thresholds below are frozen at review. They are not adjusted after any result is seen.

### H1 - Read order, and the cycle-8 discrepancy

The 72-hour campaign measured *final held-out competence*. Cycle 8 measured *crossing a
specific successor world*. These are different endpoints, so the contradiction may be
apparent. Three candidate explanations, separated by design rather than argument:

- **E1 endpoint.** The effect reverses when scored on crossing rather than final
  competence.
- **E2 execution cost.** Forcing the read costs instructions and time in a byte VM; the
  effect reverses or vanishes when the read is made free (pre-loaded into a register by
  the world rather than executed by the organism).
- **E3 non-exchangeable arms.** `moat` is derived from `read_order` AND `bridge`, so the
  two arms differ in more than read order once the derived tag is used. The effect changes
  when `bridge` is held fixed within pair.

Design: a 2 x 2 x 2 factorial over {read_order} x {endpoint: crossing, final} x {read
cost: executed, free}, with `bridge` held fixed within every matched pair. Minimum 120
matched pairs per cell.

**Decision rule.** H1 is resolved in favour of a given explanation if that factor's
interaction with read_order exceeds 0.15 in mean effect AND the sign of the read_order
effect differs between its levels. If no interaction reaches 0.15, the discrepancy is
recorded as **unexplained** and the cycle-8 claim is downgraded to *world-specific*. No
outcome here promotes anything; this hypothesis exists to remove a contradiction, and
"both measurements stand and describe different things" is an admissible answer.

### H2 - Propagation, and the reimplantation assay

The predecessor establishes replication *events*. It does not establish lineages.

Design, three arms per cell:
- **A. in situ.** Measure `max_ancestry_depth` and `propagating_replicators` directly.
- **B. reimplantation.** Take the first evidence-backed replicator, place it alone into a
  fresh world of the same cell with an otherwise random population, and run to budget.
  Measure whether its lineage reaches depth >= 5.
- **C. matched null.** Identical to B, but the implanted genome is a length-matched
  random byte string. This is the control that the 72-hour campaign never had, and it is
  what separates "this genome propagates" from "this world produces depth".

**Decision rule.** A cell supports *self-sustaining replication* only if arm B reaches
depth >= 5 in at least 3 of 5 seeds AND arm C reaches depth >= 5 in at most 1 of 5. Any
other pattern is reported as *replication events without propagation*, which is the
predecessor's actual result and remains the default conclusion.

### H3 - Reservoir stepping stones

Only answerable with P-1 in place. Design: `RESERVOIR` structure, moat task, endogenous
reproduction, random seeding, minimum 200 runs.

**Decision rule.** The reservoir claim is supported only by a complete certificate: an
ancestor resident in the easy niche, a logged migration, and a crossing in a hard niche,
on a run with `lineage_complete = True`. Certificates are counted, not rates. Fewer than
5 certificates is reported as **not demonstrated**, and a truncated lineage is
inadmissible rather than weak.

### H4 - The endogenous-only instance

Design: the cell of `64dea50f417efb02-s1203-tL-a0` exactly, plus its matched external
control, at 16 fresh seeds each. The cell is a graph world, coevolving environment,
`ENDOGENOUS_PARTIAL`, block copy, periodic-migration niches, forced read order.

**Decision rule.** The instance is confirmed if the endogenous arm reaches final held-out
>= 0.90 in at least 6 of 16 seeds AND the external arm reaches it in at most 1. Between
those, it is *seed-dependent*. Below, it is **retracted as an anecdote**, and the report
says so in those words.

---

## 3. Budget and shape

| item | value |
|---|---|
| wall clock | 24 h, single deadline, drain at the end |
| workers | 6 |
| stages | none - this is a verification campaign, not a search |
| allocation | H1 40%, H2 30%, H3 20%, H4 10% |
| producer | **none**. Cells are enumerated from the four designs above. No UCB, no exploration floor, no promotion. |
| grammar | inherited, hash-gated; the four designs pin most factors, so the space is small and fully enumerable |

The absence of a producer is deliberate. The predecessor searched; this campaign tests
named hypotheses with preregistered rules. Adding a bandit would reintroduce the
allocation feedback that makes descriptive counts uninterpretable.

---

## 4. What would make this campaign fail honestly

Recorded now so the outcome cannot be reframed later:

- H1 unexplained: all three interactions below 0.15. The discrepancy stands and cycle 8's
  forced-read advantage is world-specific.
- H2 negative: arm B never separates from arm C. Then the predecessor's 1,031 admissible
  events are single replication events in worlds that do not sustain lineages, and the
  spontaneous-replication result is smaller than it first read.
- H3 empty: zero certificates. The reservoir hypothesis has no support in this substrate.
- H4 retracted: the single instance does not reproduce. One anecdote removed.

All four negatives are publishable and none triggers a follow-up campaign by default.
"Not worth continuing" remains a first-class answer.

---

## 5. Gate before launch

1. Operator review of this document. **Not yet given.**
2. Operator review of repair tests T-P1 through T-P5, plus the carried-forward
   `test_report_audit.py`. **Tests not yet written; P-6 is the only repair already built
   and passing.**
3. Calibration gate: all repair tests pass, plus the predecessor's 10 controls.
4. Freeze: grammar hash written into this file, `CALIBRATION.json` records PASS for that
   hash, `run_campaign.py` refuses to start otherwise.

Until every step is complete this campaign does not launch.
