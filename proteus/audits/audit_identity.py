"""Atomic audit identity (V0.4 brief section 7). Mechanical, not prose discipline.

The V0 packet reported a quarantine PASS that had been produced BEFORE export.py entered the
audited tree, so the claim was true of the code when it ran and false of the code it shipped.
This module closes that hole: an audit result is bound to a digest of every source file it
covers, plus the grammar, runtime and affordance identities and the git commit. `verify()`
recomputes the digest and reports STALE the moment any covered source changes.

    python proteus/audits/audit_identity.py stamp    # run the audit, write AUDIT_IDENTITY.json
    python proteus/audits/audit_identity.py verify   # exit 0 iff the stamp still matches the tree
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
STAMP = os.path.join(HERE, "AUDIT_IDENTITY.json")

# Every file whose content the audit's conclusion depends on: the audited tree plus the auditor.
COVERED_DIRS = (os.path.join("proteus", "foundry"),)
COVERED_FILES = (os.path.join("proteus", "audits", "quarantine.py"),
                 os.path.join("proteus", "audits", "audit_identity.py"),
                 os.path.join("proteus", "contracts", "affordance_table.v0.json"))


def _lf(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def covered_files():
    out = []
    for d in COVERED_DIRS:
        full = os.path.join(ROOT, d)
        for fn in sorted(os.listdir(full)):
            if fn.endswith(".py"):
                out.append(os.path.join(d, fn).replace("\\", "/"))
    out.extend(f.replace("\\", "/") for f in COVERED_FILES)
    return sorted(set(out))


def tree_digest():
    h = hashlib.sha256()
    per = {}
    for rel in covered_files():
        d = hashlib.sha256(_lf(os.path.join(ROOT, rel))).hexdigest()
        per[rel] = d
        h.update(rel.encode() + b"\x00" + d.encode() + b"\x00")
    return h.hexdigest(), per


def git_identity():
    def g(*args):
        try:
            return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                                  text=True, timeout=30).stdout.strip()
        except Exception:
            return ""
    return {"commit": g("rev-parse", "HEAD"),
            "tree": g("rev-parse", "HEAD^{tree}"),
            "dirty": bool(g("status", "--porcelain"))}


def run_audit():
    from proteus.audits import quarantine
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = quarantine.main()
    text = buf.getvalue()
    return code, text


def stamp():
    from proteus.foundry import grammar
    from proteus.foundry.affordances import AFFORDANCE_HASH
    from proteus.foundry.identity import RUNTIME_HASH
    code, text = run_audit()
    td, per = tree_digest()
    rec = {
        "schema_version": "proteus.audit_identity.v1",
        "audit": "proteus/audits/quarantine.py",
        "audit_exit_code": code,
        "audit_result": "PASS" if code == 0 else "FAIL",
        "audit_result_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "audited_tree_digest": td,
        "audited_files": per,
        "grammar_version": grammar.GRAMMAR_VERSION,
        "grammar_hash": grammar.GRAMMAR_HASH,
        "runtime_hash": RUNTIME_HASH,
        "affordance_hash": AFFORDANCE_HASH,
        "git": git_identity(),
    }
    rec["stamp_id"] = hashlib.sha256(
        json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with open(STAMP, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"audit {rec['audit_result']} | tree {td[:16]} | grammar {rec['grammar_hash'][:12]} "
          f"| stamp {rec['stamp_id'][:16]}")
    return 0 if code == 0 else 1


def verify():
    if not os.path.exists(STAMP):
        print("STALE: no audit stamp exists")
        return 2
    with open(STAMP, encoding="utf-8") as f:
        rec = json.load(f)
    from proteus.foundry import grammar
    from proteus.foundry.affordances import AFFORDANCE_HASH
    from proteus.foundry.identity import RUNTIME_HASH
    td, per = tree_digest()
    problems = []
    if td != rec["audited_tree_digest"]:
        changed = [k for k in per if rec["audited_files"].get(k) != per[k]]
        added = sorted(set(per) - set(rec["audited_files"]))
        removed = sorted(set(rec["audited_files"]) - set(per))
        problems.append(f"covered source changed: modified={changed} added={added} removed={removed}")
    for k, cur in (("grammar_hash", grammar.GRAMMAR_HASH), ("runtime_hash", RUNTIME_HASH),
                   ("affordance_hash", AFFORDANCE_HASH)):
        if rec[k] != cur:
            problems.append(f"{k} changed since the stamp")
    if rec["audit_result"] != "PASS":
        problems.append(f"stamped audit result was {rec['audit_result']}")
    if problems:
        print("STALE:")
        for p in problems:
            print("  " + p)
        return 1
    print(f"FRESH: audit PASS binds tree {td[:16]}, grammar {rec['grammar_hash'][:12]}, "
          f"runtime {rec['runtime_hash'][:12]}, stamp {rec['stamp_id'][:16]}")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "verify"
    sys.exit(stamp() if mode == "stamp" else verify())
