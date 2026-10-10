"""Content-addressed, write-once, verified-on-read object store (C-013-T022, architecture s3.6 local layout)."""
import hashlib
import os
import shutil
import tempfile
import unittest

from rso.scale.runner import store as S


class TestObjectStore(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.s = S.ObjectStore(self.d)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_put_get(self):
        sha = self.s.put(b"abc")
        self.assertEqual(sha, hashlib.sha256(b"abc").hexdigest())
        self.assertEqual(self.s.get(sha), b"abc")
        self.assertEqual(self.s.put(b"abc"), sha)          # idempotent

    def test_verify_on_read(self):
        sha = self.s.put(b"payload")
        with open(self.s.path(sha), "wb") as f:
            f.write(b"tampered")
        with self.assertRaises(S.IntegrityError):
            self.s.get(sha)

    def test_missing(self):
        with self.assertRaises(S.IntegrityError):
            self.s.get("0" * 64)

    def test_atomic_write_and_jsonl(self):
        p = os.path.join(self.d, "x.json")
        S.atomic_write_json(p, {"a": 1})
        self.assertEqual(S.read_json(p), {"a": 1})
        log = os.path.join(self.d, "e.jsonl")
        S.append_jsonl(log, {"n": 1})
        S.append_jsonl(log, {"n": 2})
        with open(log, "ab") as f:
            f.write(b'{"n": 3')                           # a torn last line (killed mid-write)
        rows, torn = S.read_jsonl(log)
        self.assertEqual([r["n"] for r in rows], [1, 2])
        self.assertEqual(torn, 1)


if __name__ == "__main__":
    unittest.main()
