"""Resumable, rate-limit-aware runner for the model-zoo basis matrix (EXPERIMENTAL).

This is the harness that attacks the SINGLE named blocker in
`model_zoo_plan_2026-05-29.md` §5: a full zoo run is (≈18 examinees) ×
(tiers × versions × N) ≈ thousands of calls, and the blocker is throughput /
pacing / not-losing-work-to-a-429-storm, NOT reachability. Everything here is
the local scheduler that makes that run launchable and survivable; it adds NO
new model logic (it reuses `make_zoo_reasoner` / `make_opus_reasoner` and the
harness `grade`).

What it adds over `run_model_comparison.py`:
  * **Resumable checkpoint** — every graded cell is appended to a JSONL as it
    completes; on restart, done (examinee, probe_id) cells are skipped. A 429
    storm or a crash costs at most the one in-flight call.
  * **Per-provider pacing** — a ProviderPacer enforces a min-interval AND a
    sliding-window RPM cap per provider, and examinees are interleaved
    round-robin so consecutive calls hit DIFFERENT providers (Groq/GitHub/Gemini
    free tiers 429 under burst; NVIDIA/OpenAI tolerate spaced calls).
  * **Bounded single re-ask** — on a *genuine JSON parse* failure (class 3 only,
    not transport/content), one retry with a "return ONLY the JSON" suffix.
  * **Per-examinee parse-rate gate** — track genuine-parse-fail rate; flag (and
    optionally drop) any examinee above the threshold, because >~40% parse loss
    can't be scored fairly and pollutes the factor analysis.
  * **Cold-start warm-up** — a throwaway long-timeout ping for cold-start-prone
    providers (NVIDIA NIM) before their first scored probe.

DEPENDENCY INJECTION FOR TESTING: ProviderPacer takes now()/sleep(); run_matrix
takes a reasoner factory and a grader. `test_zoo_matrix.py` injects fakes to
exercise pacing, resume, the gate, and the error taxonomy with NO network and NO
real sleeps. The default factory dispatches Anthropic→structured, else→zoo.

SECURITY: never reads key files, never prints key values — credentials flow
through the same `make_zoo_reasoner` / `make_opus_reasoner` paths as elsewhere.

Usage:
    python harmonia/experiments/run_zoo_matrix.py --dry-run        # offline mock, no network
    python harmonia/experiments/run_zoo_matrix.py --n 3            # LIVE zoo run, 3/version
    python harmonia/experiments/run_zoo_matrix.py --n 3 --with-anchors --drop-degraded
    # resume is automatic: re-running with the same --ckpt skips completed cells
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter, deque
from pathlib import Path
from typing import Callable, Optional

_EXP = Path(__file__).resolve().parent
if str(_EXP) not in sys.path:
    sys.path.insert(0, str(_EXP))

from reasoning_phase0 import (  # noqa: E402
    gen_R0, gen_R1, gen_R2, gen_R3, gen_R5, gen_R6, gen_R7, gen_R8,
    gen_sqrt_label, gen_rational_extra, gen_abs_extra, gen_log_extra, grade,
)

# ----------------------------------------------------------------- error taxonomy
# Mirrors model_zoo_plan §2 / zoo_reasoner's three-class taxonomy. Only "parse"
# measures the free-text-vs-structured loss the synthesis cares about; "transport"
# is rate-limit / network noise and must NOT be counted as a reasoning failure.
_TRANSPORT_PFX = ("http_error", "call_exception", "no_key", "unknown_provider",
                  "api_error")   # api_error* = Anthropic-path transient
_CONTENT = {"no_choices", "empty_content"}
_PARSE_PFX = ("empty_response", "no_json_object", "json_decode_error",
              "unbalanced_braces")


def err_class(parse_error: Optional[str]) -> str:
    """Classify a trace _parse_error tag into ok|transport|content|parse|other."""
    if not parse_error:
        return "ok"
    for pfx in _TRANSPORT_PFX:
        if parse_error.startswith(pfx):
            return "transport"
    if parse_error in _CONTENT:
        return "content"
    for pfx in _PARSE_PFX:
        if parse_error.startswith(pfx):
            return "parse"
    return "other"


# ----------------------------------------------------------------- pacing
class ProviderPacer:
    """Per-provider min-interval + sliding-window RPM throttle.

    Single-threaded and blocking: `wait(provider)` sleeps exactly long enough to
    honor both the min-interval since this provider's last call and the per-minute
    cap, then records the call. now()/sleep() are injectable so tests run with a
    fake clock and zero real delay.
    """

    def __init__(self, limits: dict, now: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep):
        self._limits = limits
        self._now = now
        self._sleep = sleep
        self._next_allowed: dict[str, float] = {}
        self._window: dict[str, deque] = {}

    def wait(self, provider: str) -> None:
        lim = self._limits.get(provider, self._limits.get("_default", {}))
        # 1) min-interval since last call to this provider
        t = self._now()
        na = self._next_allowed.get(provider, 0.0)
        if t < na:
            self._sleep(na - t)
            t = self._now()
        # 2) sliding-window RPM cap
        rpm = lim.get("rpm")
        if rpm:
            dq = self._window.setdefault(provider, deque())
            while dq and dq[0] <= t - 60.0:
                dq.popleft()
            if len(dq) >= rpm:
                wait_s = dq[0] + 60.0 - t
                if wait_s > 0:
                    self._sleep(wait_s)
                    t = self._now()
                while dq and dq[0] <= t - 60.0:
                    dq.popleft()
            dq.append(t)
        self._next_allowed[provider] = t + lim.get("min_interval", 0.0)


# Conservative defaults from the §1 inventory: Groq free tier 429s under burst;
# GitHub Models / Gemini are near-zero throughput; NVIDIA/OpenAI tolerate spaced
# calls. Tune from observed 429s — pacing is a living instrument, not a constant.
DEFAULT_LIMITS = {
    "Groq":         {"min_interval": 2.0, "rpm": 25},
    "Cerebras":     {"min_interval": 1.0, "rpm": 40},
    "NVIDIA":       {"min_interval": 1.0, "rpm": 40},
    "OpenAI":       {"min_interval": 0.5, "rpm": 60},
    "GitHubModels": {"min_interval": 6.0, "rpm": 8},
    "Gemini":       {"min_interval": 6.0, "rpm": 8},
    "Anthropic":    {"min_interval": 0.3, "rpm": 50},
    "_default":     {"min_interval": 1.0, "rpm": 30},
}
WARMUP_PROVIDERS = {"NVIDIA"}   # cold-start-prone (§5)


# ----------------------------------------------------------------- checkpoint
class Checkpoint:
    """Append-only JSONL of completed cells; resumable done-set keyed by
    (examinee, probe_id). flush() after each write so a kill loses nothing."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.done: set[tuple[str, str]] = set()
        self.records: list[dict] = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue   # tolerate a half-written final line from a kill
                # HARMA-P18 (fixed P44): a well-formed line missing its keys was
                # FATAL while a truncated line was tolerated — inverted robustness.
                # Same contract both ways: skip and count, never die on load.
                if not isinstance(rec, dict) or "examinee" not in rec or "probe_id" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue
                self.records.append(rec)
                self.done.add((rec["examinee"], rec["probe_id"]))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a", encoding="utf-8")

    def is_done(self, examinee: str, probe_id: str) -> bool:
        return (examinee, probe_id) in self.done

    def record(self, rec: dict) -> None:
        self._fh.write(json.dumps(rec) + "\n")
        self._fh.flush()
        self.records.append(rec)
        self.done.add((rec["examinee"], rec["probe_id"]))

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:
            pass


