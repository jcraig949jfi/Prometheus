"""Round-trip + smuggle-attack tests for the contract-change window
2026-05-08 enum-validation hardening on MethodSpec.independence_class
and TriangulationPath.method_class.

Closes:
  - T-2026-05-07-ST-fire14-001 (P1: MethodSpec arbitrary IC strings)
  - T-2026-05-07-ST-fire17-001 (P0: TriangulationProtocol smuggle attack)
  - T-2026-05-07-ST-fire29-001 (P1: TriangulationPath arbitrary method_class)

The substrate's certification discipline (v2.3 §6.3) is now defended
at THREE layers:
  1. MethodSpec.__post_init__ rejects non-enum independence_class
  2. TriangulationPath.__post_init__ rejects non-enum method_class
  3. TriangulationProtocol.evaluate() defense-in-depth re-checks IC
     at evaluate-time before applying the independence rule
"""
from __future__ import annotations

import time

import pytest

from sigma_kernel.method_spec import IndependenceClass, MethodSpec
from sigma_kernel.triangulation_protocol import (
    MethodClass,
    TriangulationPath,
    TriangulationProtocol,
    TriangulationVerdict,
)


# ---------------------------------------------------------------------------
# MethodSpec.independence_class validation
# ---------------------------------------------------------------------------


class TestMethodSpecIndependenceClassValidation:
    """Per T-ST-fire14-001 contract change."""

    def test_enum_instance_accepted(self):
        spec = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
            version="1.0.0",
        )
        assert spec.independence_class is IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING

    def test_default_unknown_accepted(self):
        spec = MethodSpec(engine="x", strategy="y")
        assert spec.independence_class is IndependenceClass.UNKNOWN

    def test_valid_string_coerced_to_enum(self):
        spec = MethodSpec(
            engine="sympy", strategy="factor_list",
            independence_class="sympy_symbolic_factorization",  # type: ignore
            version="1.0.0",
        )
        assert spec.independence_class is IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION
        assert isinstance(spec.independence_class, IndependenceClass)

    def test_arbitrary_string_rejected_with_registered_set(self):
        with pytest.raises(ValueError, match="not a registered IndependenceClass"):
            MethodSpec(
                engine="bogus", strategy="bogus",
                independence_class="not_a_registered_class_xyz",  # type: ignore
                version="1.0.0",
            )

    def test_non_string_non_enum_rejected_with_typeerror(self):
        with pytest.raises(TypeError, match="must be an IndependenceClass"):
            MethodSpec(
                engine="bogus", strategy="bogus",
                independence_class=42,  # type: ignore
                version="1.0.0",
            )

    def test_error_message_lists_registered_values(self):
        with pytest.raises(ValueError) as excinfo:
            MethodSpec(
                engine="bogus", strategy="bogus",
                independence_class="completely_made_up",  # type: ignore
            )
        msg = str(excinfo.value)
        # Spot-check that key registered values appear in the error message
        assert "mpmath_polynomial_factorization" in msg
        assert "sympy_symbolic_factorization" in msg
        assert "unknown" in msg


# ---------------------------------------------------------------------------
# TriangulationPath.method_class validation
# ---------------------------------------------------------------------------


class TestTriangulationPathMethodClassValidation:
    """Per T-ST-fire29-001 contract change."""

    def _spec(self) -> MethodSpec:
        return MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
            version="1.0.0",
        )

    def test_enum_instance_accepted(self):
        path = TriangulationPath(
            path_id="t1",
            method_spec=self._spec(),
            method_class=MethodClass.NUMERICAL,
            verdict="verified",
            runtime_ms=10,
            rationale="r",
            timestamp=time.time(),
        )
        assert path.method_class is MethodClass.NUMERICAL

    def test_valid_string_coerced_to_enum(self):
        path = TriangulationPath(
            path_id="t2",
            method_spec=self._spec(),
            method_class="numerical",  # type: ignore
            verdict="verified",
            runtime_ms=10,
            rationale="r",
            timestamp=time.time(),
        )
        assert path.method_class is MethodClass.NUMERICAL
        assert isinstance(path.method_class, MethodClass)

    def test_arbitrary_string_rejected(self):
        with pytest.raises(ValueError, match="not a registered MethodClass"):
            TriangulationPath(
                path_id="t3",
                method_spec=self._spec(),
                method_class="not_a_method_class_enum",  # type: ignore
                verdict="verified",
                runtime_ms=10,
                rationale="r",
                timestamp=time.time(),
            )

    def test_non_string_non_enum_rejected(self):
        with pytest.raises(TypeError, match="must be a MethodClass"):
            TriangulationPath(
                path_id="t4",
                method_spec=self._spec(),
                method_class=42,  # type: ignore
                verdict="verified",
                runtime_ms=10,
                rationale="r",
                timestamp=time.time(),
            )

    def test_error_message_lists_registered_values(self):
        with pytest.raises(ValueError) as excinfo:
            TriangulationPath(
                path_id="t5",
                method_spec=self._spec(),
                method_class="bogus",  # type: ignore
                verdict="verified",
                runtime_ms=10,
                rationale="r",
                timestamp=time.time(),
            )
        msg = str(excinfo.value)
        assert "proof_bearing" in msg
        assert "numerical" in msg
        assert "exploratory" in msg


# ---------------------------------------------------------------------------
# 🔴 SMUGGLE ATTACK REPRODUCER — closes T-ST-fire17-001 P0
# ---------------------------------------------------------------------------


