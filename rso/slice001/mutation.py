"""Semantic mutation runner with the plan s5 outcome classes (C-004-T017).

Source: NEXT_ROUND_PLAN_v0.4 s5 (frozen into CONTRACT.md s6); caps CONTRACT.md s5 (OP-1).

Edits are DATA committed before execution (an edits file, schema EDITS_SCHEMA). The runner reads them,
applies each to the target module's source TEXT in memory, compiles it, and runs the frozen suite in a
child process into which the edited module is injected through sys.modules. No source file is written: the
only file the runner writes is the rows file, a new JSONL file (never overwritten) with one row per edit,
flushed and fsynced per row, between a header + baseline row and a terminal row.

Order (plan s5): the unchanged suite runs first; if it does not pass, no edit is executed.

Per-edit status, and the plan s5 class it counts toward (summarize()):

    NOT_APPLICABLE     find text absent, ambiguous without `occurrence`, or the edit changes nothing
    DUPLICATE          edited source identical to an earlier edit's (duplicate_of names it)     duplicate
    SYNTAX_ERROR       edited source does not compile (no child launched)                       error
    IMPORT_ERROR       the edited module raises while executing its body                       executed, error
    TEST_ERROR         the suite ran; no assertion failed but some test raised                  executed, error
    TIMEOUT            the child exceeded timeout_s and was killed                              executed, timeout
    KILLED             at least one test assertion failed                                       executed, killed
    SURVIVED           the suite passed                                                         executed, survived
    NOT_RUN_BASELINE   the unchanged suite did not pass
    NOT_RUN_CAP        the child-seconds cap was exhausted before this edit (partial results kept)

Errors are not semantic kills (plan s5). The runner never decides equivalence: a survivor is
NOT_EQUIVALENT_WITNESSED only when its edit's witness expression gives a different repr on the mutant than on
the original; otherwise it is UNRESOLVED (absence of an observed difference is not equivalence). EQUIVALENT
comes only from a reviewer's adjudication passed to summarize().

Python >= 3.8, standard library only.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import time

EDITS_SCHEMA = "rso.slice001.mutation_edits.v1"
ROWS_SCHEMA = "rso.slice001.mutation_rows.v1"
# The edits object of a stage record (draft B B4.1) uses exactly these keys.
EDIT_COUNTS = ("proposed", "applicable", "duplicate", "executed", "killed", "survived", "equivalent",
               "error", "timeout")
STATUSES = ("NOT_APPLICABLE", "DUPLICATE", "SYNTAX_ERROR", "IMPORT_ERROR", "TEST_ERROR", "TIMEOUT",
            "KILLED", "SURVIVED", "NOT_RUN_BASELINE", "NOT_RUN_CAP")
EXECUTED = ("IMPORT_ERROR", "TEST_ERROR", "TIMEOUT", "KILLED", "SURVIVED")
ERRORS = ("SYNTAX_ERROR", "IMPORT_ERROR", "TEST_ERROR")
APPLICABLE = ("DUPLICATE", "SYNTAX_ERROR") + EXECUTED
ADJUDICATIONS = ("EQUIVALENT", "NOT_EQUIVALENT")

_EDIT_KEYS = ("edit_id", "path", "module", "find", "replace", "intended_fault")
_EDIT_OPTIONAL = ("occurrence", "witness")
_MODULE = re.compile(r"\A[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
_MARK = "@@RSO_MUTATION_RESULT@@"

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(PKG_DIR))


class MutationError(ValueError):
    """The edits file, rows file, or an adjudication is refused."""


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------------------------------------
# Edits file

def _no_duplicates(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise MutationError("duplicate key %r" % k)
        out[k] = v
    return out


def _module_path_matches(path, module):
    p = path.replace("\\", "/")
    stem = module.replace(".", "/")
    return p == stem + ".py" or p == stem + "/__init__.py"


def load_edits(path):
    """Read and validate an edits file; return (edits list, sha256 of the file bytes)."""
    with open(path, "rb") as f:
        raw = f.read()
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicates)
    except (UnicodeDecodeError, ValueError) as e:
        raise MutationError("edits file unreadable: %s" % e)
    if not isinstance(doc, dict) or sorted(doc) != ["edits", "schema"] or doc["schema"] != EDITS_SCHEMA:
        raise MutationError("edits file must be {schema: %s, edits: [...]}" % EDITS_SCHEMA)
    edits = doc["edits"]
    if not isinstance(edits, list) or not edits:
        raise MutationError("edits must be a non-empty list")
    seen = set()
    for i, e in enumerate(edits):
        where = "edits[%d]" % i
        if not isinstance(e, dict):
            raise MutationError(where + ": object required")
        for k in _EDIT_KEYS:
            if k not in e:
                raise MutationError("%s: missing %s" % (where, k))
        for k in e:
            if k not in _EDIT_KEYS and k not in _EDIT_OPTIONAL:
                raise MutationError("%s: unknown field %s" % (where, k))
        for k in ("edit_id", "path", "module", "find", "intended_fault"):
            if not isinstance(e[k], str) or not e[k]:
                raise MutationError("%s.%s: non-empty string required" % (where, k))
        if not isinstance(e["replace"], str):
            raise MutationError(where + ".replace: string required")
        if e["edit_id"] in seen:
            raise MutationError("%s: duplicate edit_id %s" % (where, e["edit_id"]))
        seen.add(e["edit_id"])
        if not _MODULE.match(e["module"]) or not _module_path_matches(e["path"], e["module"]):
            raise MutationError("%s: path %r does not hold module %r" % (where, e["path"], e["module"]))
        if os.path.isabs(e["path"]) or ".." in e["path"].replace("\\", "/").split("/"):
            raise MutationError(where + ".path: relative path inside root required")
        if "occurrence" in e:
            o = e["occurrence"]
            if not isinstance(o, int) or isinstance(o, bool) or o < 1:
                raise MutationError(where + ".occurrence: integer >= 1 required")
        if "witness" in e:
            w = e["witness"]
            if not isinstance(w, dict) or sorted(w) != ["expr"] or not isinstance(w["expr"], str) \
                    or not w["expr"]:
                raise MutationError(where + ".witness: {expr: <python expression over m>} required")
    return edits, _sha256(raw)


def _is_committed(path):
    """True iff `path` is tracked by git and has no uncommitted change (plan s5: edits committed first)."""
    d = os.path.dirname(os.path.abspath(path)) or "."
    name = os.path.basename(path)
    try:
        r1 = subprocess.run(["git", "ls-files", "--error-unmatch", "--", name], cwd=d,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        if r1.returncode != 0:
            return False
        r2 = subprocess.run(["git", "status", "--porcelain", "--", name], cwd=d,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=60,
                            universal_newlines=True)
        return r2.returncode == 0 and r2.stdout.strip() == ""
    except (OSError, subprocess.SubprocessError):
        return False


def apply_edit(source, e):
    """Return the edited source text, or None when the edit is not applicable."""
    find, n = e["find"], source.count(e["find"])
    occ = e.get("occurrence")
    if n == 0 or (occ is None and n != 1) or (occ is not None and occ > n):
        return None
    k = occ or 1
    start = -1
    for _ in range(k):
        start = source.index(find, start + 1)
    edited = source[:start] + e["replace"] + source[start + len(find):]
    return None if edited == source else edited


# --------------------------------------------------------------------------------------------------------
# Child process: inject the edited module in memory, evaluate the witness, run the frozen suite.

_CHILD = r'''
import importlib, importlib.util, io, json, sys, time, types, unittest
job = json.loads(sys.stdin.read())
for p in reversed(job["sys_path"]):
    sys.path.insert(0, p)
sys.dont_write_bytecode = True
c0 = time.process_time()
out = {"phase": "done"}
def emit():
    out["cpu_s"] = time.process_time() - c0
    sys.stdout.write("\n" + job["mark"] + json.dumps(out) + "\n")
    sys.stdout.flush()
name = job["module"]
try:
    if job["source"] is not None:
        parent, _, leaf = name.rpartition(".")
        pkg = importlib.import_module(parent) if parent else None
        mod = types.ModuleType(name)
        mod.__file__ = job["filename"]
        mod.__package__ = parent if leaf != "__init__" else name
        mod.__spec__ = importlib.util.spec_from_loader(name, loader=None, origin=job["filename"])
        sys.modules[name] = mod
        exec(compile(job["source"], job["filename"], "exec"), mod.__dict__)
        if pkg is not None:
            setattr(pkg, leaf, mod)
    else:
        importlib.import_module(name)
except BaseException as e:
    out = {"phase": "import_error", "detail": "%s: %s" % (type(e).__name__, e)}
    emit()
    sys.exit(0)
wit = {}
for expr in job["witness"]:
    try:
        wit[expr] = repr(eval(expr, {"m": sys.modules[name]}))
    except BaseException as e:
        wit[expr] = "raised %s: %s" % (type(e).__name__, e)
out["witness"] = wit
suite = unittest.TestLoader().loadTestsFromNames(job["suite"])
res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
out.update({"tests_run": res.testsRun, "failures": len(res.failures), "errors": len(res.errors),
            "skipped": len(res.skipped)})
emit()
'''


def _run_child(job, timeout_s):
    t0 = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, "-B", "-c", _CHILD], input=json.dumps(job),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
                           timeout=timeout_s, cwd=job["sys_path"][0])
    except subprocess.TimeoutExpired:
        return {"phase": "timeout"}, time.perf_counter() - t0
    wall = time.perf_counter() - t0
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith(_MARK)]
    if not lines:
        tail = (p.stderr or "").strip().splitlines()[-1:] or ["no result line"]
        return {"phase": "import_error", "detail": "child exited %s: %s" % (p.returncode, tail[0])}, wall
    return json.loads(lines[-1][len(_MARK):]), wall


def _classify(res):
    phase = res["phase"]
    if phase == "timeout":
        return "TIMEOUT"
    if phase == "import_error":
        return "IMPORT_ERROR"
    if res["failures"] > 0:
        return "KILLED"
    if res["errors"] > 0:
        return "TEST_ERROR"
    return "SURVIVED"


# --------------------------------------------------------------------------------------------------------
# Rows

class _Rows(object):
    def __init__(self, path):
        try:
            self.f = open(path, "x", encoding="utf-8", newline="\n")
        except FileExistsError:
            raise MutationError("rows file exists; rows are append-only and never overwritten: %s" % path)

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        self.f.flush()
        os.fsync(self.f.fileno())

    def close(self):
        self.f.close()


def load_rows(path):
    """Read a rows file; require header first and a terminal row last whose count matches."""
    with open(path, "r", encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    if not rows or rows[0].get("row") != "header" or rows[-1].get("row") != "terminal":
        raise MutationError("rows file not terminal (header ... terminal): %s" % path)
    n = sum(1 for r in rows if r.get("row") == "edit")
    if rows[-1].get("edit_rows") != n:
        raise MutationError("terminal row count %r != %d edit rows" % (rows[-1].get("edit_rows"), n))
    return rows


def summarize(rows, adjudications=None):
    """Counts over edit rows (EDIT_COUNTS plus detail). Equivalence only from a reviewer's adjudication."""
    edits = [r for r in rows if r.get("row") == "edit"]
    by_id = {r["edit_id"]: r for r in edits}
    adjudications = dict(adjudications or {})
    for eid, verdict in adjudications.items():
        if verdict not in ADJUDICATIONS:
            raise MutationError("adjudication %r for %s not in %s" % (verdict, eid, ADJUDICATIONS))
        r = by_id.get(eid)
        if r is None or r["status"] != "SURVIVED":
            raise MutationError("only a SURVIVED edit is adjudicated: %s" % eid)
        if verdict == "EQUIVALENT" and r["equivalence"] == "NOT_EQUIVALENT_WITNESSED":
            raise MutationError("%s has a witnessed behavioural difference; it cannot be EQUIVALENT" % eid)
    st = [r["status"] for r in edits]
    surv = [r for r in edits if r["status"] == "SURVIVED"]
    s = {
        "proposed": len(edits),
        "applicable": sum(1 for x in st if x in APPLICABLE),
        "duplicate": st.count("DUPLICATE"),
        "executed": sum(1 for x in st if x in EXECUTED),
        "killed": st.count("KILLED"),
        "survived": len(surv),
        "equivalent": sum(1 for r in surv if adjudications.get(r["edit_id"]) == "EQUIVALENT"),
        "error": sum(1 for x in st if x in ERRORS),
        "timeout": st.count("TIMEOUT"),
    }
    s["error_detail"] = {k: st.count(k) for k in ERRORS}
    s["not_applicable"] = st.count("NOT_APPLICABLE")
    s["not_run"] = {"baseline": st.count("NOT_RUN_BASELINE"), "cap": st.count("NOT_RUN_CAP")}
    s["cap_exhausted"] = st.count("NOT_RUN_CAP") > 0
    s["unresolved_survivors"] = sum(1 for r in surv if r["equivalence"] != "NOT_EQUIVALENT_WITNESSED"
                                    and r["edit_id"] not in adjudications)
    return s


