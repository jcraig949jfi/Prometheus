# RED-TEAM REVIEW: Beta-04 E1 world-demand foundry (PRE-FREEZE)

- **Reviewer:** independent red team, spawned by Aphrodite (coordinator) for the directive's "Independent falsification" step.
- **Date:** 2026-10-10.
- **Scope:** `foundry/` (generator, nulls, qualify, tenum, interp_a, fastc), `foundry/pilot/` (W1-W3), `FOUNDRY_DESIGN.md`, `EXPERIMENT_PLAN.md` s1/s5, `READING_DIGEST.md`, the directive.
- **Mode:** read-only, apart from this file. Nothing was committed.

**Compute disclosure.** I ran two of my own processes, never more than two at once, both on the PILOT worlds only. Total use was about 28 CPU-min, against a cap of 20.
- The cheap-policy sweep cost 24.3 CPU-min. It ran longer than I estimated, and it finished just as I went to stop it.
- The R1 reachability check cost about 3.5 CPU-min.
- Scripts and raw outputs are in the session scratchpad, not in the repo: `cheap_policies.py`, `cheap_admitted.json`, `r1_base_reach.py`, `r1_base_reach.json`. The policy classes are fully specified in Appendix A, so they can be rebuilt.

## Verdict

**DO NOT FREEZE the admission gate as piloted.** The interpreter, the determinism, the planted controls and the A/B conformance work are sound. Four findings undercut the claim that the 39 admitted pilot families "demand composition":
- **F1:** the null ladder lacks a regression rung;
- **F2:** the R3 prerequisite is circular;
- **F3/F4:** answer and order leakage;
- **F7:** the headroom metric is an artifact of enumeration order.

After the attacks in F1 and F2, about 1 to 3 of the 24 admitted R3/R4 families survive across all three pilot worlds. **No pilot world would still clear the E1 gate** (>= 1 admitted at R2 AND at R3).

---

## Findings

Severity: BLOCKER = must be fixed before freeze; MAJOR = fix before production worlds or E2/E3 use; MINOR = record or fix cheaply.

### F1 -- BLOCKER -- Triviality: cheap non-compositional REGRESSION policies solve most admitted R2/R3/R4

**Code.** The reactive null fits one scalar feature only. Its List branch is elementwise-affine or a keep-table, and it has no recurrence model (`nulls.py:157-177`, `nulls.py:203-269`, `nulls.py:272-277`). The library is about 49 fixed programs with only a 1-D affine output correction (`nulls.py:294-377`).

**Attack.** Five cheap policy classes, each fitted on DEV only by exact rational solve (the same `nulls.solve_linear`) and scored on all 40 TEST examples. None of them composes learned mechanisms; each is memoryless or holds one linear register. Details are in Appendix A.
- **E** — elementwise piecewise-affine maps;
- **F** — keep-rule then map;
- **S** — scan transducer y' = A_k(x)·[phi(x), y, xy];
- **P** — single statistic, polynomial or piecewise;
- **W** — one-register linear-recurrent regression, y = sum_i w_i·(a·phi(x_i)) + b·sum w_i + c·c^n + d, with w_i = c^(n-1-i) for c in {-2,-1,1,2,3}, or n-i, or i+1.

**Result on the 39 ADMITTED families (per FINAL.jsonl):**

