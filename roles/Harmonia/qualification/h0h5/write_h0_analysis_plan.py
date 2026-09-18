"""Writes h0_analysis_plan.json (HARM-01).  2026-09-18, Harmonia[m2-ca1148a0].

The four H0 cells, each with a payload hash computed from its DECLARED consumed
inputs (the design's rule: 'the cell name remains design provenance; the actual
consumed inputs determine execution identity'). Until the artifact cells run
(HARM-22, blocked on Vivarium's reserve_budget), the hash is over the declared
spec; when they run, the executor's spec_hash replaces it and the same
validate_cell_payloads check applies.

fresh == S00: H1's 'fresh search' arm and H0's S00 are the SAME consumed inputs
(no transport, no library, ordinary within-task CEGIS). That is one baseline
under two labels, declared as an alias, never a fourth distinct payload.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qualification_rules import (RULES_VERSION, validate_cell_payloads, C_G, C_I, C_TRANSPORT,  # noqa: E402
                                 C_LIBRARY, shared_arm_correlation_exchangeable, contrast_correlation,
                                 sigma_exchangeable)

BASE = {"kind": "cegis_boolean_v1", "solver_policy": "fixed_seeded_enumeration",
        "within_task_cegis": True, "resource_caps": "identical across cells"}


def payload(transport: bool, library: bool) -> dict:
    return dict(BASE, source_failure_transport=("frozen_source_pack" if transport else "ABSENT"),
                frozen_component_library=("frozen_library_artifact" if library else "ABSENT"))


def h(d: dict) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


def build() -> dict:
    cells = {}
    for label, (t, l) in {"S00": (False, False), "S10": (True, False),
                          "S01": (False, True), "S11": (True, True)}.items():
        p = payload(t, l)
        cells[label] = {"source_failure_transport": t, "frozen_component_library": l,
                        "declared_payload": p, "payload_hash": h(p),
                        "hash_is_over": "declared spec (pre-run); executor spec_hash once the cell runs"}
    plan = {
        "plan": "h0_analysis_plan", "version": "1.0.0", "rules_version": RULES_VERSION,
        "unit": "paired (seed x task_block); generations/mutations/candidates are within-unit repeats",
        "cells": cells,
        "aliases": {"fresh": "S00", "random_pack": "S10"},
        "alias_evidence": {
            "fresh == S00": "RULING_REPLICATE_C3_3_H1BETA_D3CUT_2026-09-10.md item 1b (same payload, both slots "
                            "null, same spec hash; 12 completed, 2 solved in both); "
                            "RULING_H1H0_PHASE2_CONTRASTS_2026-09-14.md s1: identical 12/12 on status, solved, vm_ops",
            "random_pack == S10": "RULING_H1H0_PHASE2_CONTRASTS_2026-09-14.md s1: identical 12/12; hashes DIFFER "
                                  "for one payload (Charon A1), which is why validate_cell_payloads compares the "
                                  "declared payload as well as the hash",
            "history": "the 09-10 alpha four-cell table had THREE distinct payloads under FOUR labels; "
                       "this plan has four distinct cell payloads and two declared aliases (six labels)"},
        "dedup_rule": ("cells are deduplicated by payload hash before analysis; one hash under two "
                       "CELL labels is refused (validate_cell_payloads); a declared alias is one "
                       "baseline under two labels and contributes ONE arm"),
        "primary_contrasts": {"G_joint_treatment_S11_minus_S00": C_G, "interaction_I": C_I},
        "secondary_contrasts": {"transport_S10_minus_S00": C_TRANSPORT, "library_S01_minus_S00": C_LIBRARY},
        "multiplicity": "BONFERRONI over the two primaries; secondaries reported with induced correlation",
        "shared_arm_correlation": {
            "rule": "corr = c1' Sigma c2 / sqrt(c1' Sigma c1 c2' Sigma c2); reported at the pilot Sigma",
            "exchangeable_equal_variance_reference": {
                "G|transport": shared_arm_correlation_exchangeable(C_G, C_TRANSPORT),
                "G|library": shared_arm_correlation_exchangeable(C_G, C_LIBRARY),
                "transport|library": shared_arm_correlation_exchangeable(C_TRANSPORT, C_LIBRARY),
                "G|I": shared_arm_correlation_exchangeable(C_G, C_I),
                "note": "0.5 for any rho for two simple differences sharing S00; G and I are uncorrelated "
                        "under exchangeable equal variances and NOT in general (measure at the pilot Sigma)"},
        },
        "attainable_range": [-1.0, 1.0],
        "min_eligible_blocks": 6,
    }
    return plan


if __name__ == "__main__":
    plan = build()
    rec = validate_cell_payloads(plan)
    plan["validation"] = rec
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h0_analysis_plan.json")
    with open(out, "w", encoding="ascii", newline="\n") as f:
        json.dump(plan, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps(rec, indent=1))
    print("wrote", out)
