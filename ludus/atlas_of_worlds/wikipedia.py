"""Wikipedia adapter -- text for classification, and a second breadth channel.

Two jobs:

1. `extract()` pulls the lead section (and, on demand, the Rules/Gameplay
   sections) of an article. This is the text the classifier reads. Wikipedia is
   CC-BY-SA; the atlas stores extracts as evidence for its own structural
   classifications, not as a rules mirror. Under charter doctrine every rule
   inferred this way is HYPOTHESIZED until the operator audits it.

2. `category_members()` and `list_page_links()` enumerate the long tail Wikidata
   misses -- playground games, regional variants, house rules, sport rule
   structures -- via 'Category:' pages and 'List of ...' / 'History of ...'
   articles, which is exactly where the cultural-variation material lives.
"""
from __future__ import annotations

import re
import time
from concurrent import futures

import requests

import utf8  # noqa: F401  (stdout encoding)

API = "https://en.wikipedia.org/w/api.php"
UA = "LudusAtlas/0.1 (research bench; jcraig949@gmail.com)"
HEADERS = {"User-Agent": UA}

# Seed enumeration targets: the 'history of X' and 'list of X' surface the user
# asked for. These are crawled alongside the Wikidata probes.
LIST_PAGES = [
    "List of board games", "List of traditional board games",
    "List of dice games", "List of card games", "List of solitaire games",
    "List of trick-taking games", "List of mancala games",
    "List of chess variants", "List of go variants", "List of tile-based games",
    "List of puzzle video games", "List of role-playing games",
    "List of children's games", "List of playground games",
    "List of party games", "List of word games", "List of drinking games",
    "List of game show hosts", "List of sports", "List of team sports",
    "List of pub games", "List of gambling games", "List of card game terms",
    "History of games", "History of board games", "History of chess",
    "History of playing cards", "History of video games",
    "History of role-playing games", "Traditional games of Korea",
    "Ancient Egyptian games", "Mesoamerican ballgame",
]

CATEGORIES = [
    "Category:Dice games", "Category:Traditional board games",
    "Category:Abstract strategy games", "Category:Mancala games",
    "Category:Chess variants", "Category:Children's games",
    "Category:Playground games", "Category:Card games by type",
    "Category:Trick-taking card games", "Category:Shedding-type card games",
    "Category:Fishing card games", "Category:Climbing card games",
    "Category:Patience card games", "Category:Gambling games",
    "Category:Ancient games", "Category:Medieval games",
    "Category:Japanese games", "Category:Chinese games", "Category:Indian games",
    "Category:African games", "Category:Native American games",
    "Category:Korean games", "Category:Persian games", "Category:Roman games",
    "Category:Norse games", "Category:Party games", "Category:Word games",
    "Category:Puzzle video games", "Category:Cooperative board games",
    "Category:Social deduction games", "Category:Auction and bidding games",
    "Category:Deck-building card games", "Category:Roll-and-write games",
    "Category:Tile-laying games", "Category:Worker placement games",
    "Category:Real-time board games", "Category:Memory games",
]


