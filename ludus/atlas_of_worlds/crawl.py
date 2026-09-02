"""One tick of the atlas crawler.

    python crawl.py tick --harvest 120 --deepen 5

A tick is deliberately small and idempotent. It rotates probes rather than
draining them, because the atlas is graded on coverage of the declared-vector
grid and not on headcount -- a thousand more push-your-luck dice games would
raise the row count and teach nothing (ludus/atlas/BACKLOG.md makes the same
argument about the bench).

Order of work:
  1. rotate probes, favouring those that have run least
  2. harvest Wikidata rows + one Wikipedia enumeration page (the long tail:
     playground games, regional variants, sports rule structures)
  3. batch-fetch lead extracts for new names
  4. classify -> declared vector, score novelty against what is already held
  5. upsert worlds and lineage relations
  6. deepen the top-K by novelty x complexity: full article text, conditions,
     object model, state diagram, turn/clock trace, dossier on disk
  7. write the tick report
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys
import time
import traceback

import utf8  # noqa: F401
import classify
import coherence
import deepen
import seeds
import store
import taxonomy as T
import wikidata
import wikipedia

HERE = pathlib.Path(__file__).resolve().parent
WORLD_DIR = HERE / "worlds"
REPORT_DIR = HERE / "reports"
LOG = HERE / "crawl.log"


def log(msg):
    line = "%s  %s" % (store.now(), msg)
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ------------------------------------------------------------ probe rotation

def pick_probes(con, k):
    """Least-run, non-exhausted probes first, with a little jitter.

    Exhausted probes are retried occasionally: Wikidata grows, and a probe that
    returned nothing last month may return something now.
    """
    rows = {r["probe"]: dict(r) for r in con.execute("SELECT * FROM probe_state")}
    scored = []
    for name in wikidata.PROBES:
        st = rows.get(name, {"runs": 0, "exhausted": 0, "yielded": 0})
        if st.get("exhausted") and random.random() > 0.12:
            continue
        scored.append((st.get("runs", 0) + random.random() * 0.9, name))
    if not scored:  # everything exhausted -- retry the whole rotation
        scored = [(random.random(), n) for n in wikidata.PROBES]
    scored.sort()
    return [n for _, n in scored[:k]]


def seen_counts(con):
    counts, total = {}, 0
    for f in T.DECLARED_VECTOR:
        for r in con.execute(
                "SELECT %s AS v, COUNT(*) AS n FROM worlds WHERE %s IS NOT NULL"
                " GROUP BY %s" % (f, f, f)):
            counts[(f, r["v"])] = r["n"]
    total = con.execute("SELECT COUNT(*) FROM worlds").fetchone()[0]
    return counts, total


# ---------------------------------------------------------------- harvesting

def harvest_wikidata(con, probes, per_probe):
    """-> list of raw records (dicts from wikidata.flatten)."""
    got = []
    for p in probes:
        cur = store.probe_cursor(con, p)
        try:
            rows = wikidata.harvest(p, limit=per_probe, offset=cur["offset"])
        except Exception as e:                                  # noqa: BLE001
            log("  probe %s FAILED: %s" % (p, e))
            continue
        recs = [wikidata.flatten(b) for b in rows]
        recs = [r for r in recs if r.get("qid") and r.get("name")]
        store.probe_advance(con, p, len(rows), per_probe)
        con.commit()
        log("  probe %-34s offset=%-6d +%d" % (p, cur["offset"], len(recs)))
        got.extend(recs)
        time.sleep(1.2)
    return got


def harvest_seeds(con, k=12):
    """Curated cell-filling seeds (see seeds.py).

    Runs before the probes each tick so that the worlds chosen to fill a named
    empty cell are never crowded out by whatever the rotation happened to draw.
    These skip the membership gate: they are hand-verified.
    """
    want = seeds.pending(con, k)
    if not want:
        return []
    titles = [t for t, _ in want]
    try:
        qmap = wikipedia.qids_for(titles)
    except Exception as e:                                      # noqa: BLE001
        log("  seeds qid lookup FAILED: %s" % e)
        qmap = {}
    recs = []
    for title, cell in want:
        recs.append({"qid": qmap.get(title), "name": title, "wp_title": title,
                     "description": None, "inception": None, "country": None,
                     "players_min": None, "players_max": None,
                     "genres": [], "instances": [], "based_on": [],
                     "subclass_of": [], "_probe": "seed:%s" % cell})
    log("  seeds %d requested -> %d resolved" % (len(want), len(qmap)))
    return recs


def harvest_wikipedia(con, n_titles=40):
    """One rotating enumeration page or category -- the long tail.

    Returns records shaped like the Wikidata ones so both paths merge cleanly.
    """
    pool = ([("list", t) for t in wikipedia.LIST_PAGES]
            + [("cat", c) for c in wikipedia.CATEGORIES])
    # skip targets that have already been tried and yielded nothing (dead
    # redirects, list pages whose links live in templates, empty categories)
    dead = {r[0] for r in con.execute(
        "SELECT probe FROM probe_state WHERE probe LIKE 'wp:%' AND runs > 0"
        " AND yielded = 0")}
    live = [(k, t) for k, t in pool if "wp:%s:%s" % (k, t) not in dead]
    if not live:
        live = pool
    kind, target = random.choice(live)
    pname = "wp:%s:%s" % (kind, target)
    store.probe_cursor(con, pname)

    try:
        titles = (wikipedia.list_page_links(target, 400) if kind == "list"
                  else wikipedia.category_members(target, 200)[0])
    except Exception as e:                                      # noqa: BLE001
        log("  wikipedia %s %s FAILED: %s" % (kind, target, e))
        return []
    bad = ("List of", "Category:", "Index of", "Outline of", "Glossary",
           "Comparison of", "Timeline of", "History of")
    titles = [t for t in titles if not t.startswith(bad)]
    random.shuffle(titles)
    titles = titles[:n_titles]
    if not titles:
        store.probe_advance(con, pname, 0, 1)
        con.commit()
        log("  wikipedia %s %s -> 0 titles (marked dead)" % (kind, target))
        return []

    try:
        qmap = wikipedia.qids_for(titles)
    except Exception as e:                                      # noqa: BLE001
        log("  wikipedia qids FAILED: %s" % e)
        qmap = {}
    # membership gate: a linked title is not automatically a game
    real = wikidata.filter_games(list(qmap.values())) if qmap else set()
    recs = []
    for t in titles:
        q = qmap.get(t)
        if q and q not in real:
            continue                      # a concept, publisher or glossary entry
        if not q:
            continue                      # no QID: cannot verify, do not guess
        recs.append({"qid": q, "name": t, "wp_title": t,
                     "description": None, "inception": None, "country": None,
                     "players_min": None, "players_max": None,
                     "genres": [], "instances": [], "based_on": [],
                     "subclass_of": [], "_probe": pname})
    store.probe_advance(con, pname, len(recs), max(len(titles), 1))
    con.commit()
    log("  wikipedia %-4s %-34s %d links -> %d games"
        % (kind, target[:34], len(titles), len(recs)))
    return recs


# ---------------------------------------------------------------- the tick

def tick(con, n_probes=6, per_probe=25, deepen_k=5, wp_titles=40, enrich_k=40,
         seed_k=12):
    n = store.next_tick(con)
    log("=" * 78)
    log("TICK %d starting" % n)

    probes = pick_probes(con, n_probes)
    raw = harvest_seeds(con, seed_k)
    raw += harvest_wikidata(con, probes, per_probe)
    raw += harvest_wikipedia(con, wp_titles)
    log("  harvested %d raw records" % len(raw))

    # de-dup within the batch, and skip anything already known
    known_q = {r[0] for r in con.execute(
        "SELECT qid FROM worlds WHERE qid IS NOT NULL")}
    known_t = {r[0] for r in con.execute(
        "SELECT wp_title FROM worlds WHERE wp_title IS NOT NULL")}
    batch, seen_q = [], set()
    for r in raw:
        q, t = r.get("qid"), r.get("wp_title")
        if q and (q in known_q or q in seen_q):
            continue
        if not q and t and t in known_t:
            continue
        if q:
            seen_q.add(q)
        batch.append(r)
    log("  %d are new" % len(batch))

    # lead extracts, batched 20 per request
    titles = [r["wp_title"] for r in batch if r.get("wp_title")]
    extracts = {}
    if titles:
        try:
            extracts = wikipedia.extract(titles[:200])
        except Exception as e:                                  # noqa: BLE001
            log("  extracts FAILED: %s" % e)
    log("  %d extracts fetched" % len(extracts))

    counts, total = seen_counts(con)
    new_slugs, n_new = [], 0
    for r in batch:
        r["wp_extract"] = extracts.get(r.get("wp_title") or "", None)
        try:
            dec = classify.classify(r)
        except Exception as e:                                  # noqa: BLE001
            log("  classify FAILED for %s: %s" % (r.get("name"), e))
            continue
        dec["novelty"] = classify.novelty(dec, counts, total)
        rec = {
            "name": r["name"], "qid": r.get("qid"), "wp_title": r.get("wp_title"),
            "description": r.get("description"), "country": r.get("country"),
            "genres": r.get("genres") or [], "instances": r.get("instances") or [],
            "wp_extract": (r.get("wp_extract") or "")[:4000] or None,
            "sources": ["wikidata"] if r.get("qid") else ["wikipedia"],
            "probe": r.get("_probe") or (probes[0] if probes else None),
            "tick_added": n, "method": "heuristic",
            "catalog_state": "SPECIFIED" if dec.get("exogenous_process") else "CATALOGUED",
        }
        rec.update(dec)
        try:
            slug, is_new = store.upsert_world(con, rec)
        except Exception as e:                                  # noqa: BLE001
            log("  upsert FAILED for %s: %s" % (r.get("name"), e))
            continue
        if is_new:
            n_new += 1
            new_slugs.append(slug)
        for q in r.get("based_on") or []:
            store.add_relation(con, slug, q, "BASED_ON")
        for q in r.get("subclass_of") or []:
            store.add_relation(con, slug, q, "SUBCLASS_OF")
    con.commit()
    log("  %d worlds inserted" % n_new)

    n_enr = enrich_batch(con, enrich_k, n)
    n_deep = deepen_batch(con, deepen_k, n)

    # Cross-check the declared vector against the independently extracted
    # conditions table and fill what the two agree on. Cheap, and it keeps
    # the grid honest as the catalog grows.
    cf, n_fix = coherence.run(con, repair=True)
    if n_fix:
        log("  coherence repaired %d fields" % n_fix)

    store.record_tick(con, n, probes, len(raw), n_new, n_enr, n_deep)
    con.commit()
    c = store.counts(con)
    log("TICK %d done | worlds=%d relations=%d conditions=%d artifacts=%d"
        % (n, c["worlds"], c["relations"], c["conditions"], c["artifacts"]))
    return n, c


# ---------------------------------------------------------------- enrichment

def enrich_batch(con, k, tick_n):
    """Fetch FULL article text for k worlds and reclassify against it.

    Why this tier exists. The bulk harvest can only afford a lead extract, and
    MediaWiki refuses to batch anything else: `exchars` is capped at 1200 and
    `exlimit` is forced to 1 for whole-article extracts, so full text costs one
    request per world. But a lead paragraph almost never contains rules language
    -- after four ticks, 211 of 221 worlds had no `exogenous_process` at all,
    which made the coverage grid a record of what had been deepened rather than
    what the catalog holds.

    So: enrich MANY (text + reclassify, no artifacts), deepen FEW (full dossier).
    """
    # Select on TEXT LENGTH, not catalog_state. Selecting on state used to skip
    # exactly the worlds that mattered: a dice game whose lead paragraph says
    # 'dice' gets exogenous_process=IID and is promoted to SPECIFIED on the
    # strength of one word, which then excluded it from enrichment forever.
    # Can't Stop, Yahtzee and Farkle all sat at ~600 characters this way.
    rows = con.execute(
        "SELECT * FROM worlds"
        " WHERE wp_title IS NOT NULL"
        "   AND enriched_ts IS NULL"
        "   AND method IN ('heuristic','source')"
        " ORDER BY (COALESCE(novelty,0.5) * (0.3 + COALESCE(complexity_score,0.2))) DESC"
        " LIMIT ?", (k,)).fetchall()
    if not rows:
        return 0

    counts, total = seen_counts(con)

    # Fetch the whole batch concurrently before touching the database. The
    # request count is fixed by MediaWiki (exlimit=1 for whole-article
    # extracts), but these are latency-bound and independent, so a small pool
    # turns the dominant cost of a tick from minutes into seconds -- measured
    # 5.3x on a six-article sample. Fetching first also shortens the window in
    # which a concurrent review could be overwritten; the write-time method
    # guard below closes it completely.
    texts = wikipedia.full_text_many([store.dec(r)["wp_title"] for r in rows],
                                     workers=6)

    done = 0
    for row in rows:
        w = store.dec(row)
        txt = texts.get(w["wp_title"])
        if not txt or len(txt) < 300:
            # Stamp it anyway: the attempt happened. Without this the world is
            # re-selected on every future tick and the backlog never drains.
            con.execute("UPDATE worlds SET catalog_state='SPECIFIED',"
                        " enriched_ts=? WHERE id=? AND method IN ('heuristic','source')",
                        (store.now(), w["id"]))
            continue
        # Classify against rule-bearing sections only. Whole-article input let
        # a Spinoffs section decide the base game: Pandemic came back REAL_TIME
        # (from Pandemic: Rapid Response) and Diplomacy came back SOLITAIRE.
        rt = wikipedia.rules_text(txt) or txt[:20000]
        r2 = dict(w)
        r2["wp_extract"] = rt
        dec = classify.classify(r2)
        dec["novelty"] = classify.novelty(dec, counts, total)
        dec["wp_extract"] = rt[:12000]
        dec["catalog_state"] = "SPECIFIED"
        dec["enriched_ts"] = store.now()
        upd, vals = [], []
        for c, v in dec.items():
            upd.append("%s = ?" % c)
            vals.append(json.dumps(sorted(set(v)), ensure_ascii=False)
                        if c in store.LIST_FIELDS and not isinstance(v, str) else v)
        upd.append("last_updated = ?")
        vals.append(store.now())
        con.execute("UPDATE worlds SET %s WHERE id = ?"
                    "   AND method IN ('heuristic','source')"
                    % ", ".join(upd),
                    vals + [w["id"]])
        done += 1
        if done % 25 == 0:
            con.commit()
    con.commit()
    log("  enriched %d worlds with full text (%d fetched)" % (done, len(texts)))
    return done


# ---------------------------------------------------------------- deepening

def deepen_batch(con, k, tick_n):
    """Full text + conditions + dossier for the K most informative candidates.

    Selection is novelty x complexity: charter v2 s41's active selection, applied
    to the catalog. A world that sits in an already-crowded cell of the declared
    grid is not deepened however famous it is.
    """
    rows = con.execute(
        "SELECT * FROM worlds WHERE catalog_state IN ('CATALOGUED','SPECIFIED')"
        "  AND wp_title IS NOT NULL"
        "  AND method IN ('heuristic','source')"
        " ORDER BY (COALESCE(novelty,0.5) * (0.4 + COALESCE(complexity_score,0.2))) DESC,"
        "          COALESCE(complexity_score,0) DESC"
        " LIMIT ?", (k * 3,)).fetchall()
    if not rows:
        return 0

    # Fetch the batch concurrently, as enrichment does. Deepening used to run
    # one serial fetch plus a 0.6 s sleep per world, which capped it at ~6 per
    # tick -- and the research item (a turn or clock trace for every world) is
    # the point of the exercise, not a garnish. At 60 of 939 worlds it was the
    # single biggest shortfall in the atlas.
    want = rows[:k]
    texts = wikipedia.full_text_many([store.dec(r)["wp_title"] for r in want],
                                     workers=6)

    done = 0
    for row in want:
        w = store.dec(row)
        txt = texts.get(w["wp_title"])
        if not txt or len(txt) < 400:
            con.execute("UPDATE worlds SET catalog_state='SPECIFIED'"
                        " WHERE id=? AND method IN ('heuristic','source')",
                        (w["id"],))
            continue

        # Structure comes from the rules sections; conditions are pulled from
        # the WHOLE article, because penalty and elimination rules often live
        # outside a section named 'Gameplay' (sports articles especially).
        rt = wikipedia.rules_text(txt) or txt[:20000]
        r2 = dict(w)
        r2["wp_extract"] = rt
        dec = classify.classify(r2)
        conds = classify.extract_conditions(txt)

        for kind, sent, th, eff in conds:
            store.add_condition(con, w["slug"], kind, sent, th, eff, method="heuristic")

        dec["catalog_state"] = "DEEPENED"
        dec["method"] = "heuristic"
        w2 = dict(w)
        w2.update(dec)

        body = deepen.dossier(w2, conds, extract=txt[:1200])
        trace, trace_kind = deepen.turn_trace(w2)
        store.put_artifact(con, w["slug"], "DOSSIER", body)
        store.put_artifact(con, w["slug"], trace_kind, trace)
        store.put_artifact(con, w["slug"], "STATE_DIAGRAM", deepen.state_diagram(w2))
        store.put_artifact(con, w["slug"], "OBJECT_MODEL", deepen.object_model(w2))

        path = WORLD_DIR / ("%s.md" % w["slug"])
        path.write_text(body, encoding="utf-8")

        upd = {k2: v for k2, v in dec.items()}
        upd["last_updated"] = store.now()
        con.execute("UPDATE worlds SET %s WHERE id = ?"
                    "   AND method IN ('heuristic','source')"
                    % ", ".join("%s = ?" % c for c in upd),
                    [json.dumps(sorted(set(v)), ensure_ascii=False)
                     if c in store.LIST_FIELDS and not isinstance(v, str) else v
                     for c, v in upd.items()] + [w["id"]])
        done += 1
        if done % 25 == 0:
            con.commit()
        if done <= 8 or done % 50 == 0:
            log("  deepened %-38s novelty=%.2f cx=%.2f conds=%d"
                % (w["name"][:38], w.get("novelty") or 0,
                   w.get("complexity_score") or 0, len(conds)))
    con.commit()
    log("  deepened %d worlds (%d fetched)" % (done, len(texts)))
    return done


# -------------------------------------------------------------- hand review

def review(con, slug, assignments, note=None, reviewer="operator"):
    """Promote named fields on one world to method='reviewed'.

    Exists because some cells cannot be recovered from source prose at all. The
    word 'simultaneous' appears nowhere in the Wikipedia articles for 7 Wonders
    or Pandemic, both canonical examples of simultaneous action selection; no
    pattern can find what the source never says. Rather than let those cells
    stay permanently empty or, worse, quietly wrong, a reviewer may set them
    directly -- attributed, dated, and with the previous value retained.

    'reviewed' is deliberately BELOW 'audited'. It means a knowledgeable human
    asserted it; it does not mean anyone checked a rulebook. Only the operator
    working through ludus/bench/RULES_AUDIT.md can produce 'audited'.
    """
    row = con.execute("SELECT * FROM worlds WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        row = con.execute("SELECT * FROM worlds WHERE name = ? OR wp_title = ?",
                          (slug, slug)).fetchone()
    if row is None:
        raise SystemExit("no such world: %s" % slug)
    w = dict(row)

    upd, vals, applied = [], [], []
    for field, value in assignments:
        if field not in w:
            raise SystemExit("unknown field: %s" % field)
        vocab = T.VOCAB.get(field)
        if field in store.LIST_FIELDS:
            items = [v.strip() for v in value.split(",") if v.strip()]
            if vocab:
                bad = [v for v in items if v not in vocab]
                if bad:
                    raise SystemExit("not in %s vocabulary: %s" % (field, bad))
            stored_val = json.dumps(sorted(set(items)), ensure_ascii=False)
        else:
            if vocab and value not in vocab:
                raise SystemExit("not in %s vocabulary: %s\n  allowed: %s"
                                 % (field, value, ", ".join(vocab)))
            stored_val = value
        con.execute(
            "INSERT INTO reviews (slug, field, old_value, value, note, reviewer, ts)"
            " VALUES (?,?,?,?,?,?,?)",
            (w["slug"], field, str(w.get(field)), stored_val, note, reviewer, store.now()))
        upd.append("%s = ?" % field)
        vals.append(stored_val)
        applied.append("%s: %s -> %s" % (field, w.get(field), stored_val))

    upd += ["method = ?", "last_updated = ?"]
    vals += ["reviewed", store.now()]
    con.execute("UPDATE worlds SET %s WHERE id = ?" % ", ".join(upd),
                vals + [w["id"]])
    con.commit()
    log("reviewed %s" % w["slug"])
    for a in applied:
        log("    %s" % a)
    return w["slug"], applied


# ------------------------------------------------------------------ backfill

def reclassify(con):
    """Re-run the classifier over stored text after a rule change.

    The classifier improves across a long run; without this, early rows keep
    whatever the classifier believed on tick 1 and the grid-coverage numbers
    become a record of when a world was harvested rather than what it is.
    Reviewed and audited values are left alone.
    """
    rows = con.execute(
        "SELECT * FROM worlds WHERE wp_extract IS NOT NULL"
        " AND method IN ('heuristic','source')").fetchall()
    counts, total = seen_counts(con)
    n = 0
    for row in rows:
        w = store.dec(row)
        # Stored extracts keep their '== Heading ==' markers, so the section
        # filter can be applied retroactively without re-fetching anything.
        rt = wikipedia.rules_text(w.get("wp_extract") or "")
        if rt and len(rt) > 200:
            w["wp_extract"] = rt
        dec = classify.classify(w)
        dec["novelty"] = classify.novelty(dec, counts, total)
        # List-valued fields must be written even when the new classification
        # finds nothing, otherwise a value can never be RETRACTED -- it can only
        # ever be added to or overwritten. When HIDDEN_INFO and
        # SIMULTANEOUS_CHOICE were removed from the randomness vocabulary,
        # Gomoku and Fanorona kept them indefinitely because the fresh
        # classification simply omitted the key. Absence of evidence has to be
        # able to erase a claim, or the store only ever accumulates.
        for list_field in ("randomness_sources", "media", "live_axes",
                           "strategies", "algorithms"):
            dec.setdefault(list_field, [])
        upd, vals = [], []
        for k, v in dec.items():
            upd.append("%s = ?" % k)
            vals.append(json.dumps(sorted(set(v)), ensure_ascii=False)
                        if k in store.LIST_FIELDS and not isinstance(v, str) else v)
        upd.append("last_updated = ?")
        vals.append(store.now())
        con.execute("UPDATE worlds SET %s WHERE id = ?" % ", ".join(upd),
                    vals + [w["id"]])
        n += 1
    con.commit()
    return n


# ------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="tick",
                    choices=["tick", "status", "init", "reclassify", "seed-audit",
                             "review", "coherence"])
    ap.add_argument("--probes", type=int, default=6)
    ap.add_argument("--per-probe", type=int, default=25)
    ap.add_argument("--harvest", type=int, default=None,
                    help="target new rows; overrides --per-probe")
    ap.add_argument("--deepen", type=int, default=5)
    ap.add_argument("--wp-titles", type=int, default=40)
    # Default deliberately exceeds the typical per-tick harvest (~150). Enrich
    # must outpace harvest or the unclassified backlog grows without bound and
    # the coverage grid degrades into a record of what was harvested first.
    ap.add_argument("--enrich", type=int, default=120)
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--slug", help="review: world slug, name or wikipedia title")
    ap.add_argument("--set", action="append", default=[],
                    metavar="FIELD=VALUE", help="review: repeatable")
    ap.add_argument("--note", help="review: why")
    ap.add_argument("--reviewer", default="operator")
    ap.add_argument("--repair", action="store_true",
                    help="coherence: apply fixes, not just report")
    a = ap.parse_args()

    WORLD_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    con = store.connect()

    if a.cmd == "status":
        print(json.dumps(store.counts(con), indent=1))
        return
    if a.cmd == "init":
        log("initialised %s" % store.DB)
        return
    if a.cmd == "coherence":
        f, applied = coherence.run(con, repair=a.repair)
        print("findings: %d   applied: %d" % (len(f), applied))
        for (nm, fld, val), n in coherence.summarise(f):
            print("  %-34s %-18s -> %-18s %d" % (nm, fld, val, n))
        print("contradictions: %d" % len(coherence.contradictions(con)))
        return
    if a.cmd == "review":
        if not a.slug or not a.set:
            raise SystemExit("review needs --slug and at least one --set FIELD=VALUE")
        pairs = []
        for s in a.set:
            if "=" not in s:
                raise SystemExit("bad --set (want FIELD=VALUE): %s" % s)
            f, v = s.split("=", 1)
            pairs.append((f.strip(), v.strip()))
        review(con, a.slug, pairs, note=a.note, reviewer=a.reviewer)
        return
    if a.cmd == "seed-audit":
        hits, misses, absent = seeds.audit(con)
        print("seeds landed in target cell : %d" % len(hits))
        print("seeds landed elsewhere      : %d" % len(misses))
        print("seeds not yet harvested     : %d" % len(absent))
        for t2, c, st in misses[:25]:
            print("   MISS %-38s want=%-22s state=%s" % (t2[:38], c, st))
        return
    if a.cmd == "reclassify":
        n = reclassify(con)
        log("reclassified %d worlds" % n)
        return

    per = a.per_probe
    if a.harvest:
        per = max(10, a.harvest // max(a.probes, 1))
    try:
        tick(con, n_probes=a.probes, per_probe=per, deepen_k=a.deepen,
             wp_titles=a.wp_titles, enrich_k=a.enrich, seed_k=a.seeds)
    except Exception:                                           # noqa: BLE001
        log("TICK FAILED\n" + traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
