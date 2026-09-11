"""Pollux re-scan: re-execute the daemon's own statistic on all nine pairs.

Questions answered (each recorded in pollux_rescan_result.json):
  Q1  Is corr_raw identically 1.0 on the real data (the sorted/sorted
      tautology claimed in pivot/COMPONENT_DOSSIERS_2026-06-24.md)?
  Q2  What kill_pattern / verdict does each of the 9 pairs produce today,
      and is it deterministic (same answer on re-run)?
  Q3  Which kill_patterns are REACHABLE at all given corr_raw == 1.0?
  Q4  Does a deterministic replay of the rotation + settle policy
      (SEED_PAIRS, CANDIDATE_POOL, SETTLE_THRESHOLD, verdict-only settle)
      reproduce the P69 census (286 rows: sign_flips 86 / survives 39 /
      attenuates 161; deg18_vs_deg20 x54, even_deg_vs_odd_deg x56)?

Offline. Reads only prometheus_math's bundled Mahler database via the
daemon's own _load_subset. Writes only the result file beside this script.
The daemon module is imported (not instantiated): PolluxAgent.__init__ is
what creates state dirs, and it is never called here.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
DAEMON = REPO_ROOT / "charon" / "agents" / "pollux" / "daemon.py"
OUT = HERE / "pollux_rescan_result.json"

sys.path.insert(0, str(REPO_ROOT))


def load_daemon():
    """Import charon/agents/pollux/daemon.py as a module without running
    any agent code. Records whether the import itself succeeds (a missing
    dependency here would be a CONFIGURATION finding)."""
    spec = importlib.util.spec_from_file_location("pollux_daemon", DAEMON)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_pair(d, pair):
    """Exact replica of the arithmetic in PolluxAgent.run_tick (daemon.py
    lines ~415-437), using the daemon's own functions."""
    a_vals, a_desc = d._load_subset(pair["a"])
    b_vals, b_desc = d._load_subset(pair["b"])
    if not a_vals or not b_vals:
        return {"pair": pair["name"], "error": "subset_load_failed a=%s b=%s" % (a_desc, b_desc)}
    n = min(len(a_vals), len(b_vals))
    a_paired = sorted(a_vals)[:n]
    b_paired = sorted(b_vals)[:n]
    corr_raw = d._spearman(a_paired, b_paired)
    a_norm = d._mean_spacing_normalize(a_paired)
    b_norm = d._mean_spacing_normalize(b_paired)
    n_norm = min(len(a_norm), len(b_norm))
    corr_norm = d._spearman(a_norm[:n_norm], b_norm[:n_norm]) if n_norm >= 10 else None
    kp = d._classify(corr_raw, corr_norm)
    if kp == "pollux_correlation_survives_normalization":
        verdict = "PROMOTED"
    elif kp in ("pollux_sign_flips_under_normalization", "pollux_no_correlation_observed"):
        verdict = "REJECTED"
    else:
        verdict = "UNVERIFIED"
    return {
        "pair": pair["name"],
        "n_a": len(a_vals), "n_b": len(b_vals), "n_paired": n,
        "a_desc": a_desc, "b_desc": b_desc,
        "truncation": ("larger subset cut to its n smallest values"
                       if len(a_vals) != len(b_vals) else "none"),
        "corr_raw": corr_raw,
        "corr_norm": corr_norm,
        "kill_pattern": kp,
        "verdict": verdict,
        "settle_reachable": verdict in ("PROMOTED", "REJECTED"),
    }


def reachable_patterns(d):
    """With corr_raw == 1.0 fixed, sweep corr_norm over [-1, 1] and list
    which kill_patterns _classify can ever return, with their corr_norm
    intervals. This is the effective decision rule of the instrument."""
    out = {}
    steps = 4001
    prev = None
    for i in range(steps):
        cn = -1.0 + 2.0 * i / (steps - 1)
        kp = d._classify(1.0, cn)
        if kp != prev:
            out.setdefault(kp, []).append([round(cn, 4), None])
            if prev is not None:
                out[prev][-1][1] = round(cn, 4)
            prev = kp
    out[prev][-1][1] = 1.0
    return out


def replay_rotation(d, verdict_by_pair, n_ticks):
    """Deterministic replay of _pick_and_advance + _record_verdict_and_
    check_settle + _promote_settled_replace, assuming each pair always
    returns the verdict measured today (the scan is deterministic on
    static data)."""
    active = [p["name"] for p in d.SEED_PAIRS]
    pool = [p["name"] for p in d.CANDIDATE_POOL]
    cand_idx = 0
    rot_idx = 0
    history = {}
    settled = []
    counts = {}
    pattern_counts = {}
    for t in range(n_ticks):
        name = active[rot_idx % len(active)]
        rot_idx = (rot_idx + 1) % max(1, len(active))
        v = verdict_by_pair[name]["verdict"]
        kp = verdict_by_pair[name]["kill_pattern"]
        counts[name] = counts.get(name, 0) + 1
        pattern_counts[kp] = pattern_counts.get(kp, 0) + 1
        ph = history.get(name, [])
        ph.append(v)
        ph = ph[-d.SETTLE_THRESHOLD * 2:]
        history[name] = ph
        recent = ph[-d.SETTLE_THRESHOLD:]
        is_settled = (
            len(recent) >= d.SETTLE_THRESHOLD
            and all(x == recent[0] for x in recent)
            and recent[0] in ("PROMOTED", "REJECTED")
        )
        if is_settled:
            settled.append({"name": name, "verdict": v, "tick": t + 1})
            active = [a for a in active if a != name]
            if cand_idx < len(pool):
                active.append(pool[cand_idx])
                cand_idx += 1
            if not active:
                break
    return {
        "n_ticks": n_ticks,
        "rows_per_pair": counts,
        "rows_per_pattern": pattern_counts,
        "settled": settled,
        "final_active": active,
        "pool_exhausted": cand_idx >= len(pool),
        "never_settling_pairs": [a for a in active if verdict_by_pair[a]["verdict"] == "UNVERIFIED"],
    }


