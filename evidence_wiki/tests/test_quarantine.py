"""The scientific quarantine as a fixture, not a promise (point release
2026-09-17, packet s6): no producer's live loop imports PEW. Scans the
Archaeon campaign machine and the SFE engine sources for an import of
the ew package or a call to the PEW port. A hit here is a release
blocker, whatever it is for.

Cheat control: the scan must be able to see an import when one exists
(a temporary file with the forbidden line is detected, then removed).
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCAN_DIRS = ["archaeon/wse", "archaeon/campaign1", "archaeon/campaign2", "archaeon/campaign3",
             "SerendipityFoundry/SerendipityFoundryEngine/sfe", "proteus"]
FORBIDDEN = re.compile(r"^\s*(from\s+ew(\.|\s)|import\s+ew(\.|\s|$)|from\s+evidence_wiki|import\s+evidence_wiki)|:8377\b", re.M)


def _hits(paths, repo=None):
    out = []
    repo = repo or REPO
    for d in paths:
        base = repo / d
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for m in FORBIDDEN.finditer(txt):
                out.append((str(p.relative_to(repo)), txt[:m.start()].count("\n") + 1, m.group(0).strip()))
    return out


def test_no_producer_live_loop_imports_pew():
    hits = _hits(SCAN_DIRS)
    assert not hits, "PEW reached from a producer's code (the quarantine): " + "; ".join(f"{p}:{l} {s}" for p, l, s in hits)


def test_cheat_the_scan_sees_an_import(tmp_path, monkeypatch):
    fake = tmp_path / "campaign9"
    fake.mkdir()
    (fake / "leak.py").write_text("from ew.client import EvidenceWiki\n", encoding="utf-8")
    hits = _hits(["campaign9"], repo=tmp_path)
    assert hits and hits[0][2].startswith("from ew") and hits[0][0].endswith("leak.py")
