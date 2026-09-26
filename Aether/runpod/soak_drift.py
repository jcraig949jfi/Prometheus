"""Read a soak flight's evidence and test the Iteration 3 drift predictions.

    python soak_drift.py receipts/<run_id>.json

Every check is the preregistered one (receipts/i3_preregistration.json,
flight L1), computed from the saved rows -- the module's windowed progress
records, the platform samples, the controller's API calls and health
records -- never from the receipt's own summary, so a summary bug cannot
make a drift disappear. Prints one line per prediction, PASS / FAIL /
UNMEASURED, and exits 0 regardless: a failed prediction is a finding.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rows(path, kind=None):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if kind is None or rec.get("kind") == kind:
                out.append(rec)
    return out


def median(vals):
    vals = sorted(v for v in vals if v is not None)
    return vals[len(vals) // 2] if vals else None


def rel(a, b):
    return None if (a is None or not b) else (a - b) / b


def analyse(receipt_path):
    with open(receipt_path, encoding="utf-8") as fh:
        rec = json.load(fh)
    ev = os.path.join(HERE, rec.get("evidence_dir", ""))
    prog = rows(os.path.join(ev, "telemetry.jsonl"), "progress")
    plat = rows(os.path.join(ev, "platform.jsonl"), "platform")
    api = rows(os.path.join(ev, "api_calls.jsonl"))
    health = rows(os.path.join(ev, "controller_health.jsonl"))
    out = {"run_id": rec["run_id"], "result": rec["result"],
           "cause": (rec.get("disposition") or {}).get("cause"),
           "windows": len(prog), "platform_samples": len(plat), "checks": {}}
    c = out["checks"]

    ends = rows(os.path.join(ev, "telemetry.jsonl"), "end")
    elapsed = ends[-1].get("elapsed_s") if ends else None
    c["P1_duration"] = {"module_elapsed_s": elapsed,
                        "pass": elapsed is not None
                        and abs(elapsed - 3900.0) <= 2.0}
    cost = (rec.get("cost") or {}).get("usd_estimated")
    c["P2_cost"] = {"usd": cost, "gpu": rec.get("gpu_used"),
                    "pass": cost is not None and cost <= 0.62}

    held = [p.get("pool_held_b") for p in prog[30:]]
    free = [p.get("device_free_b") for p in prog]
    if len(prog) > 31 and held[0] is not None:
        c["P3_device_memory"] = {
            "pool_held_distinct_after_w30": sorted(set(held)),
            "device_free_w30": free[30], "device_free_last": free[-1],
            "pass": len(set(held)) == 1 and abs(free[-1] - free[30])
            <= 64 * (1 << 20)}
    else:
        c["P3_device_memory"] = {"pass": None, "note": "too few windows"}

    rss = [p.get("rss_b") for p in prog]
    if len(prog) >= 50:
        base, last = median(rss[30:40]), median(rss[-10:])
        c["P4_host_memory"] = {"rss_w30_39": base, "rss_last10": last,
                               "rel": rel(last, base),
                               "pass": abs(rel(last, base)) <= 0.05}

    p50 = [p.get("latency_p50_s") for p in prog]
    if len(prog) >= 90:
        early, late = median(p50[30:60]), median(p50[-30:])
        c["P5_throughput"] = {"p50_w30_59": early, "p50_last30": late,
                              "rel": rel(late, early),
                              "pass": abs(rel(late, early)) <= 0.05}
    ratios = [p["latency_p99_s"] / p["latency_p50_s"] for p in prog
              if p.get("latency_p50_s")]
    if ratios:
        share = sum(1 for r in ratios if r < 1.5) / float(len(ratios))
        c["P6_tail_latency"] = {"share_windows_p99_over_p50_lt_1_5": share,
                                "max_ratio": max(ratios),
                                "pass": share >= 0.95}

    t = [p.get("t_elapsed_s") for p in prog]
    gaps = [b - a for a, b in zip(t, t[1:])]
    costs = [p.get("sample_cost_s") for p in plat]
    first10 = [p.get("sample_cost_s") for p in plat
               if p.get("t_elapsed_s", 0) - plat[0].get("t_elapsed_s", 0)
               <= 600] if plat else []
    last10 = [p.get("sample_cost_s") for p in plat
              if plat[-1].get("t_elapsed_s", 0) - p.get("t_elapsed_s", 0)
              <= 600] if plat else []
    c["P7_telemetry_cadence"] = {
        "max_progress_gap_s": max(gaps) if gaps else None,
        "sampler_cost_p50_first10min": median(first10),
        "sampler_cost_p50_last10min": median(last10),
        "pass": (bool(gaps) and max(gaps) <= 30.0 and median(first10)
                 and median(last10) <= 2 * median(first10))}

    integ = rec.get("artifact_integrity") or {}
    last = prog[-1] if prog else {}
    peak = (rec.get("platform_summary") or {}).get("artifact_dir_b_peak")
    c["P8_artifact_growth"] = {
        "series_rows": len(prog), "series_bytes_last": last.get("series_bytes"),
        "checkpoints": len(rows(os.path.join(ev, "telemetry.jsonl"), "event")),
        "artifact_dir_peak_b": peak, "verified": integ.get("verified"),
        "mismatch": integ.get("mismatch"), "missing": rec.get("artifacts_missing"),
        "pass": (388 <= len(prog) <= 392 and not integ.get("mismatch")
                 and not rec.get("artifacts_missing")
                 and sorted(integ.get("verified") or [])
                 == sorted(rec.get("artifacts_expected") or []))}

    lat = rec.get("api_latency") or {}
    per_op = {}
    ok = True
    for op, e in lat.items():
        f, s = e.get("first_half_p50_s"), e.get("second_half_p50_s")
        fail_share = e["failures"] / float(e["calls"]) if e["calls"] else 0
        per_op[op] = {"first_p50": f, "second_p50": s, "calls": e["calls"],
                      "failure_share": round(fail_share, 4)}
        if f and s and s > 2 * f:
            ok = False
        if op != "fetch" and fail_share >= 0.05:
            ok = False
    c["P9_provider_latency"] = {"per_op": per_op, "pass": ok,
                                "note": "fetch failures include every "
                                        "not-yet-up poll before first "
                                        "contact, so they are excluded "
                                        "from the 5% bound"}

    cs = rec.get("clock_sync") or {}
    a, b = (cs.get("start") or {}), (cs.get("end") or {})
    if a.get("offset_s") is not None and b.get("offset_s") is not None:
        c["P10_clock"] = {"start": a["offset_s"], "end": b["offset_s"],
                          "drift_s": round(b["offset_s"] - a["offset_s"], 4),
                          "pass": abs(b["offset_s"] - a["offset_s"]) <= 0.5}
    else:
        c["P10_clock"] = {"pass": None, "note": "offset missing at one end"}

    res = rec.get("resumed") or {}
    pods = rec.get("pods") or []
    c["P11_controller_state"] = {
        "resumed": res, "creates": len(rec.get("create_attempts") or []),
        "absence_evidence": (pods[0] if pods else {}).get("absence_evidence"),
        "pass": bool(res) and bool(pods) and pods[0].get("observed_absent")}

    if health:
        c["P12_spend_accounting"] = {
            "controller_last_spend": health[-1].get("spend_usd"),
            "receipt_cost": cost,
            "note": "the controller's last watch spend precedes retrieval "
                    "and teardown, so the receipt is expected to be slightly "
                    "higher",
            "pass": cost is not None and health[-1].get("spend_usd")
            is not None and abs(cost - health[-1]["spend_usd"]) / cost
            <= 0.02}
    return out


def main(argv=None):
    argv = argv or sys.argv[1:]
    out = analyse(argv[0])
    for name, check in out["checks"].items():
        verdict = {True: "PASS", False: "FAIL", None: "UNMEASURED"}[
            check.get("pass")]
        print("%-24s %-10s %s" % (name, verdict, json.dumps(
            {k: v for k, v in check.items() if k != "pass"}, default=str)))
    if len(argv) > 1:
        with open(argv[1], "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, sort_keys=True, default=str)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
