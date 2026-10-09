"""Frontier digest (charter C5, the reader-facing side of the intake): papers published in
the last `days` days, grouped by the seed topic that surfaced them and ranked by how many
seed queries matched plus Hugging Face daily-paper upvotes; and HF models first seen in
the window that are estimated to fit 16 GB. Written as pure ASCII to
roles/Pan/reports/frontier/DIGEST_<date>.md. Retrieval output, not a relevance verdict:
items stay UNTYPED (Eos's vocabulary) until a seat types them.
"""
import datetime as dt
import unicodedata

from .. import REPO


def ascii_fold(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")


TOPIC_NAMES = {
    "Q_LLM_EVOLUTION": "LLM-guided program evolution", "Q_PROGRAM_SYNTHESIS": "Program synthesis / ARC",
    "Q_LEAN_PROVERS": "Lean provers", "Q_FALSIFICATION_AGENTS": "Falsification / automated science",
    "Q_OPEN_ENDEDNESS": "Open-endedness / ALife", "Q_SELF_REPLICATION_ALIFE": "Self-replication / soups",
    "Q_NCA_LENIA": "Neural cellular automata / Lenia", "Q_QUALITY_DIVERSITY": "Quality-diversity",
    "Q_ENV_GENERATION_UED": "Environment generation / UED", "Q_SELF_MODIFYING": "Self-modifying agents",
    "Q_WORLD_MODELS": "World models", "Q_LATENT_RECURSIVE": "Latent / recursive reasoning",
    "Q_COGNITIVE_ARCH": "Cognitive architectures",
}


def run(days=3, per_topic=6, model_days=14, out=print):
    from .. import db
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=days)
    lines = ["# Frontier digest {} (last {} days of publications)".format(now.strftime("%Y-%m-%d"), days), "",
             "Generated {} by `python -m pan frontier digest` from pan.frontier_item / pan.hf_model.".format(
                 now.strftime("%Y-%m-%dT%H:%MZ")),
             "Ranking = number of seed queries that matched, then HF upvotes, then date. Items are",
             "retrieval results (UNTYPED); a seat decides whether any is an ANCHOR or ACQUIRE.", ""]
    with db.cursor() as cur:
        cur.execute("""select f.source_id, f.title, f.authors, f.published_at::date, f.query_tags,
                              coalesce((select (h.signals->>'upvotes')::int from pan.frontier_item h
                                        where h.source='hf_daily' and h.source_id=f.source_id), 0) as up
                       from pan.frontier_item f
                       where f.source='arxiv' and f.published_at >= %s""", (since,))
        papers = cur.fetchall()
        # windows are by when an item appeared in the WORLD (publication / repo creation), not when Pan
        # first saw it: on the first digest everything was "first seen" today (found in review, 2026-10-09)
        cur.execute("""select source_id, title, (signals->>'upvotes')::int, published_at::date from pan.frontier_item
                       where source='hf_daily' and published_at >= %s order by (signals->>'upvotes')::int desc nulls last
                       limit 12""", (since,))
        hf_top = cur.fetchall()
        cur.execute("""select repo_id, pipeline_tag, params_total, fit->>'est_gb_q4', license, likes,
                              coalesce((fit->>'reliable')::boolean, false) from pan.hf_model
                       where created_at >= %s and (fit->>'fits_16gb_q4')::boolean
                       and pipeline_tag in ('text-generation', 'feature-extraction', 'text-ranking', 'image-text-to-text')
                       order by likes desc nulls last limit 15""", (now - dt.timedelta(days=model_days),))
        models = cur.fetchall()
    lines.append("{} arXiv papers published since {} in the corpus.".format(len(papers), since.strftime("%Y-%m-%d")))
    lines.append("")
    by_topic = {}
    for p in papers:
        for t in (p[4] or []):
            if t in TOPIC_NAMES:
                by_topic.setdefault(t, []).append(p)
    for t in TOPIC_NAMES:
        items = sorted(by_topic.get(t, []), key=lambda p: (-len([x for x in p[4] if x.startswith("Q_")]), -p[5],
                                                             -(p[3].toordinal() if p[3] else 0)))[:per_topic]
        if not items:
            continue
        lines += ["## {} ({} new)".format(TOPIC_NAMES[t], len(by_topic.get(t, []))), ""]
        for sid, title, authors, pub, tags, up in items:
            au = ", ".join(ascii_fold(a) for a in (authors or [])[:3]) + (" et al." if len(authors or []) > 3 else "")
            lines.append("- {} {}  {}{}".format(sid, pub, ascii_fold(title)[:110], "  (+{} HF)".format(up) if up else ""))
            lines.append("    {}  https://arxiv.org/abs/{}".format(au[:90], sid))
        lines.append("")
    lines += ["## Most upvoted Hugging Face daily papers (published in the same window)", ""]
    for sid, title, up, pub in hf_top:
        lines.append("- {} {} (+{})  {}".format(sid, pub, up or 0, ascii_fold(title)[:100]))
    lines += ["", "## Hugging Face models created in the last {} days, estimated to fit 16 GB at Q4".format(model_days),
              ""]
    if not models:
        lines.append("(none)")
    for rid, pipe, params, est, lic, likes, rel in models:
        lines.append("- {}  [{}] {} q4~{} GB{} lic={} likes={}".format(
            rid, pipe, "{:.1f}B".format(params / 1e9) if params else "?", est, "" if rel else " (estimate UNRELIABLE)",
            lic, likes))
    lines.append("")
    d = REPO / "roles" / "Pan" / "reports" / "frontier"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "DIGEST_{}.md".format(now.strftime("%Y-%m-%d"))
    p.write_text("\n".join(lines), encoding="ascii", errors="replace", newline="\n")
    out("wrote {} ({} papers, {} topics, {} models)".format(p, len(papers), len(by_topic), len(models)))
    return p
