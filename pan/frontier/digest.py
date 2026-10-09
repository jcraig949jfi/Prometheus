"""Frontier digest (charter C5, the reader-facing side of the intake): papers published in
the last `days` days, grouped by the seed topic that surfaced them and ranked by how many
seed queries matched plus Hugging Face daily-paper upvotes; and HF models first seen in
the window that are estimated to fit 16 GB; then lab-blog, newsletter and GitHub-release
feed entries dated in the window (PAN-35) with feed health. Written as pure ASCII to
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


KINDS = (("blog", "Lab blogs"), ("newsletter", "Newsletters"), ("society", "Societies"),
         ("releases", "Releases of tracked repositories"))


def run(days=3, per_topic=6, model_days=14, per_kind=12, out=print):
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
        # order by the QUALIFIED column: a bare "published_at" binds to the ::date output column (day ties -> any
        # order), which once made the digest's "newest" release an arbitrary one of the day
        cur.execute("""select signals->>'kind', signals->>'feed', published_at::date, title, url from pan.frontier_item f
                       where source in ('rss', 'github') and signals->>'kind' in ('blog', 'newsletter', 'society', 'releases')
                       and f.published_at >= %s order by f.published_at desc""",
                    (since,))
        feed_items = cur.fetchall()
        cur.execute("""select count(*), count(*) filter (where last_error is null),
                              string_agg(feed_id || ' (' || coalesce(last_error, '') || ', ' || consecutive_failures || 'x)', '; ')
                                  filter (where last_error is not null), max(last_checked_at)
                       from pan.feed_state where kind in ('blog', 'newsletter', 'society', 'releases')""")
        health = cur.fetchone()
        cur.execute("""select f.published_at::date, raw->>'full_name', (signals->>'stars')::int, signals->>'language',
                              left(coalesce(summary, ''), 90), url from pan.frontier_item f
                       where source = 'github' and signals->>'kind' = 'repo' and f.published_at >= %s
                       order by f.published_at desc limit 20""", (now - dt.timedelta(days=model_days),))
        new_repos = cur.fetchall()
        cur.execute("""select count(*), count(*) filter (where last_error is null), max(last_checked_at)
                       from pan.feed_state where kind in ('gh_owner', 'gh_repo')""")
        gh_health = cur.fetchone()
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
    lines += ["## Feeds: lab blogs, newsletters, societies, tracked releases (dated in the window)", "",
              "Feed health: {} of {} feeds OK at the last poll ({}).{}".format(
                  health[1], health[0],
                  health[3].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ") if health[3] else "never",
                  " Failing: " + ascii_fold(health[2]) if health[2] else ""), ""]
    for kind, name in KINDS:
        rows = [r for r in feed_items if r[0] == kind]
        if not rows:
            continue
        lines += ["### {} ({} entries)".format(name, len(rows)), ""]
        per_feed = {}
        for r in rows:                       # newest first, so each feed's first row is its newest
            per_feed.setdefault(r[1], []).append(r)
        if kind == "releases":
            # one line per repository: nightly / CI tags (llama.cpp builds, pytorch viable/strict) would
            # otherwise fill the section with one repo
            for feed, rs in per_feed.items():
                _, _, pub, title, url = rs[0]
                lines.append("- {} [{}] {} entr{} in the window; newest: {}".format(
                    pub, feed, len(rs), "y" if len(rs) == 1 else "ies",
                    ascii_fold(title.split(" release: ", 1)[-1])[:70]))
                lines.append("    {}".format(ascii_fold(url)[:120]))
        else:
            # at most 3 per feed, so one prolific blog cannot take the whole section
            shown = [r for rs in per_feed.values() for r in rs[:3]]
            for _, feed, pub, title, url in sorted(shown, key=lambda r: r[2], reverse=True)[:per_kind]:
                lines.append("- {} [{}] {}".format(pub, feed, ascii_fold(title)[:100]))
                lines.append("    {}".format(ascii_fold(url)[:120]))
            more = len(rows) - min(len(shown), per_kind)
            if more > 0:
                lines.append("  (+{} more; `python -m pan frontier search` finds them)".format(more))
        lines.append("")
    lines += ["## New repositories from tracked GitHub owners (created in the last {} days)".format(model_days), "",
              "GitHub watch: {} of {} owner/repo endpoints OK at their last poll ({}); anonymous API.".format(
                  gh_health[1], gh_health[0],
                  gh_health[2].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ") if gh_health[2] else "never"), ""]
    if not new_repos:
        lines.append("(none)")
    for created, full, stars, lang, summ, url in new_repos:
        lines.append("- {} {} stars={}{}".format(created, full, stars, " " + lang if lang else ""))
        if summ:
            lines.append("    {}".format(ascii_fold(summ)))
    lines.append("")
    d = REPO / "roles" / "Pan" / "reports" / "frontier"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "DIGEST_{}.md".format(now.strftime("%Y-%m-%d"))
    p.write_text("\n".join(lines), encoding="ascii", errors="replace", newline="\n")
    out("wrote {} ({} papers, {} topics, {} models, {} feed entries)".format(p, len(papers), len(by_topic), len(models),
                                                                         len(feed_items)))
    return p