# ----------------------------------------------------------------- examinee panel
# Reachable-today panel from model_zoo_plan §4.1 (zoo via free-text JSON). Anthropic
# anchors are added only with --with-anchors (saturated top; costs Anthropic budget).
ZOO_PANEL = [
    # (provider, model, size_tier)
    ("Groq",     "llama-3.1-8b-instant",                       "open-small"),
    ("NVIDIA",   "meta/llama-3.1-8b-instruct",                 "open-small"),
    ("NVIDIA",   "meta/llama-3.2-3b-instruct",                 "open-small"),
    ("NVIDIA",   "mistralai/mistral-7b-instruct-v0.3",         "open-small"),
    ("Groq",     "openai/gpt-oss-20b",                         "open-small"),
    ("Groq",     "qwen/qwen3-32b",                             "mid"),
    ("Groq",     "meta-llama/llama-4-scout-17b-16e-instruct",  "mid"),
    ("NVIDIA",   "nvidia/llama-3.3-nemotron-super-49b-v1.5",   "mid"),
    ("NVIDIA",   "meta/llama-3.3-70b-instruct",                "mid"),
    ("NVIDIA",   "qwen/qwen3-next-80b-a3b-instruct",           "mid"),
    ("NVIDIA",   "nvidia/nemotron-3-super-120b-a12b",          "mid"),
    ("Cerebras", "gpt-oss-120b",                               "mid"),
    ("Cerebras", "zai-glm-4.7",                                "mid"),
    ("OpenAI",   "gpt-4.1-mini",                               "mid"),
    ("OpenAI",   "gpt-4.1-nano",                               "open-small"),
    ("OpenAI",   "gpt-4o",                                     "frontier"),
]
ANTHROPIC_ANCHORS = [
    ("Anthropic", "claude-opus-4-8",   "frontier"),
    ("Anthropic", "claude-sonnet-4-6", "frontier"),
    ("Anthropic", "claude-haiku-4-5",  "frontier"),
]


