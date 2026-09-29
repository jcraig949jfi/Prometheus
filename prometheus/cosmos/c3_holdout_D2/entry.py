"""Holdout D2 verified entry point (v5; Odysseus v4 re-audit B-1/B-2/S-1..S-6). STDLIB ONLY until verification passes.

    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py runner|custody|evidence|gates [args...]
    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py firewall-check|allowlist [args...]
    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py pin-tools [--confirm DIGEST]

ONLY `python -I -B` is accepted (v5, S-3): without -I the interpreter's own start-up (sitecustomize, PYTHONPATH, user
site) runs before this file's first line, so no re-exec from a non-isolated start can be trusted; entry refuses.
Run by FILE PATH, never with -m.

Before any prometheus module is imported, entry:
  0. drops every sys.path entry inside the repository (v5, N-2) and sets NoDefaultCurrentDirectoryInExePath=1 for this
     process and every child (v5, B-1: no bare-name executable is ever looked up in the current directory);
  1. fetches origin without tags, REFUSING if the fetch fails; resolves refs/remotes/origin/main ONCE to a commit;
     refuses tags/branches shadowing it; git runs by ABSOLUTE path with GIT_* removed, replace objects off, hooks off,
     auto-gc off, and it refuses a repository with info/grafts or a shallow file (v5, S-5);
  2. refuses unexpected files in protocol/ and unexpected *.py in the package directory;
  3. binds the code:
     - GOVERNING audit = the highest allow-listed FIREWALL_AUDIT_<n>.json; if its verdict is PASS, EVERY target is bound
       to its code_sha256 (v5, S-2: firewall-check and allowlist too, once a PASS audit governs);
     - otherwise only the PRE-AUDIT tools (firewall-check, allowlist) may run, bound to the committed files at the
       resolved commit AND only if each file's sha256 is PINNED by the custodian in the allow-list (role
       PREAUDIT_TOOL, written by `entry.py pin-tools --confirm`, which runs no repository code at all) (v5, S-2/B-2);
  4. sets sys.path to the interpreter's own library paths ONLY and installs the audited import guard: `prometheus` is
     served only from the binding; any other module that would resolve inside the repository is refused;
  5. exports the binding (C3D2_BOUND) so a multiprocessing spawn child, which re-imports this file as __mp_main__,
     installs the SAME guard before it unpickles its target (v5, S-1: the predictor child can import the runner).

NOT a boundary (FIREWALL.md v5): every process of the custodian's OS account can read the secrets directory. The operator
should check this file's sha256 (printed at start) against the governing audit's binding.
"""
import sys                                                        # built in: cannot be shadowed from any path

if __name__ in ("__main__", "__mp_main__") and not (sys.flags.isolated and sys.flags.dont_write_bytecode):
    raise SystemExit("REFUSED: run as: python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py <target> ...")

import os  # noqa: E402  (-I: the standard library precedes site-packages; the repo is not on the path)

_REPO_STR = os.path.normcase(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
if __name__ in ("__main__", "__mp_main__"):
    sys.path[:] = [p for p in sys.path if p and not (os.path.normcase(os.path.abspath(p)) + os.sep).startswith(
        _REPO_STR.rstrip(os.sep) + os.sep)]                       # v5 N-2: nothing from the repo before verification
    os.environ["NoDefaultCurrentDirectoryInExePath"] = "1"        # v5 B-1: for this process and every child

import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import site  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PKG_REL = "prometheus/cosmos/c3_holdout_D2"
PROTO_REL = PKG_REL + "/protocol"
REF = "refs/remotes/origin/main"
ALLOWLIST = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json")
AUDIT_RE = re.compile(r"^FIREWALL_AUDIT_([1-9][0-9]*)\.json$")
FIXED = {"PREDICTION_COMMITMENT.json", "RUNNER_DESIGNATION.json", "RESULT_SEAL.json", "KEY_RELEASED.json",
         "REVEALED.json"}
PKG_PY = {"__init__.py", "allowlist.py", "custody.py", "draw.py", "entry.py", "evidence.py", "firewall_check.py",
          "protocol.py", "runner.py", "sealbox.py", "selftest_D2.py", "selftest_protocol.py", "verify_reveal.py"}
TARGETS = {"runner": "prometheus.cosmos.c3_holdout_D2.runner", "custody": "prometheus.cosmos.c3_holdout_D2.custody",
           "evidence": "prometheus.cosmos.c3_holdout_D2.evidence", "gates": "prometheus.cosmos.c3_holdout_D2.protocol",
           "firewall-check": "prometheus.cosmos.c3_holdout_D2.firewall_check",
           "allowlist": "prometheus.cosmos.c3_holdout_D2.allowlist"}
BASE_BOUND = ("prometheus/__init__.py", "prometheus/cosmos/__init__.py", PKG_REL + "/__init__.py")
PRE_AUDIT_TARGETS = {"firewall-check", "allowlist"}
PRE_AUDIT_FILES = BASE_BOUND + (PKG_REL + "/firewall_check.py", PKG_REL + "/allowlist.py", PKG_REL + "/protocol.py",
                                PKG_REL + "/sealbox.py")


class EntryRefusal(SystemExit):
    pass


def git_exe() -> str:
    """git by ABSOLUTE path from an absolute PATH entry that is neither the current directory nor inside the repo."""
    repo = REPO.resolve()
    cwd = Path.cwd().resolve()
    names = ("git.exe",) if os.name == "nt" else ("git",)
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d or not os.path.isabs(d):
            continue
        try:
            rd = Path(d).resolve()
        except OSError:
            continue
        if rd == cwd or rd == repo or repo in rd.parents:
            continue
        for n in names:
            if (rd / n).is_file():
                return str(rd / n)
    raise EntryRefusal("REFUSED: no git on an absolute PATH entry outside the repository and the current directory")


def git_env() -> dict:
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith("GIT_") and k.upper() != "NODEFAULTCURRENTDIRECTORYINEXEPATH"}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["NoDefaultCurrentDirectoryInExePath"] = "1"
    return env


