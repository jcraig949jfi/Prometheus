"""S15 -- MAPPING THE FOSSILIZATION BOUNDARY.

Harmonia science loop 15, 2026-09-05.

S14's seed-shopping attack did not defeat a v6 check. It never touched the
substrate at all. That is a different kind of limit, and this experiment
measures its size before any more reconstruction machinery is built.

  CLASS A  ENGINE-TOUCHING SELECTION. The candidate generation, comparison,
           rejection or promotion NECESSARILY causes a substrate-visible event
           before the retained result exists.
  CLASS B  ENGINE-EXTERNAL SELECTION. The actor can generate, search and
           compare candidates entirely outside the engine and submit only the
           survivor, leaving no substrate evidence that alternatives existed.

PRIMARY QUANTITY: the size and character of class B. NOT reconstruction
accuracy -- reconstruction of an absent record is not a measurement problem.

THE TEST FOR EACH MECHANISM is OBSERVATIONAL EQUIVALENCE. Two records are
built on a real engine: an HONEST single-shot submission, and an ADVERSARIAL
submission in which the same science was selected from N alternatives
externally. An ARCHAEOLOGICAL PROJECTION of each -- every substrate-visible
fact modulo random ids and wall-clock -- is then compared. If the projections
are equal, the mechanism is class B and the selection is information-
theoretically absent.

NOT DONE HERE, DELIBERATELY: no heuristic that infers a missing fossil from
absence. Absence of evidence is exactly what this experiment is measuring, and
a detector built on it would be unfalsifiable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sqlite3
import statistics
import sys
import urllib.error
import urllib.request

RESULTS = []
RNG = random.Random(20260905)


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


def score(seed, cfg=None, policy=None):
    """The SCIENCE. Computed entirely OUTSIDE the engine, which is the whole
    point: SFE records outcomes and never computes them."""
    r = random.Random("%s|%s|%s" % (seed, cfg, policy))
    return r.gauss(0.5, 0.10)


# --------------------------------------------------------------------------
# THE ARCHAEOLOGICAL PROJECTION: every substrate-visible fact about one
# submission, with random ids and wall-clock removed. This is what an
# archaeologist with the whole store could ever see.
# --------------------------------------------------------------------------
def projection(dbpath, world_names):
    cx = sqlite3.connect("file:%s?mode=ro" % dbpath, uri=True)
    cx.row_factory = sqlite3.Row
    q = "SELECT world_id,name,seed_root,sharing_policy,state FROM worlds"
    worlds = [r for r in cx.execute(q) if r["name"] in world_names]
    wids = {r["world_id"] for r in worlds}
    # STRUCTURAL projection only. The first version compared VALUES --
    # seed_roots, scores, spec strings -- which differ between ANY two
    # distinct experiments, so everything scored "class A" trivially. That is
    # not what observational equivalence means here. The question is whether
    # the adversarial record is indistinguishable from SOME honest single-shot
    # record, which is a question about FORM: how many worlds, how many
    # events, of what types. Values are excluded on purpose.
    proj = {"n_worlds": len(worlds),
            "n_distinct_policies": len(set(r["sharing_policy"] for r in worlds)),
            "n_distinct_states": len(set(r["state"] for r in worlds))}
    ex = [r for r in cx.execute(
        "SELECT world_id,spec,spec_hash,unit_of_analysis,declared_n,"
        "source_set_hash FROM experiments") if r["world_id"] in wids]
    proj["n_experiments"] = len(ex)
    proj["n_distinct_spec_hashes"] = len(set(r["spec_hash"] or "" for r in ex))
    ob = [r for r in cx.execute(
        "SELECT world_id,content,outcome FROM observations")
        if r["world_id"] in wids]
    proj["n_observations"] = len(ob)
    proj["n_distinct_content_shapes"] = len(
        set(tuple(sorted(json.loads(r["content"] or "{}").keys())) for r in ob))
    ev = [r for r in cx.execute(
        "SELECT world_id,event_type,world_index FROM events")
        if r["world_id"] in wids]
    proj["n_events"] = len(ev)
    proj["event_types"] = sorted(set(r["event_type"] for r in ev))
    proj["event_type_counts"] = dict(
        sorted({t: sum(1 for r in ev if r["event_type"] == t)
                for t in set(r["event_type"] for r in ev)}.items()))
    try:
        wk = [r for r in cx.execute(
            "SELECT world_id,status,attempts FROM work_items")
            if r["world_id"] in wids]
        proj["n_work_items"] = len(wk)
        proj["total_work_attempts"] = sum(r["attempts"] or 0 for r in wk)
    except Exception:                                              # noqa: BLE001
        proj["n_work_items"] = 0
    cx.close()
    return proj


def pf(p):
    return hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()[:16]


def verdict(name, klass, honest, adver, unavoidable, derived, minimal_fix):
    same = pf(honest) == pf(adver)
    RESULTS.append({"mechanism": name, "class": "B" if same else "A",
                    "projections_identical": same,
                    "honest_fingerprint": pf(honest),
                    "adversarial_fingerprint": pf(adver),
                    "unavoidable_fossil": unavoidable,
                    "observable_is": derived,
                    "minimal_change_to_move_to_A": minimal_fix,
                    "diff": None if same else
                    {k: (honest.get(k), adver.get(k)) for k in
                     set(honest) | set(adver) if honest.get(k) != adver.get(k)}})
    print("  [class %s] %-34s %s" % ("B" if same else "A", name,
                                     "records indistinguishable" if same
                                     else "DIFFERS"))
    if not same:
        for k in sorted(set(honest) | set(adver)):
            if honest.get(k) != adver.get(k):
                print("        %-20s honest=%s  adversarial=%s"
                      % (k, honest.get(k), adver.get(k)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", default="http://127.0.0.1:8886/v2")
    ap.add_argument("--rehearsal", default="http://127.0.0.1:8885/v2")
    ap.add_argument("--recdb", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = C(a.record)
    H = C(a.rehearsal)
    if R.call("GET", "/version")[0] != 200 or H.call("GET", "/version")[0] != 200:
        print("engines unreachable"); return 2
    rsid = R.boot("s15-record")
    hsid = H.boot("s15-rehearsal")

    def submit(eng, sid, name, seed, cfg, policy, val, extra_spec=None,
               n_obs=1):
        b = {"session_id": sid, "name": name, "sharing_policy": "ISOLATED",
             "seed_root": seed}
        w = eng.call("POST", "/worlds", b)[1]["world_id"]
        eng.call("POST", "/worlds/%s/start" % w, {})
        h = eng.call("POST", "/worlds/%s/hypotheses" % w,
                     {"statement": "H"})[1]["hyp_id"]
        spec = {"action": "encounter", "config": cfg, "policy": policy}
        if extra_spec:
            spec.update(extra_spec)
        for i in range(n_obs):
            x = eng.call("POST", "/worlds/%s/experiments" % w,
                         {"spec": spec, "hyp_id": h, "commit": True})[1]
            eng.call("POST", "/worlds/%s/observations" % w,
                     {"exp_id": x["exp_id"], "content": {"score": val},
                      "outcome": "SURVIVED"})
        return w

    print("=" * 78)
    print("S15  THE FOSSILIZATION BOUNDARY")
    print("=" * 78)
    print("  engine of record : %s" % a.record)
    print("  rehearsal replica: %s  (the adversary's private engine)\n"
          % a.rehearsal)

    # ==================================================================
    # M1 SEED SHOPPING
    # ==================================================================
    honest_seed = 500
    submit(R, rsid, "M1-honest", honest_seed, "c0", "p0",
           score(honest_seed, "c0", "p0"))
    best = max(range(600, 660), key=lambda s: score(s, "c0", "p0"))
    submit(R, rsid, "M1-adver", best, "c0", "p0", score(best, "c0", "p0"))
    verdict("M1_seed_shopping", "B",
            projection(a.recdb, {"M1-honest"}),
            projection(a.recdb, {"M1-adver"}),
            "none -- rejected seeds never executed anywhere",
            "n/a",
            "require every candidate seed to be REGISTERED before any is run")

    # ==================================================================
    # M2 CONFIGURATION / HYPERPARAMETER SEARCH
    # ==================================================================
    submit(R, rsid, "M2-honest", 700, "cfg_default", "p0",
           score(700, "cfg_default", "p0"))
    bcfg = max(["cfg_%d" % i for i in range(40)],
               key=lambda c: score(700, c, "p0"))
    submit(R, rsid, "M2-adver", 700, bcfg, "p0", score(700, bcfg, "p0"))
    verdict("M2_config_search", "B",
            projection(a.recdb, {"M2-honest"}),
            projection(a.recdb, {"M2-adver"}),
            "none -- the spec differs but a single spec is what an honest "
            "single-shot also shows",
            "claimant-supplied (the spec value itself)",
            "declare the search space before the run")

    # ==================================================================
    # M3 POLICY / PROMPT SEARCH
    # ==================================================================
    submit(R, rsid, "M3-honest", 800, "c0", "policy_default",
           score(800, "c0", "policy_default"))
    bpol = max(["policy_%d" % i for i in range(50)],
               key=lambda p: score(800, "c0", p))
    submit(R, rsid, "M3-adver", 800, "c0", bpol, score(800, "c0", bpol))
    verdict("M3_policy_search", "B",
            projection(a.recdb, {"M3-honest"}),
            projection(a.recdb, {"M3-adver"}),
            "none", "claimant-supplied (policy identity hash is of the "
            "SURVIVOR, not of the search)",
            "register candidate policy hashes before evaluation")

    # ==================================================================
    # M4 CANDIDATE BATCHING -- generate N outputs, submit 1
    # ==================================================================
    submit(R, rsid, "M4-honest", 900, "c0", "p0", score(900, "c0", "p0"))
    cands = [score(900, "c0", "p%d" % i) for i in range(30)]
    submit(R, rsid, "M4-adver", 900, "c0", "p0", max(cands))
    verdict("M4_candidate_batching", "B",
            projection(a.recdb, {"M4-honest"}),
            projection(a.recdb, {"M4-adver"}),
            "none -- only the retained value is submitted",
            "n/a",
            "the executor must attest how many candidates it produced")

    # ==================================================================
    # M5 RETRY-UNTIL-GOOD, INSIDE the engine (the honest way to do it)
    # ==================================================================
    for i in range(6):
        submit(R, rsid, "M5-adver-%d" % i, 1000 + i, "c0", "p0",
               score(1000 + i, "c0", "p0"))
    submit(R, rsid, "M5-honest", 1100, "c0", "p0", score(1100, "c0", "p0"))
    hp = projection(a.recdb, {"M5-honest"})
    ap_ = projection(a.recdb, {"M5-adver-%d" % i for i in range(6)})
    verdict("M5_retry_inside_engine", "A", hp, ap_,
            "YES -- six worlds, six event chains, six observations",
            "ENGINE-DERIVED (row and event counts)",
            "already class A; nothing to change")

    # ==================================================================
    # M6 RETRY-UNTIL-GOOD, REHEARSED on a replica then submitted once
    # This is the general reduction: ANY class-A mechanism becomes class B
    # by performing it on a different engine instance.
    # ==================================================================
    for i in range(6):
        submit(H, hsid, "M6-rehearsal-%d" % i, 1200 + i, "c0", "p0",
               score(1200 + i, "c0", "p0"))
    bseed = max(range(1200, 1206), key=lambda s: score(s, "c0", "p0"))
    submit(R, rsid, "M6-adver", bseed, "c0", "p0", score(bseed, "c0", "p0"))
    submit(R, rsid, "M6-honest", 1300, "c0", "p0", score(1300, "c0", "p0"))
    verdict("M6_retry_rehearsed_on_replica", "B",
            projection(a.recdb, {"M6-honest"}),
            projection(a.recdb, {"M6-adver"}),
            "none IN THE ENGINE OF RECORD -- the six rehearsals exist, but in "
            "a different engine instance the archaeologist has no reason to "
            "hold and no pointer to",
            "n/a",
            "cross-instance evidence federation, which does not exist and "
            "cannot be made mandatory for an actor who controls their own "
            "hardware")

    # ==================================================================
    # M7 FORK-BASED SELECTION, rehearsed -- the hardest case for the
    # reduction, because fork identity IS engine-conferred
    # ==================================================================
    ph = submit(H, hsid, "M7-reh-parent", 1400, "c0", "p0",
                score(1400, "c0", "p0"))
    ck = H.call("POST", "/worlds/%s/checkpoint" % ph, {})[1]["checkpoint_id"]
    kids = H.call("POST", "/worlds/%s/fork" % ph,
                  {"checkpoint_id": ck,
                   "children": [{"name": "reh-%d" % i,
                                 "interventions": {"arm": "a%d" % i}}
                                for i in range(10)]})[1]
    kids = kids.get("children", kids)
    scores = {i: score(1400, "c0", "a%d" % i) for i in range(10)}
    bi = max(scores, key=lambda i: scores[i])
    pr = submit(R, rsid, "M7-adver-parent", 1400, "c0", "p0",
                score(1400, "c0", "p0"))
    ckr = R.call("POST", "/worlds/%s/checkpoint" % pr, {})[1]["checkpoint_id"]
    R.call("POST", "/worlds/%s/fork" % pr,
           {"checkpoint_id": ckr,
            "children": [{"name": "M7-adver-child",
                          "interventions": {"arm": "a%d" % bi}}]})
    ph2 = submit(R, rsid, "M7-honest-parent", 1500, "c0", "p0",
                 score(1500, "c0", "p0"))
    ck2 = R.call("POST", "/worlds/%s/checkpoint" % ph2, {})[1]["checkpoint_id"]
    R.call("POST", "/worlds/%s/fork" % ph2,
           {"checkpoint_id": ck2,
            "children": [{"name": "M7-honest-child",
                          "interventions": {"arm": "a0"}}]})
    verdict("M7_fork_selection_rehearsed", "B",
            projection(a.recdb, {"M7-honest-parent", "M7-honest-child"}),
            projection(a.recdb, {"M7-adver-parent", "M7-adver-child"}),
            "none -- one parent and one child in both records; the ten "
            "rehearsed siblings live on the replica",
            "n/a",
            "same as M6: only federation would help, and it is unenforceable")

    # ==================================================================
    # M8 ANALYSIS / ESTIMATOR SEARCH on exported data
    # ==================================================================
    ids = []
    for i in range(8):
        w = submit(R, rsid, "M8-shared-%d" % i, 1600 + i, "c0", "p0",
                   score(1600 + i, "c0", "p0"))
        got = R.call("GET", "/worlds/%s/observations" % w)[1]
        lst = got.get("observations", got) if isinstance(got, dict) else got
        ids += [o.get("obs_id") for o in (lst or [])]
    wa_h = submit(R, rsid, "M8-honest-analysis", 1700, "c0", "p0", 0.5)
    wa_a = submit(R, rsid, "M8-adver-analysis", 1701, "c0", "p0", 0.5)
    for wid, est in ((wa_h, "hedges_g"), (wa_a, "trimmed_winsorised")):
        h = R.call("POST", "/worlds/%s/hypotheses" % wid,
                   {"statement": "A"})[1]["hyp_id"]
        R.call("POST", "/worlds/%s/experiments" % wid,
               {"spec": {"action": "analysis", "estimator": est},
                "hyp_id": h, "commit": True, "unit_of_analysis": "world",
                "declared_n": 8, "source_set": ids})
    ph_ = projection(a.recdb, {"M8-honest-analysis"})
    pa_ = projection(a.recdb, {"M8-adver-analysis"})
    verdict("M8_estimator_search_offline", "B", ph_, pa_,
            "the estimator NAME differs, but a single named estimator is what "
            "an honest single-shot also records",
            "claimant-supplied (the estimator string in the spec)",
            "declare the estimator BEFORE the source set is readable")

    # ==================================================================
    print("\n" + "=" * 78)
    print("BOUNDARY")
    print("=" * 78)
    nb = sum(1 for r in RESULTS if r["class"] == "B")
    na = len(RESULTS) - nb
    print("  class A (engine-touching, unavoidable fossil) : %d" % na)
    print("  class B (engine-external, no fossil)          : %d" % nb)
    for r in RESULTS:
        print("    %s  %-34s %s" % (r["class"], r["mechanism"],
                                    r["unavoidable_fossil"][:44]))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"results": RESULTS, "class_A": na, "class_B": nb},
                  f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
