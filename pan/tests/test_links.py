"""Controls for the reference-graph extractor (no database).

POSITIVE  exact and directory-relative paths resolve to their artifacts
NEGATIVE  a bare ambiguous name and a path that is not catalogued do not link
CHEAT     a path embedded in a longer token (a URL fragment, a different
          extension) does not produce a false link; Windows separators normalise
"""
from pan.links import mentions, resolve

KNOWN = {"roles/Pan/QUESTIONS.md", "roles/Pan/reports/INVENTORY_2026-10-09.md", "pan/search.py",
         "roles/base-role/RESPONSIBILITIES.md"}


def test_positive_exact_and_relative():
    text = "See roles/Pan/QUESTIONS.md and reports/INVENTORY_2026-10-09.md; code in pan\\search.py."
    m = mentions(text)
    got = {resolve(p, "roles/Pan/STATUS.md", KNOWN) for p in m}
    assert ("roles/Pan/QUESTIONS.md", "exact") in got
    assert ("roles/Pan/reports/INVENTORY_2026-10-09.md", "relative") in got
    assert ("pan/search.py", "exact") in got


def test_negative_bare_and_unknown():
    m = mentions("Read QUESTIONS.md, then roles/Nobody/GHOST.md.")
    assert "QUESTIONS.md" not in m                      # bare names are not even extracted
    assert resolve("roles/Nobody/GHOST.md", "x/y.md", KNOWN) == (None, None)


def test_cheat_embedded_tokens():
    # a URL that CONTAINS a catalogued path, and a look-alike with a longer extension:
    # neither may resolve to the catalogued artifact
    m = mentions("https://example.org/roles/Pan/QUESTIONS.md.bak and roles/Pan/QUESTIONS.mdx")
    resolved = {resolve(p, "a/b.md", KNOWN)[0] for p in m}
    assert "roles/Pan/QUESTIONS.md" not in resolved
    # and the same path written plainly DOES resolve (the channel can see it)
    assert resolve("roles/Pan/QUESTIONS.md", "a/b.md", KNOWN)[0] == "roles/Pan/QUESTIONS.md"


def test_counts():
    m = mentions("pan/search.py pan/search.py ./pan/search.py")
    assert m == {"pan/search.py": 3}
