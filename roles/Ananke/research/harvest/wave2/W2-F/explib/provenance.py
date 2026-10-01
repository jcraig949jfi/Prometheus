"""(7) Intervention provenance: every intervention record carries its seed namespace, a digest of the hook
code that acted, and a link to the commit that froze the plan it serves.

Pieces
  hook_digest(fn, params)     sha256 over the hook's source (or bytecode + constants when no source exists),
                              its qualified name, its closure values, the simple-valued globals it reads,
                              and canonical params (objects reached through attributes are NOT digested:
                              pass what matters as params)
  seeds_digest(ns, seeds)     sha256 over the namespace and the derived unit seeds
  InterventionRecord          frozen dataclass; record_id = sha256 of its canonical JSON (deposit.py style)
  verify_record(...)          R1 id integrity, R2 hook digest recomputed from the live function, R3 plan
                              committed strictly before the first result (tools/freeze_check.py semantics,
                              read-only git), R4 plan blob unchanged since its first add, R5 seed namespace
  seed_reuse(records, groups) arms declared independent must not share a seed namespace
  support_check(claim, recs)  which records may support which claim kind (a TRANSFER cell is not a SEARCH NULL:
                              fac4aaa23 was cited as "C1 search failed multi-hop at d9cc", H-PLANT review)
  Ledger                      append-only JSONL; refuses a duplicate id; verifies every record's hash on read
All git access is read-only (log, rev-parse, merge-base --is-ancestor).
"""
from __future__ import annotations

import dataclasses
import datetime
import hashlib
import inspect
import json
import pathlib
import subprocess
import textwrap
from typing import Any, Callable, Iterable, Optional

from .outcomes import FAIL, NOT_VERIFIED, PASS, Check, worst


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_default)


def _default(o):
    try:
        import numpy as np
        if isinstance(o, np.ndarray):
            return {"__nd__": o.tolist(), "dtype": str(o.dtype)}
        if isinstance(o, np.generic):
            return o.item()
    except ImportError:  # pragma: no cover
        pass
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    return repr(o)


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- digests
def hook_digest(fn: Callable, params: Optional[dict] = None) -> dict:
    """{'digest', 'basis'}. basis 'source' when inspect finds the source, else 'bytecode'. Closure cell
    values are included, so two lambdas from one factory with different captured targets differ."""
    name = getattr(fn, "__qualname__", repr(fn))
    try:
        src = textwrap.dedent(inspect.getsource(fn))
        basis = "source"
    except (OSError, TypeError):
        code = getattr(fn, "__code__", None)
        if code is None:
            raise TypeError(f"cannot digest {fn!r}: no source and no code object")
        src = code.co_code.hex() + canonical([repr(c) for c in code.co_consts])
        basis = "bytecode"
    cells = []
    for c in (getattr(fn, "__closure__", None) or ()):
        try:
            v = c.cell_contents
        except ValueError:
            v = "<empty>"
        cells.append(hook_digest(v)["digest"] if callable(v) else canonical(v))
    # simple-valued globals the hook reads (a module-level target index, a tick) are part of what acted
    glb = {}
    code = getattr(fn, "__code__", None)
    g = getattr(fn, "__globals__", {}) or {}
    for nm in (code.co_names if code is not None else ()):
        v = g.get(nm)
        if isinstance(v, (int, float, str, bool, tuple, frozenset)) or type(v).__name__ == "ndarray":
            glb[nm] = canonical(v)
    payload = canonical({"name": name, "src": src, "closure": cells, "globals": glb, "params": params or {}})
    return {"digest": sha256(payload), "basis": basis}


def seeds_digest(namespace: int, seeds: Iterable[int]) -> str:
    return sha256(canonical({"ns": int(namespace), "seeds": [int(s) for s in seeds]}))


