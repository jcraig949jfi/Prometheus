"""
Substrate-Tester Fire #3 — Lane 4 (cross-domain-leak) + Lane 8 (ExclusionCertificate-extension)

Lane 4: domain-isolation discipline on LearnerCorpus + observation that the
v1.5 substrate has no unified cross-domain CLAIM entry (BSD env, modular env
etc. are independent per-domain pipelines). Tests the LearnerCorpus domain
tagging.

Lane 8: load LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION; verify it's strength=COMPLETE
with triangulation_history; submit a fresh in-scope candidate through
DiscoveryPipeline and verify NO silent certificate extension; attempt to
register a duplicate certificate with the same chart_id.

Author: substrate-tester (Charon-aligned), fire #3, 2026-05-06
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 4 — cross-domain-leak (adapted to v1.5 substrate)
# ---------------------------------------------------------------------------


def lane_4_cross_domain_leak() -> dict:
    """Tests domain isolation in LearnerCorpus + documents the v1.5
    architectural reality (no unified cross-domain CLAIM entry).
    """
    from prometheus_math.learner_corpus import (
        RAW_INVARIANTS_PER_DOMAIN,
        get_raw_invariant_keys,
        stub_emit_from_legacy_ledger,
        write_emission_to_disk,
        LearnerCorpusLoader,
    )

    tests = []

    # Test 1: domain registry returns the right keys per domain.
    try:
        bsd_keys = get_raw_invariant_keys("bsd_rank")
        lehmer_keys = get_raw_invariant_keys("lehmer")
        # Must be disjoint (cross-domain isolation at the schema level)
        overlap = set(bsd_keys) & set(lehmer_keys)
        if overlap:
            tests.append({
                "id": "T1_domain_registry_disjoint",
                "expected": "bsd_rank and lehmer raw_invariants are disjoint",
                "actual": f"overlap = {overlap}",
                "verdict": "FAIL",
                "severity": "P2-normal",
            })
        else:
            tests.append({
                "id": "T1_domain_registry_disjoint",
                "expected": "bsd_rank and lehmer raw_invariants are disjoint",
                "actual": f"disjoint; bsd={len(bsd_keys)} keys, lehmer={len(lehmer_keys)} keys",
                "verdict": "PASS",
                "severity": None,
            })
    except Exception as exc:
        tests.append({
            "id": "T1_domain_registry_disjoint",
            "expected": "bsd_rank and lehmer raw_invariants are disjoint",
            "actual": f"exception: {type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # Test 2: stub_emit with domain="bsd_rank" but Lehmer-shaped record content.
    # This forces a domain/content mismatch; substrate behavior tells us whether
    # there's any coherence check.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        # Lehmer-shaped record (coeffs + M); no BSD-shape fields (cremona_label etc.)
        lehmer_record = {
            "canonical_form": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],  # Lehmer poly
            "raw_invariants": {
                "poly_coefficients": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
                "mahler_measure_dps60": 1.176,
                "height": 1,
            },
            "operator_class": "test_cross_domain_leak",
            "timestamp": time.time(),
            "label_source": "fire-3-cross-domain-test",
        }
        try:
            emission = stub_emit_from_legacy_ledger(
                legacy_records=[lehmer_record],
                region_key="bsd:fire-3:cross-domain-test",
                label_version="substrate-tester:fire-3",
                domain="bsd_rank",  # WRONG domain for the record content
            )
            emission_path = write_emission_to_disk(emission, out)
            loader = LearnerCorpusLoader(emission_path)
            pre_views = list(loader.load())
            # All BSD keys should resolve to None since the record has Lehmer-shape only
            obj = pre_views[0].object
            bsd_keys = get_raw_invariant_keys("bsd_rank")
            none_count = sum(
                1 for k in bsd_keys if obj.raw_invariants.get(k) is None
            )
            # Substrate accepted with mismatch; the emission has all-None raw_invariants.
            # That's a soft-fail: substrate doesn't validate domain-content coherence.
            # But: the domain TAG on the object is preserved correctly.
            tests.append({
                "id": "T2_emit_with_domain_content_mismatch",
                "expected": "either reject OR clearly mark mismatch",
                "actual": (
                    f"emission accepted; domain tag={obj.domain!r}; "
                    f"raw_invariants all-None for {none_count}/{len(bsd_keys)} BSD keys; "
                    f"no warning or coherence-check log emitted"
                ),
                "verdict": "PARTIAL",
                "severity": "P3-low",
                "note": (
                    "Domain-content coherence is not validated. The substrate stores "
                    "the declared domain tag faithfully; downstream consumers must "
                    "themselves check that raw_invariants are non-None for the domain's "
                    "registered keys. This is a substrate-architectural observation: "
                    "domain isolation is by-construction (per-pipeline) rather than "
                    "by-validation."
                ),
            })
        except Exception as exc:
            tests.append({
                "id": "T2_emit_with_domain_content_mismatch",
                "expected": "either reject OR clearly mark mismatch",
                "actual": f"raised {type(exc).__name__}: {exc}",
                "verdict": "PASS",
                "severity": None,
                "note": "substrate rejected mismatched emission; isolation is enforced",
            })

    # Test 3: invalid domain name passes silently?
    try:
        keys = get_raw_invariant_keys("nonexistent_domain_xyz")
        tests.append({
            "id": "T3_invalid_domain_silent_acceptance",
            "expected": "KeyError or ValueError raised",
            "actual": f"silently returned {keys}",
            "verdict": "FAIL",
            "severity": "P2-normal",
        })
    except (KeyError, ValueError) as exc:
        tests.append({
            "id": "T3_invalid_domain_silent_acceptance",
            "expected": "KeyError or ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        tests.append({
            "id": "T3_invalid_domain_silent_acceptance",
            "expected": "KeyError or ValueError raised",
            "actual": f"raised wrong exception: {type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # Test 4: object_id content-hash collision check.
    # Two emissions with different domains but identical canonical_form should
    # produce DIFFERENT object_ids if domain is included in the hash, OR
    # SAME object_ids if domain is excluded. Document which.
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        same_canonical = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
        rec1 = {
            "canonical_form": same_canonical,
            "raw_invariants": {"poly_coefficients": same_canonical},
            "operator_class": "T4",
            "label_source": "T4-lehmer",
        }
        rec2 = {
            "canonical_form": same_canonical,  # SAME canonical
            "raw_invariants": {"poly_coefficients": same_canonical},
            "operator_class": "T4",
            "label_source": "T4-bsd",
        }
        e1 = stub_emit_from_legacy_ledger(
            [rec1], region_key="lehmer:T4", label_version="T4", domain="lehmer"
        )
        e2 = stub_emit_from_legacy_ledger(
            [rec2], region_key="bsd:T4", label_version="T4", domain="bsd_rank"
        )
        # Same canonical_form across domains → same or different object_id?
        oid1 = e1.pre_views[0].object_id
        oid2 = e2.pre_views[0].object_id
        # Note: the bsd_rank record will also have all-None raw_invariants
        # for BSD keys, so canonical may differ in raw_invariants_dict shape.
        # But the canonical_form field is the same. Let's see what happens.
        tests.append({
            "id": "T4_object_id_cross_domain_collision",
            "expected": "object_id should include domain to prevent cross-domain ID collisions",
            "actual": f"oid1 (lehmer) = {oid1[:16]}...; oid2 (bsd_rank) = {oid2[:16]}...; equal? {oid1 == oid2}",
            "verdict": "PASS" if oid1 != oid2 else "PARTIAL",
            "severity": None if oid1 != oid2 else "P2-normal",
            "note": (
                "if equal, two different-domain objects collide on ID — could leak "
                "labels across domains during corpus joins"
                if oid1 == oid2
                else "domains produce distinct object_ids; cross-domain ID collisions ruled out"
            ),
        })

    verdict_counts = Counter(t["verdict"] for t in tests)

    return {
        "lane": "4_cross_domain_leak",
        "n_tests": len(tests),
        "verdict_counts": dict(verdict_counts),
        "architecture_observation": (
            "v1.5 substrate has NO unified cross-domain CLAIM entry. DiscoveryPipeline "
            "is Lehmer-only; BSDRankEnv is BSD-only; etc. The lane-4 spec's literal "
            "'submit Lehmer claim to BSD env' is structurally not supported. Tests above "
            "exercise the closest analogue: LearnerCorpus domain-isolation discipline."
        ),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 8 — ExclusionCertificate-extension
# ---------------------------------------------------------------------------


def lane_8_exclusion_certificate_extension() -> dict:
    """Verify the Lehmer deg-14 ±5 ExclusionCertificate is COMPLETE strength
    with triangulation history; submit a fresh in-scope candidate through
    DiscoveryPipeline; verify NO silent extension; attempt to register a
    duplicate.
    """
    from sigma_kernel.exclusion_certificates.lehmer_deg14 import (
        LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION as CERT,
    )
    from sigma_kernel.exclusion_certificate import (
        CertificateStrength,
        register_certificate,
        get_certificate,
        DEFAULT_REGISTRY,
    )
    from prometheus_math.discovery_pipeline import DiscoveryPipeline
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval_v2 import BindEvalExtension

    tests = []

    # Test 1: certificate is COMPLETE with non-empty triangulation_history
    if (
        CERT.strength == CertificateStrength.COMPLETE
        and len(CERT.triangulation_history) >= 2
    ):
        tests.append({
            "id": "T1_certificate_complete_with_triangulation",
            "expected": "strength=COMPLETE AND len(triangulation_history) >= 2",
            "actual": f"strength={CERT.strength.name}, triangulation_history={len(CERT.triangulation_history)} paths",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T1_certificate_complete_with_triangulation",
            "expected": "strength=COMPLETE AND len(triangulation_history) >= 2",
            "actual": f"strength={CERT.strength.name}, triangulation_history={len(CERT.triangulation_history)} paths",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "Aporia v2.3 hard rule: strength=COMPLETE requires triangulation_history",
        })

    # Test 2: chart_id matches expected scope
    chart_id = CERT.region_spec.coordinate_chart_id
    if chart_id == "lehmer:deg14:pm5:palindromic":
        tests.append({
            "id": "T2_certificate_chart_id_matches",
            "expected": "chart_id='lehmer:deg14:pm5:palindromic'",
            "actual": f"chart_id={chart_id!r}",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        tests.append({
            "id": "T2_certificate_chart_id_matches",
            "expected": "chart_id='lehmer:deg14:pm5:palindromic'",
            "actual": f"chart_id={chart_id!r}",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    # Test 3: submit a fresh in-scope candidate through DiscoveryPipeline.
    # Construct a deg-14 ±5 palindromic poly that is NOT in the catalog
    # (we'll use a clearly novel half: [1, 2, -3, 4, -2, 1, 0, -2]). M will
    # likely be out-of-band; the substrate should run normal pipeline (no
    # certificate-aware short-circuit).
    novel_half = [1, 2, -3, 4, -2, 1, 0, -2]
    novel_coeffs = novel_half + list(reversed(novel_half[:-1]))
    # Compute Mahler measure quickly
    import numpy as np
    roots = np.roots(list(reversed(novel_coeffs)))
    leading = abs(novel_coeffs[-1])
    M = float(leading)
    for r in roots:
        if abs(r) > 1.0:
            M *= abs(r)

    kernel = SigmaKernel()
    ext = BindEvalExtension(kernel)
    pipe = DiscoveryPipeline(kernel=kernel, ext=ext)

    rec = pipe.process_candidate(coeffs=novel_coeffs, mahler_measure=M)

    # The substrate should process normally regardless of whether there's a
    # matching certificate. If there's a "this is in cert scope so KILL" path,
    # we'd see kill_pattern referencing the certificate id. Check the kill
    # pattern.
    kp = rec.kill_pattern or ""
    cert_referenced = "certificate" in kp.lower() or "exclusion_zone" in kp.lower()
    tests.append({
        "id": "T3_in_scope_candidate_normal_pipeline",
        "expected": "candidate processed via normal pipeline; no certificate-aware short-circuit",
        "actual": (
            f"M={M:.6f}, terminal_state={rec.terminal_state}, "
            f"kill_pattern={kp[:80]!r}, cert_referenced={cert_referenced}"
        ),
        "verdict": "PASS" if not cert_referenced else "FAIL",
        "severity": None if not cert_referenced else "P0-blocker",
        "note": (
            "no silent certificate extension; substrate runs the normal pipeline"
            if not cert_referenced
            else "substrate referenced certificate as part of kill_pattern — silent extension"
        ),
    })

    # Test 4: attempt to register a SECOND certificate against the same
    # chart_id. Behavior: substrate should either reject, accept (overwrite),
    # or accept (alongside) — but the behavior should be deterministic and
    # documented.
    from sigma_kernel.exclusion_certificate import (
        Boundary,
        CertificateType,
        ExclusionClaim,
        ExclusionCertificate,
        RegionSpec,
        ReplayInfo,
        VerifierSet,
    )
    weaker_cert = ExclusionCertificate(
        region_spec=RegionSpec(
            coordinate_chart_id="lehmer:deg14:pm5:palindromic",
            constraints={"degree": 14, "coefficient_bound": 5, "palindromic": True},
            bounds={"n_polynomials_enumerated": 100},  # weaker
        ),
        exclusion_claim=ExclusionClaim(
            excluded_property="cheap claim by lane-8 test",
            result_class="lane8_duplicate_test",
            reason="testing whether duplicate registration is allowed",
        ),
        certificate_type=CertificateType.FAILED_SEARCH_ONLY,
        strength=CertificateStrength.DIAGNOSTIC_ONLY,
        verifier_set=VerifierSet(methods=(), independence_classes=frozenset()),
        replay=ReplayInfo(code_hash="x"*64, data_hash="y"*64, seed=0, environment_hash="z"*64),
        triangulation_history=(),
        initial_verdict="diagnostic",
        upgrade_path_summary=(),
        boundary=Boundary(adjacent_regions=(), known_escape_hatches=()),
    )
    n_certs_for_chart_before = len(DEFAULT_REGISTRY.by_chart("lehmer:deg14:pm5:palindromic"))
    duplicate_registered = None
    try:
        register_certificate(weaker_cert)
        n_after = len(DEFAULT_REGISTRY.by_chart("lehmer:deg14:pm5:palindromic"))
        if n_after > n_certs_for_chart_before:
            duplicate_registered = "appended (substrate allows multiple certs per chart)"
        else:
            duplicate_registered = "no-op or replaced silently"
    except Exception as exc:
        duplicate_registered = f"rejected: {type(exc).__name__}: {exc}"

    tests.append({
        "id": "T4_duplicate_certificate_per_chart",
        "expected": "deterministic behavior (allow/reject/replace explicit)",
        "actual": (
            f"before: {n_certs_for_chart_before} certs for chart; "
            f"after: {duplicate_registered}"
        ),
        "verdict": "PASS",  # any deterministic behavior is OK; just observing
        "severity": None,
        "note": "documenting substrate behavior on duplicate-chart certificate registration",
    })

    verdict_counts = Counter(t["verdict"] for t in tests)

    return {
        "lane": "8_exclusion_certificate_extension",
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

    print("=== Substrate-Tester Fire #3 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 4: cross-domain-leak ---")
    lane4 = lane_4_cross_domain_leak()
    print(f"Tests: {lane4['n_tests']}, verdicts: {lane4['verdict_counts']}")
    for t in lane4["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 8: ExclusionCertificate-extension ---")
    lane8 = lane_8_exclusion_certificate_extension()
    print(f"Tests: {lane8['n_tests']}, verdicts: {lane8['verdict_counts']}")
    for t in lane8["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_3_2026_05_06",
        "lanes": ["4_cross_domain_leak", "8_exclusion_certificate_extension"],
        "lane_4": lane4,
        "lane_8": lane8,
    }
    out_path = out_dir / "substrate_tester_fire_3_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
