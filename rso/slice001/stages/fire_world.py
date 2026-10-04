"""Fire tests and AUTHOR_TESTED stage records for the world-plane instruments (C-004-T023A).

Instruments: P0 BOUNDS, P3 ERASE, P4 PRESERVE, P5 CHANNEL, P6 RESTART (reset.py), P7 OBSERVER (observer.py),
P8 TWIN_EQ (encoding.py). Draft B B4.1 / rso-builder-role s2.4: a stage record at AUTHOR_TESTED needs a fire test
executed at exactly the instrument VERSION: at least one case the instrument must accept and one it must reject
with the expected reason. VERSION = CodeRefs (LF-normalised sha256 and length) of the instrument's source files at
a commit on main; every file a predicate imports and executes is part of its version.

Two steps, two commits (the record cites the receipt's commit):
    python -B -m rso.slice001.stages.fire_world fire  --commit <main sha holding the sources>
        runs the cases, refuses unless every source file equals its blob at that commit, writes
        stages/FIRE_RECEIPT_world.json
    python -B -m rso.slice001.stages.fire_world records --receipt-commit <sha holding the receipt>
        writes one StageRecord per instrument (stages/<Pn>_<NAME>.json); validate_stage_record must accept each.
check_record(rec, root) refuses a record whose version or receipt hash differs from the committed blob.
Nothing here registers with the custody store (Aporia writes; Palamedes requests).
Python >= 3.8, standard library only.
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

from rso.slice001 import adapter as AD
from rso.slice001 import receipt as R

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STAGES = "rso/slice001/stages"
RECEIPT_PATH = STAGES + "/FIRE_RECEIPT_world.json"
RECORDED_BY = "Cadmus[m1-a86ec5e4]"

_BASE = ["rso/slice001/world.py", "rso/slice001/reset.py"]
SOURCES = {
    "P0": _BASE, "P3": _BASE, "P4": _BASE, "P5": _BASE, "P6": _BASE,
    "P7": _BASE + ["rso/slice001/observer.py"],
    "P8": _BASE + ["rso/slice001/observer.py", "rso/slice001/rulers.py", "rso/slice001/encoding.py",
                   "rso/slice001/fixtures/world_cases.py"],
}
NAMES = {"P0": "BOUNDS", "P3": "ERASE", "P4": "PRESERVE", "P5": "CHANNEL", "P6": "RESTART", "P7": "OBSERVER",
         "P8": "TWIN_EQ"}

# (instrument, contract case id, ACCEPT | REJECT, expected reason for REJECT). Contract case ids (contract.json).
CASES = (
    ("P0", "T03.REG", "ACCEPT", None),
    ("P0", "P0.OVERDELAY", "REJECT", "runtime outside the registered model: DELAY_RANGE at (1, CUE)"),
    ("P3", "T03.REG", "ACCEPT", None),
    ("P3", "T04.LAGD", "REJECT", "forbidden influence across boundary 3, first visible at (4, PROBE_A)"),
    ("P4", "T05.REG", "ACCEPT", None),
    ("P4", "T05.WIPE", "REJECT", "reset at 3 destroys allowed content carried without it"),
    ("P5", "T01.REG", "ACCEPT", None),
    ("P5", "T01.QCARRY", "REJECT", "retained answer does not follow the declared allowed channel at 1"),
    ("P6", "T06.REG", "ACCEPT", None),
    ("P6", "T06.HCOUNT", "REJECT", "capture/restore loses future-influencing state at (RESET 1), target FRESH"),
    ("P7", "T07.NULL", "ACCEPT", None),
    ("P7", "T07.HEAL", "REJECT", "observer HEAL changes state:d at (1, CUE)"),
    ("P8", "E06.REG_ONEHOT", "ACCEPT", None),
    ("P8", "E06.LOSSY", "REJECT", "twin LOSSY differs from REG on RETENTION: POSITIVE vs NEGATIVE"),
)


def _evaluate(instrument, case_id):
    """The instrument's outcome on the contract case (imports inside, so a version check runs first)."""
    from rso.slice001 import encoding as EN
    from rso.slice001 import observer as OB
    from rso.slice001 import reset as RS
    from rso.slice001.fixtures import world_cases as WC
    fixture = case_id.split(".", 1)[1]
    if instrument == "P7":
        return OB.observer(WC.REG, WC.OBSERVERS[fixture], fixture)
    if instrument == "P8":
        return EN.twin_eq(WC.REG, getattr(EN, fixture))
    fn = {"P0": RS.bounds, "P3": RS.erase, "P4": RS.preserve, "P5": RS.channel, "P6": RS.restart}[instrument]
    return fn(WC.RUNTIMES[fixture])


def _lf_bytes(path, root=ROOT):
    with open(os.path.join(root, *path.split("/")), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def committed_blob(path, commit, root=ROOT):
    """LF bytes of path at commit, or None if git cannot show it."""
    try:
        r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], cwd=root, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.replace(b"\r\n", b"\n") if r.returncode == 0 else None


def version_of(instrument, commit, root=ROOT):
    return [AD.file_code_ref(p, commit, root) for p in SOURCES[instrument]]


class VersionMismatch(ValueError):
    def __init__(self, code, detail):
        self.code = code
        ValueError.__init__(self, "%s: %s" % (code, detail))


