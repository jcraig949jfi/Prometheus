"""Evidence Wiki UI — server-rendered projections of the canonical substrate.

Same objects as the API (gate G16); every page descends to raw provenance;
epistemic class is always badged (gate G2/§22). No external assets.
"""
import html
import json
from urllib.parse import parse_qs

from . import db as ewdb
from . import store

CSS = """
<style>
:root{--bg:#faf9f6;--ink:#1f2328;--line:#d8d4cc;--card:#fff}
body{font-family:Georgia,serif;background:var(--bg);color:var(--ink);margin:0}
header{background:#26343f;color:#f4efe6;padding:.7rem 1.2rem}
header a{color:#f4efe6;text-decoration:none;margin-right:1rem}
header .brand{font-weight:bold;letter-spacing:.06em}
main{max-width:1000px;margin:1.2rem auto;padding:0 1rem}
h1,h2{font-weight:normal}
.card{background:var(--card);border:1px solid var(--line);border-radius:6px;
      padding: .8rem 1rem;margin:.6rem 0}
.badge{font-family:monospace;font-size:.72rem;padding:.1rem .45rem;
       border-radius:9px;margin-left:.4rem;white-space:nowrap}
.b-source{background:#e2efe2;color:#1d5c1d;border:1px solid #9dc79d}
.b-model{background:#fdf3dc;color:#7a5a00;border:1px solid #e0c37a}
.b-tensor{background:#efe3f7;color:#5b2d84;border:1px dashed #b18ad1}
.b-hypo{background:#fdeaea;color:#9c2b2b;border:1px dashed #d99}
.b-human{background:#e3ecf7;color:#1d4c7a;border:1px solid #8fb3d9}
.b-status{background:#eee;border:1px solid #bbb;color:#333}
.neg{border-left:4px solid #b23}
.pos{border-left:4px solid #2a7}
small.meta{color:#666}
blockquote{border-left:3px solid var(--line);margin:.4rem 0;padding:.2rem .8rem;
           color:#444;font-style:italic}
table{border-collapse:collapse}td,th{border:1px solid var(--line);
      padding:.3rem .6rem;font-size:.9rem}
a{color:#1d4c7a}
.warn{background:#fff5e8;border:1px solid #e0c37a;padding:.6rem 1rem;
      border-radius:6px;font-size:.9rem}
</style>"""

NAV = ("<header><span class='brand'>PROMETHEUS EVIDENCE WIKI</span> "
       "<a href='/wiki'>Home</a><a href='/wiki/claims'>Claims</a>"
       "<a href='/wiki/agents'>Agents</a><a href='/wiki/mechanisms'>Mechanisms</a>"
       "<a href='/wiki/failures'>Failures</a>"
       "<a href='/wiki/contradictions'>Contradictions</a>"
       "<a href='/wiki/open'>Open Questions</a>"
       "<a href='/wiki/orphans'>Orphans</a>"
       "<a href='/wiki/latent'>Latent&nbsp;⚠</a></header>")


def esc(s):
    return html.escape(str(s if s is not None else ""))


def badge_method(m):
    cls = {"HUMAN": "b-human", "EXPERIMENT": "b-source",
           "MODEL_EXTRACTED": "b-model", "TENSOR_INFERRED": "b-tensor"}
    lbl = {"HUMAN": "HUMAN RULING", "EXPERIMENT": "SOURCE FACT",
           "MODEL_EXTRACTED": "MODEL EXTRACTED",
           "TENSOR_INFERRED": "TENSOR INFERRED"}
    return f"<span class='badge {cls.get(m,'b-status')}'>{lbl.get(m, esc(m))}</span>"


def badge_class(c):
    cls = {"OBSERVED": "b-source", "INFERRED": "b-tensor",
           "HYPOTHESIZED": "b-hypo"}
    return f"<span class='badge {cls.get(c,'b-status')}'>{esc(c)}</span>"


def badge_status(s):
    return f"<span class='badge b-status'>{esc(s)}</span>"


def page(title, body):
    return (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{esc(title)}</title>{CSS}</head><body>{NAV}"
            f"<main><h1>{esc(title)}</h1>{body}</main></body></html>")


def _current_claims(cur, where="true", args=()):
    cur.execute(
        "SELECT c.* FROM ew.claims c JOIN (SELECT claim_id, max(version) v "
        "FROM ew.claims GROUP BY claim_id) m ON m.claim_id=c.claim_id AND "
        f"m.v=c.version WHERE {where} ORDER BY c.agent_id, c.claim_id", args)
    return cur.fetchall()