# ----------------------------------------------------------------------------- the record
@dataclasses.dataclass(frozen=True)
class InterventionRecord:
    experiment: str
    arm: str
    kind: str                       # evolve / transfer / census / intervention / plant / control ...
    seed_namespace: int
    seeds_digest: str
    hook_name: str
    hook_digest: str
    hook_basis: str
    params: dict
    plan_path: Optional[str]
    plan_commit: Optional[str]
    code_sha: Optional[str]
    parent: Optional[str] = None
    created_utc: str = ""
    extra: dict = dataclasses.field(default_factory=dict)

    def body(self) -> dict:
        return dataclasses.asdict(self)

    @property
    def record_id(self) -> str:
        return sha256(canonical(self.body()))


def make_record(*, experiment: str, arm: str, kind: str, seed_namespace: int, seeds: Iterable[int],
                hook: Callable, params: Optional[dict] = None, plan_path: Optional[str] = None,
                plan_commit: Optional[str] = None, code_sha: Optional[str] = None, parent: Optional[str] = None,
                extra: Optional[dict] = None, now: Optional[str] = None) -> InterventionRecord:
    hd = hook_digest(hook, params)
    return InterventionRecord(experiment=experiment, arm=arm, kind=kind, seed_namespace=int(seed_namespace),
                              seeds_digest=seeds_digest(seed_namespace, seeds),
                              hook_name=getattr(hook, "__qualname__", repr(hook)), hook_digest=hd["digest"],
                              hook_basis=hd["basis"], params=dict(params or {}), plan_path=plan_path,
                              plan_commit=plan_commit, code_sha=code_sha, parent=parent,
                              created_utc=now or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                              extra=dict(extra or {}))


# ----------------------------------------------------------------------------- git (read-only)
def _git(repo: str, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)


def first_add(repo: str, pathspecs: list, ref: str = "HEAD") -> Optional[str]:
    p = _git(repo, "log", ref, "--diff-filter=A", "--format=%H", "--topo-order", "--reverse", "--", *pathspecs)
    lines = p.stdout.split()
    return lines[0] if p.returncode == 0 and lines else None


def plan_precedes(repo: str, plan_path: str, result_pathspecs: list, ref: str = "HEAD") -> Check:
    """tools/freeze_check.py semantics: PASS iff the plan's first-add commit is a STRICT ancestor of the first
    commit adding any result path, and the plan blob at `ref` equals the blob it was added with."""
    p_add = first_add(repo, [plan_path], ref)
    r_add = first_add(repo, list(result_pathspecs), ref)
    if p_add is None or r_add is None:
        return Check("R3_plan_precedes", NOT_VERIFIED, {"plan_add": p_add, "result_add": r_add})
    strict = p_add != r_add and _git(repo, "merge-base", "--is-ancestor", p_add, r_add).returncode == 0
    b0 = _git(repo, "rev-parse", f"{p_add}:{plan_path}").stdout.strip()
    b1 = _git(repo, "rev-parse", f"{ref}:{plan_path}").stdout.strip()
    ok = strict and b0 == b1
    return Check("R3_plan_precedes", PASS if ok else FAIL,
                 {"plan_add": p_add[:9], "result_add": r_add[:9], "strictly_before": strict, "plan_unchanged": b0 == b1})


