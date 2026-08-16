"""grading_oracle.py — Harmonia's "are we closer?" instrument, as a callable + bus service.

The TDD-layer reframing (REASSESSMENT v3) makes Prometheus a progress meter for
building a reasoner. That needs ONE trustworthy, non-gameable grade of "is a
candidate reasoner getting better?" Harmonia owns it: the testable reasoning ladder
(`reasoning_phase0`, procedural probes) + the independent verifier (`verifier_lens`,
z3/sympy, fails closed). This module wraps them so any agent (Hephaestus's organism
loop, Apollo, Icarus) can grade a candidate and get back a tier staircase + the
failure SHAPES that say what to try next.

NON-GAMEABLE by construction: a candidate reasoner only ever supplies an ANSWER (and
an optional process trace). Correctness is decided server-side against the probe's
ground truth (`_ans_correct`) and, where the kind is dispatchable, re-certified by the
independent `verifier_lens.verify` (which recomputes from the probe, ignoring the
candidate's self-report). The candidate cannot see ground truth and cannot grade
itself. (Reassessment Q1 "are we there yet" + Q3 "what next".)

A candidate reasoner is a callable `reasoner(probe) -> (answer, trace_dict)` — the
interface `reasoning_phase0`'s baselines already use, and the one Hephaestus's engines
adapt to.

Usage:
  # local (same machine as the reasoner)
  from harmonia.services.grading_oracle import grade_reasoner
  report = grade_reasoner(my_reasoner)                 # callable
  report = grade_reasoner("harmonia.experiments.reasoning_phase0:reasoner_careful")

  # cross-machine over the bus
  python -m harmonia.services.grading_oracle --serve              # on the reasoner's host
  from harmonia.services.grading_oracle import request_grade
  report = request_grade("agents.hephaestus.src.engines:composed_reasoner")

  # CLI one-shot
  python -m harmonia.services.grading_oracle --grade <module:func> [--tiers R0,R2] [--seed N]
"""
from __future__ import annotations

import argparse
import importlib
import json
import random
import time
from collections import Counter, defaultdict
from typing import Any, Callable, Dict, List, Optional

from harmonia.experiments.reasoning_phase0 import (
    gen_R0, gen_R1, gen_R2, gen_R3, gen_R5, gen_R6, gen_R7, gen_R8,
    grade, SEED, TRACE_FIELDS,
)

try:
    from harmonia.experiments.verifier_lens import verify as _verify
except Exception:  # verifier is a stronger cross-check; absence must not break grading
    _verify = None

ORACLE_VERSION = "grading_oracle@v1"

# Core tier generators. (No R4 generator exists in reasoning_phase0 — tiers are the
# orthogonal axes the ladder actually tests; R4 is intentionally absent.)
TIER_GENS: Dict[str, Callable] = {
    "R0": gen_R0, "R1": gen_R1, "R2": gen_R2, "R3": gen_R3,
    "R5": gen_R5, "R6": gen_R6, "R7": gen_R7, "R8": gen_R8,
}
ALL_TIERS = list(TIER_GENS)

REQ_STREAM = "harmonia:oracle:requests"
RES_STREAM = "harmonia:oracle:results"


# ---------------------------------------------------------------------------
# Core: grade a candidate reasoner
# ---------------------------------------------------------------------------
def _resolve(reasoner) -> tuple[Callable, str]:
    """Accept a callable or a 'module:func' reference; return (callable, name)."""
    if callable(reasoner):
        return reasoner, getattr(reasoner, "__qualname__", repr(reasoner))
    if isinstance(reasoner, str) and ":" in reasoner:
        mod, fn = reasoner.split(":", 1)
        obj = getattr(importlib.import_module(mod), fn)
        return obj, reasoner
    raise ValueError(f"reasoner must be callable or 'module:func', got {reasoner!r}")