def check_record(rec, root=ROOT):
    """Refuse a StageRecord whose version or fire-test receipt does not equal the blob committed at its commit.

    Raises receipt.StageError (schema) or VersionMismatch(STAGE_VERSION_MISMATCH:<path> |
    STAGE_RECEIPT_MISMATCH:<path> | STAGE_BLOB_UNAVAILABLE:<path>); returns rec unchanged.
    """
    R.validate_stage_record(rec)
    for ref in rec["version"]:
        path = ref["role"][len("code:"):]
        blob = committed_blob(path, ref["commit"], root)
        if blob is None:
            raise VersionMismatch("STAGE_BLOB_UNAVAILABLE:" + path, "no blob at %s" % ref["commit"])
        if hashlib.sha256(blob).hexdigest() != ref["sha256"] or len(blob) != ref["length"]:
            raise VersionMismatch("STAGE_VERSION_MISMATCH:" + path, "version hash differs from the committed blob")
    rr = rec["fire_test"]["receipt"]
    blob = committed_blob(rr["path"], rr["commit"], root)
    if blob is None:
        raise VersionMismatch("STAGE_BLOB_UNAVAILABLE:" + rr["path"], "no blob at %s" % rr["commit"])
    if hashlib.sha256(blob).hexdigest() != rr["blob_sha256"]:
        raise VersionMismatch("STAGE_RECEIPT_MISMATCH:" + rr["path"], "receipt hash differs from the committed blob")
    return rec


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cases(cases=CASES):
    rows = []
    for inst, case_id, want, reason in cases:
        out = _evaluate(inst, case_id)
        value = out["value"]
        ok = (value == "PASS") if want == "ACCEPT" else (value == "FAIL" and out["reason"] == reason)
        rows.append({"instrument": inst, "case_id": case_id, "expected": want, "expected_reason": reason,
                     "observed_value": value, "observed_reason": out["reason"], "ok": ok})
    return rows


def fire(commit, root=ROOT, out_path=RECEIPT_PATH):
    """Run the fire cases at the sources committed at `commit`; write the fire-test receipt."""
    versions = {}
    for inst in sorted(SOURCES):
        for p in SOURCES[inst]:
            if committed_blob(p, commit, root) != _lf_bytes(p, root):
                raise VersionMismatch("STAGE_VERSION_MISMATCH:" + p, "working file differs from %s" % commit)
        versions[inst] = version_of(inst, commit, root)
    started = _utc()
    rows = run_cases()
    doc = {"schema": "rso.slice001.fire_receipt.v1", "packet": "C-004-T023A", "executed_by": RECORDED_BY,
           "started_at_utc": started, "finished_at_utc": _utc(), "python": sys.version.split()[0],
           "versions": versions, "cases": rows, "all_ok": all(r["ok"] for r in rows)}
    with open(os.path.join(root, *out_path.split("/")), "wb") as f:
        f.write(R.canonical_bytes(doc) + b"\n")
    return doc


def build_records(receipt_commit, root=ROOT, receipt_path=RECEIPT_PATH, recorded_at=None):
    with open(os.path.join(root, *receipt_path.split("/")), "rb") as f:
        raw = f.read().replace(b"\r\n", b"\n")
    doc = json.loads(raw)
    if not doc["all_ok"]:
        raise ValueError("fire receipt has failing cases; no AUTHOR_TESTED record is written")
    ref = {"path": receipt_path, "blob_sha256": hashlib.sha256(raw).hexdigest(), "commit": receipt_commit}
    recs = {}
    for inst in sorted(SOURCES):
        rows = [r for r in doc["cases"] if r["instrument"] == inst]
        rec = {"instrument": inst, "version": doc["versions"][inst], "stage": "AUTHOR_TESTED",
               "fire_test": {"must_accept": [r["case_id"] for r in rows if r["expected"] == "ACCEPT"],
                             "must_reject": [{"case_id": r["case_id"], "expected_reason": r["expected_reason"]}
                                             for r in rows if r["expected"] == "REJECT"],
                             "receipt": ref},
               "first_sight": None, "closure": None, "recorded_by": RECORDED_BY,
               "recorded_at_utc": recorded_at or _utc()}
        R.validate_stage_record(rec)
        recs[inst] = rec
    return recs


def record_path(inst):
    return "%s/%s_%s.json" % (STAGES, inst, NAMES[inst])


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -B -m rso.slice001.stages.fire_world")
    ap.add_argument("command", choices=("fire", "records"))
    ap.add_argument("--commit", help="fire: main commit holding the instrument sources")
    ap.add_argument("--receipt-commit", help="records: commit holding the fire receipt")
    a = ap.parse_args(argv)
    if a.command == "fire":
        doc = fire(a.commit)
        print(json.dumps({"all_ok": doc["all_ok"], "cases": len(doc["cases"])}))
        return 0 if doc["all_ok"] else 1
    recs = build_records(a.receipt_commit)
    for inst, rec in recs.items():
        with open(os.path.join(ROOT, *record_path(inst).split("/")), "wb") as f:
            f.write(R.canonical_bytes(rec) + b"\n")
    print(json.dumps({"records": sorted(record_path(i) for i in recs)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