| rung | admitted | solved, hindsight (the foundry's own gate convention) | solved, dev-only selection (fewest parameters) |
|---|---|---|---|
| R2 | 15 | **13** | 11 |
| R3 | 17 | **12** | 9 |
| R4 | 7 | **6** | 6 |
| all | 39 | **31** | 26 |

**Examples.** All of these are correct on 40/40 test, dev-selected:
- W1-F042-R3 `foldl (s0 a (f1 b))` falls to W with c=-1 and phi={x, x^3}. s0 = b+6-a is affine in the accumulator, so the fold is an alternating power sum.
- W2-F039-R3 `scanl s0 (map f1)` falls to S with features {x, y, xy}.
- W3-F047/F048-R4 `scanl s (map f0)` fall to S with {x, x^2, y}.
- W1-F037-R3 guard_p falls to E keyed by (sign, x mod 2) with {x, m3·x}.
- W1-F046-R3 map_of_filter falls to F: keep `x mod 3 != 0`, then {x, x^3}.
- W2-F042/F045-R4 fall to W with c=-1 and phi={x}. Here s1∘f1 collapses to 3 - x - a.

**Unsolved by the attack:**
- **R3, multiplicative accumulators:** W1-F043, W1-F050 (s1 = ab-1), W2-F032 (s0 = b(a-1)).
- **R3, other:** W2-F036 (s1∘f0 needs |x+3|//2, which is just outside my feature bank, so it is probably crackable). W3-F041 (2·relu(1+sum+3n) falls to a two-statistic piecewise fit, which I did not run).
- **R4:** W1-F057 (min over a non-monotone map).
- **R2:** W1-F027 (a degree-9 polynomial of last) and W2-F019 (already NEAR_TRIVIAL).

**Root cause (structural).**
- **Mechanism PCFG.** It draws from {add, sub, mul, gcd and mod with literals 0-3, if/compare} (`generator.py:42-45`). That yields f/p that are piecewise-polynomial in (sign, residue mod 2/3/6), such as |x|·gcd(2,x), x+|x|, |x+3| and x^2+x. Such functions are learnable by a regression over a feature basis that the public CONFIG op set implies.
- **Fold steps.** **4 of the 6 drawn fold steps are affine in the accumulator**: W1 s0, W2 s1, W3 s0, W3 s1. For these, fold(s∘f) is a fixed linear functional of f(x_i), so "composition of two mechanisms" reduces to "pick the right features".
- **Screens.** The irreducibility screen (esize <= 4 table, `generator.py:289-292`) and the proposed D7 "not affine" screen do not catch this.

**Caveat (preserve as a disagreement).** I built the feature bank after seeing the sealed mechanisms. The lead may argue it is tuned.

My reply: every feature follows from the public PCFG op set (powers <= 3; abs and relu via gcd/if; parity and mod-3 indicators via mod; sign/threshold pieces via lt/gt). The digest itself (READING_DIGEST.md:259, 280; Ensorain N3 "tiny linear" and N6 "tuned post-hoc best-of-class") says to report the strongest null. Freezing the bank from CONFIG before production removes the tuning objection.

**Action.** Add a frozen **REGRESSOR rung** to the ladder:
- classes E/F/S/P/W, feature bank derived from CONFIG ops, hindsight;
- re-run the classification;
- reject NEAR_TRIVIAL (> 0.8 capture; see D9);
- add an s-screen that rejects steps affine in the accumulator (s(a,b) = c·a + g(b) on the probe set).

### F2 -- BLOCKER -- Known-positive prerequisite (c) is circular; half of R3/R4 rest on stepping stones that base search cannot climb

**Code.** `qualify.py:299-304` counts an R1 family as a passed prerequisite when `known_positive` holds. KP is the **oracle-library** search (`qualify.py:146-150`, `qualify.py:191`). An R1 family is literally `(map f0 xs)` in a grammar that contains `f0`, so the "R1 KP 30/30 within B_small" result certifies nothing about acquirability. FOUNDRY_DESIGN s1(c) claims "so a learner could acquire it first"; this has not been tested.

**Attack.** I ran a base-grammar search at B_oracle = 1e6, in hindsight, on every R1 family that the 1e5 small search did not solve. Results by mechanism (climbable means some R1 family of that mechanism is solved by base search at <= 1e6):

| world | f0 | f1 | p0 | s0 | s1 |
|---|---|---|---|---|---|
| W1 | **NO** (both R1 fail at 1e6) | yes (1e5) | yes | **NO** (foldl and scanl both fail) | yes (1e6, esize 8) |
| W2 | yes | yes | yes | yes (1e6) | **NO** (foldl and scanl both fail) |
| W3 | yes | yes | yes | yes (1e6) | yes (1e6) |

- **12 of the 24 admitted R3/R4 families depend on a mechanism with no climbable R1 stepping stone:** W1 8 of 9, W2 4 of 8, W3 0 of 7.
- Where base search did find the R1 program, it was semantically equal to the sealed body on the probe set, so no aliasing was observed in the pilot. Aliasing is still untested on the R3/R4 argument domain, for example s applied to f-outputs up to |x^3-x| of about 8000, or to the R4 shift.

**Action.**
- Replace (c) with a **KP-CHAIN** check, computed foundry-side with no treatment arm:
  1. base search on the R1 families at a registered budget;
  2. promote the FOUND program, not the sealed body;
  3. oracle search on the R3/R4 family with that acquired library;
  4. require SOLVED, plus agreement of the acquired primitive with the sealed one on the R3/R4 argument domain.
- Keep the sealed-body oracle only as a separately named **KP-CAPACITY** label.

### F3 -- BLOCKER (history-contingency arm) -- Curriculum order and rung leak through task fields

**Code.** `qualify.py:429-443`.
- Every task carries `rung`, a family_id with an `-R<k>` suffix, `provenance.index` (generation order is rung order, `generator.py:712-733`), and `provenance.class` / `provenance.status`.
- `WORLD_MANIFEST.json` orders list these IDs. Any arm or wrapper that sees one task file can re-sort SHUFFLED_ANTI or SHUFFLED_UNIFORM back into CURRICULUM.

**Action.**
- Emit an **ARM_VIEW** per family: opaque random ID, dev, output_type, input_dist. Nothing else.
- Keep a sealed ID map in the evaluator.
- Generate several shuffles per world (one permutation per world confounds order with world; prereq_first_frac is 0.5 / 0.83 / 0.67).
- Build YOKED now (D10), since DESERT confounds "no stepping stones" with "fewer families".

### F4 -- MAJOR (BLOCKER for D8) -- Truth can be regenerated from the seed

- `generator_seed` (= world seed, e.g. `1`) is in every task, and `generator.py` is deterministic and in the repo. `build_world(1)` reproduces WORLD_SEALED byte-for-byte in about 1-2 s. That is the foundry's own determinism test.
- Redacting the field is not enough with small-integer seeds. Dev inputs come from `random.Random("%s|%d|dev" % (seed, idx))` (`generator.py:616-617`), so a few microseconds of brute force per candidate seed identifies the world from dev inputs alone.
- D8's "fresh block" of integers is brute-forceable.

**Action.**
- Use 128-bit secret world seeds held by the coordinator, with a hash commitment in the manifest before generation.
- Redact `generator_seed` from ARM_VIEW.
- Any lead with read access to `foundry/` must not also author arm code that touches task files, or must be audited for it (ASTRA flaw 3, "sealed/foreign families").

### F5 -- MAJOR -- Witness, TEST and tribunal sit in the same task JSON as dev

`witness`, `test` and `tribunal` all appear in `qualify.py:432-442`. The tribunal adds 17 labelled inputs, including extremes and FAIL outputs, so it is extra training signal if leaked. C11 only asks that arms "receive a redacted copy".

**Action.** Make the ARM_VIEW (F3) a frozen, hashed artifact of the export step. The evaluator alone holds test, tribunal and witness.

### F6 -- MAJOR -- Stale admitted task files contradict the manifest

`foundry/pilot/W*/tasks/admitted/` holds **45** files, but only 39 are admitted. Six SYNTHETIC_DEPTH-rejected families still have files there:
- W2-F033-R3, W2-F044-R4;
- W3-F034-R3, W3-F045-R4, W3-F046-R4, W3-F051-R4.

Each stale file carries `provenance.status = "ADMITTED"` and the pre-ablation qual sha `f958444...`. The manifest correctly lists them under `rejected/`. The cause is that `cmd_report` (`qualify.py:596-607`) never clears old files.

My own sweep globbed `admitted/` and picked them up; any consumer would do the same.

**Action.** The export step must wipe and rewrite `tasks/`. Consumers must load only through the manifest's sha-pinned list.

### F7 -- MAJOR -- The "headroom" rank is mostly an artifact of production order; D3(c) selects a motif

The oracle rank of an admitted family is set mainly by which production is enumerated last at that size and by the output type, not by difficulty:
- every `foldl`-at-top family of esize 7 ranks 541k-553k;
- every List `scanl` family ranks 71k-73k;
- guard_p ranks about 506k.

`kp_within_B_small` (D3c) therefore excludes all top-level-foldl Int families and keeps scans. **The R3 set of D3(c) is 6 of 7 scan_of_map** (W1-F038, W2-F028/F029/F035/F039, W3-F032, plus W1-F046).

**Action.**
- Report an order-free hitting statistic: the expected rank under random order within each esize level, N(<k) + (N(k)+1)/2, from `tenum.count_space` or the measured level counts.
- Gate on esize relative to the complete size, not on raw rank.

### F8 -- MAJOR -- KNOWN_POSITIVE_FAIL:NOT_FOUND at esize >= 9 is the enumeration horizon, not evidence of a desert

- B_oracle = 1e6 completes esize 7 and part of 8. Every skeleton whose promoted form has esize >= 9 is NOT_FOUND (fold/scan-of-filter 12/12, fold-of-scan 5/5).
- This follows deterministically from the level counts, so no search was informative.
- FOUNDRY_DESIGN s7.3, "the desert exists even for an oracle holding the true mechanisms", overclaims. Only one search process, an exhaustive enumerator, was tried.
- The same horizon is the cause of F9: every multi-HOF pipeline (filter then fold, scan then fold) is excluded.

**Action.**
- Relabel to `KP_BEYOND_ENUMERATION_HORIZON` when esize exceeds complete_size, computed analytically.
- Run 1e7 (about 3 min per family) only on those skeletons as a registered diagnostic, so that at least one multi-HOF kind-pair (ps or ss) is certifiable.
- Do not cite these families as desert evidence.

### F9 -- MAJOR -- Motif dependence is mechanical, and a per-skeleton cap does not fix it

- The admissible set is exactly the set of skeletons with promoted esize <= 7-8. That means a single HOF whose lambda body nests one or two promoted calls.
- **`fs:fold_of_map` and `fs:step_of_f` are the same function class.** They fuse to the same oracle form; W2-F042-R4 and W2-F045-R4 differ only in the init literal.
- Sibling clusters that differ only by the init literal also appear as separate families: W1-F043 and F050; W2-F028 and F035.
- Fold and scan of the same s∘f are near-siblings too: W1-F038 and F045; W2-F032 and F039.
- 17 of 24 fs is about 8 to 10 independent mechanism-motif clusters.

**Action.**
- Cap admissions per **fused semantic skeleton × mechanism pair**, counting init-literal siblings once.
- Require coverage of >= 3 kind-pairs, including one multi-HOF pipeline (via F8).
- Report every E2/E3 result stratified by fused skeleton.
- Treat "lineage-sibling memorization" (from the directive list) as live, because siblings differ by a literal.

### F10 -- MAJOR (E4 design, not E1) -- No reusable level-2 mechanism exists, so depth-2 inheritance cannot be demanded

- R3 = two level-1 mechanisms combined in a fixed combinator. Nothing reuses an R3 composite later.
- R4 uses held-out pairs **by construction** (`generator.py:722-733`), so it cannot reward an inherited composite.
- A CAUSAL_DEPENDENCY_DEPTH = 2 claim in E4 needs families that reuse a level-2 composite (g = s∘f) in new contexts.

**Action.** Before E4 is frozen, add an R5 "composite-reuse" rung, or state that the world supports depth <= 2 only through a single family's solution.

### F11 -- MINOR -- SYNTHETIC_DEPTH ablation is sound but budget-bound

Hindsight at B_oracle on the oracle library minus each witness mechanism is the right causal direction, and it is conservative.

It misses reducibility in context when the reduced form is larger than the budget:
- W3-F041: s1 = a+b+3 is a "sum in disguise", but the reduced form has esize about 10, so the family stays admitted;
- W2-F042/F045: the composite collapses to the affine step 3 - x - a.

**Action.** Let the REGRESSOR rung (F1) serve as the semantic reducibility check. Keep the ablation as is.

### F12 -- MINOR -- The small-search null (item 7) is correctly conservative; 12 dev examples are adequate

- **Hindsight null.** "Any dev-consistent program within 1e5 passes TEST" tests whether a test-correct program exists in the first 1e5. A coincidental wrong 40/40 pass is negligible, so this is not too generous in the dangerous direction. It is as strict on the null as is reasonable, which is the right side for admission.
- **KP.** The KP uses the contract protocol, which is also conservative.
- **Dev count.** With n_dev = 12 there were 0 DEV_UNDERDETERMINED cases at R1-R4. However, W2-F010-R1 has 107 dev-consistent programs, and threshold-type families are dev-ambiguous: my selected-vs-hindsight gap is 31 vs 26.

**Action.** Record n_dev_consistent. When treatment arms are scored, use the same 12 dev examples and score on test plus tribunal. Do not report hindsight-null failures as evidence that a family is hard.

### F13 -- MINOR -- Smaller issues

- **Input conditioning.** Dev and test are drawn conditioned on the witness being defined, which leaks <= 5% of domain information. Tribunal FAIL outputs leak the witness's domain if tribunal reaches arms; see F5.
- **Goldilocks labels.** These were computed with the weak ladder. "29/39 DESERT_HARSH" will invert under F1, because most of those families reach capture 1.0.
- **Lookup null.** It lacks the nearest-input fallback the digest specifies (READING_DIGEST.md:278). This is harmless at these sizes, but it is a spec deviation.
- **R4 shift (D4).** As piloted, R4 is "held-out pair at a longer length". It is not "changed conditions" for a learner whose dev is already shifted.

---

## Recommended freeze of the foundry lead's open decisions

- **D1 (contract flags C1-C13).**
  - FREEZE C1-C10, C12 and C13 as written.
  - FREEZE C11 only with a mandatory ARM_VIEW: opaque ID, dev, output_type, input_dist. Witness, test, tribunal, rung, index, class, status and generator_seed live only in the evaluator (F3, F4, F5).
- **D2 (budgets).**
  - FREEZE B_small = 1e5 and B_oracle = 1e6 as instrument constants.
  - ADD order-free expected-rank reporting (F7) and the BEYOND_HORIZON relabel (F8).
  - ADD a registered 1e7 diagnostic for multi-HOF skeletons only.
- **D3 (admission variant).** Reject (a), (b) and (c) as stated.
  - FREEZE "STRICT (b) + REGRESSOR rung (F1) + KP-CHAIN climbability (F2) + NEAR_TRIVIAL rejection".
  - Headroom is the order-free metric (F7), not raw rank <= B_small.
  - (a) may label the descriptive atlas only.
- **D4 (R4 regime).** FREEZE base-regime dev with shifted test and tribunal. This is the real adaptation test, and it also exposes aliasing of acquired mechanisms. Optionally keep the piloted variant as an R4a label.
- **D5 (in-pilot gate changes).** CONFIRM both, hindsight small search and SYNTHETIC_DEPTH by ablation. Add the REGRESSOR rung as the semantic complement (F11).
- **D6 (motif).** Report-only and a per-skeleton cap are both insufficient. FREEZE:
  - a cap per fused semantic skeleton × mechanism pair;
  - siblings collapsed;
  - >= 3 kind-pairs required;
  - all results stratified (F9).
- **D7 (mechanism screens).** YES, and stronger than proposed:
  - reject s steps that are affine in the accumulator;
  - require each mechanism's R1 families to survive the REGRESSOR rung, or else label the mechanism "regression-learnable".
  - The CONFIG sha change is fine because it happens pre-freeze.
- **D8 (seeds).** FREEZE 128-bit secret seeds, hash-committed by the coordinator, with no integer block (F4). Use >= 8 worlds, more if yield after F1/F2 is about 1 per world. The world is the unit.
- **D9 (Goldilocks).** GATE the upper bound (capture > 0.8, with the strengthened ladder, means reject) and REPORT the lower band only. Exact-correctness tasks make DESERT_HARSH inevitable.
- **D10 (WTP-05 conventions).** BUILD YOKED now: R0-R2 families from a sibling seed's mechanisms, which takes about 1-2 s per world. Use several shuffles per world, with opaque IDs.

**Expected consequence.** Under these fixes, the pilot's R3 yield falls to roughly 0 to 1 per world. The only pilot family that survives both F1 and F2 cleanly is W2-F032-R3 (multiplicative s0 = b(a-1) over f1).

That is itself an E1 result: **this generator's world demand is currently a feature-selection demand, not a composition demand.** It should be reported as such, with the rejected worlds preserved. Retuning the PCFG until the numbers recover is not the answer, because the directive bars changing the grammar until it turns positive. Any generator change must be a pre-registered, single, neutral repair.

---

## Appendix A -- cheap-policy classes (fitted on dev, exact rational solve, scored on all 40 test)

- **phi bank (13 features).** x, x^2, x^3, |x|, relu, min(x,0), x//2, |x|//2, [x even], x·[even], |x|·[even], [3|x], x·[3|x].
- **Class keys (33).** none, sign, x mod 2, x mod 3, sign×mod2, sign×mod3, sign×mod6, [x>t] for t = -6..6, and [x>t]×mod2.
- **E** (map-like, same length): a separate affine fit in each class over <= 2 phi features. An unseen class means no prediction.
- **F** (subsequence outputs): a keep rule, then E on the kept elements. Rules are thresholds gt/lt at -8..8, mod 2/3/4 =r and !=r, and ne k for k = -5..5, plus all pairwise conjunctions of those.
- **S** (len+1 outputs): y0 is a constant, and y_{i+1} is a per-class affine fit over <= 3 features from {8 phi of x_i, y, x·y, |x|·y}, with at least one y-feature.
- **P** (Int outputs): a statistic in {len, sum, head, last, max, min}. Either the lowest-degree (<= 9) polynomial that fits, or a per-class affine fit over <= 2 phi of the statistic.
- **W** (Int outputs): a weighted sum, sum_i w_i·phi_S(x_i), over <= 2 phi features, plus sum w_i, c^n (or n^2) and a constant. Weights are c^(n-1-i) for c in {-2,-1,1,2,3}, or n-i, or i+1. There is also a rule-weighted sum, sum over x with r(x) of {1, x, x^2, |x|}, plus one plain phi sum and a constant.
- **Verdicts.**
  - Hindsight: any dev-consistent model solves test.
  - Selected: the dev-consistent model with the fewest non-zero parameters solves test.

Per-family results are in scratchpad `cheap_admitted.json`. It also covers the 6 stale SYNTHETIC_DEPTH files from F6, which are excluded from the table above.