def grade_reasoner(reasoner, tiers: Optional[List[str]] = None,
                   seed: int = SEED, emit_path=None) -> Dict[str, Any]:
    """Grade a candidate reasoner across the testable ladder. Deterministic for a
    given (reasoner, tiers, seed). Returns the tier staircase + failure shapes.

    `emit_path` (opt-in, default None -> byte-identical prior behaviour): when set, the
    PER-ITEM score VECTOR from the two independent evaluators — ground-truth `grade` and the
    independent `verifier_lens.verify` recompute — is persisted BEFORE it is collapsed into
    the aggregate counters, via `prometheus_math.reasoning_quality_emit`. This is the site the
    emit primitive was forged for on 2026-06-09 and could not reach: the substrate combined
    head scores and kept only the scalar (`feedback_no_naive_score_combination`).

    Off by default deliberately. Turning it on writes a file as a side effect of grading, and
    this oracle is load-bearing for a pre-registered probe at co-sign; that call belongs to
    this file's owner, not to the toolsmith who wired the seam. Emission failure can never
    affect a grade — the write is guarded and dropped silently.

    Expected yield, stated so nobody reads an empty stream as a bug: this evaluator pair
    agreed 157/157 at calibration, and the H-R1 relational instrument feeds on DISAGREEMENT.
    A near-empty contested pool is the honest prediction, not a defect.
    """
    fn, name = _resolve(reasoner)
    tiers = tiers or ALL_TIERS
    out_tiers: Dict[str, Any] = {}
    _emit_records: List[Any] = []
    _make_record = None
    if emit_path is not None:
        try:
            from prometheus_math.reasoning_quality_emit import make_record as _make_record
        except Exception:                              # never let the seam break the grade
            _make_record = None

    for tier in tiers:
        gen = TIER_GENS[tier]
        probes = gen(random.Random(seed))           # fresh RNG per tier -> reproducible
        per_version_correct: Dict[str, List[int]] = defaultdict(list)
        kill_patterns: Counter = Counter()
        n = n_correct = n_verified = n_verifiable = 0

        for p in probes:
            n += 1
            try:
                ans, tr = fn(p)
            except Exception as exc:                  # a crashing reasoner FAILS the probe
                ans, tr = None, {"error": f"{type(exc).__name__}: {exc}"}
            # Independent correctness vs ground truth (non-gameable; candidate never sees GT).
            tvec, correct = grade(p, ans, tr)
            n_correct += int(bool(correct))
            per_version_correct[p.version].append(int(bool(correct)))
            if not correct and tvec.get("_kill_pattern"):
                kill_patterns[tvec["_kill_pattern"]] += 1
            # Stronger independent re-certification where the verifier dispatches this kind.
            _verifier_score = None
            if _verify is not None:
                vres = _verify(p, ans)
                if vres.get("valid") is not None:     # dispatchable + decidable
                    n_verifiable += 1
                    n_verified += int(bool(vres["valid"]))
                    _verifier_score = float(bool(vres["valid"]))
                    if not vres["valid"] and vres.get("kill_pattern"):
                        kill_patterns[f"verify:{vres['kill_pattern']}"] += 1

            # Emit the per-item VECTOR before it is collapsed (opt-in; see docstring).
            if _make_record is not None and _verifier_score is not None:
                try:
                    _emit_records.append(_make_record(
                        candidate_id=f"{name}:{tier}:{n}",
                        task_id=f"{tier}:{getattr(p, 'version', '?')}:{n}",
                        evaluator_scores={"ground_truth": float(bool(correct)),
                                          "verifier_lens": _verifier_score},
                        outcome="correct" if correct else "incorrect",
                        scorer_versions={"oracle": ORACLE_VERSION},
                    ))
                except Exception:
                    pass                               # a grade is never affected by the seam

        out_tiers[tier] = {
            "n": n,
            "n_correct": n_correct,
            "pass_rate": round(n_correct / n, 4) if n else None,
            "by_version": {
                v: {"n": len(c), "pass_rate": round(sum(c) / len(c), 4)}
                for v, c in sorted(per_version_correct.items())
            },
            "independently_verified": {
                "n_verifiable": n_verifiable,
                "n_verified": n_verified,
                "verified_rate": round(n_verified / n_verifiable, 4) if n_verifiable else None,
            },
            "dominant_kill_patterns": kill_patterns.most_common(5),
        }

    if emit_path is not None and _emit_records:
        try:
            from prometheus_math.reasoning_quality_emit import append_records, mark_contested
            append_records(emit_path, mark_contested(_emit_records))
        except Exception:
            pass                                       # a grade is never affected by the seam

    staircase = {t: out_tiers[t]["pass_rate"] for t in tiers}
    tot_n = sum(out_tiers[t]["n"] for t in tiers)
    tot_c = sum(out_tiers[t]["n_correct"] for t in tiers)
    return {
        "oracle_version": ORACLE_VERSION,
        "reasoner": name,
        "seed": seed,
        "tiers_graded": tiers,
        "staircase": staircase,                       # the "are we there yet" signal
        "overall_pass_rate": round(tot_c / tot_n, 4) if tot_n else None,
        "per_tier": out_tiers,                         # detail + "what next" kill shapes
    }


