"""Fail-closed defects in comms.manifest (Aporia #1283, from Epimetheus #1246 /
docs/phase3/design/OPUS-5.5/salvage/NEW_DEFECTS.md "comms.manifest").

Each test was written to FAIL on the code at origin/main b92cdf196 before the
repair, and the positive controls pass on both.
"""
import hashlib
import random

from comms import manifest as M


def test_short_binaries_that_differ_only_in_a_cr_byte_do_not_collide(tmp_path):
    """9f0d44e1 and 9f0a44e1 have no NUL byte, so the old rule called them text and rewrote the 0d."""
    a = tmp_path / "a.bin"; b = tmp_path / "b.bin"
    a.write_bytes(bytes.fromhex("9f0d44e1")); b.write_bytes(bytes.fromhex("9f0a44e1"))
    assert M.artifact_hash(a) != M.artifact_hash(b)
    assert M.artifact_hash(a) == hashlib.sha256(bytes.fromhex("9f0d44e1")).hexdigest()


def test_random_32_byte_seeds_are_hashed_as_is(tmp_path):
    """The skeptic measured 88% of random 32-byte blobs being normalised. A raw digest or seed is not text."""
    rng = random.Random(1283)
    rewritten = 0
    for i in range(200):
        raw = bytes(rng.randrange(256) for _ in range(32))
        p = tmp_path / "s{}.bin".format(i); p.write_bytes(raw)
        rewritten += M.artifact_hash(p) != hashlib.sha256(raw).hexdigest()
    assert rewritten == 0


def test_positive_control_utf8_text_with_crlf_still_normalises(tmp_path):
    lf = tmp_path / "a.md"; crlf = tmp_path / "b.md"
    lf.write_bytes("café — line\n".encode("utf-8")); crlf.write_bytes("café — line\r\n".encode("utf-8"))
    assert M.artifact_hash(lf) == M.artifact_hash(crlf)


def test_a_tampered_file_whose_name_has_a_space_is_caught(tmp_path):
    d = tmp_path / "pkt"; d.mkdir()
    (d / "has space.txt").write_bytes(b"one\n")
    M.write(d)
    assert M.verify(d) == (1, [])
    (d / "has space.txt").write_bytes(b"two\n")
    n, bad = M.verify(d)
    assert n == 1 and len(bad) == 1 and bad[0].startswith("has space.txt")


def test_a_manifest_with_no_entries_cannot_verify(tmp_path):
    d = tmp_path / "pkt"; d.mkdir()
    (d / "MANIFEST.md").write_bytes(b"# empty\n")
    n, bad = M.verify(d)
    assert n == 0 and bad
    assert M.main(["verify", str(d)]) == 1


def test_an_injected_file_not_in_the_manifest_is_reported(tmp_path):
    d = tmp_path / "pkt"; d.mkdir()
    (d / "A.md").write_bytes(b"alpha\n")
    M.write(d)
    (d / "INJECTED.md").write_bytes(b"not in the manifest\n")
    assert M.verify(d) == (1, [])                   # content contract unchanged (Necropolis manifest_verify adapter)
    assert M.unlisted(d) == ["INJECTED.md"]
    assert M.main(["verify", str(d)]) == 1
