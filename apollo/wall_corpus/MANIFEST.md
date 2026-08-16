# Tier A ablation-wall corpus — manifest

> **Supplier:** Apollo (M2) · **Generated:** 2026-08-15 · **Substrate commit:** see
> `provenance.substrate_commit` in each record
> **Contract:** `stations/M1_STATUS.md` §7b · spec
> `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` §2/§4.2 · prereg
> `pivot/PREREG_METABOLIZATION_PROBE_v1.md`
> **Also discharges:** W0/W1 of `pivot/STRATEGY_2026-08-12_resumption_and_roadmap.md` §10.

**28 runs — 26 walls across 4 failure classes, plus 2 unablated controls.**
Contract minimum was ≥20 walls / ≥4 classes.

| file | contents |
|---|---|
| `corpus.jsonl` | one typed record per line — the consumable |
| `walls/<WALL_ID>.json` | the same records, one file each |
| `corpus_manifest.json` | machine-readable class index + field dispositions |
| `runs/<WALL_ID>/` | raw `evolve_log.jsonl` + checkpoint per run — **gitignored** (23 MB); deterministic, regenerate with the command below |
| `runs/<WALL_ID>_console.log` | per-run console capture (written from Python with per-line flush, never shell-redirected) |

Regenerate: `python apollo/scripts/wall_corpus.py --all --gens 150`
Validate: `python apollo/scripts/wall_corpus_validate.py` (exit 0 = clean)

---

## 1. Field disposition — what may enter which arm's packet

**This is the F-answer / F-oracle firewall. It is enforced by the validator, not by
convention.**

| field | disposition |
|---|---|
| `wall_id`, `wall_signature`, `oracle_diagnosis` | **SHIPPABLE to F-oracle** |
| `answer_content` | **QUARANTINED** — the fix. F-answer only. |
| `ablation_applied` | **QUARANTINED** — names the exact edit; this is answer content in provenance clothing |
| `failure_class` | **QUARANTINED** — the label a detector must predict; shipping it is self-answering |
| `provenance`, `separability` | never shipped to any solver |

`oracle_diagnosis` is CAUSE ONLY: it names the mechanism and the missing capability
*class*, never the operator to add or the edit to make. The validator enforces two rules —
(A) no registered operator name appears in an oracle, (B) no imperative-repair verb
appears in an oracle — and ships a **planted-violation self-test that must fail loud**
(spec §4.2 exit criterion). Current status: **28 records, 0 violations, planted violation
CAUGHT.**

`separability`: all 26 walls are `clean` (cause and fix are separately statable). No wall
required the `tight` / F-answer-only flag, so Ergon has no inclusion rulings owed on this
corpus.

## 2. The four failure classes

| class | n | what is ablated | what remains intact |
|---|---|---|---|
| `search_operator_removed` | 6 | the move that could assemble the capability | the capability itself, in the registry |
| `expressiveness_restricted` | 8 | the operator, from the registry entirely | the search, the meter, the wiring |
| `measurement_artifact` | 6 | the meter's scope, resolution, precision or identity function | the capability, the search, the wiring |
| `interface_bug` | 6 | one wiring detail (guard slot, write persistence, failure mode) | everything else |
| `control_none` | 2 | nothing | everything |

## 3. Corpus-level findings

These emerged from building the corpus and are reportable results in their own right.

**F1 — Withholding any single mutation move produces NO wall while recombination is
active.** SO-02/03/05/06 were first built as single-move ablations with crossover at the
production 0.3. All four reached **exact control parity** (max_acc 0.833, routable 1.000,
coverage 0.833). Crossover reconstructs whatever the withheld move would have supplied.
The four were therefore re-specified as **compound** ablations (move withheld *and*
crossover disabled), recorded as `ablation_applied.compound = true`, and re-run — they now
wall at 0.233–0.542. This is an independent replication, from the ablation side, of the
2026-06-16 recombination finding: **the recombination operator, not the single-step
mutation set, is what makes this substrate searchable.**

**F2 — The routing-purity term is inert under dispatch mode.** The original MA-03 removed
`routing_purity` from the composition score and produced telemetry **byte-identical to
CTRL-01** on every logged field. Cause: in dispatch mode the mutation scorer pool is
already narrowed to guarded scorers, so plain+guarded hybrids never form and the purity
factor is always 1.0. The guard is belt-and-braces, not load-bearing, in this
configuration. MA-03 was replaced with a descriptor ablation that does bind.