def staircase_str(report: Dict[str, Any]) -> str:
    s = report["staircase"]
    return "  ".join(f"{t}:{(v*100):.0f}%" if v is not None else f"{t}:-" for t, v in s.items())


# ---------------------------------------------------------------------------
# Bus service (cross-machine): grade a NAMED reasoner ('module:func'), no probe
# serialization needed — reasoners are shared code, graded on whichever host imports them.
# ---------------------------------------------------------------------------
def request_grade(reasoner_ref: str, tiers: Optional[List[str]] = None,
                  seed: int = SEED, timeout_s: float = 120.0) -> Optional[Dict[str, Any]]:
    """Post a grade request to the bus and wait for the result. Returns None on timeout."""
    from thesauros.prometheus_data import get_bus
    r = get_bus(decode_responses=True)
    req_id = f"{int(time.time()*1000)}-{random.randint(1000,9999)}"
    r.xadd(REQ_STREAM, {"req_id": req_id, "reasoner_ref": reasoner_ref,
                        "tiers": ",".join(tiers) if tiers else "", "seed": str(seed)})
    deadline = time.time() + timeout_s
    last = "0"
    while time.time() < deadline:
        for eid, fields in r.xrange(RES_STREAM, min=last):
            last = f"{eid}-x"
            if fields.get("req_id") == req_id:
                return json.loads(fields["report"])
        time.sleep(1.0)
    return None


def serve(poll_s: float = 2.0, once: bool = False) -> None:
    """Daemon: grade named reasoners requested over the bus. Run on a host that can
    import the candidate reasoners (e.g. M3 for Hephaestus engines)."""
    from thesauros.prometheus_data import get_bus
    r = get_bus(decode_responses=True)
    last = "$"  # only new requests
    print(f"[oracle] serving on {REQ_STREAM} -> {RES_STREAM} ({ORACLE_VERSION})", flush=True)
    while True:
        for eid, f in r.xrange(RES_STREAM, min="+", max="+"):  # noop; keeps API symmetric
            pass
        msgs = r.xrange(REQ_STREAM, min=last) if last != "$" else []
        if last == "$":
            # initialize cursor to current tail
            tail = r.xrevrange(REQ_STREAM, count=1)
            last = f"{tail[0][0]}-x" if tail else "0"
        for eid, fields in msgs:
            last = f"{eid}-x"
            ref = fields.get("reasoner_ref")
            if not ref:
                continue
            tiers = [t for t in fields.get("tiers", "").split(",") if t] or None
            seed = int(fields.get("seed") or SEED)
            try:
                report = grade_reasoner(ref, tiers=tiers, seed=seed)
                payload = json.dumps(report)
                print(f"[oracle] graded {ref}: {staircase_str(report)}", flush=True)
            except Exception as exc:
                payload = json.dumps({"error": f"{type(exc).__name__}: {exc}", "reasoner": ref})
                print(f"[oracle] FAILED {ref}: {exc}", flush=True)
            r.xadd(RES_STREAM, {"req_id": fields.get("req_id", ""), "report": payload})
        if once:
            return
        time.sleep(poll_s)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Harmonia grading oracle")
    ap.add_argument("--grade", metavar="module:func", help="grade a named reasoner locally")
    ap.add_argument("--tiers", help="comma list e.g. R0,R2,R6 (default all)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--serve", action="store_true", help="run the bus grading daemon")
    args = ap.parse_args()
    tiers = [t for t in args.tiers.split(",")] if args.tiers else None
    if args.serve:
        serve()
    elif args.grade:
        rep = grade_reasoner(args.grade, tiers=tiers, seed=args.seed)
        print(staircase_str(rep))
        print(json.dumps(rep, indent=1))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