def claim_row(c):
    neg = "neg" if c["status"] in ("REFUTED", "RETRACTED", "NOT_ESTABLISHED") else "pos"
    return (f"<div class='card {neg}'><a href='/wiki/claims/{c['claim_id']}'>"
            f"{esc(c['text_canonical'])}</a> {badge_status(c['status'])}"
            f"{badge_method(c['creation_method'])}"
            f"<br><small class='meta'>{esc(c['agent_id'])} · {c['claim_id']}"
            + (f" · ceiling: {esc(c['claim_ceiling'])}" if c["claim_ceiling"] else "")
            + "</small></div>")


def home(cur):
    counts = {}
    for t in ("claims", "evidence", "relations", "hypotheses", "source_packets"):
        cur.execute(f"SELECT count(*) c FROM ew.{t}")
        counts[t] = cur.fetchone()["c"]
    body = ("<div class='card'>One knowledge substrate, many representations. "
            "Everything on these pages traces to source packets; "
            "<span class='badge b-tensor'>TENSOR INFERRED</span> and "
            "<span class='badge b-hypo'>HYPOTHESIZED</span> items are NOT evidence.</div>"
            "<div class='card'>" + " · ".join(
                f"{v} {k}" for k, v in counts.items()) + "</div>"
            "<form action='/wiki/search'><input name='q' size='40' "
            "placeholder='search claims and evidence…'>"
            "<button>Search</button></form>")
    return page("Evidence Wiki", body)


def search_page(conn, cur, qs):
    q = (parse_qs(qs).get("q") or [""])[0]
    if not q:
        return page("Search", "<p>Empty query.</p>")
    from .search import SearchIndex
    ix = SearchIndex(conn)
    hits = ix.hybrid(q, k=15)
    rows = []
    for h in hits:
        cs = _current_claims(cur, "c.claim_id=%s", (h["claim_id"],))
        if cs:
            rows.append(claim_row(cs[0]))
    return page(f"Search: {q}", "".join(rows) or "<p>No results.</p>")


def claims_index(cur):
    return page("Claims", "".join(claim_row(c) for c in _current_claims(cur)))


def claim_page(conn, cur, claim_id):
    data = store.get_claim(conn, claim_id)
    if not data:
        return page("Unknown claim", "<p>No such claim.</p>")
    c = data["current"]
    body = [f"<div class='card'><b>{esc(c['text_canonical'])}</b> "
            f"{badge_status(c['status'])}{badge_method(c['creation_method'])}"]
    if c["source_wording"] and c["source_wording"] != c["text_canonical"]:
        body.append(f"<blockquote>source wording: {esc(c['source_wording'])}</blockquote>")
    if c["claim_ceiling"]:
        body.append(f"<p><b>Claim ceiling:</b> {esc(c['claim_ceiling'])}</p>")
    body.append(f"<small class='meta'>agent {esc(c['agent_id'])} · "
                f"version {c['version']} · stage {esc(c['write_stage'])} · "
                f"ontology v{c['ontology_version']}</small></div>")
    if len(data["versions"]) > 1:
        body.append("<h2>History</h2>")
        for v in data["versions"][1:]:
            body.append(f"<div class='card'>v{v['version']}: "
                        f"{esc(v['text_canonical'])} {badge_status(v['status'])}</div>")
    body.append("<h2>Evidence</h2>")
    for e in data["evidence"]:
        neg = "neg" if e["negative"] else "pos"
        body.append(
            f"<div class='card {neg}'>{badge_method(e['creation_method'])} "
            f"<span class='badge b-status'>{esc(e['evidence_type'])}</span> "
            f"{badge_status(e['outcome_canonical'])}"
            f"<blockquote>{esc(e['source_quote'])}</blockquote>"
            + (f"<p>metrics: <code>{esc(e['metric_text'])}</code></p>" if e["metric_text"] else "")
            + (f"<p>gate: {esc(e['gate'])}</p>" if e["gate"] else "")
            + f"<small class='meta'><a href='/wiki/provenance/{e['evidence_id']}'>"
              f"provenance ⛓</a> · {e['evidence_id']} · span {esc(e['source_span'])}"
              f"</small></div>")
    obs = [r for r in data["relations"] if r["epistemic_class"] == "OBSERVED"]
    inf = [r for r in data["relations"] if r["epistemic_class"] != "OBSERVED"]
    body.append("<h2>Relations (observed)</h2>")
    for r in obs:
        other = r["dst_id"] if r["src_id"] == claim_id else r["src_id"]
        arrow = "→" if r["src_id"] == claim_id else "←"
        body.append(f"<div class='card'>{arrow} <b>{esc(r['relation_type'])}</b> "
                    f"<a href='/wiki/claims/{other}'>{other}</a> "
                    f"{badge_class(r['epistemic_class'])}{badge_method(r['creation_method'])}"
                    + (f"<br><small class='meta'>{esc(r['rationale'])}</small>" if r["rationale"] else "")
                    + "</div>")
    if inf:
        body.append("<h2>Latent relationships ⚠</h2><div class='warn'>"
                    "The following are inferred or hypothesized — they are "
                    "NOT evidence.</div>")
        for r in inf:
            other = r["dst_id"] if r["src_id"] == claim_id else r["src_id"]
            body.append(f"<div class='card'>{esc(r['relation_type'])} "
                        f"<a href='/wiki/claims/{other}'>{other}</a> "
                        f"{badge_class(r['epistemic_class'])}"
                        f"{badge_method(r['creation_method'])} "
                        f"score={r['confidence']}</div>")
    return page(c["text_canonical"][:70], "".join(body))


