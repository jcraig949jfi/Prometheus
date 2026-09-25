# Z80 x Atlas VERIFICATION campaign - 24 hours - PREREGISTRATION

Status: **DRAFT rev B. NOT FROZEN. NOT LAUNCHED.** No grammar hash, no protocol hash and
no manifest hash is written as final here; the proposed values live in the review packet
and are written into this file only at freeze, by the operator's instruction.

Predecessor: `z80atlas-2026-09-19`, 23,471 runs, closed 2026-09-22. **That evidence is
frozen and is not read-modify-written by anything in this campaign.** This directory
carries its own copy of the substrate; the predecessor's files are untouched.

---

## Amendment log

Rev B incorporates operator review of rev A. Rev A's text is superseded, not deleted:
each change is recorded here so the diff is auditable.

| # | Rev A said | Rev B says | Why |
|---|---|---|---|
| A-1 | P-1 certificate = easy niche ancestry | Certificate must distinguish **born easy -> migrated -> carrying lineage in hard -> crossing in hard**, and record the crossing niche | Rev A's certificate could be satisfied by an organism that never left the easy niche |
| A-2 | P-2 measured genealogy depth | Adds **causal replication depth**: an edge counts only if the parent met the evidence-backed endogenous criterion. H2's depth>=5 rule now uses causal depth | Ordinary descent inflates depth without any copying having occurred |
| A-3 | H1 framed as "cycle 8 showed forced read wins" | **Withdrawn.** Cycle 8 established the answer-before-read obstruction; its successor worlds did not cross, and forcing the ask read was a proposed continuation, never a result | Rev A misattributed a proposal as a finding |
| A-4 | H1 was 2x2x2 over read_order x endpoint x cost | **Replaced** by a 2x2 over output gate x cue-consumption cost, on a single fixed task | `FORCED_READ` is not a read-order change: `episodes()` sets `base = v XOR key` and passes a 3-element input vector, so it changes target and input construction. The rev A design was confounded |
| A-5 | H1 endpoints were an experimental factor | Endpoints are **readouts** of one run | `crossed_ever`, `crossed_at_final` and held-out competence are three measurements of the same organism, not three arms |
| A-6 | H1 explanation E3 blamed the derived moat tag | **Removed** | The matched-pair audit showed all 10,741 pairs are Hamming-1 on the declared axis; a derived label does not alter dynamics |
| A-7 | H2 "three arms per cell" | **Fixed 16-specimen panel** chosen algorithmically from the frozen predecessor record, committed to a manifest before any Cycle-9 result | 1,031 admissible runs over 35 strata is not a bounded experiment |
| A-8 | H3 "minimum 200 RESERVOIR runs" | **Three-arm shared-seed bundles** on frozen cells: easy+migration, homogeneous+migration, easy+no-migration | Certificate counts alone cannot show the easy niche *caused* accessibility |
| A-9 | H4 16 seeds, one block | **Four blocks** (historical, RANDOM seeding, STATIC env, topology comparator), 16 seed-pairs each | Separates reproducibility from scaffold, coevolution and migration dependence |
| A-10 | allocation by percentage | **Fixed machine-readable job manifest**, hashed, enumerating every run | Percentages permit result-dependent invention of work |
| A-11 | - | **New P-7** verification bundle integrity, a launch blocker | Family-level mutable control state cannot survive restart or completion reordering |
| A-12 | - | **New P-8** deterministic multi-niche initialization | Predecessor places the entire initial population in niche 0 |
| A-13 | - | **New P-9** explicit environment x structure composition | `COEVO_ENV` silently bypasses the reservoir's niche-0 modification |
| A-14 | - | **New P-10** ENV_MIG semantic validity | Its gate is `env_difficulty(niche) < 0.5`, and that function returns 1.0 for every structure except RESERVOIR, so under ENV_MIG the gate never fires |

---

## 0. Why this campaign exists

Four questions the 72-hour campaign raised and cannot close from its own record.

| # | Question | Why the predecessor cannot close it |
|---|---|---|
| H1 | Does requiring the cue to be consumed before answering change accessibility? | The predecessor's `read_order` factor changes the task itself, so its two arms are not the same experiment measured twice |
| H2 | Do evidence-backed replication events become self-sustaining lineages? | Ancestry depth was never an endpoint. Reconstruction shows depth 1 in 911 of 1,031 admissible runs |
| H3 | Does an easy niche act as a genetic reservoir? | The lineage record keeps a 400-event tail, logs no migration, and stores only the parent's niche at birth |
| H4 | Is the single admissible endogenous-only instance real? | n = 1 |

