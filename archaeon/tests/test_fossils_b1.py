"""B1 cutover (operator 2026-09-12): the read-grant reader is the evidence
source when configured, and it NEVER falls back to the raw ledger."""
import json

from archaeon import config as cfg, fossils_b1


def test_unconfigured_b1_is_an_errored_empty_corpus_not_a_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(fossils_b1, "LOCAL", tmp_path / "config.local.json")     # no config at all
    c = fossils_b1.read_b1(cfg.CHARTS[cfg.DEFAULT_CHART], 10)
    assert c.rows == [] and c.window["source"] == "b1" and "not configured" in c.window["error"]


def test_unreachable_b1_is_an_errored_empty_corpus_not_a_fallback(monkeypatch, tmp_path):
    p = tmp_path / "config.local.json"
    p.write_text(json.dumps({"sfe_base_url": "https://127.0.0.1:9", "sfe_token": "x", "b1_scope": "scp_none", "sfe_cacert": None}), encoding="utf-8")
    monkeypatch.setattr(fossils_b1, "LOCAL", p)
    c = fossils_b1.read_b1(cfg.CHARTS[cfg.DEFAULT_CHART], 10)
    assert c.rows == [] and c.window["source"] == "b1" and c.window["error"].startswith("b1 read failed")


def test_evidence_source_switch_is_explicit(monkeypatch, tmp_path):
    p = tmp_path / "config.local.json"; p.write_text(json.dumps({"evidence_source": "b1"}), encoding="utf-8")
    monkeypatch.setattr(fossils_b1, "LOCAL", p); monkeypatch.delenv("ARCHAEON_EVIDENCE_SOURCE", raising=False)
    assert fossils_b1.evidence_source() == "b1"
    p.write_text("{}", encoding="utf-8")
    assert fossils_b1.evidence_source() == "raw"
    monkeypatch.setenv("ARCHAEON_EVIDENCE_SOURCE", "b1")
    assert fossils_b1.evidence_source() == "b1"


def test_recent_fossils_routes_to_b1_when_configured(monkeypatch, tmp_path):
    """With evidence_source=b1 and no usable grant config, the corpus is the
    B1 error corpus -- the raw ledger is not consulted."""
    from archaeon.producer import readers
    p = tmp_path / "config.local.json"; p.write_text(json.dumps({"evidence_source": "b1"}), encoding="utf-8")
    monkeypatch.setattr(fossils_b1, "LOCAL", p); monkeypatch.delenv("ARCHAEON_EVIDENCE_SOURCE", raising=False)
    c = readers.recent_fossils(cfg.DEFAULT.chart, 10)
    assert c.window["source"] == "b1" and c.rows == [] and "error" in c.window
