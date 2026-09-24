# Z80 x Atlas VERIFICATION campaign - 24 hours - PREREGISTRATION

Status: **rev D (operator final rulings + promotion directive 2026-09-24). NOT FROZEN.
NOT LAUNCHED.** Under the seat's autonomous charter this is the INNER experiment `C9` of
the Cycle-9 campaign (`roles/Nestor/EXPERIMENT_GRAPH.jsonl`); freeze and launch are the
seat's decision once every gate passes. No
grammar, protocol, manifest, panel or constants hash is written as final here. The
proposed values are in `PROPOSED_HASHES.json`, recomputed by `proposed_hashes.py`, and are
written into this file only at freeze. Governing rulings:
`roles/Nestor/prompts/2026-09-24_cycle9_final_rulings/DIRECTIVE_VERBATIM.md`.

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
| A-15 | pair-tape causal edge = predecessor write-count criterion | **New P-11**: the predecessor criterion AND a matched randomized-victim assay (`P11_SPEC.md`) | The write count does not show the donor's bytes were carried; S1-C: 57 of 1,031 survive, and in 6,287 of 6,547 RECOMBINATION events the post-interaction splice made the match |
| A-16 | - | P-11 authorship: **primary = causal_value_authorship** (last context to CHANGE a byte into its final donor-matching value; a later same-value rewrite does not erase it); **literal last-write attribution = mandatory sensitivity analysis**, reported beside every P-11 result | Operator ruling 2026-09-24. Reassay: primary 57, literal 48 |
| A-17 | H2 panel: 16 specimens from the predecessor's 1,031 | **16-specimen panel rebuilt from P-11 survivors** (`specimens.manifest_p11`, rule committed before S1-C results); arm B implants the donor of the first P-11-causal event, embedded in the manifest | Operator ruling; none of the rev-B specimens is retained |
| A-18 | H2 5 seeds; B >= 3/5 and C <= 1/5 | **16 shared seeds; B >= 8/16 and C <= 2/16; panel positive needs >= 2 supporting specimens from different strata; depth >= 2 and >= 3 secondary readouts only** | Operator ruling 2026-09-24 |
| A-19 | P-1 certificate walked every lineage edge | **Every hereditary PAIR_EXECUTION edge on the certificate chain must be P-11 causal; a non-P-11 pair edge breaks the certificate** | Operator ruling (C9-D11); test T-H3-P11 fails on the old code |
| A-20 | H3 cells = RESERVOIR specimens of the H2 panel, 16 seeds | **Two RESERVOIR cells repicked prospectively from the P-11 record** (cells of `4931614d912c52b2-s1190-tL-a0`, same-cell survivor `-s9368-tM-a0`, and `a62116831aa6d956-s7926-tM-a0`); **32 shared seeds**; 192 runs | Operator ruling |
| A-21 | H3 arm B = `NICHES_HIGH_MIG` | **Arm B = RESERVOIR structure with the easy-niche modifier off** | C9-D13: NICHES_HIGH_MIG migrates at 0.08, the reservoir at 0.02; "identical migration" was false |
| A-22 | H4 four blocks x 16 seed-pairs | **WITHHELD. Removed from this campaign.** A-4 is withdrawn; the S1-B autopsy is preserved | Operator ruling. The endogenous arm never reproduces (C9-D07), and the historical control was unmatched (Z80A-D04) |
| A-23 | thresholds as literals in several modules | **One hash-covered constants object** (`constants.py`), including the H1, H2 and H3 decision thresholds | S3-2 |
| A-24 | H3 certificate = organism-id ancestry (repaired by A-19) | **Ruler R3, MATERIAL certificate**: a crossing outside the easy niche by a genome whose bytes are >= 0.50 easy-niche MATERIAL. Every byte carries the niche in which its value was made; the tag moves with the data through the VM (`z8taint.run_tainted`, bit-identical to `z8.run`) and through mutation (sequence alignment). The id certificate is kept as `id_certificate_legacy`, a sensitivity reading | C9-D14: on the pair tape an organism keeps its id while its bytes are replaced (0.97 -> 0.00 identity over 600 epochs with no lineage event). Bounded repair tournament over R0 (id), R1 (founder fidelity), R2 (causal edge + window), R3 (material) on 9 adversarial fixtures run through the real pair-interaction code: R3 9/9, R1 7, R0 4, R2 4 (`H3_RULER_TOURNAMENT.json`, T-H3-MAT) |
| A-25 | H3 arms read as: C isolates transport | **C removes ORGANISM migration only.** On the pair tape, pairing is niche-blind, so material also crosses niches through pair writes in every arm; A vs C isolates migration as one transport route | Consequence of the physics, stated before any result |
| A-26 | H3 decision per cell, unspecified | **Primary = POOLED over the two cells** (64 bundles per arm); per-cell verdicts are secondary | Declared before launch; pooling maximises power for a rare event |
| A-27 | adjudication rules existed only as prose | **`hypotheses.py`** implements H1 (readout `held_max_final`), H2 and H3; **`adjudicate_c9.py`** applies them to the bundle store; **`report_c9.py`** renders the report from a machine block; **`report_audit_c9.py`** recomputes every number independently from the raw bundle files. **`run_campaign.py`** consumes the frozen manifest: resume from the P-7 store, one identical retry per failing job, no replacement jobs. T-H2, T-INFRA (kill/resume byte-identity, freeze refusal, error path, 7 audit negative controls) | Launch blockers found pre-freeze (INFRASTRUCTURE) |
| A-28 | P-11 literal sensitivity only in the forensic reassay | **Every pair edge also carries `pass_literal`**; `max_causal_replication_depth_literal` is recorded and the H2 panel rule is re-read on it as the mandatory sensitivity | A-16 applied to the campaign itself |

