"""Controls for the GitHub watch item builder (PAN-36; no network, no database).

POSITIVE  a REST repository object becomes an item with world dates (created, pushed),
          owner and name as separate searchable words, stars and topics kept
NEGATIVE  a repository without description/topics/language still yields a titled item
CHEAT     the session can never pick up a credential: trust_env is off on the client the
          module builds (checked by source inspection, the run itself needs the network)
"""
import datetime as dt
import inspect

from pan.frontier import ghwatch

REPO = {"id": 1, "full_name": "SakanaAI/ShinkaEvolve", "html_url": "https://github.com/SakanaAI/ShinkaEvolve",
        "description": "Open-ended program evolution", "topics": ["evolution", "llm"], "language": "Python",
        "created_at": "2025-09-01T10:00:00Z", "pushed_at": "2026-10-08T22:15:00Z", "stargazers_count": 1200,
        "forks_count": 90, "archived": False, "fork": False, "license": {"spdx_id": "Apache-2.0"},
        "default_branch": "main"}


def test_positive_repo_item():
    it = ghwatch.repo_item(REPO, ["GH_OWNER:SakanaAI"])
    assert it["source"] == "github" and it["source_id"] == "repo:SakanaAI/ShinkaEvolve"
    assert it["title"] == "SakanaAI ShinkaEvolve: Open-ended program evolution"
    assert it["published_at"] == dt.datetime(2025, 9, 1, 10, 0, tzinfo=dt.timezone.utc)
    assert it["updated_at"] == dt.datetime(2026, 10, 8, 22, 15, tzinfo=dt.timezone.utc)
    assert it["signals"]["stars"] == 1200 and it["signals"]["license"] == "Apache-2.0"
    assert it["categories"] == ["evolution", "llm"] and "KIND:repo" in it["tags"]
    assert "topics: evolution, llm" in it["summary"] and "language: Python" in it["summary"]


def test_negative_bare_repo():
    bare = {"full_name": "o/r", "html_url": "https://github.com/o/r", "created_at": None, "pushed_at": None,
            "license": None}
    it = ghwatch.repo_item(bare, [])
    assert it["title"] == "o r (repository)" and it["summary"] is None and it["published_at"] is None


def test_cheat_anonymous_by_construction():
    src = inspect.getsource(ghwatch.run)
    assert "cl.s.trust_env = False" in src
    assert "Authorization" not in src and "get_key" not in src
