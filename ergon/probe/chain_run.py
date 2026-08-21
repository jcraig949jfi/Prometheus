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
import os
import socket
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .extract import extract_numeric
from .solver import EXECUTOR, VERIFIED_SOLVERS, call, preflight
from .task_gen_v2 import DEPTHS, generate, generate_manifest, generator_sha256, manifest_sha256
from . import task_gen_v3

#: Family registry. `axis` is family-agnostic: three axes have died, so the rung sweep is the
#: reusable instrument and the generator is the swappable part.
FAMILIES = {
    "chain": (generate, DEPTHS),                       # v2 — compositional depth (measured dead)
    "nearmiss": (task_gen_v3.generate, task_gen_v3.LEVELS),   # v3 — adversarial near-misses
    "nearmiss_mix": (task_gen_v3.generate, task_gen_v3.LEVELS_MIX),  # v3 intermediate rungs
    "nearmiss_mix_paid": (task_gen_v3.generate, task_gen_v3.LEVELS_MIX_PAID),  # paid-host bisection
}

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER_DIR = ROOT / "ergon" / "probe" / "ledgers"
MANIFEST_DIR = ROOT / "ergon" / "probe" / "manifests"

#: Transport timeout for the NEAR-MISS family, re-derived by measurement (same discipline as
#: the token budget). The standing 180s was derived on families with <=96-token outputs; this
#: family generates up to 3,873 tokens (lenprobe), so generation time dominates and 180s clips
#: the long-response rungs hardest — M40 hit 17.5% timeouts vs M80's 2.5%, the truncation
#: defect's class one level down. The length probe ran 24/24 with ZERO timeouts at 300s;
#: 420s carries ~40% margin over that.
TIMEOUT_LONG_S = 420.0

BAND = (0.35, 0.60)
MOVABLE_FLOOR = 0.30          # Harmonia B ruling 2
WORKERS = 6
#: 30 RPM was measured clean with 64-TOKEN outputs (the 08-13 ladder). This family generates
#: 1,500-3,900 tokens per response, and the free tier's throttle is effectively token-driven:
#: the chain-3 mislaunch took 240x HTTP429 out of 400 calls at 30 RPM dispatch, with each 429
#: retrying up to 5x and multiplying the request rate past the pacing. 12 RPM matches the
#: observed sustainable throughput (p50 latency 24s across 6 workers).
RATE_RPM = 12.0
#: MEASURED, not assumed (2026-08-18, ergon/probe/ledgers/lenprobe_nearmiss.txt). At 16384 no
#: response on this family hit the cap; pooled p99 = 3873 and the per-rung maxima are
#: A0 3873 · A1 1531 · A2 2698 · A3 3346. That distribution explains the rung-correlated
#: truncation exactly: A1's longest response fits under 2048, A0's and A2's do not, which is why
#: truncation ran 0.000 at A1 against 0.400/0.425 at A0/A2 — silent, rung-correlated missing data
#: on the very comparison the axis rests on. 8192 is >2x the observed maximum. A high cap costs
#: nothing when unused: latency scales with tokens GENERATED, not with the ceiling.
MAX_TOKENS = 8192

