"""Wikidata harvester -- the breadth engine of the atlas.

Design note. BoardGameGeek's XML API returned 401 on every endpoint when this was
built (2026-08-31); it now requires registered credentials. Wikidata is used
instead: it is keyless, CC0, covers every medium the atlas cares about (board,
card, dice, video, RPG, puzzle, traditional, sport), and -- unlike BGG -- carries
inception dates back into the third millennium BCE, country of origin, and
derivation edges. A BGG adapter can be dropped in beside this one if credentials
ever arrive; nothing downstream depends on the source.

Harvest is organised as PROBES. A probe is one slice of the space (a class, an
epoch, a region, a decade of video games). The crawler rotates probes rather than
draining one, because the atlas is graded on coverage of the classifier grid, not
on headcount.
"""
from __future__ import annotations

import time
from urllib.parse import unquote

import requests

import utf8  # noqa: F401  (stdout encoding)

ENDPOINT = "https://query.wikidata.org/sparql"
UA = "LudusAtlas/0.1 (research bench; jcraig949@gmail.com)"
HEADERS = {"User-Agent": UA, "Accept": "application/sparql-results+json"}

CLASS = {
    "board":       "Q131436",
    "card":        "Q142714",
    "dice":        "Q1515156",
    "rpg":         "Q1643932",
    "abstract":    "Q573573",
    "party":       "Q839864",
    "children":    "Q1509934",
    "traditional": "Q676977",
    "trick":       "Q1191150",
    "tile":        "Q1272194",
    "ccg":         "Q734698",
    "wargame":     "Q1501543",
    "mancala":     "Q267989",
    "chessvar":    "Q299191",
    "puzzle":      "Q13698",
    "wordgame":    "Q15220419",
    "sport":       "Q349",
    "video":       "Q7889",
}

BODY = """
  %(selector)s
  ?g rdfs:label ?gLabel . FILTER(LANG(?gLabel) = "en")
  OPTIONAL { ?g schema:description ?gDesc . FILTER(LANG(?gDesc) = "en") }
  OPTIONAL { ?g wdt:P571 ?inception }
  OPTIONAL { ?g wdt:P495 ?country . ?country rdfs:label ?countryLabel . FILTER(LANG(?countryLabel) = "en") }
  OPTIONAL { ?g wdt:P1872 ?pmin }
  OPTIONAL { ?g wdt:P1873 ?pmax }
  OPTIONAL { ?g wdt:P136 ?genre . ?genre rdfs:label ?genreLabel . FILTER(LANG(?genreLabel) = "en") }
  OPTIONAL { ?g wdt:P31 ?inst . ?inst rdfs:label ?instLabel . FILTER(LANG(?instLabel) = "en") }
  OPTIONAL { ?g wdt:P144 ?basedon }
  OPTIONAL { ?g wdt:P279 ?subclassof }
  OPTIONAL { ?article schema:about ?g ; schema:isPartOf <https://en.wikipedia.org/> }
"""

QUERY = """SELECT ?g ?gLabel ?gDesc ?inception ?countryLabel ?pmin ?pmax ?article
  (GROUP_CONCAT(DISTINCT ?genreLabel; separator="|") AS ?genres)
  (GROUP_CONCAT(DISTINCT ?instLabel;  separator="|") AS ?insts)
  (GROUP_CONCAT(DISTINCT ?basedon;    separator="|") AS ?basedons)
  (GROUP_CONCAT(DISTINCT ?subclassof; separator="|") AS ?subclasses)
WHERE {
%(body)s
}
GROUP BY ?g ?gLabel ?gDesc ?inception ?countryLabel ?pmin ?pmax ?article
ORDER BY ?g
LIMIT %(limit)d OFFSET %(offset)d
"""

CONTINENT = {
    "africa": "Q15", "asia": "Q48", "europe": "Q46",
    "north_america": "Q49", "south_america": "Q18", "oceania": "Q55538",
}

EPOCH_EDGES = [
    (None, -1000), (-1000, 1), (1, 500), (500, 1450), (1450, 1750),
    (1750, 1900), (1900, 1970), (1970, 2000), (2000, 2015), (2015, None),
]


def _sel_class(qid):
    return "?g wdt:P31/wdt:P279* wd:%s ." % qid


def _sel_class_years(qid, lo, hi):
    s = "?g wdt:P31/wdt:P279* wd:%s ; wdt:P571 ?dt ." % qid
    if lo is not None:
        s += "\n  FILTER(YEAR(?dt) >= %d)" % lo
    if hi is not None:
        s += "\n  FILTER(YEAR(?dt) < %d)" % hi
    return s


def _sel_class_continent(qid, cont_qid):
    return ("?g wdt:P31/wdt:P279* wd:%s ; wdt:P495 ?c ."
            "\n  ?c wdt:P30 wd:%s ." % (qid, cont_qid))


