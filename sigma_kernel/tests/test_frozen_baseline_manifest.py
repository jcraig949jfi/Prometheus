"""Frozen-baseline manifest test — closes the audit gap surfaced by
substrate-tester fire #50 (2026-05-08).

**Background.** `test_frozen_invariance.py` (filed during the
2026-05-08 mini contract-change window) auto-enrolls every
`@dataclass(frozen=True)` class found in `sigma_kernel/*` and asserts
attribute mutation raises `FrozenInstanceError`. The auto-enrollment
filter (`_is_frozen_dataclass`) checks `cls.__dataclass_params__.frozen
is True` — which means classes whose `frozen` flag has been flipped to
`False` are silently EXCLUDED from the audit.

Substrate-tester fire #50 (2026-05-08) empirically confirmed this:
after manually flipping `frozen=True -> False` on TWO classes in
`sigma_kernel/method_spec.py`, the auto-enrollment audit still PASSES
because the flipped classes drop out of the enrollment loop.

This file closes that gap with a baseline-manifest test:
`EXPECTED_FROZEN_CLASSES` is a frozen list of qualified class names
that MUST remain `frozen=True`. The test asserts each one's
`__dataclass_params__.frozen is True` directly. Mutation that flips
the flag is caught immediately.

**How to maintain the manifest.** When you intentionally add or remove
a `@dataclass(frozen=True)` class in `sigma_kernel/*`, update
`EXPECTED_FROZEN_CLASSES` here. The test enforces append-only growth
(an entry is removed only with explicit substrate-design review).

**Source ticket:** T-2026-05-08-ST-fire50-001 (Techne investigation;
P2-medium).
"""
from __future__ import annotations

import dataclasses
import importlib
from typing import List

import pytest


# ---------------------------------------------------------------------------
# Baseline manifest — qualified class names that MUST stay frozen
# ---------------------------------------------------------------------------

# Generated 2026-05-08 by walking sigma_kernel/* + filtering frozen
# dataclasses. Keep this list sorted alphabetically; add new entries
# when a new @dataclass(frozen=True) class is added intentionally;
# REMOVE only with explicit substrate-design review.
EXPECTED_FROZEN_CLASSES: List[str] = [
    # bind_eval
    "sigma_kernel.bind_eval.Binding",
    "sigma_kernel.bind_eval.CostModel",
    "sigma_kernel.bind_eval.Evaluation",
    # coordinate_chart
    "sigma_kernel.coordinate_chart.CanonicalizationProtocol",
    "sigma_kernel.coordinate_chart.CoordinateChart",
    # exclusion_certificate (Boundary added fire #53; was missed in fire #50)
    "sigma_kernel.exclusion_certificate.Boundary",
    "sigma_kernel.exclusion_certificate.ExclusionCertificate",
    "sigma_kernel.exclusion_certificate.ExclusionClaim",
    "sigma_kernel.exclusion_certificate.RegionSpec",
    "sigma_kernel.exclusion_certificate.ReplayInfo",
    "sigma_kernel.exclusion_certificate.TriangulationPathRef",
    "sigma_kernel.exclusion_certificate.VerifierSet",
    # method_spec
    "sigma_kernel.method_spec.DriftChannel",
    "sigma_kernel.method_spec.MethodSpec",
    # operator_portability
    "sigma_kernel.operator_portability.OperatorPortabilityCertificate",
    "sigma_kernel.operator_portability.PortabilityEvidence",
    "sigma_kernel.operator_portability.PortabilityReplay",
    # residual_benchmark
    "sigma_kernel.residual_benchmark.BenchmarkEntry",
    # residuals
    "sigma_kernel.residuals.Residual",
    "sigma_kernel.residuals.SpectralVerdict",
    # sigma_kernel
    "sigma_kernel.sigma_kernel.Capability",
    "sigma_kernel.sigma_kernel.Symbol",
    "sigma_kernel.sigma_kernel.VerdictResult",
    # triangulation_protocol
    "sigma_kernel.triangulation_protocol.TriangulationPath",
    "sigma_kernel.triangulation_protocol.TriangulationResult",
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("qualified_name", EXPECTED_FROZEN_CLASSES)
def test_class_remains_frozen(qualified_name: str):
    """For each manifest entry, import the class and assert
    `__dataclass_params__.frozen is True`. Catches frozen=True->False
    mutations that the auto-enrollment audit silently misses."""
    module_name, _, class_name = qualified_name.rpartition(".")
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name, None)
    assert cls is not None, (
        f"Class {qualified_name} not found — manifest out of date "
        f"(class was renamed or removed?). Update "
        f"EXPECTED_FROZEN_CLASSES in this test file."
    )
    assert dataclasses.is_dataclass(cls), (
        f"{qualified_name} is not a dataclass. Either the class lost "
        f"its @dataclass decorator (substrate-design regression) or "
        f"the manifest entry is wrong."
    )
    params = getattr(cls, "__dataclass_params__", None)
    assert params is not None, (
        f"{qualified_name} has no __dataclass_params__ — internal "
        f"inconsistency."
    )
    assert params.frozen is True, (
        f"{qualified_name} has frozen={params.frozen!r}; manifest "
        f"requires True. If this is intentional, remove the manifest "
        f"entry with substrate-design review per fire #50 closure."
    )


def test_manifest_count_matches_baseline():
    """The manifest must contain at least the 25 classes enumerated by
    fire #53 (was 12 in fire #50; expanded after Lane 16 surfaced
    `Boundary` as a missed entry). Removing entries is a contract
    change requiring review."""
    assert len(EXPECTED_FROZEN_CLASSES) >= 25, (
        f"Manifest shrunk below baseline ({len(EXPECTED_FROZEN_CLASSES)} "
        f"< 25). Remove an entry only with explicit substrate-design "
        f"review per fire #50 ticket T-2026-05-08-ST-fire50-001 "
        f"(updated baseline fire #53 ticket T-2026-05-08-ST-fire53-001)."
    )


def test_manifest_uniqueness():
    """Manifest entries must be unique."""
    assert len(EXPECTED_FROZEN_CLASSES) == len(set(EXPECTED_FROZEN_CLASSES)), (
        "Duplicate entries in EXPECTED_FROZEN_CLASSES."
    )
