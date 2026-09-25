"""H-R6-1 (round 6, D7): predicate code stays reachable forever.

A predicate cites a code commit. An ops.push rebase rewrites the lane's branch commits, so a cited sha can become
unreachable from every branch (round 5 PC 1789474379663-1) and a preregistration then points at code nobody can
check out. Fix: at predicate post the cited commit is pinned under a ref that no branch operation rewrites.

  pin(predicate_id, sha)        git push <remote> <full sha>:refs/pm/pred/<predicate_id>   (never force)
                                same sha already pinned -> idempotent; a different sha -> PREDICATE_REF_CONFLICT
  resolve(predicate_id)         the sha the ref names on the remote (git ls-remote), or None
  verify(predicate_id, cited)   OK via "ref" when the remote ref names the cited commit (full sha or >= 7 hex prefix);
                                OK via "patch_id" when the ref's commit and the cited commit have the same patch-id
                                (the cited commit was rebased); else PREDICATE_CODE_UNREACHABLE
  post_predicate(...)           pin FIRST, then the bus claim 'PREDICATE <id>' whose body starts 'code_sha=<sha>'
                                (a structured field the receipt guard reads; no prose parsing)

predicate_id must be refname-safe: [A-Za-z0-9][A-Za-z0-9._-]* (else PREDICATE_ID_INVALID).
ops.push pushes only HEAD:refs/heads/<integration> and never prunes, so refs/pm/* are untouched by it (H 1789479724154-0).

    python -m primordial.ops.predicate_ref pin ID SHA
    python -m primordial.ops.predicate_ref verify ID SHA
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
REF = "refs/pm/pred/{}"
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}")
SHA_RE = re.compile(r"[0-9a-f]{7,40}")
CODE_SHA_RE = re.compile(r"code_sha=([0-9a-f]{7,40})")


class PredicateRefError(ValueError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


def _git(repo, *a, input_text=None, timeout=120):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, input=input_text,
                          timeout=timeout)


def _check_id(predicate_id: str) -> str:
    if not isinstance(predicate_id, str) or not ID_RE.fullmatch(predicate_id) or ".." in predicate_id \
            or predicate_id.endswith((".", ".lock")):
        raise PredicateRefError("PREDICATE_ID_INVALID", repr(predicate_id))
    return predicate_id


def full_sha(sha: str, repo=ROOT) -> str | None:
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha.strip().lower()):
        return None
    q = _git(repo, "rev-parse", "--verify", "--quiet", f"{sha.strip()}^{{commit}}")
    return q.stdout.strip() if q.returncode == 0 and q.stdout.strip() else None


def resolve(predicate_id: str, repo=ROOT, remote: str = "origin") -> str | None:
    q = _git(repo, "ls-remote", remote, REF.format(_check_id(predicate_id)))
    line = q.stdout.strip().splitlines()
    return line[0].split()[0] if q.returncode == 0 and line else None


def pin(predicate_id: str, sha: str, repo=ROOT, remote: str = "origin") -> dict:
    ref = REF.format(_check_id(predicate_id))
    full = full_sha(sha, repo)
    if full is None:
        raise PredicateRefError("PREDICATE_SHA_INVALID", f"{sha!r} is not a commit in {repo}")
    existing = resolve(predicate_id, repo, remote)
    if existing == full:
        return {"ok": True, "ref": ref, "sha": full, "pushed": False}
    if existing is not None:
        raise PredicateRefError("PREDICATE_REF_CONFLICT", f"{ref} already names {existing}, not {full}")
    p = _git(repo, "push", remote, f"{full}:{ref}")
    if p.returncode != 0:
        raise PredicateRefError("PREDICATE_REF_PUSH_FAILED", (p.stdout + p.stderr).strip()[-300:])
    return {"ok": True, "ref": ref, "sha": full, "pushed": True}


def patch_id(sha: str, repo=ROOT) -> str | None:
    show = _git(repo, "show", "--pretty=format:", "--patch", sha)
    if show.returncode != 0 or not show.stdout.strip():
        return None
    q = _git(repo, "patch-id", "--stable", input_text=show.stdout)
    return q.stdout.split()[0] if q.returncode == 0 and q.stdout.strip() else None


def verify(predicate_id: str, cited_sha: str, repo=ROOT, remote: str = "origin") -> dict:
    """-> {ok, via: ref|patch_id|None, reason: None|PREDICATE_CODE_UNREACHABLE, ref_sha, detail}."""
    try:
        ref = REF.format(_check_id(predicate_id))
    except PredicateRefError as e:
        return {"ok": False, "via": None, "reason": "PREDICATE_CODE_UNREACHABLE", "ref_sha": None, "detail": str(e)}
    cited = str(cited_sha or "").strip().lower()
    if not SHA_RE.fullmatch(cited):
        return {"ok": False, "via": None, "reason": "PREDICATE_CODE_UNREACHABLE", "ref_sha": None,
                "detail": f"cited code sha {cited_sha!r} is not a sha"}
    ref_sha = resolve(predicate_id, repo, remote)
    if ref_sha is None:
        return {"ok": False, "via": None, "reason": "PREDICATE_CODE_UNREACHABLE", "ref_sha": None,
                "detail": f"{ref} does not exist on {remote}"}
    if ref_sha.startswith(cited):
        return {"ok": True, "via": "ref", "reason": None, "ref_sha": ref_sha, "detail": f"{ref} -> {ref_sha}"}
    _git(repo, "fetch", "-q", remote, f"{ref}:{ref}")                   # the pinned object, for its patch-id
    cited_full = full_sha(cited, repo)
    a, b = patch_id(ref_sha, repo), (patch_id(cited_full, repo) if cited_full else None)
    if a is not None and a == b:
        return {"ok": True, "via": "patch_id", "reason": None, "ref_sha": ref_sha,
                "detail": f"{ref} -> {ref_sha}; patch-id {a} == cited {cited_full}"}
    return {"ok": False, "via": None, "reason": "PREDICATE_CODE_UNREACHABLE", "ref_sha": ref_sha,
            "detail": f"{ref} -> {ref_sha} is not the cited {cited} and patch-ids differ ({a} vs {b})"}


def cited_code_sha(body: str) -> str | None:
    m = CODE_SHA_RE.search(str(body or ""))
    return m.group(1) if m else None


def post_predicate(predicate_id: str, sha: str, subject: str, body: str = "", to: str = "ALL", repo=ROOT,
                   remote: str = "origin", post=None, *, experiment_class: str | None = None,
                   sample: dict | None = None, evidence_class: str | None = None) -> dict:
    """H-R7-1: check EVIDENCE_N_v1 FIRST (a verdict-class predicate needs a conforming 32/4/8 sample block, else
    SAMPLE_RULE_MISMATCH and nothing is pinned or posted); then pin the cited commit and post
    'PREDICATE <id>: <subject>' whose body starts with 'code_sha=<full sha>' and 'evidence=<json>'."""
    from primordial.score import evidence_n as EN
    if not experiment_class:
        raise PredicateRefError("SAMPLE_RULE_MISMATCH", f"experiment_class not declared ({EN.RULE} needs it)")
    ev = EN.requirement(experiment_class, sample, evidence_class)
    if ev is not None:
        raise PredicateRefError("SAMPLE_RULE_MISMATCH", json.dumps(ev["failures"]))
    pinned = pin(predicate_id, sha, repo, remote)
    if post is None:
        from primordial.bus.bus import post
    declared = evidence_class or ("VERDICT" if experiment_class in EN.VERDICT_CLASSES else None)
    evidence = json.dumps({"rule": EN.RULE, "experiment_class": experiment_class, "evidence_class": declared,
                           "sample": sample}, sort_keys=True)
    mid = post("claim", f"PREDICATE {predicate_id}: {subject}", f"code_sha={pinned['sha']}\nevidence={evidence}\n{body}",
               to=to)
    return {**pinned, "bus_id": mid}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("pin", "verify"):
        s = sub.add_parser(name)
        s.add_argument("predicate_id")
        s.add_argument("sha")
        s.add_argument("--remote", default="origin")
    a = ap.parse_args(argv)
    try:
        out = pin(a.predicate_id, a.sha, remote=a.remote) if a.cmd == "pin" else verify(a.predicate_id, a.sha,
                                                                                       remote=a.remote)
    except PredicateRefError as e:
        out = {"ok": False, "reason": e.reason, "detail": e.detail}
    print(json.dumps(out, indent=1))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
