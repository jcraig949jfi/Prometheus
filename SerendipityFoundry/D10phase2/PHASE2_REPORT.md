# D-10 Phase 2 — Capacity Gate: can the syntax-only interface express task-conditional relevance?

**DECISION: `ASSAY_NOT_VIABLE_SYNTAX_ONLY`**

The organizer GA was not run. No preregistration was frozen. No scientific
effect for E was estimated. The Foundry was not modified or upgraded.

---

## 1. Starting state and instrument identity

The instrument is byte-identical to the version D-10 began with.

| check | result |
|---|---|
| transferable-subset tree hash (141 files, generator's own algorithm) | `71feebc474be88696695ac653eaa3ea23fddb5a5e3f2d780ca63e7d13ed471d7` — **reproduces exactly** |
| `foundry/` files modified | **0** |
| files missing | **0** |
| `foundry/` .py count / total repo .py lines | 67 / 17,809 — unchanged from Phase 1 |

`RELEASE_MANIFEST.json` now inventories 189 files rather than Phase 1's 146,
and its own sha256 differs. Cause established, benign: the manifest was
**regenerated inside this workspace** (its `git.commit` field records
`<git unavailable>` for `F:\SerendipityE`), and the generator's
`EXCLUDE_DIRS` omits `d10`, so it swept in 43 `d10/` files plus
`BOOTSTRAP.md`. 141 instrument + 43 d10 + 1 BOOTSTRAP + 4 `.pytest_cache`
= 189. This is the same generator-scope defect `BOOTSTRAP.md` §8 already
recorded for `.pytest_cache`. **No upgrade occurred; no stop condition.**

---

## 2. Defect reproduction and repair

All reproductions were run against the *current* D-10 code, and D2 was
measured **inside the real `acquire` loop** rather than against a simulated
sort — Phase 1's explanation was not preserved as fact.

### D1 — supplied artifact-length channel · CONFIRMED, REPAIRED
`artifact_words` emitted `len(g)` as word 0, which the VM mirrors into `R0`,
so the two-byte program `LDR R0` returned the length exactly:

```
len   7 -> key   7      len  96 -> key  96
len  16 -> key  16      len 250 -> key 250
len  40 -> key  40      word0 == len(g) for 400/400 sampled genotypes
```

Repair: `len(g)` removed. Residual channels declared rather than asserted
away and measured in §5: the **word count** still varies with length
(intrinsic — StackVM has no stack-depth opcode), and the final partial word
is zero-padded so `len mod 8` is weakly encoded (a supplied packing
artifact).

### D2 — accidental selection channel · RE-DERIVED, REPAIRED
Measured in the real loop over 24,441 parent draws, injected genotypes
differing only in their leading byte:

| leading byte | share of parent slots |
|---|---|
| `0x00` | **0.06137** |
| `0xFF` | **0.00217** |
| ratio | **28.3×** (15.95× on a second task set) |

Mechanism, confirmed by inspection: `pop.sort(key=(-fitness, genotype_bytes))`
plus a tournament that broke ties by list position. At cold start essentially
all fitness is tied, so the early GA was a lexicographic sort on bytes.
This differs from Phase 1's reported magnitude (97.9% vs 0.0% of elite slots,
measured on a simulated sort); **the real-loop figure supersedes it**.

Repair: ties are broken by a seeded per-individual hash
`sha256(salt‖genotype)`, deterministic in the trial seed and pseudorandom
with respect to every admissible property. Post-repair ratio **0.80**.
Donor variation semantics untouched.

### D3 — ontology-smuggling fitness shaping · REMOVED (spec-level)
No organizer objective existed in code. The draft term
`+0.01 × mean best_train_fitness` is struck. `d10/lib/objective.py` now
defines the primary metric as the endpoint alone (`test_exact_solve_rate`)
and provides `audit_no_shaping()`, a fail-closed source audit over a
forbidden-term list. The capacity gate uses no shaped quantity anywhere.