GIT_HARDEN = ("-c", "core.hooksPath=" + os.devnull, "-c", "gc.auto=0", "-c", "maintenance.auto=false")


def git(*a, binary=False):
    p = subprocess.run([git_exe(), *GIT_HARDEN, "-C", str(REPO), *a], capture_output=True, env=git_env())
    return p.returncode, (p.stdout if binary else p.stdout.decode("utf-8", "replace"))


def lf_sha(b: bytes) -> str:
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def _inside_repo(p) -> bool:
    try:
        Path(p).resolve().relative_to(REPO.resolve())
        return True
    except (ValueError, OSError):
        return False


class AuditedImportGuard:
    """Meta-path guard: prometheus.* only from the binding, compiled from the verified source bytes; any other module
    resolving inside the repository is refused."""

    def __init__(self, bound):
        self.bound = bound

    def find_spec(self, fullname, path=None, target=None):
        import importlib.machinery as M
        if not (fullname == "prometheus" or fullname.startswith("prometheus.")):
            if M.BuiltinImporter.find_spec(fullname) is not None or M.FrozenImporter.find_spec(fullname) is not None:
                return None
            spec = M.PathFinder.find_spec(fullname, path)
            if spec is not None:
                locs = [spec.origin] + list(spec.submodule_search_locations or [])
                if any(x and x not in ("built-in", "frozen") and _inside_repo(x) for x in locs):
                    raise ImportError("audited import guard: %s would load from the repository (%s)"
                                      % (fullname, spec.origin))
            return None
        spec = M.PathFinder.find_spec(fullname, path if path is not None else [str(REPO)])
        if spec is None or not spec.origin or not spec.origin.endswith(".py"):
            raise ImportError("audited import guard: %s has no .py source" % fullname)
        p = Path(spec.origin).resolve()
        try:
            rel = str(p.relative_to(REPO.resolve())).replace("\\", "/")
        except ValueError:
            raise ImportError("audited import guard: %s resolves outside the repo" % fullname)
        if rel not in self.bound:
            raise ImportError("audited import guard: %s (%s) is not bound by the governing audit" % (fullname, rel))
        spec.loader = _VerifiedSourceLoader(fullname, str(p), self.bound[rel])
        return spec


import importlib.machinery as _M  # noqa: E402


class _VerifiedSourceLoader(_M.SourceFileLoader):
    """Compiles from the SOURCE bytes it has just hashed; never reads __pycache__."""

    def __init__(self, fullname, path, want_sha):
        super().__init__(fullname, path)
        self.want_sha = want_sha

    def get_code(self, fullname):
        data = self.get_data(self.path)
        if lf_sha(data) != self.want_sha:
            raise ImportError("audited import guard: %s changed since the governing audit" % self.path)
        return compile(data, self.path, "exec", dont_inherit=True)


if __name__ == "__mp_main__":
    # v5 (S-1): a multiprocessing spawn child of a verified process re-imports this file under this name; it installs
    # the parent's binding before it unpickles its target. No binding -> no prometheus import at all (fails closed).
    _b = os.environ.get("C3D2_BOUND")
    if _b:
        sys.meta_path.insert(0, AuditedImportGuard(json.loads(_b)))


