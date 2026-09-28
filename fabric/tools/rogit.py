#!/usr/bin/env python3
"""rogit -- read-only git for fabric workers (defect D12 repair).

    rogit [-C <dir inside the worktree>] <subcommand> [args...]

Workers get this ONE command instead of `Bash(git log:*)`-style string rules. Those rules were brittle: they
denied `git -C ...` and compound forms, so 4 of 18 S2 verifiers could not search branches. rogit parses argv
itself (no shell) and:
  - permits only read-only subcommands (READ_ONLY below). `branch` and `tag` are allowed only in listing form;
  - confines `-C` to the assigned worktree (FABRIC_WORKTREE) and refuses --git-dir, --work-tree, -c,
    --config-env, --exec-path, --no-index, --output, --ext-diff, --textconv, --filters, --open-files-in-pager, -O
    and pattern files, i.e. every way to read outside the repository, write a file or run a helper program;
  - runs git with system and global config ignored, and hooks, fsmonitor, external diff, textconv, pager,
    credential prompting and all transports disabled, with a scrubbed environment;
  - caps output at 400 kB.
Exit status 64 means refused by policy, and the reason goes to stderr.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

READ_ONLY = {
    "status", "rev-parse", "log", "show", "diff", "grep", "ls-tree", "ls-files", "cat-file", "for-each-ref",
    "branch", "tag", "rev-list", "merge-base", "describe", "blame", "shortlog", "name-rev", "show-ref",
    "count-objects", "var",
}
# option prefixes refused anywhere in argv (for any subcommand)
FORBIDDEN_OPTS = (
    "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env", "--super-prefix", "--list-cmds",
    "--no-index", "--output", "--ext-diff", "--textconv", "--filters", "--open-files-in-pager", "--paginate",
    "--upload-pack", "--receive-pack", "--exec", "--run", "--edit", "--interactive", "--patterns-from",
)
# short options refused (exact or as a prefix with an attached value): -c (config), -O (grep pager / diff orderfile),
# -f (grep pattern file, branch --force), -X (ls-files exclude file), -S for blame is handled below (revs file)
FORBIDDEN_SHORT_PREFIX = ("-c", "-O", "-f", "-X")
FORBIDDEN_LONG_EXTRA = ("--contents", "--orderfile", "--resolve-git-dir", "--git-common-dir-override")
BRANCH_LISTING = {"--contains", "--no-contains", "--merged", "--no-merged", "--points-at", "--list", "-l", "-a",
                  "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "--format", "--sort", "--column",
                  "--no-column", "--color", "--no-color", "--abbrev", "--no-abbrev", "--ignore-case"}
FORCED = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-c", "diff.external=",
          "-c", "core.pager=cat", "-c", "protocol.allow=never", "-c", "credential.helper=",
          "-c", "core.sshCommand=false", "-c", "uploadpack.packObjectsHook=", "--no-pager", "--no-optional-locks"]
NO_TEXTCONV = {"log", "show", "diff", "blame", "grep"}
REFUSED = 64
CAP = 400_000


def refuse(msg: str) -> int:
    sys.stderr.write("rogit: refused: %s\n" % msg)
    return REFUSED


def _inside(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check(argv, root: Path):
    """Returns (cwd, git_args) or raises ValueError(reason)."""
    args = list(argv)
    cwd = root
    while args and args[0] == "-C":
        if len(args) < 2:
            raise ValueError("-C needs a directory")
        d = Path(args[1])
        d = d if d.is_absolute() else cwd / d
        if not _inside(d, root):
            raise ValueError("-C %s is outside the assigned worktree %s" % (args[1], root))
        cwd, args = d, args[2:]
    if not args:
        raise ValueError("no subcommand")
    sub, rest = args[0], args[1:]
    if sub not in READ_ONLY:
        raise ValueError("subcommand %r is not read-only-permitted (allowed: %s)" % (sub, ", ".join(sorted(READ_ONLY))))
    after_ddash = False
    for a in rest:
        if a == "--":
            after_ddash = True
            continue
        if after_ddash:
            continue                                               # pathspecs: resolved inside the repo by git
        if a.startswith("--"):
            name = a.split("=", 1)[0]
            if any(name == f for f in FORBIDDEN_OPTS + FORBIDDEN_LONG_EXTRA) or "file" in name or "-from" in name:
                raise ValueError("option %s is not permitted (reads/writes files or runs programs)" % a)
        elif a.startswith("-") and len(a) > 1:
            if any(a == f or a.startswith(f) for f in FORBIDDEN_SHORT_PREFIX) and not (sub == "log" and a == "-c"):
                raise ValueError("option %s is not permitted" % a)
            if sub == "blame" and a.startswith("-S"):
                raise ValueError("blame -S (revs file) is not permitted")
    if sub in ("branch", "tag"):
        opts = [a for a in rest if a.startswith("-")]
        positional = [a for a in rest if not a.startswith("-")]
        listing = any(o.split("=")[0] in BRANCH_LISTING for o in opts) or not rest
        bad = [o for o in opts if o.split("=")[0] not in BRANCH_LISTING]
        if bad or not listing:
            raise ValueError("%s is permitted only in listing form (%s)" % (sub, ", ".join(sorted(BRANCH_LISTING))))
        takes_value = {"--contains", "--no-contains", "--merged", "--no-merged", "--points-at"}
        if positional and not any(o.split("=")[0] in takes_value or o in ("--list", "-l") for o in opts):
            raise ValueError("%s with a name would create a ref" % sub)
    if sub == "cat-file" and any(a in ("--batch-command",) for a in rest):
        raise ValueError("cat-file --batch-command is not permitted")
    git_args = list(FORCED) + [sub]
    if sub in NO_TEXTCONV and sub != "grep":
        git_args += ["--no-textconv"]
    if sub in ("log", "show", "diff"):
        git_args += ["--no-ext-diff"]
    git_args += rest
    return cwd, git_args


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = os.environ.get("FABRIC_WORKTREE")
    if not root or not Path(root).is_dir():
        return refuse("FABRIC_WORKTREE is not set to the assigned worktree")
    try:
        cwd, git_args = check(argv, Path(root))
    except ValueError as e:
        return refuse(str(e))
    env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/nonexistent"), "LANG": "C.UTF-8",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
           "GIT_PAGER": "cat", "PAGER": "cat", "GIT_OPTIONAL_LOCKS": "0", "GIT_ATTR_NOSYSTEM": "1"}
    p = subprocess.run(["git", "-C", str(cwd)] + git_args, env=env, capture_output=True, timeout=120)
    out = p.stdout
    sys.stdout.buffer.write(out[:CAP])
    if len(out) > CAP:
        sys.stdout.write("\n[rogit: output truncated at %d bytes of %d; narrow the query]\n" % (CAP, len(out)))
    sys.stderr.buffer.write(p.stderr[-20000:])
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
