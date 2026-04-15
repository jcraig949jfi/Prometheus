"""
Validate — Connect TT-Cross discoveries back to the falsification battery.

When TT-Cross finds rank-R structure between two domains, this module
extracts the R principal components and runs them through battery tests
to determine the true (validated) bond dimension.
"""
import torch
import numpy as np
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import sys

from harmonia.src.domain_index import DomainIndex


@dataclass
class ComponentResult:
    """Result of validating one principal component of a TT bond."""
    component_idx: int
    singular_value: float
    energy_fraction: float
    verdict: str  # SURVIVES, KILLED, UNTESTED
    kill_reason: Optional[str] = None
    battery_results: Optional[dict] = None


@dataclass
class ValidationReport:
    """Full validation report for a bond between two domains."""
    domain_a: str
    domain_b: str
    raw_rank: int
    validated_rank: int
    components: list[ComponentResult]

    def summary(self) -> str:
        lines = [
            f"Bond: {self.domain_a} <-> {self.domain_b}",
            f"  Raw rank: {self.raw_rank} -> Validated rank: {self.validated_rank}",
        ]
        for c in self.components:
            lines.append(
                f"  Component {c.component_idx}: SV={c.singular_value:.4f} "
                f"({c.energy_fraction:.1%} energy) -> {c.verdict}"
                + (f" ({c.kill_reason})" if c.kill_reason else "")
            )
        return "\n".join(lines)


def extract_bond_components(tt, bond_idx: int, domains: list[DomainIndex]):
    """
    Extract the principal components of a TT bond as paired object rankings.

    Each component defines a ranking of objects in domain_a and domain_b
    that contribute most to that component of the coupling.

    Returns:
        List of (sv, left_scores, right_scores) tuples where:
        - sv: singular value (strength of this component)
        - left_scores: (n_a,) tensor scoring objects in domain_a
        - right_scores: (n_b,) tensor scoring objects in domain_b
    """
    core_a = tt.cores[bond_idx]    # (r_{i-1}, n_a, r_i)
    core_b = tt.cores[bond_idx + 1]  # (r_i, n_b, r_{i+1})

    # Unfold core_a: (r_{i-1} * n_a, r_i)
    r0, n_a, r1 = core_a.shape
    unfolded_a = core_a.reshape(r0 * n_a, r1)

    # SVD of the bond
    U, S, Vh = torch.linalg.svd(unfolded_a, full_matrices=False)

    components = []
    for k in range(len(S)):
        # Left scores: how much each object in domain_a loads on component k
        # U is (r0*n_a, min(r0*n_a, r1)), reshape to (r0, n_a, ...)
        u_k = U[:, k].reshape(r0, n_a)
        left_scores = u_k.norm(dim=0)  # aggregate across input rank

        # Right scores from Vh and core_b
        # Vh is (min, r1), core_b is (r1, n_b, r2)
        vh_k = Vh[k, :]  # (r1,)
        # Contract with core_b: (r1,) @ (r1, n_b, r2) -> (n_b, r2)
        right_contracted = torch.einsum("r,rnk->nk", vh_k, core_b)
        right_scores = right_contracted.norm(dim=1)  # (n_b,)

        components.append((S[k].item(), left_scores, right_scores))

    return components


