"""The S2 reference bundle G0 built from real executions (C-004-T024).

Normative text: rso/slice001/contract/CONTRACT.md (draft B B9 G0, B5.2 manifest, B6.1 complete nodes) with
AMENDMENT_v1.0.1 V7 (G-INV attribution) and V8. evidence_cases.g0_dicts() is the synthetic G0 (fixture trace
strings, the contract's expected outcomes); this module produces the same node set from runs of the integrated
world (world.py) on the A6 runtimes (fixtures/world_cases.py), with outcomes from the integrated predicates
(rulers.py, reset.py, observer.py, encoding.py), wrapped by the producer adapter (adapter.make_receipt).

    build_g0(commit, ledger) -> G0(dicts, traces, inventory, manifest, run_id)
    build_bundle(commit, ledger, subjects, observers, twins) -> the same shape for any subject set (T026)

G0 nodes (B9): CALIBRATION(WORLD, STANDARD); for REG, PKTD, LAGD: BOUNDS, RETENTION, ERASE, PRESERVE, CHANNEL,
RESTART and OBSERVER for the observers B9 names (REG, PKTD: BOOKKEEP, NULL; LAGD: NULL); TWIN_EQ(REG) with
twin REG-ONEHOT. 24 receipts.

Ledger (T019, T025): a build is ONE TOP_LEVEL attempt (the one launch) plus one RECEIPT row per receipt with
its node_id (V7; escalation C-004-T024_1 answered option 2): every receipt's execution.run_id is its own
RECEIPT row, so G-INV attributes each run and RUN_UNREPORTED fires for an omitted receipt. rows="build" keeps
the T024 single-row form.

predicate.code of each receipt is its instrument VERSION in the stage-record convention of T023A/T023B (one
adapter.file_code_ref per slice file the predicate imports, transitively, at one commit); a caller may pass
`versions` read from the committed stage records so receipts and records cannot drift.

Nothing here registers with the custody store (V8: Palamedes requests registration from Aporia at T020), and
nothing compares against the expected-answer table (T020).

Python >= 3.8, standard library only.
"""
import collections
import hashlib
import os
import re
import subprocess
import time

from rso.slice001 import adapter as A
from rso.slice001 import encoding as EN
from rso.slice001 import evidence as EV
from rso.slice001 import ledger as L
from rso.slice001 import observer as OB
from rso.slice001 import receipt as R
from rso.slice001 import reset as RS
from rso.slice001 import rulers as P
from rso.slice001 import world as W
from rso.slice001.fixtures import world_cases as WC

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJECTS = ("REG", "PKTD", "LAGD")
RUNTIMES = {"REG": WC.REG, "PKTD": WC.PKTD, "LAGD": WC.LAGD}
OBSERVERS = {"REG": ("BOOKKEEP", "NULL"), "PKTD": ("BOOKKEEP", "NULL"), "LAGD": ("NULL",)}
OBSERVER_FN = {"NULL": WC.NULL, "BOOKKEEP": WC.BOOKKEEP}
TWIN_NAME = ("REG", "REG_ONEHOT")
SUBJECT_NAMES = ("BOUNDS", "RETENTION", "ERASE", "PRESERVE", "CHANNEL", "RESTART")
# The entry file of each predicate's instrument; its version is this file plus its slice imports.
ENTRY = {"BOUNDS": "rso/slice001/reset.py", "CALIBRATION": "rso/slice001/rulers.py",
         "RETENTION": "rso/slice001/rulers.py", "ERASE": "rso/slice001/reset.py",
         "PRESERVE": "rso/slice001/reset.py", "CHANNEL": "rso/slice001/reset.py",
         "RESTART": "rso/slice001/reset.py", "OBSERVER": "rso/slice001/observer.py",
         "TWIN_EQ": "rso/slice001/encoding.py"}
CONTRACT = "rso/slice001/contract/contract.json"
EXPECTED = "rso/slice001/expected/EXPECTED_ANSWERS.json"
MANIFEST_PATH = "fixtures/G0/MANIFEST.json"

G0 = collections.namedtuple("G0", "dicts traces inventory manifest run_id")


class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------------------------------------
# Versions and identities

