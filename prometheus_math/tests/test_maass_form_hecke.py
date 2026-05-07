"""Tests for prometheus_math.encodings.maass_form_hecke — T-2026-05-07-T023."""
from __future__ import annotations

import pytest

from prometheus_math.encodings.maass_form_hecke import (
    OperatorOutputSequence,
    SerializedMpf,
)


# ---------------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------------


class TestOperatorOutputSequenceConstruction:
    def _basic(self, **overrides) -> OperatorOutputSequence:
        kwargs = dict(
            operator_id="hecke_eigenvalue",
            index_parameter_name="prime",
            index_values=(2, 3, 5, 7),
            output_values=("1.5491353837", "0.2456789012", "-0.4012345678", "0.8765432109"),
            output_precision_dps=10,
            output_unit="real_eigenvalue",
            object_canonical_form={"level": 1, "weight": 0, "label": "Selberg_PSL2Z"},
            chart_id="harmonic_analysis:maass_form:Selberg_PSL2Z",
            notes="Selberg's classic Maass form on PSL2(Z) — placeholder values",
        )
        kwargs.update(overrides)
        return OperatorOutputSequence(**kwargs)

    def test_basic_construction(self):
        s = self._basic()
        assert s.operator_id == "hecke_eigenvalue"
        assert len(s) == 4

    def test_empty_operator_id_raises(self):
        with pytest.raises(ValueError, match="operator_id"):
            self._basic(operator_id="")

    def test_index_output_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="same length"):
            self._basic(
                index_values=(2, 3, 5),  # 3
                output_values=("1.5", "0.2"),  # 2
            )

    def test_non_int_indices_raise(self):
        with pytest.raises(TypeError, match="index_values entries"):
            self._basic(
                index_values=("two", "three"),  # type: ignore
                output_values=("1.5", "0.2"),
            )

    def test_non_string_outputs_raise(self):
        with pytest.raises(TypeError, match="output_values entries"):
            self._basic(
                index_values=(2, 3),
                output_values=(1.5, 0.2),  # type: ignore — must be strings
            )

    def test_zero_precision_raises(self):
        with pytest.raises(ValueError, match="output_precision_dps"):
            self._basic(output_precision_dps=0)

    def test_non_mapping_canonical_form_raises(self):
        with pytest.raises(TypeError, match="object_canonical_form"):
            self._basic(object_canonical_form=[("level", 1)])  # type: ignore

    def test_non_tuple_indices_raise(self):
        with pytest.raises(TypeError, match="index_values"):
            self._basic(
                index_values=[2, 3, 5, 7],  # type: ignore — list not tuple
                output_values=("a", "b", "c", "d"),
            )


# ---------------------------------------------------------------------------
# lookup / has_index
# ---------------------------------------------------------------------------


class TestLookup:
    def _seq(self) -> OperatorOutputSequence:
        return OperatorOutputSequence(
            operator_id="hecke_eigenvalue",
            index_parameter_name="prime",
            index_values=(2, 3, 5, 7, 11),
            output_values=("a", "b", "c", "d", "e"),
            output_precision_dps=10,
            output_unit="real_eigenvalue",
            object_canonical_form={"label": "test"},
            chart_id="harmonic_analysis:maass_form:test",
        )

    def test_lookup_returns_correct_value(self):
        s = self._seq()
        assert s.lookup(2) == "a"
        assert s.lookup(7) == "d"
        assert s.lookup(11) == "e"

    def test_lookup_unknown_index_raises_keyerror(self):
        """Per 2026-05-07 contract-change window loud-fail-on-typo
        discipline (T-2026-05-06-ST003 + T-2026-05-07-T018 sister
        pattern): unknown index raises KeyError instead of returning
        a sentinel."""
        s = self._seq()
        with pytest.raises(KeyError, match="not in sequence"):
            s.lookup(13)

    def test_has_index_optional_check(self):
        s = self._seq()
        assert s.has_index(2) is True
        assert s.has_index(13) is False


# ---------------------------------------------------------------------------
# Round-trip + worked example
# ---------------------------------------------------------------------------


class TestSelbergMaassFormWorkedExample:
    def test_selberg_maass_form_encoding_roundtrips(self):
        """Per HARD-4 (calibration anchor density in under-explored
        harmonic-analysis territory) + HARD-5 ((object, operator-output)
        pairs, NOT discipline labels): encode Selberg's classic Maass
        form on PSL2(Z) as an OperatorOutputSequence with the first 6
        Hecke eigenvalues at small primes. (Values are placeholders; a
        future Charon/Mnemosyne LMFDB-ingestion ticket populates real
        values.)"""
        seq = OperatorOutputSequence(
            operator_id="hecke_eigenvalue",
            index_parameter_name="prime",
            index_values=(2, 3, 5, 7, 11, 13),
            output_values=(
                "1.5491353837000000",  # placeholder; real values from LMFDB
                "0.2456789012000000",
                "-0.4012345678000000",
                "0.8765432109000000",
                "-1.2345678901000000",
                "0.5678901234000000",
            ),
            output_precision_dps=16,
            output_unit="real_eigenvalue",
            object_canonical_form={
                "level": 1,
                "weight": 0,
                "archimedean_type": "real_analytic",
                "eigenvalue_label": "Selberg_PSL2Z",
            },
            chart_id="harmonic_analysis:maass_form:Selberg_PSL2Z",
            notes=(
                "Selberg's classic Maass form on the modular surface PSL2(Z)\\H. "
                "Placeholder eigenvalues; real LMFDB values pending ingestion. "
                "Per HARD-5: 'Maass form' is the discipline label (in this notes "
                "field); the substrate's coordinate is the (Hecke eigenvalue at "
                "prime p) sequence shape, NOT the discipline category."
            ),
        )
        # Round-trip through lookup
        assert seq.lookup(2) == "1.5491353837000000"
        assert seq.lookup(13) == "0.5678901234000000"
        # Provenance: chart and operator are addressable substrate keys
        assert seq.chart_id == "harmonic_analysis:maass_form:Selberg_PSL2Z"
        assert seq.operator_id == "hecke_eigenvalue"
