"""Smoke tests for aporia/scripts/parse_substrate_blocks.py.

Covers the four recognized emission conventions:
  - Strict marker (`# substrate_block: <type>`, the documented preferred shape)
  - C1: substrate_type as field inside the YAML body (DR-001 pilot shape)
  - C2: block_type as the single top-level YAML key (DR-007 pilot shape)
  - C3: schema field on each item of a JSON array (DR-231 pilot shape)

Per Track 4 finding 2026-05-13: the pilot model emitted 16 substrate-shaped
blocks across 3 reports using three different conventions, none matching the
strict marker. Parser hardening at consumption time recognizes all four.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_APORIA_SCRIPTS = Path(__file__).resolve().parents[2] / "aporia" / "scripts"
sys.path.insert(0, str(_APORIA_SCRIPTS))

from parse_substrate_blocks import (  # noqa: E402
    KNOWN_BLOCK_TYPES,
    _detect_alt_convention,
    iter_blocks_in_text,
)


class TestDetectAltConvention:
    def test_returns_none_for_plain_dict(self):
        assert _detect_alt_convention({"foo": "bar"}) is None

    def test_returns_none_for_non_dict(self):
        assert _detect_alt_convention([1, 2, 3]) is None
        assert _detect_alt_convention("string") is None
        assert _detect_alt_convention(None) is None

    def test_c1_substrate_type_field(self):
        doc = {
            "substrate_type": "anti_anchor",
            "_schema_version": "1.0.0",
            "id": "AA-013",
            "name": "STRASSEN_ADDITIVITY_FOO",
        }
        result = _detect_alt_convention(doc)
        assert result is not None
        bt, payload = result
        assert bt == "anti_anchor"
        assert "substrate_type" not in payload
        assert payload["id"] == "AA-013"

    def test_c1_unknown_substrate_type_returns_none(self):
        doc = {"substrate_type": "fake_block_type", "id": "X"}
        assert _detect_alt_convention(doc) is None

    def test_c2_block_type_as_only_key(self):
        doc = {
            "training_anchor": {
                "_schema_version": "1.0.0",
                "id": "anchor-knots-001",
                "domain": "knots",
            }
        }
        result = _detect_alt_convention(doc)
        assert result is not None
        bt, payload = result
        assert bt == "training_anchor"
        assert payload["id"] == "anchor-knots-001"

    def test_c2_requires_single_top_level_key(self):
        doc = {
            "training_anchor": {"id": "x"},
            "extra_key": "extra_value",
        }
        assert _detect_alt_convention(doc) is None

    def test_c2_value_must_be_dict(self):
        doc = {"training_anchor": "not a dict"}
        assert _detect_alt_convention(doc) is None

    def test_c3_schema_field_json_form(self):
        doc = {
            "schema": "paradigm_candidate",
            "name": "MurmurationRootNumberPrediction",
            "category": "methodology",
        }
        result = _detect_alt_convention(doc)
        assert result is not None
        bt, payload = result
        assert bt == "paradigm_candidate"
        assert "schema" not in payload
        assert payload["name"] == "MurmurationRootNumberPrediction"

    def test_c3_unknown_schema_returns_none(self):
        doc = {"schema": "bogus", "name": "x"}
        assert _detect_alt_convention(doc) is None


class TestIterBlocksInText:
    """End-to-end parsing across all four conventions."""

    def test_strict_marker_single_block(self):
        text = """
Some prose.

```yaml
# substrate_block: anti_anchor
_schema_version: "1.0.0"
id: AA-001
name: TEST_ANCHOR
false_form: false_form_text
true_form: true_form_text
```

More prose.
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 1
        bt, payload, _line = blocks[0]
        assert bt == "anti_anchor"
        assert payload["id"] == "AA-001"

    def test_c1_substrate_type_field_multidoc(self):
        """DR-001 shape: multi-doc YAML with substrate_type fields."""
        text = """
```yaml
---
_schema_version: "1.0.0"
substrate_type: anti_anchor
id: AA-013
name: STRASSEN_ADDITIVITY_TEST
false_form: foo
true_form: bar
---
_schema_version: "1.0.0"
substrate_type: catalog_edit
entry_id: T#AA013-ROUTING
field: downstream_consumer
before: foo
after: bar
```
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 2
        types = sorted(bt for bt, _, _ in blocks)
        assert types == ["anti_anchor", "catalog_edit"]
        for bt, payload, _ in blocks:
            assert "substrate_type" not in payload  # stripped

    def test_c2_block_type_as_key_multidoc(self):
        """DR-007 shape: multi-doc YAML with block_type as mapping key."""
        text = """
```yaml
---
training_anchor:
  _schema_version: "1.0.0"
  id: "anchor-knots-001"
  domain: knots
---
paradigm_candidate:
  _schema_version: "1.0.0"
  id: "P-NEW-042"
  name: TestParadigm
```
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 2
        types = sorted(bt for bt, _, _ in blocks)
        assert types == ["paradigm_candidate", "training_anchor"]

    def test_c3_schema_field_json_array(self):
        """DR-231 shape: JSON array with schema field per item."""
        text = """
```json
[
  {
    "schema": "training_anchor",
    "domain": "knot_theory",
    "anchor_type": "invariant_value_prediction"
  },
  {
    "schema": "paradigm_candidate",
    "name": "TestParadigm",
    "description": "desc"
  }
]
```
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 2
        types = sorted(bt for bt, _, _ in blocks)
        assert types == ["paradigm_candidate", "training_anchor"]
        for bt, payload, _ in blocks:
            assert "schema" not in payload  # stripped

    def test_strict_and_alt_no_double_count(self):
        """A strict-marker block must not also be reparsed as alt."""
        text = """
```yaml
# substrate_block: anti_anchor
_schema_version: "1.0.0"
substrate_type: anti_anchor
id: AA-001
false_form: foo
true_form: bar
```
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        # Strict path consumes it; alt path skips because span overlaps
        assert len(blocks) == 1
        assert blocks[0][0] == "anti_anchor"

    def test_unknown_block_type_skipped(self):
        text = """
```yaml
# substrate_block: not_a_real_type
foo: bar
```
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 0

    def test_malformed_yaml_skipped(self):
        text = """
```yaml
# substrate_block: anti_anchor
this is: not [valid yaml: at all
```
"""
        # Should not raise; should skip cleanly
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 0

    def test_unrelated_yaml_block_skipped(self):
        text = """
```yaml
foo: bar
baz: qux
```
"""
        blocks = list(iter_blocks_in_text(text, source_file="test.md"))
        assert len(blocks) == 0  # no known convention markers

    def test_all_seven_block_types_recognized(self):
        # Each known block_type should be detectable via C1
        for bt in KNOWN_BLOCK_TYPES:
            doc = {"substrate_type": bt, "id": "test"}
            result = _detect_alt_convention(doc)
            assert result is not None
            assert result[0] == bt
