# D-10 — Endogenous Relevance Keying

Experiment-side material for D-10. Everything here is **experimental, not
instrument**: the Prometheus Serendipity Foundry under `F:\SerendipityE\foundry`
was never modified.

## Status

| phase | question | decision |
|---|---|---|
| **Phase 1** | Design a preregistrable experiment for machine-created memory organization | **`REVISE_BEFORE_FREEZE`** |
| **Phase 2** | Can the syntax-only KA/KQ interface express task-conditional relevance at all? | **`ASSAY_NOT_VIABLE_SYNTAX_ONLY`** |

The organizer GA was **never run**. No preregistration was ever frozen. No
scientific effect for arm E was ever estimated. D-10 stopped at the Phase-2
capacity gate, which retired the syntax-only interface.

## Instrument identity (verified at the start of both phases)

Transferable-subset tree hash over 141 files, computed with the release
generator's own algorithm:

```
71feebc474be88696695ac653eaa3ea23fddb5a5e3f2d780ca63e7d13ed471d7
```

0 files modified, 0 missing, at both Phase 1 and Phase 2. `foundry/` is 67
`.py` files; the repo total of 17,809 `.py` lines was unchanged across both
phases. The full instrument gate passed 465/465 twice.

Note: `RELEASE_MANIFEST.json` in the workspace inventories 189 files rather
than the 146 recorded in `BOOTSTRAP.md`, and its own sha256 differs. This was
investigated in Phase 2 and is **benign**: the manifest was regenerated inside
`F:\SerendipityE` (its `git.commit` field records `<git unavailable>`) and the
generator's `EXCLUDE_DIRS` omits `d10`, so it swept in 43 `d10/` files plus
`BOOTSTRAP.md`. 141 + 43 + 1 + 4 `.pytest_cache` = 189. The same generator-scope
defect was already recorded for `.pytest_cache` in `BOOTSTRAP.md` §8.

## The one-paragraph result

Task-conditional relevance genuinely exists in the accumulated corpus and is
large — artifact×task interaction accounts for **69.3%** of relevance variance,
and the best-4 artifacts for two different tasks overlap only **4.5%** of the
time. A privileged oracle exploiting it lifts held-out exact-solve from
**0.042** (uniform memory) to **0.375**. But that structure is **not
recoverable from the information the declared interface admits**. Six
hand-designed admissible pairings all score *negative* capture of the available
conditional headroom; a learned RandomForest scores −0.134; and a fitted
bilinear model — a strict superset of anything `KA`/`KQ` + Hamming can express,
with no 64-bit limit and no step cap — captures **+3.3% in-sample** and
**−24.4% on held-out families**. The frozen capacity gate confirmed it
downstream: the best hand-built PP2 scored **0.000** against its own
query-shuffled twin at **0.021**, i.e. worse than the null and worse than
uniform retrieval.

Structurally: for PP2 to beat its query-shuffled twin, `KQ` must produce — from
input/output pairs alone — a fingerprint matching one `KA` produces from program
syntax alone. The only bridge between syntax and semantics is execution, which
this interface excludes by construction.

This is **not** evidence that endogenous relevance keying is impossible, and
says nothing about geometry, memory organization, concepts, or cognition. It
retires **this interface**.

## Layout

```
PHASE1_REPORT.md            Phase 1, all 15 charter deliverables
PHASE2_REPORT.md            Phase 2, all 16 charter deliverables
REVIEW_PACKET_PHASE1.txt    self-contained ASCII external-review packet
REVIEW_PACKET_PHASE2.txt    self-contained ASCII capacity-gate packet

prereg/PREREG_DRAFT.md      Phase-1 draft preregistration.
                            SUPERSEDED in ~30 places by adversarial review;
                            retained UNEDITED so the review record can be
                            audited against what was actually reviewed.
                            DO NOT FREEZE.

review/DESIGN_BRIEF.md      what the three hostile reviewers were given
review/REVIEW_RECORD.md     Reviewer A (ontology smuggling, circularity)
review/REVIEW_RECORD_B.md   Reviewer B (leakage, control adequacy)
review/REVIEW_RECORD_C.md   Reviewer C (statistics, power, cost)
                            38 findings, 15 blocking, each marked
                            CONFIRMED-BY-REPRODUCTION / CONFIRMED /
                            ACCEPTED-UNVERIFIED

preflight/                  Phase-1 probes p2..p11 (scripts, JSON, logs),
                            including the preserved p11 crash
lib/                        experiment code (Phase-2 repaired state)
tests/                      boundary, query-firewall and repair suites
repair/                     Phase-2 defect reproductions, pre-repair code
                            snapshots, and the pre-repair failure proof
phase2/                     dataset, capacity analyses, PP2 construction,
                            frozen GATE_SPEC + hash, gate results, diagnostics
```

## Reproduction

From `F:\SerendipityE`, using `.venv\Scripts\python.exe`:

```
.venv\Scripts\python.exe -m pytest tests -q          # instrument gate, 465
.venv\Scripts\python.exe d10\tests\test_boundary.py       # 9/9
.venv\Scripts\python.exe d10\tests\test_query_firewall.py # 13/13
.venv\Scripts\python.exe d10\tests\test_repairs.py        # 17/17
.venv\Scripts\python.exe d10\repair\verify_tests_fail_pre_repair.py
.venv\Scripts\python.exe d10\phase2\run_gate.py           # deterministic
```

`run_gate.py` verifies `GATE_SPEC.sha256` before doing anything and reproduces
`gate_result.json` byte-identically (`98de31b38258fb56…`).

## What a successor should know

1. **Do not reuse the syntax-only KA/KQ interface** without addressing the
   syntax/semantics bridge. A null under it is uninterpretable.
2. The Phase-1 preregistration's `E4` is **false as written** and was replaced
   by `E4′`, which admits that the 64-bit space, Hamming distance and top-k are
   experimenter-supplied.
3. Four defects were confirmed live in D-10's own code (supplied length
   channel, byte-lexicographic tie-break, PP1-equivalent fitness shaping,
   unbounded genotype growth) and two fail-open defects were found in the
   instrument's Court. All are documented with reproductions; the D-10 ones are
   repaired, the Court ones are **not** (the Foundry was not modified).
4. Absolute numbers from Phase 1 and Phase 2 are **not directly comparable**:
   the tie-break repair legitimately changed acquisition trajectories
   (history solves 11 → 6, corpus 3,962 → 4,110), though headroom improved
   (gate PP1 0.375 vs U 0.042).