---

## 0. Why this campaign exists

Four questions the 72-hour campaign raised and cannot close from its own record.

| # | Question | Why the predecessor cannot close it |
|---|---|---|
| H1 | Does requiring the cue to be consumed before answering change accessibility? | The predecessor's `read_order` factor changes the task itself, so its two arms are not the same experiment measured twice |
| H2 | Do evidence-backed replication events become self-sustaining lineages? | Ancestry depth was never an endpoint. Reconstruction shows depth 1 in 911 of 1,031 admissible runs |
| H3 | Does an easy niche act as a genetic reservoir? | The lineage record keeps a 400-event tail, logs no migration, and stores only the parent's niche at birth |
| H4 | ~~Is the single admissible endogenous-only instance real?~~ **WITHHELD (A-22).** A-4 is withdrawn: its control was unmatched and its endogenous population never reproduced | - |

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

### P-11 PAIR_EXECUTION copy causality (H2, H3)

Specified in `P11_SPEC.md` and implemented in `p11.py` (commit `f28e5fd72`, before any of
the 1,031 was inspected). A pair-tape edge is causal iff it passes the predecessor
criterion AND the randomized-victim assay (3 draws, majority 2: rebuild >= 0.90, donor
authorship >= 0.90 of donor-directed changes, donor-disabled control < 0.90).
**Authorship, primary: causal_value_authorship** (A-16). **Literal last-write
authorship is a mandatory sensitivity analysis.** Every P-11 result is reported under
both. `max_causal_replication_depth` on the pair tape uses P-11 edges;
`max_predecessor_replication_depth` is kept beside it. **T-P11** (14 checks) fails the
predecessor detector on three negative controls. The frozen predecessor result, 1,031
admissible under its historical criterion, is not rewritten.

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

**Specimen panel (A-17).** 16 specimens chosen from the 57 P-11 survivors by a
deterministic rule committed before any S1-C result was read (`specimens.select_p11`):
coverage round-robin over (reproduction, structure, representation), then P-11 events
descending, first P-11 donor fidelity descending, ties by sha256(run_id). There were 52
eligible candidates; the panel covers 13 strata. Panel hash in `PROPOSED_HASHES.json`.

Three arms per specimen, **16 shared seeds**, identical background and RNG seed:

- **A in situ** — the specimen's own cell.
- **B actual-genome reimplant** — the donor genome of the specimen's first P-11-causal
  event, implanted alone. The bytes are embedded in the manifest.
- **C length-matched random-byte implant** — identical to B except for the bytes.

**Primary strong endpoint:** `max_causal_replication_depth >= 5` (P-11 edges).

**Specimen rule.** A specimen SUPPORTS the strong endpoint iff arm B reaches it in
**>= 8 of 16** seeds AND arm C reaches it in **<= 2 of 16**. A specimen with any
incomplete bundle is INCOMPLETE and never supports.

