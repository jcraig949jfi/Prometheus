"""Regression tests for deposit.py (BX-5): empty or undelimited worker messages must be refused."""
import importlib.util
import pathlib

import pytest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("deposit_mod", HERE.parent / "deposit.py")
dep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dep)


@pytest.fixture
def tmp_here(tmp_path, monkeypatch):
    monkeypatch.setattr(dep, "HERE", tmp_path)
    return tmp_path


def test_delimited_deposits_and_verifies(tmp_here):
    p = dep.deposit("W-T1", "chat\n===BEGIN REPORT===\nbody line\n===END REPORT===\ntail")
    assert p.read_text(encoding="utf-8").split("\n", 1)[1].strip() == "body line"
    assert dep.verify(p)


def test_empty_message_refused(tmp_here):
    with pytest.raises(ValueError):
        dep.deposit("W-T2", "")
    assert not (tmp_here / "workers" / "W-T2" / "REPORT.md").exists()


def test_empty_delimited_block_refused(tmp_here):
    with pytest.raises(ValueError):
        dep.deposit("W-T3", "===BEGIN REPORT===\n\n===END REPORT===")


def test_undelimited_refused_unless_allowed(tmp_here):
    with pytest.raises(ValueError):
        dep.deposit("W-T4", "a report without delimiters")
    p = dep.deposit("W-T4", "a report without delimiters", allow_undelimited=True)
    assert dep.verify(p)