def examinee_key(provider: str, model: str) -> str:
    return f"{provider}:{model}"


# ----------------------------------------------------------------- probe sampling
GENS = {"R0": gen_R0, "R1": gen_R1, "R2": gen_R2, "R3": gen_R3, "R5": gen_R5,
        "R6": gen_R6, "R7": gen_R7, "R8": gen_R8,
        "CF": gen_sqrt_label, "RE": gen_rational_extra,
        "AE": gen_abs_extra, "LE": gen_log_extra}
VERSIONS = ("clean", "iso", "adversarial", "transfer")


def sample_probes(rng, n_per: int):
    """Same probes for every examinee (apples-to-apples). Each carries a stable
    probe_id = enumeration index + tier/version, so the checkpoint can resume."""
    probes = []
    for t, g in GENS.items():
        allp = g(rng)
        for v in VERSIONS:
            pv = [p for p in allp if p.version == v]
            rng.shuffle(pv)
            probes.extend(pv[:n_per])
    indexed = []
    for i, p in enumerate(probes):
        indexed.append((f"{i:04d}:{p.tier}:{p.version}", p))
    return indexed


# ----------------------------------------------------------------- default factory
def default_reasoner_factory(provider: str, model: str, call_log: list,
                             prompt_suffix: Optional[str] = None):
    """Dispatch: Anthropic anchors → structured outputs; everything else → the
    free-text zoo adapter pinned to one model on one provider (no fallback)."""
    if provider == "Anthropic":
        from reasoners_llm import make_opus_reasoner
        return make_opus_reasoner(model=model, call_log=call_log)
    from zoo_reasoner import make_zoo_reasoner
    timeout = 120 if provider in WARMUP_PROVIDERS else 90
    return make_zoo_reasoner(model, provider, call_log=call_log, timeout=timeout,
                             prompt_suffix=prompt_suffix)


_REASK_SUFFIX = ("Return ONLY the JSON object that matches the contract above. "
                 "No prose, no markdown fences, no explanation.")


