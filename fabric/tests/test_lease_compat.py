"""The legacy lease CLIs are thin frontends onto the ONE fabric lease row (operator ruling 2026-09-28).
A legacy helper and a fabric Attempt racing for the same resource: exactly one wins, every round."""
import os
import random
import secrets
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from fabric import store as S

REPO = Path(__file__).resolve().parents[2]
ANANKE = str(REPO / "roles/Ananke/research/lease.py")
NESTOR = str(REPO / "roles/Nestor/tools/nestor_lease.py")
HOST = socket.gethostname().lower()
RES = HOST + ":cpu8"


@pytest.fixture
def env(monkeypatch, tmp_path):
    name = "fabric_test_" + secrets.token_hex(4)
    monkeypatch.setenv("FABRIC_SCHEMA", name)
    try:
        c = S.connect(require_schema=False)
    except Exception as e:  # pragma: no cover
        pytest.skip("canonical store unreachable: {}".format(e))
    S.init_schema(c)
    cur = c.cursor()
    cur.execute("CREATE TABLE {}.legacy_msgs (id BIGSERIAL PRIMARY KEY, subject TEXT NOT NULL, body TEXT NOT NULL DEFAULT '')".format(name))
    c.commit()
    monkeypatch.setenv("FABRIC_LEGACY_LEASE_TABLE", name + ".legacy_msgs")
    monkeypatch.setenv("FABRIC_LEGACY_LEASE_DIR", str(tmp_path / "ananke_runs" / "leases"))
    home = tmp_path / "home"; home.mkdir()
    e = dict(os.environ, HOME=str(home), USERPROFILE=str(home))
    yield c, e, tmp_path
    cur = c.cursor(); cur.execute("DROP SCHEMA {} CASCADE".format(name)); c.commit(); c.close()


def cli(e, *args):
    return subprocess.run([sys.executable, *args], env=e, capture_output=True, text=True, timeout=120)


def test_ananke_and_nestor_clis_use_the_fabric_row(env):
    c, e, tmp = env
    a = cli(e, ANANKE, "acquire", "cpu8", "--owner", "t", "--ttl-min", "5")
    assert a.returncode == 0, a.stderr
    assert any(l["resource"] == RES and l["holder"] == "Ananke t" for l in S.leases(c))
    n = cli(e, NESTOR, "acquire", "cpu8", "--work", "W", "--log", str(tmp / "log.jsonl"))
    assert n.returncode == 3 and "BUSY" in n.stdout                       # same row: Nestor sees Ananke's lease
    tok = __import__("json").loads(a.stdout)["token"]
    assert cli(e, ANANKE, "release", "cpu8", "--token", "wrong").stdout.strip() == "NOT HELD"
    assert cli(e, ANANKE, "release", "cpu8", "--token", tok).stdout.strip() == "RELEASED"
    n = cli(e, NESTOR, "acquire", "cpu8", "--work", "W", "--log", str(tmp / "log.jsonl"))
    assert n.returncode == 0 and n.stdout.startswith("ACQUIRED"), n.stdout + n.stderr
    assert cli(e, NESTOR, "extend", "cpu8", "--ttl-min", "10", "--log", str(tmp / "log.jsonl")).stdout.strip() == "EXTENDED"
    assert cli(e, NESTOR, "release", "cpu8", "--log", str(tmp / "log.jsonl")).stdout.strip() == "RELEASED"
    assert not any(l["resource"] == RES for l in S.leases(c))
    # the retired acquisition path: no host lease file was ever created
    assert not (tmp / "home" / "ananke_runs").exists()


@pytest.mark.parametrize("helper", ["ananke", "nestor"])
def test_legacy_cli_vs_fabric_attempt_race_exactly_one_wins(env, helper):
    c, e, tmp = env
    rng = random.Random(7)
    wins = {"cli": 0, "attempt": 0}
    for i in range(12):
        tid = S.submit(c, "Tester", "race %d" % i, "synthetic", resources=[RES], max_attempts=1)["task_id"]
        out = {}

        def run_cli():
            time.sleep(rng.uniform(0, 0.25))
            if helper == "ananke":
                p = cli(e, ANANKE, "acquire", "cpu8", "--owner", "race", "--ttl-min", "5")
                out["cli"] = p.returncode == 0
                out["tok"] = __import__("json").loads(p.stdout)["token"] if p.returncode == 0 else None
            else:
                p = cli(e, NESTOR, "acquire", "cpu8", "--work", "race", "--log", str(tmp / "log.jsonl"))
                out["cli"] = p.returncode == 0

        def run_claim():
            time.sleep(rng.uniform(0.15, 0.45))                       # python start-up of the CLI is ~0.2-0.3 s
            cc = S.connect()
            out["claim"] = S.claim(cc, "worker.t", "t-1", HOST, [], ["synthetic"])
            cc.close()
        ts = [threading.Thread(target=run_cli), threading.Thread(target=run_claim)]
        [t.start() for t in ts]; [t.join() for t in ts]
        cli_won, att_won = bool(out.get("cli")), out.get("claim") is not None
        assert cli_won != att_won, "round %d: cli=%s attempt=%s (exactly one must win)" % (i, cli_won, att_won)
        holders = [l for l in S.leases(c) if l["resource"] == RES]
        assert len(holders) == 1
        if att_won:
            wins["attempt"] += 1
            S.finish_attempt(c, out["claim"]["attempt_id"], "succeeded", "worker.t")
        else:
            wins["cli"] += 1
            if helper == "ananke":
                cli(e, ANANKE, "release", "cpu8", "--token", out["tok"])
            else:
                cli(e, NESTOR, "release", "cpu8", "--log", str(tmp / "log.jsonl"))
            S.cancel(c, tid, "Tester")
        assert not [l for l in S.leases(c) if l["resource"] == RES]
    assert wins["cli"] >= 1 and wins["attempt"] >= 1, wins            # both sides really contended


def test_unreachable_store_grants_nothing(env):
    _, e, tmp = env
    bad = dict(e, EW_DB_HOST="127.0.0.1", EW_DB_PORT="1")
    n = cli(bad, NESTOR, "acquire", "cpu8", "--work", "W", "--log", str(tmp / "log.jsonl"))
    assert n.returncode == 4 and "UNAVAILABLE" in n.stdout
    a = cli(bad, ANANKE, "acquire", "cpu8", "--owner", "t")
    assert a.returncode != 0 and "UNAVAILABLE" in a.stderr
    assert not (tmp / "home" / "ananke_runs").exists() and not (tmp / "log.jsonl").exists()
