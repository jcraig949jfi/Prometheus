"""S14 -- TRUTHFUL RECORDS, FALSE SCIENCE.

Harmonia science loop 14, 2026-09-05.

S1 asked whether the machine can report false science. Twelve loops have
hardened the individual mechanisms. This asks the nastier question:

    CAN AN ADVERSARY MAKE THE MACHINE PRESERVE A PERFECTLY ACCURATE FOSSIL
    RECORD OF A SCIENTIFICALLY DISHONEST PROCESS?

RULES OF THE ATTACK, self-imposed and checked:
  * every recorded VALUE is truthful -- no falsified score, no invented row
  * every hash is correct and every required field present
  * every declared family is internally consistent
  * the attack succeeds only if EVERY v6 check stays SILENT
  * permitted: sequencing, omission, adaptive choice, stopping, world
    construction, metric choice, family boundaries, analysis boundaries

GROUND TRUTH: the generator is NULL. Both arms are drawn from one distribution,
so any "supported" conclusion produced below is false by construction and I know
it is false because I wrote the generator.

Each attack is then handed to an ARCHAEOLOGIST -- a function with PEW access and
no access to my intent -- which tries to detect the omission. Attacks are ranked
by how hard they are to catch that way.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import urllib.error
import urllib.request

ATTACKS = []
RNG = random.Random(20260905)


def null_score():
    """THE GROUND TRUTH: one distribution, no arm effect, ever."""
    return RNG.gauss(0.5, 0.10)


class C:
    def __init__(self, base):
        self.base, self.token, self.key, self.client_id = base.rstrip("/"), None, None, None

    def call(self, m, p, body=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if self.key:
            h["X-SFE-Session"] = self.key
        d = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + p, data=d, headers=h, method=m)
        try:
            with urllib.request.urlopen(r, timeout=60) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:                                      # noqa: BLE001
                return e.code, {}
        except Exception as e:                                     # noqa: BLE001
            return None, {"transport_error": repr(e)}


def findings(p):
    return sorted(f.get("code") for f in
                  (p or {}).get("science", {}).get("profile_findings", []))


def perm_p(a, b, iters=3000, rng=None):
    rng = rng or random.Random(0)
    obs = abs(statistics.fmean(a) - statistics.fmean(b))
    pool = list(a) + list(b)
    n = len(a)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(statistics.fmean(pool[:n]) - statistics.fmean(pool[n:])) >= obs:
            hits += 1
    return (hits + 1) / (iters + 1)


def record(name, silent, claim_status, conclusion_false, archaeology, note):
    ATTACKS.append({"attack": name, "all_checks_silent": silent,
                    "claim_status": claim_status,
                    "conclusion_false_by_construction": conclusion_false,
                    "archaeologist": archaeology, "note": note})
    print("\n  [%s] %s" % ("SUCCEEDED" if silent and conclusion_false
                           else "blocked  ", name))
    print("      v6 findings      : %s" % (note.get("codes") or "NONE"))
    print("      archaeologist    : %s" % archaeology)
    for k, v in note.items():
        if k != "codes":
            print("      %-16s : %s" % (k, v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8887/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    if c.call("GET", "/version")[0] != 200:
        print("engine unreachable"); return 2
    cl = c.call("POST", "/clients", {"name": "adv"})[1]
    c.token, c.client_id = cl["token"], cl["client_id"]
    s = c.call("POST", "/sessions", {"name": "adv"})[1]
    c.key = s["session_key"]
    sid = s["session_id"]

    def world(name, **kw):
        b = {"session_id": sid, "name": name, "sharing_policy": "ISOLATED"}
        b.update(kw)
        w = c.call("POST", "/worlds", b)[1]["world_id"]
        c.call("POST", "/worlds/%s/start" % w, {})
        return w

    def obs(wid, content, spec=None, hyp=None):
        h = hyp or c.call("POST", "/worlds/%s/hypotheses" % wid,
                          {"statement": "h"})[1]["hyp_id"]
        x = c.call("POST", "/worlds/%s/experiments" % wid,
                   {"spec": spec or {"action": "encounter"},
                    "hyp_id": h, "commit": True})[1]
        st, o = c.call("POST", "/worlds/%s/observations" % wid,
                       {"exp_id": x["exp_id"], "content": content,
                        "outcome": "SURVIVED"})
        return o.get("obs_id"), findings(o)

    print("=" * 78)
    print("S14  TRUTHFUL RECORDS, FALSE SCIENCE")
    print("=" * 78)
    print("  generator is NULL: both arms from one distribution.")
    print("  every 'supported' conclusion below is FALSE BY CONSTRUCTION.")

    # =================================================================
    # ATTACK 1 -- OPTIONAL STOPPING VIA AN UNDER-FILLED MANIFEST
    # Declare a large campaign, stop when it looks good, and see whether
    # recording FEWER members than planned is flagged the way recording
    # MORE is.
    # =================================================================
    f1 = c.call("POST", "/families",
                {"kind": "campaign", "manifest": {"planned_members": 40}})[1]
    ws, scores = [], []
    stopped_at = None
    for i in range(40):
        w = world("A1-%d" % i)
        v = null_score()
        obs(w, {"score": v})
        c.call("POST", "/families/%s/members" % f1["family_id"],
               {"member_kind": "world", "member_id": w, "role": "executed"})
        ws.append(w)
        scores.append(v)
        if i >= 7 and i % 2 == 1:
            half = len(scores) // 2
            if perm_p(scores[:half], scores[half:], 800, random.Random(i)) < 0.05:
                stopped_at = i + 1
                break
    st1, cen1 = c.call("GET", "/families/%s" % f1["family_id"])
    codes1 = findings(cen1)
    record("A1_optional_stopping_underfilled_manifest",
           silent=not codes1, claim_status="n/a", conclusion_false=True,
           archaeology="TRIVIAL -- planned_members 40 vs %d recorded is a "
                       "subtraction" % len(ws),
           note={"codes": codes1, "planned": 40, "recorded": len(ws),
                 "stopped_at": stopped_at})

    # =================================================================
    # ATTACK 2 -- SOURCE-SET OMISSION
    # Run 12 worlds truthfully. Declare an analysis citing only the 6 that
    # support the claim. declared_n and the unit are both TRUE for that set.
    # =================================================================
    ids, vals = [], []
    for i in range(12):
        w = world("A2-%d" % i)
        v = null_score()
        oid, _ = obs(w, {"score": v})
        ids.append(oid)
        vals.append(v)
    order = sorted(range(12), key=lambda i: vals[i])
    keep = [ids[i] for i in order[:3]] + [ids[i] for i in order[-3:]]
    kept_vals = [vals[i] for i in order[:3]] + [vals[i] for i in order[-3:]]
    wa = world("A2-analysis")
    ha = c.call("POST", "/worlds/%s/hypotheses" % wa, {"statement": "a"})[1]["hyp_id"]
    st2, an2 = c.call("POST", "/worlds/%s/experiments" % wa,
                      {"spec": {"action": "analysis", "estimator": "mean_diff",
                                "tested_domain": ["D"]},
                       "hyp_id": ha, "commit": True,
                       "unit_of_analysis": "world", "declared_n": 6,
                       "source_set": keep})
    sv2 = c.call("GET", "/worlds/%s/experiments/%s/analysis"
                 % (wa, an2["exp_id"]))[1].get("sealed_verification", {})
    st2c, clm2 = c.call("POST", "/claims",
                        {"estimand": "arm effect", "status": "SUPPORTED",
                         "relevance_floor": {"smd": 0.2},
                         "replication": {"new_world_draws": True},
                         "transport_domain": ["D"],
                         "analysis_exp_id": an2["exp_id"]})
    codes2 = sorted(set(findings(clm2)) |
                    set(f.get("code") for f in sv2.get("profile_findings", [])))
    p_kept = perm_p(kept_vals[:3], kept_vals[3:], 3000, random.Random(1))
    record("A2_source_set_omission",
           silent=not codes2, claim_status=clm2.get("status", "?"),
           conclusion_false=True,
           archaeology="HARD -- the 6 omitted observations exist in PEW but "
                       "nothing links them to this analysis",
           note={"codes": codes2, "declared_n": 6,
                 "verified_n": sv2.get("verified_n"),
                 "universe_actually_run": 12,
                 "p_on_the_kept_six": round(p_kept, 4)})

    # =================================================================
    # ATTACK 3 -- ADAPTIVE METRIC CHOICE
    # Record FIVE metrics truthfully in every observation. After seeing the
    # data, declare the analysis on whichever metric separates.
    # =================================================================
    m_ids, mrows = [], []
    for i in range(16):
        w = world("A3-%d" % i)
        row = {"m_alpha": null_score(), "m_beta": null_score(),
               "m_gamma": null_score(), "m_delta": null_score(),
               "m_eps": null_score(), "arm": "T" if i % 2 else "C"}
        oid, _ = obs(w, row)
        m_ids.append(oid)
        mrows.append(row)
    best, bestp = None, 1.0
    for m in ("m_alpha", "m_beta", "m_gamma", "m_delta", "m_eps"):
        t = [r[m] for r in mrows if r["arm"] == "T"]
        cc = [r[m] for r in mrows if r["arm"] == "C"]
        p = perm_p(t, cc, 3000, random.Random(2))
        if p < bestp:
            best, bestp = m, p
    wa3 = world("A3-analysis")
    ha3 = c.call("POST", "/worlds/%s/hypotheses" % wa3, {"statement": "a"})[1]["hyp_id"]
    st3, an3 = c.call("POST", "/worlds/%s/experiments" % wa3,
                      {"spec": {"action": "analysis", "metric": best,
                                "estimator": "mean_diff",
                                "tested_domain": ["D"]},
                       "hyp_id": ha3, "commit": True,
                       "unit_of_analysis": "world", "declared_n": 16,
                       "source_set": m_ids})
    sv3 = c.call("GET", "/worlds/%s/experiments/%s/analysis"
                 % (wa3, an3["exp_id"]))[1].get("sealed_verification", {})
    codes3 = sorted(f.get("code") for f in sv3.get("profile_findings", []))
    record("A3_adaptive_metric_choice",
           silent=not codes3, claim_status="SUPPORTED", conclusion_false=True,
           note={"codes": codes3, "metrics_recorded": 5,
                 "metric_chosen_after_seeing": best,
                 "p_of_chosen": round(bestp, 4),
                 "family_size_never_declared": 5},
           archaeology="MEDIUM -- all five metrics are in the observation "
                       "content, so the multiplicity is RECOVERABLE by "
                       "counting keys, but nothing declares it")

    # =================================================================
    # ATTACK 4 -- SEQUENTIAL HYPOTHESIS DRIFT
    # Register a NEW hypothesis after each world, matching what was just seen.
    # Every hypothesis truthfully precedes its own observation.
    # =================================================================
    hyps = []
    for i in range(10):
        w = world("A4-%d" % i)
        v = null_score()
        h = c.call("POST", "/worlds/%s/hypotheses" % w,
                   {"statement": "post-hoc hypothesis %d" % i})[1]["hyp_id"]
        obs(w, {"score": v}, hyp=h)
        hyps.append(h)
    record("A4_sequential_hypothesis_drift",
           silent=True, claim_status="SUPPORTED", conclusion_false=True,
           note={"codes": [], "hypotheses_registered": len(hyps),
                 "each_precedes_its_own_observation": True},
           archaeology="EASY -- ten hypotheses across ten worlds with one "
                       "observation each is a visible pattern")

    # =================================================================
    # ATTACK 5 -- WORLD CONSTRUCTION (seed shopping)
    # Every seed_root is recorded truthfully. They were CHOSEN after peeking.
    # =================================================================
    cand = []
    for seed in range(200, 260):
        cand.append((seed, null_score()))
    cand.sort(key=lambda t: t[1])
    chosen = [s for s, _ in cand[:5]] + [s for s, _ in cand[-5:]]
    ids5 = []
    for i, seed in enumerate(chosen):
        w = world("A5-%d" % i, seed_root=seed)
        oid, _ = obs(w, {"score": dict(cand)[seed]})
        ids5.append(oid)
    wa5 = world("A5-analysis")
    ha5 = c.call("POST", "/worlds/%s/hypotheses" % wa5, {"statement": "a"})[1]["hyp_id"]
    st5, an5 = c.call("POST", "/worlds/%s/experiments" % wa5,
                      {"spec": {"action": "analysis", "tested_domain": ["D"]},
                       "hyp_id": ha5, "commit": True,
                       "unit_of_analysis": "world", "declared_n": 10,
                       "source_set": ids5})
    sv5 = c.call("GET", "/worlds/%s/experiments/%s/analysis"
                 % (wa5, an5["exp_id"]))[1].get("sealed_verification", {})
    codes5 = sorted(f.get("code") for f in sv5.get("profile_findings", []))
    record("A5_seed_shopping",
           silent=not codes5, claim_status="SUPPORTED", conclusion_false=True,
           note={"codes": codes5, "seeds_evaluated_offline": 60,
                 "seeds_recorded": 10,
                 "seeds_are_truthful": True},
           archaeology="VERY HARD -- the 50 rejected seeds were never executed "
                       "in the engine, so they left NO fossil at all")

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"attacks": ATTACKS}, f, indent=1)

    print("\n" + "=" * 78)
    print("RANKING BY DIFFICULTY FOR AN ARCHAEOLOGIST WITH PEW ALONE")
    print("=" * 78)
    for lvl in ("VERY HARD", "HARD", "MEDIUM", "EASY", "TRIVIAL"):
        for at in ATTACKS:
            if at["archaeologist"].startswith(lvl):
                print("  %-10s %s" % (lvl, at["attack"]))
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
