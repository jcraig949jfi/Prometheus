"""
Icarus adversarial probe battery -- spec v0.2 #6.

Eight probes, each parameterized with a fresh random seed per cycle. Static
attack classes (probe TYPES are fixed) but parameters are dynamic.

  1. Single-primitive baseline
  2. Random-wiring baseline
  3. Symbol-isomorphism (AST rename)
  4. Scrambled-graph
  5. Null-transformation
  6. Reversal
  7. Perturbation (tier-specific)
  8. Ablation with random noise

For Phase 0, each probe is implemented as a stub that returns a sensible
verdict when no reasoner is present. Phase 1+ fills in the deep implementations.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import ast
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ProbeVerdict:
    probe_name: str
    passed: bool
    metric: Optional[float]
    detail: str
    seed: int


def run_probe_battery(
    reasoner_module_path: Path,
    tier: str,
    problems: list[dict],
    seed: Optional[int] = None,
) -> list[ProbeVerdict]:
    """Run all 8 probes against the reasoner. Each probe gets a fresh
    derived-from-master seed so they're reproducible per cycle but vary
    cycle-to-cycle."""
    if seed is None:
        seed = random.SystemRandom().randint(0, 2**32 - 1)

    rng = random.Random(seed)

    if not reasoner_module_path.exists():
        return [
            ProbeVerdict(
                probe_name=p, passed=False, metric=None,
                detail="reasoner_missing", seed=seed
            )
            for p in (
                "single_primitive_baseline", "random_wiring", "symbol_isomorphism",
                "scrambled_graph", "null_transformation", "reversal",
                "perturbation", "ablation_noise",
            )
        ]

    verdicts: list[ProbeVerdict] = []
    verdicts.append(_probe_single_primitive_baseline(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_random_wiring(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_symbol_isomorphism(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_scrambled_graph(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_null_transformation(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_reversal(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_perturbation(reasoner_module_path, problems, tier, rng.randint(0, 2**32 - 1)))
    verdicts.append(_probe_ablation_noise(reasoner_module_path, problems, rng.randint(0, 2**32 - 1)))
    return verdicts


def _probe_single_primitive_baseline(reasoner_path, problems, seed) -> ProbeVerdict:
    """The Apollo gen-3551 lesson: composition must beat best single primitive."""
    # Phase 0 stub: assume passes since no composition is yet defined
    return ProbeVerdict(
        probe_name="single_primitive_baseline", passed=True, metric=None,
        detail="phase_0_stub_no_composition_yet", seed=seed,
    )


def _probe_random_wiring(reasoner_path, problems, seed) -> ProbeVerdict:
    """Random rewire of composition graph. If still passes, wiring was decorative."""
    return ProbeVerdict(
        probe_name="random_wiring", passed=True, metric=None,
        detail="phase_0_stub_no_wiring_to_scramble", seed=seed,
    )


def _probe_symbol_isomorphism(reasoner_path, problems, seed) -> ProbeVerdict:
    """AST-rename every var and func to random hashes; re-run. Failure here
    means the reasoner hardcoded string-matching heuristics (per Gemini's
    frontier review)."""
    try:
        text = reasoner_path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        # Phase 0 stub: just confirm it parses. Phase 1 will rename + run.
        node_count = sum(1 for _ in ast.walk(tree))
        return ProbeVerdict(
            probe_name="symbol_isomorphism", passed=True,
            metric=float(node_count),
            detail=f"phase_0_stub_ast_parsed_{node_count}_nodes",
            seed=seed,
        )
    except SyntaxError as e:
        return ProbeVerdict(
            probe_name="symbol_isomorphism", passed=False, metric=None,
            detail=f"reasoner_has_syntax_error: {e}", seed=seed,
        )


def _probe_scrambled_graph(reasoner_path, problems, seed) -> ProbeVerdict:
    """More aggressive variant of random_wiring -- insert random intermediate
    nodes. For R5+."""
    return ProbeVerdict(
        probe_name="scrambled_graph", passed=True, metric=None,
        detail="phase_0_stub_for_R5+", seed=seed,
    )


def _probe_null_transformation(reasoner_path, problems, seed) -> ProbeVerdict:
    """Apply reasoner to invariant inputs (identity, empty, trivial-case).
    Any output change = failure."""
    return ProbeVerdict(
        probe_name="null_transformation", passed=True, metric=None,
        detail="phase_0_stub_no_reasoner_to_test", seed=seed,
    )


def _probe_reversal(reasoner_path, problems, seed) -> ProbeVerdict:
    """For invertible ops, can output be inverted to recover input?"""
    return ProbeVerdict(
        probe_name="reversal", passed=True, metric=None,
        detail="phase_0_stub_no_inverse_primitives", seed=seed,
    )


def _probe_perturbation(reasoner_path, problems, tier, seed) -> ProbeVerdict:
    """Tier-specific perturbation: paraphrase (R0), var-rename (R1),
    distractor (R2), inconsistent constraint (R3), etc."""
    return ProbeVerdict(
        probe_name="perturbation", passed=True, metric=None,
        detail=f"phase_0_stub_tier_{tier}", seed=seed,
    )


def _probe_ablation_noise(reasoner_path, problems, seed) -> ProbeVerdict:
    """Gaussian noise into intermediate reprs. Performance should degrade
    smoothly."""
    return ProbeVerdict(
        probe_name="ablation_noise", passed=True, metric=None,
        detail="phase_0_stub_no_intermediate_reprs", seed=seed,
    )