# ----------------------------------------------------------------- the run
def run_matrix(examinees, probes, ckpt: Checkpoint, pacer: ProviderPacer,
               factory: Callable = default_reasoner_factory,
               grader: Callable = grade,
               gate_min_attempts: int = 8, gate_parse_thresh: float = 0.40,
               drop_degraded: bool = False, reask: bool = True,
               warmup: bool = True, log: Callable[[str], None] = print) -> dict:
    """Run every (examinee × probe) cell not already in the checkpoint.

    Returns a summary dict. Side effect: appends one record per graded cell to
    `ckpt`. Examinees are processed with their probes interleaved round-robin by
    provider via the pacer, so no single provider is bursted.
    """
    # Build per-examinee state.
    state = {}
    for provider, model, size in examinees:
        ek = examinee_key(provider, model)
        state[ek] = {"provider": provider, "model": model, "size": size,
                     "call_log": [], "attempts": 0, "parse_fail": 0,
                     "degraded": False, "warmed": False}

    # Round-robin work queue: list of (examinee, probe_id, probe), grouped so we
    # rotate examinees (hence providers) rather than draining one at a time.
    queue: list[tuple] = []
    by_ex = {examinee_key(p_, m_): [] for (p_, m_, _s) in examinees}
    for (provider, model, size) in examinees:
        ek = examinee_key(provider, model)
        for pid, probe in probes:
            if ckpt.is_done(ek, pid):
                continue
            by_ex[ek].append((ek, pid, probe))
    # interleave
    idx = 0
    drained = False
    while not drained:
        drained = True
        for ek in by_ex:
            if idx < len(by_ex[ek]):
                queue.append(by_ex[ek][idx])
                drained = False
        idx += 1

    skipped_done = sum(1 for (provider, model, _s) in examinees
                       for pid, _p in probes
                       if ckpt.is_done(examinee_key(provider, model), pid))
    log(f"[zoo-matrix] examinees={len(examinees)} probes/examinee={len(probes)} "
        f"queued={len(queue)} resumed(skipped)={skipped_done}")

    done_count = 0
    for (ek, pid, probe) in queue:
        st = state[ek]
        provider, model = st["provider"], st["model"]

        # Drop-degraded short-circuit: stop spending on a hopeless examinee.
        if st["degraded"] and drop_degraded:
            ckpt.record({"examinee": ek, "probe_id": pid, "tier": probe.tier,
                         "version": probe.version, "kind": probe.kind,
                         "ok": None, "err_class": "skipped_degraded",
                         "parse_error": "skipped_degraded", "kill_pattern": None,
                         "provider": provider, "model": model, "size": st["size"]})
            continue

        # Cold-start warm-up: one throwaway long-timeout ping before first scored probe.
        if warmup and not st["warmed"] and provider in WARMUP_PROVIDERS:
            st["warmed"] = True
            try:
                pacer.wait(provider)
                warm = factory(provider, model, [], None)
                warm(probe)   # result ignored; just to spin up the NIM cold start
            except Exception:
                pass

        # First attempt.
        pacer.wait(provider)
        reasoner = factory(provider, model, st["call_log"], None)
        ans, tr = reasoner(probe)
        cls = err_class(tr.get("_parse_error"))

        # Bounded single re-ask on a GENUINE parse failure only.
        if reask and cls == "parse":
            pacer.wait(provider)
            reasoner2 = factory(provider, model, st["call_log"], _REASK_SUFFIX)
            ans2, tr2 = reasoner2(probe)
            cls2 = err_class(tr2.get("_parse_error"))
            if cls2 != "parse":          # re-ask recovered (or hit a different class)
                ans, tr, cls = ans2, tr2, cls2

        v, ok_raw = grader(probe, ans, tr)
        # Only a CLEAN parse yields a scoreable answer. Transport (429/timeout),
        # content-empty, and genuine-parse cells are recorded for their covariate
        # columns but excluded from accuracy (ok=None) — same discipline as the
        # established runners, which never fold api-failures into accuracy.
        ok = ok_raw if cls == "ok" else None
        st["attempts"] += 1
        if cls == "parse":
            st["parse_fail"] += 1
        # Parse-rate gate (only count genuine parse failures; transport excluded).
        if (st["attempts"] >= gate_min_attempts
                and st["parse_fail"] / st["attempts"] > gate_parse_thresh
                and not st["degraded"]):
            st["degraded"] = True
            log(f"[zoo-matrix] DEGRADED {ek}: parse-fail "
                f"{st['parse_fail']}/{st['attempts']} > {gate_parse_thresh:.0%}"
                + (" — dropping remaining cells" if drop_degraded else ""))

        ckpt.record({"examinee": ek, "probe_id": pid, "tier": probe.tier,
                     "version": probe.version, "kind": probe.kind,
                     "ok": (None if ok is None else bool(ok)), "err_class": cls,
                     "parse_error": tr.get("_parse_error"),
                     "kill_pattern": v.get("_kill_pattern"),
                     "provider": provider, "model": model, "size": st["size"]})
        done_count += 1
        if done_count % 25 == 0:
            log(f"[zoo-matrix] {done_count}/{len(queue)} cells")

    return summarize(ckpt, examinees, probes, state)


