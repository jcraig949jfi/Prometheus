"""Controls for roles/base-role/seat_kit/new_seat.py (run: python -m pytest roles/base-role/seat_kit/test_new_seat.py -q).

The push path writes to the shared main, so it is tested against a scratch bare repository with a
competing pusher: POSITIVE (unraced push lands), RACE (origin moved, unrelated change: merged then
pushed, both histories kept), CHEAT/negative (origin moved with a conflicting change: nothing is
pushed and the competitor's commit is untouched).
"""
import pathlib
import subprocess
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import new_seat  # noqa: E402


def sh(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True).stdout.decode().strip()


def clone(remote, dest):
    sh("git", "clone", "-q", str(remote), str(dest))
    sh("git", "config", "user.email", "t@example.invalid", cwd=dest)
    sh("git", "config", "user.name", "t", cwd=dest)
    return dest


@pytest.fixture()
def remote(tmp_path):
    r = tmp_path / "remote.git"
    sh("git", "init", "-q", "--bare", "-b", "main", str(r))
    seed = clone(r, tmp_path / "seed")
    (seed / "base.txt").write_text("base\n")
    sh("git", "add", "base.txt", cwd=seed)
    sh("git", "commit", "-q", "-m", "base", cwd=seed)
    sh("git", "push", "-q", "origin", "HEAD:main", cwd=seed)
    return r


def seat_commit(w, fname, text):
    sh("git", "checkout", "-q", "-b", "seat", cwd=w)
    (w / fname).write_text(text)
    sh("git", "add", fname, cwd=w)
    sh("git", "commit", "-q", "-m", "seat", cwd=w)


def test_push_unraced_lands(remote, tmp_path):
    w = clone(remote, tmp_path / "w")
    seat_commit(w, "seat.txt", "s\n")
    out = new_seat.push_ff(w, "X", "d", [], {}, None)
    assert out.startswith("PUSHED")
    assert sh("git", "show", "main:seat.txt", cwd=remote) == "s"


def test_push_survives_a_moved_origin_with_an_unrelated_change(remote, tmp_path):
    w = clone(remote, tmp_path / "w")
    seat_commit(w, "seat.txt", "s\n")
    other = clone(remote, tmp_path / "other")  # the competing seat pushes first
    (other / "other.txt").write_text("o\n")
    sh("git", "add", "other.txt", cwd=other)
    sh("git", "commit", "-q", "-m", "other", cwd=other)
    sh("git", "push", "-q", "origin", "HEAD:main", cwd=other)
    out = new_seat.push_ff(w, "X", "d", ["Co-Authored-By: t <t@example.invalid>"], {}, None)
    assert out.startswith("PUSHED")
    assert sh("git", "show", "main:seat.txt", cwd=remote) == "s"
    assert sh("git", "show", "main:other.txt", cwd=remote) == "o"  # the competitor's work is kept


def test_conflicting_origin_pushes_nothing(remote, tmp_path):
    w = clone(remote, tmp_path / "w")
    seat_commit(w, "base.txt", "mine\n")  # same file the competitor changes
    other = clone(remote, tmp_path / "other")
    (other / "base.txt").write_text("theirs\n")
    sh("git", "add", "base.txt", cwd=other)
    sh("git", "commit", "-q", "-m", "other", cwd=other)
    sh("git", "push", "-q", "origin", "HEAD:main", cwd=other)
    before = sh("git", "rev-parse", "main", cwd=remote)
    with pytest.raises(new_seat.SeatError):
        new_seat.push_ff(w, "X", "d", [], {}, None)
    assert sh("git", "rev-parse", "main", cwd=remote) == before
    assert sh("git", "show", "main:base.txt", cwd=remote) == "theirs"
    assert sh("git", "status", "--porcelain", "--untracked-files=no", cwd=w) == ""  # merge aborted cleanly


REGISTER = (b"| role | stamped document(s) |\r\n|---|---|\r\n| A | x |\r\n| Vivarium | y |\r\n\r\nprose\r\n"
            b"| role | entry file |\r\n|---|---|\r\n| A | RESPONSIBILITIES.md |\r\n| Vivarium | RESPONSIBILITIES.md |\r\n\r\n"
            b"| shared role | inherits | seats |\r\n|---|---|---|\r\n")


