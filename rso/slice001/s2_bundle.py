"""The S2 reference bundle G0 built from real executions (C-004-T024).

Normative text: rso/slice001/contract/CONTRACT.md (draft B B9 G0, B5.2 manifest, B6.1 complete nodes) with
AMENDMENT_v1.0.1 V7 (G-INV attribution) and V8. evidence_cases.g0_dicts() is the synthetic G0 (fixture trace
strings, the contract's expected outcomes); this module produces the same node set from runs of the integrated
world (world.py) on the A6 runtimes (fixtures/world_cases.py), with outcomes from the integrated predicates
(rulers.py, reset.py, observer.py, encoding.py), wrapped by the producer adapter (adapter.make_receipt).

    build_g0(commit, ledger) -> G0(dicts, traces, inventory, manifest, run_id)

G0 nodes (B9): CALIBRATION(WORLD, STANDARD); for REG, PKTD, LAGD: BOUNDS, RETENTION, ERASE, PRESERVE, CHANNEL,
RESTART and OBSERVER for the observers B9 names (REG, PKTD: BOOKKEEP, NULL; LAGD: NULL); TWIN_EQ(REG) with
twin REG-ONEHOT. 24 receipts.

Ledger (T019): the build is ONE TOP_LEVEL attempt (node_id "G0"), charged its measured CPU and artifact bytes,
and every receipt's execution.run_id is that attempt's run_id (rows="build"; escalation C-004-T024_1: 24
per-receipt TOP_LEVEL rows cannot fit the 12-launch cap). G-INV then counts each receipt's run exactly once;
per-node RUN_UNREPORTED attribution (V7) is not available on this G0 until that escalation is answered.

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
from rso.slice001 import observer as OB
from rso.slice001 import receipt as R
from rso.slice001 import reset as RS
from rso.slice001 import rulers as P
from rso.slice001.fixtures import world_cases as WC

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUBJECTS = ("REG", "PKTD", "LAGD")
RUNTIMES = {"REG": WC.REG, "PKTD": WC.PKTD, "LAGD": WC.LAGD}
OBSERVERS = {"REG": ("BOOKKEEP", "NULL"), "PKTD": ("BOOKKEEP", "NULL"), "LAGD": ("NULL",)}
OBSERVER_FN = {"NULL": WC.NULL, "BOOKKEEP": WC.BOOKKEEP}
TWIN = ("REG", EN.REG_ONEHOT)
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


def build_g0(commit, ledger, run_id=None, rows="build", versions=None, root=REPO_ROOT, created_at_utc=None):
    """Run every G0 node, charge the build to `ledger`, return G0(dicts, traces, inventory, manifest, run_id).

    versions: {predicate NAME: [CodeRef]} to use as predicate.code (e.g. read from the stage records);
    default predicate_version(NAME, commit).
    """
    if rows != "build":
        raise NotImplementedError("rows=%r: per-receipt rows await escalation C-004-T024_1" % (rows,))
    run_id = run_id or "g0-%s-%d" % (commit[:12], os.getpid())
    ids = identities(commit, root)
    code = {n: (versions or {}).get(n) or predicate_version(n, commit, root) for n in ENTRY}
    stamp = created_at_utc or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    dicts, traces, artifact = {}, {}, 0
    attempt = ledger.begin(run_id, "G0", supplied_by="rso.slice001.s2_bundle.build_g0")
    c0 = time.process_time()
    try:
        def add(subject, name, outcome, runs, observer=None, extra=None):
            rc, tr = A.make_receipt(ids[subject], name, lambda r: _outcome(outcome), code[name], run_id,
                                    runs=runs, observer=observer, extra_traces=extra, created_at_utc=stamp)
            d = rc.to_dict()
            dicts[d["node_id"]], traces[d["node_id"]] = d, tr

        add(EV.WORLD_SUBJECT, "CALIBRATION", P.calibration("STANDARD"), {})
        vectors = {}
        for s in SUBJECTS:
            make = RUNTIMES[s]
            runs = A.world_runs(make)
            sends = A.traces_from_runs({"trace:sends": runs["trace:sends"]})
            out = {"BOUNDS": RS.bounds(make), "RETENTION": P.retention_from_runs(runs), "ERASE": RS.erase(make),
                   "PRESERVE": RS.preserve(make), "CHANNEL": RS.channel(make), "RESTART": RS.restart(make)}
            for name in SUBJECT_NAMES:
                add(s, name, out[name], runs, extra=sends if name == "BOUNDS" else None)
            observed = {o: OB.observer(make, OBSERVER_FN[o], o) for o in OBSERVERS[s]}
            for o in OBSERVERS[s]:
                add(s, "OBSERVER", observed[o], runs, observer=o)
            vectors[s] = {R._ID_BY_NAME[n]: out[n]["value"] for n in SUBJECT_NAMES}
            vectors[s]["P1"] = P.calibration("STANDARD")["value"]
            vectors[s]["P7"] = observed["NULL"]["value"]
        subject, twin = TWIN
        add(subject, "TWIN_EQ", EN.twin_eq(RUNTIMES[subject], twin,
                                           vectors=(vectors[subject], EN.outcome_vector(twin))), {})
        artifact = sum(len(b) for tr in traces.values() for b in tr.values())
    except BaseException:
        attempt.finish("FAILED", cpu_s=time.process_time() - c0, artifact_bytes=artifact)
        raise
    attempt.finish("COMPLETED", cpu_s=time.process_time() - c0, artifact_bytes=artifact)
    manifest = EV.build_manifest(R.Receipt.from_dict(d) for d in dicts.values())
    return G0(dicts, traces, ledger.inventory(), manifest, run_id)
