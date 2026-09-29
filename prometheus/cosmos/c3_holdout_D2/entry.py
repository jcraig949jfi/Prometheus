"""Holdout D2 verified entry point (v4; Odysseus v3 re-audit P1/P2/P3). STDLIB ONLY until verification passes.

    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py runner|custody|evidence|gates [args...]
    python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py firewall-check [args...]     (pre-audit, see below)

Run by FILE PATH, never with -m: `python -m prometheus...` would import prometheus/__init__.py and the package
__init__ files BEFORE anything is checked. Plain `python entry.py` also works: stage 1 re-executes under -I -B, and
before it does so it imports NOTHING from a path (v4, P1):
  0. stage 1: `sys` is built in. The script directory ('' / cwd under -c) is dropped from sys.path FIRST, then sys.path
     is cut to the interpreter's own standard-library directories (PYTHONPATH entries, which precede the stdlib, and
     site-packages are removed), and only then is `subprocess` imported and the script re-run as `python -I -B`. If
     `os` was not preloaded by site (python -S), stage 1 refuses instead of importing it.
Stage 2 (isolated, no bytecode writes) imports no prometheus module until it has:
  1. fetched origin without tags (S5), REFUSING if the fetch fails (v4 F-FETCH: no silent stale origin/main), and
     resolved the fully qualified reference refs/remotes/origin/main ONCE to a commit, refusing short names and any
     tag/branch that shadows origin/main (F3). git is run by ABSOLUTE path from PATH (never from the current or the
     repository directory, v4 F-CWD) with every GIT_* variable removed and replace objects disabled (v4 F-GITENV);
  2. refused any file in protocol/ other than the named record files, INCLUDING the once-only KEY_RELEASED.json and
     REVEALED.json (v4 P3: v3 omitted them, so the protocol deadlocked after key release), and any *.py in the package
     directory other than the known modules (v4 P1 defence in depth);
  3. found the GOVERNING audit = the highest FIREWALL_AUDIT_<n>.json WHOSE sha256 IS IN the custodian's allow-list
     (v4 F-GOV: the allow-list filters first, exactly as protocol.check_gates; an unauthenticated later record is
     ignored and reported, it can neither govern nor block), required verdict PASS, and verified that EVERY file it
     binds hashes (LF) to the binding, in the committed tree AND in the working tree that is about to be imported;
  4. set sys.path to the interpreter's own library paths ONLY. The repository root is NOT on sys.path (v4 P2):
     `prometheus` is served exclusively by the audited import guard from an explicit path, and ANY other module that
     would resolve to a file inside the repository is refused (a repo-root __future__.py / argparse.py / numpy/ can
     no longer load in the key-holding process).
Only then does it import the target module and run its main() with C3D2_ENTRY=verified. The imported code then
re-checks every gate, including the loaded-module closure (every loaded module whose file is in the repository must
be audited).

firewall-check runs BEFORE any audit exists (the auditor asks for it), so it cannot be bound by an audit. It is bound
instead to the COMMITTED code at the resolved origin/main commit (working tree must equal it; C3D2_ENTRY=
verified-pre-audit). That defends against uncommitted, untracked or bytecode tampering, not against committed code.

NOT a boundary (declared in FIREWALL.md v4): every process of the custodian's OS account can read the secrets
directory. These checks stop the protocol's OWN tools from executing code the audit did not bind; they cannot stop
other code that the same account runs. The operator should check this file's sha256 (printed at start) against the
governing audit's binding: a modified copy of entry.py can simply skip its own checks.
"""
import sys                                                        # built in: cannot be shadowed from any path

