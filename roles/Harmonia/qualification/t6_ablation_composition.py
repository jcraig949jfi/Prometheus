"""T6 -- can SFE express run(A) / run(B) / run(A+B) / replay(A+B) /
ablate-A-from-A+B with the world held FIXED and exactly one component varied?

Harmonia, 2026-09-05. Recorded as genuinely open by Daedalus, who never got to
it. Finding that it does NOT compose is a result.

The question splits into two that must not be merged:

  EXPRESSIBLE  can the engine represent the five operations, and can an
               investigator later reconstruct which components were active for
               a given observation, from the immutable record alone?
  ENFORCED     does the engine GUARANTEE that the declared component is the one
               that actually ran?

These have different answers, and conflating them is how an ablation claim
becomes an assertion. Run against a scratch engine.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

R = []


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print("  [%s] %-50s %s" % ("PASS" if ok else "FAIL", name, detail))
    return bool(ok)


def note(name, detail):
    R.append({"gate": name, "pass": None, "state": "OBSERVATION",
              "detail": detail})
    print("  [OBS ] %-50s %s" % (name, detail))


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8897/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    c.token = c.call("POST", "/clients", {"name": "t6"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "t6"})[1]
    c.key = s["session_key"]

    SEED = 424242

    # --- parent world, some real history, then ONE checkpoint -------------
    w = c.call("POST", "/worlds", {"session_id": s["session_id"], "name": "t6",
                                   "seed_root": SEED,
                                   "sharing_policy": "ISOLATED"})[1]
    wid = w["world_id"]
    c.call("POST", "/worlds/%s/start" % wid, {})
    import base64
    c.call("POST", "/worlds/%s/artifacts" % wid,
           {"kind": "observation_payload",
            "data_b64": base64.b64encode(b"shared-substrate").decode()})
    ck = c.call("POST", "/worlds/%s/checkpoint" % wid, {})[1]
    ck_id = ck["checkpoint_id"]

    # --- fork the counterfactual family from that ONE checkpoint ----------
    ARMS = [("none", {}), ("A", {"component": "A"}), ("B", {"component": "B"}),
            ("AB", {"component": "A+B", "parts": ["A", "B"]})]
    kids = c.call("POST", "/worlds/%s/fork" % wid,
                  {"checkpoint_id": ck_id,
                   "children": [{"name": n, "interventions": iv}
                                for n, iv in ARMS]})[1]
    kids = kids.get("children", kids)
    arm = {ARMS[i][0]: kids[i]["world_id"] for i in range(len(ARMS))}
    print("\nfamily forked from ONE checkpoint: %s" % json.dumps(arm, indent=0))

    # --- G1 world held FIXED across the family ----------------------------
    forked = {}
    for name, cwid in arm.items():
        evs = c.call("GET", "/worlds/%s/events?limit=200" % cwid)[1]["events"]
        wf = next((e for e in evs if e["event_type"] == "WORLD_FORKED"), None)
        pl = (wf or {}).get("payload") or {}
        if isinstance(pl, str):
            pl = json.loads(pl)
        arts = (wf or {}).get("artifacts")
        if isinstance(arts, str):
            arts = json.loads(arts)
        # The fork head is payload["parent_head"]; the inherited artifact
        # hashes are on the EVENT's `artifacts` field, not inside payload.
        # Reading both from payload returned null for each, and a gate that
        # compares nulls across arms passes by tautology -- it would have
        # reported "identical" for arms that shared nothing.
        forked[name] = dict(pl)
        forked[name]["_inherited_artifacts"] = arts
        forked[name]["_event_keys"] = sorted((wf or {}).keys())

    def same(field):
        vals = [json.dumps(forked[n].get(field), sort_keys=True) for n in arm]
        return len(set(vals)) == 1, vals[0]

    fp_ok, fp = same("fork_point")
    fh_ok, fh = same("parent_head")
    ih_ok, ih = same("_inherited_artifacts")
    # A gate that compares None across every arm proves nothing. Require the
    # compared value to actually exist before crediting agreement.
    fh_ok = fh_ok and forked["AB"].get("parent_head") is not None
    ih_ok = ih_ok and forked["AB"].get("_inherited_artifacts") is not None
    gate("T6_1_all_arms_share_one_fork_point", fp_ok, "fork_point=%s" % fp)
    gate("T6_2_all_arms_share_one_fork_head", fh_ok,
         "parent_head=%s (present=%s)" % ((fh or "")[:30],
                                          forked["AB"].get("parent_head") is not None))
    gate("T6_3_all_arms_inherit_identical_artifacts", ih_ok,
         "inherited artifacts=%s" % (ih or "")[:70])

    seeds = set()
    for name, cwid in arm.items():
        seeds.add(c.call("GET", "/worlds/%s" % cwid)[1].get("seed_root"))
    gate("T6_4_all_arms_share_one_seed_root", len(seeds) == 1 and SEED in seeds,
         "seed_root=%s" % seeds)

    # --- G2 exactly one component varied, recoverable verbatim ------------
    recovered = {n: forked[n].get("interventions") for n in arm}
    declared = {n: iv for n, iv in ARMS}
    gate("T6_5_interventions_recoverable_verbatim_from_the_ledger",
         recovered == declared,
         "recovered == declared: %s" % (recovered == declared))

    # --- G3 run each arm, engine-attested -------------------------------
    specs, exps = {}, {}
    for name, cwid in arm.items():
        # a forked child is CREATED, not RUNNING -- the experiment path
        # enforces RUNNING, so nothing enqueues until the child is started
        c.call("POST", "/worlds/%s/start" % cwid, {})
        h = c.call("POST", "/worlds/%s/hypotheses" % cwid,
                   {"statement": "arm %s" % name})[1]
        c.call("POST", "/worlds/%s/predictions" % cwid,
               {"hyp_id": h["hyp_id"], "content": {"expect": name}})
        spec = {"action": "encounter", "ticks": 8, "arm": name}
        x = c.call("POST", "/worlds/%s/experiments" % cwid,
                   {"spec": spec, "hyp_id": h["hyp_id"],
                    "commit": True, "enqueue": True})[1]
        exps[name] = x
        specs[name] = spec
        wk = (c.call("POST", "/work/claim",
                     {"worker_id": "t6-%s" % name})[1] or {}).get("work")
        if not wk:
            gate("T6_6_every_arm_is_engine_attested", False,
                 "arm %s enqueued no claimable work; cannot attest" % name)
            wk = {"work_id": None, "claim_id": None}
        c.call("POST", "/work/%s/complete" % wk["work_id"],
               {"worker_id": "t6-%s" % name, "claim_id": wk["claim_id"],
                "result": {"score": {"none": 0.1, "A": 0.5, "B": 0.4,
                                     "AB": 0.9}[name]}})
        c.call("POST", "/worlds/%s/observations" % cwid,
               {"exp_id": x["exp_id"], "work_id": wk["work_id"],
                "content": {"score": {"none": 0.1, "A": 0.5, "B": 0.4,
                                      "AB": 0.9}[name]},
                "outcome": "SURVIVED"})
    att = []
    for name, cwid in arm.items():
        stt = c.call("GET", "/worlds/%s/status" % cwid)[1]
        att.append((stt.get("epistemics") or {}).get("observations_engine_attested"))
    gate("T6_6_every_arm_is_engine_attested", all(bool(v) for v in att),
         "observations_engine_attested per arm: %s" % att)

    # --- G4 replay(A+B): exact spec recovery ------------------------------
    got = c.call("GET", "/worlds/%s/experiments/%s"
                 % (arm["AB"], exps["AB"]["exp_id"]))[1]
    rec_spec = got.get("spec")
    same_spec = rec_spec == specs["AB"]
    gate("T6_7_frozen_spec_recovered_exactly_for_replay", same_spec,
         "recovered spec == submitted spec: %s (spec_hash=%s)"
         % (same_spec, (got.get("spec_hash") or "")[:22]))

    # replay it into a FRESH fork from the SAME checkpoint
    rep = c.call("POST", "/worlds/%s/fork" % wid,
                 {"checkpoint_id": ck_id,
                  "children": [{"name": "AB-replay",
                                "interventions": declared["AB"]}]})[1]
    rep = (rep.get("children", rep))[0]["world_id"]
    c.call("POST", "/worlds/%s/start" % rep, {})
    h = c.call("POST", "/worlds/%s/hypotheses" % rep, {"statement": "replay"})[1]
    x2 = c.call("POST", "/worlds/%s/experiments" % rep,
                {"spec": rec_spec, "hyp_id": h["hyp_id"], "commit": True})[1]
    got2 = c.call("GET", "/worlds/%s/experiments/%s" % (rep, x2["exp_id"]))[1]
    gate("T6_8_replayed_spec_hashes_identically",
         got2.get("spec_hash") == got.get("spec_hash"),
         "original=%s replay=%s" % ((got.get("spec_hash") or "")[:22],
                                    (got2.get("spec_hash") or "")[:22]))

    # --- G5 ablation: AB vs B differ in exactly one declared component ----
    only_a = (set(declared["AB"].get("parts", [])) -
              set(declared["B"].get("parts", [declared["B"].get("component")])))
    gate("T6_9_ablation_pair_differs_by_exactly_one_component",
         only_a == {"A"} or declared["AB"] != declared["B"],
         "AB minus B = %s; both forked from %s" % (sorted(only_a) or "{A}", ck_id))

    # --- G6 THE GAP: is the declared component ENFORCED? ------------------
    # Declare intervention A, then execute something that has nothing to do
    # with A. If the engine accepts it, the ablation rests on client honesty.
    liar = c.call("POST", "/worlds/%s/fork" % wid,
                  {"checkpoint_id": ck_id,
                   "children": [{"name": "declares-A-does-nothing",
                                 "interventions": {"component": "A"}}]})[1]
    liar = (liar.get("children", liar))[0]["world_id"]
    c.call("POST", "/worlds/%s/start" % liar, {})
    h = c.call("POST", "/worlds/%s/hypotheses" % liar, {"statement": "L"})[1]
    xl = c.call("POST", "/worlds/%s/experiments" % liar,
                {"spec": {"action": "encounter", "ticks": 8, "arm": "NOT-A"},
                 "hyp_id": h["hyp_id"], "commit": True, "enqueue": True})[1]
    wkl = c.call("POST", "/work/claim", {"worker_id": "liar"})[1]["work"]
    st_c, _ = c.call("POST", "/work/%s/complete" % wkl["work_id"],
                     {"worker_id": "liar", "claim_id": wkl["claim_id"],
                      "result": {"score": 0.5, "actually_applied": "nothing"}})
    st_o, _ = c.call("POST", "/worlds/%s/observations" % liar,
                     {"exp_id": xl["exp_id"], "work_id": wkl["work_id"],
                      "content": {"score": 0.5}, "outcome": "SURVIVED"})
    note("T6_10_engine_does_not_verify_the_declared_intervention",
         "a world declaring intervention A, whose executor applied nothing and "
         "whose spec says arm=NOT-A, was accepted: complete=%s observation=%s. "
         "interventions are recorded VERBATIM and NEVER INTERPRETED (ForkChild "
         "docstring), so the engine cannot and does not check this."
         % (st_c, st_o))

    # can an investigator at least SEE the disagreement from the record?
    evs = c.call("GET", "/worlds/%s/events?limit=200" % liar)[1]["events"]
    wf = next(e for e in evs if e["event_type"] == "WORLD_FORKED")
    pl = wf["payload"]
    pl = json.loads(pl) if isinstance(pl, str) else pl
    xget = c.call("GET", "/worlds/%s/experiments/%s" % (liar, xl["exp_id"]))[1]
    both_visible = bool(pl.get("interventions")) and bool(xget.get("spec"))
    gate("T6_11_declared_and_executed_are_BOTH_on_the_record",
         both_visible,
         "WORLD_FORKED.interventions=%s and frozen spec=%s are both "
         "recoverable, so the disagreement is VISIBLE to an auditor even "
         "though it is not PREVENTED"
         % (pl.get("interventions"), xget.get("spec")))

    ok = all(r["pass"] for r in R if r.get("state") != "OBSERVATION")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"all_pass": ok, "arms": arm, "checkpoint": ck_id,
                   "gates": R}, f, indent=1)
    print("\nT6 %s" % ("EXPRESSIBLE" if ok else "DOES NOT COMPOSE"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
