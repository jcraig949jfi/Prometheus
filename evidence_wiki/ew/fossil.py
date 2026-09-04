"""Fossil-record mining (charter s11-s12): multidimensional queries over the
ingested cemetery. Sparse/relational implementation, justified: at current
scale the fossil space is a family x outcome x time structure best served by
grouped SQL + small dense factorization; the representation can migrate
without changing the query contract.

All outputs carry SFE anchors (entry hashes / content hashes) so every
number resolves to authoritative history (s10).
"""
import json
import time
from pathlib import Path

import numpy as np

from . import db as ewdb

HERE = Path(__file__).resolve().parent.parent


def q1_family_failure_matrix(conn, namespace="prod"):
    """Failure-type x world-family occupancy (the basic cemetery map)."""
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT w.family, e.outcome, COUNT(*) n "
            "FROM ew.fossil_encounters e JOIN ew.fossil_worlds w "
            " ON w.world_id=e.world_id WHERE e.namespace=%s "
            "GROUP BY 1,2 ORDER BY 1,2", (namespace,))
        rows = cur.fetchall()
    fams = sorted({r["family"] for r in rows})
    outs = sorted({r["outcome"] for r in rows})
    M = np.zeros((len(fams), len(outs)))
    for r in rows:
        M[fams.index(r["family"]), outs.index(r["outcome"])] = r["n"]
    return {"families": fams, "outcomes": outs, "matrix": M.tolist(),
            "total": int(M.sum())}


def q2_anomalous_worlds(conn, top=5, namespace="prod"):
    """Worlds whose failure profile diverges most from their family marginal
    (candidate 'previously dismissed as noise' neighborhoods)."""
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT e.world_id, w.family, e.outcome, COUNT(*) n, "
            " min(e.sfe_entry_hash) sample_hash "
            "FROM ew.fossil_encounters e JOIN ew.fossil_worlds w "
            " ON w.world_id=e.world_id WHERE e.namespace=%s "
            "GROUP BY 1,2,3", (namespace,))
        rows = cur.fetchall()
    fam_tot, fam_out = {}, {}
    wrl = {}
    for r in rows:
        fam_tot[r["family"]] = fam_tot.get(r["family"], 0) + r["n"]
        fam_out.setdefault(r["family"], {}).setdefault(r["outcome"], 0)
        fam_out[r["family"]][r["outcome"]] += r["n"]
        w = wrl.setdefault(r["world_id"], {"family": r["family"], "n": 0,
                                           "out": {}, "hash": r["sample_hash"]})
        w["n"] += r["n"]
        w["out"][r["outcome"]] = r["n"]
    scored = []
    for wid, w in wrl.items():
        if w["n"] < 10:
            continue
        f = w["family"]
        div = 0.0
        for o, n in w["out"].items():
            p_w = n / w["n"]
            p_f = fam_out[f].get(o, 0) / fam_tot[f]
            if p_f > 0:
                div += p_w * np.log(p_w / p_f)
        scored.append({"world_id": wid, "family": f, "n_encounters": w["n"],
                       "kl_vs_family": round(float(div), 4),
                       "sfe_anchor": w["hash"]})
    scored.sort(key=lambda x: -x["kl_vs_family"])
    return scored[:top]


def q3_discriminating_families(conn, namespace="prod"):
    """World families that separate player scores at low encounter cost:
    discrimination = score variance across players / mean encounters."""
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT w.family, "
            " COUNT(DISTINCT p.player_id) n_players, "
            " var_pop((p.phenotype->>'score')::float) score_var, "
            " COUNT(DISTINCT e.encounter_id)::float / "
            "  GREATEST(COUNT(DISTINCT p.player_id),1) enc_per_player "
            "FROM ew.fossil_players p "
            "JOIN ew.fossil_worlds w ON w.sfe_world_id=p.sfe_world_id "
            "LEFT JOIN ew.fossil_encounters e ON e.world_id=w.world_id "
            "WHERE p.namespace=%s AND p.phenotype->>'score' IS NOT NULL "
            "GROUP BY 1 HAVING COUNT(DISTINCT p.player_id) >= 20", (namespace,))
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["score_var"] = round(float(r["score_var"] or 0), 5)
        r["enc_per_player"] = round(float(r["enc_per_player"]), 2)
        r["discrimination_per_cost"] = round(
            r["score_var"] / max(r["enc_per_player"], 0.01), 5)
    rows.sort(key=lambda x: -x["discrimination_per_cost"])
    return rows


