# mathlib4 tactic Pareto distribution

**Computed:** 2026-05-05 | **Author:** Charon (one-shot diagnostic) | **For:** Aporia Study 12 + arsenal_meta proof-primitive question

## Headline

- **122,517 theorems** in LeanDojo Benchmark 4 v10 (mathlib4 commit `29dcec07`, 2024-07-02 snapshot).
- **49.77% of theorems are proved in TERM MODE** — no traced tactics. The rest of this report covers the tactic-mode subset only.
- **259,560 tactic invocations** across 61,544 tactic-mode theorems (≈4.22 invocations per theorem). 4,590 invocations contain a `<;>` combinator and contribute two head counts each, giving **265,168 total tactic head counts**.
- **231 distinct tactic heads observed.**
- **Top 10 heads = 69.8%, top 20 = 83.7%, top 50 = 94.6%** of all head counts. Strong heavy-tail Pareto.
- **Study 12's 10 functional categories (rewrite, simp_normalize, intro, apply, case_split, induct_on, decide_arith, ring_normalize, extensionality, contradiction) account for 97.99% of all head counts.** Cross-system convergent list **substantially confirmed** for Lean 4 mathlib4.

## Top 30 raw tactic heads

| Rank | Tactic | Count | % of head counts |
|---:|:---|---:|---:|
| 1 | `rw` | 49,209 | 18.56% |
| 2 | `simp` | 35,582 | 13.42% |
| 3 | `exact` | 30,950 | 11.67% |
| 4 | `have` | 16,891 | 6.37% |
| 5 | `refine` | 14,351 | 5.41% |
| 6 | `apply` | 10,185 | 3.84% |
| 7 | `intro` | 8,679 | 3.27% |
| 8 | `simpa` | 7,368 | 2.78% |
| 9 | `obtain` | 6,551 | 2.47% |
| 10 | `rcases` | 5,233 | 1.97% |
| 11 | `ext` | 5,182 | 1.95% |
| 12 | `rintro` | 5,113 | 1.93% |
| 13 | `simp_rw` | 4,825 | 1.82% |
| 14 | `rfl` | 4,407 | 1.66% |
| 15 | `rwa` | 3,253 | 1.23% |
| 16 | `let` | 3,214 | 1.21% |
| 17 | `by_cases` | 2,812 | 1.06% |
| 18 | `cases` | 2,794 | 1.05% |
| 19 | `convert` | 2,638 | 0.99% |
| 20 | `dsimp` | 2,601 | 0.98% |
| 21 | `constructor` | 2,344 | 0.88% |
| 22 | `congr` | 1,740 | 0.66% |
| 23 | `cases'` | 1,645 | 0.62% |
| 24 | `suffices` | 1,535 | 0.58% |
| 25 | `induction'` | 1,498 | 0.56% |
| 26 | `haveI` | 1,251 | 0.47% |
| 27 | `use` | 1,250 | 0.47% |
| 28 | `erw` | 1,160 | 0.44% |
| 29 | `induction` | 1,125 | 0.42% |
| 30 | `filter_upwards` | 1,082 | 0.41% |

(Full ranking in `mathlib4_tactic_pareto.json` → `raw_distribution`.)

## Category distribution (Study 12 mapping)

