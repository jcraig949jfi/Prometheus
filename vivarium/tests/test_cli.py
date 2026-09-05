"""The status surface. A smoke test that each question is answerable."""
from __future__ import annotations

import json

import pytest

from conftest import make_spec
from viv import cli as _cli
from viv import queue as _q


def _run(capsys, *argv):
    code = _cli.main(list(argv))
    return code, capsys.readouterr().out


def test_status_answers_the_operational_questions(conn, schema, capsys, tmp_path):
    code, out = _run(capsys, "--schema", schema, "status")
    assert code == 0
    for line in ("workers:", "running:", "next:", "most recent:", "stranded:"):
        assert line in out

    path = tmp_path / "spec.json"
    path.write_text(json.dumps(make_spec(name="cli-world")), encoding="utf-8")
    code, out = _run(capsys, "--schema", schema, "enqueue", str(path),
                     "--by", "operator", "--reason", "cli smoke")
    assert code == 0
    eid = out.split()[0]

    code, out = _run(capsys, "--schema", schema, "status")
    assert eid in out and "queued" in out

    code, out = _run(capsys, "--schema", schema, "show", eid)
    assert code == 0 and "enqueued" in out

    code, out = _run(capsys, "--schema", schema, "trace")
    assert code == 0 and eid in out

    code, out = _run(capsys, "--schema", schema, "cancel", eid,
                     "--by", "operator", "--reason", "done with it")
    assert code == 0
    assert _q.get(conn, eid, schema=schema)["status"] == "cancelled"


def test_enqueue_reports_every_reason_a_spec_was_rejected(capsys, schema,
                                                          tmp_path, conn):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"spec_version": 9, "sneaky": 1}),
                    encoding="utf-8")
    code, out = _run(capsys, "--schema", schema, "enqueue", str(path),
                     "--by", "operator", "--reason", "should fail")
    err = capsys.readouterr().err
    assert code == 2
    assert _q.counts(conn, schema=schema) == {}


def test_status_exits_nonzero_when_something_is_stranded(conn, schema, capsys):
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(name="strand"), schema=schema)
    _q.claim_next(conn, "ghost-worker", schema=schema)
    conn.commit()
    code, out = _run(capsys, "--schema", schema, "status", "--stale-after", "0")
    assert code == 1
    assert "stranded:     1" in out
    assert eid in out