---

## 1. Repairs required before freeze

Every repair is a change to the **measurement apparatus**, made before any Cycle-9 data
exists. Each has a test that must **fail on the unrepaired code** and pass on the
repaired code. The calibration gate runs all of them and refuses to launch on any
failure.

### P-1 Ancestry certificate (H3)

Unrepaired: `run_cell()` returns `lineage[-400:]`, thinned to `[-50:]` under disk
pressure. Records are `(child, parent, epoch, niche, fidelity, span)` where `niche` is the
**parent's** niche at the birth instant. Migration increments a counter and is never
logged.

Repaired:
- Migration logged as an event `(oid, from_niche, to_niche, epoch)` in the lineage stream.
- Full parent map retained for any `RESERVOIR` run regardless of tail budget.
- `lineage_complete` recorded per run.
- **A truncated lineage can never support a causal ancestry claim.** The adjudicator
  treats it as inadmissible by construction, not as weaker evidence.

The certificate must establish, in order, that the lineage was **born in the easy niche**,
**migrated out of it**, **carried through to a descendant resident in a hard niche**, and
**crossed in that hard niche**. The crossing niche is recorded explicitly.

**T-P1** builds a world where a known organism is born in niche 0, migrates to niche 2 and
reproduces there. The certificate must name niche 0 as birth and niche 2 as crossing. On
the unrepaired code no certificate can be built at all.

### P-2 Causal replication depth (H2)

Unrepaired: depth is recoverable only by post-hoc reconstruction, and every birth is a
lineage edge regardless of whether copying occurred.

Repaired, added to `summary`:

| field | meaning |
|---|---|
| `max_ancestry_depth` | longest chain of any parent-child edges |
| `n_lineages_depth_ge_2`, `n_lineages_depth_ge_5` | genealogy counts |
| `max_causal_replication_depth` | longest chain using **only** edges where the parent met the evidence-backed endogenous replication criterion |
| `n_causal_lineages_depth_ge_2`, `n_causal_lineages_depth_ge_5` | causal counts |
| `propagating_replicators` | organisms that replicated with evidence **and** have a descendant that also replicated with evidence |

**T-P2**, three fixtures:

- **A star.** One parent, many children, no child replicates. Requires
  `max_ancestry_depth == 1`, `max_causal_replication_depth == 1`,
  `propagating_replicators == 0`.
- **B ordinary descent.** A chain of births without evidence-backed replication. Requires
  `max_ancestry_depth > 1` **and** `max_causal_replication_depth` does **not** increase.
- **C causal chain.** An evidence-backed replication chain. Requires
  `max_causal_replication_depth` to equal the constructed chain length.

H2's depth >= 5 criterion uses `max_causal_replication_depth`.

### P-3 Historical and final-state outcomes kept separate

Repaired: `summary` carries `crossed_ever`, `crossed_at_final`, `held_max_ever`,
`held_max_final` as four distinct fields. Every flag declares which pair it fires on, and
no flag reports one as evidence for the other. The separation is preserved through INDEX,
adjudication and report generation.

**T-P3** forces `crossed_ever=True`, `crossed_at_final=False`, `held_max_ever >= threshold`,
`held_max_final < threshold` and proves no final-state claim fires.

### P-4 Reservoir flag requires the certificate

Repaired: `RESERVOIR_CROSSED_A_MOAT` fires only on a complete P-1 certificate.
Seeded-instrument populations are excluded **at the flag**, not at adjudication.

**T-P4**: the flag must not fire where all niches are uniformly occupied and no migration
precedes the crossing. The unrepaired code fires on exactly that run.

A reservoir flag is **necessary, not sufficient**. H3 supplies the causal controls.

### P-5 INDEX sufficient for adjudication

Repaired: `replication_events`, `births_similar_no_write`, `max_causal_replication_depth`,
`lineage_complete`, and the four P-3 fields join the index whitelist.

**T-P5** adjudicates a fixture set covering **every** special-result class twice, once from
INDEX alone and once from the per-run records, and requires exact verdict equality. No
silent fallback to per-run files is permitted.

### P-6 Report integrity (carried forward, mandatory)

`report_audit.py` and `test_report_audit.py` run as part of the launch gate. Any Cycle-9
report declares its claims machine-readably, cites the adjudication record for every named
instance, and does not publish without passing its own audit.

