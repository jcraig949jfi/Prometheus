"""PAN-10 / PAN-11: Hugging Face Hub intake -- models (with a local-fit estimate for
this program's 16 GB GPUs) and daily papers. Anonymous access only (Q-005), at most
375 calls per 5 minutes (75 percent of the documented anonymous 500) and >= 1 s apart.

The fit estimate is arithmetic on a parameter count, not a measurement: PAN-19 loads
and times models to measure. A quantized repo reports a PACKED parameter count
(research note: an NVFP4 27.78B model shows 18.16B), so such rows are marked
reliable=false rather than trusted.
"""
import datetime as dt
import json
import re

from . import Client, finish_run, new_run, seeds

API = "https://huggingface.co/api/models"
EXPAND = ["author", "pipeline_tag", "library_name", "tags", "createdAt", "lastModified", "downloads", "likes",
          "trendingScore", "safetensors", "gguf", "cardData", "gated"]
QUANT_MARKERS = ("gptq", "awq", "fp8", "nvfp4", "mxfp4", "bnb", "4bit", "4-bit", "8bit", "8-bit", "int4", "int8",
                 "exl2", "mlx", "quantized", "bitsandbytes")
VRAM_GB = 16.0
HEADROOM_GB = 1.5          # KV cache, CUDA context, activations at modest context
Q4_BYTES_PER_PARAM = 0.5625  # ~4.5 bits (Q4_K_M class)


def params_from_name(repo_id):
    """Total parameters from a name like '...-30B-A3B', '...-0.6B', '...-7b'; None if absent."""
    name = repo_id.split("/")[-1]
    m = re.findall(r"(?<![A-Za-z0-9])(\d+(?:\.\d+)?)\s*([BbMm])(?![A-Za-z])", name.replace("_", "-"))
    if not m:
        return None
    vals = [float(v) * (1e9 if u.lower() == "b" else 1e6) for v, u in m]
    return int(max(vals))   # '30B-A3B' -> 30B total (all experts are resident)


def fit(repo_id, tags, safetensors, gguf):
    tags_l = [t.lower() for t in (tags or [])]
    rid = repo_id.lower()
    quant = any(q in rid or any(q in t for t in tags_l) for q in QUANT_MARKERS)
    params, basis = None, "none"
    if gguf and gguf.get("total"):
        params, basis = int(gguf["total"]), "gguf"
    elif safetensors and safetensors.get("total"):
        params, basis = int(safetensors["total"]), "safetensors"
    else:
        p = params_from_name(repo_id)
        if p:
            params, basis = p, "name"
    if params is None:
        return params, basis, dict(reliable=False, basis=basis)
    reliable = not (basis == "safetensors" and quant)
    q4 = params * Q4_BYTES_PER_PARAM / 1e9 + HEADROOM_GB
    fp16 = params * 2 / 1e9 + HEADROOM_GB
    return params, basis, dict(est_gb_q4=round(q4, 2), est_gb_fp16=round(fp16, 2), fits_16gb_q4=q4 <= VRAM_GB,
                               fits_16gb_fp16=fp16 <= VRAM_GB, reliable=reliable, basis=basis, quant_marked=quant)


def _row(m, tag, run_id):
    card = m.get("cardData") or {}
    base = card.get("base_model")
    if isinstance(base, str):
        base = [base]
    params, basis, f = fit(m["id"], m.get("tags"), m.get("safetensors"), m.get("gguf"))
    lic = card.get("license") if isinstance(card.get("license"), str) else json.dumps(card.get("license"))
    return (m["id"], m.get("author") or m["id"].split("/")[0], m.get("pipeline_tag"), m.get("library_name"),
            m.get("tags"), lic, str(m.get("gated")), m.get("createdAt"), m.get("lastModified"), m.get("downloads"),
            m.get("likes"), m.get("trendingScore"), params, basis, json.dumps(m.get("gguf")) if m.get("gguf") else None,
            base, json.dumps(f), [tag], run_id, json.dumps(m))


def upsert_models(cur, models, tag, run_id):
    from psycopg2.extras import execute_values
    if not models:
        return 0
    execute_values(cur, """
        insert into pan.hf_model (repo_id, author, pipeline_tag, library_name, tags, license, gated, created_at,
            last_modified, downloads, likes, trending_score, params_total, params_basis, gguf, base_models, fit,
            query_tags, run_id, raw) values %s
        on conflict (repo_id) do update set pipeline_tag=excluded.pipeline_tag, library_name=excluded.library_name,
            tags=excluded.tags, license=excluded.license, gated=excluded.gated, last_modified=excluded.last_modified,
            downloads=excluded.downloads, likes=excluded.likes, trending_score=excluded.trending_score,
            params_total=excluded.params_total, params_basis=excluded.params_basis, gguf=excluded.gguf,
            base_models=excluded.base_models, fit=excluded.fit, raw=excluded.raw, last_seen_at=now(),
            query_tags=(select array_agg(distinct t) from unnest(pan.hf_model.query_tags || excluded.query_tags) t)""",
                   [_row(m, tag, run_id) for m in models], page_size=500)
    return len(models)