def build_probes():
    """The rotation. Ordered so a fresh atlas fills breadth before depth."""
    p = {}

    # 1. whole classes, non-video (small enough to drain completely)
    for name, qid in CLASS.items():
        if name in ("video", "sport"):
            continue
        p["class:%s" % name] = _sel_class(qid)

    # 2. epoch slices -- reaches the oldest games Wikidata knows about
    for cname in ("board", "card", "dice", "abstract", "traditional"):
        for lo, hi in EPOCH_EDGES:
            tag = "%s_%s" % (lo if lo is not None else "min",
                             hi if hi is not None else "now")
            p["epoch:%s:%s" % (cname, tag)] = _sel_class_years(CLASS[cname], lo, hi)

    # 3. regional slices -- cultural variety, enforced not hoped for
    for cname in ("board", "card", "dice", "traditional", "children"):
        for rname, cqid in CONTINENT.items():
            p["region:%s:%s" % (cname, rname)] = _sel_class_continent(CLASS[cname], cqid)

    # 4. video games, stratified by decade (183k total: sampled, never drained)
    for lo, hi in [(1958, 1980), (1980, 1990), (1990, 2000),
                   (2000, 2010), (2010, 2020), (2020, None)]:
        p["video:%ss" % lo] = _sel_class_years(CLASS["video"], lo, hi)

    # 5. sports -- carried for their rule structure (foul limits, clocks,
    #    substitution, elimination), which tabletop games rarely expose.
    p["class:sport"] = _sel_class(CLASS["sport"])

    return p


PROBES = build_probes()


def run(sparql, timeout=120, retries=3):
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(ENDPOINT, headers=HEADERS, timeout=timeout,
                             params={"query": sparql, "format": "json"})
            if r.status_code == 200:
                return r.json()["results"]["bindings"]
            last = "HTTP %s: %s" % (r.status_code, r.text[:200])
        except Exception as e:                                  # noqa: BLE001
            last = "%s: %s" % (type(e).__name__, e)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError("wikidata query failed after %d tries: %s" % (retries, last))


def harvest(probe, limit=100, offset=0):
    """Return raw binding dicts for one probe slice."""
    sparql = QUERY % {"body": BODY % {"selector": PROBES[probe]},
                      "limit": limit, "offset": offset}
    return run(sparql)


GAME_ROOTS = ["Q11410", "Q131436", "Q142714", "Q1515156", "Q7889", "Q1643932",
              "Q13698", "Q349", "Q573573", "Q676977", "Q1509934", "Q839864"]


def filter_games(qids, chunk=180):
    """Keep only QIDs that really are games (or sports).

    Enumeration pages are generous: 'List of dice games' links to
    'Advantage gambling' and 'Amerigame' alongside actual games. Without this
    gate the atlas fills with concepts, publishers and glossary entries, and the
    grid-coverage numbers stop meaning anything.
    """
    keep = set()
    qids = [q for q in qids if q]
    roots = " ".join("wd:%s" % r for r in GAME_ROOTS)
    for i in range(0, len(qids), chunk):
        vals = " ".join("wd:%s" % q for q in qids[i:i + chunk])
        sparql = ("SELECT DISTINCT ?g WHERE { VALUES ?g { %s } VALUES ?root { %s }"
                  " ?g wdt:P31/wdt:P279* ?root . }" % (vals, roots))
        try:
            for b in run(sparql):
                keep.add(b["g"]["value"].rsplit("/", 1)[-1])
        except Exception:                                       # noqa: BLE001
            keep.update(qids[i:i + chunk])   # on failure, do not silently drop
        time.sleep(1.0)
    return keep


def flatten(b):
    """Binding dict -> plain record."""
    def g(k):
        return b.get(k, {}).get("value")

    def split(k):
        return [x for x in (g(k) or "").split("|") if x]

    art = g("article")
    wp = unquote(art.rsplit("/", 1)[-1]).replace("_", " ") if art else None
    return {
        "qid": (g("g") or "").rsplit("/", 1)[-1],
        "name": g("gLabel"),
        "description": g("gDesc"),
        "inception": g("inception"),
        "country": g("countryLabel"),
        "players_min": g("pmin"),
        "players_max": g("pmax"),
        "wp_title": wp,
        "genres": split("genres"),
        "instances": split("insts"),
        "based_on": [x.rsplit("/", 1)[-1] for x in split("basedons")],
        "subclass_of": [x.rsplit("/", 1)[-1] for x in split("subclasses")],
    }


if __name__ == "__main__":
    import json
    import sys
    pr = sys.argv[1] if len(sys.argv) > 1 else "class:mancala"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rows = [flatten(b) for b in harvest(pr, limit=n)]
    print("probe %s: %d rows" % (pr, len(rows)))
    print(json.dumps(rows[:4], indent=1, ensure_ascii=False))
    print("\ntotal probes defined: %d" % len(PROBES))