#: Truncation is a STANDING HAZARD of this family, not an incident. It corrupted the leveling run
#: on 2026-08-16 and reappeared in the first sweep that produced a working axis. So it is a
#: pre-flight gate on every rung from here on: a sweep with any rung above this refuses to name a
#: chosen rung, whatever the accuracies look like.
TRUNCATION_GATE = 0.02


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _attempt(solver: str, row: dict, rep: int) -> dict:
    r = call(solver, row["prompt"], max_tokens=MAX_TOKENS, timeout=TIMEOUT_LONG_S)
    ex = extract_numeric(r.text if r.status == "ok" else None)
    return {
        "uid": row["uid"], "domain": row["domain"], "depth": row.get("depth"),
        "rep": rep, "solver": solver, "status": r.status, "latency_s": r.latency_s,
        "rung": row.get("depth", row.get("level")),
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


def axis(solver: str, per_depth: int, depths=DEPTHS, seed: int = 20260817,
         family: str = "chain") -> dict:
    """Measure a rung set's effect on accuracy across ALL pre-declared rungs, Bonferroni-adjusted.

    Family-agnostic by design: three difficulty axes have now died, so the sweep is the durable
    instrument and the generator is the part that gets replaced.
    """
    gen, default_rungs = FAMILIES[family]
    depths = depths if depths is not None else default_rungs
    conf = 1 - 0.05 / len(depths)          # Bonferroni over the pre-declared rungs
    out = {"solver": solver, "family": family, "band": BAND, "per_depth": per_depth,
           "depths": {}, "bonferroni_conf": round(conf, 5), "ts_utc": _now(),
           "host": socket.gethostname(), "executor": EXECUTOR}
    print(f"[axis] family={family} {len(depths)} rungs x {per_depth}, "
          f"Bonferroni conf={conf:.4f}")
    for d in depths:
        rows = gen(d, per_depth, seed)
        for i, r in enumerate(rows):
            r["uid"] = f"axis-{family}-{d}-{i:04d}"
        recs = _run_batch(solver, rows, rep=0)
        gold = {r["uid"]: r["gold_int"] for r in rows}
        succ = [rec["extracted_int"] == gold[rec["uid"]] for rec in recs]
        acc = sum(succ) / len(succ)
        pf = sum(1 for r in recs if r["extracted_int"] is None) / len(recs)
        tr = sum(1 for r in recs if r["truncated"]) / len(recs)
        to = sum(1 for r in recs if r["status"] == "timeout") / len(recs)
        mlo, mhi = _manifest_interval(succ, conf)
        wlo, whi = _wilson(succ, conf)
        verdict = classify(mlo, mhi)
        out["depths"][str(d)] = {
            "n": len(recs), "accuracy": round(acc, 4),
            "manifest_interval": [round(mlo, 4), round(mhi, 4)],
            "wilson_interval": [round(wlo, 4), round(whi, 4)],
            "parse_fail_rate": round(pf, 4), "truncation_rate": round(tr, 4),
            "timeout_rate": round(to, 4), "max_tokens": MAX_TOKENS,
            "band_verdict": verdict,
        }
        print(f"  rung {d}: acc {acc:6.1%}  manifest [{mlo:.3f},{mhi:.3f}]  "
              f"pf {pf:.1%}  trunc {tr:.1%}  to {to:.1%}  -> {verdict}")

    in_band = [d for d in depths if out["depths"][str(d)]["band_verdict"] == "IN-BAND"]
    undecided = [d for d in depths if out["depths"][str(d)]["band_verdict"] == "UNDECIDED"]
    out["in_band"] = in_band
    out["undecided"] = undecided
    # PRE-FLIGHT GATE, applied before any rung is chosen.
    worst_trunc = max((out["depths"][str(d)]["truncation_rate"] for d in depths), default=0.0)
    out["max_truncation_rate"] = worst_trunc
    out["truncation_gate_passed"] = worst_trunc <= TRUNCATION_GATE
    out["chosen_depth"] = (min(in_band) if in_band else None) if out["truncation_gate_passed"] else None
    if not out["truncation_gate_passed"]:
        out["verdict"] = "TRUNCATION-CONFOUNDED"
        out["verdict_note"] = (
            f"max truncation {worst_trunc:.1%} exceeds the {TRUNCATION_GATE:.0%} gate — "
            "accuracies are not comparable across rungs and no rung may be chosen")
    else:
        out["verdict"] = "LEVELED" if in_band else ("UNDECIDED-NEEDS-DECISION-N" if undecided
                                                    else "HEADROOM-FAILURE")
    accs = [out["depths"][str(d)]["accuracy"] for d in depths]
    out["accuracy_by_rung"] = dict(zip([str(d) for d in depths], accs))
    out["monotone_decreasing"] = all(a >= b for a, b in zip(accs, accs[1:]))
    out["axis_span_pp"] = round((max(accs) - min(accs)) * 100, 1)
    return out


def prepass(solver: str, depth: int, n: int, seed: int = 20260819,
            ledger_name: str = None, family: str = "chain", rung: str = None) -> dict:
    """Two cold executions, three uses (§4.2): contamination screen + dispersion term + D0/D1
    residue. For a rung escalated to decision-n this run IS the decision measurement — the
    band is read on rep-1 of the full manifest (HB-R1: at one solver the lenient screen is a
    diagnostic, not a filter), and the dispersion term comes from the two reps."""
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    gen, _rungs = FAMILIES[family]
    rung_id = rung if rung is not None else depth
    rows = gen(rung_id, n, seed)
    tag = f"{family}-{rung_id}"
    for i, r in enumerate(rows):
        r["uid"] = f"{tag}-{i:05d}"
    ledger_name = ledger_name or f"{tag}_prepass"

    man_path = MANIFEST_DIR / f"{tag}_manifest_n{n}.jsonl"
    with man_path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[prepass] family={family} rung={rung_id} n={len(rows)} seed={seed} -> {man_path.name}")
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
        "solver": solver, "family": family, "rung": str(rung_id), "n_tasks": len(rows),
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
    # TRANSPORT GATE (2026-08-21). Two artifacts have now emitted vacuous verdicts from dead
    # lanes: the M20 free-lane run (400/400 err -> NOT-LEVELED at 0.0) and the nemotron
    # cold-band (357/400 err -> same). A band read from a dead lane is not a band read.
    ok_rate = sum(1 for r in rep1 + rep2 if r["status"] == "ok") / max(1, len(rep1) + len(rep2))
    if ok_rate < 0.95:
        raise SystemExit(
            f"TRANSPORT-DEAD: ok-rate {ok_rate:.2f} < 0.95 - no band read, no screen, no "
            "residue ledger is emitted from a dead lane (R11: discard whole)")

    # DECISION-N BAND READ (prereg §3.1, full rule): point estimate on rep-1 of the FULL
    # manifest (HB-R1), manifest-level interval at k=1 (only this rung is being re-measured,
    # per "Bonferroni across whatever rungs you re-measure"), AND the dispersion term.
    succ_r1 = [r["extracted_int"] == gold[r["uid"]] for r in rep1]
    blo, bhi = _manifest_interval(succ_r1, 0.95)
    point_in = BAND[0] <= acc_r1 <= BAND[1]
    interval_in = blo >= BAND[0] and bhi <= BAND[1]
    band_read = {
        "point_estimate": round(acc_r1, 4),
        "manifest_interval_95": [round(blo, 4), round(bhi, 4)],
        "point_in_band": point_in,
        "interval_wholly_in_band": interval_in,
        "movable_share": round(movable, 4),
        "dispersion_term_passes": movable >= MOVABLE_FLOOR,
        "full_band_passes": point_in and movable >= MOVABLE_FLOOR,
        "leveling_verdict": ("LEVELED" if (point_in and movable >= MOVABLE_FLOOR)
                             else "NOT-LEVELED"),
    }

    meta = {
        "band_read": band_read,
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


def write_atomic(path: pathlib.Path, text: str) -> None:
    """Write-to-temp-then-rename. A ledger that can exist while empty is a hazard in its own
    right — the M-sweep's output file sat zero-bytes on origin for a day because shell
    redirection creates the file at launch and Python block-buffers until exit, so a mid-run
    commit captured an empty shell. Results now land atomically or not at all."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["axis", "prepass"])
    ap.add_argument("--solver", default="nvidia:deepseek-v4-flash")
    ap.add_argument("--per-depth", type=int, default=40)
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--family", default="chain", choices=sorted(FAMILIES))
    ap.add_argument("--out", default=None, help="atomic JSON output path (temp+rename)")
    ap.add_argument("--rung", default=None, help="prepass: rung id for non-chain families")
    ap.add_argument("--skip-preflight", action="store_true")
    args = ap.parse_args()

    if not args.skip_preflight:
        pf = preflight(args.solver)
        print(f"[R8a] {args.solver}: passed={pf['passed']} small={pf['small_latency_s']} "
              f"ceiling={pf['ceiling_latency_s']}s")
        if not pf["passed"]:
            raise SystemExit(f"R8a: {args.solver} failed preflight {pf['failures']}")

    if args.mode == "axis":
        out = axis(args.solver, args.per_depth, depths=None, family=args.family)
    else:
        out = prepass(args.solver, args.depth, args.n, family=args.family, rung=args.rung)
    text = json.dumps(out, indent=2)
    print(text)
    if args.out:
        write_atomic(pathlib.Path(args.out), text)


if __name__ == "__main__":
    main()