if __name__ == "__main__":
    # v4 (P1): nothing may come from a path before the re-exec.
    if not sys.flags.safe_path and sys.path:
        del sys.path[0]                                           # the script directory ('' under -c)
    if not (sys.flags.isolated and sys.flags.dont_write_bytecode):
        _os = sys.modules.get("os")                               # preloaded by site; never imported here
        if _os is None:
            raise SystemExit("REFUSED: run as: python -I -B <repo>/prometheus/cosmos/c3_holdout_D2/entry.py ...")
        _roots = [_os.path.normcase(_os.path.abspath(x)) for x in (sys.base_prefix, sys.base_exec_prefix)]

        def _stdlib_dir(p):
            q = _os.path.normcase(_os.path.abspath(p)) if p else ""
            return bool(q) and "site-packages" not in q and "dist-packages" not in q and \
                any(q == r or q.startswith(r.rstrip(_os.sep) + _os.sep) for r in _roots)
        sys.path[:] = [p for p in sys.path if _stdlib_dir(p)]
        import subprocess as _sp                                  # now resolvable from the standard library only
        raise SystemExit(_sp.run([sys.executable, "-I", "-B", _os.path.abspath(__file__)] + sys.argv[1:]).returncode)

import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
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
# v4 (P3): the SAME set as protocol.FIXED_RECORDS (the selftest asserts equality)
FIXED = {"PREDICTION_COMMITMENT.json", "RUNNER_DESIGNATION.json", "RESULT_SEAL.json", "KEY_RELEASED.json",
         "REVEALED.json"}
# v4 (P1 defence in depth): the only *.py files allowed in the package directory (committed or in the working tree)
PKG_PY = {"__init__.py", "allowlist.py", "custody.py", "draw.py", "entry.py", "evidence.py", "firewall_check.py",
          "protocol.py", "runner.py", "sealbox.py", "selftest_D2.py", "selftest_protocol.py", "verify_reveal.py"}
TARGETS = {"runner": "prometheus.cosmos.c3_holdout_D2.runner", "custody": "prometheus.cosmos.c3_holdout_D2.custody",
           "evidence": "prometheus.cosmos.c3_holdout_D2.evidence", "gates": "prometheus.cosmos.c3_holdout_D2.protocol",
           "firewall-check": "prometheus.cosmos.c3_holdout_D2.firewall_check"}
BASE_BOUND = ("prometheus/__init__.py", "prometheus/cosmos/__init__.py", PKG_REL + "/__init__.py")
PRE_AUDIT = {"firewall-check": BASE_BOUND + (PKG_REL + "/firewall_check.py", PKG_REL + "/protocol.py",
                                            PKG_REL + "/sealbox.py")}


class EntryRefusal(SystemExit):
    pass


def git_exe() -> str:
    """v4 (F-CWD): git by ABSOLUTE path from an absolute PATH entry that is neither the current directory nor inside
    the repository (Windows CreateProcess would otherwise try the current directory before PATH)."""
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
    """v4 (F-GITENV): no GIT_* steering; replace objects disabled; no current-directory executable search."""
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith("GIT_") and k.upper() != "NODEFAULTCURRENTDIRECTORYINEXEPATH"}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["NoDefaultCurrentDirectoryInExePath"] = "1"
    return env


def git(*a, binary=False):
    p = subprocess.run([git_exe(), "-C", str(REPO), *a], capture_output=True, env=git_env())
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
    """v3 (B1) + v4 (P2): meta-path guard installed BEFORE any prometheus import.
    - every prometheus.* module must resolve to a .py file inside the repo that the binding covers, and its bytes must
      hash to the binding AT IMPORT TIME (closes the verify-then-import window);
    - v4: ANY other module that would resolve to a file (or package directory) inside the repository is refused, so a
      repository file can never shadow a standard-library or third-party module in a key-holding process."""

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
    """Compiles from the SOURCE bytes it has just hashed; never reads __pycache__ (-B only stops writes, a planted .pyc
    with a matching header would otherwise load), and the bytes compiled are the bytes verified (no check-then-read gap)."""

    def __init__(self, fullname, path, want_sha):
        super().__init__(fullname, path)
        self.want_sha = want_sha

    def get_code(self, fullname):
        data = self.get_data(self.path)
        if lf_sha(data) != self.want_sha:
            raise ImportError("audited import guard: %s changed since the governing audit" % self.path)
        return compile(data, self.path, "exec", dont_inherit=True)