**F3 — Five wall pairs are indistinguishable on headline numbers alone** (accuracy,
routable accuracy, coverage, per-subset). They are separable on deeper telemetry; the
separators are listed in §4. These are the corpus's hard items **by construction** and
should be treated as such when scoring: EX-05/IB-01, EX-02/IB-04, EX-04/IB-06,
CTRL-01/MA-06, MA-02/SO-04.

**F4 — Two walls are silent on accuracy entirely.** MA-06 (archive identity function
ignores the body) and, in its original form, MA-03 leave max_acc, routable accuracy and
coverage at control values. The fault is real and visible only in population structure
(31 cells vs the control's 878–956). A detector that fires only on accuracy loss will
score zero on these, which is why they are retained.

## 4. Candidate discriminators — a first cut, NOT a validated detector

Structure visible in the corpus. Offered as W1's starting hypothesis, with its limits
stated first.

**Limits:** one seed per wall; the no-fault noise floor is estimated from a single control
pair (CTRL-01 vs CTRL-02), which spread 878 vs 956 cells (~9%) and 51 vs 49
gens-to-plateau. Any separator whose margin is inside that spread is not established.
Nothing below has been cross-validated.

The relation between **`final_max_acc`** (best single organism) and
**`final_portfolio_coverage`** (union over the whole archive) carries most of the signal:

| observed relation | reading | classes exhibiting it |
|---|---|---|
| `max_acc == coverage`, both below control | no organism and no union solves it — the capability is genuinely unreachable | EX (7/8), IB (4/6) |
| `coverage == control` (0.833) while `max_acc` collapses | the capability is present in the population but no single organism assembles it | **SO (6/6)** |
| `coverage == control` while `max_acc` sits below it | the population is healthy; the meter disagrees with it | MA-01/02/03/05 |
| **`max_acc > coverage`** | logically impossible — one organism cannot out-solve the union of all organisms. Instrument fault, no inference about the population is admissible | MA-04 |

That last row is the sharpest signature in the corpus and needs no threshold.

Within the EX-vs-IB collisions, `final_primitive_families` separates all three pairs
(EX-05 19 vs IB-01 20; EX-02 19 vs IB-04 20; EX-04 18 vs IB-06 20; control 20).
**It is not a general EX-detector** — the count is families observed *in the archive*, not
registry membership, so a search that explores less (SO-02/03/05/06) or an archive that
collapses (MA-06, IB-05) also drops below 20. Necessary, not sufficient.

`shape_inflation_ratio` (cells ÷ distinct real shapes) isolates MA-02 (1.746) and IB-05
(1.643) against a control of 1.05–1.06.

**The honest negative result:** `branches_load_bearing_for_nothing` — the per-branch
ablation audit, which I expected to be the primary EX-vs-IB discriminator — is
**identical** across EX-05/IB-01 and EX-02/IB-04. A branch whose producer was deleted and
a branch whose guard was mis-keyed both present as "load-bearing for nothing." Plateau
telemetry alone does not distinguish *capability absent* from *capability present but
mis-wired*; separating them needed a feature (family count) that is only an indirect proxy
for registry state. **This is the program's representational-vs-interface distinction
appearing as a measurement problem inside Apollo**, and it is the concrete W1 finding this
corpus produced.

## 5. How each wall was produced

The harness (`apollo/scripts/wall_corpus.py`) **never edits the substrate** — heredity
rule. Each ablation rebinds module globals on a freshly imported `blackboard_evolve` in a
throwaway subprocess. `blackboard_evolve.py`, `blackboard.py` and the `blackboard_ops_*`
modules are unmodified on disk. Mutation-move withholding rejection-samples the
substrate's *own* mutator on its lineage tag rather than reimplementing it.

Base configuration = the current production config, so every wall differs from the control
in exactly one declared factor: `--dispatch --crossover-frac 0.3`, pop 24, deterministic,
seed 20260815, **150 generations** (per leverage #4 — the substrate ceilings at ~130 and
every wall here plateaus by gen 137).

## 6. What this corpus does NOT establish

- Tier A's permitted verdict vocabulary is exactly `HARNESS_ADMISSIBLE` /
  `HARNESS_NOT_ADMISSIBLE` (spec §4.2). **No number in this corpus is thesis evidence.**
  These are *constructed* failures and their F-oracle diagnoses are cleaner than any real
  residue will ever be — that idealization is the reason Tier A was demoted to harness
  qualification, and it applies to everything here.
- Nothing about whether a *model* can read these diagnoses. This is supply only.
- The discriminators in §4 are unvalidated at n=1 seed per wall.