_IMPORT = re.compile(r"^\s*from rso\.slice001(?:\.(\w+))? import (\w+)", re.M)


def _lf(path, root):
    with open(os.path.join(root, *path.split("/")), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def slice_imports(path, root=REPO_ROOT, seen=None):
    """`path` and every rso/slice001 module it imports, transitively (top-level and function-level)."""
    seen = {path} if seen is None else seen
    for pkg, name in _IMPORT.findall(_lf(path, root).decode("utf-8")):
        dep = "rso/slice001/%s%s.py" % (pkg + "/" if pkg else "", name)
        if dep not in seen and os.path.isfile(os.path.join(root, *dep.split("/"))):
            seen.add(dep)
            slice_imports(dep, root, seen)
    return seen


def _blob(path, commit, root):
    r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], cwd=root, capture_output=True, timeout=60)
    if r.returncode != 0:
        raise BuildError("%s not present at %s" % (path, commit))
    return r.stdout.replace(b"\r\n", b"\n")


def _ref(path, commit, root):
    """file_code_ref after checking the working file equals its blob at `commit` (a receipt names committed code)."""
    if _blob(path, commit, root) != _lf(path, root):
        raise BuildError("%s differs from its blob at %s" % (path, commit[:12]))
    return A.file_code_ref(path, commit, root)


def predicate_version(name, commit, root=REPO_ROOT):
    return [_ref(p, commit, root) for p in sorted(slice_imports(ENTRY[name], root))]


def _repo_ref(path, commit, root):
    return {"path": path, "blob_sha256": hashlib.sha256(_blob(path, commit, root)).hexdigest(), "commit": commit}


def _git(args, root):
    r = subprocess.run(["git"] + args, cwd=root, capture_output=True, text=True, timeout=60)
    return r.stdout.strip() if r.returncode == 0 else ""


def identities(commit, root=REPO_ROOT):
    """Identity per subject (and WORLD) for adapter.make_receipt; cells share every axis within a subject."""
    contract = _repo_ref(CONTRACT, commit, root)
    world_ref = _ref("rso/slice001/world.py", commit, root)
    subj_ref = _ref("rso/slice001/fixtures/world_cases.py", commit, root)
    producer = [_ref("rso/slice001/adapter.py", commit, root), _ref("rso/slice001/s2_bundle.py", commit, root)]
    # dirty = some code this receipt names differs from its blob at `commit`. Every CodeRef here is made by
    # _ref, which refuses exactly that, so a receipt that exists is clean by construction (FD-T024-4); edits
    # elsewhere in the worktree do not touch what the receipt names.
    state = {"base_sha": commit, "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], root) or "detached",
             "worktree_path": root.replace("\\", "/"), "dirty": False}
    out = {}
    for s in SUBJECTS + (EV.WORLD_SUBJECT,):
        physics = ("WORLD" if s == EV.WORLD_SUBJECT
                   else "%s fixtures/world_cases.py@%s" % (s, subj_ref["sha256"][:16]))
        cell = {"cell_id": "W-S1", "revision": contract["blob_sha256"], "physics": physics,
                "world": "STANDARD world.py@%s" % world_ref["sha256"][:16],
                "boundary": "EPISODE_CONTENT_RESET j=1..3", "search": "NONE", "development": "NONE",
                "resources": "OP-1 caps (contract %s)" % contract["blob_sha256"][:16], "exposure": "S2 G0 build"}
        out[s] = A.Identity(contract, contract, cell, {"id": s, "code": [subj_ref]}, [world_ref], producer, state,
                            _repo_ref(EXPECTED, commit, root))
    return out


# --------------------------------------------------------------------------------------------------------
# Build

def _outcome(o):
    """A predicate's outcome as a receipt outcome: reset/observer/encoding carry `execution` beside it."""
    ex = o.get("execution")
    if ex is not None and ex.get("status") != "RAN":
        raise BuildError("predicate %s did not run: %s" % (o.get("predicate"), ex))
    return {k: v for k, v in o.items() if k != "execution"}


def runtime(name):
    """A runtime class by fixture name: fixtures/world_cases.py, else encoding.py (twins); '-' reads as '_'."""
    key = name.replace("-", "_")
    for mod in (WC, EN):
        if hasattr(mod, key):
            return getattr(mod, key)
    raise BuildError("no runtime fixture %r" % (name,))


