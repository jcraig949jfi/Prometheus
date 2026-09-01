"""Atlas-level maps: coverage grid, epoch/region matrices, lineage graph.

The headline output is the EMPTY CELLS table. A catalog's value is not its row
count -- it is whether it can answer 'which world would most change what we
know'. Empty and thin cells in the declared grid are that answer, written down.
"""
from __future__ import annotations

import collections
import json
import pathlib

import utf8  # noqa: F401
import classify
import store
import taxonomy as T

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "ATLAS.md"
REPORT_DIR = HERE / "reports"


def _tab(rows, head):
    w = [len(h) for h in head]
    for r in rows:
        for i, c in enumerate(r):
            w[i] = max(w[i], len(str(c)))
    L = ["| " + " | ".join(h.ljust(w[i]) for i, h in enumerate(head)) + " |",
         "| " + " | ".join("-" * w[i] for i in range(len(head))) + " |"]
    for r in rows:
        L.append("| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(r)) + " |")
    return "\n".join(L)


def coverage(con):
    """Per-field value counts across the declared vector, plus unfilled cells."""
    out = {}
    total = con.execute("SELECT COUNT(*) FROM worlds").fetchone()[0]
    for f in T.DECLARED_VECTOR:
        got = {r["v"]: r["n"] for r in con.execute(
            "SELECT %s AS v, COUNT(*) AS n FROM worlds WHERE %s IS NOT NULL"
            " GROUP BY %s" % (f, f, f))}
        vocab = T.VOCAB.get(f, [])
        out[f] = {"counts": got,
                  "empty": [v for v in vocab if got.get(v, 0) == 0],
                  "thin": [v for v in vocab if 0 < got.get(v, 0) <= 2],
                  "null": total - sum(got.values())}
    return out, total


def cross(con, a, b, limit_a=12, limit_b=12):
    """Two-way matrix over any pair of scalar columns."""
    rows = con.execute(
        "SELECT %s AS a, %s AS b, COUNT(*) AS n FROM worlds"
        " WHERE %s IS NOT NULL AND %s IS NOT NULL GROUP BY a, b" % (a, b, a, b))
    m = collections.defaultdict(int)
    ca, cb = collections.Counter(), collections.Counter()
    for r in rows:
        m[(r["a"], r["b"])] += r["n"]
        ca[r["a"]] += r["n"]
        cb[r["b"]] += r["n"]
    ax = [k for k, _ in ca.most_common(limit_a)]
    bx = [k for k, _ in cb.most_common(limit_b)]
    head = [a] + bx
    body = [[x] + [m.get((x, y), 0) or "." for y in bx] for x in ax]
    return _tab(body, head)


def list_counts(con, field, top=18):
    c = collections.Counter()
    for (blob,) in con.execute("SELECT %s FROM worlds WHERE %s IS NOT NULL" % (field, field)):
        try:
            for v in json.loads(blob):
                c[v] += 1
        except Exception:                                       # noqa: BLE001
            pass
    return c.most_common(top)


def lineage_graph(con, max_edges=60):
    """Mermaid graph of BASED_ON / SUBCLASS_OF edges between catalogued worlds."""
    slug_by_qid = {r["qid"]: r["slug"] for r in con.execute(
        "SELECT qid, slug FROM worlds WHERE qid IS NOT NULL")}
    name_by_slug = {r["slug"]: r["name"] for r in con.execute("SELECT slug, name FROM worlds")}
    edges = []
    for r in con.execute("SELECT src, dst, kind FROM relations"):
        dst = slug_by_qid.get(r["dst"])
        if dst and dst != r["src"] and r["src"] in name_by_slug:
            edges.append((r["src"], dst, r["kind"]))
    if not edges:
        return None
    deg = collections.Counter()
    for s, d, _ in edges:
        deg[s] += 1
        deg[d] += 1
    edges.sort(key=lambda e: -(deg[e[0]] + deg[e[1]]))
    edges = edges[:max_edges]
    L = ["graph LR"]
    seen = set()
    for s, d, k in edges:
        for node in (s, d):
            if node not in seen:
                seen.add(node)
                L.append('    %s["%s"]' % (node, str(name_by_slug.get(node, node)).replace('"', "'")[:34]))
        L.append("    %s -->|%s| %s" % (s, k.lower(), d))
    return "\n".join(L)


def build(con):
    c = store.counts(con)
    cov, total = coverage(con)

    L = ["# Atlas of Game Worlds", "",
         "Generated %s. Source: Wikidata (CC0) + Wikipedia (CC BY-SA)." % store.now(), "",
         "Every declared value below is `heuristic` unless a world's dossier says",
         "otherwise: machine classification from source text, not a rules audit.",
         "Claims about named commercial games stay HYPOTHESIZED until reviewed.", "",
         "## Totals", "",
         _tab([[k, v] for k, v in c.items()], ["metric", "n"]), ""]

    ladder = con.execute(
        "SELECT catalog_state AS s, COUNT(*) AS n FROM worlds GROUP BY s ORDER BY n DESC").fetchall()
    L += ["## Catalog ladder", "",
          _tab([[r["s"], r["n"]] for r in ladder], ["state", "n"]), ""]

    # Reachability check. An empty cell is only meaningful if something COULD
    # have filled it. turn_structure=CONTINUOUS sat empty for four iterations
    # and was reported as a gap in the atlas's knowledge; it was actually a
    # defect in the vocabulary -- no classifier rule could ever set it. A value
    # that cannot be reached makes the coverage grid lie, so it is surfaced
    # here rather than left to be rediscovered.
    unreachable = []
    for field in T.DECLARED_VECTOR:
        rules = classify.RULES.get(field)
        if not rules:
            continue
        settable = {v for v, _, _ in rules}
        for value in T.VOCAB.get(field, []):
            if value not in settable:
                unreachable.append((field, value))
    if unreachable:
        L += ["## Unreachable vocabulary (defect, not a gap)", "",
              "No classifier rule can set these, so they can never leave the",
              "'empty values' column. Either add a rule or drop the value.", "",
              _tab(unreachable, ["field", "value"]), ""]

    # The source ceiling. 'Unclassified' conflates two very different things:
    # a world waiting its turn for enrichment, and a world that can NEVER be
    # enriched because no English Wikipedia article exists for it. The second
    # is a property of the source, not a backlog, and reporting them together
    # makes the atlas look further behind than it is.
    total_w = con.execute("SELECT COUNT(*) FROM worlds").fetchone()[0]
    no_article = con.execute(
        "SELECT COUNT(*) FROM worlds WHERE wp_title IS NULL").fetchone()[0]
    pending = con.execute(
        "SELECT COUNT(*) FROM worlds WHERE enriched_ts IS NULL"
        "   AND wp_title IS NOT NULL").fetchone()[0]
    enriched = con.execute(
        "SELECT COUNT(*) FROM worlds WHERE enriched_ts IS NOT NULL").fetchone()[0]
    L += ["## Source ceiling", "",
          "Enrichment reads English Wikipedia. A world with no article there can",
          "only ever carry its Wikidata description (often just '2007 board game'),",
          "so it is a limit of the source rather than a queue to work through.", "",
          _tab([["enriched from full article", enriched,
                 "%.0f%%" % (100.0 * enriched / max(total_w, 1))],
                ["awaiting enrichment", pending,
                 "%.0f%%" % (100.0 * pending / max(total_w, 1))],
                ["no English article (ceiling)", no_article,
                 "%.0f%%" % (100.0 * no_article / max(total_w, 1))]],
               ["state", "worlds", "share"]), ""]

    # Research-item coverage. Every world is supposed to carry a simulated
    # turn trace, or a clock trace where there is no turn boundary. That is the
    # artifact that makes an incoherent classification visible, so its coverage
    # is a first-class number rather than a by-product of deepening.
    trace_n = con.execute(
        "SELECT COUNT(DISTINCT slug) FROM artifacts"
        " WHERE kind IN ('TURN_TRACE','CLOCK_TRACE')").fetchone()[0]
    by_kind = con.execute(
        "SELECT kind, COUNT(*) n FROM artifacts GROUP BY kind ORDER BY n DESC").fetchall()
    L += ["## Research items", "",
          "%d of %d worlds carry a simulated trace (%.0f%% of all worlds, "
          "%.0f%% of those with a source article)." % (
              trace_n, total_w, 100.0 * trace_n / max(total_w, 1),
              100.0 * trace_n / max(enriched, 1)), "",
          _tab([[r["kind"], r["n"]] for r in by_kind], ["artifact", "n"]), ""]

    L += ["## Declared-grid coverage", "",
          "The point of the atlas. A value with 0 worlds is a hole in the",
          "experimental design, not a missing title.",
          "Values reachable only by hand review are filled via `crawl.py review`.", ""]
    rows = []
    for f in T.DECLARED_VECTOR:
        d = cov[f]
        filled = len(d["counts"])
        vocab = len(T.VOCAB.get(f, []))
        rows.append([f, "%d/%d" % (filled, vocab), d["null"],
                     ", ".join(d["empty"][:4]) or "--"])
    L += [_tab(rows, ["field", "values seen", "unclassified", "empty values (gaps)"]), ""]

    for f in T.DECLARED_VECTOR:
        d = cov[f]
        if not d["counts"]:
            continue
        top = sorted(d["counts"].items(), key=lambda kv: -kv[1])
        L += ["### %s" % f, "",
              _tab([[k, v] for k, v in top], ["value", "n"]), ""]

    L += ["## Epoch x medium", "", "```", cross(con, "epoch", "region"), "```", "",
          "## Interaction x exogenous process", "",
          "```", cross(con, "interaction", "exogenous_process"), "```", ""]

    for field, title in [("media", "Media"), ("live_axes", "Decision axes"),
                         ("randomness_sources", "Randomness sources"),
                         ("strategies", "Strategies"), ("algorithms", "Algorithms")]:
        mc = list_counts(con, field)
        if mc:
            L += ["## %s" % title, "", _tab(mc, ["value", "n"]), ""]

    # oldest / newest
    old = con.execute(
        "SELECT name, year_created, epoch, region FROM worlds"
        " WHERE year_created IS NOT NULL ORDER BY year_created ASC LIMIT 12").fetchall()
    new = con.execute(
        "SELECT name, year_created, epoch, region FROM worlds"
        " WHERE year_created IS NOT NULL ORDER BY year_created DESC LIMIT 8").fetchall()
    if old:
        L += ["## Oldest catalogued", "",
              _tab([[r["name"][:40], r["year_created"], r["epoch"], r["region"] or "--"]
                    for r in old], ["world", "year", "epoch", "region"]), ""]
    if new:
        L += ["## Newest catalogued", "",
              _tab([[r["name"][:40], r["year_created"], r["epoch"], r["region"] or "--"]
                    for r in new], ["world", "year", "epoch", "region"]), ""]

    hi = con.execute(
        "SELECT name, novelty, complexity_score, information_score, catalog_state"
        " FROM worlds ORDER BY (COALESCE(novelty,0)*COALESCE(complexity_score,0)) DESC"
        " LIMIT 15").fetchall()
    L += ["## Highest information x novelty (next to deepen)", "",
          _tab([[r["name"][:38], r["novelty"], r["complexity_score"],
                 r["information_score"], r["catalog_state"]] for r in hi],
               ["world", "novelty", "complexity", "info", "state"]), ""]

    cond = con.execute(
        "SELECT kind, COUNT(*) AS n FROM conditions GROUP BY kind ORDER BY n DESC").fetchall()
    if cond:
        L += ["## Conditions extracted", "",
              _tab([[r["kind"], r["n"]] for r in cond], ["kind", "n"]), ""]
        th = con.execute(
            "SELECT w.name, c.kind, c.threshold, c.effect, c.trigger FROM conditions c"
            " JOIN worlds w ON w.slug = c.slug WHERE c.threshold IS NOT NULL"
            " ORDER BY RANDOM() LIMIT 14").fetchall()
        if th:
            L += ["### Thresholded rules (machine-checkable)", "",
                  _tab([[r["name"][:24], r["kind"], r["threshold"],
                         (r["effect"] or "--")[:22], r["trigger"][:74]] for r in th],
                       ["world", "kind", "threshold", "effect", "trigger"]), ""]

    g = lineage_graph(con)
    if g:
        L += ["## Lineage graph", "", "```mermaid", g, "```", ""]

    ticks = con.execute(
        "SELECT n, ts, harvested, new_worlds, deepened FROM ticks ORDER BY n DESC LIMIT 12").fetchall()
    if ticks:
        L += ["## Recent ticks", "",
              _tab([[r["n"], r["ts"][11:19], r["harvested"], r["new_worlds"], r["deepened"]]
                    for r in ticks], ["tick", "utc", "harvested", "new", "deepened"]), ""]

    return "\n".join(L)


def main():
    con = store.connect()
    REPORT_DIR.mkdir(exist_ok=True)
    md = build(con)
    OUT.write_text(md, encoding="utf-8")
    print("wrote %s (%d bytes)" % (OUT, len(md.encode("utf-8"))))
    print(json.dumps(store.counts(con), indent=1))


if __name__ == "__main__":
    main()
