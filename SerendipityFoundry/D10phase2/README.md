# D10phase2 — Phase 2: defect repair and the syntax-only capacity gate

Archived from `F:\SerendipityE\d10\` (2026-09-01). Experiment-side material
only; the Prometheus Serendipity Foundry instrument was never modified or
upgraded — its 141-file transferable-subset hash
`71feebc474be88696695ac653eaa3ea23fddb5a5e3f2d780ca63e7d13ed471d7` was
re-verified at the start of this phase (0 modified, 0 missing).

**Phase 2 decision: `ASSAY_NOT_VIABLE_SYNTAX_ONLY`.**
Phase 1 lives in the sibling directory `../D10/`. Read `D10_INDEX.md` for the
combined story.

## The question this phase answered

Not "does endogenous relevance keying happen" but the prior question: *can the
declared syntax-only `KA`/`KQ` interface express useful task-conditional
relevance at all?* If not, a later evolutionary null would measure the
interface rather than the hypothesis.

## Repairs (all reproduced first, against the current code)

| id | defect | reproduction | repair |
|---|---|---|---|
| D1 | supplied genotype-length channel | `LDR R0` returned length exactly; word0 == len for 400/400 | `len(g)` removed from `artifact_words` |
| D2 | accidental selection channel | **re-derived in the real `acquire` loop**: injected parent-slot share 0.06137 (`0x00`) vs 0.00217 (`0xFF`) = **28.3×** | seeded-hash tie-break; post-repair ratio 0.80 |
| D3 | PP1-equivalent fitness shaping | arithmetic + ontology both confirmed | shaping struck; `objective.py` + fail-closed source audit |
| D4 | false compute parity | 3,139-byte genotype against a 1,000,000 limit | bound 1024; `vm_steps` first-class meter |
| D7 | wall-clock-dependent keys | `timeout_s=5.0` in the key path | `KEY_WALL_S=3600`; raises `NondeterministicKey` |

Phase 1's reported D2 magnitude (97.9% vs 0.0% of elite slots) was measured on
a *simulated* sort; the real-loop figure above **supersedes** it. That
re-derivation was required by the Phase-2 charter rather than assumed.

**Regression discipline:** 10/10 repair tests are *discriminating* — each fails
against the archived pre-repair code and passes after. Suites: repairs 17,
boundary 9, query-firewall 13 → **39/39 pass**.

## The measurement that decided the phase

Conditional relevance **exists and is large**: artifact×task interaction is
**69.3%** of relevance variance; top-4 sets for two tasks overlap **4.5%**;
downstream headroom available to any keying is **0.125** (uncond. oracle 0.073
→ cond. oracle 0.198 on dev).

It is **not recoverable from admissible syntax**:

| predictor | capture of the conditional headroom |
|---|---|
| six hand-designed admissible pairings | −0.234 … −0.328 |
| learned RandomForest, leave-one-family-out | −0.134 |
| **fitted bilinear model, in-sample** | **+0.033** |
| **fitted bilinear model, leave-one-family-out** | **−0.244** |

The bilinear model is a **strict superset** of the interface — since
`−popcount(x XOR y) = (x·y − 64)/2`, any `KA`/`KQ` + Hamming scheme is a
bilinear form — with no 64-bit limit and no step cap. It captures 3.3% even
when fitted and scored on the same tasks. **The failure is informational.**

## Frozen gate result

`GATE_SPEC.md` (sha256 `45ec9ae326fff87e…`) was frozen and hashed before any
gate evaluation and is verified by the runner at start.

| arm | held-out exact-solve |
|---|---|
| U — uniform corpus sample | 0.0417 |
| R2 — same keys, query-shuffled | 0.0208 |
| **PP2** | **0.0000** |
| PP1 — privileged oracle (calibration only) | 0.3750 |
| PN — planted negative | 0.0104 |

Primary: mean(PP2 − R2) = **−0.0208**, one-sided permutation **p = 1.0**,
bootstrap 95% CI [−0.052, 0.000], n = 24 held-out tasks. The planted negative
correctly fails; σ is family-disjoint (same-family rate 0.0); PP1 exceeds U by
0.33; cap-parity holds; bit-permutation invariance is 24/24; and the gate
reproduces **byte-identically** across two independent runs
(`98de31b38258fb56…`).

## Contents

```
PHASE2_REPORT.md           all 16 charter deliverables
REVIEW_PACKET_PHASE2.txt   self-contained ASCII capacity-gate packet
D10_INDEX.md               combined Phase 1 + Phase 2 index

phase2/GATE_SPEC.md        the frozen gate specification
phase2/GATE_SPEC.sha256    its hash, checked by run_gate.py at start
phase2/dataset.json        corpus (4,110 genotypes) + history/dev/gate tasks
phase2/relevance_dev.npy   4110 x 24 oracle relevance matrix (dev)
phase2/capacity_*.py|json  ceiling, pairing screen, bilinear superset
phase2/pp2_dev.py|json     the five PP2 candidates on the dev set
phase2/pp2_selection.json  the frozen candidate and its selection rule
phase2/run_gate.py         the gate runner
phase2/gate_result.json    the result (and gate_result_run1.json, identical)
phase2/diagnostics.*       post-freeze metric + bit-permutation diagnostics

repair/                    defect reproductions, PRE-REPAIR code snapshots,
                           and verify_tests_fail_pre_repair.py
lib/                       repaired experiment code (+ pp2.py, objective.py)
tests/                     boundary (9), query-firewall (13), repairs (17)
```

## Reproduction

From `F:\SerendipityE` with the paths restored, using `.venv\Scripts\python.exe`:

```
python d10\tests\test_repairs.py                     # 17/17
python d10\repair\verify_tests_fail_pre_repair.py    # 10/10 discriminating
python d10\phase2\run_gate.py                        # byte-identical result
```

## What this does and does not establish

It **retires this interface**: for PP2 to beat its query-shuffled twin, `KQ`
must produce from input/output pairs alone a fingerprint matching one `KA`
produces from program syntax alone, and the only bridge between syntax and
semantics is execution — excluded by construction.

It is **not** evidence that endogenous relevance keying is impossible, and says
nothing about geometry, memory organization, concepts, or cognition. Per the
Phase-2 charter no execution primitive, behaviour trace, or human-designed
semantic feature was added to rescue capacity. A syntax-only failure was
allowed to remain a failure.
