# G0 — Was the 2026-04-02 forge T2/T3 rebuild approved and built?

**Seat:** Lexis · **Date:** 2026-08-25 · **Method:** read-only inspection of `forge/`, git history,
file mtimes. No forge code modified.
**Gate text (ROLE.md G0):** *"Was the 2026-04-02 T2/T3 rebuild ('AWAITING REVIEW — no implementation
code until approved') ever approved and built? → **Fires:** if the rebuild shipped, re-measure
primitive usage before any other work in this slice."*

---

## Verdict: **THE REBUILD SHIPPED. G0 FIRES.**

`forge/ARCHITECTURE_T2_T3.md` §11 specifies a file structure. Every single planned artifact exists
on disk, and the implementation mtimes begin **the same evening the document was written**:

- `forge/amino_acids/{registry,pgmpy_acids,pysat_acids,constraint_acids,nashpy_acids}.py`
  — 2026-04-02 **19:01–19:04**. The document is dated 2026-04-02.
- `forge/thresholds.py` (2026-04-03), `forge/tester.py` (2026-04-03), `forge/builder.py`,
  `forge/runner.py` (2026-04-06), `forge/tester_quarantine/trap_generator_t{2,3}.py` (2026-04-02
  19:11), `forge/null_baselines.json` (2026-04-02 19:11).
- `forge/candidates/` — **606 files** (~303 tools + meta), `forge/verdicts/` — **203 files**.
- Execution ran **2026-04-03 → 2026-04-12** (verdict timestamps, `forge/v2/hephaestus_t2/runs/`,
  13 run directories, `ledger_t2.jsonl`).

The four planned external libraries are all actually imported by generated tools:
`pgmpy_acids` 134, `constraint_acids` 114, `pysat_acids` 94, `nashpy_acids` 21 import statements
across `forge/candidates/`. **502 of 606 candidate files reference the amino-acid layer.**

The review in §12 was answered by building, not by a written approval. No approval document was
found; the evidence is the implementation itself.

---

## Consequence 1 — the "0% primitive usage" headline describes a SUPERSEDED system

`forge/ARCHITECTURE_T2_T3.md` §1 is titled **"Failure Analysis of Previous Attempt."** The quote

> *"Winning tools used 0% of their own primitive libraries — primitives were decoration"*

is a statement about the forge **before** 2026-04-02, not about the rebuilt one. `SIDE_BY_SIDE.md`
§9b promotes it to "the sharpest finding" about *the forge* without that qualifier. Corrected.

**And `CONTROLS.md` §2 measured the wrong population.** It reports the six tools in
`forge/v2/hephaestus_t2/forge/` calling **zero** of their twelve imported reasoning primitives, and
calls that *"the live tree."* Those files are dated **2026-04-02 10:38–10:41** — seven to eight hours
**before** the rebuild's first implementation file. They are the previous attempt's surviving tools:
the very population the architecture document was written to replace. Calling that measurement
"current-tree evidence" was `feedback_wrong_population_statistics`, committed inside the document
whose §2 exists to warn against exactly that error. Withdrawn.

The rebuilt population is `forge/candidates/` — the one `CONTROLS.md` §2 reported at
**1,343 of 1,646 imported primitives called (82%)** at rung R2.

## Consequence 2 — R4 ablation was never "unbuilt". It already ran.

`CONTROLS.md` §7 states *"Rung 3 (coverage trace) and rung 4 (ablation) are **not yet built**."*
False for the forge.

- `forge/tester.py:122` `run_ablation(tool_path, tier, seed=42, n_per_category=2)` — stubs each
  called primitive to `return None`, re-runs the battery, records `delta` and
  `load_bearing = |delta| >= min_ablation_impact`.
- `forge/thresholds.py` **pre-committed** `min_ablation_impact = 0.20` and
  `max_ablation_budget_share = 0.60` for both tiers, before any evaluation run.
- `FAIL_ABLATION` is a real verdict branch (`tester.py:445`).
- **198 of 203 verdict files carry an `ablation` block, containing 2,103 measured primitive deltas
  and 3 errors.**

So the criterion `ROLE.md` describes as *"ratified in June 2026 and never measured"* was in fact
pre-committed and measured in **April 2026**, on 198 tools. The G1 dataset exists on disk. This is a
read, not a build. It is mined in `G1_ABLATION_2026-08-25.md`.

