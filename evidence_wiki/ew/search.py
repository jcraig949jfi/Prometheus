"""Multi-paradigm retrieval over the canonical substrate (charter §8, §17).

Modes: lexical BM25, embedding (all-MiniLM-L6-v2), graph traversal over
observed relations, tensor-factor retrieval (CP factor space), and hybrid
reciprocal-rank fusion. Documents are SOURCE VOCABULARY ONLY (claim text,
source wording, verbatim quotes) — canonical dimension terms are deliberately
excluded from text docs so the text baselines are not fed the curated
structure; the tensor path consumes that structure explicitly, which is
exactly the comparison V0 must measure.
"""
import json
import re
from pathlib import Path

import numpy as np

from . import ids
from . import db as ewdb

DERIVED = Path(__file__).resolve().parent.parent / "derived"
_MODEL = None


def _tok(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def corpus_docs(conn):
    """One document per claim (current version), source vocabulary only."""
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT c.* FROM ew.claims_prod c JOIN "
            "(SELECT claim_id, max(version) v FROM ew.claims_prod GROUP BY claim_id) m "
            "ON m.claim_id=c.claim_id AND m.v=c.version "
            "WHERE c.write_stage IN ('SOURCE_BOUND','INDEXED') "
            "ORDER BY c.claim_id")
        claims = cur.fetchall()
        docs = []
        for c in claims:
            cur.execute("SELECT source_quote, metric_text FROM ew.evidence "
                        "WHERE claim_id=%s", (c["claim_id"],))
            ev = cur.fetchall()
            text = " ".join(filter(None, [
                c["text_canonical"], c.get("source_wording") or "",
                c.get("claim_ceiling") or ""
            ] + [e["source_quote"] or "" for e in ev]
              + [e["metric_text"] or "" for e in ev]))
            docs.append({"claim_id": c["claim_id"], "title": c["text_canonical"],
                         "status": c["status"], "agent": c.get("agent_id"),
                         "text": text})
    return docs


