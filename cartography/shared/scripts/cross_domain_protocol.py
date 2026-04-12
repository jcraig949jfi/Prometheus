#!/usr/bin/env python3
"""
CrossDomainProtocol: Automated 7-layer filter for cross-domain claims.
Wraps F27, F29-F32 + permutation null into a single callable.
"""
import numpy as np
from collections import defaultdict


class CrossDomainProtocol:
    """Run the full 7-layer cross-domain falsification gauntlet."""

    def __init__(self, battery, logger=None):
        self.bv2 = battery
        self.logger = logger

    def test(self, set_a, set_b, values_a=None, values_b=None,
             shared_keys=None, domain_a="A", domain_b="B"):
        """Run all applicable layers. Returns (overall_verdict, layer_results)."""

        set_a = set(int(x) for x in set_a if x and int(x) > 0)
        set_b = set(int(x) for x in set_b if x and int(x) > 0)
        overlap = set_a & set_b

        layers = {}

        # Layer 1: Distributional baseline (F29)
        v1, r1 = self.bv2.F29_distributional_baseline(set_a, set_b)
        layers["L1_distributional"] = {"verdict": v1, "details": r1}
        if v1 == "ARTIFACT":
            return f"KILLED_AT_LAYER_1", layers

        # Layer 2: Range-conditioned enrichment (F30)
        v2, r2 = self.bv2.F30_range_conditioned_enrichment(set_a, set_b)
        layers["L2_range"] = {"verdict": v2, "details": r2}
        if v2 == "RANGE_ARTIFACT":
            return "KILLED_AT_LAYER_2", layers

        # Layer 3: Prime-mediated null (F31) — only if values provided
        if values_a is not None and values_b is not None and shared_keys is not None:
            v3, r3 = self.bv2.F31_prime_mediated_null(
                values_a, values_b, None, None, shared_keys)
            layers["L3_prime_mediated"] = {"verdict": v3, "details": r3}
            if v3 == "PRIME_MEDIATED":
                return "KILLED_AT_LAYER_3", layers
        else:
            layers["L3_prime_mediated"] = {"verdict": "SKIPPED", "details": {}}

        # Layer 4: Scaling degeneracy (F32) — only if continuous values
        if values_a is not None and values_b is not None:
            # Need x and y arrays — use shared keys as x-axis
            if shared_keys:
                shared = sorted(shared_keys if isinstance(shared_keys, set) else set(shared_keys))
                xa = [values_a.get(k, 0) for k in shared]
                ya = [values_b.get(k, 0) for k in shared]
                v4, r4 = self.bv2.F32_scaling_degeneracy(
                    list(range(len(xa))), xa,
                    list(range(len(ya))), ya,
                    domain_a, domain_b)
                layers["L4_scaling"] = {"verdict": v4, "details": r4}
            else:
                layers["L4_scaling"] = {"verdict": "SKIPPED", "details": {}}
        else:
            layers["L4_scaling"] = {"verdict": "SKIPPED", "details": {}}

        # Layer 5: Consequence check (F27)
        v5, r5 = self.bv2.F27_consequence_check(domain_a, domain_b)
        layers["L5_tautology"] = {"verdict": v5, "details": r5}
        if v5 == "TAUTOLOGY":
            return "KILLED_AT_LAYER_5", layers

        # Layer 6: Permutation null on overlap count
        if len(overlap) > 0:
            max_val = max(max(set_a), max(set_b))
            null_overlaps = []
            rng = np.random.default_rng(42)
            for _ in range(500):
                fake_b = set(int(x) for x in np.exp(rng.uniform(0, np.log(max_val + 1), len(set_b))))
                null_overlaps.append(len(set_a & fake_b))
            null_mean = np.mean(null_overlaps)
            null_std = np.std(null_overlaps)
            z = (len(overlap) - null_mean) / null_std if null_std > 0 else 0
            layers["L6_permutation"] = {
                "verdict": "SIGNIFICANT" if z > 3 else "NOT_SIGNIFICANT",
                "overlap": len(overlap), "null_mean": null_mean, "z": z
            }
        else:
            layers["L6_permutation"] = {"verdict": "NO_OVERLAP", "details": {}}
            return "KILLED_NO_OVERLAP", layers

        # Layer 7: Summary
        killed_layers = [k for k, v in layers.items()
                         if v.get("verdict") in ("ARTIFACT", "RANGE_ARTIFACT",
                                                  "PRIME_MEDIATED", "TAUTOLOGY",
                                                  "NOT_SIGNIFICANT", "NO_OVERLAP")]
        if killed_layers:
            return f"KILLED_AT_{killed_layers[0]}", layers
        else:
            return "SURVIVES", layers
