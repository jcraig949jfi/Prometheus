"""Genealogy of 7ae3/16000006 from D0 to the first STATE-ROBUST competent lineage member.

Reads replay_events.json (replay.py). Genome VERSIONS are nodes: a version is created by an accepted replication
(birth: parent version = the donor's current version) or by an in-place ATOMIC mutation (parent version = the
same organism's previous version). D0 = live organisms whose genome is COMPETENT (run_de cached screen) at the
first 20-epoch check where any is (must equal the recorded 340). Lineage L as X-P2-LINEAGE: births whose parent is
in L join L, births from a non-L parent leave L.

Screens every version created in [D0, first_robust_snapshot] that is in L for COMPETENT, and competent ones for
STATE_ROBUST (measure.state_rates, 20 seeds x 2 sides, FRESH vs SELF1). Output: genealogy.json.
"""
from __future__ import annotations

import json
import pathlib
import sys

import measure as M

HERE = pathlib.Path(__file__).resolve().parent


def main():
    D = json.loads((HERE / "replay_events.json").read_text())
    assert D["meta"]["replay_ok"], D["meta"]
    ev, snaps = D["events"], {int(k): v for k, v in D["snaps"].items()}
    # ---- D0
    d0 = None
    for e in sorted(snaps):
        if e % 20:
            continue
        comp = [(oid, g) for oid, g in snaps[e]["live"] if M.competent(bytes.fromhex(g))]
        if comp:
            d0 = e
            break
    S0 = snaps[d0]
    comp_oids = {oid for oid, g in S0["live"] if M.competent(bytes.fromhex(g))}
    # ---- versions
    V = []                       # id -> dict
    cur = {}                     # oid -> version id
    for oid, g in S0["live"]:
        cur[oid] = len(V)
        V.append({"vid": len(V), "oid": oid, "g": g, "parent_vid": None, "via": "D0" if oid in comp_oids else "init",
                  "e": d0, "seq": S0["seq"], "inL": oid in comp_oids, "causal": None})
    alive = set(cur)
    for x in ev:
        if x["seq"] <= S0["seq"]:
            continue
        if x["kind"] == "birth":
            pv = cur.get(x["parent"])
            # the donor's version at the START of the interaction wrote the child: if the donor was itself
            # mutated (ATOMIC write-back) or overwritten in the same interaction (logged first), step back.
            k = 0
            while pv is not None and V[pv]["g"] != x["donor_pre"] and k < 3:
                pv = V[pv]["parent_vid"] if V[pv]["via"] == "mut" else V[pv].get("victim_vid")
                k += 1
            vv = cur.pop(x["victim_oid"], None)
            alive.discard(x["victim_oid"])
            nid = len(V)
            V.append({"vid": nid, "oid": x["child"], "g": x["g"], "parent_vid": pv, "via": "birth", "e": x["e"],
                      "seq": x["seq"], "causal": x["causal"], "fid": x["fid"], "victim_vid": vv,
                      "donor_pre": x["donor_pre"], "victim_old": x["victim_old"],
                      "donor_match": pv is not None and V[pv]["g"] == x["donor_pre"],
                      "inL": pv is not None and V[pv]["inL"]})
            cur[x["child"]] = nid
            alive.add(x["child"])
        elif x["kind"] == "mut":
            pv = cur.get(x["oid"])
            assert pv is not None and V[pv]["g"] == x["g_old"], x["seq"]
            nid = len(V)
            V.append({"vid": nid, "oid": x["oid"], "g": x["g"], "parent_vid": pv, "via": "mut", "e": x["e"],
                      "seq": x["seq"], "inL": V[pv]["inL"], "causal": None})
            cur[x["oid"]] = nid
        elif x["kind"] == "reap":
            cur.pop(x["oid"], None)
            alive.discard(x["oid"])
    # consistency: cur vs snapshots
    mism = 0
    for e in sorted(snaps):
        if e <= d0:
            continue
    last_e = max(snaps)
    live_last = {oid: g for oid, g in snaps[last_e]["live"]}
    mism = sum(1 for oid, vid in cur.items() if live_last.get(oid) != V[vid]["g"]) if snaps[last_e]["seq"] == ev[-1]["seq"] else None
    # ---- screen L versions chronologically for COMPETENT and STATE_ROBUST
    rcache = {}
    first = None
    screened = 0
    for v in V:
        if not v["inL"]:
            continue
        g = bytes.fromhex(v["g"])
        v["competent"] = M.competent(g)
        if not v["competent"]:
            continue
        if v["g"] not in rcache:
            rcache[v["g"]] = M.state_rates(g, 20, ("FRESH", "SELF1"))
            screened += 1
        v["rates"] = rcache[v["g"]]
        v["robust"] = M.robust(v["rates"])
        if v["robust"] and first is None:
            first = v["vid"]
            stop_seq = v["seq"]
        if first is not None and v["seq"] > stop_seq and v["e"] > V[first]["e"] + 20:
            break
    # ---- ancestry of the first robust member
    path = []
    x = first
    while x is not None:
        path.append(x)
        x = V[x]["parent_vid"]
    path.reverse()
    for vid in path:
        v = V[vid]
        g = bytes.fromhex(v["g"])
        v.setdefault("competent", M.competent(g))
        if "rates" not in v:
            v["rates"] = M.state_rates(g, 20, ("FRESH", "SELF1"))
            v["robust"] = M.robust(v["rates"])
    steps = []
    for a, b in zip(path, path[1:]):
        ga, gb = bytes.fromhex(V[a]["g"]), bytes.fromhex(V[b]["g"])
        steps.append({"from": a, "to": b, "via": V[b]["via"], "e": V[b]["e"], "causal": V[b].get("causal"),
                      "diffs": [[i, "%02X" % ga[i], "%02X" % gb[i]] for i in range(min(len(ga), len(gb))) if ga[i] != gb[i]],
                      "len": [len(ga), len(gb)]})
    robust_versions = [v["vid"] for v in V if v.get("robust")]
    out = {"d0_epoch": d0, "d0_oids": sorted(comp_oids),
           "d0_genomes": sorted({g for oid, g in S0["live"] if oid in comp_oids}),
           "n_versions_total": len(V), "n_versions_L_screened_upto_stop": sum(1 for v in V if "competent" in v),
           "n_distinct_competent_rate_tested": screened, "end_state_mismatch": mism,
           "first_robust_vid": first, "path": [{k: V[i].get(k) for k in ("vid", "oid", "via", "e", "seq", "causal", "fid",
                                                                          "competent", "rates", "robust", "g",
                                                                          "donor_match", "victim_vid", "victim_old")}
                                                for i in path],
           "steps": steps, "robust_versions_found": robust_versions[:200],
           "n_generations_births": sum(1 for i in path if V[i]["via"] == "birth"),
           "n_mut_steps": sum(1 for i in path if V[i]["via"] == "mut")}
    (HERE / "genealogy.json").write_text(json.dumps(out, indent=1))
    (HERE / "versions.json").write_text(json.dumps(V))
    print(json.dumps({k: out[k] for k in ("d0_epoch", "d0_oids", "first_robust_vid", "n_generations_births",
                                          "n_mut_steps", "n_distinct_competent_rate_tested", "end_state_mismatch")}))
    for s in steps:
        print(s)


if __name__ == "__main__":
    main()
