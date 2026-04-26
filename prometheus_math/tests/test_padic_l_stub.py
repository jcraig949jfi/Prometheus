"""Tests for the Phase-1 stub of pm.elliptic_curves.padic_l_function.

Project #38 Phase 1 — literature survey + stubbed API surface.

The stub is required to:
1. Be importable from ``prometheus_math.elliptic_curves``.
2. Validate inputs aggressively (ainvs length, p primality, precision >= 0).
3. Raise ``NotImplementedError`` with a message pointing to the survey doc
   at ``techne/whitepapers/padic_l_survey.md`` once validation passes.
4. Coexist with all existing pm.elliptic_curves operations
   (faltings_height, conductor, etc.).

Run: pytest prometheus_math/tests/test_padic_l_stub.py -v
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from prometheus_math import elliptic_curves as ec
from prometheus_math.elliptic_curves import padic_l_function


# Test inputs that should pass validation. Ainvs of 11.a3, conductor 11,
# and p = 5 (good ordinary). The call still raises NotImplementedError.
_VALID_AINVS_11A3 = [0, -1, 1, 0, 0]


# ---------------------------------------------------------------------------
# AUTHORITY TESTS — stub behaviour and pointer to survey doc.
# ---------------------------------------------------------------------------

class TestAuthority:
    """Authoritative claims the stub must honor in Phase 1."""

    def test_stub_raises_not_implemented_with_pointer_message(self):
        """Stub raises NotImplementedError citing the survey path."""
        with pytest.raises(NotImplementedError) as excinfo:
            padic_l_function(_VALID_AINVS_11A3, 5)
        msg = str(excinfo.value)
        assert "padic_l_survey.md" in msg, (
            f"NotImplementedError must point to the survey whitepaper; "
            f"got: {msg}"
        )
        assert "Phase" in msg, (
            f"Message must reference upcoming phases; got: {msg}"
        )

    def test_docstring_cites_survey(self):
        """Docstring of padic_l_function must mention the survey doc."""
        doc = inspect.getdoc(padic_l_function) or ""
        assert "padic_l_survey.md" in doc, (
            f"Docstring must cite techne/whitepapers/padic_l_survey.md; "
            f"got docstring of length {len(doc)}: {doc[:200]!r}"
        )

    def test_survey_whitepaper_exists_on_disk(self):
        """The survey whitepaper must be present at the cited path."""
        # The repo root is two levels above this test file:
        # F:/Prometheus/prometheus_math/tests/test_padic_l_stub.py
        # -> F:/Prometheus/
        repo_root = Path(__file__).resolve().parent.parent.parent
        survey_path = repo_root / "techne" / "whitepapers" / "padic_l_survey.md"
        assert survey_path.is_file(), (
            f"Survey whitepaper expected at {survey_path}; not found."
        )
        # Sanity: the whitepaper should be substantial (>= 400 lines).
        line_count = sum(1 for _ in survey_path.open(encoding="utf-8"))
        assert line_count >= 400, (
            f"Survey whitepaper at {survey_path} has only {line_count} "
            f"lines; expected >= 400 for a Phase-1 deliverable."
        )


# ---------------------------------------------------------------------------
# PROPERTY TESTS — stub-as-API-surface.
# ---------------------------------------------------------------------------

class TestProperties:
    """Universal properties of the stub function."""

    def test_function_is_importable_from_pm_elliptic_curves(self):
        """``from prometheus_math.elliptic_curves import padic_l_function``
        must succeed and bind to a callable."""
        from prometheus_math.elliptic_curves import padic_l_function as fn
        assert callable(fn), f"padic_l_function is not callable: {fn!r}"

    def test_function_in_module_dunder_all(self):
        """The stub must be advertised in the module's ``__all__``."""
        assert "padic_l_function" in ec.__all__, (
            f"padic_l_function missing from __all__: {ec.__all__}"
        )

    def test_stub_accepts_5_integer_ainvs(self):
        """A length-5 list of integers passes validation
        (proceeding to the NotImplementedError)."""
        # 14.a4 — another canonical optimal curve.
        for ainvs in [
            [0, -1, 1, 0, 0],     # 11.a3
            [1, 0, 1, 4, -6],     # 14.a4
            [1, -1, 1, -1, -14],  # 17.a4
            [0, 0, 1, -1, 0],     # 37.a1
        ]:
            with pytest.raises(NotImplementedError):
                padic_l_function(ainvs, 5)

    def test_stub_signature_matches_survey_appendix_b(self):
        """The stub's signature matches the contract specified in the
        survey's Appendix B: ``(ainvs, p, T_precision=10, M_precision=20,
        prec='auto')``."""
        sig = inspect.signature(padic_l_function)
        params = list(sig.parameters.values())
        names = [p.name for p in params]
        assert names == ["ainvs", "p", "T_precision", "M_precision", "prec"], (
            f"Phase-2 contract requires the signature in survey Appendix B; "
            f"got names {names}"
        )
        # Defaults for the kwargs.
        assert sig.parameters["T_precision"].default == 10
        assert sig.parameters["M_precision"].default == 20
        assert sig.parameters["prec"].default == "auto"


