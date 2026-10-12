"""C-016-T011 tests: durable, idempotent INTEGRATION_READY notices (rso/scale/notify)."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from rso.scale.notify import notify as N

SHA1 = "a" * 40
SHA2 = "b" * 40


class MemSink:
    """In-memory stand-in for the comms table: the durable record the idempotency key lives in."""

    def __init__(self):
        self.rows = []

    def find(self, task_ref, marker):
        return [r for r in self.rows if r["task_ref"] == task_ref and marker in r["subject"]]

    def post(self, subject, body, task_ref):
        self.rows.append({"id": len(self.rows) + 1, "subject": subject, "body": body, "task_ref": task_ref})
        return len(self.rows)


def make_tree(root, status="INTEGRATION_READY", sha=SHA1, extra_history=()):
    camp = Path(root) / "C-900"
    (camp / "tasks" / "C-900-T001").mkdir(parents=True)
    (camp / "CAMPAIGN.json").write_text(json.dumps({"campaign_id": "C-900", "coordinator_role": "Palamedes"}))
    hist = [{"status": "READY", "by": "P", "at_utc": "2026-10-11T00:00:00Z", "note": ""},
            {"status": "CLAIMED", "by": "E", "at_utc": "2026-10-11T00:10:00Z", "note": ""}]
    if status != "CLAIMED":
        hist.append({"status": "INTEGRATION_READY", "by": "E", "at_utc": "2026-10-11T01:00:00Z",
                     "note": "tests ok; branch x/y at " + sha})
    hist.extend(extra_history)
    t = {"task_id": "C-900-T001", "campaign_id": "C-900", "title": "demo", "owner_role": "E",
         "status": hist[-1]["status"], "history": hist}
    (camp / "tasks" / "C-900-T001" / "TASK.json").write_text(json.dumps(t))
    return Path(root)


def tree_digest(root):
    h = hashlib.sha256()
    for p in sorted(Path(root).rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.d, True)

    def test_scan_emits_one_notice(self):
        root = make_tree(self.d)
        s = MemSink()
        r = N.scan(root, s, campaigns=["C-900"])
        self.assertEqual(len(r["posted"]), 1)
        self.assertEqual(len(s.rows), 1)
        self.assertEqual(s.rows[0]["task_ref"], "C-900-T001")
        self.assertIn(SHA1[:12], s.rows[0]["subject"])

    def test_repeated_scan_or_second_scanner_does_not_duplicate(self):
        root = make_tree(self.d)
        s = MemSink()
        N.scan(root, s, campaigns=["C-900"])
        r2 = N.scan(root, s, campaigns=["C-900"])     # retry / second scanner, same durable sink
        self.assertEqual(r2["posted"], [])
        self.assertEqual(len(r2["already"]), 1)
        self.assertEqual(len(s.rows), 1)

    def test_new_attempt_sha_emits_new_notice(self):
        root = make_tree(self.d)
        s = MemSink()
        N.scan(root, s, campaigns=["C-900"])
        make_tree(self.d + "/n", sha=SHA2)           # same task, new head sha
        N.scan(Path(self.d + "/n"), s, campaigns=["C-900"])
        self.assertEqual(len(s.rows), 2)

    def test_disposition_recorded_once(self):
        root = make_tree(self.d)
        s = MemSink()
        N.scan(root, s, campaigns=["C-900"])
        # task later INTEGRATED
        root2 = make_tree(self.d + "/m", extra_history=[
            {"status": "INTEGRATED", "by": "Palamedes", "at_utc": "2026-10-11T02:00:00Z", "note": "merged"}])
        r = N.scan(Path(self.d + "/m"), s, campaigns=["C-900"])
        self.assertEqual(len(r["dispositions"]), 1)
        self.assertEqual(r["dispositions"][0]["disposition"], "INTEGRATED")
        r = N.scan(Path(self.d + "/m"), s, campaigns=["C-900"])
        self.assertEqual(r["dispositions"], [])
        self.assertEqual(len(s.rows), 2)

    def test_sent_back_disposition(self):
        root = make_tree(self.d)
        s = MemSink()
        N.scan(root, s, campaigns=["C-900"])
        make_tree(self.d + "/m", extra_history=[
            {"status": "IMPLEMENTING", "by": "Palamedes", "at_utc": "2026-10-11T02:00:00Z", "note": "fails"}])
        r = N.scan(Path(self.d + "/m"), s, campaigns=["C-900"])
        self.assertEqual(r["dispositions"][0]["disposition"], "SENT_BACK")

    def test_no_notice_for_other_states_or_unlisted_campaign(self):
        root = make_tree(self.d, status="CLAIMED")
        s = MemSink()
        self.assertEqual(N.scan(root, s, campaigns=["C-900"])["posted"], [])
        root = make_tree(self.d + "/x")
        self.assertEqual(N.scan(root, s, campaigns=["C-123"])["posted"], [])
        self.assertEqual(s.rows, [])

    def test_coordinator_selects_campaigns(self):
        root = make_tree(self.d)
        s = MemSink()
        self.assertEqual(len(N.scan(root, s, coordinator="Palamedes")["posted"]), 1)
        s2 = MemSink()
        self.assertEqual(N.scan(root, s2, coordinator="Nobody")["posted"], [])

    def test_never_writes_workgraph_state(self):
        root = make_tree(self.d)
        before = tree_digest(root)
        s = MemSink()
        N.scan(root, s, campaigns=["C-900"])
        N.queue(root, s, campaigns=["C-900"])
        self.assertEqual(before, tree_digest(root))

    def test_queue_shows_age_and_notified(self):
        root = make_tree(self.d)
        s = MemSink()
        q = N.queue(root, s, campaigns=["C-900"], now="2026-10-11T03:30:00Z")
        self.assertEqual(q[0]["age_minutes"], 150)
        self.assertFalse(q[0]["notified"])
        N.scan(root, s, campaigns=["C-900"])
        self.assertTrue(N.queue(root, s, campaigns=["C-900"], now="2026-10-11T03:30:00Z")[0]["notified"])

    def test_key_falls_back_to_receipt_then_timestamp(self):
        root = make_tree(self.d)
        tdir = Path(root) / "C-900" / "tasks" / "C-900-T001"
        t = json.loads((tdir / "TASK.json").read_text())
        t["history"][-1]["note"] = "no sha here"
        (tdir / "TASK.json").write_text(json.dumps(t))
        k1 = N.integration_entries(tdir, t)[0]["key"]
        self.assertIn("2026-10-11T01:00:00Z", k1)
        (tdir / "attempts" / "A-001").mkdir(parents=True)
        (tdir / "attempts" / "A-001" / "RECEIPT.json").write_text(json.dumps({"attempt_id": "A-001", "end_sha": SHA2}))
        k2 = N.integration_entries(tdir, t)[0]["key"]
        self.assertIn(SHA2, k2)


if __name__ == "__main__":
    unittest.main()