# --------------------------------------------------------------------------------------------------------
# Runner

def run(edits_path, root, suite, rows_path, timeout_s=60, require_committed=True, max_child_seconds=None):
    """Run every edit of an edits file against the frozen `suite` (unittest names importable from root).

    root               directory placed first on the child's sys.path; edit paths are relative to it
    rows_path          new JSONL file (refused if it exists)
    require_committed  refuse an edits file that is untracked or modified in git (plan s5)
    max_child_seconds  cap on summed child wall seconds (timeouts charged at timeout_s); once reached,
                       remaining edits are NOT_RUN_CAP and the partial rows are kept (plan s6)
    Returns {"rows_path", "baseline", "summary"}.
    """
    if not isinstance(suite, (list, tuple)) or not suite or not all(isinstance(s, str) for s in suite):
        raise MutationError("suite must be a non-empty list of unittest names")
    if require_committed and not _is_committed(edits_path):
        raise MutationError("edits file is not committed (plan s5: edits are committed before execution)")
    edits, edits_sha = load_edits(edits_path)
    root = os.path.abspath(root)
    sys_path = [root] + ([REPO_ROOT] if REPO_ROOT != root else [])
    sources = {}
    for e in edits:
        if e["path"] not in sources:
            fp = os.path.join(root, e["path"])
            with open(fp, "rb") as f:
                sources[e["path"]] = f.read().decode("utf-8")
    witnesses = sorted({e["witness"]["expr"] for e in edits if "witness" in e})

    rows = _Rows(rows_path)
    try:
        rows.write({"row": "header", "schema": ROWS_SCHEMA, "edits_file": edits_path.replace("\\", "/"),
                    "edits_sha256": edits_sha, "suite": list(suite), "timeout_s": timeout_s,
                    "max_child_seconds": max_child_seconds, "python": sys.version.split()[0],
                    "sources": {p: _sha256(s) for p, s in sorted(sources.items())},
                    "started_at_utc": _utc_now()})
        charged = 0.0
        # Baseline: the unchanged suite, original modules imported from disk, witnesses on the original.
        base_witness = {}
        base_ok = True
        for module in sorted({e["module"] for e in edits}):
            job = {"sys_path": sys_path, "module": module, "source": None, "filename": None,
                   "suite": list(suite), "witness": [w for w in witnesses
                                                     if any(e["module"] == module and e.get("witness", {})
                                                            .get("expr") == w for e in edits)],
                   "mark": _MARK}
            res, wall = _run_child(job, timeout_s)
            charged += timeout_s if res["phase"] == "timeout" else wall
            ok = res["phase"] == "done" and res["failures"] == 0 and res["errors"] == 0 \
                and res["tests_run"] > 0
            base_ok = base_ok and ok
            for w, v in res.get("witness", {}).items():
                base_witness[(module, w)] = v
            rows.write({"row": "baseline", "module": module, "status": "PASSED" if ok else "FAILED",
                        "phase": res["phase"], "tests_run": res.get("tests_run"),
                        "failures": res.get("failures"), "errors": res.get("errors"),
                        "detail": res.get("detail"), "wall_seconds": round(wall, 3)})

        seen = {}
        written = []
        for e in edits:
            row = {"row": "edit", "edit_id": e["edit_id"], "path": e["path"], "module": e["module"],
                   "intended_fault": e["intended_fault"], "edited_sha256": None, "duplicate_of": None,
                   "tests_run": None, "failures": None, "errors": None, "detail": None, "witness": None,
                   "equivalence": None, "wall_seconds": 0}
            if not base_ok:
                row["status"] = "NOT_RUN_BASELINE"
            elif max_child_seconds is not None and charged >= max_child_seconds:
                row["status"] = "NOT_RUN_CAP"
            else:
                edited = apply_edit(sources[e["path"]], e)
                if edited is None:
                    row["status"] = "NOT_APPLICABLE"
                else:
                    h = _sha256(edited)
                    row["edited_sha256"] = h
                    key = (e["path"], h)
                    if key in seen:
                        row["status"], row["duplicate_of"] = "DUPLICATE", seen[key]
                    else:
                        seen[key] = e["edit_id"]
                        fn = os.path.join(root, e["path"])
                        try:
                            compile(edited, fn, "exec")
                        except (SyntaxError, ValueError) as err:
                            row["status"], row["detail"] = "SYNTAX_ERROR", "%s: %s" % (
                                type(err).__name__, err)
                        else:
                            wexpr = e.get("witness", {}).get("expr")
                            job = {"sys_path": sys_path, "module": e["module"], "source": edited,
                                   "filename": fn, "suite": list(suite),
                                   "witness": [wexpr] if wexpr else [], "mark": _MARK}
                            res, wall = _run_child(job, timeout_s)
                            charged += timeout_s if res["phase"] == "timeout" else wall
                            row["status"] = _classify(res)
                            row["wall_seconds"] = round(wall, 3)
                            row["detail"] = res.get("detail")
                            for k in ("tests_run", "failures", "errors"):
                                row[k] = res.get(k)
                            if row["status"] == "SURVIVED":
                                row["equivalence"] = "UNRESOLVED"
                                if wexpr:
                                    orig = base_witness.get((e["module"], wexpr))
                                    mut = res.get("witness", {}).get(wexpr)
                                    differs = orig is not None and mut is not None and orig != mut
                                    row["witness"] = {"expr": wexpr, "original": orig, "mutant": mut,
                                                      "result": "DIFFERS" if differs
                                                      else "NO_DIFFERENCE_OBSERVED"}
                                    if differs:
                                        row["equivalence"] = "NOT_EQUIVALENT_WITNESSED"
            rows.write(row)
            written.append(row)
        summary = summarize(written)
        rows.write({"row": "terminal", "edit_rows": len(written), "summary": summary,
                    "child_seconds_charged": round(charged, 3), "ended_at_utc": _utc_now()})
    finally:
        rows.close()
    return {"rows_path": rows_path, "baseline": "PASSED" if base_ok else "FAILED", "summary": summary}
