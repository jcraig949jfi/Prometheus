"""Holdout D2 verified entry point (v2; Odysseus F1). STDLIB ONLY until verification passes.

    python <repo>/prometheus/cosmos/c3_holdout_D2/entry.py runner|custody|evidence [args...]

Run by FILE PATH, never with -m: `python -m prometheus...` would import prometheus/__init__.py and the package
__init__ files BEFORE anything is checked. This script imports no prometheus module until it has:
  1. fetched origin without tags (S5) and resolved the fully qualified reference refs/remotes/origin/main, refusing
     short names and any tag/branch that shadows origin/main (F3);
  2. refused any file in protocol/ other than the named record files (F1 variant);
  3. found the GOVERNING audit (highest FIREWALL_AUDIT_<n>.json on the reference), required verdict PASS, required its
     sha256 to be in the custodian's allow-list (S1), and verified that EVERY file it binds hashes (LF) to the binding,
     in the committed tree AND in the working tree that is about to be imported;
  4. set sys.path to [repo root] + the interpreter's own library paths (no cwd, no script dir, no user site).
Only then does it import the target module and run its main() with C3D2_ENTRY=verified. The imported code then
re-checks every gate, including the loaded-module closure (every loaded prometheus.* module must be audited).
"""
import hashlib
import json
import os
import re
import site
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PKG_REL = "prometheus/cosmos/c3_holdout_D2"
PROTO_REL = PKG_REL + "/protocol"
REF = "refs/remotes/origin/main"
ALLOWLIST = Path("C:/Users/jcrai/nestor_receipts/holdout_D2/ALLOWLIST.json")
AUDIT_RE = re.compile(r"^FIREWALL_AUDIT_([1-9][0-9]*)\.json$")
FIXED = {"PREDICTION_COMMITMENT.json", "RUNNER_DESIGNATION.json", "RESULT_SEAL.json"}
TARGETS = {"runner": "prometheus.cosmos.c3_holdout_D2.runner", "custody": "prometheus.cosmos.c3_holdout_D2.custody",
           "evidence": "prometheus.cosmos.c3_holdout_D2.evidence"}


class EntryRefusal(SystemExit):
    pass


def git(*a, binary=False):
    p = subprocess.run(["git", "-C", str(REPO), *a], capture_output=True)
    return p.returncode, (p.stdout if binary else p.stdout.decode("utf-8", "replace"))


def lf_sha(b: bytes) -> str:
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


class AuditedImportGuard:
    """v3 (Odysseus v2 re-audit, R2 B1): meta-path guard installed BEFORE any prometheus import. Every prometheus.*
    module must resolve to a .py file inside the repo that the governing audit binds, and its bytes must hash to the
    binding AT IMPORT TIME (closes the verify-then-import window). Anything else raises ImportError."""

    def __init__(self, bound):
        self.bound = bound

    def find_spec(self, fullname, path=None, target=None):
        if not (fullname == "prometheus" or fullname.startswith("prometheus.")):
            return None
        import importlib.machinery as M
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


def verify(no_fetch=False):
    if not no_fetch:
        subprocess.run(["git", "-C", str(REPO), "fetch", "--no-tags", "--quiet", "origin"], capture_output=True)
    for shadow in ("refs/tags/origin/main", "refs/heads/origin/main", "refs/tags/main"):
        if git("show-ref", "--verify", "--quiet", shadow)[0] == 0:
            raise EntryRefusal("REFUSED: %s exists and could shadow %s" % (shadow, REF))
    rc, _ = git("rev-parse", "--verify", "--quiet", REF + "^{commit}")
    if rc != 0:
        raise EntryRefusal("REFUSED: %s does not resolve" % REF)
    _, names = git("ls-tree", "--name-only", REF, PROTO_REL + "/")
    names = {Path(x).name for x in names.split()}
    wt = REPO / PROTO_REL
    if wt.exists():
        names |= {p.name for p in wt.iterdir()}
    bad = sorted(n for n in names if not (n in FIXED or AUDIT_RE.match(n)))
    if bad:
        raise EntryRefusal("REFUSED: unexpected files in %s: %s" % (PROTO_REL, ", ".join(bad)))
    audits = sorted((int(AUDIT_RE.match(n).group(1)), n) for n in names if AUDIT_RE.match(n))
    if not audits:
        raise EntryRefusal("REFUSED: no firewall audit on %s" % REF)
    gov = audits[-1][1]
    rc, b = git("show", "%s:%s/%s" % (REF, PROTO_REL, gov), binary=True)
    if rc != 0:
        raise EntryRefusal("REFUSED: governing audit %s is not committed on %s" % (gov, REF))
    au = json.loads(b.decode("utf-8"))
    if au.get("verdict") != "PASS":
        raise EntryRefusal("REFUSED: governing audit %s is not PASS" % gov)
    try:
        entries = json.loads(ALLOWLIST.read_text(encoding="utf-8"))["entries"]
    except Exception as e:                                        # noqa: BLE001
        raise EntryRefusal("REFUSED: allow-list unreadable: %s" % type(e).__name__)
    if not any(e.get("role") == "AUDIT" and e.get("record") == gov and e.get("sha256") == lf_sha(b) for e in entries):
        raise EntryRefusal("REFUSED: governing audit %s is not in the custodian's allow-list" % gov)
    bound = au.get("code_sha256") or {}
    must = {"prometheus/__init__.py", "prometheus/cosmos/__init__.py", PKG_REL + "/__init__.py",
            PKG_REL + "/protocol.py", PKG_REL + "/entry.py"}
    if not must <= set(bound):
        raise EntryRefusal("REFUSED: the audit does not bind the entry/package files")
    for rel, h in sorted(bound.items()):
        rc, cb = git("show", "%s:%s" % (REF, rel), binary=True)
        p = REPO / rel
        if rc != 0 or lf_sha(cb) != h or not p.exists() or lf_sha(p.read_bytes()) != h:
            raise EntryRefusal("REFUSED: %s does not match the governing audit's binding" % rel)
    return gov, bound


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in TARGETS:
        raise EntryRefusal("usage: entry.py runner|custody|evidence [args...]")
    target = TARGETS[sys.argv[1]]
    if not (sys.flags.isolated and sys.flags.dont_write_bytecode):
        # v3 (B1): re-run in isolated mode (-I: no user site, no PYTHON* env, no script dir on sys.path) with no bytecode
        # writes (-B), so no stale or planted .pyc can be imported and no environment variable can steer imports
        env = dict(os.environ)
        raise SystemExit(subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve())] + sys.argv[1:],
                                        env=env).returncode)
    gov, bound = verify(no_fetch=os.environ.get("C3D2_NO_FETCH") == "1")
    prefixes = [Path(x).resolve() for x in {sys.prefix, sys.base_prefix, sys.exec_prefix}]
    user_site = site.getusersitepackages() if hasattr(site, "getusersitepackages") else None

    def interpreter_path(p):
        if not p or p == user_site:
            return False
        rp = Path(p).resolve()
        if rp in (HERE, Path.cwd().resolve(), REPO.resolve()):
            return False
        return any(rp == pre or pre in rp.parents for pre in prefixes)
    sys.path[:] = [str(REPO)] + [p for p in sys.path if interpreter_path(p)]
    sys.meta_path.insert(0, AuditedImportGuard(bound))
    os.environ["C3D2_ENTRY"] = "verified"
    print(json.dumps({"entry": "verified", "governing_audit": gov, "target": target}), file=sys.stderr)
    mod = __import__(target, fromlist=["main"])
    sys.exit(mod.main(sys.argv[2:]))


if __name__ == "__main__":
    main()
