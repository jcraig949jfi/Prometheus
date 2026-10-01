"""audit.kind_audit: citation-kind flags on synthetic text with a synthetic index (known answers for every
severity, prefix resolution and the held-out exemption), and one real committed document (W-E REPORT: the
adjudicate-row naming holes W2-I reported)."""
from __future__ import annotations

from prometheus.ananke.audit import kind_audit as KA
from prometheus.ananke.audit.tests import _data as D

IDX = {"aaaaaaaa11111111": {"kind": "transfer", "wave": "T", "family": "RELAY"},
       "bbbbbbbb22222222": {"kind": "adjudicate", "wave": "D", "family": "XOR"},
       "cccccccc33333333": {"kind": "evolve", "wave": "A", "family": "MAJ"},
       "dddddddd44444444": {"kind": "census", "wave": "A0", "family": "XOR"},
       "eeeeeeee55555555": {"kind": "evolve", "wave": "A", "family": "HOLD"},
       "eeeeeeee66666666": {"kind": "evolve", "wave": "B", "family": "HOLD"}}
RES = KA.Resolver(IDX)


def one(text):
    out = KA.audit_text(text, RES)
    assert len(out) == 1, out
    return out[0]


def test_severities_known_answers():
    assert one("the search on aaaaaaaa failed: a NULL")["severity"] == "HIGH"
    assert one("aaaaaaaa is a transfer, not a search NULL")["severity"] == "LOW"
    assert one("the champion of bbbbbbbb evolved twice")["severity"] == "NAMING"
    assert one("the search behind bbbbbbbb was NULL")["severity"] == "HIGH"
    assert one("champion cccccccc searched hard")["flagged"] == 0               # evolve rows are never flagged
    assert one("dddddddd held .5")["severity"] == "HIGH"
    assert one("dddddddd on the held-out target")["flagged"] == 0               # 'held-out' names a transfer target


def test_prefix_resolution_is_unique_or_nothing():
    assert RES.resolve("eeeeeeee") is None                                       # ambiguous prefix
    assert RES.resolve("eeeeeeee5555") == "eeeeeeee55555555"
    assert KA.audit_text("cell 0123456789 and Aaaaaaaaa", RES) == []            # unknown / non-hex-bounded


def test_summary_and_rank():
    pad = " " + "x " * 120                                                    # > the 200-character window
    recs = KA.audit_text(pad.join(["search aaaaaaaa NULL.", "Then bbbbbbbb champion.",
                                   "aaaaaaaa transfer, not searched."]), RES)
    s = KA.summarise(recs)
    assert (s["flagged_HIGH"], s["flagged_NAMING"], s["flagged_LOW"]) == (1, 1, 1)
    assert [r["severity"] for r in KA.rank(recs)] == ["HIGH", "NAMING", "LOW"]


WE = D.REPO / "roles/Ananke/research/workers/W-E/REPORT.md"


@D.need(D.ROWS, WE)
def test_real_document_W_E_naming_holes():
    res = KA.Resolver(KA.load_index(D.ROWS))
    recs = KA.audit_text(WE.read_text(encoding="utf-8", errors="replace"), res, "W-E/REPORT.md")
    s = KA.summarise(recs)
    assert s["flagged_NAMING"] == 8 and s["flagged_HIGH"] == 0                  # W2-I kind_audit_summary.json