### D4 — false compute parity · CONFIRMED, REPAIRED
Observed max genotype **3,139 bytes** at B=6400 against
`EngineLimits.max_genotype_bytes = 1,000,000`, with nothing bounding growth
and 567.5 VM steps per evaluation. Repair: `MAX_GENOTYPE_BYTES = 1024`
(operator runs unchanged, output truncated — total, since every byte string
is a legal program), and `vm_steps` is now a first-class field of
`AcqResult`, reported per arm.

### D7 — wall-clock-dependent key semantics · CONFIRMED, REPAIRED
`run_key` passed `timeout_s=5.0`, so a key program near the backstop yielded
a different key under load. Repair: `KEY_WALL_S = 3600` (can never bind
before `KEY_MAX_STEPS = 300`), and a wall halt now raises
`NondeterministicKey` instead of returning a key.

---

## 3. Regression testing

`d10/repair/verify_tests_fail_pre_repair.py` loads the archived pre-repair
modules and re-runs each predicate: **10/10 discriminating** — every test
fails against pre-repair code and passes after.

| suite | checks | result |
|---|---|---|
| `test_repairs.py` | 17 | all pass |
| `test_boundary.py` | 9 | all pass |
| `test_query_firewall.py` | 13 | all pass |

No existing assertion was weakened; no Foundry test or source was touched.

---

## 4. Artifact-side admissible-observation inventory

After D1, `KA` receives exactly: the genotype's first 192 bytes packed as up
to 24 little-endian 64-bit words, with the first 8 words mirrored into
`R0..R7`. Nothing else — no execution statistic, no length field, no
histogram, no opcode decode, no admin metadata, no chronology.

---

## 5. Reconstruction probes

Given the best possible shot (full byte histogram, opcode histogram, word
count, padding, mean/std; a RandomForest; 4-fold CV) — none of which `KA`
could compute within 300 steps.

| nuisance variable | accuracy | baseline | lift | verdict |
|---|---|---|---|---|
| genotype length | r² = **0.863** | 0.0 | — | **INTRINSIC** (word count + padding) |
| source history task | **0.919** | 0.033 | **+0.886** | **INTRINSIC** (clonal final populations) |
| source family | 0.314 | 0.129 | +0.185 | INTRINSIC, weak |
| restart phase | 0.359 | 0.334 | +0.025 | not reconstructible |
| corpus-admission source | 0.363 | 0.527 | −0.164 | not reconstructible |
| solver status | 0.996 | 0.996 | −0.000 | not reconstructible |
| **family from LENGTH ALONE** | **0.106** | 0.129 | **−0.023** | **worse than chance** |

Interpretation, drawing the distinction §5 requires: the one channel that
was **experimenter-supplied** (length) is removed, and length alone predicts
family *worse than the majority baseline*. What remains is **intrinsic**: a
genotype's syntax genuinely reveals which search run produced it, because
each history search's final population is clonal. That is a legitimate
property of accumulated experience, not leakage.

**And it is the wrong signal.** Run identity is 0.919 reconstructible while
family is only 0.314 — the corpus's syntactic structure encodes *which
search produced this artifact*, not *what it computes*, and relevance depends
on the latter.

---

## 6. Query-side firewall recheck

13/13 pass after repairs: `task_id` inaccessible (300/300 random `KQ`
programs agree across two tasks with identical train evidence and different
`task_id`), test examples absent from the encoding entirely, family identity
and generator parameters absent, `TaskEvidence` exposes no chronology field
and still rejects injected oracle fields, and identical train evidence
yields an identical `KQ` input regardless of oracle-side identity.

---

## 7. Capacity ceiling — the measurement that decides this phase

Run on DEV only. PP1 vs U proves useful memories exist; it does **not**
prove that *which* memory is useful depends on the query. That is what a
`PP2 > R2` result would require, so it was measured directly.

