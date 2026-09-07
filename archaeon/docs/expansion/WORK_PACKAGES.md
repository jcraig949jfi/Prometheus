# Work packages

Annex to `archaeon/docs/ROADMAP.md` §Diversity. 2026-09-07. Graph in
`GRAPH.md`. Every package states: the question and crosswalk entries it
serves; the capability an organism or experiment gains; the smallest faithful
implementation with reuse evidence and semantic compromises; owner and
handoffs (checked against `CHARTERS_SURVEY.md`); prerequisites; cost and
uncertainty with the smallest spike; the acceptance artifact; what failure
would establish and leave open; when a deferred route is reconsidered.

Cost: **S** under a day, **M** a few days, **L** longer. Compute is host CPU
unless stated; nothing here needs the GPU.

## Compact table

| WP | Owner (handoffs) | Serves | Gains | Cost | Pre-reqs | Acceptance artifact |
|---|---|---|---|---|---|---|
| 0a | Daedalus | all bitstring | no silent ceiling | S | — | test: `len(bits)!=length` → rejected candidate; one live re-run of Herakles's F-1 table showing refusal |
| 0b | Vivarium | any stateful family | honest degeneracy flag | S | — | test: constant seed + reset + stateful kind → `degenerate_by_construction=True` |
| 0c | Vivarium (Daedalus: `sfclient.family_member(arm=)`) | M-ELIGIBLE | one arm value in both seals | S | v7 live (done) | one executed arm-bound request whose `family_members.arm` == PEW `design.arm_id`; audit envelope carries arm by value |
| 0d | Archaeon (Harmonia reads) | M-SIGNAL | D3 null rate reconciled | S | — | eligible-region count per null corpus + either reconciliation or a regenerated null with region and neighbourhood drawn independently; Harmonia's 0.106 reproduced or explained |
| 0e | Archaeon | 7 inbox templates now, every kind later | non-bitstring specs buildable | M | — | `falsification_walk.v0` (with `step_scale` fixed) builds, validates, and `check()` reports buildable; 213+ tests |
| 0f | Vivarium | every new kind | checkable result fields | S | — | `Kind.result_schema`; `cli kinds` prints it; Archaeon's `check()` validates the template's outcome-rule field against it |
| X1 | Harmonia (Daedalus: nothing; Archaeon: first analysis) | 22 R-COMPOSE entries; M-SIGNAL endpoint | adjudicable cross-observation statistic | S policy | — | a written convention: `families(kind=analysis)` + `source_set` + `unit_of_analysis` + `analysis_version` + declared null; one worked analysis over M-ELIGIBLE rows |
| X2 | Vivarium (operator: tool admission; Harmonia: what a grade licenses) | 22 R-BACKEND entries | orchestrated tool with measured reproducibility | M | D-4 | contract doc + one tool (from WP-P0) run twice under one seed with digests compared; per-observation `reproducibility` measured, lease sized |
| X5 | Mnemosyne | B, D | queryable witness; lineage edges | S | — | additive `witness jsonb`; `POST /fossil/edges` (ANCESTOR/MUTATION/TRANSFER); round trip shown |
| X6 | Archaeon (operator sets numbers) | all new families | new families get draws | S | D-6 | `allocation.reserve.v0` policy file; census reports reserve spent/unspent per lane |
| X7 | Archaeon (operator admits) | each family | fossil→selection loop closes per family | S each | family kind exists | `<family>.resample_region.v0` + `<family>.uniform.v0` (frozen control) admitted; tick draws the directed one when a qualified detector fires on that family |
| X8 | Archaeon | R2 | retained distinct organisms + informative failures | M | 0f | archive table keyed by descriptor cell with pointers only; health report counts occupied cells |
| A1 | Daedalus (executor) + Vivarium (kind) | 17 entries | epistasis with a control | M | 0f | `nk_landscape_v0(bits,length,k)`; k=0 reproduces additive scoring; replay: same seed → identical tables and score; contribution witness returned |
| A2 | Archaeon (operator admits) | A | known-answer null + mechanism control | S | A1, 0e | `nk.permutation_null.v0`, `nk.k0_control.v0`, `nk.uniform.v0` PROPOSED and checkable |
| A3 | Archaeon issues; Vivarium runs; Harmonia adjudicates | A; M-SIGNAL on a non-flat substrate | first fossils with interaction structure | S (+ ~180 runs) | A2, X1, X7 | comparison family k∈{0,2,4} × 3 seeds × 20 queries; preserved observations with witnesses; D3 eligibility per k against the permutation null; Stage 0 rerun unchanged on the family |
| A4 | Daedalus + Harmonia | transfer entries | related landscapes (shared tables) | M | a stateful organism (B4) | deferred |
| B1 | Proteus (VM as a pure library) + Vivarium (kind); Daedalus: nothing | 17 entries | exact counterexamples; traces | M | 0f, D-9 | `program_eval_v0(program, spec_id, step_budget)` → outputs, halted, steps, trace digest, witness; replay identical; the 64 USE_A specimens evaluate under it |
| B2 | Archaeon (operator admits) | B | bijection null; witness-withheld control | S | B1, 0e | `program.opcode_bijection_null.v0`, `program.witness_withheld.v0`, `program.uniform.v0` PROPOSED and checkable |
| B3 | Archaeon issues; Vivarium runs; Harmonia adjudicates | `cegar`, `cegis`, `query_by_committee`, `l2s` | C-2 priced in rounds | S (+ ~120 runs) | B2, X1, X7 | two-arm comparison family, rounds-to-match with vs without witness, same deterministic proposal rule, 3 seeds; region structure on opcode-histogram coordinate reported |
| B4 | Proteus + Harmonia | organism diversity, transfer | organisms that observe the world | L | — | Harmonia PATH B: widened input channel, re-run L2; usable population reported with alphabet/entropy/floor/ceiling |
| C1 | Herakles (verifier as a pure library) + Vivarium (kind) | 10 entries | a spatial, stateful world with real organisms | S/M | 0f, D-9 | `ca_density_v0(rule_hex, radius, n_cells, steps, n_ic, ic_density_set)` → accuracy, misclassified-IC witness, one space-time digest; the six historical genomes reproduce their published accuracies within IC sampling error |
| C2 | Archaeon (operator admits) | C | reflection null; r=0 / T=1 controls | S | C1, 0e | `ca.reflection_null.v0`, `ca.r0_control.v0`, `ca.t1_control.v0`, `ca.uniform.v0` PROPOSED and checkable |
| C3 | Archaeon issues; Vivarium runs; Harmonia adjudicates | C; historical collider GATE-1 | first spatial fossils; a literature anchor | S (+ ~100 runs) | C2, X1, X7 | comparison family random-rules vs historical genomes, 4 ordered repeats per world; witnesses and digests preserved; D3/D6 eligibility on the random arm against the reflection null; rediscovery, if any, labelled calibration |
| C4 | Harmonia + Archaeon | `poet`, `hide_and_seek` | environment co-development | M | C3, D-3 | deferred; reopen after C3 |
| P0 | Vivarium (build/run) + operator (authorise); Ergon consulted (freeze record) | D | a measured fact about runnability and determinism | 2 days | — | for each of {Avida 2.2 under MinGW, replicator soup sketch, hct01.c}: builds? runs? two runs one seed → digests equal? cost per run; written up, no science |
| P1 | Vivarium (kind) or X2 (backend) | D | a population world | M | P0, P2, P3 | one observation per generation with lineage fields; unlimited-resource control reproduces neutral drift statistics |
| P2 | Harmonia (vocabulary) + Daedalus (schema) | D, C (episodes) | honest units | S | — | `generation`, `episode` in `unit_of_analysis`; REPLICATION typing declared in the manifest |
| P3 | Harmonia (test) + Proteus/Vivarium (kernel) | D; any diversity claim | a neutral variation operator | M | — | detailed-balance test passed by the kernel, not zero marginal drift |