def provenance_page(conn, object_id):
    chain = store.provenance_chain(conn, object_id)
    body = []
    for link in chain:
        body.append(f"<div class='card'><b>{esc(link['layer'])}</b>"
                    f"<pre style='white-space:pre-wrap'>"
                    f"{esc(json.dumps(link['object'], indent=1, default=str)[:2500])}"
                    f"</pre></div>")
    return page(f"Provenance: {object_id}", "".join(body) or "<p>Unknown object.</p>")


def agents_page(cur):
    cur.execute("SELECT agent_id, count(*) n FROM ew.claims GROUP BY agent_id "
                "ORDER BY n DESC")
    rows = "".join(f"<div class='card'><a href='/wiki/agents/{esc(r['agent_id'])}'>"
                   f"{esc(r['agent_id'])}</a> — {r['n']} claims</div>"
                   for r in cur.fetchall())
    return page("Agents", rows)


def agent_page(cur, agent):
    cs = _current_claims(cur, "c.agent_id=%s", (agent,))
    groups = {"Established/Supported": [], "Refuted/Retracted": [], "Other": []}
    for c in cs:
        if c["status"] in ("ESTABLISHED", "SUPPORTED", "OBSERVED"):
            groups["Established/Supported"].append(c)
        elif c["status"] in ("REFUTED", "RETRACTED", "NOT_ESTABLISHED"):
            groups["Refuted/Retracted"].append(c)
        else:
            groups["Other"].append(c)
    body = []
    for g, items in groups.items():
        if items:
            body.append(f"<h2>{g}</h2>" + "".join(claim_row(c) for c in items))
    return page(f"Agent: {agent}", "".join(body))


def mechanisms_page(cur, term=None):
    if term is None:
        cur.execute("SELECT d.term_id, d.label, count(t.evidence_id) n "
                    "FROM ew.dim_terms d LEFT JOIN ew.term_mappings m "
                    "ON m.dimension=d.dimension AND m.term_id=d.term_id "
                    "LEFT JOIN ew.evidence_terms t ON t.dimension=d.dimension "
                    "AND t.source_term=m.source_term "
                    "WHERE d.dimension='mechanism' GROUP BY 1,2 ORDER BY n DESC")
        rows = "".join(
            f"<div class='card'><a href='/wiki/mechanisms/{esc(r['term_id'])}'>"
            f"{esc(r['label'])}</a> — {r['n']} evidence rows</div>"
            for r in cur.fetchall())
        return page("Mechanisms", rows)
    cur.execute(
        "SELECT DISTINCT e.*, t.source_term FROM ew.evidence e "
        "JOIN ew.evidence_terms t ON t.evidence_id=e.evidence_id "
        "JOIN ew.term_mappings m ON m.dimension=t.dimension "
        "AND m.source_term=t.source_term WHERE m.term_id=%s "
        "AND t.dimension='mechanism'", (term,))
    body = []
    for e in cur.fetchall():
        body.append(f"<div class='card'>{badge_status(e['outcome_canonical'])} "
                    f"agent {esc(e['agent_id'])} · source term "
                    f"“{esc(e['source_term'])}”"
                    f"<blockquote>{esc(e['source_quote'][:400])}</blockquote>"
                    f"<small class='meta'><a href='/wiki/claims/{e['claim_id']}'>"
                    f"claim</a> · <a href='/wiki/provenance/{e['evidence_id']}'>"
                    f"provenance ⛓</a></small></div>")
    return page(f"Mechanism: {term}",
                "<div class='warn'>Cross-agent links via a shared canonical "
                "mechanism; source vocabulary shown per row.</div>" + "".join(body))


