"""Read side of the frontier intake: full-text over papers, and a model finder."""


def search_cli(q, k=15):
    from .. import db
    with db.cursor(statement_timeout_ms=60000) as cur:
        cur.execute("""
          with lx as (select distinct lexeme as l from unnest(to_tsvector('english', %(q)s))),
          tq as (select string_agg(quote_literal(l), ' | ')::tsquery as tq, count(*) as n from lx),
          hits as (select f.*, ts_rank_cd(f.tsv, tq.tq, 32) as r,
                          (select count(*) from lx where f.tsv @@ quote_literal(lx.l)::tsquery) as cov
                   from pan.frontier_item f, tq where f.tsv @@ tq.tq)
          select h.source, h.source_id, h.published_at::date, h.title, h.cov, tq.n, h.query_tags,
                 h.signals->>'upvotes'
          from hits h, tq where h.cov >= greatest(1, ceil(tq.n * 0.34))
          order by h.cov desc, h.r desc limit %(k)s""", dict(q=q, k=k))
        for src, sid, pub, title, cov, n, tags, up in cur.fetchall():
            print("{} {:<11} {} [{}/{}] {}{}".format(src[:6], sid, pub, cov, n, (title or "")[:95],
                                                     " (+{} upvotes)".format(up) if up else ""))
            print("      tags: " + ", ".join((tags or [])[:4]))


def models_cli(q, k=15, fits=False):
    from .. import db
    where = "(repo_id ilike %(p)s or %(q)s = '' or exists (select 1 from unnest(tags) t where t ilike %(p)s))"
    if fits:
        where += " and (fit->>'fits_16gb_q4')::boolean"
    with db.cursor() as cur:
        cur.execute("""select repo_id, pipeline_tag, params_total, params_basis, fit->>'est_gb_q4',
                              fit->>'reliable', license, last_modified::date, downloads, likes
                       from pan.hf_model where {} order by trending_score desc nulls last, likes desc nulls last
                       limit %(k)s""".format(where), dict(p="%" + q + "%", q=q, k=k))
        for r in cur.fetchall():
            params = "{:.1f}B".format(r[2] / 1e9) if r[2] else "?"
            print("{:<55} {:<20} {:>7} ({}) q4~{}GB rel={} lic={} mod={} dl={} likes={}".format(
                r[0][:55], (r[1] or "")[:20], params, r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
