"""Compute mathlib4 tactic Pareto distribution from LeanDojo Benchmark 4 v10.

Source: https://huggingface.co/datasets/1337xyz1337xyz/leandojo-benchmark4-v10
        (mirror of https://zenodo.org/records/12740403, the official LeanDojo
        Benchmark 4 v10 archive).

mathlib4 commit: 29dcec074de168ac2bf835a77ef68bbe069194c5 (2024-07-02)
LeanDojo version: 2.0.0

Outputs:
  charon/diagnostics/mathlib4_tactic_pareto.json
  charon/diagnostics/MATHLIB4_PARETO_REPORT.md
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DATA_BASE = Path(
    r"E:\hf_cache\hub\datasets--1337xyz1337xyz--leandojo-benchmark4-v10"
    r"\snapshots\b4518b8fd6d2353f23793889700ed02a6bfc31fe"
)
SPLIT_DIR = DATA_BASE / "leandojo_benchmark_4" / "random"
OUT_JSON = Path(r"F:\Prometheus\charon\diagnostics\mathlib4_tactic_pareto.json")
OUT_MD = Path(r"F:\Prometheus\charon\diagnostics\MATHLIB4_PARETO_REPORT.md")


# Identifier head: alphanumeric, underscore, primes, optional `?` (e.g. `cases?`)
# Lean 4 tactic names like `nth_rw`, `simp_rw`, `rcases`, `cases'`, `omega`.
_HEAD_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*[?!]?")


def extract_heads(tactic_str: str) -> list[str]:
    """Extract tactic head identifiers from a tactic string.

    Splits on `<;>` (top-level combinator) and counts the head of each side.
    Newlines treated as continuation; we take the first head per non-empty
    physical-line segment in the rare multi-line case.

    Returns list of heads (may be empty if string is e.g. just `· · ·`
    or a term-mode expression we cannot classify).
    """
    if not tactic_str:
        return []
    # Strip surrounding parens at top level (rare).
    s = tactic_str.strip()
    # Drop leading bullet markers.
    while s.startswith(("·", "·")):
        s = s[1:].lstrip()
    # Split on `<;>`. We DO NOT split on `;` because Lean 4 rarely uses `;`
    # outside `<;>` and splitting risks slicing inside brackets.
    segments: list[str] = []
    for piece in s.split("<;>"):
        # Each piece may have multiple newline-separated sub-tactics in
        # the rare match/by-block-inside-tactic case. Take the first
        # non-empty line as the dominant head for that piece.
        for line in piece.splitlines():
            line = line.strip()
            # Strip leading bullet on each line too.
            while line.startswith(("·", "·")):
                line = line[1:].lstrip()
            if line:
                segments.append(line)
                break  # first non-empty line per <;>-piece
    heads: list[str] = []
    for seg in segments:
        # Skip leading parens.
        while seg.startswith("("):
            seg = seg[1:].lstrip()
        m = _HEAD_RE.match(seg)
        if m:
            heads.append(m.group(0))
    return heads


# ---- Normalization ---------------------------------------------------------
# Map raw heads to a "canonical" form. Goal: collapse aliases and minor
# variants without erasing meaningful distinctions. Each rule is auditable
# below.
NORMALIZE: dict[str, str] = {
    # rfl / refl: in Lean 4 only `rfl` is current; `refl` was a Lean 3 alias
    # and should not appear in mathlib4 v10 data, but we map defensively.
    "refl": "rfl",
    # cases and cases': cases' is a mathlib variant of cases that names
    # hypotheses. Keep separate because they have different ergonomics
    # but BOTH map to the same Study 12 category (case_split).
    # No collapse here.
    # introv subsumed under intro for raw normalization? No — introv is
    # genuinely a different tactic (intro until non-dependent). Keep.
    # Common typo / informal spellings: none expected in machine-traced data.
}


def normalize(head: str) -> str:
    return NORMALIZE.get(head, head)


# ---- Study-12 functional category mapping ---------------------------------
# Each entry maps a category name to the list of canonical heads that fall
# under it. Compiled into a reverse lookup for the actual mapping pass.
# Categories follow Study 12's table verbatim where possible.
CATEGORY_MEMBERS: dict[str, list[str]] = {
    "rewrite": [
        "rw", "rewrite",       # core rewrites
        "rwa",                 # rewrite-then-assumption
        "erw",                 # experimental (more aggressive defeq) rewrite
        "nth_rw", "nth_rewrite",
        "simp_rw",             # rewrite using simp lemmas (closer to rewrite than to simp normalization)
        "rw_mod_cast",         # rewrite with cast normalization
        "conv",                # explicit conv-mode rewriting
        "conv_lhs", "conv_rhs",
        "slice_lhs", "slice_rhs",   # category-theory rewriting
        "subst", "substs", "subst_vars",
        "change",              # definitional rewrite of goal
        "show",                # type-ascribe / definitional rewrite
        "unfold", "delta", "fold", "unfold_let", "unfold_projs",  # definitional unfolds
        "beta_reduce",
        "rcongr",              # repeated congruence rewrite
        "rfl",                 # closing reflexivity (a degenerate rewrite)
        "ac_rfl",              # AC-aware rfl
    ],
    "simp_normalize": [
        "simp", "simp!", "simp?", "simp_all", "simp_arith", "simp_intro", "simpa", "simpa?",
        "dsimp", "dsimp?", "dsimp!",
        "map_simp", "eval_simp", "C_simp", "matrix_simp", "pderiv_simp",  # simp variants for specific lemma sets
        "norm_num", "norm_num1", "norm_cast", "push_cast", "push_neg",
        "abel", "abel_nf",
        "trivial", "tauto", "tauto!",
        "aesop", "aesop_cat",  # automation that primarily simp-normalizes
        "fun_prop", "coherence",
    ],
    "intro": [
        "intro", "intros", "introv", "rintro", "intro_cases",
    ],
    "apply": [
        "apply", "apply?", "apply!", "apply_fun", "apply_assumption", "apply_rules",
        "exact", "exact?", "exacts", "exact_mod_cast",
        "refine", "refine'",
        "use", "use!", "existsi",
        "have", "have'", "haveI", "let", "letI",
        "assumption", "assumption!", "assumption'", "assumption_mod_cast",
        "convert", "convert_to",
        "specialize",
        "fapply", "eapply",
        "suffices", "rsuffices",   # introduce a target reduction (apply-style reasoning move)
        "replace",                 # replace a hypothesis (apply-with-fresh-name)
        "lift",                    # lift a value into a subtype
        "inhabit",                 # provide an inhabited instance
        "symm", "symm_saturate",   # apply Eq.symm
        "trans",                   # apply Eq.trans / Iff.trans
        "tfae_have", "tfae_finish",   # tfae proof structure (introduce hypothesis)
        "filter_upwards",          # filter-library apply with side conditions
        "fconstructor",            # constructor variant
        "peel",                    # quantifier peeling
        "show",                    # type ascription (already in rewrite; precedence resolves)
    ],
    "case_split": [
        "cases", "cases'", "rcases", "rcases'", "obtain", "obtain'",
        "cases_type", "injection", "injections",
        "by_cases",
        "if",                  # tactic-mode if-then-else (case-split on decidable)
        "split", "split_ifs",
        "match",               # match-as-tactic
        "constructor", "left", "right", "exists",
        "interval_cases",
        "nontriviality",       # case-split on triviality
        "wlog",                # without-loss-of-generality reduction
        "choose", "choose!",   # axiom-of-choice case-extraction
    ],
    "induct_on": [
        "induction", "induction'", "induct",
        "fin_cases",                     # finite case-induction
        "well_founded_recursion",
        "strong_induction", "strong_induction_on",
    ],
    "decide_arith": [
        "decide", "decide!", "native_decide",
        "omega", "omega_nat",
        "linarith", "nlinarith", "polyrith",
        "positivity", "sz_positivity",
        "bound",
        "linear_combination", "linear_combination'",
        "gcongr",                        # generalised congruence solver
        "monotonicity", "mono", "mono*",
        "continuity", "measurability",   # domain-specific decision procedures (continuity / measurability)
        "solve_by_elim", "solve",        # generic solve
        "qify", "zify",                  # lift goal to ℚ/ℤ then decide
    ],
    "ring_normalize": [
        "ring", "ring_nf", "ring1", "ring!",
        "field_simp",
        "group",                  # group-equational normalization
        "noncomm_ring",
        "compute_degree", "compute_degree!",   # polynomial degree normalization
    ],
    "extensionality": [
        "ext", "ext1", "ext_iff",
        "funext",
        "congr", "congr!", "congr_arg", "congrm",
    ],
    "contradiction": [
        "contradiction", "exfalso",
        "absurd",
        "by_contra", "by_contra!", "by_contra'",
        "contrapose", "contrapose!",
    ],
    # Catch-all for the long tail of structural/admin tactics that don't
    # cleanly fit Study 12's 10. Reported separately so we're honest about
    # what doesn't map.
    "structural_admin": [
        "skip", "sorry", "stop", "done",
        "first", "try", "repeat", "repeat'", "iterate", "any_goals", "all_goals",
        "focus", "case", "swap", "rotate_left", "rotate_right",
        "pick_goal", "pick_goal_later", "on_goal",
        "set", "set!", "clear", "clear!", "clear_value",
        "rename", "rename_i",
        "revert", "generalize", "generalize'", "generalize_proofs",
        "checkpoint",
        "with_reducible",
        "trace", "trace_state", "show_term",
        "infer_instance", "infer_param",
        "classical",            # opens classical-logic context
        "borelize",             # opens Borel-σ context (similar admin role)
        "nofun",                # closes goal by no-confusion (admin)
        "next",                 # case orchestration
        "set_option",           # local option setting in tactic mode
    ],
    # `calc` is a proof-structure keyword (introduces a chain), not a single
    # tactic primitive; we report it separately rather than forcing it into
    # one of Study 12's categories.
    "calc_chain": [
        "calc",
    ],
    # Domain-specific custom tactics (mostly `*_tac` named macros for one
    # corner of mathlib4 — Witt vectors, p-game well-foundedness, set
    # encoding, etc.). Reported separately so the long-tail composition is
    # legible. These are not in Study 12's table and shouldn't be forced
    # into it.
    "domain_specific": [
        "mfld_set_tac", "pgame_wf_tac", "bitwise_assoc_tac",
        "mem_tac", "to_encard_tac", "ghost_fun_tac", "map_fun_tac",
        "witt_truncateFun_tac", "pderiv_simp",
        "init_ring", "unit_interval", "pi_lower_bound", "pi_upper_bound",
        "subst_hom_lift", "ghost_calc", "isBoundedDefault", "valid",
    ],
}

# Build reverse lookup: head -> category. If a head appears in multiple
# categories above (e.g. `show`, `noncomm_ring`, `fin_cases`), the FIRST
# category in the iteration order wins. We define an explicit precedence:
PRECEDENCE = [
    # Most-specific buckets first so that overlapping aliases land in the
    # narrower category. Note `simpa` lives ONLY in simp_normalize; `show`
    # appears in both rewrite and apply and resolves to rewrite via this
    # ordering.
    "ring_normalize",
    "extensionality",
    "rewrite",
    "simp_normalize",
    "induct_on",
    "case_split",
    "decide_arith",
    "contradiction",
    "intro",
    "apply",
    "calc_chain",
    "domain_specific",
    "structural_admin",
]


def build_head_to_category() -> dict[str, str]:
    head_to_cat: dict[str, str] = {}
    for cat in PRECEDENCE:
        for head in CATEGORY_MEMBERS.get(cat, []):
            head_to_cat.setdefault(head, cat)
    return head_to_cat


HEAD_TO_CATEGORY = build_head_to_category()


# ---- Main pipeline --------------------------------------------------------
def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    splits = ["train.json", "val.json", "test.json"]
    raw_counter: Counter[str] = Counter()
    n_theorems = 0
    n_theorems_with_tactics = 0
    n_invocations = 0
    n_unparsed = 0
    multi_head_count = 0
    per_split_stats: list[dict] = []

    for split_file in splits:
        path = SPLIT_DIR / split_file
        with open(path, "r", encoding="utf-8") as f:
            records = json.load(f)
        split_inv = 0
        split_with_tac = 0
        for rec in records:
            n_theorems += 1
            tactics = rec.get("traced_tactics", [])
            if tactics:
                n_theorems_with_tactics += 1
                split_with_tac += 1
            for t in tactics:
                tactic_str = t.get("tactic", "")
                heads = extract_heads(tactic_str)
                if not heads:
                    n_unparsed += 1
                    continue
                if len(heads) > 1:
                    multi_head_count += 1
                # Each head counts once toward raw distribution (so a `<;>`
                # tactic produces two head counts).
                for h in heads:
                    h_norm = normalize(h)
                    raw_counter[h_norm] += 1
                # An "invocation" is the original tactic string. This is
                # the LeanDojo unit. We may count multiple HEADS per
                # invocation (when <;> is used).
                n_invocations += 1
                split_inv += 1
        per_split_stats.append({
            "split": split_file,
            "n_theorems": len(records),
            "n_theorems_with_tactics": split_with_tac,
            "n_invocations": split_inv,
        })

    # Raw distribution sorted by count desc.
    total_head_counts = sum(raw_counter.values())
    raw_dist = [
        {"tactic": h, "count": c, "fraction": c / total_head_counts}
        for h, c in raw_counter.most_common()
    ]

    # Category distribution.
    cat_counter: Counter[str] = Counter()
    unmapped: Counter[str] = Counter()
    for h, c in raw_counter.items():
        cat = HEAD_TO_CATEGORY.get(h)
        if cat is None:
            cat_counter["__unmapped__"] += c
            unmapped[h] += c
        else:
            cat_counter[cat] += c

    cat_dist = [
        {"category": cat, "count": c, "fraction": c / total_head_counts}
        for cat, c in cat_counter.most_common()
    ]

    # Reverse mapping for output (category -> sorted list of constituent heads
    # actually observed, with their counts).
    category_mapping_observed: dict[str, list[dict]] = {}
    for cat in PRECEDENCE + ["__unmapped__"]:
        members = []
        if cat == "__unmapped__":
            for h, c in unmapped.most_common():
                members.append({"tactic": h, "count": c})
        else:
            for h in CATEGORY_MEMBERS.get(cat, []):
                if h in raw_counter:
                    members.append({"tactic": h, "count": raw_counter[h]})
            members.sort(key=lambda d: -d["count"])
        if members:
            category_mapping_observed[cat] = members

    # Convergence-with-Study-12 check.
    study12_categories = {
        "rewrite", "simp_normalize", "intro", "apply", "case_split",
        "induct_on", "decide_arith", "ring_normalize", "extensionality",
        "contradiction",
    }
    observed_categories = {
        cat for cat in cat_counter
        if cat in study12_categories and cat_counter[cat] > 0
    }
    missing_from_observed = study12_categories - observed_categories
    convergence_str = (
        f"agreement: all {len(study12_categories)} Study 12 categories present"
        if not missing_from_observed
        else f"partial: missing categories {sorted(missing_from_observed)}"
    )
    # Top-10 / Pareto coverage.
    top10_share = sum(d["count"] for d in raw_dist[:10]) / total_head_counts
    top20_share = sum(d["count"] for d in raw_dist[:20]) / total_head_counts
    top50_share = sum(d["count"] for d in raw_dist[:50]) / total_head_counts

    output = {
        "computed_date": "2026-05-05",
        "data_source": "1337xyz1337xyz/leandojo-benchmark4-v10 (HF mirror of LeanDojo Benchmark 4 v10, Zenodo record 12740403)",
        "leandojo_version": "2.0.0",
        "mathlib4_commit": "29dcec074de168ac2bf835a77ef68bbe069194c5",
        "mathlib4_snapshot_date": "2024-07-02",
        "split_used": "random (train + val + test, union)",
        "n_theorems": n_theorems,
        "n_theorems_with_tactics": n_theorems_with_tactics,
        "fraction_term_mode": (n_theorems - n_theorems_with_tactics) / n_theorems,
        "n_invocations": n_invocations,
        "n_unparsed_invocations": n_unparsed,
        "n_multi_head_invocations": multi_head_count,
        "n_total_head_counts": total_head_counts,
        "per_split_stats": per_split_stats,
        "raw_distribution": raw_dist,
        "category_mapping": {k: [d["tactic"] for d in v] for k, v in category_mapping_observed.items()},
        "category_mapping_with_counts": category_mapping_observed,
        "category_distribution": cat_dist,
        "convergence_check": convergence_str,
        "pareto_summary": {
            "top_10_head_share": top10_share,
            "top_20_head_share": top20_share,
            "top_50_head_share": top50_share,
            "n_distinct_heads_observed": len(raw_counter),
        },
        "honesty_notes": [
            "Source is a HuggingFace mirror (1337xyz1337xyz/leandojo-benchmark4-v10) of the official LeanDojo Benchmark 4 v10 archive on Zenodo (record 12740403). Verified against metadata.json: leandojo_version 2.0.0, mathlib4 commit 29dcec074de168ac2bf835a77ef68bbe069194c5, creation 2024-07-02. The canonical kaiyuy/leandojo_benchmark_4 HF dataset was not searchable at compute time; LeanDojo's primary distribution is via Zenodo, not HF.",
            "Split: random (train+val+test = 122,517 theorems). The 'novel_premises' split was not analyzed; for tactic-frequency analysis the union of train+val+test of any split covers each theorem exactly once.",
            "Roughly 50% of mathlib4 theorems are PROVED IN TERM MODE (no traced_tactics). The Pareto here is over the tactic-mode subset only. The fraction_term_mode field captures this. Conclusions about 'how mathlib is proved' must include this caveat.",
            "Tactic head extraction: regex on first identifier of the (whitespace-stripped, bullet-stripped) tactic string. This is a syntactic head, NOT the elaborated tactic; e.g., a custom user tactic registered as `my_tac` will appear as `my_tac` not as the underlying primitives it desugars to.",
            "<;> combinator handling: when a tactic invocation contains `<;>` (sequencing onto subgoals), we count the head of BOTH sides. This means n_total_head_counts > n_invocations. The n_multi_head_invocations field reports how many invocations had this pattern.",
            "We do NOT split on `;` (only on `<;>`), to avoid slicing inside brackets like `simp [h₁, h₂]`. This may slightly under-count rare semicolon-sequenced tactics.",
            "Normalization aliases applied: refl→rfl. Lean 4 mathlib uses rfl exclusively; the alias is a defensive map. Other aliases (cases'/cases, intro/intros) are NOT collapsed because they preserve meaningful semantic distinctions while still mapping to the same Study 12 category.",
            "Category mapping is opinion-tinted. Notable judgment calls: (a) `rfl` placed under 'rewrite' (it closes a rewrite-style goal); (b) `aesop` and `aesop_cat` placed under 'simp_normalize' even though they're broader-spectrum automation; (c) `convert` and `convert_to` placed under 'apply' (they apply with congruence holes); (d) `congr*` family placed under 'extensionality' (per Study 12 table); (e) `linear_combination` placed under 'decide_arith'; (f) `noncomm_ring` appears in BOTH simp_normalize and ring_normalize lists — precedence resolution puts it in ring_normalize.",
            "Heads not in any category list go into '__unmapped__' bucket. This bucket's size and composition is the most informative debug signal: if it's small and structural-only (admin tactics like `swap`, `pick_goal`), the 8-10 category set is approximately complete; if it contains substantively-mathematical tactics, Study 12's list is missing categories.",
            "The 'structural_admin' category is OUR addition, not Study 12's. It captures admin/orchestration tactics (`swap`, `try`, `all_goals`, `set`, `clear`, ...) that are not derivation primitives in the Study 12 sense. Reporting it separately keeps the 10-category convergence check honest.",
            "This is a snapshot of mathlib4 at commit 29dcec07 (2024-07-02), as captured by LeanDojo v2.0.0. mathlib4 evolves continuously; `aesop` adoption, `omega` adoption, etc. have changed substantially over time. Recomputing on a newer snapshot would shift specific frequencies but is unlikely to change the qualitative Pareto shape or the category dominance pattern.",
        ],
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"  n_theorems = {n_theorems:,}")
    print(f"  n_invocations = {n_invocations:,}")
    print(f"  n_total_head_counts = {total_head_counts:,}")
    print(f"  distinct_heads = {len(raw_counter)}")
    print(f"  top10_share = {top10_share:.3f}")
    print(f"  unmapped_share = {cat_counter.get('__unmapped__', 0) / total_head_counts:.3f}")
    print(f"  convergence: {convergence_str}")


if __name__ == "__main__":
    main()