def q4_factorize(conn, rank=3, namespace="prod"):
    """Small factorization exercise over family x outcome (SVD); reports
    reconstruction + timing. Scaffolding measurement, not a discovery claim."""
    m = q1_family_failure_matrix(conn, namespace)
    M = np.array(m["matrix"])
    if min(M.shape) < 2:
        return {"skipped": "matrix too small"}
    t0 = time.time()
    U, S, Vt = np.linalg.svd(M, full_matrices=False)
    k = min(rank, len(S))
    rec = (U[:, :k] * S[:k]) @ Vt[:k]
    err = float(np.linalg.norm(rec - M) / (np.linalg.norm(M) + 1e-12))
    return {"shape": list(M.shape), "rank": k,
            "relative_error": round(err, 4),
            "seconds": round(time.time() - t0, 4),
            "top_factor_families": [m["families"][i] for i in
                                    np.argsort(-np.abs(U[:, 0]))[:5]]}


def q5_lineage_survival(conn, namespace="prod"):
    """Forked child worlds whose failure rate is lower than their parent's
    (transplant/reacquisition proxy over real fork lineage)."""
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "WITH rates AS (SELECT e.world_id, "
            "  AVG(CASE WHEN e.outcome <> 'committed' THEN 1 ELSE 0 END) fr, "
            "  COUNT(*) n FROM ew.fossil_encounters e WHERE e.namespace=%s "
            "  GROUP BY 1 HAVING COUNT(*) >= 5) "
            "SELECT g.dst_id child, g.src_id parent, g.sfe_entry_hash, "
            " c.fr child_fr, p.fr parent_fr, c.n child_n, p.n parent_n "
            "FROM ew.fossil_edges g "
            "JOIN rates c ON c.world_id=g.dst_id "
            "JOIN rates p ON p.world_id=g.src_id "
            "WHERE g.relation='FORK'", (namespace,))
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["child_fr"] = round(float(r["child_fr"]), 3)
        r["parent_fr"] = round(float(r["parent_fr"]), 3)
        r["improved"] = r["child_fr"] < r["parent_fr"]
    return {"fork_pairs_with_data": len(rows),
            "improved_children": sum(1 for r in rows if r["improved"]),
            "pairs": rows[:10]}


def run_all(conn):
    out = {}
    for name, fn in [("q1_family_failure_matrix", q1_family_failure_matrix),
                     ("q2_anomalous_worlds", q2_anomalous_worlds),
                     ("q3_discriminating_families", q3_discriminating_families),
                     ("q4_factorize", q4_factorize),
                     ("q5_lineage_survival", q5_lineage_survival)]:
        t0 = time.time()
        try:
            res = fn(conn)
            out[name] = {"latency_ms": round((time.time() - t0) * 1000, 1),
                         "result": res}
        except Exception as e:
            out[name] = {"error": str(e)[:200]}
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(HERE))
    conn = ewdb.connect()
    res = run_all(conn)
    (HERE / "benchmarks" / "fossil_tensor_v3.json").write_text(
        json.dumps(res, indent=1, default=str), encoding="utf-8")
    slim = {k: {"latency_ms": v.get("latency_ms"),
                "summary": str(v.get("result"))[:200]} for k, v in res.items()}
    print(json.dumps(slim, indent=1))
    conn.close()
