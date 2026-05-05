"""Tink 2 (Tier B) — F043 reproduction with CAS Layer C + η_trace.

Demonstrates:
  1. The aggregate-vs-Pareto disagreement claim from v2 (carried over
     from v1 cheap-path; v1 verdict: VALIDATED).
  2. CAS Layer C provides a symbolic certainty layer that confirms
     basis-projection verdicts at zero numerical noise.
  3. η_trace identifies AST steps that information-collapse, providing
     a structural signal complementary to η_inverse_model.

Run: `PYTHONIOENCODING=utf-8 python tink_2.py`
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import sympy

from candidates import CANDIDATES
from scorer import (
    score_candidate, pareto_front, ALPHA, BETA,
)
from synthetic_bsd import generate, materialize_basis
from trace_eta import W_EXTERNAL, W_INTERNAL


# ---------- atom symbols for CAS Layer C -----------------------------------

# In-basis atoms: BSD ingredients (rank 0 with Reg = 1)
BASIS_ATOM_NAMES = ["log_omega", "log_prod_cp", "log_sha", "log_tor", "log_L"]

# Off-basis atoms: not part of BSD identity
OFF_BASIS_ATOM_NAMES = ["log_j", "log_disc", "log_N"]

ALL_ATOM_NAMES = BASIS_ATOM_NAMES + OFF_BASIS_ATOM_NAMES


def make_atom_symbols() -> dict:
    """Build SymPy Symbol map for all atoms used in candidates."""
    return {name: sympy.Symbol(name) for name in ALL_ATOM_NAMES}


# ---------- run ------------------------------------------------------------

def run_tink_2(n: int = 1000, seed: int = 42) -> dict:
    print("=" * 80)
    print("Tink 2 (Tier B) — F043 reproduction with CAS Layer C + η_trace")
    print(f"  Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"  n = {n}, seed = {seed}")
    print(f"  Basis atoms (CAS): {BASIS_ATOM_NAMES}")
    print(f"  Aggregate: α · L_expr − β · |z|   (α={ALPHA}, β={BETA})")
    print(f"  Pareto axes: (1 − basis_projection, affordance_gain, reconstructability)")
    print(f"  η_composite = {W_EXTERNAL} · η_inverse + {W_INTERNAL} · η_trace")
    print("=" * 80)

    data = generate(n=n, seed=seed)
    basis = materialize_basis(data)
    atom_symbols = make_atom_symbols()

    rng = np.random.default_rng(seed + 1)
    baseline_features = rng.standard_normal((n, 2))

    print(f"\nScoring {len(CANDIDATES)} candidates...\n")
    scored = [
        score_candidate(c, data, basis, BASIS_ATOM_NAMES, atom_symbols, baseline_features)
        for c in CANDIDATES
    ]

    name_to_class = {c["name"]: c["class"] for c in CANDIDATES}
    by_aggregate = sorted(scored, key=lambda s: s["aggregate_score"])
    pf = pareto_front(scored)
    pf_names = {c["name"] for c in pf}

    return {
        "data_n": n,
        "data_seed": seed,
        "scored": scored,
        "name_to_class": name_to_class,
        "by_aggregate": by_aggregate,
        "pareto_front": pf,
        "pareto_front_names": pf_names,
    }


def print_results(results: dict) -> None:
    scored = results["scored"]
    by_aggregate = results["by_aggregate"]
    pf = results["pareto_front"]
    pf_names = results["pareto_front_names"]
    name_to_class = results["name_to_class"]

    # ---- score table -----------------------------------------------------
    print("\n" + "=" * 110)
    print(
        f"{'name':<24}{'class':<14}{'tok':>5}"
        f"{'|z|':>8}{'BP':>7}{'src':>8}"
        f"{'aff':>7}{'η_inv':>7}{'η_tr':>6}{'η_c':>6}{'agg':>9}"
    )
    print("-" * 110)
    for s in scored:
        on_pf = "*" if s["name"] in pf_names else " "
        bp_src = "CAS" if s["basis_projection_source"] == "CAS_Layer_C" else "L_B"
        eta_tr = min(s["eta_trace_A"], s["eta_trace_B"])
        print(
            f"{s['name']:<24}{s['class']:<14}{s['n_tokens']:>5}"
            f"{s['z_abs']:>8.2f}{s['basis_projection']:>7.3f}{bp_src:>8}"
            f"{s['affordance_gain']:>7.3f}{s['eta_inverse']:>7.3f}"
            f"{eta_tr:>6.2f}{s['reconstructability']:>6.2f}{s['aggregate_score']:>9.2f}  {on_pf}"
        )
    print("(* = on Pareto front; BP = basis_projection;"
          " src = CAS or Layer B regression)")

    # ---- CAS layer detail ------------------------------------------------
    print("\n" + "=" * 80)
    print("CAS LAYER C — per-side reduction:")
    print("-" * 80)
    for s in scored:
        if s["basis_projection_source"] == "CAS_Layer_C":
            print(
                f"  {s['name']:<24}  E_A: {s['cas_marker_E_A']:<22}  "
                f"E_B: {s['cas_marker_E_B']:<22}"
            )
        else:
            print(
                f"  {s['name']:<24}  fall through to Layer B  "
                f"(E_A: {s['cas_marker_E_A']}; E_B: {s['cas_marker_E_B']})"
            )

    # ---- aggregate top-K --------------------------------------------------
    print("\n" + "=" * 80)
    print("TOP 5 BY AGGREGATE SCALAR (lower = better):")
    print("-" * 80)
    for i, s in enumerate(by_aggregate[:5], 1):
        on_pf = "✓ on Pareto" if s["name"] in pf_names else "✗ NOT on Pareto"
        print(
            f"  {i}. {s['name']:<24} [{s['class']}]  "
            f"agg={s['aggregate_score']:>+8.2f}  |z|={s['z_abs']:>7.2f}  "
            f"BP={s['basis_projection']:.3f} ({s['basis_projection_source']})  {on_pf}"
        )

    # ---- pareto front -----------------------------------------------------
    print("\n" + "=" * 80)
    print(f"PARETO FRONT (substrate-value triple, {len(pf)} non-dominated):")
    print("-" * 80)
    for s in pf:
        print(
            f"  {s['name']:<24} [{s['class']}]  "
            f"novelty={s['pareto_novelty']:>5.3f}  "
            f"usefulness={s['pareto_usefulness']:>6.3f}  "
            f"faithfulness={s['pareto_faithfulness']:>5.3f}"
        )

    # ---- disagreement ------------------------------------------------------
    print("\n" + "=" * 80)
    print("DISAGREEMENT ANALYSIS:")
    print("-" * 80)
    f043_in_top5 = sum(
        1 for s in by_aggregate[:5] if s["class"] == "F043_family"
    )
    f043_on_pf = sum(1 for s in pf if s["class"] == "F043_family")
    cas_decided_count = sum(
        1 for s in scored if s["basis_projection_source"] == "CAS_Layer_C"
    )
    print(
        f"  F043_family in top-5 by aggregate:    {f043_in_top5} / 5"
    )
    print(f"  F043_family on Pareto front:          {f043_on_pf} / {len(pf)}")
    print(f"  CAS Layer C decided:                  {cas_decided_count} / {len(scored)}")
    print(f"  Layer B linear fallback:              "
          f"{len(scored) - cas_decided_count} / {len(scored)}")

    # ---- η_trace vs η_inverse interesting comparisons ---------------------
    print("\n" + "=" * 80)
    print("η_trace vs η_inverse — diagnostic:")
    print("-" * 80)
    for s in scored:
        eta_tr = min(s["eta_trace_A"], s["eta_trace_B"])
        diff = abs(s["eta_inverse"] - eta_tr)
        if diff > 0.2:
            print(
                f"  {s['name']:<24} "
                f"η_inverse={s['eta_inverse']:.3f}  η_trace={eta_tr:.3f}  "
                f"DIFF={diff:.2f}"
            )

    # ---- Verdict ----------------------------------------------------------
    print("\n" + "=" * 80)
    if f043_in_top5 >= 3 and f043_on_pf == 0:
        verdict = "VALIDATED"
        msg = (
            "  Aggregate scalar promotes F043 (3+ in top 5);\n"
            "  Pareto-front rejects them (0 on front).\n"
            "  Tier B (CAS Layer C + η_trace) does not break the v2 verdict; it tightens it."
        )
    elif f043_in_top5 >= 3 and f043_on_pf < f043_in_top5:
        verdict = "PARTIAL"
        msg = (
            f"  Aggregate promotes F043 ({f043_in_top5} in top 5); "
            f"Pareto partially rejects ({f043_on_pf} on front).\n"
            "  Disagreement present but not absolute. Investigate."
        )
    elif f043_in_top5 < 3:
        verdict = "ANOMALY"
        msg = "  Aggregate did NOT promote F043 to top 5; investigate scorer."
    else:
        verdict = "FAILED"
        msg = "  Aggregate AND Pareto both promote F043. Reset to critique."
    print(f"VERDICT (Tier B): {verdict}")
    print(msg)
    print("=" * 80)


def write_results_md(results: dict, path: str) -> None:
    scored = results["scored"]
    by_aggregate = results["by_aggregate"]
    pf = results["pareto_front"]
    pf_names = results["pareto_front_names"]

    f043_in_top5 = sum(
        1 for s in by_aggregate[:5] if s["class"] == "F043_family"
    )
    f043_on_pf = sum(1 for s in pf if s["class"] == "F043_family")
    cas_decided_count = sum(
        1 for s in scored if s["basis_projection_source"] == "CAS_Layer_C"
    )

    if f043_in_top5 >= 3 and f043_on_pf == 0:
        verdict = "VALIDATED"
    elif f043_in_top5 >= 3 and f043_on_pf < f043_in_top5:
        verdict = "PARTIAL"
    elif f043_in_top5 < 3:
        verdict = "ANOMALY"
    else:
        verdict = "FAILED"

    L = []
    L.append(f"# Tink 2 Tier B results — {datetime.now(timezone.utc).date().isoformat()}")
    L.append("")
    L.append(f"**Verdict (Tier B): {verdict}**")
    L.append("")
    L.append(f"- n = {results['data_n']}, seed = {results['data_seed']}")
    L.append(f"- Aggregate: α · L_expr − β · |z|  (α=`{ALPHA}`, β=`{BETA}`)")
    L.append("- Pareto axes: (1 − basis_projection, affordance_gain, reconstructability)")
    L.append(f"- η_composite = `{W_EXTERNAL}` · η_inverse + `{W_INTERNAL}` · η_trace")
    L.append("- Lineage tags: DISABLED (γ = 0; basis_projection measured but not penalized)")
    L.append("")

    L.append("## Tier B additions")
    L.append("")
    L.append("- **CAS Layer C** (SymPy symbolic canonicalization). For each candidate,")
    L.append("  expressions are converted to SymPy and checked for linear-combination")
    L.append("  membership in the identity basis. If reduced, basis_projection = 1.0")
    L.append("  is set with explicit `cas_reduced_to` provenance. Else fall through to")
    L.append("  Layer B linear regression.")
    L.append("- **η_trace** (AST step-by-step reversibility). Per internal AST node,")
    L.append("  measure how reversible the operation is. `add`/`sub`/`mul` collapse")
    L.append("  information; `neg`/`scalar_mul`/`exp`/`log` are bijective. η_trace =")
    L.append("  min over steps. Composite η = `0.7` · η_inverse + `0.3` · η_trace.")
    L.append("")

    L.append("## Per-candidate scores (Tier B)")
    L.append("")
    L.append(
        "| name | class | tok | \\|z\\| | BP | BP src | aff | η_inv | η_trace | η_comp | agg | Pareto |"
    )
    L.append(
        "|------|-------|----:|-----:|---:|:------:|----:|-----:|-------:|-------:|----:|:------:|"
    )
    for s in scored:
        on_pf = "✓" if s["name"] in pf_names else "·"
        bp_src = "CAS" if s["basis_projection_source"] == "CAS_Layer_C" else "L_B"
        eta_tr = min(s["eta_trace_A"], s["eta_trace_B"])
        L.append(
            f"| `{s['name']}` | {s['class']} | {s['n_tokens']} | {s['z_abs']:.2f} | "
            f"{s['basis_projection']:.3f} | {bp_src} | "
            f"{s['affordance_gain']:.3f} | {s['eta_inverse']:.3f} | "
            f"{eta_tr:.3f} | {s['reconstructability']:.3f} | "
            f"{s['aggregate_score']:+.2f} | {on_pf} |"
        )
    L.append("")

    L.append("## CAS Layer C activations")
    L.append("")
    cas_decided = [s for s in scored if s["basis_projection_source"] == "CAS_Layer_C"]
    L.append(f"**{cas_decided_count} of {len(scored)} candidates decided by CAS Layer C.**")
    L.append("")
    L.append("| name | E_A marker | E_B marker | reduced_to |")
    L.append("|------|-----------|-----------|-----------|")
    for s in cas_decided:
        L.append(
            f"| `{s['name']}` | {s['cas_marker_E_A']} | {s['cas_marker_E_B']} | "
            f"{s['cas_reduced_to']} |"
        )
    L.append("")

    L.append("## Top 5 by aggregate")
    L.append("")
    for i, s in enumerate(by_aggregate[:5], 1):
        on_pf = "✓ on Pareto" if s["name"] in pf_names else "✗ NOT on Pareto"
        L.append(
            f"{i}. `{s['name']}` ({s['class']}) — agg={s['aggregate_score']:+.2f}, "
            f"|z|={s['z_abs']:.2f}, BP={s['basis_projection']:.3f} "
            f"({s['basis_projection_source']}), **{on_pf}**"
        )
    L.append("")

    L.append("## Pareto front (substrate-value triple)")
    L.append("")
    for s in pf:
        L.append(
            f"- `{s['name']}` ({s['class']}) — "
            f"novelty={s['pareto_novelty']:.3f}, "
            f"usefulness={s['pareto_usefulness']:.3f}, "
            f"faithfulness={s['pareto_faithfulness']:.3f}"
        )
    L.append("")

    L.append("## Disagreement")
    L.append("")
    L.append(f"- F043_family in top-5 by aggregate: **{f043_in_top5} / 5**")
    L.append(f"- F043_family on Pareto front: **{f043_on_pf} / {len(pf)}**")
    L.append("")

    L.append("## η_trace diagnostic — where η_trace and η_inverse disagree")
    L.append("")
    L.append("Differences greater than 0.2 between the two reconstructability")
    L.append("signals are surfaced for inspection. Disagreement is informative —")
    L.append("it localizes which kind of information loss the candidate has.")
    L.append("")
    for s in scored:
        eta_tr = min(s["eta_trace_A"], s["eta_trace_B"])
        diff = abs(s["eta_inverse"] - eta_tr)
        if diff > 0.2:
            L.append(
                f"- `{s['name']}` — η_inverse=`{s['eta_inverse']:.3f}`, "
                f"η_trace=`{eta_tr:.3f}` (diff `{diff:.2f}`)"
            )
    L.append("")

    L.append("## Verdict notes")
    L.append("")
    if verdict == "VALIDATED":
        L.append(
            "Tier B does not break v2's verdict; it tightens it. CAS Layer C "
            "now provides explicit symbolic provenance for basis-projection "
            "decisions on most F043-family candidates. η_trace adds a "
            "complementary signal to η_inverse."
        )
        L.append("")
        L.append(
            "**Tier B implementation gates close. Tier C (gen_11 merger, TRG "
            "implementation) remains gated on Tink 3 (full-grammar empty-niche "
            "scan) producing real VACUUM signals and auto-descriptor candidates.**"
        )
    elif verdict == "PARTIAL":
        L.append("Disagreement present but not absolute. Investigate before propagating.")
    else:
        L.append("See verdict text in stdout.")
    L.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    results = run_tink_2(n=1000, seed=42)
    print_results(results)
    out_path = "results_2026-04-25_tier_b.md"
    write_results_md(results, out_path)
    print(f"\nMarkdown summary written to: {out_path}")