class TestSmuggleAttackNowFails:
    """Per T-ST-fire17-001 P0: the substrate-tester fire #17 demonstrated
    that a 3-step smuggle attack could UPGRADE a triangulation to
    LOCAL_LEMMA via an arbitrary-IC MethodSpec. Post-fix, each step in
    the chain raises at the boundary."""

    def test_step1_methodspec_with_arbitrary_ic_now_raises(self):
        """Pre-fix: silently accepted. Post-fix: ValueError at construction."""
        with pytest.raises(ValueError, match="not a registered IndependenceClass"):
            MethodSpec(
                engine="bogus_engine", strategy="bogus_strategy",
                independence_class="not_a_registered_class_xyz",  # type: ignore
                version="1.0.0",
            )

    def test_step2_triangpath_with_arbitrary_method_class_now_raises(self):
        """Even if attacker bypasses step 1 (e.g. via dict-construction or
        legacy payload), the method_class boundary still rejects arbitrary
        strings."""
        spec = MethodSpec(
            engine="x", strategy="y",
            independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
        )
        with pytest.raises(ValueError, match="not a registered MethodClass"):
            TriangulationPath(
                path_id="smuggle",
                method_spec=spec,
                method_class="not_a_method_class_enum",  # type: ignore
                verdict="verified",
                runtime_ms=10,
                rationale="r",
                timestamp=time.time(),
            )

    def test_step3_defense_in_depth_at_evaluate_time(self):
        """Last-resort: even if a path somehow carries a non-enum IC at
        evaluate-time (e.g. via runtime mutation through object.__setattr__,
        legacy unpickle, etc.), the protocol REJECTS the upgrade rather
        than silently treating the bogus IC as 'different from primary'."""
        # Construct three valid paths first.
        spec_proof = MethodSpec(
            engine="sympy", strategy="factor_list",
            independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        )
        spec_num = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
        )
        spec_cat = MethodSpec(
            engine="lmfdb", strategy="lookup",
            independence_class=IndependenceClass.LMFDB_CATALOG,
        )
        path_primary = TriangulationPath(
            path_id="primary",
            method_spec=spec_proof,
            method_class=MethodClass.PROOF_BEARING,
            verdict="verified",
            runtime_ms=10,
            rationale="primary",
            timestamp=time.time(),
        )
        path_real_other = TriangulationPath(
            path_id="real_other",
            method_spec=spec_num,
            method_class=MethodClass.NUMERICAL,
            verdict="verified",
            runtime_ms=15,
            rationale="other",
            timestamp=time.time(),
        )
        # Now construct the THIRD path, then mutate its IC to an arbitrary
        # string AFTER construction (simulating a legacy unpickle or
        # adversarial mutation path that bypasses __post_init__).
        path_smuggled = TriangulationPath(
            path_id="smuggled",
            method_spec=spec_cat,
            method_class=MethodClass.CATALOG,
            verdict="verified",
            runtime_ms=20,
            rationale="smuggled",
            timestamp=time.time(),
        )
        # Force a bypass: mutate the inner MethodSpec's independence_class
        # via object.__setattr__ to a bogus string, simulating the attack.
        object.__setattr__(
            path_smuggled.method_spec,
            "independence_class",
            "post_construction_arbitrary_ic_string",
        )

        # Now run the protocol. Pre-fix: this might have UPGRADED. Post-fix:
        # the defense-in-depth check refuses.
        protocol = TriangulationProtocol()
        result = protocol.evaluate([path_primary, path_real_other, path_smuggled])

        assert result.upgrade_eligible is False, (
            "Defense-in-depth FAILED: protocol still upgraded despite "
            "non-enum IC on smuggled path."
        )
        assert result.verdict == TriangulationVerdict.REJECTED
        assert "Defense-in-depth violation" in result.summary
        assert "smuggled" in result.summary

    def test_clean_three_real_paths_still_upgrade(self):
        """Sanity: post-fix, a CLEAN 3-path triangulation with all-real ICs
        still UPGRADES. The hardening doesn't over-block legitimate paths."""
        spec_proof = MethodSpec(
            engine="sympy", strategy="factor_list",
            independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
        )
        spec_num = MethodSpec(
            engine="mpmath", strategy="polyroots",
            independence_class=IndependenceClass.MPMATH_NUMERICAL_ROOT_FINDING,
        )
        spec_cat = MethodSpec(
            engine="lmfdb", strategy="lookup",
            independence_class=IndependenceClass.LMFDB_CATALOG,
        )
        paths = [
            TriangulationPath(
                path_id="p1", method_spec=spec_proof,
                method_class=MethodClass.PROOF_BEARING,
                verdict="verified", runtime_ms=10, rationale="r",
                timestamp=time.time(),
            ),
            TriangulationPath(
                path_id="p2", method_spec=spec_num,
                method_class=MethodClass.NUMERICAL,
                verdict="verified", runtime_ms=15, rationale="r",
                timestamp=time.time(),
            ),
            TriangulationPath(
                path_id="p3", method_spec=spec_cat,
                method_class=MethodClass.CATALOG,
                verdict="verified", runtime_ms=20, rationale="r",
                timestamp=time.time(),
            ),
        ]
        protocol = TriangulationProtocol()
        result = protocol.evaluate(paths)
        assert result.verdict == TriangulationVerdict.UPGRADED_TO_LOCAL_LEMMA
        assert result.upgrade_eligible is True
