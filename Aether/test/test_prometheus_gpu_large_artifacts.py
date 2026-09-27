"""Artifacts above KEEP_ARTIFACT_BYTES are kept OUTSIDE the repository and
recorded in the receipt -- never silently dropped (C-002 pilot finding: a
9 MB science result was verified and then discarded)."""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_RUNPOD = os.path.join(os.path.dirname(_HERE), "runpod")
if _RUNPOD not in sys.path:
    sys.path.insert(0, _RUNPOD)

import flight  # noqa: E402


class _Ctl(object):
    def __init__(self, blobs):
        self.platform_text = ""
        self.artifact_blobs = blobs
        self.health = []
        self.api_calls = []
        self._ledger_state = None
        self.telemetry_text = ""


def test_large_artifact_is_kept_outside_and_receipted(tmp_path, monkeypatch):
    monkeypatch.setattr(flight, "RECEIPT_DIR", str(tmp_path / "receipts"))
    monkeypatch.setattr(flight, "LARGE_ARTIFACT_DIR", str(tmp_path / "data"))
    os.makedirs(flight.RECEIPT_DIR)
    big = os.urandom(flight.KEEP_ARTIFACT_BYTES + 1)
    small = b"{}"
    receipt = {"run_id": "t-run", "result": "OK"}
    flight.rc.write = lambda obj, path: open(path, "w").write(json.dumps(obj))
    path = flight.save_evidence(_Ctl({"units.tar": big, "result.json": small}), receipt)
    run_dir = tmp_path / "receipts" / "t-run"
    assert (run_dir / "result.json").exists()
    assert not (run_dir / "units.tar").exists()
    kept = tmp_path / "data" / "t-run" / "units.tar"
    assert kept.read_bytes() == big
    rec = json.loads(open(path).read())
    (entry,) = rec["large_artifacts"]
    assert entry["path"] == "units.tar" and entry["bytes"] == len(big)
    import hashlib
    assert entry["sha256"] == hashlib.sha256(big).hexdigest()
