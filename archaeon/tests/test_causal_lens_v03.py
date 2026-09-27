"""Contract v0.3 (B6 repair): three-referent governance. Synthetic cheats + the real adapters on committed fixtures (portable)."""
from __future__ import annotations

import json
from pathlib import Path

from archaeon.causal_lens import adapters_v03 as A
from archaeon.causal_lens.schema_v03 import Graph, NI

FX = Path(__file__).parent / "fixtures_v03"


def _g(**fields):
    g = Graph("synthetic", "segment"); g.event("t", ["UNCLASSIFIED"], **fields); return g


def test_where_only_engine_leaves_write_governing_unidentifiable():
    g = _g(code_location_share=dict(value={"own_region": 0.1, "window": 0.9}, basis="TRACE", referent="WHERE"),
           write_governing=dict(value=NI, basis="NATIVE_RECORD", referent="WHAT"))
    assert g.check() == []


def test_write_governing_from_location_is_rejected():
    g = _g(write_governing=dict(value={"writer": 0.9}, basis="TRACE", referent="WHAT", source="copy op pc < L"))
    assert any(v.startswith("J21") for v in g.check())


def test_write_governing_from_context_is_rejected():
    g = _g(write_governing=dict(value={"donor": 0.8}, basis="TRACE", referent="WHAT", source="NPE prov (context that wrote)"))
    assert any(v.startswith("J21") for v in g.check())


def test_referent_missing_or_mismatched_is_rejected():
    assert any(v.startswith("J21") for v in _g(write_governing=dict(value=NI, basis="TRACE")).check())
    assert any(v.startswith("J21") for v in _g(execution_share=dict(value={"a": 1.0}, basis="TRACE", referent="WHERE")).check())


def test_location_autonomy_may_not_wear_the_material_name():
    g = _g(); g.prop("t", "autonomy_write", "YES", "TRACE"); g.nodes["t"]["props"]["autonomy_write"]["referent"] = "WHERE"
    assert any(v.startswith("J22") for v in g.check())


def test_bee_adapter_on_real_rows():
    d = json.loads((FX / "bee_r038751_sample.json").read_text())
    loc_only = A.graph_of("bee", [A.bee_fields(r, d["L"]) for r in d["rows"]])
    assert loc_only.check() == []
    assert all(loc_only.nodes[t]["fields"]["write_governing"]["value"] == NI for t in loc_only.of_kind("TRANSFORMATION"))
    full = A.graph_of("bee", [A.bee_fields(r, d["L"], cp) for r, cp in zip(d["rows"], d["codeprov"])])
    assert full.check() == []
    # the B6 case: rows whose location reading is foreign-dominated but whose code is the writer's own material
    diverge = sum(1 for r, cp in zip(d["rows"], d["codeprov"])
                  if (r[8] - r[9]) > r[7] / 2 and (cp["own_region"] + cp["self_copied"]) > r[7] / 2)
    assert diverge > 0


def test_npe_adapter_on_t003_births():
    d = json.loads((FX / "npe_t003_births.json").read_text())
    g = A.graph_of("npe", [A.npe_fields(b) for b in d["births"]])
    assert g.check() == [] and len(d["births"]) == 34
    who_ne_what = sum(1 for b in d["births"] if (A.npe_fields(b)["context_authorship"]["value"]["donor_context"] > 0.5)
                      != (A.npe_fields(b)["write_governing"]["value"]["donor_material"] > 0.5))
    assert who_ne_what == 13                                  # T-004: majority-level WHO != WHAT in 13 of 34 births


def test_archaeon_adapter_on_block13_events():
    d = json.loads((FX / "archaeon_block13_sample.json").read_text())
    g = A.graph_of("archaeon", [A.archaeon_fields(e) for e in d["events"]])
    assert g.check() == []