**Task-conditional relevance genuinely exists, and is large:**

| quantity | value |
|---|---|
| artifact main effect | 9.9% of relevance variance |
| task main effect | 20.8% |
| **artifact × task interaction** | **69.3%** |
| mean top-4 overlap between two tasks | **0.045** |
| mean top-4 overlap with the global-best set | **0.021** |
| downstream UNIFORM | 0.0000 |
| downstream ORACLE_UNCOND (one fixed global top-4) | 0.0729 |
| downstream ORACLE_COND (per-task oracle = PP1) | 0.1979 |
| **conditional headroom available to any keying** | **0.125** |

**But it is not predictable from admissible syntax-only information.**
Capture = (top-4 relevance − global-best) / (conditional oracle − global-best):

| admissible pairing | capture |
|---|---|
| byte-value bitset vs output-value bitset (all visible bytes) | −0.234 |
| same, restricted to the 24 bytes the VM can afford | −0.234 |
| byte-value bitset vs output+input bitset | −0.328 |
| exact byte-set ∩ output-set overlap | −0.258 |
| byte-histogram vs output-histogram cosine | −0.286 |
| opcode set vs outputs mod 33 | −0.309 |
| learned RandomForest, leave-one-family-out | −0.134 |
| **fitted bilinear model, in-sample** | **+0.033** |
| **fitted bilinear model, leave-one-family-out** | **−0.244** |

The bilinear model matters most. Because
`−popcount(x XOR y) = (x·y − 64)/2` for ±1 bit embeddings, **any** KA/KQ +
Hamming scheme is a bilinear form in the two sides' embeddings. A fitted
bilinear model over rich admissible features is therefore a **strict
superset** of the declared interface — no 64-bit limit, no step cap, not
restricted to programs a human can write. It captures **3.3% of the
conditional span even when fitted and evaluated on the same tasks**, and
goes negative on held-out families.

**The failure is informational, not a failure of ingenuity or of the step
cap.**

---

## 8. PP2 construction methodology and candidate accounting

Every candidate obeys the same instruction set, step cap, key width,
Hamming geometry, top-k rule, encodings and resource limits an evolved
organizer would. No execution primitive, no behaviour trace, no
human-designed semantic feature. Each is packaged as a **real organizer
genome** (2-byte header + KA + KQ) and driven through the same
decode → build → query path.

Serious candidates evaluated on DEV: **5** (plus 6 offline pairings, one
learned RF, and one bilinear superset in §7).

| # | candidate | rationale | KA steps/artifact | KQ steps | distinct keys | PP2 | R2 | PP2−R2 |
|---|---|---|---|---|---|---|---|---|
| C1 | byte-value bitset(3 words) × output bitset(8) | program literals vs task output values, mod 64 | 267 | 95 | 2865 | 0.0208 | 0.0104 | +0.0104 |
| C2 | byte-value bitset(2) × output bitset(8) | shorter scan, step headroom | 179 | 95 | 2552 | 0.0208 | 0.0104 | +0.0104 |
| C3 | opcode bitset(3) × output bitset(8) | decoded opcodes drive behaviour | 300 (capped) | 95 | 2613 | 0.0000 | 0.0104 | −0.0104 |
| C4 | constant bitset(3) × output bitset(8) | only bytes following `PUSH1` | 300 (capped) | 95 | **1** | 0.0000 | 0.0000 | 0.0000 |
| **C5** | **byte-value bitset(3) × output+input bitset(5)** | **query signature uses inputs too** | **267** | **98** | **2865** | **0.0208** | **0.0000** | **+0.0208** |

C4 degenerates: the `EQ`-gated multiply plus the step cap collapses the whole
corpus to one key, so retrieval reduces to the tie-break hash (≈ arm U).