## Consequence 3 — the frozen thresholds were softened after the numbers existed

`forge/thresholds.py` opens:

> *"FROZEN THRESHOLDS — Pre-committed before any tool evaluation. DO NOT MODIFY after first
> evaluation run."*

`git diff b674a997 c07c5b17 -- forge/thresholds.py` (2026-04-03 → 2026-04-04):

- `pass_threshold` **0.50 → 0.40**
- `max_seed_drop` **0.15 → 0.20**

The committed rationale states the reason outright: *"50% was beyond the population maximum
(best=45%, mean=23%). 24-trap battery granularity means 0.50 filtered ALL 75+ candidates. 0.40
admits 5 tools across 3 families."* And: *"Old 0.15 ceiling allowed only ~3 answers variance, which
29% of tools exceeded."*

Both edits move the line **toward the observed data**, are justified **by** the observed data, and
were made in the file that forbids it. Direction of the confound is unambiguous: it can only
increase the pass count. **Every passing tool in the rebuilt forge passes only under the softened
threshold** — the pre-registered 0.50 admitted zero of 75+ candidates by the file's own admission.

Note the second edit is also `feedback_gate_must_exceed_measurement_error` in reverse: the observed
seed variance was measured *first*, then the gate moved to accommodate it.

This is not a claim that 0.40 is the wrong number. `best = 45%` against a `0.2917` NCD null means
0.50 was a gate that could not fire (`feedback_gate_must_be_shown_reachable`) — the original
threshold was itself unreachable and someone was right to notice. It is a claim that the correction
was made **after** seeing the results, inside a frozen file, and that no artifact records the
re-freeze. Reachability should have been computed before the freeze, not discovered by it.

## Consequence 4 — two PASS verdicts are instrument artifacts, not results

Of 203 verdicts: **176 FAIL_BATTERY, 19 FAIL_DIVERSITY, 3 flat PASS, plus a later cluster gate with
4 FAIL / 1 PASS.**

Only one tool survives the cluster gate: `t2_temporal_scheduling_007_gem`
(cluster B, 0.7667, 3/6 categories, seed drop 0.1667).

The other two flat PASSes — `t2_liar_detection_000` and `t2_simpson_paradox_003`, both
`overall_score = 0.400`, exactly at the softened threshold — are **byte-identical in their
measurements**: the same five seed scores `[0.3333, 0.5, 0.375, 0.375, 0.4167]`, the same
`seed_stability = 0.16667`, and the same per-category pass/fail vector (1 of 12: `perspective_shift`).
The two source files differ (369 vs 277 lines, different md5). Two structurally distinct tools cannot
produce identical per-seed and per-category results unless the tester is scoring something common to
both — a shared fallback path, a default answer, or a failed import resolving to the same behaviour.

Supporting evidence for the failed-import reading: **13 candidate files import amino-acid modules
that do not exist** — `forge.amino_acids.{basic, core, standard, proteins, protein, peptide,
nucleic_acids, leucine, helix, generic, basic_amino_acids}`. All eleven module names were verified
absent. The builder hallucinated module paths, and the tester scored the result anyway.

**Reading:** the rebuilt forge's admitted set is **one tool**, not three. The other two are the
tester measuring its own fallback.

---

## What G0 changes for the slice

1. The 0%-usage finding stays true but is **relabelled to its correct population** (pre-2026-04-02
   forge). It is no longer evidence about the current system.
2. `CONTROLS.md` §2's "live tree" claim is **withdrawn**; §7's "ablation not yet built" is
   **withdrawn**.
3. G1 becomes a **mining task over existing data**, not a build. 2,103 deltas are on disk.
4. A new finding enters the ledger that is arguably worth more than G0 itself: **the forge's
   admission gate was moved after its numbers existed, and one of its three admitted tools is real.**
5. The rebuild's own design **already contained** the thing this slice was going to recommend —
   a pre-committed ablation gate on primitive load-bearingness. It was built in April and, per the
   verdict distribution, was almost never the binding constraint (0 `FAIL_ABLATION` verdicts;
   battery failure dominates at 176/203). Why it never bound is the next question.
