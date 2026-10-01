"""Derived-file reproduction (regression infrastructure, CORRECTIONS 2026-10-01 K14).

Invariant: every committed derived results file under hecate/ equals what its
committed generator produces from committed rows -- OR it is listed in
HISTORICAL below, with a pointer to its current re-derivation.

hecate/autopsy/FLOW.json went stale after K4 because nothing re-derived it.
These tests re-derive every covered file IN MEMORY or in a temporary sandbox
copy and compare. Nothing is ever written into the repository:
  * pure functions are called directly (flow.flow, index.build, ...);
  * generators that write their own output have their output directory
    monkeypatched to tmp_path (reach.HERE, meta.analyze.HERE, corpus.OUT_DIR,
    index.OUT);
  * fold reports (probe_report, probe_round3, pass4_report) run against a
    sandbox copy of hecate/programs/**.json with PROGS patched;
  * world evaluators (evaluate.py, attain.py, pilot_eval.py) run as scripts in
    a sandbox copy of their program directory.
No model/API calls are made: the gravity gate is rebuilt from committed rows
by calibration_gate() without run_items().

Ignored when comparing:
  * ANNOTATION_KEYS (top level only): documented hand annotations added after
    derivation ("corrections", "_note", "note").
  * VOLATILE_WORLD_KEYS (world evaluator outputs only): "core_minutes" -- the
    evaluators add their own process CPU time (and, for some, prior-attempt
    CPU from the environment), so it cannot reproduce by construction.
  * STATE_DEPENDENT_KEYS (named fold reports only): a fold copies a field from
    the program record as it stood at fold time; later rounds rewrote that
    record and the pre-fold state is not committed as rows.

test_inventory_every_derived_json_is_classified fails on any JSON under hecate/
that is neither covered here, HISTORICAL, nor explicitly classified as
non-derived / gap, so new derived files cannot silently escape.

Heavy work (alien scoring, dataset rebuild, world scripts) is started once per
session in a process/thread pool so the whole module stays within ~3 minutes.
"""

from __future__ import annotations

import fnmatch
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEC = os.path.join(ROOT, "hecate")
PROGS = os.path.join(HEC, "programs")

ANNOTATION_KEYS = frozenset({"corrections", "_note", "note"})
VOLATILE_WORLD_KEYS = frozenset({"core_minutes"})
STATE_DEPENDENT_KEYS = {
    # probe_report.fold() records p["currentVerdict"] after round 1; rounds 2/3
    # and Pass 4 have since rewritten every one of those program records.
    "hecate/programs/PROBE_ROUND1_REPORT.json": {"worlds[].verdict_after"},
}

# Per-script environment the committed outputs were produced with (read from
# the outputs' own fields; see each evaluator's header).
WORLD_ENV = {
    "HT-79e904e13a/worlds/W4/evaluate.py": {"W4_ATTEMPTS": "2"},
}

# Known historical snapshots. Each entry must (a) still DIFFER from what its
# generator now produces (else the entry has rotted and must be removed) and
# (b) name its current re-derivation, which must reproduce.
HISTORICAL = {
    "hecate/autopsy/FLOW.json": {
        "why": "Part A flow derived before K4 (a9e2 W3 NULL -> SPEC_UNATTAINABLE); "
               "kept as the pre-K4 record (CORRECTIONS 2026-10-01 K14).",
        "successor": "hecate/autopsy/FLOW_postK4.json",
    },
    "hecate/alien/runs/gptoss/RESULTS.json": {
        "why": "scored on the 29-row partial blind run; newer blind rows were "
               "appended by the B/C trickle (INV_Z4: 48/100 scored).",
        "successor": None,   # no committed successor: `python -m hecate.alien.analyze gptoss`
    },
    # Pilot attempt-1 snapshots whose attempt-1 rerun no longer reproduces them.
    # Successor: the world's PILOT.json (the passing attempt), which must reproduce.
    "hecate/programs/HT-37e311ce05/worlds/W4/PILOT_attempt1.json": {
        "why": "superseded pilot attempt 1 (pilot repaired before attempt 2).",
        "successor": "hecate/programs/HT-37e311ce05/worlds/W4/PILOT.json",
    },
    "hecate/programs/HT-55162c0ac0/worlds/W2/PILOT_attempt1.json": {
        "why": "superseded pilot attempt 1 (pilot repaired before attempt 2).",
        "successor": "hecate/programs/HT-55162c0ac0/worlds/W2/PILOT.json",
    },
    "hecate/programs/HT-8a87057933/worlds/W4/PILOT_attempt1.json": {
        "why": "superseded pilot attempt 1 (pilot repaired before attempt 2).",
        "successor": "hecate/programs/HT-8a87057933/worlds/W4/PILOT.json",
    },
    "hecate/programs/HT-a9e2ba7618/worlds/W3/PILOT_attempt1.json": {
        "why": "superseded pilot attempt 1 (pilot repaired before attempt 2).",
        "successor": "hecate/programs/HT-a9e2ba7618/worlds/W3/PILOT.json",
    },
    "hecate/programs/HT-ae38c641b1/worlds/W4/PILOT_attempt1.json": {
        "why": "superseded pilot attempt 1 (pilot repaired before attempt 2).",
        "successor": "hecate/programs/HT-ae38c641b1/worlds/W4/PILOT.json",
    },
}

