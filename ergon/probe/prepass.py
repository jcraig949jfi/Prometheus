"""The pre-pass and difficulty leveling (prereg §3, §4.2). STEP 2 of the execution order.

One cold pass, three uses (review C1, adjudicated 2026-08-15):

  1. **Difficulty leveling** (R4)  — cold F0 accuracy must land in [0.35, 0.60] on the
     strongest solver; outside it, re-level or HEADROOM-FAILURE. Symmetric, never a silent
     proceed.
  2. **Contamination screen** (R13) — an item every solver answers correctly on BOTH reps is
     CONTAMINATED-OR-TRIVIAL and is stratified out of the primary analysis.
  3. **D0/D1 residue**            — rep-1 records ONLY are packet-eligible, enforced
     mechanically at write, at load, and again at assembly.

The firewall that matters here: **no gold label, no correctness flag, and no grader output may
enter a residue record.** Correctness exists only in the screen file, which is stamped
`derives_from_gold: true` and is structurally ineligible for packet assembly. The residue
ledger is written, closed, and hashed before anything reads it.

    python -m ergon.probe.prepass level --solver nvidia:deepseek-v4-flash --sample 28
    python -m ergon.probe.prepass run   --solver nvidia:deepseek-v4-flash --level L2 --per-class 60
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import socket
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .extract import extract_verdict
from .solver import EXECUTOR, VERIFIED_SOLVERS, call, preflight
from .task_gen import LEVELS, generate, generator_sha256, manifest_sha256

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "ergon" / "probe" / "ledgers"
MANIFEST_DIR = ROOT / "ergon" / "probe" / "manifests"

#: prereg §3 — the leveling band, on the STRONGEST available solver.
BAND = (0.35, 0.60)
#: prereg §3 / R13 — minimum post-stratification N for the Tier-B manifest.
POWER_FLOOR_N = 300
WORKERS = 6
#: Dispatch pacing. The 2026-08-13 ladder measured this lane clean to 40 RPM with the cliff at
#: 60; the first pre-pass attempt used an UNPACED thread pool (~64 RPM effective) and took
#: HTTP429 on 216 of 252 calls. That ledger was discarded whole per R11 — never partially
#: averaged — and this is the fix: fixed-interval dispatch at 30 RPM, the rate the 15-minute
#: soak sustained at 449/450.
RATE_RPM = 30.0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _attempt(solver: str, row: dict, rep: int, max_tokens: int = 512) -> dict:
    """One cold attempt. Carries NO gold and NO correctness — that is the point."""
    r = call(solver, row["prompt"], max_tokens=max_tokens)
    ex = extract_verdict(r.text if r.status == "ok" else None)
    return {
        "uid": row["uid"], "domain": row["domain"], "level": row["level"],
        "rep": rep, "solver": solver,
        "status": r.status, "latency_s": r.latency_s,
        "prompt_tokens": r.prompt_tokens, "completion_tokens": r.completion_tokens,
        "attempt_text": (r.text or "").strip(),
        "extracted_verdict": ex.verdict,          # retained for audit; REDACTED at render (§4.5)
        "extract_flags": ex.flags,
        "error_type": r.error_type,
        "truncated": (r.completion_tokens or 0) >= max_tokens,
        "ts_utc": r.ts_utc, "host": r.host, "executor": r.executor,
        "derives_from_gold": False,
    }


def _run_batch(solver: str, rows: list[dict], rep: int, max_tokens: int = 512,
               rate_rpm: float = RATE_RPM) -> list[dict]:
    """Fixed-interval dispatch. Unpaced pools exceed the free-tier cap and take 429s."""
    interval = 60.0 / rate_rpm
    out: list[dict] = [None] * len(rows)  # type: ignore[list-item]
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = []
        for i, row in enumerate(rows):
            slack = (t0 + i * interval) - time.monotonic()
            if slack > 0:
                time.sleep(slack)
            futs.append((i, ex.submit(_attempt, solver, row, rep, max_tokens)))
        for i, f in futs:
            out[i] = f.result()
    return out


# ------------------------------------------------------------------ leveling (use 1)

def level(solver: str, sample: int = 28, levels=LEVELS, max_tokens: int = 512) -> dict:
    """Cold F0 accuracy per difficulty level. Picks the SMALLEST level inside the band."""
    out = {"solver": solver, "band": BAND, "levels": {}, "ts_utc": _now(),
           "host": socket.gethostname(), "executor": EXECUTOR}
    chosen = None
    for L in levels:
        per_class = max(1, sample // 14)
        rows = generate(L, per_class=per_class)
        recs = _run_batch(solver, rows, rep=0, max_tokens=max_tokens)
        gold = {r["uid"]: r["gold_bool"] for r in rows}
        scored = [(r["extracted_verdict"] == gold[r["uid"]]) for r in recs]
        acc = sum(scored) / len(scored) if scored else float("nan")
        pf = sum(1 for r in recs if r["extracted_verdict"] is None) / len(recs)
        tr = sum(1 for r in recs if r.get("truncated")) / len(recs)
        out["levels"][L] = {"n": len(recs), "cold_f0_accuracy": round(acc, 4),
                            "parse_fail_rate": round(pf, 4), "truncation_rate": round(tr, 4),
                            "in_band": BAND[0] <= acc <= BAND[1]}
        print(f"  [level] {L}: cold F0 {acc:.1%}  parse-fail {pf:.1%}  trunc {tr:.1%}  "
              f"{'IN BAND' if BAND[0] <= acc <= BAND[1] else 'out of band'}")
        if chosen is None and BAND[0] <= acc <= BAND[1]:
            chosen = L
    out["chosen_level"] = chosen
    out["verdict"] = "LEVELED" if chosen else "HEADROOM-FAILURE"
    return out


# ------------------------------------------------------------------ pre-pass (uses 2 + 3)

def run(solver: str, level_id: str, per_class: int, *, ledger_name: str = "probe_prepass",
        max_tokens: int = 512) -> dict:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    rows = generate(level_id, per_class=per_class)
    man_path = MANIFEST_DIR / f"manifest_{level_id}_n{len(rows)}.jsonl"
    with man_path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[prepass] manifest n={len(rows)} level={level_id} -> {man_path.name}")
    print("[prepass] rep 1 (packet-eligible)…")
    rep1 = _run_batch(solver, rows, rep=1, max_tokens=max_tokens)
    print("[prepass] rep 2 (screen + determinism only)…")
    rep2 = _run_batch(solver, rows, rep=2, max_tokens=max_tokens)

    # --- residue ledger: rep-1 AND rep-2 written for audit; loader admits rep-1 only ---------
    ledger_path = LEDGER_DIR / f"{ledger_name}.jsonl"
    with ledger_path.open("w", encoding="utf-8") as fh:
        for seq, rec in enumerate(rep1 + rep2):
            rec = dict(rec)
            rec["ledger_id"] = ledger_name
            rec["seq"] = seq
            rec["record_id"] = f"{rec['uid']}#r{rec['rep']}"
            for forbidden in ("gold", "gold_bool", "correct", "grader_output"):
                rec.pop(forbidden, None)   # belt and braces; they were never added
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    ledger_sha = hashlib.sha256(ledger_path.read_bytes()).hexdigest()

    # --- contamination screen: GOLD-DERIVED, kept in a separate, packet-ineligible file ------
    gold = {r["uid"]: r["gold_bool"] for r in rows}
    by_uid: dict[str, dict[int, bool | None]] = defaultdict(dict)
    for rec in rep1 + rep2:
        by_uid[rec["uid"]][rec["rep"]] = rec["extracted_verdict"]

    lenient, strict = [], []
    for uid, reps in by_uid.items():
        correct = {rep: (v == gold[uid]) for rep, v in reps.items()}
        if all(correct.values()) and len(correct) == 2:
            lenient.append(uid)                       # all solvers x BOTH reps (single solver here)
        if any(correct.values()):
            strict.append(uid)                        # any solver, either rep (BC-3 second read)

    screen_path = LEDGER_DIR / f"{ledger_name}_screen.json"
    screen = {
        "derives_from_gold": True,
        "note": "GOLD-DERIVED. Never packet-eligible. Analysis artifact only (R13, BC-3).",
        "solver": solver, "level": level_id, "n_tasks": len(rows),
        "contaminated_or_trivial_lenient": sorted(lenient),
        "excluded_strict": sorted(strict),
        "n_after_lenient_screen": len(rows) - len(lenient),
        "n_after_strict_screen": len(rows) - len(strict),
        "ts_utc": _now(), "host": socket.gethostname(), "executor": EXECUTOR,
    }
    screen_path.write_text(json.dumps(screen, indent=2), encoding="utf-8")

    transport = Counter(r["status"] for r in rep1 + rep2)
    meta = {
        "ledger": str(ledger_path.relative_to(ROOT)),
        "ledger_sha256": ledger_sha,
        "ledger_closed": True,
        "records": len(rep1) + len(rep2),
        "rep1_records": len(rep1),
        "manifest": str(man_path.relative_to(ROOT)),
        "manifest_sha256": manifest_sha256(rows),
        "generator_sha256": generator_sha256(),
        "screen": str(screen_path.relative_to(ROOT)),
        "n_after_lenient_screen": screen["n_after_lenient_screen"],
        "n_after_strict_screen": screen["n_after_strict_screen"],
        "power_floor_n": POWER_FLOOR_N,
        "meets_power_floor": screen["n_after_lenient_screen"] >= POWER_FLOOR_N,
        "transport": dict(transport),
        "solver": solver, "model_id": VERIFIED_SOLVERS[solver][0],
        "ts_utc": _now(), "host": socket.gethostname(), "executor": EXECUTOR,
    }
    (LEDGER_DIR / f"{ledger_name}_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["level", "run"])
    ap.add_argument("--solver", default="nvidia:deepseek-v4-flash")
    ap.add_argument("--sample", type=int, default=28)
    ap.add_argument("--level", default="L2", choices=LEVELS)
    ap.add_argument("--per-class", type=int, default=60)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    if not args.skip_preflight:
        pf = preflight(args.solver)
        print(f"[R8a] preflight {args.solver}: passed={pf['passed']} "
              f"small={pf['small_latency_s']} ceiling={pf['ceiling_latency_s']}s")
        if not pf["passed"]:
            raise SystemExit(f"R8a: {args.solver} failed preflight {pf['failures']} — "
                             "swap the solver BEFORE any arm, never mid-run")

    if args.mode == "level":
        out = level(args.solver, sample=args.sample, max_tokens=args.max_tokens)
        print(json.dumps(out, indent=2))
        if out["verdict"] == "HEADROOM-FAILURE":
            raise SystemExit("HEADROOM-FAILURE: no level lands in [0.35, 0.60]")
    else:
        meta = run(args.solver, args.level, args.per_class, max_tokens=args.max_tokens)
        print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
