"""S13 / T-B -- CAN A SELECTION OPPORTUNITY SET BE DERIVED FROM THE SUBSTRATE?

Harmonia science loop 13, 2026-09-05.

R12 established that self-declared scope cannot certify its own completeness.
4a and 4b were the same exploit: the claimant supplies the set against which
their selection is audited, so consistency INSIDE the declared family can be
verified and completeness OF the family cannot.

THIS EXPERIMENT DOES NOT BUILD A FEATURE. It asks whether the substrate holds
enough information to propose a CANDIDATE UNIVERSE that is useful -- high
recall on real alternatives without drowning in false positives -- and where
the claimant's control simply relocates.

The target primitive is RECONCILIATION, not replacement:
    declared_family    what the claimant says belongs together
    candidate_family   what substrate evidence says plausibly belongs together
and the engine audits the RELATIONSHIP, saying "you declared 2, I can see 12
that plausibly belong to the same selection opportunity, explain the other 10."
The claimant may hold grouping knowledge lineage does not; the engine must not
decide that every sibling world is one hypothesis test.

=============================================================================
PRE-REGISTRATION. THE RULES BELOW ARE FROZEN BEFORE ANY SCORE IS COMPUTED.
The scoring function is also frozen here. No rule is tuned to reconstruct the
known twelve; a tuned time window would make T-B itself a selection experiment,
which is the failure it exists to study.
=============================================================================
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request

# --------------------------------------------------------------------------
# FROZEN MANIFEST
# --------------------------------------------------------------------------
MANIFEST = {
    "experiment": "S13 / T-B",
    "question": "does the substrate support a useful CANDIDATE selection "
                "universe, and where does claimant control relocate?",
    "rules_frozen_before_scoring": [
        "R_LIN     same parent world (fork siblings)",
        "R_SES     same session",
        "R_SEED    same seed_root",
        "R_SPEC    same experiment spec_hash",
        "R_CLIENT  same client",
        "R_TIME_10 created within 10s of the survivor",
        "R_TIME_60 created within 60s of the survivor",
        "R_SPEC_SES   same spec_hash AND same session",
        "R_LIN_OR_SPEC same parent OR same spec_hash",
        "R_CLIENT_SPEC_TIME same client AND same spec_hash AND within 60s",
    ],
    "scoring": "recall = |candidate AND truth| / |truth| ; "
               "precision = |candidate AND truth| / |candidate| ; "
               "both reported, neither optimised, no rule adjusted after "
               "seeing a score",
    "constructions": [
        "C1 twelve fork siblings, best one reported -> infer all 12",
        "C2 the same twelve split into 12 singleton families -> still 12",
        "C3 two genuinely separate experiments from one parent -> do NOT merge",
        "C4 a repeat of the same experiment later -> separable",
        "C5 two interleaved A/B campaigns sharing lineage -> do not collapse",
        "C6 debugging/calibration forks -> not selection alternatives",
        "C7 the same experiment across separate sessions -> is the session "
        "boundary meaningful or another evasion?",
        "C8 adversary uses a FRESH PARENT for every trial -> does derivation "
        "survive, or does control merely relocate?",
    ],
    "prohibited": "tuning any window, threshold or rule after observing a "
                  "score; adding a rule after seeing the constructions",
}
MANIFEST_HASH = hashlib.sha256(
    json.dumps(MANIFEST, sort_keys=True).encode()).hexdigest()


# --------------------------------------------------------------------------
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


WORLDS = {}          # world_id -> substrate facts, as an auditor would see them


def observe_world(c, wid, session_id, client_id, parent=None):
    got = c.call("GET", "/worlds/%s" % wid)[1]
    WORLDS[wid] = {"world_id": wid,
                   "parent": got.get("parent_world_id", parent),
                   "session": session_id, "client": client_id,
                   "seed_root": got.get("seed_root"),
                   "created_ts": got.get("created_ts") or time.time(),
                   "spec_hash": None, "name": got.get("name")}
    return WORLDS[wid]


def run_experiment(c, wid, spec):
    h = c.call("POST", "/worlds/%s/hypotheses" % wid, {"statement": "h"})[1]
    x = c.call("POST", "/worlds/%s/experiments" % wid,
               {"spec": spec, "hyp_id": h["hyp_id"], "commit": True})[1]
    got = c.call("GET", "/worlds/%s/experiments/%s" % (wid, x["exp_id"]))[1]
    WORLDS[wid]["spec_hash"] = got.get("spec_hash")
    c.call("POST", "/worlds/%s/observations" % wid,
           {"exp_id": x["exp_id"], "content": {"score": 0.5},
            "outcome": "SURVIVED"})
    return got.get("spec_hash")


# --------------------------------------------------------------------------
# THE FROZEN RULES. Each maps a survivor world to a candidate universe.
# --------------------------------------------------------------------------
def rules(survivor, pool):
    s = WORLDS[survivor]

    def near(w, sec):
        return abs(WORLDS[w]["created_ts"] - s["created_ts"]) <= sec

    return {
        "R_LIN": {w for w in pool
                  if WORLDS[w]["parent"] and WORLDS[w]["parent"] == s["parent"]}
                 | ({survivor} if s["parent"] else set()),
        "R_SES": {w for w in pool if WORLDS[w]["session"] == s["session"]},
        "R_SEED": {w for w in pool if WORLDS[w]["seed_root"] == s["seed_root"]},
        "R_SPEC": {w for w in pool if WORLDS[w]["spec_hash"] == s["spec_hash"]},
        "R_CLIENT": {w for w in pool if WORLDS[w]["client"] == s["client"]},
        "R_TIME_10": {w for w in pool if near(w, 10)},
        "R_TIME_60": {w for w in pool if near(w, 60)},
        "R_SPEC_SES": {w for w in pool
                       if WORLDS[w]["spec_hash"] == s["spec_hash"]
                       and WORLDS[w]["session"] == s["session"]},
        "R_LIN_OR_SPEC": {w for w in pool
                          if (WORLDS[w]["parent"] and
                              WORLDS[w]["parent"] == s["parent"])
                          or WORLDS[w]["spec_hash"] == s["spec_hash"]},
        "R_CLIENT_SPEC_TIME": {w for w in pool
                               if WORLDS[w]["client"] == s["client"]
                               and WORLDS[w]["spec_hash"] == s["spec_hash"]
                               and near(w, 60)},
    }


def score(cand, truth, pool):
    inter = len(cand & truth)
    recall = inter / len(truth) if truth else float("nan")
    prec = inter / len(cand) if cand else float("nan")
    return recall, prec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8888/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    print("=" * 78)
    print("S13 / T-B  DERIVING A CANDIDATE SELECTION UNIVERSE")
    print("=" * 78)
    print("  frozen manifest sha256: %s" % MANIFEST_HASH[:32])
    print("  %d rules and %d constructions declared BEFORE any score\n"
          % (len(MANIFEST["rules_frozen_before_scoring"]),
             len(MANIFEST["constructions"])))

    c = C(a.base)
    if c.call("GET", "/version")[0] != 200:
        print("engine unreachable"); return 2
    cl = c.call("POST", "/clients", {"name": "tb-main"})[1]
    c.token, client_id = cl["token"], cl["client_id"]
    s1 = c.call("POST", "/sessions", {"name": "tb-s1"})[1]
    c.key = s1["session_key"]
    S1 = s1["session_id"]

    def world(name, sid, **kw):
        b = {"session_id": sid, "name": name, "sharing_policy": "ISOLATED"}
        b.update(kw)
        w = c.call("POST", "/worlds", b)[1]["world_id"]
        c.call("POST", "/worlds/%s/start" % w, {})
        observe_world(c, w, sid, client_id)
        return w

    def fork(parent, n, prefix):
        ck = c.call("POST", "/worlds/%s/checkpoint" % parent, {})[1]["checkpoint_id"]
        kids = c.call("POST", "/worlds/%s/fork" % parent,
                      {"checkpoint_id": ck,
                       "children": [{"name": "%s-%d" % (prefix, i)}
                                    for i in range(n)]})[1]
        out = []
        for k in kids.get("children", kids):
            wid = k["world_id"]
            c.call("POST", "/worlds/%s/start" % wid, {})
            observe_world(c, wid, S1, client_id, parent=parent)
            WORLDS[wid]["parent"] = parent
            out.append(wid)
        return out

    constructions = {}

    # ---- C1: twelve fork siblings, best one reported --------------------
    p1 = world("C1-parent", S1, seed_root=4242)
    run_experiment(c, p1, {"action": "encounter", "arm": "C1"})
    c1 = fork(p1, 12, "C1")
    for w in c1:
        run_experiment(c, w, {"action": "encounter", "arm": "C1"})
    constructions["C1_twelve_siblings"] = {"survivor": c1[0],
                                           "truth": set(c1),
                                           "desired": "infer all 12"}

    # ---- C2: the same twelve, split into 12 singleton families ----------
    for i, w in enumerate(c1):
        f = c.call("POST", "/families",
                   {"kind": "selection", "manifest": {"planned_members": 1}})[1]
        c.call("POST", "/families/%s/members" % f["family_id"],
               {"member_kind": "world", "member_id": w, "role": "selected"})
    constructions["C2_twelve_singleton_families"] = {
        "survivor": c1[0], "truth": set(c1),
        "desired": "still infer the common universe"}

    # ---- C3: two genuinely separate experiments from one parent ---------
    p3 = world("C3-parent", S1, seed_root=71)
    run_experiment(c, p3, {"action": "encounter", "arm": "C3"})
    c3a = fork(p3, 4, "C3a")
    c3b = fork(p3, 4, "C3b")
    for w in c3a:
        run_experiment(c, w, {"action": "encounter", "question": "alpha"})
    for w in c3b:
        run_experiment(c, w, {"action": "encounter", "question": "beta"})
    constructions["C3_two_separate_from_one_parent"] = {
        "survivor": c3a[0], "truth": set(c3a),
        "desired": "do NOT merge the beta arm"}

    # ---- C4: a repeat of the same experiment later ----------------------
    p4 = world("C4-parent", S1, seed_root=88)
    run_experiment(c, p4, {"action": "encounter", "arm": "C4"})
    c4_first = fork(p4, 4, "C4first")
    for w in c4_first:
        run_experiment(c, w, {"action": "encounter", "arm": "C4"})
    time.sleep(2)
    c4_later = fork(p4, 4, "C4later")
    for w in c4_later:
        run_experiment(c, w, {"action": "encounter", "arm": "C4"})
    constructions["C4_repeat_later"] = {
        "survivor": c4_first[0], "truth": set(c4_first),
        "desired": "separable from the later repeat"}

    # ---- C5: two interleaved A/B campaigns sharing lineage --------------
    p5 = world("C5-parent", S1, seed_root=99)
    run_experiment(c, p5, {"action": "encounter", "arm": "C5"})
    c5 = fork(p5, 8, "C5")
    c5A, c5B = c5[0::2], c5[1::2]
    for w in c5A:
        run_experiment(c, w, {"action": "encounter", "campaign": "A"})
    for w in c5B:
        run_experiment(c, w, {"action": "encounter", "campaign": "B"})
    constructions["C5_interleaved_campaigns"] = {
        "survivor": c5A[0], "truth": set(c5A),
        "desired": "do not collapse A and B"}

    # ---- C6: debugging / calibration forks ------------------------------
    p6 = world("C6-parent", S1, seed_root=123)
    run_experiment(c, p6, {"action": "encounter", "arm": "C6"})
    c6_real = fork(p6, 4, "C6real")
    c6_debug = fork(p6, 3, "C6debug")
    for w in c6_real:
        run_experiment(c, w, {"action": "encounter", "purpose": "experiment"})
    for w in c6_debug:
        run_experiment(c, w, {"action": "encounter", "purpose": "calibration"})
    constructions["C6_debug_forks"] = {
        "survivor": c6_real[0], "truth": set(c6_real),
        "desired": "calibration forks are not alternatives"}

    # ---- C7: the same experiment across separate sessions ---------------
    s2 = c.call("POST", "/sessions", {"name": "tb-s2"})[1]
    key1 = c.key
    c.key = s2["session_key"]
    S2 = s2["session_id"]
    c7b = []
    for i in range(4):
        w = world("C7-s2-%d" % i, S2, seed_root=555)
        run_experiment(c, w, {"action": "encounter", "arm": "C7"})
        c7b.append(w)
    c.key = key1
    c7a = []
    for i in range(4):
        w = world("C7-s1-%d" % i, S1, seed_root=555)
        run_experiment(c, w, {"action": "encounter", "arm": "C7"})
        c7a.append(w)
    constructions["C7_across_sessions"] = {
        "survivor": c7a[0], "truth": set(c7a) | set(c7b),
        "desired": "is the session boundary meaningful, or an evasion?"}

    # ---- C8: adversary uses a FRESH PARENT for every trial ---------------
    c8 = []
    for i in range(12):
        p = world("C8-parent-%d" % i, S1, seed_root=1000 + i)
        run_experiment(c, p, {"action": "encounter", "arm": "C8"})
        kid = fork(p, 1, "C8-%d" % i)[0]
        run_experiment(c, kid, {"action": "encounter", "arm": "C8"})
        c8.append(kid)
    constructions["C8_adversary_fresh_parent"] = {
        "survivor": c8[0], "truth": set(c8),
        "desired": "does derivation survive, or does control relocate?"}

    # ==================================================================
    pool = set(WORLDS)
    print("  substrate pool: %d worlds\n" % len(pool))
    results = {}
    for cname, cfg in constructions.items():
        rs = rules(cfg["survivor"], pool)
        row = {}
        for rname, cand in rs.items():
            rec, prec = score(cand, cfg["truth"], pool)
            row[rname] = {"recall": rec, "precision": prec, "size": len(cand)}
        results[cname] = {"truth_size": len(cfg["truth"]),
                          "desired": cfg["desired"], "rules": row}
        print("  %s  (truth=%d, %s)"
              % (cname, len(cfg["truth"]), cfg["desired"]))
        print("      rule                 recall  prec   size")
        for rname in ("R_LIN", "R_SES", "R_SEED", "R_SPEC", "R_CLIENT",
                      "R_TIME_10", "R_TIME_60", "R_SPEC_SES",
                      "R_LIN_OR_SPEC", "R_CLIENT_SPEC_TIME"):
            v = row[rname]
            print("      %-20s %.2f    %.2f   %d"
                  % (rname, v["recall"], v["precision"], v["size"]))
        print()

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"manifest": MANIFEST, "manifest_hash": MANIFEST_HASH,
                   "pool_size": len(pool), "results": results,
                   "worlds": WORLDS}, f, indent=1, default=str)
    print("rows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
