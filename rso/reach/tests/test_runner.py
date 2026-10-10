"""End-to-end TOY run of the D1 runner (toy lineages < 0, toy budget; no frozen lineage is touched)."""
import json

from rso.reach import analyze, run_d1


def test_toy_run_controls_pass_and_resume_reproduces_a_single_call(tmp_path):
    one = tmp_path / "one"
    assert run_d1.main(["--toy", "--out-dir", str(one), "--workers", "2"]) == 0
    ctl = json.loads((one / "CONTROLS.json").read_text())
    assert ctl["ok"] and all(v["ok"] for v in ctl["seeded"].values())
    assert all(not v["counted_as_discovery"] for v in ctl["seeded"].values())
    run = json.loads((one / "RUN.json").read_text())
    assert run["status"] == "COMPLETE" and run["rounds_completed"] == run_d1.TOY_ROUNDS

    two = tmp_path / "two"
    assert run_d1.main(["--toy", "--out-dir", str(two), "--workers", "1", "--max-rounds-this-call", "1"]) == 0
    assert json.loads((two / "RUN.json").read_text())["status"] == "PAUSED"
    assert run_d1.main(["--toy", "--out-dir", str(two), "--workers", "1", "--resume"]) == 0

    def strip(p):
        rows = [json.loads(x) for x in (p / "LEDGER.jsonl").read_text().splitlines()]
        for r in rows:
            r.pop("cpu_s")
        return rows
    assert strip(one) == strip(two)
    rows, meta = analyze.load(one)
    assert analyze.complete_rounds(rows) == run_d1.TOY_ROUNDS


def test_the_runner_refuses_to_overwrite(tmp_path):
    (tmp_path / "LEDGER.jsonl").write_text("")
    try:
        run_d1.main(["--toy", "--out-dir", str(tmp_path)])
    except SystemExit as e:
        assert "REFUSED" in str(e)
    else:
        raise AssertionError("did not refuse")
