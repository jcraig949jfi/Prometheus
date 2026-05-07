"""
Substrate-Tester Fire #2 — Lane 2 (adversarial-CLAIM) + Lane 9 (NearMissCorpus-leak)

Lane 2: 5 deliberately ill-formed CLAIMs through SigmaKernel.CLAIM and
CoordinateChart constructor. Substrate must reject at typing layer.

Lane 9: pre/post view separation. Try load_post_view without flag (must
raise PostFalsificationLeakageError); try with flag + audit log; verify
leakage log records the load.

Author: substrate-tester (Charon-aligned), fire #2, 2026-05-06
"""

from __future__ import annotations

import json
import tempfile
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")

# ---------------------------------------------------------------------------
# Lane 2 — adversarial-CLAIM
# ---------------------------------------------------------------------------


def lane_2_adversarial_claim() -> dict:
    """5 ill-formed inputs against SigmaKernel.CLAIM + CoordinateChart.

    Per lane spec:
      - silent acceptance: P0-blocker
      - gauntlet-execution on ill-formed claim: P1-high
      - error message uninformative: P3-low
    """
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.coordinate_chart import (
        CoordinateChart,
        CanonicalizationProtocol,
    )

    kernel = SigmaKernel()

    probes = []

    # Probe 1: SigmaKernel.CLAIM with precision_metadata as a STRING (must be dict or None per code)
    try:
        kernel.CLAIM(
            target_name="adversarial-probe-1",
            hypothesis="malformed precision_metadata",
            evidence={"x": 1},
            kill_path="adversarial",
            precision_metadata="this should be a dict not a string",  # type: ignore
        )
        probes.append({
            "id": "P1_precision_metadata_as_string",
            "expected": "TypeError raised",
            "actual": "silently accepted",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "ill_formed_aspect": "precision_metadata is a string, not a dict",
        })
    except TypeError as exc:
        probes.append({
            "id": "P1_precision_metadata_as_string",
            "expected": "TypeError raised",
            "actual": f"TypeError: {exc}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        probes.append({
            "id": "P1_precision_metadata_as_string",
            "expected": "TypeError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
            "note": "raised wrong exception type — TypeError expected",
        })

    # Probe 2: CoordinateChart with empty domain string
    try:
        # Need a valid CanonicalizationProtocol stub
        cp = CanonicalizationProtocol(
            impl="group_quotient",
            decidability_status="decidable",
            choice_dependencies=(),
            version="0.0",
        )
        chart = CoordinateChart(
            domain="",  # ill-formed — must be non-empty
            region_key="r1",
            coordinate_system=("x",),
            canonicalization=cp,
            metric=lambda a, b: 0.0,
            metric_id="trivial",
            equivalence_relations=(),
            admissible_region=lambda p: True,
            valid_operations=(),
        )
        probes.append({
            "id": "P2_chart_empty_domain",
            "expected": "ValueError raised",
            "actual": "silently accepted",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "ill_formed_aspect": "domain is empty string",
        })
    except ValueError as exc:
        probes.append({
            "id": "P2_chart_empty_domain",
            "expected": "ValueError raised",
            "actual": f"ValueError: {exc}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        probes.append({
            "id": "P2_chart_empty_domain",
            "expected": "ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # Probe 3: CoordinateChart with colon in domain (forbidden)
    try:
        cp = CanonicalizationProtocol(
            impl="group_quotient",
            decidability_status="decidable",
            choice_dependencies=(),
            version="0.0",
        )
        chart = CoordinateChart(
            domain="lehmer:bad",  # ill-formed — colons forbidden in domain
            region_key="r1",
            coordinate_system=("x",),
            canonicalization=cp,
            metric=lambda a, b: 0.0,
            metric_id="trivial",
            equivalence_relations=(),
            admissible_region=lambda p: True,
            valid_operations=(),
        )
        probes.append({
            "id": "P3_chart_colon_in_domain",
            "expected": "ValueError raised",
            "actual": "silently accepted",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "ill_formed_aspect": "domain contains colon (would break chart_id splitting)",
        })
    except ValueError as exc:
        probes.append({
            "id": "P3_chart_colon_in_domain",
            "expected": "ValueError raised",
            "actual": f"ValueError: {exc}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        probes.append({
            "id": "P3_chart_colon_in_domain",
            "expected": "ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # Probe 4: CoordinateChart with coordinate_system as a list (must be tuple)
    try:
        cp = CanonicalizationProtocol(
            impl="group_quotient",
            decidability_status="decidable",
            choice_dependencies=(),
            version="0.0",
        )
        chart = CoordinateChart(
            domain="adversarial",
            region_key="r1",
            coordinate_system=["x", "y"],  # type: ignore  ill-formed — must be tuple
            canonicalization=cp,
            metric=lambda a, b: 0.0,
            metric_id="trivial",
            equivalence_relations=(),
            admissible_region=lambda p: True,
            valid_operations=(),
        )
        probes.append({
            "id": "P4_chart_coordsys_as_list",
            "expected": "TypeError raised",
            "actual": "silently accepted",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "ill_formed_aspect": "coordinate_system is a list, not a tuple",
        })
    except TypeError as exc:
        probes.append({
            "id": "P4_chart_coordsys_as_list",
            "expected": "TypeError raised",
            "actual": f"TypeError: {exc}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        probes.append({
            "id": "P4_chart_coordsys_as_list",
            "expected": "TypeError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # Probe 5: DiscoveryPipeline.process_candidate with non-numeric mahler_measure
    try:
        from prometheus_math.discovery_pipeline import DiscoveryPipeline
        from sigma_kernel.bind_eval_v2 import BindEvalExtension

        kernel2 = SigmaKernel()
        ext = BindEvalExtension(kernel2)
        pipe = DiscoveryPipeline(kernel=kernel2, ext=ext)
        rec = pipe.process_candidate(
            coeffs=[1, 2, 3, 2, 1],
            mahler_measure="not_a_number",  # type: ignore  ill-formed
        )
        # If we get here without exception, check whether the substrate
        # silently accepted (worst case) or routed to a kill_pattern.
        verdict_state = rec.terminal_state if rec else "no_record"
        kill_pattern = rec.kill_pattern if rec else None
        probes.append({
            "id": "P5_pipeline_string_mahler_measure",
            "expected": "TypeError or ValueError",
            "actual": f"silently accepted; terminal_state={verdict_state}, kill_pattern={kill_pattern}",
            "verdict": "FAIL",
            "severity": "P0-blocker" if verdict_state == "PROMOTED" else "P1-high",
            "ill_formed_aspect": "mahler_measure is a string, not a float",
        })
    except (TypeError, ValueError) as exc:
        probes.append({
            "id": "P5_pipeline_string_mahler_measure",
            "expected": "TypeError or ValueError",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        probes.append({
            "id": "P5_pipeline_string_mahler_measure",
            "expected": "TypeError or ValueError",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
            "note": "raised but with wrong exception class",
        })

    # Tally
    verdict_counts = Counter(p["verdict"] for p in probes)

    return {
        "lane": "2_adversarial_claim",
        "n_probes": len(probes),
        "verdict_counts": dict(verdict_counts),
        "probes": probes,
    }


# ---------------------------------------------------------------------------
# Lane 9 — NearMissCorpus-leak
# ---------------------------------------------------------------------------


def lane_9_nearmiss_leak() -> dict:
    """View-separation discipline tests for LearnerCorpusLoader.

    Per lane spec:
      - silent allow-without-flag: P0-blocker
      - allow with flag but no opt-in log: P1-high
      - refuse with flag (over-blocking): P2-normal
    """
    from prometheus_math.learner_corpus import (
        LearnerCorpusLoader,
        PostFalsificationLeakageError,
        stub_emit_from_legacy_ledger,
        write_emission_to_disk,
    )

    # Build a minimal CorpusEmission with 3 records
    legacy_records = [
        {
            "canonical_form": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],  # Lehmer
            "raw_invariants": {"degree": 10, "M": 1.176},
            "kill_vector": None,
            "operator_class": "test",
            "timestamp": time.time(),
            "label_source": "fire-2-stub",
        },
        {
            "canonical_form": [1, 0, 0, 0, 1],
            "raw_invariants": {"degree": 4, "M": 1.0},
            "kill_vector": None,
            "operator_class": "test",
            "timestamp": time.time(),
            "label_source": "fire-2-stub",
        },
        {
            "canonical_form": [1, 1, 1, 1, 1],  # Phi_5
            "raw_invariants": {"degree": 4, "M": 1.0},
            "kill_vector": None,
            "operator_class": "test",
            "timestamp": time.time(),
            "label_source": "fire-2-stub",
        },
    ]

    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp)
        emission = stub_emit_from_legacy_ledger(
            legacy_records=legacy_records,
            region_key="lehmer:adversarial:fire-2",
            label_version="substrate-tester:fire-2",
            domain="lehmer",
        )
        # Persist to disk so loader has something to read
        emission_path = write_emission_to_disk(emission, output_root)
        loader = LearnerCorpusLoader(emission_path)

        tests = []

        # Test 1: load_post_view WITHOUT allow_post_falsification flag
        # (i.e. allow_post_falsification=False, kw-only).
        try:
            list(loader.load_post_view(
                allow_post_falsification=False,
                caller_id="substrate-tester:lane-9:T1",
                purpose="audit",
            ))
            tests.append({
                "id": "T1_post_view_without_flag",
                "expected": "PostFalsificationLeakageError raised",
                "actual": "silently allowed (P0-blocker)",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
        except PostFalsificationLeakageError as exc:
            tests.append({
                "id": "T1_post_view_without_flag",
                "expected": "PostFalsificationLeakageError raised",
                "actual": f"PostFalsificationLeakageError: {str(exc)[:120]}",
                "verdict": "PASS",
                "severity": None,
            })
        except Exception as exc:
            tests.append({
                "id": "T1_post_view_without_flag",
                "expected": "PostFalsificationLeakageError raised",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "PARTIAL",
                "severity": "P3-low",
                "note": "raised but with wrong exception class",
            })

        # Test 2: load_post_view WITH allow_post_falsification=True,
        # caller_id, and purpose. Must succeed and log.
        try:
            views = list(loader.load_post_view(
                allow_post_falsification=True,
                caller_id="substrate-tester:lane-9:T2",
                purpose="audit",
            ))
            n_views = len(views)
            # Verify log entry exists
            log_events = loader.post_view_load_events()
            t2_log_entries = [
                e for e in log_events
                if e.get("caller_id") == "substrate-tester:lane-9:T2"
            ]
            log_present = len(t2_log_entries) > 0
            tests.append({
                "id": "T2_post_view_with_flag",
                "expected": "succeeds + log entry written",
                "actual": f"loaded {n_views} views; log entries for caller={len(t2_log_entries)}",
                "verdict": "PASS" if (n_views > 0 and log_present) else "FAIL",
                "severity": None if (n_views > 0 and log_present) else "P1-high",
            })
        except Exception as exc:
            tests.append({
                "id": "T2_post_view_with_flag",
                "expected": "succeeds + log entry written",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P2-normal",
                "note": "refused with flag (over-blocking)",
            })

        # Test 3: try load_post_view with positional args (must be kw-only)
        try:
            list(loader.load_post_view(
                True,  # type: ignore  positional should fail
                "substrate-tester:lane-9:T3",
                "audit",
            ))
            tests.append({
                "id": "T3_post_view_positional_args",
                "expected": "TypeError (kw-only enforcement)",
                "actual": "silently accepted positional",
                "verdict": "FAIL",
                "severity": "P1-high",
                "note": "kw-only enforcement is decorative",
            })
        except TypeError as exc:
            tests.append({
                "id": "T3_post_view_positional_args",
                "expected": "TypeError (kw-only enforcement)",
                "actual": f"TypeError: {str(exc)[:120]}",
                "verdict": "PASS",
                "severity": None,
            })
        except Exception as exc:
            tests.append({
                "id": "T3_post_view_positional_args",
                "expected": "TypeError (kw-only enforcement)",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "PARTIAL",
                "severity": "P3-low",
            })

        # Test 4: default load() yields ONLY pre-views (no post_falsification fields)
        try:
            pre_views = list(loader.load())
            # Every pre-view should be PreFalsificationView (no kill_vector etc.)
            has_post_fields = any(
                hasattr(v, "kill_vector") and getattr(v, "kill_vector", None) is not None
                for v in pre_views
            )
            tests.append({
                "id": "T4_default_load_yields_pre_only",
                "expected": "default load() returns only pre-falsification views",
                "actual": f"loaded {len(pre_views)} pre-views; any had kill_vector? {has_post_fields}",
                "verdict": "PASS" if not has_post_fields else "FAIL",
                "severity": None if not has_post_fields else "P0-blocker",
            })
        except Exception as exc:
            tests.append({
                "id": "T4_default_load_yields_pre_only",
                "expected": "default load() returns only pre-falsification views",
                "actual": f"{type(exc).__name__}: {exc}",
                "verdict": "FAIL",
                "severity": "P1-high",
            })

        verdict_counts = Counter(t["verdict"] for t in tests)

        return {
            "lane": "9_nearmiss_corpus_leak",
            "n_tests": len(tests),
            "verdict_counts": dict(verdict_counts),
            "tests": tests,
        }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #2 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 2: adversarial-CLAIM ---")
    lane2 = lane_2_adversarial_claim()
    print(f"Probes: {lane2['n_probes']}, verdicts: {lane2['verdict_counts']}")
    for p in lane2["probes"]:
        print(f"  [{p['verdict']}] {p['id']}: {p['actual'][:120]}")

    print("\n--- Lane 9: NearMissCorpus-leak ---")
    lane9 = lane_9_nearmiss_leak()
    print(f"Tests: {lane9['n_tests']}, verdicts: {lane9['verdict_counts']}")
    for t in lane9["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:120]}")

    summary = {
        "fire_id": "fire_2_2026_05_06",
        "lanes": ["2_adversarial_claim", "9_nearmiss_corpus_leak"],
        "lane_2": lane2,
        "lane_9": lane9,
    }
    out_path = out_dir / "substrate_tester_fire_2_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