def _get(params, retries=3, timeout=30):
    p = dict(params)
    p.setdefault("format", "json")
    p.setdefault("formatversion", "2")
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(API, headers=HEADERS, params=p, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            last = "HTTP %s" % r.status_code
        except Exception as e:                                  # noqa: BLE001
            last = "%s: %s" % (type(e).__name__, e)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError("wikipedia api failed: %s" % last)


def extract(titles, chars=2400):
    """Lead-section extracts for up to 20 titles at a time. -> {title: text}"""
    if isinstance(titles, str):
        titles = [titles]
    out = {}
    for i in range(0, len(titles), 20):
        chunk = [t for t in titles[i:i + 20] if t]
        if not chunk:
            continue
        d = _get({"action": "query", "prop": "extracts", "explaintext": 1,
                  "exintro": 1, "exchars": chars, "titles": "|".join(chunk),
                  "redirects": 1})
        for pg in d.get("query", {}).get("pages", []):
            if "extract" in pg:
                out[pg["title"]] = pg["extract"]
        time.sleep(0.4)
    return out


def full_text(title, max_chars=40000):
    """Whole article plain text -- used when deepening a world into a dossier."""
    d = _get({"action": "query", "prop": "extracts", "explaintext": 1,
              "titles": title, "redirects": 1})
    pages = d.get("query", {}).get("pages", [])
    if not pages or "extract" not in pages[0]:
        return None
    return pages[0]["extract"][:max_chars]


def full_text_many(titles, workers=4, timeout=30, chunk_pause=0.5):
    """Fetch whole-article text for many titles concurrently. -> {title: text}

    MediaWiki forces `exlimit=1` for whole-article extracts, so the request
    COUNT is irreducible: one per world. The wall-clock is not. These fetches
    are independent and mostly latency-bound, so a small pool collapses the
    dominant cost of a tick -- enriching ~450 backlogged worlds serially at
    ~0.7 s each is roughly five minutes of pure waiting.

    Kept small (4) with a shared connection pool, a pause between chunks and a
    descriptive User-Agent. Six workers sustained across a ~900-request backfill
    drew HTTP 429s, so the ceiling is real and this sits under it. Politeness
    here is not decoration: the atlas depends on continued access.
    """
    titles = [t for t in titles if t]
    if not titles:
        return {}
    workers = max(1, min(workers, 8))

    session = requests.Session()
    session.headers.update(HEADERS)
    adapter = requests.adapters.HTTPAdapter(pool_connections=workers,
                                            pool_maxsize=workers)
    session.mount("https://", adapter)

    def one(title):
        params = {"action": "query", "prop": "extracts", "explaintext": 1,
                  "titles": title, "redirects": 1, "format": "json",
                  "formatversion": "2"}
        for attempt in range(3):
            try:
                r = session.get(API, params=params, timeout=timeout)
                if r.status_code == 200:
                    pages = r.json().get("query", {}).get("pages", [])
                    if pages and "extract" in pages[0]:
                        return title, pages[0]["extract"][:40000]
                    return title, None
                if r.status_code in (429, 503):
                    time.sleep(2 * (attempt + 1))
                    continue
                return title, None
            except Exception:                                   # noqa: BLE001
                time.sleep(1.5 * (attempt + 1))
        return title, None

    out = {}
    with futures.ThreadPoolExecutor(max_workers=workers) as pool:
        # Chunked with a short pause rather than one unbroken burst: the same
        # total request count, spread out enough to stay under the rate limit.
        for i in range(0, len(titles), workers * 10):
            batch = titles[i:i + workers * 10]
            for title, txt in pool.map(one, batch):
                if txt:
                    out[title] = txt
            if i + workers * 10 < len(titles):
                time.sleep(chunk_pause)
    session.close()
    return out


_HEAD_RE = re.compile(r"^(=+)\s*(.+?)\s*=+\s*$")

# Sections that describe THIS game's rules.
RULES_SECTIONS = (
    "rule", "gameplay", "game play", "play", "scoring", "score", "objective",
    "object of", "setup", "set up", "equipment", "component", "turn",
    "procedure", "mechanic", "victory", "winning", "how to play", "penalt",
    "foul", "strategy", "tactics", "notation", "board", "deck", "cards",
)

# Sections that describe something ELSE and poison the classifier. This is not
# fastidiousness: Pandemic's article is mostly 'Expansions' and 'Spinoffs', one
# of which (Pandemic: Rapid Response) is real-time -- which is exactly how the
# base game came back classified REAL_TIME. Diplomacy's 'Other ways to play'
# mentions solo play, and the base game came back SOLITAIRE.
EXCLUDE_SECTIONS = (
    "expansion", "spin-off", "spinoff", "sequel", "edition", "reception",
    "review", "award", "development", "publication", "history", "legacy",
    "popular culture", "in media", "adaptation", "video game version",
    "digital", "app", "tournament", "championship", "notable", "record",
    "see also", "reference", "external link", "further reading", "bibliograph",
    "note", "variant", "variation", "related game", "trivia", "controvers",
)


def split_sections(text):
    """-> [(level, title, body)] from an explaintext extract.

    Plaintext extracts keep '== Heading ==' markers, so hierarchy survives and
    a subsection can be attributed to its parent.
    """
    out, cur, buf = [], None, []
    for line in (text or "").splitlines():
        m = _HEAD_RE.match(line.strip())
        if m:
            if cur:
                out.append((cur[0], cur[1], "\n".join(buf).strip()))
            cur, buf = (len(m.group(1)), m.group(2)), []
        else:
            buf.append(line)
    if cur:
        out.append((cur[0], cur[1], "\n".join(buf).strip()))
    return out


def rules_text(text, max_chars=20000):
    """Lead + rules-bearing sections only, with excluded subtrees dropped.

    Classifying against a whole article lets one stray mention in a Spinoffs or
    Reception section outweigh the entire Gameplay section. Restricting the
    input is the single cheapest quality win available to the classifier.
    """
    if not text:
        return ""
    secs = split_sections(text)
    lead = text.split("\n==", 1)[0].strip()
    keep, spare, excluded_at = [lead], [lead], None
    for level, title, body in secs:
        low = title.lower()
        if excluded_at is not None and level > excluded_at:
            continue                       # inside an excluded subtree
        excluded_at = None
        if any(w in low for w in EXCLUDE_SECTIONS):
            excluded_at = level
            continue
        # `spare` keeps every non-excluded section; `keep` keeps only the
        # rule-bearing ones.
        spare.append("== %s ==\n%s" % (title, body))
        if any(w in low for w in RULES_SECTIONS):
            keep.append("== %s ==\n%s" % (title, body))

    out = "\n\n".join(keep)
    # Many articles name their rules section something unmatched, or carry a
    # two-paragraph Gameplay section and nothing else. Sushi Go! kept 440 of
    # 3159 characters that way and classified to nothing at all. Below a floor,
    # widen to every non-excluded section: still free of the Spinoffs and
    # Reception noise that caused the original misfires, but not starved.
    if len(out) < 1200:
        out = "\n\n".join(spare)
    return out[:max_chars]


def sections(title, wanted=RULES_SECTIONS):
    """Return {section_title: text} for rule-bearing sections only."""
    txt = full_text(title)
    if not txt:
        return {}
    return {t: b for _, t, b in split_sections(txt)
            if any(w in t.lower() for w in wanted)}


def category_members(category, limit=200, cont=None):
    """Article titles in a category. Returns (titles, continue_token)."""
    p = {"action": "query", "list": "categorymembers", "cmtitle": category,
         "cmlimit": min(limit, 500), "cmnamespace": 0}
    if cont:
        p["cmcontinue"] = cont
    d = _get(p)
    titles = [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
    return titles, d.get("continue", {}).get("cmcontinue")


def list_page_links(title, limit=500):
    """Blue links out of a 'List of ...' / 'History of ...' article."""
    d = _get({"action": "query", "prop": "links", "titles": title,
              "plnamespace": 0, "pllimit": limit, "redirects": 1})
    pages = d.get("query", {}).get("pages", [])
    if not pages:
        return []
    return [ln["title"] for ln in pages[0].get("links", [])]


def qids_for(titles):
    """Map article titles -> Wikidata QIDs, so list-page finds join the atlas."""
    out = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        d = _get({"action": "query", "prop": "pageprops", "ppprop": "wikibase_item",
                  "titles": "|".join(chunk), "redirects": 1})
        for pg in d.get("query", {}).get("pages", []):
            q = (pg.get("pageprops") or {}).get("wikibase_item")
            if q:
                out[pg["title"]] = q
        time.sleep(0.3)
    return out


if __name__ == "__main__":
    import json
    import sys
    what = sys.argv[1] if len(sys.argv) > 1 else "Senet"
    print(json.dumps(extract([what]), indent=1, ensure_ascii=False)[:1500])
    ts, _ = category_members("Category:Mancala games", 12)
    print("\ncategory sample:", ts[:12])
    ls = list_page_links("List of dice games", 40)
    print("\nlist sample:", ls[:20])