| Category | Count | % of head counts | Top constituents |
|:---|---:|---:|:---|
| `apply` | 87,600 | **33.04%** | `exact`, `have`, `refine`, `apply`, `obtain`*, `let`, `convert`, `suffices` |
| `rewrite` | 67,273 | **25.37%** | `rw`, `simp_rw`, `rfl`, `rwa`, `erw`, `subst`, `change`, `unfold` |
| `simp_normalize` | 49,316 | **18.60%** | `simp`, `simpa`, `dsimp`, `norm_cast`, `norm_num`, `aesop`, `push_cast` |
| `case_split` | 23,860 | **9.00%** | `obtain`, `rcases`, `by_cases`, `cases`, `constructor`, `cases'`, `rintro`** |
| `intro` | 14,321 | **5.40%** | `intro`, `rintro`, `intros`, `introv` |
| `extensionality` | 7,995 | **3.02%** | `ext`, `congr`, `funext`, `congr!`, `congrm` |
| `structural_admin` | 4,152 | 1.57% | `clear`, `set`, `swap`, `try`, `rotate_left`, `next`, `classical` |
| `decide_arith` | 3,500 | **1.32%** | `omega`, `linarith`, `positivity`, `gcongr`, `nlinarith`, `decide` |
| `induct_on` | 2,788 | **1.05%** | `induction'`, `induction`, `fin_cases` |
| `ring_normalize` | 1,686 | **0.64%** | `ring`, `ring_nf`, `field_simp`, `group` |
| `contradiction` | 1,488 | **0.56%** | `by_contra`, `exfalso`, `contrapose!`, `absurd` |
| `calc_chain` | 986 | 0.37% | `calc` |
| `domain_specific` | 158 | 0.06% | `mfld_set_tac`, `pgame_wf_tac`, `init_ring`, … |
| `__unmapped__` | 45 | 0.02% | 30 distinct singletons (`transitivity`, `cc`, `casesm`, …) |

\* `obtain` and `rintro` introduce hypotheses *and* do pattern destructuring; precedence in this analysis assigns them to `case_split` because the destructuring is the more discriminating operation. They are also legitimately in `intro`. See **honesty notes**.

\*\* `rintro` listed under `intro` in the raw table; under our category precedence it lands in `case_split`. The 5,113 `rintro` count appears in `case_split` aggregate.

**Sum of Study 12's 10 categories: 259,827 / 265,168 = 97.99% of head counts.** The remaining 2.01% is `structural_admin` (1.57%), `calc_chain` (0.37%), `domain_specific` (0.06%), and unmapped singletons (0.02%).

## Convergence with Study 12

**Verdict: substantial agreement, with quantitative refinements.**

1. **All 10 Study 12 categories are present** in the empirical distribution and together cover **97.99%** of tactic head counts.
2. **The dominant kernel is broader than 8–10 tactics.** The top-10 raw tactic heads cover only 69.8% of calls; the top-20 reaches 83.7%; coverage to 95% requires the top-50. The 10 *categories* cover the substrate; the 10 *individual tactics* do not.
3. **The biggest category is `apply` (33%), not `simp` or `rewrite`.** Lean 4 mathlib4 is more "structured proof construction" (`have`, `refine`, `exact`, `suffices`, `obtain`) than "rewrite-driven normalization." Coq's traditional emphasis on `apply`+`rewrite` is preserved; the mathlib idiom of building intermediate facts via `have` and discharging with `refine ⟨..., ?_, ...⟩` shows up clearly.
4. **`decide_arith` is smaller than expected (1.32%).** Mathlib4 does not lean heavily on `omega`/`linarith`/`decide` as automation; the bulk of work goes through `simp` and human-driven `apply` chains. This is a non-obvious finding worth noting for any "automation-first" proof-strategy hypothesis.
5. **`extensionality` (3.0%) is larger than `decide_arith` (1.3%).** `ext`/`congr`/`funext` are heavier-used than the decision procedures. Suggests mathlib4 invests more in definitional bookkeeping than in deciding closed-form goals.
6. **`contradiction` is small (0.56%).** Constructive bias holds — proof by contradiction is rare and concentrated in `by_contra`/`exfalso`.

## Implications for arsenal_meta

If Prometheus adds a proof-primitive sub-namespace, the data supports starting with the Study 12 list, with two refinements:

- **`apply` should be unpacked into sub-primitives** in the arsenal, not collapsed: `exact` (close goal), `have` (introduce intermediate), `refine` (apply with metavars), `suffices` (reduce target), `convert` (apply with congruence holes). Each is sufficiently distinct in usage and intent that lumping them obscures the design surface.
- **`rfl` deserves its own slot.** It's #14 raw at 1.66% of all calls and serves a distinct role from `rw` (closing reflexive goals vs. equational rewriting). Folding it into a generic `rewrite` callable is correct categorically but loses the most-frequent termination move.

