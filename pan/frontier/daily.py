"""Daily frontier refresh (charter C5): newest arXiv items per seed query, Hugging Face
daily papers for the last two days, the HF model listings, then vectors for any new
items. Polite by the same limits (seeds.json). Skips itself when the last daily run
finished less than `min_age_h` hours ago, and says so.

Productivity signal (base rule 8): new_items and new_models; a run that finds nothing
new reports that, it is not counted as work.
"""
import json
import time


def run(min_age_h=20.0, force=False, out=print):
    from .. import db
    from . import arxiv, hf, query
    with db.cursor() as cur:
        cur.execute("""select extract(epoch from now() - max(finished_at)) / 3600 from pan.run
                       where kind = 'frontier-daily' and status = 'OK'""")
        age = cur.fetchone()[0]
        cur.execute("select count(*) from pan.frontier_item")
        items0 = cur.fetchone()[0]
        cur.execute("select count(*) from pan.hf_model")
        models0 = cur.fetchone()[0]
    if age is not None and float(age) < min_age_h and not force:
        res = dict(skipped=True, last_run_age_h=round(float(age), 1), min_age_h=min_age_h)
        out(json.dumps(res))
        return res
    from . import new_run, finish_run
    run_id = new_run("frontier-daily", {"min_age_h": min_age_h})
    t0 = time.time()
    a = arxiv.run(max_results=50, include_authors=True, include_ids=False, out=lambda *_: None)
    d = hf.run_daily_papers(days=2, out=lambda *_: None)
    m = hf.run_models(out=lambda *_: None)
    e = query.embed_items(out=lambda *_: None)
    with db.cursor() as cur:
        cur.execute("select count(*) from pan.frontier_item")
        items1 = cur.fetchone()[0]
        cur.execute("select count(*) from pan.hf_model")
        models1 = cur.fetchone()[0]
    from .. import iceberg
    snap = iceberg.snapshot_frontier()
    res = dict(new_items=items1 - items0, new_models=models1 - models0, vectors_new=e, iceberg_snapshot=snap,
               arxiv_failed=a.get("failed"), hf_daily_failed=d.get("failed"), hf_models_failed=m.get("failed"),
               seconds=round(time.time() - t0, 1))
    finish_run(run_id, res, "OK")
    out(json.dumps(res))
    return res
