"""O2 (MNE-D1, 2026-09-17): the M2-owned backup and restore qualification.

The live path was exercised for real the same day (backup pewbk-20260917T
055050-fea46038fa3c, 1.10 GB in 153 s; restore into the M2 cluster
RESTORE_VERIFIED, 164/164 tables, receipt ops/restore_verification.json).
These tests pin the two decision points that must never regress, without
a database:

    cheat      a source that is not the named environment is refused
               BEFORE any byte is written (no dump, no manifest), the
               state records the failure, and the alarm is raised
    positive   a healthy dump updates the state's last_success
    drift/loss row-count differences on a live source: restored <= live is
               drift (append-only rows arrived after the dump), anything
               else is loss; only loss fails the verdict
"""
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "ops"))
sys.path.insert(0, str(HERE))

import pew_backup            # noqa: E402
import pew_restore_verify    # noqa: E402


class WrongCluster(RuntimeError):
    pass


def test_cheat_wrong_environment_writes_nothing_and_alarms(tmp_path, monkeypatch):
    monkeypatch.setattr(pew_backup, "STATE", tmp_path / "state.json")
    monkeypatch.setattr(pew_backup, "source_identity",
                        lambda c, environment=None: (_ for _ in ()).throw(WrongCluster("REFUSED: not canonical")))
    alarms = []
    monkeypatch.setattr(pew_backup, "alert", lambda s, b: alarms.append(s) or True)
    monkeypatch.setattr(sys, "argv", ["pew_backup.py", "--dir", str(tmp_path / "dumps")])
    rc = pew_backup.main()
    assert rc == 1
    assert not list((tmp_path / "dumps").glob("*")) if (tmp_path / "dumps").exists() else True
    st = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert st["consecutive_failures"] == 1 and "REFUSED" in st["last_error"]
    assert st["last_success"] is None
    assert alarms and "BACKUP FAILED" in alarms[0]


def test_positive_success_updates_state(tmp_path, monkeypatch):
    monkeypatch.setattr(pew_backup, "STATE", tmp_path / "state.json")
    fake_man = {"created_at": "2026-09-17T05:53:24-0400", "dump_file": "x.dump",
                "backup_id": "pewbk-test", "sha256": "ab" * 32, "bytes": 1,
                "source_identity": {"db_system_id": "7628127204585430828"}}
    monkeypatch.setattr(pew_backup, "dump", lambda d: dict(fake_man))
    monkeypatch.setattr(pew_backup, "rotate", lambda d, keep=None: [])
    monkeypatch.setattr(pew_backup, "alert", lambda s, b: pytest.fail("no alarm on success"))
    monkeypatch.setattr(sys, "argv", ["pew_backup.py", "--dir", str(tmp_path / "dumps")])
    assert pew_backup.main() == 0
    st = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert st["last_success"] == fake_man["created_at"] and st["consecutive_failures"] == 0
    assert st["source_db_system_id"] == "7628127204585430828"


def test_drift_versus_loss_classification():
    differing = {
        "comms.messages": {"live": 330, "restored": 327},        # drift
        "ew.write_log": {"live": 5551, "restored": 5550},        # drift
        "ew.claims": {"live": 100, "restored": None},            # loss: absent
        "viv.rows": {"live": 10, "restored": 12},                # loss: more than live
    }
    drift, loss = pew_restore_verify.classify_diffs(differing)
    assert set(drift) == {"comms.messages", "ew.write_log"}
    assert set(loss) == {"ew.claims", "viv.rows"}
    assert pew_restore_verify.classify_diffs({}) == ({}, {})
