"""NS-01 evaluation of one proposal (GENERATION_PROTOCOL.md steps 1-4). Executable judgements only.

    python -m prometheus.cosmos.ns01.evaluate one <campaign_dir> <arm> <idx> <source.py | spec.json>
Appends to <campaign_dir>/CANDIDATES.jsonl (frozen sha first) and EXCLUSION_RESULTS.jsonl; prints the compact
signal (the only thing an Arm C / D generator ever sees).
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ALLOWED_IMPORTS = {"numpy", "prometheus.cosmos.c3.system", "prometheus.cosmos.c3.task"}
BANNED_NAMES = {"open", "eval", "exec", "__import__", "compile", "globals", "input", "breakpoint"}


def compliance(src: str):
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return f"syntax error: {e}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] != "numpy":
                    return f"import {a.name} not allowed"
        if isinstance(node, ast.ImportFrom):
            if node.module not in ALLOWED_IMPORTS and (node.module or "").split(".")[0] != "numpy":
                return f"from {node.module} not allowed"
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            return f"name {node.id} not allowed"
        if isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr not in ("__init__",):
            return f"dunder attribute {node.attr} not allowed"
    return None


def load_llm(src: str):
    ns = {}
    exec(compile(src, "<candidate>", "exec"), ns)          # source passed the AST gate above
    if "make" not in ns:
        raise ValueError("no make(task)")
    return ns["make"]


def dry_run(make):
    from prometheus.cosmos.c3.task import Task
    for k in (1, 4):
        t = Task(4, k)
        m = make(t)
        rng = np.random.default_rng(0)
        st = m.init(64)
        t0 = time.time()
        for _ in range(k + 2):
            st = m.step(st, rng.integers(0, 13, 64), m.noise(64, rng))
            if not isinstance(st, dict):
                raise TypeError("step must return a dict")
        R, F = np.asarray(m.readout_features(st), float), np.asarray(m.full_state(st), float)
        if R.shape[0] != 64 or F.shape[0] != 64 or R.ndim != 2 or F.ndim != 2:
            raise ValueError(f"bad shapes {R.shape} {F.shape}")
        if not (np.all(np.isfinite(R)) and np.all(np.isfinite(F))):
            raise ValueError("non-finite features")
    m = make(Task(4, 8))
    st = m.init(4000)
    rng = np.random.default_rng(1)
    t0 = time.time()
    for _ in range(3):
        st = m.step(st, rng.integers(0, 13, 4000), m.noise(4000, rng))
    per = (time.time() - t0) / 3
    if per > 0.25:
        raise ValueError(f"step too slow: {per:.3f}s at E=4000")
    return per


def label(sig, cls, d_near):
    from prometheus.cosmos.ns01.signature import TAU
    f = cls["fired"]
    if "DEGENERATE" in f:
        return "DEGENERATE"
    if d_near <= TAU:
        return "KNOWN_EQUIVALENCE"
    if not cls["viable"] and f:
        return "KNOWN_FAILURE"
    if cls["viable"] and f:
        return "VIABLE_KNOWN_STRUCTURE"
    if cls["viable"]:
        return "VIABLE_DISTINCT"
    return "DISTINCT_BEHAVIOR_UNEXPLAINED"


def signal(lab, cls):
    if lab == "NONEXECUTABLE":
        return "REJECTED: not executable"
    if lab == "DEGENERATE":
        return "REJECTED: degenerate"
    if lab == "KNOWN_EQUIVALENCE":
        return "REJECTED: equivalent to a known mechanism"
    if lab in ("KNOWN_FAILURE", "VIABLE_KNOWN_STRUCTURE"):
        return "REJECTED: known failure class " + ",".join(x for x in cls["fired"])
    return "ACCEPTED"


def _sigjson(sig):
    return {k: ({str(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in sig.items()}


def witness_sigs(cache: Path):
    from prometheus.cosmos.ns01 import signature as S
    from prometheus.cosmos.ns01.witnesses import WITNESSES
    if cache.exists():
        d = json.loads(cache.read_text())
        return {n: {k: ({int(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in s.items()}
                for n, s in d.items()}
    d = {n: S.signature(f) for n, (f, _, _) in WITNESSES.items()}
    cache.write_text(json.dumps({n: _sigjson(s) for n, s in d.items()}))
    return d


def evaluate(camp: Path, arm: str, idx: int, path: Path, meta: dict = None) -> dict:
    from prometheus.cosmos.ns01 import signature as S
    from prometheus.cosmos.ns01.grammar import make_from_spec
    raw = path.read_text()
    sha = hashlib.sha256(raw.encode()).hexdigest()
    cand = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "arm": arm, "idx": idx, "file": str(path),
            "sha256": sha, "kind": "grammar_spec" if path.suffix == ".json" else "llm_source", **(meta or {})}
    with open(camp / "CANDIDATES.jsonl", "a") as fh:                    # frozen before execution
        fh.write(json.dumps(cand, sort_keys=True) + "\n")
    t0 = time.process_time()
    res = {"arm": arm, "idx": idx, "sha256": sha}
    try:
        if path.suffix == ".json":
            make = make_from_spec(json.loads(raw))
        else:
            bad = compliance(raw)
            if bad:
                raise ValueError("compliance: " + bad)
            make = load_llm(raw)
        res["step_s_E4000"] = dry_run(make)
        sig = S.signature(make)
        cls = S.classify(sig)
        W = witness_sigs(camp / "witness_signatures.json")
        d = {n: S.distance(sig, w) for n, w in W.items()}
        near = min(d, key=d.get)
        lab = label(sig, cls, d[near])
        res.update({"sig": _sigjson(sig), "cls": cls, "nearest_witness": near, "d_nearest": d[near],
                    "d_witness": d, "label": lab})
    except Exception as e:
        res.update({"label": "NONEXECUTABLE", "error": repr(e)[:500], "cls": {"fired": [], "viable": False}})
    res["cpu_s"] = round(time.process_time() - t0, 1)
    res["signal"] = signal(res["label"], res["cls"])
    with open(camp / "EXCLUSION_RESULTS.jsonl", "a") as fh:
        fh.write(json.dumps(res, sort_keys=True, default=float) + "\n")
    return res


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "one":
        r = evaluate(Path(a[2]), a[3], int(a[4]), Path(a[5]))
        print(json.dumps({"label": r["label"], "signal": r["signal"], "nearest": r.get("nearest_witness"),
                          "d": r.get("d_nearest"), "fired": r["cls"]["fired"], "err": r.get("error")}, default=float))