def test_insert_rows_preserves_crlf_and_adds_exactly_two_rows(tmp_path):
    p = tmp_path / "INHERITANCE.md"
    p.write_bytes(REGISTER)
    new_seat.insert_rows(p, [(b"| role | stamped document(s) |", "| Z | RESPONSIBILITIES.md (created) |"),
                             (b"| role | entry file |", "| Z | RESPONSIBILITIES.md |")])
    out = p.read_bytes()
    assert out.count(b"\r\n") == REGISTER.count(b"\r\n") + 2 and b"\r\r" not in out
    assert out.replace(b"\r\n", b"\n").count(b"| Z |") == 2
    # each row lands at the end of ITS table, not in the shared-role table
    text = out.decode().split("\r\n")
    assert text.index("| Z | RESPONSIBILITIES.md (created) |") < text.index("prose")
    assert text.index("| Z | RESPONSIBILITIES.md |") < text.index("| shared role | inherits | seats |")


def test_insert_rows_refuses_a_missing_table(tmp_path):
    p = tmp_path / "INHERITANCE.md"
    p.write_bytes(b"no tables here\n")
    with pytest.raises(new_seat.SeatError):
        new_seat.insert_rows(p, [(b"| role | entry file |", "| Z | RESPONSIBILITIES.md |")])


@pytest.mark.parametrize("name,ok", [("Hestia", True), ("Atlas-M2", True), ("ab", False), ("base-role", False),
                                     ("My-role", False), ("1Seat", False), ("Has Space", False), ("x" * 41, False)])
def test_name_rules(name, ok):
    good = bool(new_seat.NAME_RE.match(name)) and 3 <= len(name) <= 40 and name.lower() not in new_seat.RESERVED \
        and not name.lower().endswith("-role")
    assert good is ok


def test_render_refuses_unfilled_tokens():
    with pytest.raises(new_seat.SeatError):
        new_seat.render("hello @@NOPE@@", {"SEAT": "x"})


def test_roster_patterns_keep_cone_parents_and_add_every_seat_doc():
    pats = new_seat.roster_patterns(new_seat.CONE, "Zed")
    assert pats[:2] == ["/*", "!/*/"] and pats[-1] == "/roles/*/*.md"
    assert "/roles/Zed/" in pats and "/roles/base-role/" in pats
    for parent in ("archaeon", "ergon", "roles", "aporia", "ops"):  # parents of nested cone dirs keep their own files
        assert "/%s/*" % parent in pats and "!/%s/*/" % parent in pats
        assert pats.index("/%s/*" % parent) < pats.index("!/%s/*/" % parent)
    assert not any(chr(92) in x or x.startswith("C:") for x in pats)  # never a path-mangled or backslashed pattern


def test_cone_supports_comms_imports_and_the_host_precommit_hook(tmp_path):
    """Control for Hades's and Themis's field reports (2026-10-04): the creation tree must import what comms imports
    (evidence_wiki) and satisfy the host pre-commit preflight (attacks/ + ergon/probe), or a creation fails AFTER
    the files are written. Built from this repository's HEAD, so it also catches future drift in either."""
    pytest.importorskip("psycopg2")
    repo = pathlib.Path(sh("git", "rev-parse", "--show-toplevel", cwd=pathlib.Path(__file__).resolve().parent))
    wt = tmp_path / "wt"
    try:
        sh("git", "-C", str(repo), "worktree", "add", "-q", "--no-checkout", "--detach", str(wt), "HEAD")
    except subprocess.CalledProcessError as e:
        pytest.skip("cannot add a worktree here: %s" % e)
    try:
        sh("git", "sparse-checkout", "set", "--cone", *new_seat.CONE, cwd=wt)
        sh("git", "checkout", "-f", "HEAD", cwd=wt)
        r = subprocess.run([sys.executable, "-c", "import comms.api; from evidence_wiki.ew import db"], cwd=wt, capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        if (repo / "attacks/preflight.py").exists() and (wt / "attacks/preflight.py").exists():
            full = subprocess.run([sys.executable, "attacks/preflight.py", "--probes"], cwd=repo, capture_output=True)
            if full.returncode == 0:  # only meaningful where the preflight passes on a full tree
                sp = subprocess.run([sys.executable, "attacks/preflight.py", "--probes"], cwd=wt, capture_output=True)
                assert sp.returncode == 0, sp.stdout.decode()[-400:]
    finally:
        subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)], capture_output=True)