def _allowlisted(entries, role, name, b) -> bool:
    return any(e.get("role") == role and e.get("record") == name and e.get("sha256") == lf_sha(b) for e in entries)


def verify(pre_audit_files=None):
    rc, _ = git("fetch", "--no-tags", "--quiet", "origin")
    if rc != 0:                                                   # v4 F-FETCH
        raise EntryRefusal("REFUSED: git fetch origin failed (rc %d); refusing to verify against a possibly stale %s"
                           % (rc, REF))
    for shadow in ("refs/tags/origin/main", "refs/heads/origin/main", "refs/tags/main"):
        if git("show-ref", "--verify", "--quiet", shadow)[0] == 0:
            raise EntryRefusal("REFUSED: %s exists and could shadow %s" % (shadow, REF))
    rc, out = git("rev-parse", "--verify", "--quiet", REF + "^{commit}")
    if rc != 0:
        raise EntryRefusal("REFUSED: %s does not resolve" % REF)
    ref_c = out.strip()                                           # v4: resolved ONCE; every read below uses the commit
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
    if pre_audit_files is not None:
        bound = {}
        for rel in pre_audit_files:
            rc, cb = git("show", "%s:%s" % (ref_c, rel), binary=True)
            p = REPO / rel
            if rc != 0 or not p.exists() or lf_sha(p.read_bytes()) != lf_sha(cb):
                raise EntryRefusal("REFUSED: %s differs from the committed %s (pre-audit binding)" % (rel, ref_c[:12]))
            bound[rel] = lf_sha(cb)
        return "pre-audit:committed@" + ref_c, bound
    try:
        entries = json.loads(ALLOWLIST.read_text(encoding="utf-8"))["entries"]
    except Exception as e:                                        # noqa: BLE001
        raise EntryRefusal("REFUSED: allow-list unreadable: %s" % type(e).__name__)
    audits = []
    for n, name in sorted((int(AUDIT_RE.match(x).group(1)), x) for x in names if AUDIT_RE.match(x)):
        rc, b = git("show", "%s:%s/%s" % (ref_c, PROTO_REL, name), binary=True)
        if rc == 0 and _allowlisted(entries, "AUDIT", name, b):   # v4 F-GOV: allow-list filters FIRST
            audits.append((n, name, b))
    if not audits:
        raise EntryRefusal("REFUSED: no allow-listed firewall audit committed on %s" % REF)
    _n, gov, b = audits[-1]
    au = json.loads(b.decode("utf-8"))
    if au.get("verdict") != "PASS":
        raise EntryRefusal("REFUSED: governing audit %s is not PASS" % gov)
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
    if len(sys.argv) < 2 or sys.argv[1] not in TARGETS:
        raise EntryRefusal("usage: entry.py %s [args...]" % "|".join(sorted(TARGETS)))
    if not (sys.flags.isolated and sys.flags.dont_write_bytecode):
        raise EntryRefusal("REFUSED: not isolated (-I -B)")
    name = sys.argv[1]
    target = TARGETS[name]
    gov, bound = verify(PRE_AUDIT.get(name))
    sys.path[:] = interpreter_paths(sys.path)                     # v4 P2: the repository root is NOT on sys.path
    sys.meta_path.insert(0, AuditedImportGuard(bound))
    os.environ["C3D2_ENTRY"] = "verified-pre-audit" if name in PRE_AUDIT else "verified"
    print(json.dumps({"entry": os.environ["C3D2_ENTRY"], "entry_sha256": lf_sha(Path(__file__).read_bytes()),
                      "governing": gov, "target": target}), file=sys.stderr)
    mod = __import__(target, fromlist=["main"])
    sys.exit(mod.main(sys.argv[2:]))


if __name__ == "__main__":
    main()
