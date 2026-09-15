"""H-R6-1 (D7): a predicate-cited commit orphaned by a rebase still verifies through refs/pm/pred/<id>."""
from __future__ import annotations

import subprocess

import pytest

from primordial.ops import predicate_ref as PR


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def commit(repo, name, text):
    (repo / name).write_text(text, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", f"add {name}")
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def world(tmp_path):
    """A bare 'origin', a lane clone with an integration branch, and a lane commit cited by a predicate."""
    origin, lane = tmp_path / "origin.git", tmp_path / "lane"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "integ", str(lane)], check=True)
    for k, v in (("user.email", "h@test"), ("user.name", "h")):
        git(lane, "config", k, v)
    git(lane, "remote", "add", "origin", str(origin))
    commit(lane, "base.txt", "base\n")
    git(lane, "push", "-q", "origin", "integ")
    cited = commit(lane, "harness.py", "def job():\n    return 1\n")         # the predicate cites this commit
    return origin, lane, cited


def test_a_rebase_orphans_the_cited_commit_and_verify_still_passes_via_the_ref(world, tmp_path):
    origin, lane, cited = world
    # A 1789479784925-0: the cited commit is LOCAL ONLY at pin time; the ref push itself uploads its objects
    assert subprocess.run(["git", "-C", str(origin), "cat-file", "-e", f"{cited}^{{commit}}"],
                          capture_output=True).returncode != 0
    assert PR.pin("B-R6-1-demo", cited, repo=lane)["pushed"]
    assert subprocess.run(["git", "-C", str(origin), "cat-file", "-e", f"{cited}^{{commit}}"]).returncode == 0
    # someone else lands on integ; the lane rebases (ops.push behaviour) and the cited commit is rewritten
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", "-b", "integ", str(origin), str(other)], check=True)
    for k, v in (("user.email", "o@test"), ("user.name", "o")):
        git(other, "config", k, v)
    commit(other, "other.txt", "other\n")
    git(other, "push", "-q", "origin", "integ")
    git(lane, "fetch", "-q", "origin")
    git(lane, "rebase", "-q", "origin/integ")
    rebased = git(lane, "rev-parse", "HEAD")
    assert rebased != cited
    git(lane, "push", "-q", "origin", "integ")
    assert subprocess.run(["git", "-C", str(origin), "merge-base", "--is-ancestor", cited, "integ"]).returncode != 0
    subprocess.run(["git", "-C", str(origin), "gc", "-q", "--prune=now"], check=True)
    # the cited sha is on no branch, but the ref keeps it: verify from the lane and from a fresh clone
    got = PR.verify("B-R6-1-demo", cited, repo=lane)
    assert got["ok"] and got["via"] == "ref" and got["ref_sha"] == cited
    fresh = tmp_path / "fresh"
    subprocess.run(["git", "clone", "-q", str(origin), str(fresh)], check=True)
    assert PR.verify("B-R6-1-demo", cited[:9], repo=fresh)["ok"]
    subprocess.run(["git", "-C", str(fresh), "fetch", "-q", "origin", f"refs/pm/pred/B-R6-1-demo"], check=True)
    assert git(fresh, "show", f"{cited}:harness.py").startswith("def job")      # the code is checkable out


def test_a_rebased_copy_verifies_by_patch_id_and_other_code_does_not(world, tmp_path):
    origin, lane, cited = world
    git(lane, "checkout", "-q", "-b", "side", "HEAD~1")
    commit(lane, "unrelated.txt", "x\n")
    git(lane, "cherry-pick", cited)                                         # same patch, new sha
    copy = git(lane, "rev-parse", "HEAD")
    assert copy != cited
    PR.pin("P-copy", copy, repo=lane)
    got = PR.verify("P-copy", cited, repo=lane)
    assert got["ok"] and got["via"] == "patch_id"
    unrelated = git(lane, "rev-parse", "HEAD~1")
    bad = PR.verify("P-copy", unrelated, repo=lane)
    assert not bad["ok"] and bad["reason"] == "PREDICATE_CODE_UNREACHABLE"


def test_refusals(world):
    origin, lane, cited = world
    assert PR.verify("never-pinned", cited, repo=lane)["reason"] == "PREDICATE_CODE_UNREACHABLE"
    assert PR.verify("B-R6-x", "not-a-sha", repo=lane)["reason"] == "PREDICATE_CODE_UNREACHABLE"
    PR.pin("B-R6-x", cited, repo=lane)
    assert PR.pin("B-R6-x", cited, repo=lane) == {"ok": True, "ref": "refs/pm/pred/B-R6-x", "sha": cited,
                                                  "pushed": False}                     # idempotent
    base = git(lane, "rev-parse", "HEAD~1")
    with pytest.raises(PR.PredicateRefError) as e:
        PR.pin("B-R6-x", base, repo=lane)                                   # never repointed, never forced
    assert e.value.reason == "PREDICATE_REF_CONFLICT" and PR.resolve("B-R6-x", repo=lane) == cited
    for bad_id in ("has space", "../up", "x..y", "ends.lock", ""):
        with pytest.raises(PR.PredicateRefError) as e:
            PR.pin(bad_id, cited, repo=lane)
        assert e.value.reason == "PREDICATE_ID_INVALID"
    with pytest.raises(PR.PredicateRefError) as e:
        PR.pin("B-R6-y", "0" * 40, repo=lane)
    assert e.value.reason == "PREDICATE_SHA_INVALID"


def test_post_predicate_pins_first_and_writes_the_structured_code_sha(world):
    origin, lane, cited = world
    posts = []
    out = PR.post_predicate("C-R6-p", cited[:10], "demo rule", "body text", repo=lane,
                            post=lambda kind, subject, body, to: posts.append((kind, subject, body, to)) or "9-0")
    assert out["bus_id"] == "9-0" and PR.resolve("C-R6-p", repo=lane) == cited
    kind, subject, body, _ = posts[0]
    assert kind == "claim" and subject == "PREDICATE C-R6-p: demo rule"
    assert body.splitlines()[0] == f"code_sha={cited}" and PR.cited_code_sha(body) == cited