**A bug in my own evaluation, found and fixed:** an earlier dev run passed
bare `KA` programs to `build_organization`, which decodes its argument as a
*genome* and therefore silently truncated them — C1 and C2 produced
byte-identical keys for all 4110 artifacts, and C4 showed a spurious
+0.0417. That run is discarded; all results above are from the corrected
genome-packaged path. `make_genome` now asserts an exact round-trip.

Selection rule, pre-declared and applied to DEV only: maximise dev
(PP2 − R2), then dev PP2, then candidate order. **C5 selected.**

---

## 9. Frozen gate specification

`d10/phase2/GATE_SPEC.md`, sha256
`45ec9ae326fff87e05e0d0337b28926ba4232de5eaae13ba7ba91d774317f27c`,
frozen and hashed **before** any gate evaluation and verified by the runner
at start. It fixes the corpus, the 24 held-out gate tasks (family members
7–9, disjoint from history 0–3 and dev 4–6), acquisition seeds, retrieval
seeds, k=4, B_EVAL=400, step limits, cost units, the family-block
derangement procedure, `DELTA_MIN = 0.03`, the statistical procedure, and
the invalidation conditions. `DELTA_MIN` was set from the DEV conditional
headroom (0.125) via the same 25% rule Phase 1 preregistered — **before**
the gate ran.

---

## 10. Gate results (24 tasks × 4 seeds = 96 trials per arm)

| arm | test-exact solve rate |
|---|---|
| `U` uniform corpus sample | 0.0417 |
| `R2(PP2)` same keys, query-shuffled | 0.0208 |
| **`PP2`** | **0.0000** |
| `PP1` privileged oracle (calibration only) | **0.3750** |
| `PN` planted negative | 0.0104 |

**Primary:** mean(PP2 − R2) = **−0.0208**, one-sided sign-flip permutation
**p = 1.0**, bootstrap 95% CI **[−0.052, 0.000]**, n = 24 tasks.

PP2 is worse than its own query-shuffled twin and worse than uniform
retrieval.

---

## 11. Planted negative

`PN` = PP2's artifact keys with a constant `KQ` (`PUSH1 0`), so retrieval is
query-independent by construction while preserving key width, geometry and
all retrieval mechanics. **PN − R2 = −0.0104, p = 1.0 — correctly fails.**
The gate is discriminating.

---

## 12. Cost accounting

| arm | evaluations | VM steps | steps/eval | max evals per trial |
|---|---|---|---|---|
| U | 35,212 | 22,369,077 | 635.3 | 400 |
| R2 | 36,702 | 17,687,843 | 481.9 | 400 |
| PP2 | 36,740 | 19,207,022 | 522.8 | 400 |
| PP1 | 20,844 | 7,939,110 | 380.9 | 400 |
| PN | 36,473 | 19,856,433 | 544.4 | 400 |

**Cap-parity holds** (every arm ≤ B_EVAL = 400). Key-computation cost: KA
267 steps/artifact, KQ 98 steps — both within `KEY_MAX_STEPS = 300`.
Steps-per-evaluation varies 381–635 across arms, which is exactly why D4
made VM steps a first-class meter: matched evaluation counts do **not** mean
matched compute.

---

## 13. Decision against the frozen pass criteria

| criterion | required | observed | met |
|---|---|---|---|
| 1. effect ≥ `DELTA_MIN` = 0.03 | ≥ +0.03 | −0.0208 | **NO** |
| 2. permutation p < 0.05 | < 0.05 | 1.0 | **NO** |
| 3. no boundary violation | all suites pass | 39/39 pass, no `NondeterministicKey` | yes |
| 4. no cost violation | cap-parity | all arms ≤ 400 | yes |
| 5. planted negative fails | must fail | fails (p = 1.0) | yes |
| 6. nuisance check | only if 1–5 hold | not reached | n/a |

Invalidation conditions: σ realised same-family rate **0.0**; PP1 (0.375)
exceeds U (0.042); gate disjoint from dev; no arm exceeded budget; no
nondeterministic key. **The gate is valid.**