def verify_record(rec: InterventionRecord, *, stored_id: Optional[str] = None, hook: Optional[Callable] = None,
                  repo: Optional[str] = None, result_pathspecs: Optional[list] = None) -> dict:
    checks = []
    if stored_id is None:
        checks.append(Check("R1_id", NOT_VERIFIED, "no stored id"))
    else:
        checks.append(Check("R1_id", PASS if stored_id == rec.record_id else FAIL,
                            {"stored": stored_id[:16], "computed": rec.record_id[:16]}))
    if hook is None:
        checks.append(Check("R2_hook_digest", NOT_VERIFIED, "live hook not supplied"))
    else:
        d = hook_digest(hook, rec.params)["digest"]
        checks.append(Check("R2_hook_digest", PASS if d == rec.hook_digest else FAIL,
                            {"recorded": rec.hook_digest[:16], "live": d[:16]}))
    if repo and rec.plan_path and result_pathspecs:
        c = plan_precedes(repo, rec.plan_path, result_pathspecs)
        checks.append(c)
        if rec.plan_commit and c.detail and isinstance(c.detail, dict) and c.detail.get("plan_add"):
            same = rec.plan_commit.startswith(c.detail["plan_add"]) or c.detail["plan_add"].startswith(rec.plan_commit[:9])
            checks.append(Check("R4_plan_commit_link", PASS if same else FAIL,
                                {"recorded": rec.plan_commit[:9], "git_first_add": c.detail["plan_add"]}))
    else:
        checks.append(Check("R3_plan_precedes", NOT_VERIFIED, "no repo/plan/results"))
    checks.append(Check("R5_seed_namespace", PASS if rec.seeds_digest and rec.seed_namespace is not None else FAIL))
    return {"outcome": worst(checks), "checks": [c.as_dict() for c in checks]}


# ----------------------------------------------------------------------------- cross-record checks
def seed_reuse(records: list, independent: Iterable[Iterable[str]]) -> Check:
    """independent: groups of arm names that the analysis treats as independent. Two arms of one group that
    share a seed namespace are a reused RNG stream (their errors are correlated)."""
    by_arm = {r.arm: r for r in records}
    clashes = []
    for g in independent:
        g = list(g)
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                a, b = by_arm.get(g[i]), by_arm.get(g[j])
                if a and b and (a.seed_namespace == b.seed_namespace or a.seeds_digest == b.seeds_digest):
                    clashes.append((g[i], g[j]))
    return Check("seed_reuse", FAIL if clashes else PASS, {"clashes": clashes})


DEFAULT_SUPPORT = {
    "search_null": {"evolve"},        # "search failed to find X" needs a search that ran
    "transfer_null": {"transfer"},    # "champion of A does not transfer to B"
    "physics_ceiling": {"plant", "lightcone", "bound"},
    "census": {"census"},
}


def support_check(claim: str, records: list, policy: Optional[dict] = None) -> Check:
    """records: InterventionRecords or dicts with a 'kind' and an id ('cell_id' or record_id)."""
    allowed = (policy or DEFAULT_SUPPORT).get(claim)
    if allowed is None:
        return Check("support", NOT_VERIFIED, f"no support policy for claim {claim!r}")
    refused, ok = [], []
    for r in records:
        kind = r.kind if isinstance(r, InterventionRecord) else r.get("kind")
        rid = r.record_id[:16] if isinstance(r, InterventionRecord) else r.get("cell_id", r.get("id"))
        (ok if kind in allowed else refused).append({"id": rid, "kind": kind})
    if not records:
        return Check("support", FAIL, {"claim": claim, "why": "no supporting records"})
    return Check("support", FAIL if refused else PASS, {"claim": claim, "admissible": ok, "refused": refused})


# ----------------------------------------------------------------------------- append-only ledger
class Ledger:
    def __init__(self, path):
        self.path = pathlib.Path(path)

    def _ids(self) -> set:
        return {json.loads(l)["record_id"] for l in self.path.read_text().splitlines() if l.strip()} \
            if self.path.exists() else set()

    def append(self, rec: InterventionRecord) -> str:
        rid = rec.record_id
        if rid in self._ids():
            raise ValueError(f"record {rid[:16]} already in ledger (append-only, no overwrite)")
        with self.path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(canonical({"record_id": rid, "body": rec.body()}) + "\n")
        return rid

    def verify(self) -> Check:
        bad = []
        n = 0
        if self.path.exists():
            for i, l in enumerate(self.path.read_text().splitlines()):
                if not l.strip():
                    continue
                n += 1
                row = json.loads(l)
                if sha256(canonical(row["body"])) != row["record_id"]:
                    bad.append(i)
        return Check("ledger_integrity", FAIL if bad else (PASS if n else NOT_VERIFIED), {"rows": n, "tampered": bad})
