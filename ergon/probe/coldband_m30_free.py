"""Cold-band read for rung M30 on the free host — a MEASUREMENT, not a rung advance.

Why this is not me pre-empting the kill authority: §3.1 ruling 2 is Charon's own —
*"measure all pre-declared rungs, under Bonferroni adjustment"* — because "stopping early
was the error". M30 is a pre-declared rung (`LEVELS_MIX_PAID`) that has **never been measured
on the free host**: the n=40 free-host sweep covered M20/M40/M60/M80 only. Collecting it
executes a ruling that already exists.

What this script deliberately does NOT do: select a rung, write anything the campaign reads,
or touch `ergon/probe/ledgers/campaign/`. The *selection* between routes (a) more reps and
(b) advance to the next rung is Charon's call per
`ergon/probe/ESCALATION_P1_BAND_2026-08-21.md`. This only puts the number in his hands so the
ruling is made against data instead of my projection (~0.442, which is exactly the kind of
projection that should be checked before anyone leans on it).

Runs at n=200 x 2 reps — screening resolution, matching the paid host's M30 read (n=200,
0.500) so the two are comparable, and NOT the decision-n. Waits for the main campaign's lock
so the two never contend for the same lane.

    python ergon/probe/coldband_m30_free.py
"""
import json
import math
import os
import pathlib
import sys
import time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ergon.probe.solver import call                                  # noqa: E402
from ergon.probe.extract import extract_numeric                      # noqa: E402
from ergon.probe.task_gen_v3 import generate, manifest_sha256, generator_sha256  # noqa: E402
from ergon.probe.chain_run import TRUNCATION_GATE                    # noqa: E402

SOLVER = "nvidia:deepseek-v4-flash"
RUNG, N, SEED = "M30", 200, 20260822
MAX_TOK, TIMEOUT = 16384, 420          # 16384: the 8192 cap truncation-confounded P1 (§7m)
SPACING_S = 2.0
BAND, MOVABLE_FLOOR = (0.35, 0.60), 0.30
TRANSPORT_FLOOR = 0.95

OUT = ROOT / "ergon/probe/ledgers/coldband_m30_free"
CAMPAIGN_LOCK = ROOT / "ergon/probe/ledgers/campaign/campaign.lock"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def manifest():
    OUT.mkdir(parents=True, exist_ok=True)
    mp = OUT / f"manifest_{RUNG}_n{N}.jsonl"
    if not mp.exists():
        rows = generate(RUNG, N, SEED)
        for i, r in enumerate(rows):
            r["uid"] = f"cb30-{i:05d}"
        mp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                      encoding="utf-8")
        (OUT / "manifest_meta.json").write_text(json.dumps(
            {"rung": RUNG, "n": N, "seed": SEED, "solver_pin": SOLVER,
             "manifest_sha256": manifest_sha256(rows),
             "generator_sha256": generator_sha256(), "ts_utc": now()}, indent=2),
            encoding="utf-8")
    return [json.loads(l) for l in mp.read_text(encoding="utf-8").splitlines()]


def done_keys(led):
    if not led.exists():
        return set()
    return {(r["rep"], r["uid"]) for r in
            (json.loads(l) for l in led.read_text(encoding="utf-8").splitlines())
            if r["status"] == "ok"}