**Panel rule.** PANEL_POSITIVE requires **at least two supporting specimens from
different frozen strata**. Exactly one supporting specimen is an **ISOLATED_CANDIDATE,
not a panel-level positive**. Two or more supporting specimens that all share one
stratum are reported as SAME_STRATUM_CANDIDATES, which is also not panel-level positive;
the ruling does not name this case, and it is flagged for review. Otherwise the result
is **replication events without propagation**, the default conclusion.

**Secondary readouts only:** the same counts at depth >= 2 and depth >= 3 for every arm.
They never change a verdict. Implemented in `hypotheses.py`, test T-H2.

Precedent, recorded before launch: across all 1,031 predecessor runs, the maximum P-11
depth is 2.

### H3 — Does the easy niche cause accessibility?

**Cells (A-20)**, repicked prospectively from the completed P-11 record: the two unique
RESERVOIR cells among the P-11 survivors, those of `4931614d912c52b2-s1190-tL-a0` (same-cell
survivor `4931614d912c52b2-s9368-tM-a0`) and `a62116831aa6d956-s7926-tM-a0`. They are pinned
in `manifest.H3_CELLS`, independent of the H2 panel.

Three arms, **32 shared seeds per cell**, everything else held fixed (192 runs):

- **A** easy niche + migration (RESERVOIR)
- **B** homogeneous niches + **identical** migration: the RESERVOIR structure with the
  easy-niche modifier off (A-21)
- **C** easy niche + migration disabled

**Certificate (A-24, supersedes A-19 for the verdict).** Ruler R3: the first crossing
(held >= 0.90) outside the easy niche by a genome at least 0.50 easy-niche MATERIAL,
material provenance carried by dataflow through the VM. The A-19 id certificate (every
pair edge P-11 causal) is recorded as `id_certificate_legacy`, a sensitivity reading only.
Arm C removes organism migration; material can still move through pair writes (A-25).
Primary verdict pooled over both cells (A-26).

**Eligibility, recorded before launch:** in the frozen record, 50 of 194 random-start
pair-tape RESERVOIR runs crossed at least once; the `4931614d912c52b2` family never did, and
the `a62116831aa6d956` family crossed in both of its runs. The bar of >= 5 arm-A
certificates is attainable but not assured.

**Decision rule** (unchanged). A reservoir-supporting result requires **both** a complete
hard-niche ancestry certificate in A **and** preregistered separation from B and C: a
certificate rate in A exceeding both controls by >= 0.20. Certificate count alone cannot
establish causation. Fewer than 5 certificates in A is **not demonstrated**.

### H4 — WITHHELD (A-22)

Removed from this campaign by operator ruling on 2026-09-24. It is not redesigned before
Cycle 9. A-4 is withdrawn. The S1-B autopsy
(`campaigns/z80atlas-forensics-2026-09-23/H4_AUTOPSY.md`) is preserved.

---

## 3. Fixed job manifest

Percentage allocation is replaced by a machine-readable manifest enumerating every
hypothesis, bundle, cell or specimen, seed, arm, tier and budget, and every expected
control relationship. The manifest is hashed.

Generated manifest, authoritative for counts: **H1 240, H2 768, H3 192, H4 0; 1,200
runs** in 380 bundles (`manifest.build()`, validated by T-MAN).

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
- **H4**: withheld (A-22); A-4 is already withdrawn.

All three negatives are publishable. None triggers a follow-up campaign by default.
"Not worth continuing" remains a first-class answer.

---

## 5. Gate before launch

Freeze block, written only by `freeze.py` after every gate passes, and excluded from the
preregistration hash it records:

<!-- FREEZE-BEGIN -->
NOT FROZEN.
<!-- FREEZE-END -->


| # | Gate | State |
|---|---|---|
| 1 | Operator review of this document (rev B) | **pending** |
| 2 | Operator review of repair tests T-P1..T-P11, T-S3, T-H3-P11, T-H2 | rulings 2026-09-24 |
| 3 | Every T-P test fails on injected-defect fixture and passes on repaired substrate | see packet |
| 4 | Predecessor's 10 calibration controls pass | see packet |
| 5 | Verification smoke: real bundles, same-seed controls, reordered completions, forced restart | see packet |
| 6 | Freeze: grammar, protocol and manifest hashes written here; `CALIBRATION.json` records PASS | **not done** |

Until every row is complete this campaign does not launch. No production observatory is
created before freeze.