class SearchIndex:
    def __init__(self, conn):
        self.conn = conn
        self.docs = corpus_docs(conn)
        self.ids = [d["claim_id"] for d in self.docs]
        from rank_bm25 import BM25Okapi
        self.bm25 = BM25Okapi([_tok(d["text"]) for d in self.docs] or [["x"]])
        self._emb = None
        with conn.cursor() as cur:
            self.canonical_revision = ewdb.canonical_revision(cur)

    # ---------------------------------------------------------- lexical
    def lexical(self, query, k=10):
        scores = self.bm25.get_scores(_tok(query))
        order = np.argsort(scores)[::-1][:k]
        return [{"claim_id": self.ids[i], "score": float(scores[i]),
                 "method": "bm25"} for i in order if scores[i] > 0]

    # -------------------------------------------------------- embedding
    def _model(self):
        global _MODEL
        if _MODEL is None:
            from sentence_transformers import SentenceTransformer
            _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        return _MODEL

    def embeddings(self):
        if self._emb is None:
            cache = DERIVED / f"emb_rev{self.canonical_revision}.npz"
            if cache.exists():
                self._emb = np.load(cache)["emb"]
            else:
                self._emb = self._model().encode(
                    [d["text"] for d in self.docs], normalize_embeddings=True)
                np.savez_compressed(cache, emb=self._emb)
                self._register_artifact("embedding_index", str(cache),
                                        {"model": "all-MiniLM-L6-v2"})
        return self._emb

    def _register_artifact(self, kind, path, params):
        from . import COMPILER_VERSION, ONTOLOGY_VERSION, SCHEMA_VERSION
        aid = ids.artifact_id(kind, None, {**params,
                                           "rev": self.canonical_revision})
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ew.derived_artifacts(artifact_id, kind, snapshot_id, "
                "source_schema_version, ontology_version, compiler_version, "
                "params, path, canonical_revision) "
                "VALUES (%s,%s,NULL,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                (aid, kind, SCHEMA_VERSION, ONTOLOGY_VERSION, COMPILER_VERSION,
                 json.dumps(params), path, self.canonical_revision))
        self.conn.commit()
        return aid

    def semantic(self, query, k=10):
        emb = self.embeddings()
        qv = self._model().encode([query], normalize_embeddings=True)[0]
        scores = emb @ qv
        order = np.argsort(scores)[::-1][:k]
        return [{"claim_id": self.ids[i], "score": float(scores[i]),
                 "method": "embedding"} for i in order]

    def semantic_related(self, claim_id, k=10):
        if claim_id not in self.ids:
            return []
        emb = self.embeddings()
        i = self.ids.index(claim_id)
        scores = emb @ emb[i]
        order = np.argsort(scores)[::-1]
        return [{"claim_id": self.ids[j], "score": float(scores[j]),
                 "method": "embedding"}
                for j in order if j != i][:k]

    # ------------------------------------------------------------ graph
    def graph_neighbors(self, claim_id, hops=2, include_inferred=False):
        seen = {claim_id: 0}
        frontier = [claim_id]
        edges = []
        with ewdb.dict_cur(self.conn) as cur:
            for depth in range(1, hops + 1):
                if not frontier:
                    break
                cls = ["OBSERVED"] + (["INFERRED"] if include_inferred else [])
                cur.execute(
                    "SELECT * FROM ew.relations WHERE epistemic_class = ANY(%s) "
                    "AND (src_id = ANY(%s) OR dst_id = ANY(%s))",
                    (cls, frontier, frontier))
                nxt = []
                for r in cur.fetchall():
                    edges.append(r)
                    for n in (r["src_id"], r["dst_id"]):
                        if n not in seen:
                            seen[n] = depth
                            nxt.append(n)
                frontier = nxt
        return [{"claim_id": n, "score": 1.0 / d, "method": "graph",
                 "hops": d} for n, d in seen.items() if d > 0], edges

    # ----------------------------------------------------------- tensor
    def tensor_related(self, claim_id, factor_result, k=10):
        """Cosine similarity in CP factor space. Each claim's vector is the
        sum over its evidence coordinates of the elementwise product of the
        per-mode factor rows (the CP cell embedding)."""
        modes, dicts = factor_result["modes"], factor_result["dicts"]
        payload = factor_result["_payload"]
        if "factors" not in payload:
            raise ValueError("tensor_related requires cp or tucker factors")
        factors = [np.array(f) for f in payload["factors"]]
        idx = {m: {v: i for i, v in enumerate(dicts[m])} for m in modes}
        with ewdb.dict_cur(self.conn) as cur:
            cur.execute(
                "SELECT e.claim_id, c.coords FROM ew.coordinates c "
                "JOIN ew.evidence e ON e.evidence_id=c.evidence_id "
                "WHERE c.view_name=%s AND e.claim_id IS NOT NULL",
                (factor_result.get("view_name", "evidence_v1"),))
            rows = cur.fetchall()
        vecs = {}
        for r in rows:
            co = r["coords"]
            try:
                cell = np.ones(factors[0].shape[1])
                for mi, m in enumerate(modes):
                    cell = cell * factors[mi][idx[m][co[m]]]
            except KeyError:
                continue
            vecs.setdefault(r["claim_id"], np.zeros_like(cell))
            vecs[r["claim_id"]] += cell
        if claim_id not in vecs:
            return []
        q = vecs[claim_id]
        qn = np.linalg.norm(q) + 1e-12
        out = []
        for cid, v in vecs.items():
            if cid == claim_id:
                continue
            s = float(q @ v / (qn * (np.linalg.norm(v) + 1e-12)))
            out.append({"claim_id": cid, "score": s, "method": "tensor_cp",
                        "artifact_id": factor_result["artifact_id"],
                        "epistemic_note": "latent association, not evidence"})
        out.sort(key=lambda x: -x["score"])
        return out[:k]

    # ----------------------------------------------------------- hybrid
    def hybrid(self, query, k=10):
        ranks = {}
        for res in (self.lexical(query, k=30), self.semantic(query, k=30)):
            for rank, r in enumerate(res):
                ranks.setdefault(r["claim_id"], 0.0)
                ranks[r["claim_id"]] += 1.0 / (60 + rank)
        out = sorted(ranks.items(), key=lambda kv: -kv[1])[:k]
        return [{"claim_id": c, "score": s, "method": "hybrid_rrf"}
                for c, s in out]