Gate determinism: two independent runs produced **byte-identical** output
(`98de31b38258fb56…`).

---

## 14. Post-freeze diagnostics

- **Bit-permutation invariance: 24/24 tasks return identical top-k** under a
  shared permutation of the 64 bit positions. The implementation is correct.
- Descriptive reinterpretation of the identical PP2 keys under alternative
  supplied comparisons: mean top-4 overlap with Hamming is 0.031 (unsigned
  numeric distance) and 0.042 (common-prefix length). The keys are
  Hamming-specific. **Not used to revisit the verdict** — a failed Hamming
  PP2 is not rescued by an alternative metric.

---

## 15. Unresolved contamination threats and caveats

1. **The operating point shifted under legitimate repair.** The D2 tie-break
   repair changed acquisition trajectories: history test-solves fell from
   Phase 1's 11 to **6**, and corpus size moved 3,962 → 4,110. Headroom did
   **not** disappear — PP1 on the gate set is 0.375 against U 0.042, better
   than Phase 1's 0.344 vs 0.031 — so no stop condition fired. But Phase-1
   absolute numbers are not directly comparable to Phase-2 ones.
2. **The environment's output bound is enforced on probe inputs, not on the
   sampled cases.** Some train/test outputs therefore fall outside [0,255].
   This was discovered mid-phase and is recorded, not repaired.
3. **`n_examples` and `arity` remain in the `KQ` encoding** as words 0–1 and
   occupy two registers. Both are constant across every task in this
   experiment, so they leak nothing, but they waste half the cheap register
   channel. Deliberately **not** changed, because removing them would have
   been a capacity-enhancing interface change made after seeing PP2 fail.
4. **`KA` sees only the first 192 bytes**; the median corpus genotype is 47
   bytes so this rarely binds, but it does for the tail.
5. **Intrinsic run-identity reconstructibility (0.919)** is legitimate but
   would need controlling in any future design that gets past this gate.
6. **The bilinear superset argument assumes** ±1 bit embeddings and rich but
   finite feature sets; it is a very strong upper bound, not a proof.
7. **An operational slip:** two gate processes ran concurrently for one
   execution. Because the gate is fully deterministic the outputs are
   byte-identical, verified by re-running; no result depends on it.

---

## 16. Decision

**`ASSAY_NOT_VIABLE_SYNTAX_ONLY`**

After a serious bounded construction effort — 5 mechanism-faithful hand-built
KA/KQ pairs, 6 offline admissible pairings, a learned RandomForest, and a
fitted bilinear model that is a strict superset of the declared interface —
no admissible PP2 demonstrated the required effect, while the gate itself
remained valid: PP1 exceeds U by 0.33 on the gate set, the planted negative
fails as required, the derangement is family-disjoint, cap-parity holds, and
the whole gate reproduces byte-identically.

**Why it fails, stated structurally.** For `PP2 > R2`, `KQ` must produce —
from input/output pairs alone — a fingerprint that matches one `KA` produces
from program syntax alone. The only bridge between syntax and semantics is
execution, which this interface excludes by construction. The measurements
agree: conditional relevance is abundant (69% interaction, 4.5% top-4
overlap between tasks) and simply not recoverable from admissible syntax
(bilinear superset captures 3.3% in-sample, −24% held out). Meanwhile the
syntax that *is* highly readable encodes which search run produced an
artifact (0.919), not what it computes.

**Interpretation.** This is **not** evidence that endogenous relevance keying
is impossible, and it says nothing about endogenous geometry, memory
organization, concepts, or cognition. It retires **this interface**: a
future evolutionary null under the syntax-only KA/KQ design would have been
uninterpretable, because the mechanism it was meant to detect cannot be
expressed within it.

Per the Phase-2 charter §15, no execution primitive, behaviour trace, or
human-designed semantic feature was added to rescue capacity. A syntax-only
failure is allowed to remain a failure.
