"""Repository acquisition at an IMMUTABLE revision, with submodules pinned.

A branch name is not a revision. Every clone here lands on an explicit commit sha, and
the receipt records the sha that was actually checked out -- not the one requested --
so a redirected ref cannot pass as the pin.

Submodules are recorded before they are fetched: .gitmodules at the pinned revision
names them, and `git submodule status` after init gives the commit each one is pinned to.
A submodule pointing at a moving branch is a finding, not a detail.
"""
from __future__ import annotations

import hashlib
import pathlib
import re

from . import paths
from .budget import Budget


def _git(budget: Budget, args: list[str], cwd: pathlib.Path | None = None) -> dict:
    argv = ["git"] + args
    r = budget.run(argv, cwd=str(cwd) if cwd else None)
    return r


def clone_at_revision(entry: dict, budget: Budget, with_submodules: bool = True) -> dict:
    """Fetch exactly one commit into the host-local cache.

    Uses a blobless partial clone with --filter=blob:none and a single-commit fetch so a
    repository with a large history does not spend the download budget on objects no
    check will ever read. That is a deliberate deviation from `git clone` and is recorded:
    the working tree is complete at the pinned revision, the HISTORY is not present.
    """
    budget.require_network()
    rev = entry["upstream_revision"]["commit"]
    url = entry["official_source"]
    if not url.startswith("https://github.com/"):
        return {"ok": False, "reason": f"official_source {url!r} is documentation, not a "
                                       f"repository; no repository acquisition is defined "
                                       f"for this entry"}
    dest = paths.repos() / entry["id"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    steps = []

    if not (dest / ".git").exists():
        dest.mkdir(parents=True, exist_ok=True)
        steps.append(_git(budget, ["init", "--quiet"], cwd=dest))
        steps.append(_git(budget, ["remote", "add", "origin", url], cwd=dest))
    steps.append(_git(budget, ["fetch", "--filter=blob:none", "--depth", "1",
                               "origin", rev], cwd=dest))
    steps.append(_git(budget, ["checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=dest))

    head = _git(budget, ["rev-parse", "HEAD"], cwd=dest)
    actual = head["stdout"].strip()
    out = {
        "ok": all(s["returncode"] == 0 for s in steps) and head["returncode"] == 0,
        "path": str(dest),
        "url": url,
        "requested_commit": rev,
        "checked_out_commit": actual,
        "pin_verified": actual == rev,
        "clone_shape": "blobless partial clone, --depth 1 -- working tree complete at the "
                       "pinned revision, HISTORY NOT PRESENT (deliberate, download budget)",
        "steps": [{k: (v[:1500] if isinstance(v, str) else v) for k, v in s.items()} for s in steps],
    }
    if not out["pin_verified"]:
        out["ok"] = False
        out["reason"] = "checked-out sha does not match the requested pin"
        return out

    out["submodules"] = _submodules(budget, dest, with_submodules)
    out["licenses"] = license_files(dest)
    return out


def _submodules(budget: Budget, dest: pathlib.Path, fetch: bool) -> dict:
    gm = dest / ".gitmodules"
    if not gm.exists():
        return {"declared": [], "status": "NONE_DECLARED", "fetched": False}
    text = gm.read_text(encoding="utf-8", errors="replace")
    declared = []
    cur = {}
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'\[submodule "(.+)"\]', line)
        if m:
            if cur:
                declared.append(cur)
            cur = {"name": m.group(1)}
        elif "=" in line and cur:
            k, v = [x.strip() for x in line.split("=", 1)]
            cur[k] = v
    if cur:
        declared.append(cur)

    out = {"declared": declared, "n_declared": len(declared), "fetched": False,
           "moving_branch_pins": [d for d in declared if d.get("branch")]}
    if not fetch:
        out["status"] = "DECLARED_NOT_FETCHED"
        return out
    r = budget.run(["git", "submodule", "update", "--init", "--recursive",
                    "--depth", "1", "--filter=blob:none"], cwd=str(dest))
    st = budget.run(["git", "submodule", "status", "--recursive"], cwd=str(dest))
    out["fetched"] = r["returncode"] == 0
    out["update_returncode"] = r["returncode"]
    out["update_stderr_tail"] = r["stderr"][-3000:]
    pins = []
    for line in st["stdout"].splitlines():
        line = line.rstrip()
        if not line:
            continue
        flag = line[0] if line[0] in " +-U" else " "
        body = line[1:] if flag != " " or line[0] == " " else line
        parts = body.split()
        if len(parts) >= 2:
            pins.append({"commit": parts[0], "path": parts[1],
                         "describe": parts[2] if len(parts) > 2 else None,
                         "state_flag": flag,
                         "state": {" ": "initialized_at_pin", "+": "DIFFERENT_FROM_PIN",
                                   "-": "NOT_INITIALIZED", "U": "MERGE_CONFLICT"}.get(flag, "?")})
    out["pins"] = pins
    out["status"] = "FETCHED_AND_PINNED" if out["fetched"] else "FETCH_FAILED"
    return out


_LIC_RE = re.compile(r"^(LICEN[CS]E|COPYING|NOTICE|COPYRIGHT)([.\-_][A-Za-z0-9]+)?$", re.I)


def license_files(root: pathlib.Path) -> dict:
    """Hash the notice files that actually shipped. No SPDX guess is made from them:
    identifying a license from its text is a judgement, and the design says record an
    unresolved result rather than guess."""
    found = []
    for p in sorted(root.rglob("*")):
        if ".git" in p.parts or not p.is_file():
            continue
        if _LIC_RE.match(p.name):
            data = p.read_bytes()
            head = data.decode("utf-8", "replace").strip().splitlines()
            found.append({
                "path": str(p.relative_to(root)).replace("\\", "/"),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "first_lines": head[:3],
            })
    return {
        "files": found,
        "n_files": len(found),
        "spdx_identification": "NOT_ATTEMPTED -- identifying a license from its body text is a "
                               "judgement this tool does not make; the notices are hashed and "
                               "kept with the copy, and the SPDX claim stays UNRESOLVED until a "
                               "human records it",
        "status": "NOTICES_PRESENT" if found else "NO_NOTICE_FILES_FOUND",
    }