### P-7 Verification bundle integrity — LAUNCH BLOCKER

The campaign must not use family-level mutable control state. Adjudication operates on
immutable **bundles** carrying at minimum: `bundle_id`, `hypothesis_id`, `pair_seed`, the
treatment run, required control run(s), intervention run(s), declared factor deltas,
expected cardinality, and a protocol hash. **A bundle adjudicates only when complete.**

**T-P7** runs the same bundle under four executions:

1. treatment completes before control;
2. control completes before treatment;
3. killed after treatment, before control, then resumed;
4. killed after control, before treatment, then resumed.

All four must produce **byte-equivalent** bundle contents and identical verdicts, modulo
timestamps and path metadata explicitly named in an exclusion list.

### P-8 Deterministic multi-niche initialization

Unrepaired: `run()` calls `_place(g, anc)` whose `niche` defaults to 0, so the entire
initial population begins in niche 0.

Repaired: initial population is deterministically balanced across available niches unless
an experiment explicitly requests otherwise.

**T-P8**: under `NICHES_ISOLATED` every niche is populated, counts differ by at most one,
and no migration occurs; `RESERVOIR` does not begin with the whole population in the easy
niche. The unrepaired code fails.

### P-9 RESERVOIR x environment composition

Unrepaired: `_env_spec_for()` returns the coevolution spec and never calls `_niche_spec`,
so `COEVO_ENV` silently bypasses the reservoir's niche-0 modification. The predecessor's
one admissible endogenous instance sits in a `COEVO_ENV` cell.

Repaired: environmental dynamics and structural niche modifiers compose explicitly, in a
declared order.

**T-P9** constructs `RESERVOIR x COEVO_ENV` and proves niche 0 receives the easy
modification, hard niches retain the harder form, coevolution still changes the task, and
the composition order is deterministic. The unrepaired code fails.

### P-10 ENV_MIG semantic validity

Unrepaired: `_migrate` skips migration under `ENV_MIG` when `env_difficulty(niche) < 0.5`,
but `env_difficulty` returns 1.0 for every structure except `RESERVOIR`. Under `ENV_MIG`
the gate never fires and the factor is an ordinary 0.05 migration rate.

**Decision: option B, remove `ENV_MIG` from the Cycle-9 verification grammar.** None of
H1-H4 requires it, and a verification campaign should not be repairing a factor it does
not use. **T-P10** demonstrates the inertness on the predecessor code (migration
behaviour under `ENV_MIG` is statistically indistinguishable from a plain rate) and
asserts the level is absent from the Cycle-9 grammar.

---

## 2. Hypotheses and decision rules

Thresholds are frozen at review and are not adjusted after any result is seen.

### H1 — Does gating the answer on cue consumption change accessibility?

**Not** a read-order comparison. `FORCED_READ` changes target and input construction, so
it cannot serve as an intervention. Instead, **one fixed task** with a true intervention.

Held fixed across all four arms: inputs, expected answers, transform, bridge, population,
seeds, and VM semantics except the declared intervention.

Manipulated, 2 x 2:

| factor | levels |
|---|---|
| output gate | unrestricted; **OUT suppressed until the regime cue has been consumed** |
| cue-consumption cost | ordinary VM cost; cost-free world-mediated consumption |

Readouts of each run, not arms: `crossed_ever`, `crossed_at_final`, held-out competence.

**Predeclared statistic.** For held-out competence, the interaction is

    I = (mean[gate=on, cost=free] - mean[gate=off, cost=free])
      - (mean[gate=on, cost=vm]   - mean[gate=off, cost=vm])

with the gate main effect `M = mean[gate=on] - mean[gate=off]` over all cost levels.
**Threshold: |I| >= 0.15 is a real interaction; |M| >= 0.15 is a real main effect.**
Both are computed on final held-out competence, with `crossed_ever` and
`crossed_at_final` reported alongside and never substituted for it.

**Decision rule.** Gating changes accessibility if `|M| >= 0.15`. The execution cost
explains the gate effect if `|I| >= 0.15`. If neither reaches 0.15 the result is **no
detected effect of cue gating**, which is publishable and promotes nothing.

### H2 — Do replication events become self-sustaining lineages?

**Specimen panel frozen before launch.** Deterministic selection from the frozen
predecessor record, recorded as run IDs in `SPECIMENS.manifest.json`:

1. maximize coverage over `(reproduction, structure, representation)` strata;
2. within a stratum, rank by replication evidence (`replication_events` desc, then
   `first_replicator.fidelity` desc);