Initial recommended set, ordered by empirical share within mathlib4:

| Order | Primitive (Study 12 name) | mathlib4 head share | Notes |
|---:|:---|---:|:---|
| 1 | `rewrite` | 25.37% | core: `rw`, `simp_rw`, `subst` |
| 2 | `simp_normalize` | 18.60% | `simp` + `dsimp` + `norm_cast` family |
| 3 | `apply_chain` | 33.04% | unpack: `apply`, `exact`, `refine`, `have`, `suffices`, `convert` |
| 4 | `case_split` | 9.00% | `cases`/`rcases`/`obtain`/`by_cases`/`if` |
| 5 | `intro` | 5.40% | `intro` + variants |
| 6 | `extensionality` | 3.02% | `ext`/`funext`/`congr` |
| 7 | `decide_arith` | 1.32% | `omega`/`linarith`/`decide` (small but high-value) |
| 8 | `induct_on` | 1.05% | `induction`/`fin_cases` |
| 9 | `ring_normalize` | 0.64% | `ring`/`field_simp` |
| 10 | `contradiction` | 0.56% | `by_contra`/`exfalso` |

A 10-callable proof-primitive sub-namespace covers ~98% of mathlib4's empirical tactic kernel.

## Honesty notes

1. **Source provenance.** Used HuggingFace mirror `1337xyz1337xyz/leandojo-benchmark4-v10` (sha `b4518b8f`), which mirrors the official LeanDojo Benchmark 4 v10 archive on Zenodo (record [12740403](https://zenodo.org/records/12740403)). Verified against the embedded `metadata.json`: `leandojo_version: 2.0.0`, `mathlib4 commit: 29dcec074de168ac2bf835a77ef68bbe069194c5`, creation `2024-07-02`. The canonical `kaiyuy/leandojo_benchmark_4` HF dataset cited by Study 12 was not searchable on HF at compute time; LeanDojo's primary distribution is via Zenodo and the v10 mirror is the closest publicly browsable equivalent.

2. **Split.** Used the `random` split (118,517 train + 2,000 val + 2,000 test = 122,517 theorems). Each theorem appears in exactly one of train/val/test; their union covers the benchmark once. The `novel_premises` split was not analyzed — it contains the same theorems re-partitioned to test premise generalization, so the tactic distribution would be identical.

3. **Term-mode coverage.** **49.77% of mathlib4 theorems in this benchmark are proved without any tactic invocation.** The Pareto reported here covers only the 50.23% tactic-mode subset. Any claim about "how mathlib4 is proved" must include this caveat: half of mathlib4 is term-mode, where the distribution is over Lean expressions rather than tactic calls. A separate analysis would be needed for term-mode primitives.

4. **Tactic head extraction.** Heads were extracted by regex on the first identifier of the (whitespace-stripped, bullet-stripped) tactic string after splitting on the `<;>` combinator. This is a **syntactic head**, not the elaborated tactic; a custom user tactic registered as `my_tac` appears as `my_tac` rather than as the underlying primitives it desugars to. mathlib4's `ghost_fun_tac`, `mfld_set_tac`, etc. exemplify this — they are reported as `domain_specific` and not decomposed.

5. **`<;>` combinator.** Tactic strings containing `<;>` (sequencing onto subgoals) contribute one head count for each side. 4,590 of 259,560 invocations (1.77%) used this pattern, contributing 5,608 extra head counts. We did NOT split on bare `;` to avoid slicing inside brackets. Multi-line tactic blocks (rare) contribute one head count per `<;>`-piece.

6. **Aliases collapsed.** Only `refl → rfl` (Lean 3 alias; defensive, did not appear in v10 data). `cases'`/`cases`, `intro`/`intros`/`introv`, `induction`/`induction'`, etc. were preserved as distinct heads in the raw distribution (each maps to the same Study 12 category). The reasoning: collapsing aliases would erase mathlib4's design choices about when to use which variant.

7. **Category-mapping precedence.** When a head plausibly fits multiple Study 12 categories, precedence assigns it to the more specific bucket: `ring_normalize` > `extensionality` > `rewrite` > `simp_normalize` > `induct_on` > `case_split` > `decide_arith` > `contradiction` > `intro` > `apply`. The mappings of borderline cases:
   - `obtain`, `rintro`, `rcases` → `case_split` (destructuring is more salient than introduction)
   - `convert`, `convert_to` → `apply` (apply-with-congruence-holes)
   - `simpa` → `simp_normalize` (simp + assumption; simp dominates)
   - `aesop`, `aesop_cat`, `fun_prop` → `simp_normalize` (broad-spectrum normalization)
   - `congr`/`congr!`/`congr_arg`/`congrm` → `extensionality` (per Study 12 table)
   - `linear_combination`, `gcongr`, `continuity`, `measurability` → `decide_arith` (decision procedures, even if domain-specific)
   - `noncomm_ring`, `group` → `ring_normalize` (algebraic normalizers; ring takes precedence over simp)
   - `wlog`, `nontriviality`, `choose` → `case_split` (case-reduction reasoning moves)
   - `if` (tactic-mode if-then-else) → `case_split`
   - `rfl`, `ac_rfl` → `rewrite` (closing reflexivity)
   - `classical`, `borelize`, `set_option`, `nofun` → `structural_admin` (admin/orchestration)
   - `calc` → its own `calc_chain` bucket (proof structure, not a tactic primitive in Study 12's sense)
   - `mfld_set_tac` and other `*_tac` macros → `domain_specific` (custom domain-bound tactics, not Study 12 primitives)

   Each of these is a judgment call; alternative mappings would shift category shares by 1–3 percentage points without changing the qualitative ranking.

8. **`structural_admin` is not in Study 12.** It is our own bucket for orchestration tactics (`swap`, `try`, `rotate_left`, `set`, `clear`, `classical`, …). Reporting it separately keeps the Study 12 convergence verdict honest: Study 12's 10 categories cover 97.99% of head counts; the residual 2.01% is mostly orchestration plus the `calc` proof-structure.

9. **Snapshot in time.** mathlib4 evolves continuously. This is a snapshot at commit `29dcec07` (2024-07-02), as captured by LeanDojo v2.0.0. Adoption of `aesop`, `omega`, `polyrith`, etc. has been changing rapidly; recomputing on a 2026 snapshot would shift specific frequencies but is unlikely to alter the Pareto shape or category ranking. The substrate-relevant invariant — that ~10 categories cover ≈98% of tactic usage — is the durable finding; the specific 18.56% rate for `rw` is not.

10. **Not peer-reviewed; not external-citable.** This is an internal Prometheus diagnostic, suitable for arsenal_meta design decisions. It is NOT a substitute for the formal LeanDojo paper analysis or for a peer-reviewed Pareto study. Per Study 12's calibrated negative finding: no peer-reviewed paper reports the empirical Pareto with confidence intervals; this artifact does not change that.

## Reproducibility

```powershell
# Fetch the random split + metadata (≈390 MB, ~1 minute on broadband)
python -c "from huggingface_hub import snapshot_download; \
  snapshot_download(repo_id='1337xyz1337xyz/leandojo-benchmark4-v10', \
  repo_type='dataset', \
  allow_patterns=['leandojo_benchmark_4/random/*','leandojo_benchmark_4/metadata.json'])"

# Adjust DATA_BASE in the script to point at your snapshot path, then:
python F:/Prometheus/charon/diagnostics/compute_mathlib4_pareto.py
```

Output:
- `F:/Prometheus/charon/diagnostics/mathlib4_tactic_pareto.json` — full distribution + category mapping + honesty notes.
- `F:/Prometheus/charon/diagnostics/MATHLIB4_PARETO_REPORT.md` — this document.

— Charon, 2026-05-05