def observer_fn(name):
    if not hasattr(WC, name):
        raise BuildError("no observer fixture %r" % (name,))
    return getattr(WC, name)


class _Rows(object):
    """Ledger rows for one build: one TOP_LEVEL row (the launch) and, per receipt, one RECEIPT row (V7) charged
    the CPU of that receipt's own evaluation; the build row is charged the rest (shared world runs), so nothing
    is counted twice. rows="build" writes the TOP_LEVEL row only (every receipt then carries its run_id)."""

    def __init__(self, ledger, run_id, node_id, rows):
        if rows not in ("per_receipt", "build"):
            raise ValueError("rows must be per_receipt or build")
        self.ledger, self.run_id, self.rows = ledger, run_id, rows
        self.attempt = ledger.begin(run_id, node_id, L.TOP_LEVEL, supplied_by=SUPPLIER)
        self.c0, self.charged, self.bytes = time.process_time(), 0.0, 0

    def receipt(self, node_id, make_one):
        """make_one(run_id) -> (Receipt, traces); charged as its own RECEIPT row when per_receipt."""
        if self.rows == "build":
            rc, tr = make_one(self.run_id)
            self.bytes += sum(len(b) for b in tr.values())
            return rc, tr
        rid = "%s/%s" % (self.run_id, node_id)
        att = self.ledger.begin(rid, node_id, L.RECEIPT, supplied_by=SUPPLIER)
        c0 = time.process_time()
        try:
            rc, tr = make_one(rid)
        except BaseException:
            att.finish("FAILED", cpu_s=time.process_time() - c0)
            raise
        cpu, n = time.process_time() - c0, sum(len(b) for b in tr.values())
        att.finish("COMPLETED", cpu_s=cpu, artifact_bytes=n)
        self.charged += cpu
        return rc, tr

    def close(self, ok):
        rest = max(0.0, time.process_time() - self.c0 - self.charged)
        self.attempt.finish("COMPLETED" if ok else "FAILED", cpu_s=rest, artifact_bytes=self.bytes)


SUPPLIER = "rso.slice001.s2_bundle.build_bundle"