def validate_bond(
    tt,
    bond_idx: int,
    domains: list[DomainIndex],
    battery_path: Optional[Path] = None,
    run_battery: bool = False,
    gating_mode: str = "prosecution",
) -> ValidationReport:
    """
    Validate each component of a TT bond.

    gating_mode controls behavior:
    - "prosecution" (default): kills components with <1% energy or low
      selectivity. Original behavior — use for final validation.
    - "exploration": records all components as OBSERVED with annotations.
      No killing. Use for ungated exploration where we want to see the
      full landscape before deciding what to prosecute.

    With the battery (run_battery=True), runs F1/F3/F17/F24b on the
    top-scoring objects from each component (prosecution mode only).
    """
    if gating_mode not in ("prosecution", "exploration"):
        raise ValueError(f"gating_mode must be 'prosecution' or 'exploration', got {gating_mode}")

    components = extract_bond_components(tt, bond_idx, domains)

    total_energy = sum(sv ** 2 for sv, _, _ in components)
    results = []
    validated_count = 0

    for k, (sv, left_scores, right_scores) in enumerate(components):
        energy_frac = (sv ** 2) / total_energy if total_energy > 0 else 0

        # Compute heuristic metrics regardless of mode
        left_cv = left_scores.std() / left_scores.mean().clamp(min=1e-8)
        right_cv = right_scores.std() / right_scores.mean().clamp(min=1e-8)
        low_energy = energy_frac < 0.01
        low_selectivity = left_cv < 0.1 and right_cv < 0.1

        if gating_mode == "exploration":
            # Exploration mode: observe everything, annotate but don't kill
            verdict = "OBSERVED"
            kill_reason = None
            if low_energy:
                kill_reason = "annotation: energy < 1%"
            elif low_selectivity:
                kill_reason = "annotation: uniform scores (no selectivity)"
        else:
            # Prosecution mode: original gating behavior
            verdict = "SURVIVES"
            kill_reason = None
            if low_energy:
                verdict = "KILLED"
                kill_reason = "energy < 1%"
            elif low_selectivity:
                verdict = "KILLED"
                kill_reason = "uniform scores (no selectivity)"

        if run_battery and verdict == "SURVIVES":
            battery_result = _run_battery_on_component(
                k, sv, left_scores, right_scores, domains, bond_idx
            )
            if battery_result:
                if battery_result.get("overall_verdict") == "KILLED":
                    verdict = "KILLED"
                    kill_reason = battery_result.get("kill_reason", "battery")
            results.append(ComponentResult(
                component_idx=k,
                singular_value=sv,
                energy_fraction=energy_frac,
                verdict=verdict,
                kill_reason=kill_reason,
                battery_results=battery_result,
            ))
        else:
            results.append(ComponentResult(
                component_idx=k,
                singular_value=sv,
                energy_fraction=energy_frac,
                verdict=verdict,
                kill_reason=kill_reason,
            ))

        if verdict == "SURVIVES":
            validated_count += 1

    return ValidationReport(
        domain_a=domains[bond_idx].name,
        domain_b=domains[bond_idx + 1].name,
        raw_rank=len(components),
        validated_rank=validated_count,
        components=results,
    )


def _run_battery_on_component(
    component_idx, sv, left_scores, right_scores,
    domains, bond_idx,
):
    """
    Run the falsification battery on a TT component.

    Extracts the top-scoring objects from each domain, pairs their
    feature values, and runs F1 (permutation null), F3 (effect size),
    F17 (confound sensitivity), F24b (tail check).
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent
                                / "cartography" / "shared" / "scripts"))
        from battery_unified import UnifiedBattery
    except ImportError:
        return {"error": "battery_unified not importable", "overall_verdict": "UNTESTED"}

    dom_a = domains[bond_idx]
    dom_b = domains[bond_idx + 1]

    # Take top 500 objects from each domain by component score
    n_top = min(500, len(left_scores), len(right_scores))
    top_a = torch.topk(left_scores, n_top).indices
    top_b = torch.topk(right_scores, n_top).indices

    # Extract a representative feature from each (first feature column)
    values_a = dom_a.features[top_a, 0].numpy()
    values_b = dom_b.features[top_b, 0].numpy()

    try:
        battery = UnifiedBattery()
        verdict, results = battery.test_correlation(
            values_a, values_b,
            claim=f"TT component {component_idx} (SV={sv:.4f}) "
                  f"between {dom_a.name} and {dom_b.name}"
        )
        return {"overall_verdict": verdict, "tests": results}
    except Exception as e:
        return {"error": str(e), "overall_verdict": "UNTESTED"}