def _allowlisted(entries, role, name, b) -> bool:
    return any(e.get("role") == role and e.get("record") == name and e.get("sha256") == lf_sha(b) for e in entries)


def _allowlist_entries(required: bool):
    if not ALLOWLIST.is_absolute():                               # v6: custody is M1-only; never a relative path
        raise EntryRefusal("REFUSED: the allow-list path %s is not absolute on this OS" % ALLOWLIST)
    try:
        return json.loads(ALLOWLIST.read_text(encoding="utf-8"))["entries"]
    except FileNotFoundError:
        if required:
            raise EntryRefusal("REFUSED: allow-list missing")
        return []
    except Exception as e:                                        # noqa: BLE001
        raise EntryRefusal("REFUSED: allow-list unreadable: %s" % type(e).__name__)


def _git_state_ok():
    """v5 (S-5): refuse a repository whose history can be re-parented by grafts or truncated by a shallow file."""
    rc, gd = git("rev-parse", "--git-common-dir")
    if rc != 0:
        raise EntryRefusal("REFUSED: not a git repository")
    g = Path(gd.strip())
    g = g if g.is_absolute() else (REPO / g)
    for f in ("info/grafts", "shallow"):
        if (g / f).exists():
            raise EntryRefusal("REFUSED: %s exists in the git directory (history could be rewritten)" % f)


def resolve_and_check():
    rc, _ = git("fetch", "--no-tags", "--quiet", "origin")
    if rc != 0:
        raise EntryRefusal("REFUSED: git fetch origin failed (rc %d); refusing to verify against a possibly stale %s"
                           % (rc, REF))
    _git_state_ok()
    for shadow in ("refs/tags/origin/main", "refs/heads/origin/main", "refs/tags/main"):
        if git("show-ref", "--verify", "--quiet", shadow)[0] == 0:
            raise EntryRefusal("REFUSED: %s exists and could shadow %s" % (shadow, REF))
    rc, out = git("rev-parse", "--verify", "--quiet", REF + "^{commit}")
    if rc != 0:
        raise EntryRefusal("REFUSED: %s does not resolve" % REF)
    ref_c = out.strip()
    _, names = git("ls-tree", "--name-only", ref_c, PROTO_REL + "/")
    names = {Path(x).name for x in names.split()}
    wt = REPO / PROTO_REL
    if wt.exists():
        names |= {p.name for p in wt.iterdir()}
    bad = sorted(n for n in names if not (n in FIXED or AUDIT_RE.match(n)))
    if bad:
        raise EntryRefusal("REFUSED: unexpected files in %s: %s" % (PROTO_REL, ", ".join(bad)))
    _, pk = git("ls-tree", "--name-only", ref_c, PKG_REL + "/")
    py = {Path(x).name for x in pk.split() if x.endswith(".py")} | {p.name for p in HERE.glob("*.py")}
    bad = sorted(py - PKG_PY)
    if bad:
        raise EntryRefusal("REFUSED: unexpected .py files in %s: %s" % (PKG_REL, ", ".join(bad)))
    return ref_c, names


def committed_hashes(ref_c, files):
    out = {}
    for rel in files:
        rc, cb = git("show", "%s:%s" % (ref_c, rel), binary=True)
        p = REPO / rel
        if rc != 0 or not p.exists() or lf_sha(p.read_bytes()) != lf_sha(cb):
            raise EntryRefusal("REFUSED: %s differs from the committed %s" % (rel, ref_c[:12]))
        out[rel] = lf_sha(cb)
    return out


