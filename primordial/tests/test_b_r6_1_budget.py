from primordial.cohorts.b import r6_1_budget as B


class Ctx:
    def __init__(self):
        self.rows = []

    def emit(self, row):
        self.rows.append(row)


def test_job_emits_one_accounting_row_with_clean_crosscheck():
    ctx = Ctx()
    B.job(ctx)
    assert len(ctx.rows) == 1
    row = ctx.rows[0]
    assert row["kind"] == "search_budget_accounting" and row["exp_id"] == B.EXP and row["campaign_stage"] == "PRODUCTION"
    assert isinstance(row["ts"], float) and isinstance(row["comparator_fires"], bool)
    assert row["oracles_budget_crosscheck"]["clean"] is True


def test_crosscheck_flags_a_disagreeing_record():
    acc = {"candidate": {"search_evals_per_run": 10, "search_evals_total": 20, "runs_total": 2},
           "baseline": {"search_evals_per_run": 10, "search_evals_total": 21, "runs_total": 2}}
    out = B.crosscheck(acc, receipt_evals=10, recipe_evals=11)
    assert out["clean"] is False
    assert out["checks"]["recipe_search_evals"] is False and out["checks"]["baseline_total_eq_runs_x_per_run"] is False
    assert out["checks"]["receipt_qd_genomes_per_run"] is True
