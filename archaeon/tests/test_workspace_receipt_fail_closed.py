"""receipt() must not report a clean tree when git did not answer (Aporia #1283,
from Epimetheus #1246 / NEW_DEFECTS.md "Workspace guard"). ARCH-52 fixed this
for assert_not_canonical only; the receipt fields themselves still read
dirty=False whenever `git status` failed. Written to FAIL on origin/main
b92cdf196."""
import subprocess

from archaeon import workspace as W
from archaeon.tests.test_workspace import _init_repo


def test_a_non_repository_receipt_does_not_claim_clean(tmp_path):
    plain = tmp_path / "not-a-repo"; plain.mkdir()
    r = W.receipt(plain)
    assert r["dirty"] is None and r["workspace_known"] is False


def test_a_repository_whose_status_fails_does_not_claim_clean(tmp_path):
    """rev-parse still answers, `git status` does not: a corrupt index."""
    repo = tmp_path / "repo"; repo.mkdir(); _init_repo(repo)
    (repo / ".git" / "index").write_bytes(b"not an index")
    assert subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True).returncode != 0
    r = W.receipt(repo)
    assert len(r["base_sha"]) == 40
    assert r["dirty"] is None and r["workspace_known"] is False


def test_positive_control_clean_and_dirty_are_still_booleans(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir(); _init_repo(repo)
    assert W.receipt(repo)["dirty"] is False and W.receipt(repo)["workspace_known"] is True
    (repo / "f.txt").write_text("changed", encoding="utf-8")
    assert W.receipt(repo)["dirty"] is True
