"""PAN-05: embed pan.chunk rows with a local model on this host's GPU.

Vectors are L2-normalised and stored in pan.embedding as real[] of `dims`
(Matryoshka truncation then re-normalisation where the model supports it),
written with COPY. When pgvector exists on the cluster (Q-001) the column
becomes vector(dims) with an HNSW index in one migration; until then search
is in-process over a cached matrix (search.load_matrix).

The model is configuration (PAN_EMBED_MODEL); every row records its model
name, so two models can be compared on the same chunks.
"""
import io
import json
import os
import time
import datetime as dt

from . import host

MODELS = {
    # name: (query prompt handling, stored dims, max tokens, document prefix allowed)
    "Qwen/Qwen3-Embedding-0.6B": dict(query_prompt_name="query", dims=512, max_seq=512),
    "BAAI/bge-small-en-v1.5": dict(query_prefix="Represent this sentence for searching relevant passages: ",
                                   dims=384, max_seq=512),
}
_LOADED = {}


def default_model():
    # Tier 1 is bge-small: measured 2026-10-09 on the M2 RTX 5060 Ti at ~1,050 chunks/s
    # versus ~34 chunks/s for Qwen3-Embedding-0.6B (about 6.5 min vs 3.3 GPU-h for the
    # 394,952-chunk catalog). Which model retrieves better is measured by pan.controls.
    return os.environ.get("PAN_EMBED_MODEL", "BAAI/bge-small-en-v1.5")


def _model(name):
    if name not in _LOADED:
        from sentence_transformers import SentenceTransformer
        import torch
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        kw = {}
        if dev == "cuda":
            kw["model_kwargs"] = {"torch_dtype": torch.float16}
        m = SentenceTransformer(name, device=dev, **kw)
        m.max_seq_length = MODELS.get(name, {}).get("max_seq", 512)
        _LOADED[name] = m
    return _LOADED[name]


def _norm(x, dims):
    import numpy as np
    x = x[:, :dims].astype(np.float32)
    n = np.linalg.norm(x, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return x / n


def encode_docs(texts, name, batch=64):
    m = _model(name)
    v = m.encode(texts, batch_size=batch, convert_to_numpy=True, normalize_embeddings=False, show_progress_bar=False)
    return _norm(v, MODELS.get(name, {}).get("dims", v.shape[1]))


def encode_query(text, name):
    spec = MODELS.get(name, {})
    m = _model(name)
    if spec.get("query_prompt_name"):
        v = m.encode([text], prompt_name=spec["query_prompt_name"], convert_to_numpy=True)
    else:
        v = m.encode([spec.get("query_prefix", "") + text], convert_to_numpy=True)
    return _norm(v, spec.get("dims", v.shape[1]))[0]


def doc_text(path, heading, body, limit=3000):
    head = "{}\n{}\n".format(path, heading) if heading else "{}\n".format(path)
    return (head + body)[:limit]


def run(model=None, limit=0, batch=64, page=4096, out=print):
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
    from . import db, lake
    model = model or default_model()
    dims = MODELS.get(model, {}).get("dims")
    t0 = time.time()
    run_id = "embed-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ"), host().lower())
    with db.cursor() as cur:
        cur.execute("""select count(*) from pan.chunk c where not exists
                       (select 1 from pan.embedding e where e.chunk_id = c.chunk_id and e.model = %s)""", (model,))
        todo = cur.fetchone()[0]
        cur.execute("insert into pan.run (run_id, kind, host, params) values (%s,'embed',%s,%s)",
                    (run_id, host(), json.dumps({"model": model, "dims": dims, "limit": limit, "batch": batch})))
    if limit:
        todo = min(todo, limit)
    out("{} chunks to embed with {} (dims {})".format(todo, model, dims))
    shard_dir = lake() / "vectors" / "shards" / model.replace("/", "__")
    shard_dir.mkdir(parents=True, exist_ok=True)
    done, last_id, shard = 0, 0, 0
    conn = db.connect()
    try:
        cur = conn.cursor()
        while done < todo:
            n = min(page, todo - done)
            cur.execute("""select c.chunk_id, a.path, c.heading, c.body from pan.chunk c
                           join pan.artifact a on a.artifact_id = c.artifact_id
                           where c.chunk_id > %s and not exists (select 1 from pan.embedding e
                                 where e.chunk_id = c.chunk_id and e.model = %s)
                           order by c.chunk_id limit %s""", (last_id, model, n))
            rows = cur.fetchall()
            if not rows:
                break
            texts = [doc_text(p, h, b) for _, p, h, b in rows]
            vecs = encode_docs(texts, model, batch=batch)
            ids = [r[0] for r in rows]
            buf = io.StringIO()
            for cid, v in zip(ids, vecs):
                buf.write("{}\t{}\t{}\t{{{}}}\n".format(cid, model, vecs.shape[1],
                                                       ",".join("{:.6g}".format(x) for x in v)))
            buf.seek(0)
            cur.copy_expert("copy pan.embedding (chunk_id, model, dims, vec) from stdin", buf)
            conn.commit()
            pq.write_table(pa.table({"chunk_id": pa.array(ids, pa.int64()),
                                     "vec": pa.FixedSizeListArray.from_arrays(
                                         pa.array(vecs.astype(np.float16).ravel(), pa.float16()), vecs.shape[1])}),
                           shard_dir / "shard_{:05d}_{}.parquet".format(shard, run_id), compression="zstd")
            shard += 1
            done += len(rows)
            last_id = ids[-1]
            rate = done / max(time.time() - t0, 1e-6)
            out("  {}/{} embedded, {:.0f}/s, eta {:.0f}s".format(done, todo, rate, (todo - done) / max(rate, 1e-6)))
        counts = dict(embedded=done, model=model, dims=dims, seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps(counts), run_id))
        conn.commit()
    finally:
        conn.close()
    out(json.dumps(counts))
    return counts
