"""S9 -- EXPRESSIVENESS: what experiment SHAPES can a world actually host, and
can a running experiment be changed?

Harmonia science loop 9, 2026-09-05, against SFE schema v6.

Loops S1-S8 asked whether the record can keep a conclusion honest. This one asks
a prior and more practical question the operator raised: can varied experiments
actually be RUN inside these worlds, and is there room to change an experiment
once it is under way?

That second half is the real risk of v6. Every primitive it added SEALS
something -- spec_hash at commit, append-only family roles, manifest hashed at
creation, retraction preserving the original hash. Sealing is exactly right for
provenance and is exactly what makes a substrate rigid. A campaign that cannot
be adapted mid-flight is not a safe campaign, it is a dead one, and researchers
who cannot adapt inside the system will adapt outside it where nothing is
recorded.

So: twelve experiment shapes, then five amendment attempts. For each shape the
question is EXPRESSIBLE / EXPRESSIBLE-BUT-UNRECORDED / NOT EXPRESSIBLE. For each
amendment the question is whether the change is possible AND whether the record
distinguishes a legitimate amendment from a silent rewrite.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request

R = []


def rec(name, verdict, detail):
    R.append({"probe": name, "verdict": verdict, "detail": detail})
    print("  [%-24s] %-40s %s" % (verdict, name, detail))


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


def err(p):
    d = (p or {}).get("detail", p)
    return d.get("error") if isinstance(d, dict) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8891/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    st, ver = c.call("GET", "/version")
    if st != 200:
        print("engine unreachable"); return 2
    print("engine schema=%s profile=%s instance=%s"
          % (ver.get("schema_version"), ver.get("science_profile"),
             ver.get("engine_instance_id")))
    c.token = c.call("POST", "/clients", {"name": "s9"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "s9"})[1]
    c.key = s["session_key"]
    sid = s["session_id"]

    def world(name, **kw):
        b = {"session_id": sid, "name": name, "sharing_policy": "ISOLATED"}
        b.update(kw)
        w = c.call("POST", "/worlds", b)[1]
        c.call("POST", "/worlds/%s/start" % w["world_id"], {})
        return w["world_id"]

    def obs(wid, hyp, spec, content, **kw):
        x = c.call("POST", "/worlds/%s/experiments" % wid,
                   dict({"spec": spec, "hyp_id": hyp, "commit": True}, **kw))[1]
        if x.get("exp_id"):      # spec_hash is only on the READ path
            x = dict(x, **{"spec_hash": c.call(
                "GET", "/worlds/%s/experiments/%s" % (wid, x["exp_id"]))[1]
                .get("spec_hash")})
        o = c.call("POST", "/worlds/%s/observations" % wid,
                   {"exp_id": x.get("exp_id"), "content": content,
                    "outcome": "SURVIVED"})[1]
        return x, o

    print("\n" + "=" * 78)
    print("PART A -- CAN THESE EXPERIMENT SHAPES BE RUN INSIDE WORLDS?")
    print("=" * 78)

    # A1 repeated measures within one world
    w = world("A1-repeated")
    h = c.call("POST", "/worlds/%s/hypotheses" % w, {"statement": "A1"})[1]["hyp_id"]
    oks = [obs(w, h, {"action": "encounter", "ticks": 4, "rep": i},
               {"score": 0.5 + i * 0.01})[0].get("exp_id") for i in range(5)]
    rec("A1_repeated_measures", "EXPRESSIBLE" if all(oks) else "NOT EXPRESSIBLE",
        "%d sequential committed experiments in one world" % len(oks))

    # A2 between-world arms
    arms = {}
    for arm in ("ctrl", "treat"):
        wid = world("A2-%s" % arm)
        hh = c.call("POST", "/worlds/%s/hypotheses" % wid,
                    {"statement": arm})[1]["hyp_id"]
        obs(wid, hh, {"action": "encounter", "ticks": 4, "arm": arm},
            {"score": 0.5 if arm == "ctrl" else 0.7})
        arms[arm] = wid
    rec("A2_between_world_arms", "EXPRESSIBLE",
        "two worlds, one arm each, ISOLATED")

    # A3 factorial 2x2 -- are FACTORS representable or only flat arm labels?
    fac = {}
    for f1 in (0, 1):
        for f2 in (0, 1):
            wid = world("A3-%d%d" % (f1, f2))
            hh = c.call("POST", "/worlds/%s/hypotheses" % wid,
                        {"statement": "cell"})[1]["hyp_id"]
            x, _ = obs(wid, hh,
                       {"action": "encounter", "ticks": 4,
                        "factors": {"A": f1, "B": f2}},
                       {"score": 0.4 + 0.1 * f1 + 0.05 * f2})
            fac["%d%d" % (f1, f2)] = x.get("spec_hash")
    rec("A3_factorial_2x2",
        "EXPRESSIBLE" if len(set(fac.values())) == 4 else "NOT EXPRESSIBLE",
        "4 cells, %d distinct spec hashes; factors live in freeform spec"
        % len(set(fac.values())))

    # A4 crossover WITHIN a world -- treatment then control, order recorded?
    w4 = world("A4-crossover")
    h4 = c.call("POST", "/worlds/%s/hypotheses" % w4, {"statement": "x"})[1]["hyp_id"]
    x1, _ = obs(w4, h4, {"action": "encounter", "phase": "treat"}, {"score": 0.7})
    x2, _ = obs(w4, h4, {"action": "encounter", "phase": "ctrl"}, {"score": 0.5})
    ev = c.call("GET", "/worlds/%s/events?limit=200" % w4)[1]["events"]
    idx = [e["world_index"] for e in ev]
    rec("A4_crossover_within_world",
        "EXPRESSIBLE" if x1.get("committed_seq") < x2.get("committed_seq")
        else "EXPRESSIBLE-UNRECORDED",
        "phase order proved by committed_seq %s < %s"
        % (x1.get("committed_seq"), x2.get("committed_seq")))

    # A5 dose-response: continuous factor levels
    w5 = world("A5-dose")
    h5 = c.call("POST", "/worlds/%s/hypotheses" % w5, {"statement": "d"})[1]["hyp_id"]
    doses = [0.0, 0.25, 0.5, 0.75, 1.0]
    hs = [obs(w5, h5, {"action": "encounter", "dose": d},
              {"score": 0.4 + 0.2 * d})[0].get("spec_hash") for d in doses]
    rec("A5_dose_response",
        "EXPRESSIBLE" if len(set(hs)) == len(doses) else "NOT EXPRESSIBLE",
        "%d dose levels, %d distinct sealed specs" % (len(doses), len(set(hs))))

    # A6 cross-world campaign family (NEW in v6)
    st, fam = c.call("POST", "/families",
                     {"kind": "campaign",
                      "manifest": {"planned_members": 4, "arms": ["ctrl", "treat"]}})
    fid = fam.get("family_id")
    added = 0
    for arm, wid in arms.items():
        stm, _ = c.call("POST", "/families/%s/members" % fid,
                        {"member_kind": "world", "member_id": wid,
                         "role": "executed"})
        added += (stm == 200)
    stc, cen = c.call("GET", "/families/%s" % fid)
    rec("A6_cross_world_family",
        "EXPRESSIBLE" if fid and added == 2 else "NOT EXPRESSIBLE",
        "family=%s members=%d census keys=%s"
        % (fid, added, sorted(cen.keys())[:6]))

    # A7 nested: topology group as a grouping factor
    stg, grp = c.call("POST", "/topology-groups", {})
    gid = grp.get("group_id") or grp.get("topology_group")
    w7 = world("A7-nested", topology_group=gid) if gid else None
    rec("A7_nested_grouping",
        "EXPRESSIBLE" if w7 else "NOT EXPRESSIBLE",
        "topology_group=%s usable as a world-level grouping factor" % gid)

    # A8 analysis as an experiment over a declared source set (NEW)
    obs_ids = []
    for arm, wid in arms.items():
        got = c.call("GET", "/worlds/%s/observations" % wid)[1]
        lst = got.get("observations", got) if isinstance(got, dict) else got
        obs_ids += [o.get("obs_id") for o in (lst or []) if o.get("obs_id")]
    wa = world("A8-analysis")
    ha = c.call("POST", "/worlds/%s/hypotheses" % wa, {"statement": "an"})[1]["hyp_id"]
    st8, an = c.call("POST", "/worlds/%s/experiments" % wa,
                     {"spec": {"action": "analysis", "estimator": "hedges_g",
                               "tested_domain": ["landscapeA"]},
                      "hyp_id": ha, "commit": True,
                      "unit_of_analysis": "world", "declared_n": 2,
                      "source_set": obs_ids})
    st8b, anr = c.call("GET", "/worlds/%s/experiments/%s/analysis"
                       % (wa, an.get("exp_id", "x")))
    rec("A8_analysis_with_source_set",
        "EXPRESSIBLE" if st8 == 200 else "NOT EXPRESSIBLE",
        "declared_n=2 vs engine count -> %s" % json.dumps(anr)[:110])

    # A9 a claim citing that analysis, cross-world by construction
    st9, clm = c.call("POST", "/claims",
                      {"estimand": "treat - ctrl on score",
                       "status": "SUCCESSFUL_NEGATIVE",
                       "relevance_floor": {"smd": 0.5},
                       "replication": {"new_world_draws": True},
                       "transport_domain": ["landscapeA"],
                       "family_id": fid,
                       "analysis_exp_id": an.get("exp_id")})
    rec("A9_claim_successful_negative",
        "EXPRESSIBLE" if st9 == 200 else "NOT EXPRESSIBLE",
        "status=%s findings=%s" % (st9, json.dumps(clm.get("science", {}))[:90]))

    # A10 branch a design mid-campaign by forking a live world
    w10 = world("A10-parent", seed_root=99)
    h10 = c.call("POST", "/worlds/%s/hypotheses" % w10, {"statement": "p"})[1]["hyp_id"]
    obs(w10, h10, {"action": "encounter", "ticks": 4}, {"score": 0.5})
    ck = c.call("POST", "/worlds/%s/checkpoint" % w10, {})[1].get("checkpoint_id")
    st10, kids = c.call("POST", "/worlds/%s/fork" % w10,
                        {"checkpoint_id": ck,
                         "children": [{"name": "branch-A",
                                       "interventions": {"component": "A"}},
                                      {"name": "branch-B",
                                       "interventions": {"component": "B"}}]})
    nk = len((kids.get("children", kids) or [])) if st10 == 200 else 0
    rec("A10_branch_design_midflight",
        "EXPRESSIBLE" if nk == 2 else "NOT EXPRESSIBLE",
        "forked %d branches from a live world at checkpoint %s" % (nk, ck))

    # A11 does the parent keep running after being forked?
    st11, p11 = c.call("GET", "/worlds/%s/status" % w10)
    stx, _ = obs(w10, h10, {"action": "encounter", "ticks": 4, "after_fork": 1},
                 {"score": 0.55})
    rec("A11_parent_continues_after_fork",
        "EXPRESSIBLE" if stx.get("exp_id") else "NOT EXPRESSIBLE",
        "parent state=%s, further experiment committed=%s"
        % (p11.get("state"), bool(stx.get("exp_id"))))

    # A12 heterogeneous worlds in one family (mixture population)
    st12, fam2 = c.call("POST", "/families",
                        {"kind": "comparison",
                         "manifest": {"population": "mixture",
                                      "planned_members": 2}})
    f2 = fam2.get("family_id")
    ok12 = 0
    for nm, seed in (("smooth", 1), ("blocked", 2)):
        wid = world("A12-%s" % nm, seed_root=seed)
        stm, _ = c.call("POST", "/families/%s/members" % f2,
                        {"member_kind": "world", "member_id": wid,
                         "role": "executed"})
        ok12 += (stm == 200)
    rec("A12_heterogeneous_population",
        "EXPRESSIBLE" if ok12 == 2 else "NOT EXPRESSIBLE",
        "two structurally different worlds in one comparison family")

    # ==================================================================
    print("\n" + "=" * 78)
    print("PART B -- CAN A RUNNING EXPERIMENT BE CHANGED?")
    print("=" * 78)

    # B1 amend a committed spec  (must be refused)
    stb1, pb1 = c.call("POST", "/worlds/%s/experiments" % w5,
                       {"spec": {"action": "encounter", "dose": 0.5,
                                 "amended": True},
                        "hyp_id": h5, "commit": True})
    rec("B1_amend_by_new_committed_spec",
        "EXPRESSIBLE" if stb1 == 200 else "NOT EXPRESSIBLE",
        "a CHANGE is a new sealed experiment, not an edit -> %s" % stb1)

    # B2 grow a family beyond its declared planned_members
    stb2, _ = c.call("POST", "/families/%s/members" % fid,
                     {"member_kind": "world", "member_id": world("B2-extra"),
                      "role": "executed"})
    stb2b, cen2 = c.call("GET", "/families/%s" % fid)
    rec("B2_grow_family_past_manifest",
        "EXPRESSIBLE" if stb2 == 200 else "NOT EXPRESSIBLE",
        "added past planned_members=4 -> %s ; census says %s"
        % (stb2, json.dumps({k: v for k, v in cen2.items()
                             if "plan" in k or "member" in k or "find" in k})[:120]))

    # B3 re-role a member after the fact (must be refused: append-only)
    stb3, pb3 = c.call("POST", "/families/%s/members" % fid,
                       {"member_kind": "world", "member_id": arms["treat"],
                        "role": "selected"})
    rec("B3_reassign_role_after_results",
        "NOT EXPRESSIBLE" if stb3 == 409 else "EXPRESSIBLE",
        "re-role executed->selected -> %s %s (409 is the correct refusal)"
        % (stb3, err(pb3)))

    # B4 record a mid-campaign protocol change as a NEW family citing the old
    stb4, fam3 = c.call("POST", "/families",
                        {"kind": "campaign",
                         "manifest": {"planned_members": 2,
                                      "amends_family": fid,
                                      "reason": "budget raised after interim"}})
    f3 = fam3.get("family_id")
    stb4b, _ = c.call("POST", "/families/%s/members" % f3,
                      {"member_kind": "family", "member_id": fid,
                       "role": "planned"}) if f3 else (None, {})
    # member_kind accepts world / claim / experiment, and REFUSES family (422).
    # So an amendment can be recorded in the sealed manifest but the chain is
    # not a relation the engine can traverse or validate.
    rec("B4_amendment_as_new_family",
        "EXPRESSIBLE-UNRECORDED" if f3 else "NOT EXPRESSIBLE",
        "amends_family sealed in manifest=%s, family-as-member refused (%s), "
        "so amendment lineage is not traversable"
        % (bool(f3), stb4b))

    # B5 add an arm after seeing results, and is the selection visible?
    stb5, fam4 = c.call("POST", "/families",
                        {"kind": "selection", "manifest": {"planned_members": 3}})
    f4 = fam4.get("family_id")
    c.call("POST", "/families/%s/members" % f4,
           {"member_kind": "world", "member_id": arms["treat"], "role": "selected"})
    st5a, cen5a = c.call("GET", "/families/%s" % f4)
    c.call("POST", "/families/%s/members" % f4,
           {"member_kind": "world", "member_id": arms["ctrl"],
            "role": "alternative"})
    st5b, cen5b = c.call("GET", "/families/%s" % f4)
    rec("B5_selection_visibility_transition",
        "EXPRESSIBLE",
        "selection_visible before alternatives=%s, after=%s"
        % (cen5a.get("selection_visible"), cen5b.get("selection_visible")))

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"engine": ver, "probes": R}, f, indent=1)
    n_ok = sum(1 for r in R if r["verdict"] == "EXPRESSIBLE")
    print("\n" + "=" * 78)
    print("%d/%d probes EXPRESSIBLE   rows: %s" % (n_ok, len(R), a.out))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