def verify(target_name):
    ref_c, names = resolve_and_check()
    pre = target_name in PRE_AUDIT_TARGETS
    entries = _allowlist_entries(required=not pre)
    audits = []
    for n, name in sorted((int(AUDIT_RE.match(x).group(1)), x) for x in names if AUDIT_RE.match(x)):
        rc, b = git("show", "%s:%s/%s" % (ref_c, PROTO_REL, name), binary=True)
        if rc == 0 and _allowlisted(entries, "AUDIT", name, b):   # the allow-list filters FIRST
            audits.append((n, name, b))
    au = json.loads(audits[-1][2].decode("utf-8")) if audits else None
    if au is not None and au.get("verdict") == "PASS":
        gov = audits[-1][1]
        bound = au.get("code_sha256") or {}
        must = set(BASE_BOUND) | {PKG_REL + "/protocol.py", PKG_REL + "/entry.py"}
        if not must <= set(bound):
            raise EntryRefusal("REFUSED: the audit does not bind the entry/package files")
        for rel, h in sorted(bound.items()):
            rc, cb = git("show", "%s:%s" % (ref_c, rel), binary=True)
            p = REPO / rel
            if rc != 0 or lf_sha(cb) != h or not p.exists() or lf_sha(p.read_bytes()) != h:
                raise EntryRefusal("REFUSED: %s does not match the governing audit's binding" % rel)
        return gov, bound
    if not pre:
        raise EntryRefusal("REFUSED: no allow-listed PASS firewall audit governs on %s" % REF
                           if au is None else "REFUSED: governing audit %s is not PASS" % audits[-1][1])
    bound = committed_hashes(ref_c, PRE_AUDIT_FILES)
    batches = sorted({e.get("pinned_utc", "") for e in entries if e.get("role") == "PREAUDIT_TOOL"})
    latest = batches[-1] if batches else None                     # v6: only the LATEST pin batch counts (revocation)
    pins = {(e.get("record"), e.get("sha256")) for e in entries
            if e.get("role") == "PREAUDIT_TOOL" and e.get("pinned_utc", "") == latest}
    unpinned = sorted(rel for rel, h in bound.items() if (rel, h) not in pins)
    if unpinned:
        raise EntryRefusal("REFUSED: pre-audit tool files not pinned by the custodian (run entry.py pin-tools): %s"
                           % ", ".join(unpinned))
    return "pre-audit:pinned@" + ref_c, bound


def pin_tools(argv):
    """v5 (S-2/B-2): list the committed pre-audit tool files' sha256 and a digest; with --confirm DIGEST append them to the
    allow-list as role PREAUDIT_TOOL. Runs NO repository code: the custodian reviews those files, then confirms."""
    ref_c, _ = resolve_and_check()
    h = committed_hashes(ref_c, PRE_AUDIT_FILES)
    digest = hashlib.sha256(json.dumps(h, sort_keys=True).encode("utf-8")).hexdigest()
    if len(argv) == 2 and argv[0] == "--confirm":
        if argv[1] != digest:
            raise EntryRefusal("REFUSED: digest mismatch (the committed tool files changed since you reviewed them)")
        try:
            data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
        except FileNotFoundError:
            data = {"format": "c3-D2-allowlist/1", "entries": []}
        import datetime as _dt
        now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        data["entries"] += [{"role": "PREAUDIT_TOOL", "record": rel, "sha256": v, "commit": ref_c, "pinned_utc": now}
                            for rel, v in sorted(h.items())]
        ALLOWLIST.parent.mkdir(parents=True, exist_ok=True)
        ALLOWLIST.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
        print(json.dumps({"pinned": sorted(h), "commit": ref_c, "digest": digest}))
        return 0
    if argv:
        raise EntryRefusal("usage: entry.py pin-tools [--confirm DIGEST]")
    print(json.dumps({"commit": ref_c, "files": h, "digest": digest,
                      "next": "review these files at that commit, then: entry.py pin-tools --confirm <digest>"}, indent=1))
    return 0


def interpreter_paths(paths):
    """The interpreter's own library paths only: no '', no cwd, no script dir, no user site, nothing in the repo."""
    prefixes = [Path(x).resolve() for x in {sys.prefix, sys.base_prefix, sys.exec_prefix}]
    user_site = site.getusersitepackages() if hasattr(site, "getusersitepackages") else None
    out = []
    for p in paths:
        if not p or p == user_site:
            continue
        rp = Path(p).resolve()
        if rp == Path.cwd().resolve() or _inside_repo(rp):
            continue
        if any(rp == pre or pre in rp.parents for pre in prefixes):
            out.append(p)
    return out


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "pin-tools":
        sys.exit(pin_tools(sys.argv[2:]))
    if len(sys.argv) < 2 or sys.argv[1] not in TARGETS:
        raise EntryRefusal("usage: entry.py %s [args...]" % "|".join(sorted(list(TARGETS) + ["pin-tools"])))
    name = sys.argv[1]
    target = TARGETS[name]
    gov, bound = verify(name)
    sys.path[:] = interpreter_paths(sys.path)
    sys.meta_path.insert(0, AuditedImportGuard(bound))
    os.environ["C3D2_BOUND"] = json.dumps(bound, sort_keys=True)         # v5 S-1: for spawn children
    os.environ["C3D2_ENTRY"] = "verified" if not gov.startswith("pre-audit") else "verified-pre-audit"
    print(json.dumps({"entry": os.environ["C3D2_ENTRY"], "entry_sha256": lf_sha(Path(__file__).read_bytes()),
                      "governing": gov, "target": target}), file=sys.stderr)
    mod = __import__(target, fromlist=["main"])
    sys.exit(mod.main(sys.argv[2:]))


if __name__ == "__main__":
    main()