def failures_page(cur):
    cur.execute("SELECT e.*, c.text_canonical FROM ew.evidence e LEFT JOIN "
                "ew.claims c ON c.claim_id=e.claim_id AND c.version=1 "
                "WHERE e.negative ORDER BY e.agent_id")
    body = []
    for e in cur.fetchall():
        body.append(f"<div class='card neg'>"
                    f"<span class='badge b-status'>{esc(e['evidence_type'])}</span>"
                    f" {esc(e['agent_id'])}: {esc((e['text_canonical'] or '')[:120])}"
                    f"<blockquote>{esc(e['source_quote'][:300])}</blockquote>"
                    f"<small class='meta'><a href='/wiki/claims/{e['claim_id']}'>claim</a>"
                    f" · <a href='/wiki/provenance/{e['evidence_id']}'>provenance ⛓</a>"
                    f"</small></div>")
    return page("Failures & Negative Results",
                "<div class='warn'>Failure is a first-class knowledge object. "
                "Reuse edges (REUSES_NEGATIVE_EVIDENCE) appear on claim pages."
                "</div>" + "".join(body))


def contradictions_page(conn):
    rows = store.contradictions(conn)
    body = []
    for r in rows:
        body.append(
            f"<div class='card neg'><b>{esc(r['relation_type'])}</b> "
            f"<a href='/wiki/claims/{r['src_id']}'>{r['src_id']}</a> vs "
            f"<a href='/wiki/claims/{r['dst_id']}'>{r['dst_id']}</a> "
            f"{badge_class(r['epistemic_class'])}<br>"
            f"classification: <b>{esc(r['classification'])}</b>"
            + ("".join(f"<br><small class='meta'>differs on {esc(d['dimension'])}: "
                       f"{esc(d['side_a'])} vs {esc(d['side_b'])}</small>"
                       for d in r["differing_dimensions"]))
            + (f"<br><small class='meta'>{esc(r['rationale'])}</small>" if r.get("rationale") else "")
            + "</div>")
    return page("Contradictions",
                "<div class='warn'>Both sides stored; nothing averaged away. "
                "APPARENT_UNDER_DIFFERING_CONDITIONS = candidate conditional "
                "structure, not resolution.</div>" + "".join(body))


def open_page(cur):
    cs = _current_claims(cur, "c.status IN ('OPEN','NOT_ESTABLISHED','UNADJUDICABLE')")
    return page("Open Questions", "".join(claim_row(c) for c in cs))


def orphans_page(cur):
    cur.execute(
        "SELECT c.* FROM ew.claims c JOIN (SELECT claim_id, max(version) v FROM "
        "ew.claims GROUP BY claim_id) m ON m.claim_id=c.claim_id AND m.v=c.version "
        "WHERE NOT EXISTS (SELECT 1 FROM ew.relations r WHERE r.relation_type IN "
        "('CONSUMED_BY','DEPENDS_ON','REUSES_NEGATIVE_EVIDENCE') AND "
        "(r.src_id=c.claim_id OR r.dst_id=c.claim_id))")
    cs = cur.fetchall()
    return page("Orphaned Findings",
                "<div class='warn'>Claims with no recorded consumer or "
                "dependency edge — produced but (so far) metabolically dead."
                "</div>" + "".join(claim_row(c) for c in cs))


def latent_page(cur):
    cur.execute("SELECT * FROM ew.hypotheses ORDER BY score DESC NULLS LAST LIMIT 50")
    body = ["<div class='warn'><b>Everything on this page is inferential.</b> "
            "These are candidate experiments surfaced by decompositions and "
            "link prediction — they carry NO evidence status and can never "
            "gain one without a real experiment.</div>"]
    for h in cur.fetchall():
        body.append(f"<div class='card'>{badge_class('HYPOTHESIZED')} "
                    f"<span class='badge b-tensor'>{esc(h['method'])}</span> "
                    f"score={h['score']}<br>{esc(h['statement'])}"
                    f"<br><small class='meta'>{h['hypothesis_id']} · artifact "
                    f"{esc(h['derived_artifact_id'])}</small></div>")
    return page("Latent Structure & Missing Experiments ⚠", "".join(body))


def render(conn, path):
    path = (path or "").strip("/")
    seg = path.split("/") if path else []
    qs = ""
    if seg and "?" in seg[-1]:
        seg[-1], qs = seg[-1].split("?", 1)
    with ewdb.dict_cur(conn) as cur:
        if not seg:
            return home(cur)
        head = seg[0]
        if head == "search":
            return search_page(conn, cur, qs)
        if head == "claims":
            return claim_page(conn, cur, seg[1]) if len(seg) > 1 else claims_index(cur)
        if head == "provenance" and len(seg) > 1:
            return provenance_page(conn, seg[1])
        if head == "agents":
            return agent_page(cur, seg[1]) if len(seg) > 1 else agents_page(cur)
        if head == "mechanisms":
            return mechanisms_page(cur, seg[1] if len(seg) > 1 else None)
        if head == "failures":
            return failures_page(cur)
        if head == "contradictions":
            return contradictions_page(conn)
        if head == "open":
            return open_page(cur)
        if head == "orphans":
            return orphans_page(cur)
        if head == "latent":
            return latent_page(cur)
    return page("Not found", "<p>No such page.</p>")
