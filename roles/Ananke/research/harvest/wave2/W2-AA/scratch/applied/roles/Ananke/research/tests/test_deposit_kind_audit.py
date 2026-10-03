"""deposit.py + kind_audit (W2-AA): flags are recorded in provenance; REPORT.md bytes are unchanged and
a missing/broken auditor never blocks a deposit. Proposed path: roles/Ananke/research/tests/."""
import hashlib
import importlib.util
import json
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("deposit_mod_ka", HERE.parent / "deposit.py")
dep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dep)

BLOCK = "W2-X findings\nenv of C1 RELAY NULL cell fac4aaa23a0bdcb2 (C1 search held .5).\nbbef66a1 evolved."
MSG = f"chat\n===BEGIN REPORT===\n{BLOCK}\n===END REPORT===\ntail"


@pytest.fixture
def tmp_here(tmp_path, monkeypatch):
    monkeypatch.setattr(dep, "HERE", tmp_path)
    return tmp_path


def prov_of(p):
    return json.loads(p.with_name(p.stem + ".provenance.json").read_text())


def expected_bytes():
    sha = hashlib.sha256(BLOCK.encode("utf-8")).hexdigest()
    return (f"<!-- DEPOSITED VERBATIM by Ananke for worker W-KA; sha256(report)={sha[:16]}; delimited; see "
            f"REPORT.provenance.json -->\n{BLOCK}\n").encode("utf-8")


def test_flags_recorded_and_report_bytes_unchanged(tmp_here):
    p = dep.deposit("W-KA", MSG)
    assert p.read_bytes() == expected_bytes() and dep.verify(p)
    ka = prov_of(p)["kind_audit"]                 # KeyError before the patch
    assert ka["status"] == "ok" and ka["counts"]["HIGH"] == 1
    (f,) = [f for f in ka["flags"] if f["severity"] == "HIGH"]
    assert f["cell_id"] == "fac4aaa23a0bdcb2" and f["kind"] == "transfer"
    assert p.read_text(encoding="utf-8").split("\n")[f["line"] - 1].find(f["token"]) >= 0  # REPORT.md line
    assert all(x["cell_id"] != "bbef66a1" for x in ka["flags"])


def test_missing_auditor_does_not_block_and_bytes_identical(tmp_here, monkeypatch):
    monkeypatch.setattr(dep, "KIND_AUDIT", tmp_here / "no_such_tool.py")   # AttributeError before the patch
    p = dep.deposit("W-KA", MSG)
    assert p.read_bytes() == expected_bytes() and dep.verify(p)
    assert prov_of(p)["kind_audit"]["status"] == "NOT_VERIFIED"
