"""Controls for the feed parser (PAN-35; no network, no database).

POSITIVE  an RSS 2.0 and an Atom (GitHub releases) body parse to the known items:
          title, link, the entry's own date, HTML stripped, namespaced source_id
NEGATIVE  an HTML error page and a JSON body are "not a feed": zero items
CHEAT     an undated entry gets NO date (never the poll time); a repeated guid is one
          row; the same guid in two feeds is two rows; a body that names a local file
          is not opened as that file; an entity-expansion bomb parses flat and fast
"""
import datetime as dt
import time

from pan.frontier.feeds import dedupe, parse

BLOG = dict(feed_id="ex.org", url="https://ex.org/feed", kind="blog")
REL = dict(feed_id="gh:o/r", url="https://github.com/o/r/releases.atom", kind="releases")

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>T</title><link>https://ex.org</link>
<item><title>First &amp; post</title><link>https://ex.org/1</link><guid>g-1</guid>
<pubDate>Thu, 08 Oct 2026 10:00:00 GMT</pubDate>
<description>&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;</description><category>evolution</category></item>
<item><title>Undated</title><link>https://ex.org/2</link></item>
<item><title>First &amp; post (again)</title><link>https://ex.org/1</link><guid>g-1</guid>
<pubDate>Thu, 08 Oct 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom">
<title>Release notes</title><id>tag:github.com,2008:o/r</id><updated>2026-10-01T12:30:00Z</updated>
<entry><id>tag:github.com,2008:Repository/1/v1.2.0</id><updated>2026-10-01T12:30:00Z</updated>
<link rel="alternate" type="text/html" href="https://github.com/o/r/releases/tag/v1.2.0"/>
<title>v1.2.0</title><content type="html">&lt;p&gt;Fixes the &lt;code&gt;mutate&lt;/code&gt; bug&lt;/p&gt;</content>
<author><name>dev</name></author></entry></feed>"""


def test_positive_rss():
    items, info = parse(RSS, BLOG)
    assert info["version"].startswith("rss")
    first = items[0]
    assert first["title"] == "First & post"
    assert first["url"] == "https://ex.org/1"
    assert first["summary"] == "Hello world"
    assert first["published_at"] == dt.datetime(2026, 10, 8, 10, 0, tzinfo=dt.timezone.utc)
    assert first["source"] == "rss" and first["source_id"] == "ex.org|g-1"
    assert first["categories"] == ["evolution"]
    assert "FEED:ex.org" in first["tags"] and "KIND:blog" in first["tags"]


def test_positive_atom_release():
    items, info = parse(ATOM, REL)
    assert info["version"].startswith("atom")
    (it,) = items
    assert it["source"] == "github"
    assert it["title"] == "o r release: v1.2.0" and it["url"].endswith("/releases/tag/v1.2.0")
    assert it["published_at"] == dt.datetime(2026, 10, 1, 12, 30, tzinfo=dt.timezone.utc)
    assert it["raw"]["date_basis"] == "updated"
    assert it["summary"] == "Fixes the mutate bug" and it["authors"] == ["dev"]


def test_negative_not_a_feed():
    html = b"<!doctype html><html><head><title>404 Not Found</title></head><body><h1>Not Found</h1></body></html>"
    for body in (html, b'{"models": [{"id": "x"}]}', b""):
        items, info = parse(body, BLOG)
        assert items == [] and info["version"] == ""


def test_cheat_undated_gets_no_date():
    items, _ = parse(RSS, BLOG)
    undated = [i for i in items if i["title"] == "Undated"][0]
    assert undated["published_at"] is None and undated["raw"]["date_basis"] is None
    assert undated["source_id"] == "ex.org|https://ex.org/2"        # falls back to the link, not a hash


def test_cheat_repeat_and_namespace():
    items, _ = parse(RSS, BLOG)
    assert len(items) == 3 and len(dedupe(items)) == 2
    other, _ = parse(RSS, dict(BLOG, feed_id="mirror.org"))
    assert {i["source_id"] for i in dedupe(items)}.isdisjoint({i["source_id"] for i in other})


def test_cheat_body_naming_a_file_is_not_opened(tmp_path):
    f = tmp_path / "local.xml"
    f.write_bytes(RSS)
    items, info = parse(str(f).encode(), BLOG)       # feedparser would open a bare path argument
    assert items == [] and info["version"] == ""


def test_cheat_entity_bomb_parses_flat():
    ents = ['<!ENTITY e0 "xxxxxxxxxx">'] + ['<!ENTITY e{} "{}">'.format(i, "&e{};".format(i - 1) * 10)
                                          for i in range(1, 10)]
    bomb = ('<?xml version="1.0"?><!DOCTYPE rss [{}]><rss version="2.0"><channel><title>&e9;</title>'
            '<item><title>&e9;</title><link>https://ex.org/b</link></item></channel></rss>').format("".join(ents))
    t = time.time()
    items, _ = parse(bomb.encode(), BLOG)
    assert time.time() - t < 5
    assert all(len(i["title"] or "") < 10000 for i in items)      # 10**10 characters if expanded


def test_cheat_placeholder_dates_are_not_dates():
    body = RSS.replace(b"Thu, 08 Oct 2026 10:00:00 GMT", b"Mon, 01 Jan 0001 00:00:00 GMT", 1)
    items, _ = parse(body, BLOG)
    assert items[0]["published_at"] is None                    # year-1 sentinel: no date, no crash
    body = RSS.replace(b"Thu, 08 Oct 2026 10:00:00 GMT", b"Thu, 01 Jan 1970 00:00:00 GMT", 1)
    assert parse(body, BLOG)[0][0]["published_at"] is None     # epoch zero is a missing date written as 0


def test_rate_interval_spans_client_instances(monkeypatch):
    # two Clients of one source in one process must still keep the interval (the 0.571 s defect)
    import pan.frontier as fr

    class R:
        status_code, content, url = 200, b"", "u"

    monkeypatch.setattr(fr.Client, "_last", {})
    monkeypatch.setattr(fr.Client, "_calls", {})
    a = fr.Client("t-src", "r", 0.5)
    monkeypatch.setattr(a.s, "get", lambda *x, **k: R())
    a.get("u")
    b = fr.Client("t-src", "r", 0.5)
    monkeypatch.setattr(b.s, "get", lambda *x, **k: R())
    t = time.time()
    b.get("u")
    assert time.time() - t >= 0.45


def test_relative_links_resolve_against_the_feed():
    body = RSS.replace(b"<link>https://ex.org/1</link>", b"<link>/posts/one/</link>", 1)
    items, _ = parse(body, dict(BLOG, url="https://ex.org/feed.xml"))
    assert items[0]["url"] == "https://ex.org/posts/one/"