## Per-package notes (what failure establishes; when to reconsider)

**WP-0d.** Failure to reconcile means Archaeon's synthetic null corpora are
structurally easier than real ones; every downstream false-discovery figure is
optimistic until regenerated. Not deferrable.

**WP-0e.** Failure (a kind whose result cannot be expressed as one declared
field plus a within-run aggregate) is the first genuine outcome-rule
limitation; record the kind and the field shape, route to X1.

**WP-A1/A3.** If D3 eligibility and fire rate on `k > 0` are indistinguishable
from `k = 0` and from the permutation null, the fossil record of an epistatic
world carries no region structure the current detectors can read — a fact
about the detectors' coordinates (region = world; metric = score), and the
reopening condition is a declared descriptor coordinate (X8). It would leave
open whether other coordinates read structure; it would not license "NK is
flat."

**WP-B1/B3.** If rounds-to-match with the witness does not beat without it,
the proposal rule is not using the witness (a defect in the rule, priced) or
the specification is too small for a witness to matter (a design fact:
reopen at a larger input space). It would not establish that counterexamples
are useless. If the 64 specimens all halt without output under the
specification, B4 is confirmed as the prerequisite and B3 proceeds with
producer-proposed programs only.

**WP-C1/C3.** If the six historical genomes fail to reproduce their published
accuracies, the verifier or the IC convention is wrong — fix before anything
else; this is why the historical arm exists. If the random arm's fossils show
no region structure under any declared descriptor, the family is honestly
"needle-like" at this scale and the reopening condition is a descriptor with
literature support (particle count in the space-time diagram). A rediscovery
of block-expanding or particle strategies is a calibration anchor and is
recorded as such, never as a discovery.

**WP-P0.** If Avida 2.2 builds and is BIT_DETERMINISTIC under a seed, X2 has
its first tool and the fidelity-to-1.6 question goes to Ergon's freeze
record; if not, P1 is the in-process soup. If neither is deterministic, the
population branch is DEFERRED with the reason written, and reconsidered when
a deterministic replicator exists anywhere in the repo.

**WP-P3.** A kernel that fails detailed balance is not rejected; it is
labelled as carrying authored current, and every diversity statistic under
it is reported beside the neutral-drift control (R5). Reconsider when a
kernel passes.

**WP-B4.** Long, and not Archaeon's. Until it lands, "organism diversity"
means bitstrings, rule tables, and producer-proposed programs; the 64
specimens are a panel of fixed artifacts, not agents. Reopen every
organism-level claim in B when Harmonia reports the usable population.

## What each first experiment lets the next action depend on

- **A3 → X7(A):** a fired D3 region on an NK world (coordinates: seed, k,
  length) becomes the argument of `nk.resample_region.v0`; the directed draw
  is compared against `nk.uniform.v0` under M-SIGNAL's rules on the NK
  family's own frozen corpus.
- **B3 → `program.refine_on_witness.v0`:** the witness (an input) becomes a
  *parameter* of the next program's specification emphasis; the first
  template whose parameter is prior observation content, admitted by the
  operator, compared against `program.uniform.v0`.
- **C3 → `ca.resample_region.v0` and a directed IC distribution:** a fired
  region on the rule-table coordinate, or a witness IC set, becomes the next
  draw's constraint; compared against `ca.uniform.v0`.

In every case the comparison is a frozen-corpus, orders-committed-first,
equal-budget M-SIGNAL round on that family, adjudicated by Harmonia, with the
family's exchangeability null run in the same round.
