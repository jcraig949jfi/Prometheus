"""Mnemosyne Tensor Compiler (charter A5).

compile()  : canonical coordinates -> immutable snapshot file + ew.snapshots row
factor()   : snapshot -> CP / Tucker / TT via TensorLy -> persisted artifact
contract() : snapshot -> marginalized counts over retained modes, with the
             contributing evidence ids (explainability by construction)
score_missing() : reconstruction scores on unobserved cells (HYPOTHESES only)

Factorizations read ONLY snapshot files — never live tables. Every artifact
row carries versions, params and a reproducibility hash; delete + rebuild
must reproduce within documented tolerance (gate G17).
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from . import COMPILER_VERSION, ONTOLOGY_VERSION, SCHEMA_VERSION, ids
from . import db as ewdb
from .coords import VIEWS

DERIVED = Path(__file__).resolve().parent.parent / "derived"
DERIVED.mkdir(exist_ok=True)

DENSE_CELL_LIMIT = 5_000_000  # refuse astronomical dense materializations


def compile(conn, view_name, filters=None):
    """Freeze the current coordinates of a view (optionally filtered on
    evidence columns) into an immutable snapshot."""
    filters = filters or {}
    spec = VIEWS[view_name]
    where, args = ["c.view_name=%s AND c.view_version=%s"], [view_name, spec["version"]]
    for col in ("gate", "negative", "agent_id", "evidence_type"):
        if col in filters:
            vals = filters[col]
            if isinstance(vals, list):
                where.append(f"e.{col} = ANY(%s)")
                args.append(vals)
            else:
                where.append(f"e.{col} = %s")
                args.append(vals)
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT c.evidence_id, c.coords, c.value FROM ew.coordinates c "
            "JOIN ew.evidence e ON e.evidence_id=c.evidence_id "
            f"WHERE {' AND '.join(where)} ORDER BY c.coords::text, c.evidence_id",
            args)
        rows = cur.fetchall()
        crev = ewdb.canonical_revision(cur)
    lines = [json.dumps({"evidence_id": r["evidence_id"], "coords": r["coords"],
                         "value": r["value"]}, sort_keys=True) for r in rows]
    content = "\n".join(lines) + "\n"
    sha = hashlib.sha256(content.encode()).hexdigest()
    snap_id = ids.snapshot_id(view_name, spec["version"], filters, sha)
    path = DERIVED / f"{snap_id}.coords.jsonl"
    path.write_text(content, encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ew.snapshots(snapshot_id, view_name, view_version, "
            "filter_spec, canonical_revision, coord_count, content_sha256, path) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (snapshot_id) DO NOTHING",
            (snap_id, view_name, spec["version"], json.dumps(filters), crev,
             len(rows), sha, str(path)))
    conn.commit()
    return {"snapshot_id": snap_id, "coord_count": len(rows),
            "canonical_revision": crev, "content_sha256": sha}


def load_snapshot(conn, snapshot_id):
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.snapshots WHERE snapshot_id=%s", (snapshot_id,))
        snap = cur.fetchone()
    if snap is None:
        raise KeyError(snapshot_id)
    rows = [json.loads(l) for l in
            Path(snap["path"]).read_text(encoding="utf-8").splitlines() if l]
    modes = VIEWS[snap["view_name"]]["modes"]
    dicts = {m: sorted({r["coords"][m] for r in rows}) for m in modes}
    index = {m: {v: i for i, v in enumerate(dicts[m])} for m in modes}
    coo = np.array([[index[m][r["coords"][m]] for m in modes] for r in rows])
    vals = np.array([r["value"] for r in rows], dtype=float)
    eids = [r["evidence_id"] for r in rows]
    return snap, modes, dicts, coo, vals, eids


def _dense(modes, dicts, coo, vals):
    shape = tuple(len(dicts[m]) for m in modes)
    if np.prod(shape) > DENSE_CELL_LIMIT:
        raise ValueError(f"dense materialization {shape} exceeds cell limit")
    T = np.zeros(shape)
    for idx, v in zip(coo, vals):
        T[tuple(idx)] += v
    return T


def factor(conn, snapshot_id, method, rank, seed=0, persist=True):
    import tensorly as tl
    from tensorly.decomposition import parafac, tucker, tensor_train
    snap, modes, dicts, coo, vals, eids = load_snapshot(conn, snapshot_id)
    T = tl.tensor(_dense(modes, dicts, coo, vals))
    if method == "cp":
        res = parafac(T, rank=rank, init="random", random_state=seed,
                      n_iter_max=500, tol=1e-9)
        factors = [np.asarray(f) for f in res.factors]
        rec = tl.cp_to_tensor(res)
        payload = {"weights": np.asarray(res.weights).tolist(),
                   "factors": [f.tolist() for f in factors]}
    elif method == "tucker":
        ranks = [min(rank, len(dicts[m])) for m in modes]
        core, facs = tucker(T, rank=ranks, init="random", random_state=seed,
                            n_iter_max=500)
        factors = [np.asarray(f) for f in facs]
        rec = tl.tucker_to_tensor((core, facs))
        payload = {"core": np.asarray(core).tolist(),
                   "factors": [f.tolist() for f in factors]}
    elif method == "tt":
        ranks = [1] + [min(rank, 8)] * (len(modes) - 1) + [1]
        tt = tensor_train(T, rank=ranks)
        factors = [np.asarray(c) for c in tt]
        rec = tl.tt_to_tensor(tt)
        # mode-i row representation for retrieval: unfold core i over its rank legs
        payload = {"cores": [c.tolist() for c in factors]}
    else:
        raise ValueError(method)
    rec = np.asarray(rec)
    err = float(np.linalg.norm(rec - np.asarray(T)) / (np.linalg.norm(np.asarray(T)) + 1e-12))
    params = {"method": method, "rank": rank, "seed": seed}
    repro = hashlib.sha256(np.round(rec, 6).tobytes()).hexdigest()
    art_id = ids.artifact_id(method, snapshot_id, params)
    out = {"artifact_id": art_id, "method": method, "rank": rank, "seed": seed,
           "relative_error": err, "modes": modes, "dicts": dicts,
           "repro_sha256": repro}
    if persist:
        path = DERIVED / f"{art_id}.{method}.json"
        path.write_text(json.dumps({**out, "payload": payload}), encoding="utf-8")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ew.derived_artifacts(artifact_id, kind, snapshot_id, "
                "source_schema_version, ontology_version, compiler_version, params, "
                "path, repro_sha256, canonical_revision) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (artifact_id) DO UPDATE SET repro_sha256=EXCLUDED.repro_sha256",
                (art_id, method, snapshot_id, SCHEMA_VERSION, ONTOLOGY_VERSION,
                 COMPILER_VERSION, json.dumps(params), str(path), repro,
                 snap["canonical_revision"]))
        conn.commit()
    out["_reconstruction"] = rec
    out["_tensor"] = np.asarray(T)
    out["_payload"] = payload
    return out


def contract(conn, snapshot_id, marginalize, retain):
    """Marginalize modes by summation over the SPARSE coordinates; return the
    retained-mode cells with counts and the contributing evidence ids."""
    snap, modes, dicts, coo, vals, eids = load_snapshot(conn, snapshot_id)
    keep = [m for m in modes if m in retain]
    cells = {}
    for row_idx, (idx, v) in enumerate(zip(coo, vals)):
        key = tuple(dicts[m][idx[modes.index(m)]] for m in keep)
        cell = cells.setdefault(key, {"value": 0.0, "evidence_ids": []})
        cell["value"] += v
        cell["evidence_ids"].append(eids[row_idx])
    out = [{"cell": dict(zip(keep, k)), "value": c["value"],
            "evidence_ids": sorted(set(c["evidence_ids"]))}
           for k, c in sorted(cells.items(), key=lambda kv: -kv[1]["value"])]
    return {"snapshot_id": snapshot_id, "retained_modes": keep,
            "marginalized": [m for m in modes if m not in keep],
            "canonical_revision": snap["canonical_revision"], "cells": out}


def score_missing(conn, snapshot_id, method="cp", rank=4, seed=0, top_k=20):
    """Rank UNOBSERVED cells by reconstruction score. Output is hypothesis
    material only — the API layer stores it in ew.hypotheses, never as
    evidence."""
    res = factor(conn, snapshot_id, method, rank, seed=seed, persist=True)
    T, rec = res["_tensor"], res["_reconstruction"]
    observed = set(map(tuple, np.argwhere(T > 0)))
    flat = np.argsort(rec, axis=None)[::-1]
    modes, dicts = res["modes"], res["dicts"]
    out = []
    for f in flat:
        idx = tuple(int(i) for i in np.unravel_index(f, rec.shape))
        if idx in observed:
            continue
        out.append({"coords": {m: dicts[m][idx[i]] for i, m in enumerate(modes)},
                    "score": float(rec[idx])})
        if len(out) >= top_k:
            break
    return {"artifact_id": res["artifact_id"], "method": method, "rank": rank,
            "missing_cells": out}