def main():
    result = {"script": "pollux_rescan.py",
              "daemon_path": DAEMON.relative_to(REPO_ROOT).as_posix()}
    try:
        d = load_daemon()
        result["daemon_import"] = "ok"
    except Exception as e:  # dependency failure is itself a finding
        result["daemon_import"] = "FAILED: %s: %s" % (type(e).__name__, e)
        OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
        print(json.dumps(result, indent=1))
        return
    result["constants"] = {
        "SETTLE_THRESHOLD": d.SETTLE_THRESHOLD,
        "CORR_SIGNIFICANT": d.CORR_SIGNIFICANT,
        "CORR_FLIPPED_DELTA": d.CORR_FLIPPED_DELTA,
        "n_seed_pairs": len(d.SEED_PAIRS),
        "n_candidate_pool": len(d.CANDIDATE_POOL),
    }
    pairs = list(d.SEED_PAIRS) + list(d.CANDIDATE_POOL)
    scans = [scan_pair(d, p) for p in pairs]
    scans2 = [scan_pair(d, p) for p in pairs]
    result["scans"] = scans
    result["deterministic_on_rerun"] = all(
        (a.get("corr_raw"), a.get("corr_norm"), a.get("kill_pattern")) ==
        (b.get("corr_raw"), b.get("corr_norm"), b.get("kill_pattern"))
        for a, b in zip(scans, scans2)
    )
    ok = [s for s in scans if "error" not in s]
    # The daemon rounds to 4 dp before writing the ledger (stats["corr_raw"]),
    # so the ledger-visible value is round(corr_raw, 4); float noise of 2e-16 is
    # reported separately so nobody can read it as a departure from 1.0.
    result["Q1_corr_raw_all_exactly_1_at_ledger_precision"] = (
        all(round(s["corr_raw"], 4) == 1.0 for s in ok) and len(ok) == len(scans))
    result["Q1_corr_raw_max_abs_dev_from_1"] = max(abs(s["corr_raw"] - 1.0) for s in ok) if ok else None
    result["Q1_corr_raw_values"] = [s.get("corr_raw") for s in scans]
    result["Q2_verdicts"] = {s["pair"]: [s.get("kill_pattern"), s.get("verdict"), s.get("corr_norm")]
                             for s in scans}
    result["Q3_reachable_patterns_given_corr_raw_1"] = reachable_patterns(d)
    all_patterns = {"pollux_sign_flips_under_normalization",
                    "pollux_correlation_survives_normalization",
                    "pollux_no_correlation_observed",
                    "pollux_correlation_attenuates_under_normalization"}
    result["Q3_unreachable_patterns"] = sorted(
        all_patterns - set(result["Q3_reachable_patterns_given_corr_raw_1"]))
    if len(ok) == len(scans):
        vb = {s["pair"]: s for s in ok}
        rep = replay_rotation(d, vb, 286)
        result["Q4_replay_286_ticks"] = rep
        p69 = {"total": 286, "sign_flips": 86, "survives": 39, "attenuates": 161,
               "deg18_vs_deg20": 54, "even_deg_vs_odd_deg": 56}
        rp = rep["rows_per_pattern"]
        got = {
            "total": sum(rp.values()),
            "sign_flips": rp.get("pollux_sign_flips_under_normalization", 0),
            "survives": rp.get("pollux_correlation_survives_normalization", 0),
            "attenuates": rp.get("pollux_correlation_attenuates_under_normalization", 0),
            "deg18_vs_deg20": rep["rows_per_pair"].get("deg18_vs_deg20", 0),
            "even_deg_vs_odd_deg": rep["rows_per_pair"].get("even_deg_vs_odd_deg", 0),
        }
        result["Q4_p69_census_claimed"] = p69
        result["Q4_replay_census"] = got
        result["Q4_replay_matches_p69"] = {k: (got[k] == p69[k]) for k in p69}
        result["Q4_note"] = (
            "The replay assumes today's data equals the May-2026 data and that every "
            "tick succeeded (no short-circuit rows). A mismatch therefore does NOT by "
            "itself impeach P69; it bounds how much of the census the code alone explains."
        )
    OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")
    print(json.dumps({k: v for k, v in result.items() if k != "scans"}, indent=1))


if __name__ == "__main__":
    main()