# ----------------------------------------------------------------- summary
def summarize(ckpt: Checkpoint, examinees, probes, state) -> dict:
    tiers = list(GENS)
    recs = ckpt.records
    by_ek = {}
    for r in recs:
        by_ek.setdefault(r["examinee"], []).append(r)
    matrix = {}
    for (provider, model, size) in examinees:
        ek = examinee_key(provider, model)
        rs = by_ek.get(ek, [])
        scored = [r for r in rs if r.get("ok") is not None]
        cell = {}
        for t in tiers:
            tr_ok = [r["ok"] for r in scored if r["tier"] == t]
            cell[t] = (sum(tr_ok) / len(tr_ok)) if tr_ok else None
        pf = sum(1 for r in rs if r.get("err_class") == "parse")
        tot = sum(1 for r in rs if r.get("err_class") in ("ok", "parse", "content", "other"))
        matrix[ek] = {
            "size": size,
            "acc_by_tier": cell,
            "n_scored": len(scored),
            "parse_fail_rate": (pf / tot) if tot else None,
            "transport_fails": sum(1 for r in rs if r.get("err_class") == "transport"),
            "degraded": state[ek]["degraded"] if ek in state else None,
            "plateau": next((t for t in tiers
                             if cell.get(t) is not None and cell[t] < 0.5), None),
        }
    return {"matrix": matrix, "n_cells": len(recs), "tiers": tiers}


def print_summary(summary: dict, log: Callable[[str], None] = print) -> None:
    tiers = summary["tiers"]
    log("\n==================== ZOO MATRIX (examinee x tier accuracy) ====================")
    log(f"{'examinee':46s}{'sz':11s} " + " ".join(f"{t:>4s}" for t in tiers)
        + "  parseF plateau")
    for ek, m in summary["matrix"].items():
        accs = " ".join(
            (f"{m['acc_by_tier'][t]:4.2f}" if m['acc_by_tier'].get(t) is not None else "  - ")
            for t in tiers)
        pf = f"{m['parse_fail_rate']:.0%}" if m['parse_fail_rate'] is not None else "  - "
        deg = "*DEG" if m.get("degraded") else ""
        log(f"{ek:46.46s}{m['size']:11s} {accs}  {pf:>5s} {str(m['plateau']):>5s}{deg}")
    log(f"\n[zoo-matrix] total graded cells: {summary['n_cells']}")
    log("READ: read each row left-to-right; first tier <0.50 is that examinee's plateau. "
        "The basis question is whether plateau ORDER differs across rows (multi-axis) "
        "or every row plateaus in the same order (rank-1 ladder). parseF flags rows "
        "whose comparison is degraded by free-text JSON loss (a control covariate, not a skill).")