def build_bundle(commit, ledger, subjects, observers=None, twins=(), run_id=None, node_id="BUNDLE",
                 rows="per_receipt", versions=None, root=REPO_ROOT, created_at_utc=None):
    """One build (one launch) of receipts for any subject set: CALIBRATION(STANDARD) once; per subject BOUNDS,
    RETENTION, ERASE, PRESERVE, CHANNEL, RESTART and OBSERVER per registered observer; TWIN_EQ(M) per
    (M, twin) in `twins`. A subject whose runtime leaves the registered model gets BOUNDS FAIL (RAN) and every
    other receipt BLOCKED with missing BOUNDS_VIOLATION:<bound> (adapter behaviour), never an exception.

    observers: {M: (observer names)}; default OBSERVERS for G0 subjects, ("NULL",) otherwise.
    twins: [(M, twin runtime name)]; at most one per subject (a TWIN_EQ node id has no twin segment).
    Returns G0(dicts, traces, inventory, manifest, run_id) -- the same shape for any subject set.
    """
    if rows not in ("per_receipt", "build"):
        raise ValueError("rows must be per_receipt or build, got %r" % (rows,))
    subjects = list(subjects)
    twin_of = {}
    for m, t in twins:
        if m in twin_of:
            raise BuildError("two twins for %s in one bundle: rcpt:%s:TWIN_EQ:STANDARD would collide; "
                             "build them in separate bundles" % (m, m))
        if m not in subjects:
            raise BuildError("twin subject %s is not in subjects" % (m,))
        twin_of[m] = t
    obs = {m: tuple((observers or {}).get(m, OBSERVERS.get(m, ("NULL",)))) for m in subjects}
    run_id = run_id or "%s-%s-%d" % (node_id.lower(), commit[:12], os.getpid())
    ids = identities(commit, root)
    for m in subjects:
        if m not in ids:
            ids[m] = _subject_identity(ids, m)
    code = {n: (versions or {}).get(n) or predicate_version(n, commit, root) for n in ENTRY}
    stamp = created_at_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    dicts, traces = {}, {}
    led = _Rows(ledger, run_id, node_id, rows)
    ok = False
    try:
        def add(subject, name, evaluate, runs, make=None, observer=None, extra=None):
            nid = R.make_node_id(subject, name, "STANDARD", observer=observer)

            def one(rid):
                return A.make_receipt(ids[subject], name, lambda r: _outcome(evaluate()), code[name], rid,
                                      make=make, runs=runs, observer=observer, extra_traces=extra,
                                      created_at_utc=stamp)
            rc, tr = led.receipt(nid, one)
            dicts[nid], traces[nid] = rc.to_dict(), tr

        cal = P.calibration("STANDARD")
        add(EV.WORLD_SUBJECT, "CALIBRATION", lambda: cal, {})
        for s in subjects:
            make = runtime(s)
            try:
                runs = A.world_runs(make)
            except W.BoundsViolation:
                runs = None
            bounds = RS.bounds(make)
            if runs is None:                         # outside the model: BOUNDS says so; the rest is BLOCKED
                add(s, "BOUNDS", lambda: bounds, {})
                for name in SUBJECT_NAMES[1:]:
                    add(s, name, None, None, make=make)
                for o in obs[s]:
                    add(s, "OBSERVER", None, None, make=make, observer=o)
                if s in twin_of:
                    add(s, "TWIN_EQ", None, None, make=make)
                continue
            sends = A.traces_from_runs({"trace:sends": runs["trace:sends"]})
            out = {"BOUNDS": bounds}
            fns = {"RETENTION": lambda: P.retention_from_runs(runs), "ERASE": lambda: RS.erase(make),
                   "PRESERVE": lambda: RS.preserve(make), "CHANNEL": lambda: RS.channel(make),
                   "RESTART": lambda: RS.restart(make)}
            add(s, "BOUNDS", lambda: bounds, runs, extra=sends)
            for name in SUBJECT_NAMES[1:]:
                out[name] = None

                def ev(name=name):
                    out[name] = fns[name]()
                    return out[name]
                add(s, name, ev, runs)
            observed = {}
            for o in obs[s]:
                def evo(o=o):
                    observed[o] = OB.observer(make, observer_fn(o), o)
                    return observed[o]
                add(s, "OBSERVER", evo, runs, observer=o)
            if s in twin_of:
                twin = runtime(twin_of[s])
                vec = {R._ID_BY_NAME[n]: out[n]["value"] for n in SUBJECT_NAMES}
                vec["P1"] = cal["value"]
                vec["P7"] = (observed.get("NULL") or OB.observer(make, WC.NULL, "NULL"))["value"]
                add(s, "TWIN_EQ", lambda: EN.twin_eq(make, twin, vectors=(vec, EN.outcome_vector(twin))), {})
        ok = True
    finally:
        led.close(ok)
    manifest = EV.build_manifest(R.Receipt.from_dict(d) for d in dicts.values())
    return G0(dicts, traces, ledger.inventory(), manifest, run_id)


def _subject_identity(ids, m):
    """Identity of a non-G0 subject: the REG identity with the subject id and physics renamed."""
    base = ids["REG"]
    cell = dict(base.cell, physics="%s%s" % (m, base.cell["physics"][len("REG"):]))
    return A.Identity(base.registration_ref, base.contract_ref, cell, dict(base.subject, id=m), base.world_code,
                      base.producer_code, base.code_state, base.expected_table)


def build_g0(commit, ledger, run_id=None, rows="per_receipt", versions=None, root=REPO_ROOT, created_at_utc=None):
    """The B9 reference bundle G0 (25 receipts): build_bundle over REG, PKTD, LAGD with B9's observers and the
    twin REG-ONEHOT. Since C-004-T026 one TOP_LEVEL row plus one RECEIPT row per receipt (V7)."""
    return build_bundle(commit, ledger, SUBJECTS, observers=OBSERVERS, twins=[TWIN_NAME], run_id=run_id,
                        node_id="G0", rows=rows, versions=versions, root=root, created_at_utc=created_at_utc)