3. break remaining ties by ascending `sha256(run_id)`.

Target **16 mechanism-diverse specimens**.

Three arms per specimen, **shared background and RNG seeds**, differing only in the
implanted bytes:

- **A in situ** — the specimen's own cell, measured directly.
- **B actual-genome reimplant** — the specimen's first evidence-backed replicator genome
  implanted alone into a fresh world of the same cell.
- **C length-matched random-byte implant** — identical to B, random bytes of equal length.

**Primary endpoint: `max_causal_replication_depth`.**

**Decision rule.** A specimen supports self-sustaining replication only if arm B reaches
causal depth >= 5 in at least 3 of 5 seeds **and** arm C reaches it in at most 1 of 5.
Anything else is reported as **replication events without propagation**, which is the
predecessor's actual result and the default conclusion.

### H3 — Does the easy niche cause accessibility?

Cells frozen before launch by a deterministic rule over the predecessor record, recorded
in the manifest. No adaptive replacement after results arrive.

Three arms, shared seeds, everything else held fixed:

- **A** easy niche + migration
- **B** homogeneous niches + identical migration physics
- **C** easy niche + migration disabled

**Decision rule.** A reservoir-supporting result requires **both** a complete hard-niche
ancestry certificate in A **and** preregistered separation from B and C. Separation is a
certificate rate in A exceeding both controls by >= 0.20. Certificate count alone cannot
establish causation. Fewer than 5 certificates in A is **not demonstrated**.

### H4 — Is the n=1 endogenous instance real?

Exact cell of `64dea50f417efb02-s1203-tL-a0`. Fixed shared-seed `ENDOGENOUS_PARTIAL` vs
`EXTERNAL` pairs in four blocks, 16 seed-pairs each unless measured smoke timings force a
documented reduction before freeze:

- **A** exact historical cell, `SEEDED_READER`
- **B** same cell, `RANDOM` seeding
- **C** historical cell, `COEVO_ENV` replaced by the preregistered `STATIC` comparator
- **D** historical cell, periodic migration replaced by its preregistered topology comparator

No post-result allocation among blocks.

**Decision rule.** Confirmed if block A's endogenous arm reaches final held-out >= 0.90 in
at least 6 of 16 seed-pairs while its external arm reaches it in at most 1. Between those,
**seed-dependent**. Below, **retracted as an anecdote**, in those words. Blocks B, C and D
attribute any confirmed effect to the reader scaffold, coevolution or periodic migration
respectively.

---

## 3. Fixed job manifest

Percentage allocation is replaced by a machine-readable manifest enumerating every
hypothesis, bundle, cell or specimen, seed, arm, tier and budget, and every expected
control relationship. The manifest is hashed.

After freeze **the runner consumes the manifest only**. No UCB, no promotion, no
exploration floor, no replacement sampling, no result-dependent allocation.

The 24-hour deadline is a **maximum wall-clock envelope, not permission to invent work.**
If the manifest finishes early, the campaign stops. If smoke timings show the manifest
cannot finish with safe drain margin, the manifest is reduced **before freeze** by a
documented rule, and the power calculation is rerun.

---

## 4. What failure looks like

Recorded now so no outcome can be reframed later.

- **H1 null**: neither `|M|` nor `|I|` reaches 0.15. Cue gating has no detected effect.
- **H2 negative**: arm B never separates from arm C. The predecessor's 1,031 admissible
  events are single replication events in worlds that do not sustain lineages.
- **H3 empty**: zero certificates in arm A, or no separation from B and C. No reservoir
  support in this substrate.
- **H4 retracted**: block A does not reproduce. One anecdote removed.

All four negatives are publishable. None triggers a follow-up campaign by default.
"Not worth continuing" remains a first-class answer.

---

## 5. Gate before launch

| # | Gate | State |
|---|---|---|
| 1 | Operator review of this document (rev B) | **pending** |
| 2 | Operator review of repair tests T-P1..T-P10 | **pending** |
| 3 | Every T-P test fails on injected-defect fixture and passes on repaired substrate | see packet |
| 4 | Predecessor's 10 calibration controls pass | see packet |
| 5 | Verification smoke: real bundles, same-seed controls, reordered completions, forced restart | see packet |
| 6 | Freeze: grammar, protocol and manifest hashes written here; `CALIBRATION.json` records PASS | **not done** |

Until every row is complete this campaign does not launch. No production observatory is
created before freeze.