# ----------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3, help="probes per version per tier")
    ap.add_argument("--ckpt", default=str(_EXP / "zoo_matrix_ckpt.jsonl"))
    ap.add_argument("--with-anchors", action="store_true",
                    help="include Anthropic frontier anchors (costs Anthropic budget)")
    ap.add_argument("--drop-degraded", action="store_true",
                    help="stop spending on examinees above the parse-fail gate")
    ap.add_argument("--seed", type=int, default=20260529)
    ap.add_argument("--dry-run", action="store_true",
                    help="offline: deterministic mock reasoner, no network, no sleeps")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    probes = sample_probes(rng, args.n)
    examinees = list(ZOO_PANEL)
    if args.with_anchors:
        examinees += ANTHROPIC_ANCHORS

    if args.dry_run:
        # Offline smoke of the SCHEDULER (pacing/resume/gate), no API.
        examinees = examinees[:4]
        pacer = ProviderPacer(DEFAULT_LIMITS, now=lambda: 0.0, sleep=lambda s: None)
        factory = _make_mock_factory()
        ckpt = Checkpoint(args.ckpt)
        summary = run_matrix(examinees, probes, ckpt, pacer, factory=factory,
                             grader=_mock_grader,
                             gate_min_attempts=8, drop_degraded=args.drop_degraded)
        ckpt.close()
        print_summary(summary)
        print("[dry-run] scheduler exercised offline (no network). "
              "Delete the ckpt to re-run from scratch.")
        return

    pacer = ProviderPacer(DEFAULT_LIMITS)
    ckpt = Checkpoint(args.ckpt)
    print(f"[zoo-matrix] LIVE run | seed={args.seed} | ckpt={args.ckpt}")
    try:
        summary = run_matrix(examinees, probes, ckpt, pacer,
                             drop_degraded=args.drop_degraded)
    finally:
        ckpt.close()
    print_summary(summary)
    out = _EXP / "zoo_matrix_summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[zoo-matrix] wrote {out}")


def _mock_grader(probe, ans, tr):
    """Offline grader for --dry-run/tests: reads the mock's _mock_ok sentinel.
    Returns (trace_vector_like, ok) matching the real grade() contract shape."""
    ok = bool(tr.get("_mock_ok"))
    return {"_kill_pattern": None if ok else f"mock_fail_{probe.tier}"}, ok


def _make_mock_factory():
    """Deterministic offline reasoner factory for --dry-run / tests.

    Behavior is a pure function of (provider, model, probe.tier) so the matrix is
    reproducible: frontier-ish models pass low tiers; one model is forced to emit
    genuine parse failures so the gate path is exercised."""
    def factory(provider, model, call_log, prompt_suffix=None):
        def reasoner(probe):
            # 'mistral-7b' stands in for a weak model that buries JSON → parse fails,
            # UNLESS the re-ask suffix is present (then it complies) — exercises re-ask.
            if "mistral-7b" in model and prompt_suffix is None:
                return None, {"_parse_error": "no_json_object", "_provider": f"{provider}:{model}"}
            # crude tier ceiling by name so rows differ
            ceiling = {"open-small": 1, "mid": 2}.get("", 2)
            tier_rank = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R5": 4, "R6": 5,
                         "R7": 6, "R8": 7, "CF": 1, "RE": 2, "AE": 2, "LE": 2}
            ok = tier_rank.get(probe.tier, 9) <= (3 if "70b" in model or "120b" in model
                                                  or "gpt-4o" in model else 1)
            # produce a trace that grade() will read; we bypass real grading in tests,
            # but for the offline CLI smoke we hand back a minimal trace + a sentinel.
            return (["__mock_ok__"] if ok else ["__mock_no__"],
                    {"_parse_error": None, "_provider": f"{provider}:{model}",
                     "_mock_ok": ok})
        return reasoner
    return factory


if __name__ == "__main__":
    main()
