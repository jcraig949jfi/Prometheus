"""Controls for the Linux node probe (achilles/census/nodes.py) and its rendering.

Positive: a real probe line parses into typed fields and renders in the page and the email.
Negative: a snapshot without a nodes block (older snapshots) still renders.
Cheat: an unreachable node is shown as UNREACHABLE and counted; it is never shown as OK with stale
numbers, and a worker that is not 'active' is listed under worker_down.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from achilles.census import nodes as N  # noqa: E402
from achilles.census import render as R  # noqa: E402
from achilles.census.tests.test_census import _snap  # noqa: E402

LINE = ("ubu003 threads=4 load=0.17 0.06 0.01 mem_avail=6191/7330MB disk_free=183G worker=active "
        "mind_procs=6 mind_cpu%=0.5 mind_rss_mb=69 skullport_minds=2")


def test_positive_probe_line_parses_typed_fields():
    row = N.parse_probe_line(LINE)
    assert row["hostname"] == "ubu003" and row["threads"] == 4
    assert row["load"] == "0.17 0.06 0.01"            # three tokens re-joined
    assert row["mem_avail"] == "6191/7330MB" and row["disk_free"] == "183G" and row["worker"] == "active"
    assert row["mind_procs"] == 6 and row["mind_cpu%"] == 0.5 and row["mind_rss_mb"] == 69 and row["skullport_minds"] == 2


def test_fanout_table_loads_and_names_only_available_nodes():
    fan = N.load_fanout(ROOT)
    assert fan is not None and set(fan.ALL_AVAILABLE) <= set(fan.NODES)
    assert "ubu007" not in fan.ALL_AVAILABLE and "ubu002" not in fan.ALL_AVAILABLE   # HOLD / offline stay out


def _nodes_block():
    ok = dict(N.parse_probe_line(LINE), node="ubu003", ip="192.168.1.220", status="OK", error=None, secs=0.3)
    down = dict(N.parse_probe_line(LINE.replace("worker=active", "worker=inactive").replace("ubu003", "ubu005")),
                node="ubu005", ip="192.168.1.222", status="OK", error=None, secs=0.4)
    dead = {"node": "ubu001", "ip": "192.168.1.218", "status": "UNREACHABLE", "error": "rc=255: Connection timed out", "secs": 6.0}
    return {"status": "ok", "probed_at": "2026-10-17T01:00:00Z", "user": "jcraig", "source": "infra/ubuntu_nodes/fleet_fanout.py",
            "nodes": {"ubu001": dead, "ubu003": ok, "ubu005": down}, "unreachable": ["ubu001"], "worker_down": ["ubu005"],
            "totals": {"nodes": 3, "reachable": 2, "threads": 8, "mind_procs": 12, "skullport_minds": 4, "mind_rss_mb": 138, "mind_cpu%": 1.0}}


def test_positive_nodes_render_in_page_and_email():
    snap = dict(_snap(), nodes=_nodes_block())
    page = R.render_html(snap)
    assert "Linux nodes" in page and "ubu003" in page and "skullport" in page.lower()
    blk = R.email_block(snap)
    assert "ubu003" in blk["markdown"] and "ubu003" in blk["html"] and "mind" in blk["markdown"]


def test_cheat_unreachable_node_is_not_shown_as_ok():
    snap = dict(_snap(), nodes=_nodes_block())
    page = R.render_html(snap)
    i = page.index("ubu001")
    assert "UNREACHABLE" in page[i:i + 400]
    assert "inactive" in page            # the worker-down node shows its real worker state
    blk = R.email_block(snap)
    assert "UNREACHABLE" in blk["markdown"] and "ubu001" in blk["markdown"]


def test_negative_snapshot_without_nodes_still_renders():
    snap = _snap()
    assert "nodes" not in snap
    page = R.render_html(snap)
    blk = R.email_block(snap)
    assert "Prometheus Fleet Census" in page and blk["rows"] == 1


def test_ssh_client_never_reads_the_console():
    """The 2026-10-17 04:30Z stall: ssh.exe inheriting a hidden console as stdin. -n, -T and stdin=DEVNULL are the guard."""
    import subprocess
    argv = N.ssh_command("192.168.1.220", "echo x", 6)
    assert argv[0] == "ssh" and "-n" in argv and "-T" in argv and argv.index("-n") < argv.index("jcraig@192.168.1.220")
    seen = {}

    def fake_run(cmd, **kw):
        seen.update(kw)
        return subprocess.CompletedProcess(cmd, 0, stdout=LINE + "\n", stderr="")
    orig = N.subprocess.run
    N.subprocess.run = fake_run
    try:
        row = N._probe_one("ubu003", "192.168.1.220", "probe", 6, 25)
    finally:
        N.subprocess.run = orig
    assert row["status"] == "OK" and row["attempts"] == 1 and seen["stdin"] is subprocess.DEVNULL


def test_probe_retries_once_after_a_stalled_client_and_reports_both_when_it_fails():
    import subprocess
    calls = []

    def stall_then_answer(cmd, **kw):
        calls.append(kw["timeout"])
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(cmd, kw["timeout"], stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout=LINE + "\n", stderr="")

    def always_stall(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, kw["timeout"])

    def auth_fails(cmd, **kw):
        calls.append("auth")
        return subprocess.CompletedProcess(cmd, 255, stdout="", stderr="jcraig@192.168.1.220: Permission denied (publickey).\n")
    orig = N.subprocess.run
    try:
        N.subprocess.run = stall_then_answer
        row = N._probe_one("ubu003", "192.168.1.220", "probe", 6, 25)
        assert row["status"] == "OK" and row["attempts"] == 2 and calls == [12, 12]   # 25 s split over two tries
        N.subprocess.run = always_stall
        row = N._probe_one("ubu003", "192.168.1.220", "probe", 6, 25)
        assert row["status"] == "UNREACHABLE" and "attempt 2/2" in row["error"] and row["attempts"] == 2
        calls.clear(); N.subprocess.run = auth_fails
        row = N._probe_one("ubu003", "192.168.1.220", "probe", 6, 25)
        assert row["status"] == "UNREACHABLE" and "Permission denied" in row["error"] and calls == ["auth"]   # no retry on a definite failure
    finally:
        N.subprocess.run = orig


def test_probe_never_raises_without_table(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "CODE_ROOT", tmp_path)     # otherwise the real table is found and a live probe runs
    out = N.probe_nodes(tmp_path, "2026-10-17T01:00:00Z")
    assert out["status"] == "UNAVAILABLE" and "not found" in out["error"] and out["nodes"] == {}