# JSON under hecate/ that is NOT a derived result of a committed generator, or a
# known coverage gap. (pattern, category, reason); first match wins.
CLASSIFIED = [
    ("hecate/programs/HT-*/program.json", "RECORD",
     "program record: input to folds and target of fold mutations, not a pure derivation"),
    ("hecate/programs/*/spec.json", "INPUT", "frozen world spec"),
    ("hecate/programs/*/revisions.json", "INPUT", "spec revision record"),
    ("hecate/programs/*/_rev0/*", "SUPERSEDED", "pre-revision copy kept for provenance"),
    ("hecate/alien/data/*", "COVERED_ELSEWHERE", None),       # filled below
    ("hecate/alien/visual/*.json", "COVERED_ELSEWHERE", None),
    ("hecate/gravity/controls_v1.json", "INPUT", "detector calibration controls (frozen)"),
    ("hecate/programs/*/world_cpu*.json", "MEASUREMENT", "CPU/runtime ledger"),
    ("hecate/programs/*/pilot_cpu*.json", "MEASUREMENT", "CPU/runtime ledger"),
    ("hecate/programs/*/controls_cpu.json", "MEASUREMENT", "CPU/runtime ledger"),
    ("hecate/programs/*/compute*.json", "MEASUREMENT", "CPU/runtime ledger"),
    ("hecate/programs/*/cost.json", "MEASUREMENT", "CPU/runtime ledger"),
    ("hecate/programs/*run_meta.json", "MEASUREMENT", "runner metadata"),
    ("hecate/programs/*/attack_meta.json", "MEASUREMENT", "runner metadata"),
    ("hecate/programs/*/attempts.json", "MEASUREMENT", "attempt counter written by the runner"),
    ("hecate/programs/*/*attempt*.json", "SUPERSEDED",
     "superseded attempt output; its generator input is not separately re-runnable"),
    ("hecate/programs/*/OUTCOME.json", "GAP",
     "no evaluate.py beside it: written by the pilot/world runner on a pilot failure"),
    ("hecate/programs/*ATTAINABILITY.json", "GAP",
     "written by controls.py/alt_controls.py in the same process that simulates the rows "
     "(or assembled by hand); no rows-only entry point"),
    ("hecate/programs/*/control_summary.json", "GAP", "written by the controls simulation"),
    ("hecate/programs/*/calibration.json", "GAP", "written by the world/probe simulation"),
]
_ALIEN_DATA = "regenerated by test_alien_dataset_rebuild / test_alien_baselines / test_alien_visual"
CLASSIFIED = [(p, c, r if r is not None else _ALIEN_DATA) for p, c, r in CLASSIFIED]


# --------------------------------------------------------------------------- helpers

def _rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def _abs(rel):
    return os.path.join(ROOT, *rel.split("/"))


def _load(rel_or_abs):
    p = rel_or_abs if os.path.isabs(rel_or_abs) else _abs(rel_or_abs)
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _rt(obj, default=None):
    return json.loads(json.dumps(obj, default=default))


def _strip(obj, keys=ANNOTATION_KEYS):
    return {k: v for k, v in obj.items() if k not in keys} if isinstance(obj, dict) else obj


