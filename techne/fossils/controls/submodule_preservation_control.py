"""Positive + negative controls for the submodule preservation invariant (charter 2026-09-13 P1).

The avida defect was a body that hashed fine while a REQUIRED submodule was an empty directory.
An instrument that only ever says OK proves nothing, so this drives the real check through both
failure modes it is supposed to catch, on a real body, and restores it afterwards:

  POSITIVE    a correctly acquired body               -> preservation_check OK
  NEGATIVE A  the submodule working tree is emptied   -> FAIL "MISSING"
  NEGATIVE B  the submodule is moved off its pin      -> FAIL "NOT at the pinned commit"
  RESTORE     put it back                             -> OK and the tree hash matches again

Content alteration inside a present, correctly-pinned submodule is NOT this check's job: that is
caught by `harvest verify` (the tree hash). The two instruments together cover omission, drift and
mutation. Run:  python -m techne.fossils.controls.submodule_preservation_control [specimen_id]
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import pathlib
import shutil

from .. import harvest, vault

DEFAULT = "lru-cache-goldsborough"   # small body, submodule is test-only


def _sub_dir(sid: str) -> pathlib.Path:
    p = harvest.preservation_of(sid)
    assert p["submodules"], "%s has no submodules to control on" % sid
    return vault.body_dir(sid) / "upstream" / "tree" / p["submodules"][0]["path"], p["submodules"][0]


def main(argv=None) -> int:
    sid = (argv or sys.argv[1:] or [DEFAULT])[0]
    rows = []

    def step(name, expect_ok):
        ok, probs = harvest.preservation_check(sid)
        rows.append({"step": name, "expected_ok": expect_ok, "observed_ok": ok, "problems": probs})
        print("%-34s expected=%-5s observed=%-5s %s" % (name, expect_ok, ok, "; ".join(probs)[:90]))
        return ok

    sub, meta = _sub_dir(sid)
    pinned = meta["pinned_commit"]
    tree0 = harvest.drift(sid)["tree_sha256_now"]

    # ---- POSITIVE -------------------------------------------------------------------------
    step("POSITIVE acquired body", True)

    # ---- NEGATIVE A: omit the submodule ----------------------------------------------------
    hold = pathlib.Path(tempfile.mkdtemp(prefix="subctl_"))
    moved = []
    for child in list(sub.iterdir()):
        if child.name == ".git":
            continue
        shutil.move(str(child), str(hold / child.name))
        moved.append(child.name)
    step("NEGATIVE A submodule emptied", False)
    for n in moved:
        shutil.move(str(hold / n), str(sub / n))
    shutil.rmtree(hold, ignore_errors=True)
    step("RESTORE after A", True)

    # ---- NEGATIVE B: move the submodule off its pinned commit ------------------------------
    prev = subprocess.run(["git", "-C", str(sub), "rev-parse", "HEAD~1"],
                          capture_output=True, text=True).stdout.strip()
    did_b = False
    # A bare `git checkout` on Windows CRLF-converts the working tree and silently mutates the
    # preserved body (it modified exactly one gtest header the first time this control ran).
    # Every checkout here forces the same LF config acquisition uses, so the body comes back
    # byte-identical -- which the tree-hash assertion at the end proves.
    LF = ["-c", "core.autocrlf=false", "-c", "core.eol=lf"]
    if prev and prev != pinned:
        subprocess.run(["git", "-C", str(sub), *LF, "checkout", "--quiet", "--force", "--detach", prev], check=True)
        step("NEGATIVE B submodule off pin", False)
        subprocess.run(["git", "-C", str(sub), *LF, "checkout", "--quiet", "--force", "--detach", pinned], check=True)
        step("RESTORE after B", True)
        did_b = True
    else:
        print("NEGATIVE B skipped: no distinct parent commit available in the submodule")

    tree1 = harvest.drift(sid)["tree_sha256_now"]
    restored = (tree0 == tree1)
    print("tree hash before %s\ntree hash after  %s\nRESTORED_EXACTLY %s" % (tree0, tree1, restored))

    passed = (rows[0]["observed_ok"] is True
              and rows[1]["observed_ok"] is False
              and rows[2]["observed_ok"] is True
              and (not did_b or (rows[3]["observed_ok"] is False and rows[4]["observed_ok"] is True))
              and restored)
    doc = {"schema": "techne.fossil.submodule_control/1", "specimen_id": sid,
           "submodule": meta["path"], "pinned_commit": pinned,
           "tree_sha256_before": tree0, "tree_sha256_after": tree1,
           "restored_exactly": restored, "negative_b_run": did_b,
           "steps": rows, "control_passed": bool(passed),
           "note": "the check must FAIL on omission and on pin drift, and the body must come back "
                   "byte-identical; content mutation is verify's job, not this check's."}
    # next to this module, so the artifact lands in the working tree that ran it -- canonical_root()
    # points at the main checkout and would silently write outside a seat worktree.
    out = pathlib.Path(__file__).resolve().parent / "SUBMODULE_CONTROL_2026-09-13.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("CONTROL", "PASSED" if passed else "FAILED", "->", out)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
