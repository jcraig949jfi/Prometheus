"""Run the frozen retrieval controls (pan/tests/known_answers.json) and write every
row: per query, per mode, the top-10 paths, the rank of the first acceptable
answer, the top score, and the verdict against the frozen thresholds.

python -m pan.controls [--modes fts,vector,hybrid] [--out DIR]
"""
import argparse
import datetime as dt
import json
import os
import statistics
import time
from pathlib import Path

from . import PKG, REPO, search

KA = PKG / "tests" / "known_answers.json"


def chunked_paths(paths):
    from . import db
    with db.cursor() as cur:
        cur.execute("select path from pan.artifact where source='git' and n_chunks > 0 and path = any(%s)",
                    (list(paths),))
        return {r[0] for r in cur.fetchall()}


def rank_of(rows, answers):
    for i, r in enumerate(rows, 1):
        if r["path"] in answers:
            return i
    return None


def plant(marker, body, model):
    """Insert a planted artifact + chunk (+ embedding when a model is given)."""
    from . import db, embed
    with db.cursor() as cur:
        cur.execute("""insert into pan.artifact (source, host, path, kind, is_text, n_chunks, title)
                       values ('plant','test',%s,'doc',true,1,'plant') returning artifact_id""",
                    ("PLANT/" + marker + ".md",))
        aid = cur.fetchone()[0]
        cur.execute("""insert into pan.chunk (artifact_id, ord, line_start, line_end, heading, body, n_chars)
                       values (%s,0,1,1,'plant',%s,%s) returning chunk_id""", (aid, body, len(body)))
        cid = cur.fetchone()[0]
        if model:
            v = embed.encode_docs([embed.doc_text("PLANT/" + marker + ".md", "plant", body)], model)[0]
            cur.execute("insert into pan.embedding (chunk_id, model, dims, vec) values (%s,%s,%s,%s)",
                        (cid, model, len(v), [float(x) for x in v]))
    return aid, cid


def unplant(aid):
    from . import db
    with db.cursor() as cur:
        cur.execute("delete from pan.artifact where artifact_id=%s and source='plant'", (aid,))


