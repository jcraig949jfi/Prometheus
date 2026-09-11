"""LF and CRLF working copies cannot produce different authoritative hashes."""
import hashlib
import subprocess

from comms import manifest as M


def test_lf_and_crlf_copies_hash_identically_and_equal_the_git_blob(tmp_path):
    lf = tmp_path / "a.md"; crlf = tmp_path / "b.md"
    lf.write_bytes(b"line one\nline two\n"); crlf.write_bytes(b"line one\r\nline two\r\n")
    assert M.artifact_hash(lf) == M.artifact_hash(crlf)
    # equals git's blob content hash for the normalised text (sha256 over the normalised bytes, which is what
    # `git show HEAD:path` returns for a text file committed with autocrlf)
    assert M.artifact_hash(lf) == hashlib.sha256(b"line one\nline two\n").hexdigest()
    bin_ = tmp_path / "c.bin"; bin_.write_bytes(b"\x00\r\n\x01")
    assert M.artifact_hash(bin_) == hashlib.sha256(b"\x00\r\n\x01").hexdigest()    # binaries untouched


def test_write_then_verify_round_trip_and_a_crlf_rewrite_still_verifies(tmp_path):
    d = tmp_path / "prompts"; d.mkdir()
    (d / "A.md").write_bytes(b"alpha\n"); (d / "B.md").write_bytes(b"beta\n")
    M.write(d, title="t")
    assert M.verify(d) == (2, [])
    (d / "A.md").write_bytes(b"alpha\r\n")                      # a checkout with CRLF: still verifies
    assert M.verify(d) == (2, [])
    (d / "B.md").write_bytes(b"gamma\n")                         # a real change: caught
    n, bad = M.verify(d)
    assert n == 2 and len(bad) == 1 and bad[0].startswith("B.md")
