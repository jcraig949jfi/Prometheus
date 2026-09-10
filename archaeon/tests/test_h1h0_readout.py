from archaeon.producer import h1h0_readout as R


def _row(cs, arm, task, status="completed", res=None, err=None, spec_hash=None):
    return {"set": cs, "arm": arm, "task_id": task, "request_key": "{}-{}-{}".format(cs, task, arm), "status": status,
            "result": res or {}, "allowance_mechanism": None, "error": err, "sfe_experiment_id": "e",
            "spec_hash": spec_hash or "h-{}-{}".format(task, arm)}


BASE = {"status": "BUDGET_VM_OPS", "solved": False, "vm_ops": 6003, "oracle_calls": 12, "candidates_tried": 280,
        "witnesses": [{"inputs": [[1, 1, 1]]}], "witness_truncated": False, "seeded_from": "fresh_probe_allowance"}


def test_degeneracy_check_is_bit_identical_when_the_projection_matches_and_differs_otherwise():
    rows = [_row("cs-h1h0-1-p2", "S00", "tgt-00", res=dict(BASE)),
            _row("cs-h1h0-1-p2-r1", "S00-deg", "tgt-00", res=dict(BASE))]
    d = R.degeneracy_check(rows)
    assert d["verdict"] == "BIT_IDENTICAL" and "NOT issued" in d["consequence"]
    rows[1]["result"] = dict(BASE, vm_ops=5990)
    d = R.degeneracy_check(rows)
    assert d["verdict"] == "DIFFERS" and d["differing_fields"] == ["vm_ops"]
    assert R.degeneracy_check(rows[:1])["verdict"] == "INDETERMINATE"


def test_readout_prefers_completed_over_cancelled_and_marks_partial_until_artifact_cells_run():
    rows = [_row("cs-h1h0-1-p2", "fresh", "tgt-00", status="cancelled"),
            _row("cs-h1h0-1-p2-r1", "fresh", "tgt-00", res=dict(BASE, status="SOLVED", solved=True)),
            _row("cs-h1h0-1-p2", "S00", "tgt-00", res=dict(BASE)),
            _row("cs-h1h0-1-p2-r1", "S00-deg", "tgt-00", res=dict(BASE)),
            _row("cs-h1h0-1-p2", "random_pack", "tgt-00", status="failed", err="HTTP 404"),
            _row("cs-h1h0-1-p2", "S10", "tgt-00", status="cancelled")]
    r = R.readout(rows)
    assert r["n_targets"] == 1 and r["slot_free_complete"] is True and r["complete"] is False
    assert r["counts_per_cell"]["fresh"] == {"completed": 1, "failed": 0, "queued": 0, "running": 0, "solved": 1}
    assert r["table"][0]["random_pack"]["status"] == "failed" and r["table"][0]["S10"] is None
    md = R.to_markdown(r)
    assert "PARTIAL" in md and "fresh: SOLVED/S/6003" in md and "random_pack: FAILED" in md


def test_dedup_flags_one_hash_under_two_labels():
    rows = [_row("cs-h1h0-1-p2", "fresh", "tgt-00", res=dict(BASE), spec_hash="same"),
            _row("cs-h1h0-1-p2", "S00", "tgt-00", res=dict(BASE), spec_hash="same"),
            _row("cs-h1h0-1-p2b", "S11", "tgt-00", res=dict(BASE), spec_hash="other")]
    r = R.readout(rows)
    d = r["spec_hash_dedup"]
    assert d["distinct_payloads"] == 2 and d["labels_sharing_a_hash"] == [["S00", "fresh"]] and d["refusal"].startswith("REFUSE")
