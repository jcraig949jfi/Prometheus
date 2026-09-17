"""F15: boot pack per lane per epoch, built from live state without consuming anything."""
from __future__ import annotations

import subprocess

import pytest

from primordial.bus import bus
from primordial.ops import bootpack as bp
from primordial.ops.epoch import EpochController
from primordial.tests._live import live_url

URL = live_url()

SWARM = """# round
## 3. Cohort charters
### B -- HILL CLIMBERS (40%)
B climbs hills.
### C -- ANTI-PRIOR (25%)
C draws cells.
## 4. The rules (round 2 physics)
1. Rows go through RowWriter.
2. Predicates before experiments.
## 5. Conductor A
logistics
"""

ROWS = [
    {"cell": {"world": "w1", "pressure": "p"}, "mechanism": "big", "fitness": {"held64_median": 90.0},
     "footprint": {"genome_bytes": 64}, "status": "record"},
    {"cell": {"world": "w1", "pressure": "p"}, "mechanism": "small", "fitness": {"held64_median": 80.0},
     "footprint": {"genome_bytes": 8}, "status": "record"},
    {"cell": {"world": "w1", "pressure": "p"}, "mechanism": "abstain", "fitness": {"held64_median": 88.0},
     "footprint": {"genome_bytes": 0}, "status": "control", "floor": "abstain"},
]


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def env(tmp_path, monkeypatch):
    redis = pytest.importorskip("redis")
    r = redis.Redis.from_url(URL, decode_responses=True)
    try:
        r.ping()
    except Exception:
        pytest.skip("substrate not reachable on 6390")
    keys = (bus.SWARM, bus.CLAIMS, bus.ANOMALIES, bus.ANOM_STATUS, bus.ANOM_EVENTS, bus.TAGS)
    r.delete(*keys)
    monkeypatch.setattr(bus, "URL", URL)
    monkeypatch.setenv("PM_TAG", "t-b")
    monkeypatch.setenv("PM_LANE", "B")
    (tmp_path / "SWARM.md").write_text(SWARM, encoding="utf-8")
    jd = tmp_path / "journal"
    jd.mkdir()
    (jd / "B.md").write_text("# B\n\n## old entry\nold\n\n## newest entry\nB did X.\n", encoding="utf-8")
    yield r, tmp_path
    r.delete(*keys)


def kw(tmp_path):
    return {"journal_dir": tmp_path / "journal", "swarm_md": tmp_path / "SWARM.md", "ledger_rows": ROWS}


def test_pack_has_every_section_and_only_the_lanes_state(env):
    r, tmp = env
    bus.claim("B-exp-1", r=r)
    bus.post("note", "for B", "body for B " + "z" * 900, to="B", r=r)
    bus.post("note", "for C only", "not B's", to="C", r=r)
    bus.post("note", "broadcast", "all lanes", to="ALL", r=r)
    aid = bus.anomaly_add("odd thing", "saw it", r=r)
    groups_before = r.xinfo_groups(bus.SWARM)
    text = bp.build("B", 4, r=r, **kw(tmp))
    for h in ("# Boot pack: lane B, epoch 4", "## Boot", "## Rules", "## Open claims", "## Inbox digest",
              "## QD ledger front", "## Open anomalies", "## Last journal entry"):
        assert h in text, h
    assert "B climbs hills." in text and "Rows go through RowWriter." in text and "C draws cells." not in text
    assert "- B-exp-1" in text
    assert "for B" in text and "broadcast" in text and "for C only" not in text
    assert " [...]" in text                                                   # long body cut
    assert "w1: small 80 @ 8 B; big 90 @ 64 B | floor 88" in text
    assert aid in text and "odd thing" in text
    assert "B did X." in text and "old\n" not in text
    tops = [x for x in text.splitlines() if x.startswith("## ")]                 # only the pack's own sections
    assert [x.split(" (")[0] for x in tops] == ["## Boot", "## Rules", "## Open claims", "## Inbox digest",
                                               "## QD ledger front", "## Open anomalies", "## Last journal entry"]
    assert "#### B -- HILL CLIMBERS (40%)" in text and "### newest entry" in text
    assert "OMP_NUM_THREADS=5" in text
    assert r.xinfo_groups(bus.SWARM) == groups_before                         # nothing consumed
    assert len(text.encode()) < bp.MAX_BYTES


def test_epoch_boundary_writes_and_commits_one_pack_per_lane(env, tmp_path):
    r, tmp = env
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    (repo / "README").write_text("x", encoding="utf-8")
    git(repo, "add", "README")
    git(repo, "commit", "-q", "-m", "init")

    def fake_export(out, stamp, r):
        out.mkdir(parents=True, exist_ok=True)
        return {}
    ctl = EpochController(["B", "C"], epoch_s=1, r=r, out=repo / "epochs", repo=repo, export=fake_export,
                          post=False, log=lambda m: None, bootpack=True, bootpack_kw=kw(tmp))
    ctl.boundary(2)
    files = git(repo, "ls-tree", "-r", "--name-only", "HEAD", "epochs/epoch_2/bootpack").split()
    assert files == ["epochs/epoch_2/bootpack/B.md", "epochs/epoch_2/bootpack/C.md"]
    assert "# Boot pack: lane C, epoch 2" in git(repo, "show", "HEAD:epochs/epoch_2/bootpack/C.md")
    assert [e["event"] for e in ctl.events][:5] == ["epoch_post", "stop_set", "drained", "exported", "bootpacks"]