def run_models(per_org=30, out=print):
    from .. import db
    sd = seeds()
    lim = sd["limits"]["huggingface"]
    run_id = new_run("frontier-hf-models", dict(per_org=per_org))
    cl = Client("huggingface", run_id, lim["min_interval_s"], lim["window_s"], lim["max_calls_per_window"])
    counts = dict(orgs={}, discovery={}, failed=[])
    expand = [("expand[]", e) for e in EXPAND]
    with db.cursor() as cur:
        for org in sd["hf_orgs"] + sd["hf_gguf_mirrors"]:
            r = cl.get(API, params=[("author", org), ("sort", "createdAt"), ("direction", "-1"),
                                    ("limit", str(per_org))] + expand)
            if r is None:
                counts["failed"].append(org)
                continue
            n = upsert_models(cur, r.json(), "org:" + org, run_id)
            counts["orgs"][org] = n
        for d in sd["hf_discovery"]:
            r = cl.get(API, params=list(d["params"].items()) + expand)
            if r is None:
                counts["failed"].append(d["tag"])
                continue
            counts["discovery"][d["tag"]] = upsert_models(cur, r.json(), d["tag"], run_id)
        cl.flush(cur)
        cur.execute("""select count(*), count(*) filter (where (fit->>'fits_16gb_q4')::boolean),
                              count(*) filter (where (fit->>'reliable')::boolean is not true) from pan.hf_model""")
        counts["models_total"], counts["fits_16gb_q4"], counts["fit_unreliable"] = cur.fetchone()
    finish_run(run_id, counts, "OK" if not counts["failed"] else "PARTIAL")
    out(json.dumps({k: counts[k] for k in ("failed", "models_total", "fits_16gb_q4", "fit_unreliable")}))
    return counts


def run_daily_papers(days=14, out=print):
    """HF daily papers for the last `days` days -> pan.frontier_item (source hf_daily),
    with upvotes in signals; arXiv ids are the source ids, so the same paper in the
    arXiv intake is joinable on source_id."""
    from .. import db
    from .arxiv import upsert
    sd = seeds()
    lim = sd["limits"]["huggingface"]
    run_id = new_run("frontier-hf-daily", dict(days=days))
    cl = Client("huggingface", run_id, lim["min_interval_s"], lim["window_s"], lim["max_calls_per_window"])
    counts = dict(days={}, failed=[])
    today = dt.datetime.now(dt.timezone.utc).date()
    from psycopg2.extras import execute_values
    with db.cursor() as cur:
        for i in range(days):
            day = (today - dt.timedelta(days=i)).isoformat()
            r = cl.get("https://huggingface.co/api/daily_papers", params=dict(date=day, limit="100"))
            if r is None:
                counts["failed"].append(day)
                continue
            items = []
            for p in r.json():
                pp = p.get("paper") or {}
                if not pp.get("id"):
                    continue
                items.append(dict(source_id=pp["id"], title=" ".join((pp.get("title") or p.get("title") or "").split()),
                                  summary=" ".join((pp.get("summary") or "").split()),
                                  authors=[a.get("name") for a in pp.get("authors") or [] if a.get("name")],
                                  categories=[], primary_cat=None, published_at=pp.get("publishedAt"),
                                  updated_at=None, url="https://huggingface.co/papers/" + pp["id"],
                                  upvotes=pp.get("upvotes"), day=day))
            n = upsert(cur, items, "hf_daily:" + day, run_id, source="hf_daily")
            if items:
                execute_values(cur, """update pan.frontier_item f set signals = f.signals || v.s::jsonb
                                       from (values %s) as v(id, s) where f.source='hf_daily' and f.source_id=v.id""",
                               [(it["source_id"], json.dumps({"upvotes": it["upvotes"], "daily_date": it["day"]}))
                                for it in items])
            counts["days"][day] = n
        cl.flush(cur)
    finish_run(run_id, counts, "OK" if not counts["failed"] else "PARTIAL")
    out(json.dumps(dict(papers=sum(counts["days"].values()), failed=counts["failed"])))
    return counts