def _drop_paths(obj, paths):
    """Remove 'a[].b' style paths (list wildcard) from a deep copy."""
    obj = json.loads(json.dumps(obj))
    for path in paths:
        parts = path.split(".")

        def go(o, i):
            if i == len(parts) - 1:
                key = parts[i]
                if isinstance(o, dict):
                    o.pop(key, None)
                return
            key = parts[i]
            if key.endswith("[]"):
                for x in (o.get(key[:-2]) or []) if isinstance(o, dict) else []:
                    go(x, i + 1)
            elif isinstance(o, dict) and key in o:
                go(o[key], i + 1)
        go(obj, 0)
    return obj


def _diff(a, b, path="", out=None, limit=15):
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                out.append(f"{path}.{k}: absent in regenerated")
            elif k not in b:
                out.append(f"{path}.{k}: absent in committed")
            else:
                _diff(a[k], b[k], f"{path}.{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            _diff(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append(f"{path}: regenerated={str(a)[:90]!s} committed={str(b)[:90]!s}")
    return out


def assert_reproduces(regen, rel, ignore=ANNOTATION_KEYS, drop=()):
    committed = _drop_paths(_strip(_load(rel), ignore), drop)
    regen = _drop_paths(_strip(_rt(regen), ignore), drop)
    if regen != committed:
        d = _diff(regen, committed)
        pytest.fail(f"{rel} does NOT reproduce from its generator "
                    f"({len(d)}+ differences):\n  " + "\n  ".join(d))


def _norm_bytes(p):
    with open(p, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


# --------------------------------------------------------------------------- heavy jobs
# Top-level functions so they pickle into spawned worker processes.

def _alien_shard(model, sids):
    from hecate.alien import analyze as AA
    from hecate.alien import runner
    pub, key = runner.load()
    AA.load = lambda: (pub, {s: key[s] for s in sids})
    try:
        rows, _ = AA.per_system(model)
    finally:
        AA.load = runner.load                  # workers are reused: never leak the patch
    return rows


def _alien_summary(model, rows):
    from hecate.alien import analyze as AA
    from hecate.alien import runner
    pub, key = runner.load()
    orig = AA.per_system
    AA.per_system = lambda m: (rows, key)
    try:
        res, rows2 = AA.summarize(model)
    finally:
        AA.per_system = orig
    default = lambda o: dict(o) if isinstance(o, Counter) else str(o)   # analyze.__main__
    return _rt({"summary": res, "rows": rows2}, default)


def _dataset_build():
    from hecate.alien import dataset as D
    public, key, _ = D.build()
    return _rt(public, int), _rt(key, int)


def _baselines():
    from hecate.alien import baselines as B
    rows = B.run()
    return _rt({"summary": B.summarize(rows), "rows": rows}, str)


def _visual():
    from hecate.alien import visual as V
    sets, vkey = V.build()
    return _rt(sets), _rt(vkey, int)


def _world_scripts():
    """(script rel to PROGS, argv sequence, expected committed outputs)."""
    jobs = []
    for s in sorted(glob.glob(os.path.join(PROGS, "HT-*", "worlds", "**", "*.py"), recursive=True)):
        name = os.path.basename(s)
        if name not in ("evaluate.py", "attain.py", "pilot_eval.py"):
            continue
        d = os.path.dirname(s)
        rel = os.path.relpath(s, PROGS).replace(os.sep, "/")
        src = open(s, encoding="utf-8").read()
        writes = {"evaluate.py": ("OUTCOME.json", "PASS4_OUTCOME.json", "CONTROLS.json"),
                  "attain.py": ("ATTAINABILITY.json",), "pilot_eval.py": ("PILOT.json",)}[name]
        outs = [f for f in writes if f in src and os.path.exists(os.path.join(d, f))]
        argvs = [[]]
        if name == "pilot_eval.py":
            att = [(_load(p).get("attempt") or 1) for p in glob.glob(os.path.join(d, "PILOT*.json"))]
            n = max(att or [1])
            if "PILOT_attempt{" in src:                    # faa9: attempt k>1 -> PILOT_attempt{k}.json
                outs += [f"PILOT_attempt{k}.json" for k in range(2, n + 1)]
            if "sys.argv" in src:
                argvs = [[str(k)] for k in range(1, n + 1)]
        outs = [o for o in dict.fromkeys(outs) if os.path.exists(os.path.join(d, o))]
        jobs.append((rel, argvs, outs))
    return jobs


def _attempt1_jobs():
    """PILOT_attempt1.json beside an argv-driven pilot_eval.py: rerun attempt 1."""
    jobs = []
    for p in sorted(glob.glob(os.path.join(PROGS, "HT-*", "worlds", "*", "PILOT_attempt1.json"))):
        d = os.path.dirname(p)
        ev = os.path.join(d, "pilot_eval.py")
        if os.path.exists(ev) and "sys.argv" in open(ev, encoding="utf-8").read():
            jobs.append(os.path.relpath(ev, PROGS).replace(os.sep, "/"))
    return jobs


def _run_world(rel_script, argvs, outs, clear=()):
    """Copy the program dir to a temp sandbox, run the script there, return the
    parsed outputs. Never touches the repository."""
    tid = rel_script.split("/")[0]
    base = tempfile.mkdtemp(prefix="hecate_drv_")
    try:
        dst = os.path.join(base, tid)
        shutil.copytree(os.path.join(PROGS, tid), dst,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        sdir = os.path.join(base, *rel_script.split("/")[:-1])
        for c in clear:
            if os.path.exists(os.path.join(sdir, c)):
                os.remove(os.path.join(sdir, c))
        before = {o: os.stat(os.path.join(sdir, o)).st_mtime_ns
                  for o in outs if os.path.exists(os.path.join(sdir, o))}
        env = dict(os.environ, PYTHONPATH=ROOT + os.pathsep + os.environ.get("PYTHONPATH", ""),
                   MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
        env.update(WORLD_ENV.get(rel_script, {}))
        log = []
        for argv in argvs:
            p = subprocess.run([sys.executable, os.path.basename(rel_script), *argv], cwd=sdir,
                               capture_output=True, text=True, timeout=300, env=env)
            log.append((argv, p.returncode, p.stderr[-400:]))
            if p.returncode:
                return {"error": log}
        res = {}
        for o in outs:
            f = os.path.join(sdir, o)
            if os.path.exists(f) and os.stat(f).st_mtime_ns != before.get(o):
                with open(f, encoding="utf-8") as fh:
                    res[o] = json.load(fh)
        return {"outputs": res, "log": log}
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture(scope="session")
def heavy():
    """Start every slow regeneration at once; tests block on their own future."""
    from hecate.alien import runner
    _, key = runner.load()
    sids = sorted(key)
    n = max(2, min(14, (os.cpu_count() or 4) - 2))
    shards = [sids[i::n] for i in range(n)]
    pp = ProcessPoolExecutor(max_workers=n)
    tp = ThreadPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) // 2))
    fut = {"claude_shards": [pp.submit(_alien_shard, "claude", s) for s in shards],
           "gptoss": pp.submit(_alien_shard, "gptoss", sids),
           "gemini": pp.submit(_alien_shard, "gemini", sids),
           "dataset": pp.submit(_dataset_build),
           "baselines": pp.submit(_baselines),
           "visual": pp.submit(_visual)}
    for rel, argvs, outs in _world_scripts():
        fut[("world", rel)] = tp.submit(_run_world, rel, argvs, outs)
    for rel in _attempt1_jobs():
        fut[("attempt1", rel)] = tp.submit(_run_world, rel, [["1"]], ["PILOT.json"],
                                           clear=("PILOT.json",))
    fut["_pp"] = pp
    yield fut
    tp.shutdown(wait=True)
    pp.shutdown(wait=True)


def _alien(heavy, model):
    if model == "claude":
        rows = {}
        for f in heavy["claude_shards"]:
            rows.update(f.result())
        rows = dict(sorted(rows.items()))
    else:
        rows = heavy[model].result()
    return heavy["_pp"].submit(_alien_summary, model, rows).result()


# --------------------------------------------------------------------------- autopsy

def test_flow_postK4_reproduces():
    from hecate.autopsy import flow
    assert_reproduces(_rt(flow.flow(), str), "hecate/autopsy/FLOW_postK4.json")


def test_reach_reproduces(monkeypatch, tmp_path):
    from hecate.autopsy import reach
    monkeypatch.setattr(reach, "HERE", str(tmp_path))      # score() writes REACH.json to HERE
    assert_reproduces(reach.score(), "hecate/autopsy/REACH.json")


# --------------------------------------------------------------------------- meta / gravity

def test_meta_results_v1_reproduces(monkeypatch, tmp_path):
    from hecate.meta import analyze as MA
    monkeypatch.setattr(MA, "HERE", str(tmp_path))          # main() writes RESULTS_v1.json to HERE
    assert_reproduces(MA.main(), "hecate/meta/RESULTS_v1.json")


def _gravity_gate():
    from hecate.gravity import run as G
    latest = {}
    with open(os.path.join(HEC, "gravity", "calibration_rows_v1.jsonl"), encoding="utf-8") as fh:
        for l in fh:                                       # run_items(): latest row per item wins
            if l.strip():
                r = json.loads(l)
                latest[r["item"]] = r
    table, gate = G.calibration_gate(latest)
    return {"table": table, "gate": gate}


@pytest.mark.parametrize("rel", ["hecate/gravity/gate_v1.json", "hecate/gravity/calibration_v1.json"])
def test_gravity_gate_reproduces(rel):
    assert_reproduces(_gravity_gate(), rel)


# --------------------------------------------------------------------------- index / corpus

def test_index_reproduces(monkeypatch, tmp_path):
    from hecate import index
    monkeypatch.setattr(index, "OUT", str(tmp_path))
    index.write()
    for name in ("SUMMARY.json", "nodes.jsonl", "edges.jsonl"):
        assert _norm_bytes(tmp_path / name) == _norm_bytes(os.path.join(HEC, "index", name)), \
            f"hecate/index/{name} does NOT reproduce from hecate.index.build()"


def test_corpus_receipt_reproduces(monkeypatch, tmp_path):
    from hecate import corpus
    monkeypatch.setattr(corpus, "OUT_DIR", str(tmp_path))
    corpus.build()
    for name in ("CORPUS_RECEIPT.json", "historical_triplicates.jsonl"):
        assert _norm_bytes(tmp_path / name) == _norm_bytes(os.path.join(HEC, "corpus", name)), \
            f"hecate/corpus/{name} does NOT reproduce from hecate.corpus.build()"


# --------------------------------------------------------------------------- fold reports

def _programs_sandbox(tmp_path, *mods):
    d = str(tmp_path / "programs")
    for f in glob.glob(os.path.join(PROGS, "**", "*"), recursive=True):
        if f.endswith(".json") or f.endswith("_SELECTION.jsonl"):
            dst = os.path.join(d, os.path.relpath(f, PROGS))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(f, dst)
    rel = lambda p: "hecate/programs/" + os.path.relpath(p, d).replace(os.sep, "/")
    return d, rel


def _fold_report(name, tmp_path, monkeypatch):
    from hecate import pass4_report as P4, probe_report as PR, probe_round3 as P3
    d, rel = _programs_sandbox(tmp_path)
    for m in (PR, P3, P4):
        monkeypatch.setattr(m, "PROGS", d)
        monkeypatch.setattr(m, "_rel", rel)
    monkeypatch.setattr(PR, "SEL", os.path.join(d, "PROBE_ROUND1_SELECTION.jsonl"))
    if name == "PROBE_ROUND1_REPORT.json":
        return PR.main()
    if name == "PROBE_ROUND2_REPORT.json":
        return PR.fold_round2()
    if name == "PROBE_ROUND3_REPORT.json":
        return P3.fold()
    if name == "PASS4_ROUND1_REPORT.json":                 # pass4_report.__main__
        return {"prereg": P4.PREREG, "worlds": [P4.fold(*t) for t in P4.TARGETS]}
    if name == "PASS4_ROUND2_REPORT.json":
        return {"prereg": P4.R2_PREREG, "worlds": P4.main_round2()}
    raise KeyError(name)


FOLD_REPORTS = ["PROBE_ROUND1_REPORT.json", "PROBE_ROUND2_REPORT.json", "PROBE_ROUND3_REPORT.json",
                "PASS4_ROUND1_REPORT.json", "PASS4_ROUND2_REPORT.json"]


@pytest.mark.parametrize("name", FOLD_REPORTS)
def test_fold_report_reproduces(name, tmp_path, monkeypatch):
    rel = "hecate/programs/" + name
    regen = _fold_report(name, tmp_path, monkeypatch)
    assert_reproduces(regen, rel, drop=STATE_DEPENDENT_KEYS.get(rel, ()))



# Committed files that do NOT reproduce from their generator, recorded rather
# than fixed (data is a record; CORRECTIONS K16). Each must still differ --
# if one starts reproducing, the test fails so the entry gets removed.
KNOWN_NONREPRODUCING = {
    "hecate/alien/runs/gemini/RESULTS.json": "stale: newer valid blind row SYS-10088 never scored in",
    "hecate/programs/HT-55162c0ac0/worlds/W3/OUTCOME.json": "hand-added anomaly and notes text",
    "hecate/programs/HT-5b0b3ebb8d/worlds/W4/OUTCOME.json": "hand-appended post-run descriptive anomalies",
    "hecate/programs/HT-5b0b3ebb8d/worlds/W4/pass4/PASS4_OUTCOME.json": "hand-appended anomalies and notes",
}


def _expect_known_diff(rel, regen_equal):
    assert not regen_equal, f"{rel} now reproduces: remove it from KNOWN_NONREPRODUCING"

# --------------------------------------------------------------------------- alien assay

@pytest.mark.slow
@pytest.mark.parametrize("model", ["claude", "gemini"])
def test_alien_results_reproduce(model, heavy):
    rel = f"hecate/alien/runs/{model}/RESULTS.json"
    if rel in KNOWN_NONREPRODUCING:
        try:
            assert_reproduces(_alien(heavy, model), rel)
            same = True
        except pytest.fail.Exception:
            same = False
        _expect_known_diff(rel, same)
        return
    assert_reproduces(_alien(heavy, model), rel)


@pytest.mark.slow
def test_alien_dataset_rebuild(heavy):
    public, key = heavy["dataset"].result()
    assert public == _load("hecate/alien/data/public.json"), "alien public.json does NOT reproduce"
    assert key == _load("hecate/alien/data/answer_key.json"), "alien answer_key.json does NOT reproduce"


@pytest.mark.slow
def test_alien_baselines(heavy):
    assert_reproduces(heavy["baselines"].result(), "hecate/alien/data/BASELINES.json")


@pytest.mark.slow
def test_alien_visual(heavy):
    sets, vkey = heavy["visual"].result()
    assert sets == _load("hecate/alien/visual/sets.json"), "alien visual/sets.json does NOT reproduce"
    assert vkey == _load("hecate/alien/visual/key.json"), "alien visual/key.json does NOT reproduce"


# --------------------------------------------------------------------------- world evaluators

WORLD_JOBS = _world_scripts()


@pytest.mark.slow
@pytest.mark.parametrize("rel,argvs,outs", WORLD_JOBS, ids=[j[0] for j in WORLD_JOBS])
def test_world_output_reproduces(rel, argvs, outs, heavy):
    assert outs, f"{rel}: no committed output found for this generator"
    r = heavy[("world", rel)].result()
    assert "error" not in r, f"{rel} failed in sandbox: {r.get('error')}"
    wdir = "hecate/programs/" + "/".join(rel.split("/")[:-1])
    missing = [o for o in outs if o not in r["outputs"]]
    assert not missing, f"{rel} did not (re)write {missing}"
    fails = []
    for o in outs:
        target = f"{wdir}/{o}"
        if target in HISTORICAL:
            continue
        committed = _strip(_strip(_load(target)), VOLATILE_WORLD_KEYS)
        regen = _strip(_strip(r["outputs"][o]), VOLATILE_WORLD_KEYS)
        if target in KNOWN_NONREPRODUCING:
            _expect_known_diff(target, regen == committed)
            continue
        if regen != committed:
            fails.append(f"{target}:\n    " + "\n    ".join(_diff(regen, committed)))
    if fails:
        pytest.fail("does NOT reproduce:\n  " + "\n  ".join(fails))


ATTEMPT1_JOBS = _attempt1_jobs()


@pytest.mark.slow
@pytest.mark.parametrize("rel", ATTEMPT1_JOBS)
def test_pilot_attempt1_reproduces_or_is_historical(rel, heavy):
    target = "hecate/programs/" + rel.rsplit("/", 1)[0] + "/PILOT_attempt1.json"
    r = heavy[("attempt1", rel)].result()
    assert "error" not in r, f"{rel} attempt 1 failed in sandbox: {r.get('error')}"
    regen = _strip(r["outputs"]["PILOT.json"])
    same = regen == _strip(_load(target))
    if target in HISTORICAL:
        assert not same, (f"{target} now reproduces: remove its HISTORICAL entry "
                          "(the allowlist must not rot)")
    else:
        assert same, f"{target} does NOT reproduce:\n  " + "\n  ".join(
            _diff(regen, _strip(_load(target))))


# --------------------------------------------------------------------------- historical allowlist

@pytest.mark.parametrize("rel", sorted(HISTORICAL))
def test_historical_snapshot_still_differs_and_successor_reproduces(rel, request):
    entry = HISTORICAL[rel]
    assert os.path.exists(_abs(rel)), f"HISTORICAL entry for missing file {rel}"
    assert entry["why"]
    succ = entry["successor"]
    if rel == "hecate/autopsy/FLOW.json":
        from hecate.autopsy import flow
        regen = _rt(flow.flow(), str)
        assert _strip(regen) != _strip(_load(rel)), \
            f"{rel} now reproduces: remove its HISTORICAL entry"
        assert_reproduces(regen, succ)
    elif rel == "hecate/alien/runs/gptoss/RESULTS.json":
        assert succ is None
        regen = _alien(request.getfixturevalue("heavy"), "gptoss")
        snap = _load(rel)
        assert regen != snap, f"{rel} now reproduces: remove its HISTORICAL entry"
        # current re-derivation (in memory) scores at least the snapshot's rows
        assert regen["summary"]["n_blind"] >= snap["summary"]["n_blind"]
    elif rel.endswith("/PILOT_attempt1.json"):
        # 'still differs' is asserted by test_pilot_attempt1_reproduces_or_is_historical;
        # the successor PILOT.json must be produced by the world job.
        ev = rel[len("hecate/programs/"):].rsplit("/", 1)[0] + "/pilot_eval.py"
        assert ev in ATTEMPT1_JOBS, f"{rel}: no attempt-1 rerun job"
        r = request.getfixturevalue("heavy")[("world", ev)].result()
        assert "error" not in r
        assert _strip(r["outputs"]["PILOT.json"], VOLATILE_WORLD_KEYS | ANNOTATION_KEYS) == \
            _strip(_load(succ), VOLATILE_WORLD_KEYS | ANNOTATION_KEYS), f"successor {succ} does NOT reproduce"
    else:
        pytest.fail(f"HISTORICAL entry {rel} has no check")


# --------------------------------------------------------------------------- inventory

def _covered():
    cov = {"hecate/autopsy/FLOW_postK4.json", "hecate/autopsy/REACH.json",
           "hecate/meta/RESULTS_v1.json", "hecate/gravity/gate_v1.json",
           "hecate/gravity/calibration_v1.json", "hecate/index/SUMMARY.json",
           "hecate/corpus/CORPUS_RECEIPT.json",
           "hecate/alien/runs/claude/RESULTS.json", "hecate/alien/runs/gemini/RESULTS.json"}
    cov |= {"hecate/programs/" + n for n in FOLD_REPORTS}
    for rel, _, outs in WORLD_JOBS:
        cov |= {"hecate/programs/" + rel.rsplit("/", 1)[0] + "/" + o for o in outs}
    for rel in ATTEMPT1_JOBS:
        cov.add("hecate/programs/" + rel.rsplit("/", 1)[0] + "/PILOT_attempt1.json")
    return cov


def _classify(rel):
    for pat, cat, why in CLASSIFIED:
        if fnmatch.fnmatch(rel, pat):
            return cat, why
    return None


def _inventory():
    cov = _covered()
    out = {}
    for p in sorted(glob.glob(os.path.join(HEC, "**", "*.json"), recursive=True)):
        if "__pycache__" in p:
            continue
        rel = _rel(p)
        out[rel] = (("COVERED", None) if rel in cov else
                    ("HISTORICAL", HISTORICAL[rel]["why"]) if rel in HISTORICAL else _classify(rel))
    return out


def test_inventory_every_derived_json_is_classified():
    unclassified = [rel for rel, c in _inventory().items() if c is None]
    assert not unclassified, ("JSON under hecate/ neither re-derived here, HISTORICAL, nor "
                              "classified in CLASSIFIED:\n  " + "\n  ".join(unclassified))


def test_inventory_summary():
    """Never fails on content: prints the coverage table so GAPs stay visible (-s)."""
    inv = _inventory()
    print("\n" + json.dumps(dict(Counter(c[0] for c in inv.values() if c)), sort_keys=True))
    for rel, c in inv.items():
        if c and c[0] == "GAP":
            print("  GAP", rel)
    assert any(c and c[0] == "COVERED" for c in inv.values())
