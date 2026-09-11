from archaeon.producer import campaign_h5 as H5
from archaeon.producer import h5_reference as R


def test_plan_is_exhaustive_at_the_fixture_scope_and_validates_when_registered():
    rows = H5.plan()
    assert len(rows) == 256 and {r["rule"] for r in rows} == set(range(256))
    assert all(r["spec"]["work"]["payload"] == {"rule_number": r["rule"], "n_cells": 7, "steps": 8} for r in rows)
    c = H5.check(rows)
    if c["kind_registered"]:
        assert c["ok_to_issue"] is True, (c["invalid"][:2], c["executor_preflight"]["refused"])
        assert c["executor_preflight"]["ran"]["rule_090"]["on_fixture_scope"] is True
        assert c["executor_preflight"]["ran"]["rule_000"]["class_size"] == 7       # 0,8,18,32,64,122,126


def test_live_map_from_fake_results_and_readout_collapse():
    published = R.load_class_map()["equivalence"]
    # fake live results whose digests reproduce the published classes exactly
    results = {r: {"behaviour_digest": "d{}".format(published[r])} for r in range(256)}
    live = H5.live_class_map(results)
    assert live["agrees_with_published"] is True and live["n_classes"] == 224 and live["disagreements"] == []
    ro = H5.h5_readout(live["equivalence"])
    assert ro["direct"]["mean_reach_classes"] <= ro["direct"]["mean_reach_rules"] <= 8.0
    assert ro["balanced_7"]["max_reach_rules"] <= 12


def test_plan_reissue_keeps_spec_and_suffixes_key():
    from archaeon.producer import campaign_h5 as h5
    base = {r["label"]: r for r in h5.plan()}
    rows = h5.plan_reissue(["rule_030", "rule_110"], "R1")
    assert [r["label"] for r in rows] == ["rule_030", "rule_110"]
    for r in rows:
        assert r["spec"] == base[r["label"]]["spec"]
        assert r["request_key"] == base[r["label"]]["request_key"] + "-R1"
        assert r["reissue_of_request_key"] == base[r["label"]]["request_key"]
    import pytest
    with pytest.raises(RuntimeError):
        h5.plan_reissue(["rule_999"])


def test_table_artifact_loader_verifies_digest_and_exactness(tmp_path):
    import json
    from archaeon.producer import h5_decoders as H
    table = [H.direct(g) for g in range(4096)]
    doc = {"decoder_id": "h5.table.test", "table": table, "table_sha256": H.table_sha256(table), "provenance": {"note": "direct"}}
    p = tmp_path / "direct.json"; p.write_text(json.dumps(doc), encoding="utf-8")
    dec = H.load_table_decoder(p)
    assert [dec(g) for g in range(4096)] == table and dec.table_sha256 == doc["table_sha256"]
    bad = dict(doc); bad["table"] = table[:-1] + [(table[-1] + 1) % 256]
    p2 = tmp_path / "bad.json"; p2.write_text(json.dumps(bad), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError):
        H.load_table_decoder(p2)                      # digest no longer matches the table
    with pytest.raises(ValueError):
        H.load_table_decoder(p, expected_sha256="sha256:0000")


def test_h5_readout_reports_instruments_in_a_separate_block_with_scrambled_twin():
    from archaeon.producer import campaign_h5 as h5, h5_decoders as H
    eq = {r: r for r in range(256)}
    out = h5.h5_readout(eq, instruments={"direct_as_instrument": H.direct})
    blk = out["instruments"]["direct_as_instrument"]
    assert set(blk) >= {"member", "scrambled_3", "structure_gain_classes", "drop_rule"}
    assert "direct" in out and "direct_as_instrument" not in out

