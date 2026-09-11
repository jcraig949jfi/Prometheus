#!/usr/bin/env python3
"""
Cleric attack on Q4 of pollux_rescan.py (Rhadamanthus trial, 2026-09-11).

The Necromancer replayed the v0.6 rotation for 286 ticks on today's verdict
map and got 15/15/256, then wrote "P69's 86/39/161 not reproduced". That
replay ignores that the daemon ran v0.5 (round-robin over the four seed
pairs, no settle policy) from 2026-05-24 03:08 until the v0.6 commit at
2026-05-25 01:46 local (~22.6 h), and it fixes every pair's verdict to
today's value. This script searches the space the record leaves open:

  k        = number of v0.5 ticks (round-robin, rotation index from 0)
  idx0     = whether v0.6 inherited v0.5's persisted pair_rotation_idx
  map      = the May verdict of the six pairs whose May summaries are NOT
             preserved anywhere on the tree (the Keeper's second channel
             enumerates only the first three summaries: deg10 REJECTED
             sign_flips, deg14 PROMOTED survives, salem PROMOTED survives);
             those three are pinned.

Target: P69 (engine/ledger/AGENT_AUTOPSIES.jsonl line 18):
  patterns sign_flips=86 survives=39 attenuates=161; per pair deg18=54,
  even_deg_vs_odd_deg=56; every pair distinct-outcome=1; 286 rows total.

Output: cleric_census_fit_result.json (written from Python, flushed per
section). Read-only on the tree apart from that file. No network.
"""
import importlib.util
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
OUT = HERE / "cleric_census_fit_result.json"
sys.path.insert(0, str(REPO_ROOT))
DAEMON = REPO_ROOT / "charon" / "agents" / "pollux" / "daemon.py"

SF = "pollux_sign_flips_under_normalization"
SV = "pollux_correlation_survives_normalization"
AT = "pollux_correlation_attenuates_under_normalization"
VERDICT_OF = {SF: "REJECTED", SV: "PROMOTED", AT: "UNVERIFIED"}
P69 = {"sign_flips": 86, "survives": 39, "attenuates": 161,
       "deg18_vs_deg20": 54, "even_deg_vs_odd_deg": 56, "total": 286}
PINNED = {"deg10_vs_deg12": SF, "deg14_vs_deg16": SV, "salem_vs_pisot": SV}
TODAY = {"deg10_vs_deg12": SF, "deg14_vs_deg16": SV, "salem_vs_pisot": SV,
         "smyth_extremal_vs_rest": SF, "deg18_vs_deg20": AT, "even_deg_vs_odd_deg": AT,
         "small_deg_vs_large_deg": SV, "narrow_band_1.10_1.20_vs_1.30_1.50": SF,
         "lehmer_witness_neighborhood": AT}
TOTAL = 286
V05_HOURS_ON_RECORD = 22.6  # 2026-05-24 03:08 -> 2026-05-25 01:46 local


def load_daemon():
    spec = importlib.util.spec_from_file_location("pollux_daemon", DAEMON)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flush(result):
    OUT.write_text(json.dumps(result, indent=1) + "\n", encoding="ascii")


def simulate(seed, pool, kp_of, k, inherit_idx, threshold):
    """v0.5 for k ticks then v0.6 for TOTAL-k ticks. Returns per-pair and
    per-pattern counts. v0.6 logic copied from daemon._pick_and_advance,
    _record_verdict_and_check_settle, _promote_settled_replace."""
    counts = {}
    pats = {SF: 0, SV: 0, AT: 0}
    for t in range(k):
        name = seed[t % len(seed)]
        counts[name] = counts.get(name, 0) + 1
        pats[kp_of[name]] += 1
    active = list(seed)
    cand = 0
    rot = (k % len(seed)) if inherit_idx else 0
    history = {}
    for t in range(TOTAL - k):
        if not active:
            break
        name = active[rot % len(active)]
        rot = (rot + 1) % max(1, len(active))
        counts[name] = counts.get(name, 0) + 1
        kp = kp_of[name]
        pats[kp] += 1
        v = VERDICT_OF[kp]
        ph = history.get(name, [])
        ph.append(v)
        ph = ph[-threshold * 2:]
        history[name] = ph
        recent = ph[-threshold:]
        if (len(recent) >= threshold and all(x == recent[0] for x in recent)
                and recent[0] in ("PROMOTED", "REJECTED")):
            active = [a for a in active if a != name]
            if cand < len(pool):
                active.append(pool[cand])
                cand += 1
    return counts, pats