def run(modes=("fts", "vector", "hybrid"), out_dir=None, model=None, qset=None, fts_semantics="or", rerank=None,
        label="v1", pool=30):
    import functools
    import numpy as np
    from . import embed
    spec = json.loads(KA.read_text(encoding="utf-8"))
    if qset:
        spec["queries"] = json.loads(Path(qset).read_text(encoding="utf-8"))["queries"]
    fns = dict(fts=functools.partial(search.fts, semantics=fts_semantics), vector=search.vector,
               hybrid=functools.partial(search.hybrid, rerank=rerank, fts_semantics=fts_semantics, pool=pool))
    model = model or embed.default_model()
    qs = spec["queries"]
    evaluable = chunked_paths({p for q in qs for p in q["answers"]})
    rows = []
    t0 = time.time()
    for q in qs:
        ok_answers = [a for a in q["answers"] if a in evaluable]
        for mode in modes:
            t = time.time()
            try:
                res = fns[mode](q["q"], k=10)
                err = None
            except Exception as e:
                res, err = [], "{}: {}".format(type(e).__name__, e)
            rows.append(dict(id=q["id"], type=q["type"], mode=mode, query=q["q"], answers=q["answers"],
                             evaluable=bool(ok_answers), rank=rank_of(res, set(q["answers"])),
                             top1_score=(res[0].get("rrf", res[0].get("score")) if res else None),
                             top10=[r["path"] for r in res], seconds=round(time.time() - t, 3), error=err))
    n_eval = sum(1 for q in qs if any(a in evaluable for a in q["answers"]))

    def recall(mode, typ=None, k=10):
        sel = [r for r in rows if r["mode"] == mode and r["evaluable"] and (typ is None or r["type"] == typ)]
        return (sum(1 for r in sel if r["rank"] and r["rank"] <= k) / len(sel)) if sel else None, len(sel)

    summary = {}
    for mode in modes:
        summary[mode] = dict(all=recall(mode), lexical=recall(mode, "lexical"), paraphrase=recall(mode, "paraphrase"),
                             r1=recall(mode, None, 1), r5=recall(mode, None, 5),
                             median_s=statistics.median([r["seconds"] for r in rows if r["mode"] == mode]))

    # NEGATIVE
    neg = []
    for nq in spec["nonsense"]:
        f = search.fts(nq, k=5, semantics=fts_semantics)
        try:
            v = search.vector(nq, k=5)
        except Exception:
            v = []
        neg.append(dict(query=nq, fts_rows=len(f), fts_best_cov=(f[0].get("cov") if f else None),
                        vector_top1=(v[0]["score"] if v else None),
                        vector_top=[r["path"] for r in v[:3]]))
    pos_v_top1 = [r["top1_score"] for r in rows if r["mode"] == "vector" and r["top1_score"] is not None]
    p25 = float(np.percentile(pos_v_top1, 25)) if pos_v_top1 else None

    # CHEAT
    pl = spec["plant"]
    aid, cid = plant(pl["marker"], pl["body"], model if "vector" in modes else None)
    search._CACHE.clear()
    try:
        f_rank = rank_of(search.fts(pl["marker"], k=5), {"PLANT/" + pl["marker"] + ".md"})
        ids, m = search.load_matrix(model, refresh=False)
        # the planted vector is not in the cached matrix: append it in memory, as a fresh cache would
        from . import db
        with db.cursor() as cur:
            cur.execute("select vec from pan.embedding where chunk_id=%s and model=%s", (cid, model))
            r = cur.fetchone()
        if r is not None and len(ids):
            search._CACHE[model] = (np.concatenate([ids, [cid]]),
                                    np.vstack([m, np.asarray([r[0]], dtype=np.float16)]))
        v_rank = rank_of(search.vector(pl["paraphrase"], k=3), {"PLANT/" + pl["marker"] + ".md"}) \
            if "vector" in modes else None
    finally:
        unplant(aid)
        search._CACHE.clear()
    gone = rank_of(search.fts(pl["marker"], k=5), {"PLANT/" + pl["marker"] + ".md"}) is None

    verdict = {}
    if n_eval < 15:
        verdict["overall"] = "INDETERMINATE (only {} evaluable queries)".format(n_eval)
    h = summary.get("hybrid", {}).get("all", (None, 0))[0]
    fl = summary.get("fts", {}).get("lexical", (None, 0))[0]
    vp = summary.get("vector", {}).get("paraphrase", (None, 0))[0]
    verdict["positive_hybrid_all>=0.80"] = None if h is None else h >= 0.80
    verdict["positive_fts_lexical>=0.60"] = None if fl is None else fl >= 0.60
    verdict["positive_vector_paraphrase>=0.60"] = None if vp is None else vp >= 0.60
    # v1 (OR semantics) is expected to return rows for nonsense that shares a common word
    # ("lattice", "recipe"); the frozen v0 criterion is reported as is, and the coverage of the
    # best row is recorded beside it so the reader can see what matched.
    verdict["negative_fts_zero_rows"] = all(n["fts_rows"] == 0 for n in neg)
    verdict["negative_vector_below_p25"] = None if p25 is None else all(
        (n["vector_top1"] is not None and n["vector_top1"] < p25) for n in neg)
    verdict["cheat_fts_rank1"] = f_rank == 1
    verdict["cheat_vector_top3"] = None if v_rank is None and "vector" not in modes else (v_rank is not None)
    verdict["cheat_removed"] = gone
    result = dict(when=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), model=model, label=label,
                  qset=str(qset or KA), fts_semantics=fts_semantics, rerank=rerank, pool=pool,
                  evaluable_queries=n_eval, summary=summary, negative=neg, positive_vector_top1_p25=p25,
                  cheat=dict(fts_rank=f_rank, vector_rank=v_rank, removed=gone), verdict=verdict, rows=rows,
                  seconds=round(time.time() - t0, 1))
    if out_dir:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
        p = out_dir / "CONTROLS_{}_{}.json".format(stamp, label)
        p.write_text(json.dumps(result, indent=1, default=str), encoding="utf-8", newline="\n")
        result["written"] = str(p)
    return result


def main():
    os.environ.setdefault("EW_DB_HOST", "192.168.1.202")
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="fts,vector,hybrid")
    ap.add_argument("--out", default=str(REPO / "roles" / "Pan" / "reports" / "controls"))
    ap.add_argument("--model", default=None)
    ap.add_argument("--qset", default=None)
    ap.add_argument("--fts", default="or", choices=["or", "and"])
    ap.add_argument("--rerank", default=None)
    ap.add_argument("--label", default="v1")
    ap.add_argument("--pool", type=int, default=30)
    a = ap.parse_args()
    r = run(tuple(a.modes.split(",")), a.out, a.model, a.qset, a.fts, a.rerank, a.label, a.pool)
    print(json.dumps({k: r[k] for k in ("evaluable_queries", "summary", "negative", "positive_vector_top1_p25",
                                         "cheat", "verdict", "seconds", "written") if k in r}, indent=1, default=str))


if __name__ == "__main__":
    main()
