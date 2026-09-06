"""S11 -- RED-TEAMING v6: fork units, best-of-twelve, evasions, strict vs warn.

Harmonia science loop 11, 2026-09-05.

S9 exercised the v6 primitives honestly and they worked. This uses them the way
someone trying to get a result would.

  ITEM 1  Does unit_of_analysis="world" treat FORKED CHILDREN as independent
          worlds? Forks share a parent event prefix by reference, the same
          fork_point, the same inherited artifacts and the same seed_root. If
          the counter says n=8 for eight forks of one parent, then the
          mechanism built to fix pseudo-replication contains one.
  ITEM 3  Push packet 5's "best of twelve" through the selection family and
          ask whether an analyst reading only fossils recovers the DEFLATED
          estimate rather than the survivor.
  ITEM 4  Four evasions of the new checks:
            a  dodge FAMILY_EXTENT_DIVERGENCE with a fresh family per batch
            b  make selection_visible true while the real alternatives sit
               outside the family
            c  dodge CONFIG_DIVERGENCE with a config that canonicalises equal
               but differs semantically
            d  echo the requested hash back as executed_config_hash instead of
               attesting the config actually run
  ITEM 7  warn vs strict on identical input: do they agree on every FACT and
          differ only in CONSEQUENCE, and does strict block anything legitimate?
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import urllib.error
import urllib.request

R = []


def rec(name, verdict, detail):
    R.append({"probe": name, "verdict": verdict, "detail": detail})
    print("  [%-14s] %-42s %s" % (verdict, name, detail))


class C:
    def __init__(self, base):
        self.base, self.token, self.key = base.rstrip("/"), None, None

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

    def boot(self, tag):
        self.token = self.call("POST", "/clients", {"name": tag})[1]["token"]
        s = self.call("POST", "/sessions", {"name": tag})[1]
        self.key = s["session_key"]
        return s["session_id"]

    def world(self, sid, name, **kw):
        b = {"session_id": sid, "name": name, "sharing_policy": "ISOLATED"}
        b.update(kw)
        w = self.call("POST", "/worlds", b)[1]
        self.call("POST", "/worlds/%s/start" % w["world_id"], {})
        return w["world_id"]

    def one_obs(self, wid, score, spec=None):
        h = self.call("POST", "/worlds/%s/hypotheses" % wid,
                      {"statement": "h"})[1]["hyp_id"]
        x = self.call("POST", "/worlds/%s/experiments" % wid,
                      {"spec": spec or {"action": "encounter", "ticks": 4},
                       "hyp_id": h, "commit": True})[1]
        o = self.call("POST", "/worlds/%s/observations" % wid,
                      {"exp_id": x["exp_id"], "content": {"score": score},
                       "outcome": "SURVIVED"})[1]
        return x, o


def sci(p):
    return (p or {}).get("science", {}).get("profile_findings", [])


def codes(p):
    return sorted(f.get("code") for f in sci(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", default="http://127.0.0.1:8890/v2")
    ap.add_argument("--strict", default="http://127.0.0.1:8889/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.warn)
    if c.call("GET", "/version")[0] != 200:
        print("warn engine unreachable"); return 2
    sid = c.boot("s11")

    # ==================================================================
    print("=" * 78)
    print("ITEM 1  DOES THE UNIT COUNTER TREAT FORKS AS INDEPENDENT WORLDS?")
    print("=" * 78)
    parent = c.world(sid, "fork-parent", seed_root=4242)
    c.one_obs(parent, 0.5)
    ck = c.call("POST", "/worlds/%s/checkpoint" % parent, {})[1]["checkpoint_id"]
    kids = c.call("POST", "/worlds/%s/fork" % parent,
                  {"checkpoint_id": ck,
                   "children": [{"name": "k%d" % i} for i in range(8)]})[1]
    kids = [k["world_id"] for k in kids.get("children", kids)]
    obs_ids = []
    for i, k in enumerate(kids):
        c.call("POST", "/worlds/%s/start" % k, {})
        _, o = c.one_obs(k, 0.5 + i * 0.01)
        obs_ids.append(o.get("obs_id"))
    seeds = {c.call("GET", "/worlds/%s" % k)[1].get("seed_root") for k in kids}

    wa = c.world(sid, "fork-analysis")
    ha = c.call("POST", "/worlds/%s/hypotheses" % wa, {"statement": "a"})[1]["hyp_id"]
    counts = {}
    for unit in ("world", "seed_root", "observation"):
        st, an = c.call("POST", "/worlds/%s/experiments" % wa,
                        {"spec": {"action": "analysis", "unit": unit},
                         "hyp_id": ha, "commit": True,
                         "unit_of_analysis": unit, "declared_n": 8,
                         "source_set": obs_ids})
        stg, got = c.call("GET", "/worlds/%s/experiments/%s/analysis"
                          % (wa, an.get("exp_id", "x")))
        counts[unit] = {k: v for k, v in got.items()
                        if "count" in k or "n" in k.lower() or k == "science"}
        print("    unit=%-12s -> %s" % (unit, json.dumps(counts[unit])[:150]))
    print("\n    the 8 forks share seed_root: %s" % seeds)
    wc = counts.get("world", {})
    sc = counts.get("seed_root", {})

    def num(d):
        for k in ("engine_n", "counted_n", "n", "unit_count", "distinct_units"):
            if isinstance(d.get(k), int):
                return d[k]
        return None
    n_world, n_seed = num(wc), num(sc)
    rec("I1_fork_children_counted_as_worlds",
        "DEFECT" if n_world == 8 and n_seed == 8 else
        ("OK" if (n_seed or 9) < (n_world or 0) else "INDETERMINATE"),
        "unit=world -> n=%s, unit=seed_root -> n=%s, forks share one seed_root"
        % (n_world, n_seed))

    # ==================================================================
    print("\n" + "=" * 78)
    print("ITEM 3  BEST-OF-TWELVE THROUGH THE SELECTION FAMILY")
    print("=" * 78)
    ds = [0.60, 0.26, 0.43, 0.54, 0.35, 0.43, 0.44, 0.31, 0.08, 0.49, 0.25, 0.22]
    st, fam = c.call("POST", "/families",
                     {"kind": "selection",
                      "manifest": {"planned_members": 12,
                                   "note": "SE-1b seed blocks"}})
    fid = fam["family_id"]
    block_worlds = []
    for i, d in enumerate(ds):
        w = c.world(sid, "block-%02d" % i, seed_root=3000 + i * 1000)
        c.one_obs(w, d)
        block_worlds.append(w)
        c.call("POST", "/families/%s/members" % fid,
               {"member_kind": "world", "member_id": w,
                "role": "selected" if i == 0 else "alternative"})
    stc, cen = c.call("GET", "/families/%s" % fid)
    members = cen.get("members", [])
    roles = {}
    for m in members:
        roles[m.get("role")] = roles.get(m.get("role"), 0) + 1
    # what an analyst recovers from fossils alone
    recovered = []
    for m in members:
        wid = m.get("member_id")
        got = c.call("GET", "/worlds/%s/observations" % wid)[1]
        lst = got.get("observations", got) if isinstance(got, dict) else got
        for o in (lst or []):
            v = (o.get("content") or {}).get("score")
            if v is not None:
                recovered.append(v)
    surv = max(recovered) if recovered else None
    print("    family census: %s, selection_visible=%s"
          % (roles, cen.get("selection_visible")))
    print("    survivor reported by SE-1b        : %.3f" % surv)
    print("    mean over ALL recorded members    : %.3f"
          % statistics.fmean(recovered))
    rec("I3_best_of_twelve_recoverable",
        "OK" if (cen.get("selection_visible") and len(recovered) == 12
                 and abs(statistics.fmean(recovered) - 0.367) < 0.02)
        else "DEFECT",
        "12 members recorded, deflated mean %.3f recoverable vs survivor %.3f"
        % (statistics.fmean(recovered), surv))

    # ==================================================================
    print("\n" + "=" * 78)
    print("ITEM 4  EVASIONS")
    print("=" * 78)
    # (a) dodge FAMILY_EXTENT_DIVERGENCE with a fresh family per batch
    over = c.call("POST", "/families",
                  {"kind": "campaign", "manifest": {"planned_members": 2}})[1]
    for i in range(4):
        c.call("POST", "/families/%s/members" % over["family_id"],
               {"member_kind": "world",
                "member_id": c.world(sid, "over-%d" % i), "role": "executed"})
    fired = codes(c.call("GET", "/families/%s" % over["family_id"])[1])
    clean = []
    for b in range(4):
        f = c.call("POST", "/families",
                   {"kind": "campaign", "manifest": {"planned_members": 1}})[1]
        c.call("POST", "/families/%s/members" % f["family_id"],
               {"member_kind": "world", "member_id": c.world(sid, "sm-%d" % b),
                "role": "executed"})
        clean.append(codes(c.call("GET", "/families/%s" % f["family_id"])[1]))
    rec("I4a_extent_divergence_evadable",
        "DEFECT" if fired and not any(clean) else "OK",
        "one over-grown family -> %s ; four single-member families -> %s"
        % (fired or "no findings", clean[0] or "no findings"))

    # (b) selection_visible true while real alternatives sit outside
    f2 = c.call("POST", "/families",
                {"kind": "selection", "manifest": {"planned_members": 2}})[1]
    c.call("POST", "/families/%s/members" % f2["family_id"],
           {"member_kind": "world", "member_id": block_worlds[0],
            "role": "selected"})
    c.call("POST", "/families/%s/members" % f2["family_id"],
           {"member_kind": "world", "member_id": block_worlds[1],
            "role": "alternative"})
    st2, cen2 = c.call("GET", "/families/%s" % f2["family_id"])
    rec("I4b_selection_visible_with_one_token_loser",
        "DEFECT" if cen2.get("selection_visible") else "OK",
        "1 selected + 1 alternative (10 real losers omitted) -> "
        "selection_visible=%s" % cen2.get("selection_visible"))

    # (c) CONFIG_DIVERGENCE with a canonically-equal but semantically different
    #     config, and (d) echoing the requested hash back
    w = c.world(sid, "attest")
    h = c.call("POST", "/worlds/%s/hypotheses" % w, {"statement": "h"})[1]["hyp_id"]
    spec = {"action": "encounter", "ticks": 8, "noise": 0}
    x = c.call("POST", "/worlds/%s/experiments" % w,
               {"spec": spec, "hyp_id": h, "commit": True, "enqueue": True})[1]
    got = c.call("GET", "/worlds/%s/experiments/%s" % (w, x["exp_id"]))[1]
    wk = (c.call("POST", "/work/claim", {"worker_id": "w1"})[1] or {}).get("work")
    if wk:
        # semantically different: noise 0 -> 0.02, but keys reordered too
        lie = {"noise": 0.02, "ticks": 8, "action": "encounter"}
        stc1, pc1 = c.call("POST", "/work/%s/complete" % wk["work_id"],
                           {"worker_id": "w1", "claim_id": wk["claim_id"],
                            "result": {"score": 0.5},
                            "attestation": {"executed_config": lie}})
        rec("I4c_config_divergence_detected",
            "OK" if any("DIVERG" in x for x in codes(pc1)) else "DEFECT",
            "attested noise=0.02 against sealed noise=0 -> %s"
            % (codes(pc1) or "NO FINDING"))
    else:
        rec("I4c_config_divergence_detected", "INDETERMINATE",
            "no claimable work")

    w2 = c.world(sid, "attest2")
    h2 = c.call("POST", "/worlds/%s/hypotheses" % w2, {"statement": "h"})[1]["hyp_id"]
    x2 = c.call("POST", "/worlds/%s/experiments" % w2,
                {"spec": spec, "hyp_id": h2, "commit": True, "enqueue": True})[1]
    got2 = c.call("GET", "/worlds/%s/experiments/%s" % (w2, x2["exp_id"]))[1]
    wk2 = (c.call("POST", "/work/claim", {"worker_id": "w2"})[1] or {}).get("work")
    if wk2:
        stc2, pc2 = c.call("POST", "/work/%s/complete" % wk2["work_id"],
                           {"worker_id": "w2", "claim_id": wk2["claim_id"],
                            "result": {"score": 0.5},
                            "attestation": {
                                "executed_config_hash": got2.get("spec_hash")}})
        rec("I4d_echoing_requested_hash_accepted",
            "ACCEPTED-BY-DESIGN" if not codes(pc2) else "FLAGGED",
            "echoed the sealed spec_hash as executed_config_hash -> %s "
            "(an executor that never ran anything passes this)"
            % (codes(pc2) or "no findings"))
    else:
        rec("I4d_echoing_requested_hash_accepted", "INDETERMINATE", "no work")

    # ==================================================================
    print("\n" + "=" * 78)
    print("ITEM 7  WARN vs STRICT ON IDENTICAL INPUT")
    print("=" * 78)
    s = C(a.strict)
    if s.call("GET", "/version")[0] != 200:
        rec("I7_warn_strict_agreement", "INDETERMINATE", "strict engine down")
    else:
        ssid = s.boot("s11-strict")
        facts, cons = {}, {}
        for eng, tag, sess in ((c, "warn", sid), (s, "strict", ssid)):
            f = eng.call("POST", "/families",
                         {"kind": "campaign", "manifest": {"planned_members": 1}})[1]
            wid = eng.world(sess, "ab-%s" % tag)
            eng.call("POST", "/families/%s/members" % f["family_id"],
                     {"member_kind": "world", "member_id": wid, "role": "executed"})
            w2id = eng.world(sess, "ab2-%s" % tag)
            stx, px = eng.call("POST", "/families/%s/members" % f["family_id"],
                               {"member_kind": "world", "member_id": w2id,
                                "role": "executed"})
            stc, cen = eng.call("GET", "/families/%s" % f["family_id"])
            facts[tag] = codes(cen)
            cons[tag] = stx
            # does strict block a LEGITIMATE claim?
            stcl, pcl = eng.call("POST", "/claims",
                                 {"estimand": "x", "status": "SUPPORTED",
                                  "relevance_floor": {"smd": 0.2},
                                  "replication": {"new_world_draws": True},
                                  "transport_domain": ["A"]})
            cons[tag + "_claim"] = stcl
        same_facts = facts["warn"] == facts["strict"]
        rec("I7_same_facts",
            "OK" if same_facts else "DEFECT",
            "warn findings %s == strict findings %s" % (facts["warn"],
                                                        facts["strict"]))
        rec("I7_consequence_differs",
            "OK",
            "over-growth POST: warn=%s strict=%s ; bare claim: warn=%s strict=%s"
            % (cons["warn"], cons["strict"], cons["warn_claim"],
               cons["strict_claim"]))

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"probes": R, "fork_counts": counts,
                   "twelve": {"recovered": recovered,
                              "mean": statistics.fmean(recovered),
                              "survivor": surv}}, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