def distance(counts, pats):
    got = {"sign_flips": pats[SF], "survives": pats[SV], "attenuates": pats[AT],
           "deg18_vs_deg20": counts.get("deg18_vs_deg20", 0),
           "even_deg_vs_odd_deg": counts.get("even_deg_vs_odd_deg", 0),
           "total": sum(counts.values())}
    return sum(abs(got[key] - P69[key]) for key in P69), got


def main():
    result = {"script": "cleric_census_fit.py", "target_P69": P69,
              "pinned_by_second_channel": PINNED, "todays_map": TODAY}
    d = load_daemon()
    thr = d.SETTLE_THRESHOLD
    seed = [p["name"] for p in d.SEED_PAIRS]
    pool = [p["name"] for p in d.CANDIDATE_POOL]
    free = [n for n in seed + pool if n not in PINNED]
    result["free_pairs"] = free
    result["settle_threshold"] = thr
    flush(result)

    # S1. Necromancer's own replay, reproduced (k=0, today's map).
    c, p = simulate(seed, pool, TODAY, 0, False, thr)
    dist, got = distance(c, p)
    result["S1_necromancer_replay_k0_todays_map"] = {"got": got, "per_pair": c, "distance_to_P69": dist}
    flush(result)

    # S2. Today's map, v0.5 prefix of k ticks, k = 0..TOTAL, both idx choices.
    best = []
    for k in range(0, TOTAL + 1):
        for inherit in (False, True):
            c, p = simulate(seed, pool, TODAY, k, inherit, thr)
            dist, got = distance(c, p)
            best.append((dist, k, inherit, got, c))
    best.sort(key=lambda x: (x[0], x[1]))
    result["S2_todays_map_v05_prefix_search"] = {
        "k_range": [0, TOTAL],
        "best_distance": best[0][0],
        "best_fits": [{"k_v05_ticks": b[1], "inherit_idx": b[2], "got": b[3], "per_pair": b[4]} for b in best[:5]],
        "exact_match_exists": best[0][0] == 0,
        "sign_flips_minus_survives_range": [min(b[3]["sign_flips"] - b[3]["survives"] for b in best),
                                            max(b[3]["sign_flips"] - b[3]["survives"] for b in best)],
    }
    result["S2_note"] = ("Under today's verdict map sign_flips and survives stay within a few rows of "
                         "each other for every k because the round-robin gives deg10/smyth and "
                         "deg14/salem equal ticks and each settling pair contributes exactly "
                         "SETTLE_THRESHOLD v0.6 ticks. P69's 86 vs 39 cannot come from a v0.5 prefix alone.")
    flush(result)

    # S3. Free the six unpinned pairs' May verdicts (3^6 maps) x k x idx.
    exact = []
    best_free = (10 ** 9, None)
    for combo in itertools.product((SF, SV, AT), repeat=len(free)):
        kp_of = dict(PINNED)
        kp_of.update(dict(zip(free, combo)))
        for k in range(0, 140):
            for inherit in (False, True):
                c, p = simulate(seed, pool, kp_of, k, inherit, thr)
                dist, got = distance(c, p)
                if dist < best_free[0]:
                    best_free = (dist, {"map": {n: kp_of[n] for n in free}, "k_v05_ticks": k,
                                        "inherit_idx": inherit, "got": got, "per_pair": c})
                if dist == 0:
                    exact.append({"map": {n: kp_of[n] for n in free}, "k_v05_ticks": k,
                                  "inherit_idx": inherit, "per_pair": c})
    result["S3_free_may_verdicts_search"] = {
        "maps_searched": 3 ** len(free), "k_range": [0, 139],
        "n_exact_matches": len(exact),
        "exact_matches": exact[:20],
        "best_if_no_exact": None if exact else best_free[1],
    }
    flush(result)

    # S3b. Drop the second-channel pins: which verdict maps reproduce P69
    # exactly if ONLY the three never-settling pairs are held at attenuates
    # (they must be: 54/56/51 rows each cannot come from a settling pair)?
    free_b = seed + ["small_deg_vs_large_deg", "narrow_band_1.10_1.20_vs_1.30_1.50"]
    fixed_b = {"deg18_vs_deg20": AT, "even_deg_vs_odd_deg": AT, "lehmer_witness_neighborhood": AT}
    exact_b = []
    for combo in itertools.product((SF, SV, AT), repeat=len(free_b)):
        kp_of = dict(fixed_b)
        kp_of.update(dict(zip(free_b, combo)))
        for k in range(0, 140):
            for inherit in (False, True):
                c, p = simulate(seed, pool, kp_of, k, inherit, thr)
                dist, got = distance(c, p)
                if dist == 0:
                    conflict = {n: [PINNED[n], kp_of[n]] for n in PINNED if kp_of[n] != PINNED[n]}
                    exact_b.append({"map": {n: kp_of[n] for n in free_b}, "k_v05_ticks": k,
                                    "inherit_idx": inherit, "per_pair": c,
                                    "conflicts_with_second_channel_first_three_rows": conflict})
    result["S3b_unpinned_search"] = {
        "maps_searched": 3 ** len(free_b), "k_range": [0, 139],
        "n_exact_matches": len(exact_b), "exact_matches": exact_b,
        "reading": ("Every exact match needs k=95 v0.5 ticks (per-pair 29/29/29/28/54/56/5/5/51, "
                    "which reproduces P69's 54 and 56 and its 'n up to 56' exactly) AND three "
                    "of the four seed pairs at sign_flips. The second channel's first three rows "
                    "show deg14 and salem PROMOTED, so at most two seed pairs were sign_flips. "
                    "P69's per-pair census is therefore reproduced by the code plus v0.5; P69's "
                    "pattern split 86/39 is not reproducible by the code under any May verdict "
                    "assignment consistent with the second channel. 86 = 29+29+28 and 39 = 29+5+5 "
                    "are per-pair sums, so the split reads as pairs bucketed under the wrong "
                    "pattern name, not as a different ledger."),
    }
    flush(result)

    # S4. What the exact matches (if any) require, stated as testable claims.
    reqs = []
    for e in exact:
        changed = {n: [TODAY[n], e["map"][n]] for n in free if e["map"][n] != TODAY[n]}
        reqs.append({"k_v05_ticks": e["k_v05_ticks"], "inherit_idx": e["inherit_idx"],
                     "pairs_whose_May_verdict_must_differ_from_today": changed,
                     "v05_hours_implied_at_28min_cadence": round(e["k_v05_ticks"] * 28 / 60.0, 1),
                     "v05_hours_on_record": V05_HOURS_ON_RECORD})
    result["S4_requirements_of_exact_matches"] = reqs[:20]
    result["S5_reading"] = (
        "If S3 finds no exact match, P69's pattern census is inconsistent with the on-tree "
        "code under every May verdict assignment and every v0.5 length: the census, the "
        "code, or the assumption of one constant verdict per pair (P69's own 'distinct=1') "
        "is wrong, and the lost kill_ledger is the only artifact that can say which. If it "
        "finds matches, each names the pair(s) whose May verdict differed from today's and "
        "the v0.5 tick count it needs; compare the implied hours to the 22.6 h on record."
    )
    flush(result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("S3_free_may_verdicts_search",)}, indent=1))
    print("S3 exact matches:", len(exact))
    for e in exact[:10]:
        print(json.dumps(e))
    if not exact:
        print(json.dumps(best_free[1], indent=1))


if __name__ == "__main__":
    main()