# ---------------------------------------------------------------------------
# EDGE TESTS — input validation precedes the NotImplementedError.
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Validation must reject malformed inputs with ValueError, *before*
    the NotImplementedError fires. Phase-2 will inherit this behavior."""

    def test_ainvs_with_4_entries_raises_value_error(self):
        """Length-4 ainvs (missing one Weierstrass coefficient) ->
        ValueError, not NotImplementedError."""
        with pytest.raises(ValueError, match="length-5"):
            padic_l_function([0, -1, 1, 0], 5)

    def test_ainvs_with_6_entries_raises_value_error(self):
        """Length-6 ainvs (over-specified) -> ValueError."""
        with pytest.raises(ValueError, match="length-5"):
            padic_l_function([0, -1, 1, 0, 0, 0], 5)

    def test_ainvs_with_non_integer_entry_raises_value_error(self):
        """Float in ainvs -> ValueError."""
        with pytest.raises(ValueError, match="integers"):
            padic_l_function([0, -1.5, 1, 0, 0], 5)

    def test_non_prime_p_raises_value_error(self):
        """p = 4 is composite; must reject before NotImplementedError."""
        with pytest.raises(ValueError, match="not prime"):
            padic_l_function(_VALID_AINVS_11A3, 4)

    def test_non_prime_p_9_raises_value_error(self):
        """p = 9 is a prime power but not prime."""
        with pytest.raises(ValueError, match="not prime"):
            padic_l_function(_VALID_AINVS_11A3, 9)

    def test_p_too_small_raises_value_error(self):
        """p must be >= 2."""
        with pytest.raises(ValueError, match="prime"):
            padic_l_function(_VALID_AINVS_11A3, 1)
        with pytest.raises(ValueError, match="prime"):
            padic_l_function(_VALID_AINVS_11A3, 0)
        with pytest.raises(ValueError, match="prime"):
            padic_l_function(_VALID_AINVS_11A3, -3)

    def test_negative_t_precision_raises_value_error(self):
        """T_precision < 0 is meaningless (it is a truncation order)."""
        with pytest.raises(ValueError, match="T_precision"):
            padic_l_function(_VALID_AINVS_11A3, 5, T_precision=-1)
        with pytest.raises(ValueError, match="T_precision"):
            padic_l_function(_VALID_AINVS_11A3, 5, T_precision=-100)

    def test_zero_or_negative_m_precision_raises_value_error(self):
        """M_precision must be >= 1."""
        with pytest.raises(ValueError, match="M_precision"):
            padic_l_function(_VALID_AINVS_11A3, 5, M_precision=0)
        with pytest.raises(ValueError, match="M_precision"):
            padic_l_function(_VALID_AINVS_11A3, 5, M_precision=-5)

    def test_invalid_prec_string_raises_value_error(self):
        """prec must be one of {ordinary, supersingular, auto}."""
        with pytest.raises(ValueError, match="prec"):
            padic_l_function(_VALID_AINVS_11A3, 5, prec="multiplicative")
        with pytest.raises(ValueError, match="prec"):
            padic_l_function(_VALID_AINVS_11A3, 5, prec="")

    def test_t_precision_zero_passes_validation(self):
        """T_precision = 0 is valid (degenerate but non-negative); the
        call must reach the NotImplementedError, not a ValueError."""
        with pytest.raises(NotImplementedError):
            padic_l_function(_VALID_AINVS_11A3, 5, T_precision=0)


# ---------------------------------------------------------------------------
# COMPOSITION TESTS — stub coexists with the rest of pm.elliptic_curves.
# ---------------------------------------------------------------------------

class TestComposition:
    """The stub must not break the existing arsenal."""

    def test_faltings_height_still_callable_after_stub_import(self):
        """Adding the stub did not break ``faltings_height``."""
        from prometheus_math.elliptic_curves import faltings_height
        # 11.a3 has known Faltings height (PARI value, see existing tests).
        h = faltings_height([0, -1, 1, 0, 0])
        assert isinstance(h, float)
        # Sanity: faltings height is bounded for cond <= 100 curves.
        assert -10.0 < h < 10.0, f"faltings_height(11.a3) out of range: {h}"

    def test_conductor_still_callable_after_stub_import(self):
        """Adding the stub did not break ``conductor``."""
        from prometheus_math.elliptic_curves import conductor
        N = conductor([0, -1, 1, 0, 0])  # 11.a3
        assert N == 11, f"conductor(11.a3) should be 11; got {N}"

    def test_root_number_still_callable_after_stub_import(self):
        """Adding the stub did not break ``root_number``."""
        from prometheus_math.elliptic_curves import root_number
        w = root_number([0, -1, 1, 0, 0])  # 11.a3 has w(E) = +1
        assert w in (-1, 1), f"root_number(11.a3) must be +/-1; got {w}"

    def test_module_all_includes_legacy_plus_stub(self):
        """``__all__`` contains both the legacy operations and the new
        stub (no exclusivity)."""
        legacy = {
            "regulator", "conductor", "root_number", "analytic_sha",
            "selmer_2_rank", "faltings_height",
        }
        for name in legacy:
            assert name in ec.__all__, (
                f"Legacy operation {name} dropped from __all__: {ec.__all__}"
            )
        assert "padic_l_function" in ec.__all__
