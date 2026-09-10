"""C3 readout: the null-identity rule and ICC(1) on fixtures with known answers."""
from __future__ import annotations

from archaeon.producer import c3_readout as R


def _row(arm, label, reps, status="completed"):
    return {"arm": arm, "label": label, "status": status, "spec_hash": "x", "sfe_experiment_id": "e",
            "outcome": "SURVIVED", "repeats": reps}


def _rep(acc, n_inc, digest, mis=(0, 1)):
    return {"accuracy_stable": acc, "n_incorrect_stable": n_inc, "mask_digest_stable": digest,
            "accuracy_at_T": acc, "n_incorrect_at_T": n_inc, "mask_digest_at_T": digest,
            "misclassified_ic": list(mis), "criteria_agree": True,
            "spacetime_is_image_of_untransformed": False}


def test_null_identity_compares_masks_not_spacetime_and_reports_all_three_verdicts():
    twin = [_rep(0.58, 42, "sha256:a"), _rep(0.69, 31, "sha256:b")]
    rows = [_row("C3-hist", "exp", twin),
            _row("C3-null", "exp:reflect", [_rep(0.58, 42, "sha256:a"), _rep(0.69, 31, "sha256:b")]),
            _row("C3-null", "exp:complement", [_rep(0.58, 42, "sha256:a"), _rep(0.70, 30, "sha256:c")]),
            _row("C3-null", "par:reflect", [_rep(0.5, 50, "sha256:d")])]           # twin missing
    out = R.null_identity(rows)
    v = {(c["genome"], c["transform"]): c["verdict"] for c in out["checked"]}
    assert v == {("exp", "reflect"): "IDENTICAL", ("exp", "complement"): "NOT_IDENTICAL", ("par", "reflect"): "INDETERMINATE"}
    assert out["identical"] == 1 and out["not_identical"] == 1 and out["indeterminate"] == 1
    assert "spacetime_digest" not in out["fields"]
    diff_fields = {d["field"] for c in out["checked"] for d in c.get("diffs", [])}
    assert diff_fields == {"accuracy_stable", "n_incorrect_stable", "mask_digest_stable", "accuracy_at_T", "n_incorrect_at_T", "mask_digest_at_T"}


def test_icc1_known_cases():
    # identical measures within every group, different across -> ICC 1
    assert abs(R.icc1([[0.2] * 4, [0.5] * 4, [0.8] * 4])["icc1"] - 1.0) < 1e-12
    # every group has the same mean; all variance within -> ICC <= 0
    r = R.icc1([[0.1, 0.9, 0.1, 0.9], [0.9, 0.1, 0.9, 0.1], [0.1, 0.9, 0.9, 0.1]])
    assert r["icc1"] is not None and r["icc1"] <= 0.0
    assert R.icc1([[0.5, 0.5]])["icc1"] is None and R.icc1([[0.5], [0.4, 0.6]])["dropped"] == 1


def test_readout_excludes_null_arm_from_icc_and_marks_partial():
    rows = [_row("C3-hist", "exp", [_rep(0.58, 42, "a"), _rep(0.69, 31, "b")]),
            _row("C3-null", "exp:reflect", [_rep(0.58, 42, "a"), _rep(0.69, 31, "b")]),
            _row("C3-acq", "random_000", [_rep(0.0, 100, "z"), _rep(0.0, 100, "z")]),
            _row("C3-acq", "random_001", [], status="queued")]
    r = R.readout(rows)
    assert r["complete"] is False and r["n_completed"] == 3
    assert r["icc1_rules_all"]["groups"] == 2 and r["icc1_rules_excluding_structural_zeros"]["groups"] == 1
    assert r["d3_over_c3"]["status"] == "PARTIAL"
    md = R.to_markdown(r)
    assert "PARTIAL" in md and "exp:reflect -> IDENTICAL" in md