def collect(rows, led):
    have = done_keys(led)
    todo = [(rep, r) for rep in (1, 2) for r in rows if (rep, r["uid"]) not in have]
    if not todo:
        return 0, 0
    sent = ok = 0
    with led.open("a", encoding="utf-8") as fh:
        for rep, r in todo:
            if CAMPAIGN_LOCK.exists():        # never contend with the main campaign
                print("campaign firing active — yielding the lane")
                break
            res = call(SOLVER, r["prompt"], max_tokens=MAX_TOK, timeout=TIMEOUT, retries=0)
            sent += 1
            fh.write(json.dumps({
                "solver": SOLVER, "uid": r["uid"], "rep": rep, "status": res.status,
                "error_type": res.error_type, "latency_s": res.latency_s,
                "completion_tokens": res.completion_tokens,
                "extracted_int": extract_numeric(res.text if res.status == "ok" else None).value,
                "attempt_text": (res.text or "").strip()[:4000], "derives_from_gold": False,
                "ts_utc": res.ts_utc, "host": res.host, "executor": res.executor,
            }, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
            if res.status == "ok":
                ok += 1
            elif res.error_type in ("HTTP429", "HTTP402"):
                print("quota wall — stopping")
                break
            time.sleep(SPACING_S)
    return sent, ok


def read(rows, led):
    recs = [json.loads(l) for l in led.read_text(encoding="utf-8").splitlines()]
    gold = {r["uid"]: r["gold_int"] for r in rows}
    best = {(r["rep"], r["uid"]): r for r in recs if r["status"] == "ok"}
    n = len(rows)

    transport_ok = len(best) / max(1, len(recs))
    if transport_ok < TRANSPORT_FLOOR:
        return {"verdict": "INVALID-TRANSPORT", "transport_ok_rate": round(transport_ok, 4),
                "floor": TRANSPORT_FLOOR, "ts_utc": now(),
                "note": "a dead lane scores every row wrong and would emit a confident 0.0"}

    rep1 = [best[(1, r["uid"])] for r in rows if (1, r["uid"]) in best]
    trunc = sum(1 for x in rep1 if (x.get("completion_tokens") or 0) >= MAX_TOK) / max(1, len(rep1))
    if trunc > TRUNCATION_GATE:
        return {"verdict": "TRUNCATION-CONFOUNDED", "truncation_rate": round(trunc, 4),
                "gate": TRUNCATION_GATE, "ts_utc": now()}

    acc = sum(1 for r in rows if (1, r["uid"]) in best
              and best[(1, r["uid"])]["extracted_int"] == gold[r["uid"]]) / n
    disc = sum(1 for r in rows
               if (1, r["uid"]) in best and (2, r["uid"]) in best
               and (best[(1, r["uid"])]["extracted_int"] == gold[r["uid"]])
               != (best[(2, r["uid"])]["extracted_int"] == gold[r["uid"]])) / n
    z = 1.959964
    se = math.sqrt(max(acc * (1 - acc), 1e-12) / n)
    lo, hi = max(0.0, acc - z * se), min(1.0, acc + z * se)
    straddles = (lo < BAND[0] < hi) or (lo < BAND[1] < hi)
    edge = BAND[0] if abs(acc - BAND[0]) < abs(acc - BAND[1]) else BAND[1]
    margin = abs(acc - edge)
    n_dec = math.ceil((z / margin) ** 2 * acc * (1 - acc)) if margin > 1e-9 else None
    point_in = BAND[0] <= acc <= BAND[1]
    verdict = ("NOT-LEVELED" if not point_in else
               "NOT-LEVELED-DISPERSION" if disc < MOVABLE_FLOOR else
               ("UNDECIDED-RESOLVES-TO-FAILURE" if (n_dec is not None and n >= n_dec)
                else "UNDECIDED-UNDERPOWERED") if straddles else "LEVELED")
    return {
        "purpose": "cold-band MEASUREMENT of a pre-declared rung (§3.1 ruling 2). NOT a rung "
                   "selection — that is the kill authority's call per ESCALATION_P1_BAND.",
        "solver_pin": SOLVER, "rung": RUNG, "n": n, "resolution": "screening (n=200), not decision-n",
        "point_estimate": round(acc, 4),
        "manifest_interval_95": [round(lo, 4), round(hi, 4)],
        "interval_straddles_band_edge": straddles,
        "n_required_for_decidability": n_dec,
        "movable_share": round(disc, 4), "truncation_rate": round(trunc, 4),
        "transport_ok_rate": round(transport_ok, 4),
        "leveling_verdict": verdict,
        "comparator_paid_M30": {"point_estimate": 0.500, "n": 200,
                                "note": "paid host read; hosts are never pooled (R9)"},
        "scope_caveat": "D0 self-generated residue family; pinned to (manifest x host).",
        "ts_utc": now(),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = manifest()
    led = OUT / "coldband.jsonl"
    sent, ok = collect(rows, led)
    have = done_keys(led)
    print(f"collected +{ok}/{sent} this run · coverage {len(have)}/{2 * len(rows)}")
    if len(have) < 2 * len(rows):
        return
    out = read(rows, led)
    tmp = (OUT / "bandread.json").with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, indent=2), encoding="utf-8")
    os.replace(tmp, OUT / "bandread.json")
    print(json.dumps({k: out[k] for k in list(out)[:8] if k in out}, indent=2))


if __name__ == "__main__":
    main()
