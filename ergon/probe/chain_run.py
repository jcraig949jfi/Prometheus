"""Difficulty-axis measurement and pre-pass for task family v2 (prereg §3.1, §3.2, §4.2).

Two commands:

    python -m ergon.probe.chain_run axis    --solver nvidia:deepseek-v4-flash --per-depth 40
    python -m ergon.probe.chain_run prepass --solver nvidia:deepseek-v4-flash --depth 3 --n 200

`axis` MEASURES the effect of compositional depth on accuracy. The v1 dial's failure was an
ASSUMED axis (operand magnitude), and the assumption held silently until a full manifest
contradicted it. So depth is measured across all pre-declared rungs before any level is chosen,
under the band rule as jointly ruled (prereg §3.1):

  * point estimate is the standing rule (Harmonia B: 9.8% FR / 5.5% FA at n=126, best of six),
  * intervals are MANIFEST-LEVEL, not Wilson (correct estimand; 47% narrower on real data),
  * all pre-declared rungs are measured under Bonferroni adjustment (Charon: sweeping is right
    once multiplicity is paid for, and it is free at $0),
  * a straddling interval is UNDECIDED — re-measured at the decision-n, resolving conservatively
    into failure (Charon's escalation, Harmonia B's pre-declaration requirement),
  * the DISPERSION term is checked too: movable (rep-discordant) share >= 0.30 (Harmonia B R2),
  * `BAND-UNIDENTIFIED` is impossible here by construction — chance on an integer answer is ~0,
    not 0.500.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import socket
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .extract import extract_numeric
from .solver import EXECUTOR, VERIFIED_SOLVERS, call, preflight
from .task_gen_v2 import DEPTHS, generate, generate_manifest, generator_sha256, manifest_sha256

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "ergon" / "probe" / "ledgers"
MANIFEST_DIR = ROOT / "ergon" / "probe" / "manifests"

BAND = (0.35, 0.60)
MOVABLE_FLOOR = 0.30          # Harmonia B ruling 2
WORKERS = 6
RATE_RPM = 30.0
MAX_TOKENS = 2048


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _attempt(solver: str, row: dict, rep: int) -> dict:
    r = call(solver, row["prompt"], max_tokens=MAX_TOKENS)
    ex = extract_numeric(r.text if r.status == "ok" else None)
    return {
        "uid": row["uid"], "domain": row["domain"], "depth": row["depth"],
        "rep": rep, "solver": solver, "status": r.status, "latency_s": r.latency_s,
        "prompt_tokens": r.prompt_tokens, "completion_tokens": r.completion_tokens,
        "attempt_text": (r.text or "").strip(),
        "extracted_int": ex.value, "extract_flags": ex.flags,
        "error_type": r.error_type,
        "truncated": (r.completion_tokens or 0) >= MAX_TOKENS,
        "ts_utc": r.ts_utc, "host": r.host, "executor": r.executor,
        "derives_from_gold": False,
    }


def _run_batch(solver: str, rows: list[dict], rep: int) -> list[dict]:
    """Fixed-interval dispatch — an unpaced pool took 216/252 HTTP429 on 2026-08-16."""
    interval = 60.0 / RATE_RPM
    out: list[dict] = [None] * len(rows)  # type: ignore[list-item]
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = []
        for i, row in enumerate(rows):
            slack = (t0 + i * interval) - time.monotonic()
            if slack > 0:
                time.sleep(slack)
            futs.append((i, ex.submit(_attempt, solver, row, rep)))
        for i, f in futs:
            out[i] = f.result()
    return out


def _manifest_interval(successes: list[bool], conf: float) -> tuple[float, float]:
    """Manifest-level interval (Harmonia B): the manifest is frozen and the arms run on exactly
    these items, so the only live noise is solver stochasticity. Normal approximation on the
    per-item Bernoulli mean, which is the estimand the band actually cares about."""
    n = len(successes)
    if n == 0:
        return float("nan"), float("nan")
    p = sum(successes) / n
    z = _z_for(conf)
    se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    return max(0.0, p - z * se), min(1.0, p + z * se)


def _wilson(successes: list[bool], conf: float) -> tuple[float, float]:
    n = len(successes)
    if n == 0:
        return float("nan"), float("nan")
    p = sum(successes) / n
    z = _z_for(conf)
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def _z_for(conf: float) -> float:
    from statistics import NormalDist
    return NormalDist().inv_cdf(1 - (1 - conf) / 2)


def classify(lo: float, hi: float) -> str:
    if lo >= BAND[0] and hi <= BAND[1]:
        return "IN-BAND"
    if hi < BAND[0] or lo > BAND[1]:
        return "OUT-OF-BAND"
    return "UNDECIDED"


def axis(solver: str, per_depth: int, depths=DEPTHS, seed: int = 20260817) -> dict:
    """Measure depth's effect on accuracy across ALL pre-declared rungs, Bonferroni-adjusted."""
    conf = 1 - 0.05 / len(depths)          # Bonferroni over the pre-declared rungs
    out = {"solver": solver, "band": BAND, "per_depth": per_depth, "depths": {},
           "bonferroni_conf": round(conf, 5), "ts_utc": _now(),
           "host": socket.gethostname(), "executor": EXECUTOR}
    print(f"[axis] {len(depths)} rungs x {per_depth}, Bonferroni conf={conf:.4f}")
    for d in depths:
        rows = generate(d, per_depth, seed)
        for i, r in enumerate(rows):
            r["uid"] = f"axis-d{d}-{i:04d}"
        recs = _run_batch(solver, rows, rep=0)
        gold = {r["uid"]: r["gold_int"] for r in rows}
        succ = [rec["extracted_int"] == gold[rec["uid"]] for rec in recs]
        acc = sum(succ) / len(succ)
        pf = sum(1 for r in recs if r["extracted_int"] is None) / len(recs)
        tr = sum(1 for r in recs if r["truncated"]) / len(recs)
        mlo, mhi = _manifest_interval(succ, conf)
        wlo, whi = _wilson(succ, conf)
        verdict = classify(mlo, mhi)
        out["depths"][str(d)] = {
            "n": len(recs), "accuracy": round(acc, 4),
            "manifest_interval": [round(mlo, 4), round(mhi, 4)],
            "wilson_interval": [round(wlo, 4), round(whi, 4)],
            "parse_fail_rate": round(pf, 4), "truncation_rate": round(tr, 4),
            "band_verdict": verdict,
        }
        print(f"  depth {d}: acc {acc:6.1%}  manifest [{mlo:.3f},{mhi:.3f}]  "
              f"wilson [{wlo:.3f},{whi:.3f}]  pf {pf:.1%}  -> {verdict}")

    in_band = [d for d in depths if out["depths"][str(d)]["band_verdict"] == "IN-BAND"]
    undecided = [d for d in depths if out["depths"][str(d)]["band_verdict"] == "UNDECIDED"]
    out["in_band"] = in_band
    out["undecided"] = undecided
    out["chosen_depth"] = min(in_band) if in_band else None
    out["verdict"] = "LEVELED" if in_band else ("UNDECIDED-NEEDS-DECISION-N" if undecided
                                                else "HEADROOM-FAILURE")
    accs = [out["depths"][str(d)]["accuracy"] for d in depths]
    out["monotone_decreasing"] = all(a >= b for a, b in zip(accs, accs[1:]))
    out["axis_span_pp"] = round((max(accs) - min(accs)) * 100, 1)
    return out


def prepass(solver: str, depth: int, n: int, seed: int = 20260817,
            ledger_name: str = "chain_prepass") -> dict:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    rows = generate(depth, n, seed)
    for i, r in enumerate(rows):
        r["uid"] = f"chain-d{depth}-{i:05d}"

    man_path = MANIFEST_DIR / f"chain_manifest_d{depth}_n{n}.jsonl"
    with man_path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[prepass] manifest n={len(rows)} depth={depth} -> {man_path.name}")
    rep1 = _run_batch(solver, rows, rep=1)
    print("[prepass] rep 2 …")
    rep2 = _run_batch(solver, rows, rep=2)

    ledger_path = LEDGER_DIR / f"{ledger_name}.jsonl"
    with ledger_path.open("w", encoding="utf-8") as fh:
        for seq, rec in enumerate(rep1 + rep2):
            rec = dict(rec)
            rec.update(ledger_id=ledger_name, seq=seq,
                       record_id=f"{rec['uid']}#r{rec['rep']}")
            for forbidden in ("gold", "gold_int", "correct", "grader_output"):
                rec.pop(forbidden, None)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    ledger_sha = hashlib.sha256(ledger_path.read_bytes()).hexdigest()

    gold = {r["uid"]: r["gold_int"] for r in rows}
    by_uid: dict[str, dict[int, object]] = defaultdict(dict)
    for rec in rep1 + rep2:
        by_uid[rec["uid"]][rec["rep"]] = rec["extracted_int"]

    both_right = both_wrong = discordant = 0
    lenient, strict = [], []
    for uid, reps in by_uid.items():
        c = {rep: (v == gold[uid]) for rep, v in reps.items()}
        vals = list(c.values())
        if all(vals) and len(vals) == 2:
            both_right += 1
            lenient.append(uid)
        elif not any(vals):
            both_wrong += 1
        else:
            discordant += 1
        if any(vals):
            strict.append(uid)

    total = max(1, both_right + both_wrong + discordant)
    movable = discordant / total
    r1 = [r for r in rep1]
    acc_r1 = sum(1 for r in r1 if r["extracted_int"] == gold[r["uid"]]) / len(r1)

    screen = {
        "derives_from_gold": True,
        "note": "GOLD-DERIVED. Never packet-eligible. Analysis artifact only (R13, BC-3).",
        "solver": solver, "depth": depth, "n_tasks": len(rows),
        "cold_accuracy_rep1": round(acc_r1, 4),
        "both_right": both_right, "both_wrong": both_wrong, "discordant": discordant,
        "movable_share": round(movable, 4), "movable_floor": MOVABLE_FLOOR,
        "dispersion_term_passes": movable >= MOVABLE_FLOOR,
        "contaminated_or_trivial_lenient": sorted(lenient),
        "excluded_strict": sorted(strict),
        "n_after_lenient_screen": len(rows) - len(lenient),
        "n_after_strict_screen": len(rows) - len(strict),
        "ts_utc": _now(), "host": socket.gethostname(), "executor": EXECUTOR,
    }
    (LEDGER_DIR / f"{ledger_name}_screen.json").write_text(json.dumps(screen, indent=2),
                                                           encoding="utf-8")
    meta = {
        "ledger": str(ledger_path.relative_to(ROOT)), "ledger_sha256": ledger_sha,
        "ledger_closed": True, "records": len(rep1) + len(rep2), "rep1_records": len(rep1),
        "manifest": str(man_path.relative_to(ROOT)), "manifest_sha256": manifest_sha256(rows),
        "generator_sha256": generator_sha256(),
        "cold_accuracy_rep1": round(acc_r1, 4),
        "movable_share": round(movable, 4),
        "dispersion_term_passes": movable >= MOVABLE_FLOOR,
        "n_after_lenient_screen": screen["n_after_lenient_screen"],
        "transport": dict(Counter(r["status"] for r in rep1 + rep2)),
        "solver": solver, "model_id": VERIFIED_SOLVERS[solver][0],
        "ts_utc": _now(), "host": socket.gethostname(), "executor": EXECUTOR,
    }
    (LEDGER_DIR / f"{ledger_name}_meta.json").write_text(json.dumps(meta, indent=2),
                                                         encoding="utf-8")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["axis", "prepass"])
    ap.add_argument("--solver", default="nvidia:deepseek-v4-flash")
    ap.add_argument("--per-depth", type=int, default=40)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    if not args.skip_preflight:
        pf = preflight(args.solver)
        print(f"[R8a] {args.solver}: passed={pf['passed']} small={pf['small_latency_s']} "
              f"ceiling={pf['ceiling_latency_s']}s")
        if not pf["passed"]:
            raise SystemExit(f"R8a: {args.solver} failed preflight {pf['failures']}")

    if args.mode == "axis":
        print(json.dumps(axis(args.solver, args.per_depth), indent=2))
    else:
        print(json.dumps(prepass(args.solver, args.depth, args.n), indent=2))


if __name__ == "__main__":
    main()
