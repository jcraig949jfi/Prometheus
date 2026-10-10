"""Behavioural pins added by the D1 repair round (C-013-T013, PREREGISTRATION v1.0.1 s9).

Pallas's C-013-T011 report (rso/reach/challenge/D1/REPORT.md s2, s4) found four load-bearing lines that only the hash
manifest held: once FROZEN_D1.json is regenerated the manifest no longer distinguishes them, so each gets a test that
is RED on its mutant applied verbatim:

  E1   certify.py:52  selection evaluated on the TRAINING lives instead of SELECT0 .. SELECT0+63
  E3   analyze.py:93  the raw p instead of the Holm-adjusted p decides SEPARATES
  E4   run_d1.py:141  --resume forgets the CPU already spent (the 3.2 core-hour cap is then never reached in slices)
  M80  certify.py:54  the integrator's finding (C-013-T010 INTEGRATED note): selection threshold 90% -> 80%

No reach-world outcome is used: the analysis test is a synthetic ledger, the runner test a synthetic prior ledger plus
the toy controls, the certification tests fixed programs on the certification lives.
"""
import json

import numpy as np

from rso.reach import run_d1  # first: sets NUMBA_NUM_THREADS before numba is imported (record: T013 anomaly 1)
from rso.reach import analyze, certify, stats
from rso.reach._proto import org, ru, wm


def test_selection_reads_the_selection_lives_not_the_training_lives():
    """E1. The selection counts must be the independent oracle's counts on lives SELECT0 .. SELECT0+63 (500 BUILD
    probes for the target), not the training block's (126 probes)."""
    prog = org.builder_min()
    c = certify.certify(prog)
    o = certify._oracle_counts(np.ascontiguousarray(prog, dtype=np.int64), org.empty_store(certify.P.S),
                               certify.SELECT0, certify.N_SELECT)
    assert c["selection_probe"] == [int(o[wm.T_PROBE, 0]), int(o[wm.T_PROBE, 1])] == [500, 500]
    tr = certify._oracle_counts(np.ascontiguousarray(prog, dtype=np.int64), org.empty_store(certify.P.S),
                                certify.TRAIN0, certify.N_TRAIN)
    assert c["selection_probe"][0] != int(tr[wm.T_PROBE, 0])


def test_the_90_percent_selection_boundary_builder7_misses_by_one_probe():
    """M80. builder(7) carries 7 of 8 mechanism rows: 449/500 = 89.8% on the selection lives. It must NOT certify,
    and the selection gate (not the sealed ruler, which it passes) must be what rejects it; at 80% it would certify."""
    c = certify.certify(org.builder(7))
    assert c["selection_probe"] == [500, 449]
    assert c["selection_ok"] is False
    assert c["sealed_verdict"] == ru.PASS and c["oracle_agrees"]
    assert c["status"] == "NOT_CERTIFIED" and c["certified"] is False


def _fixed_ledger(counts, rounds=24, default=1):
    """Deterministic ledger: cell (arm, d) has counts.get((arm, d), default) discoveries, in its first rounds."""
    rows = []
    for j in range(rounds):
        for d in analyze.DISTANCES:
            for a in analyze.ARMS:
                disc = j < counts.get((a, d), default)
                rows.append(dict(round=j, arm=a, d=d, discovery=disc, hit=disc, evals=1000 if disc else -1,
                                 certificate=({"status": "CERTIFIED", "certified": True} if disc else None), cells=10,
                                 distinct_genomes=100, stones_retained_end=0, stones_evaluated=0, max_stone_restored=0))
    return rows


def test_holm_not_the_raw_p_decides_separation():
    """E3. X1 9/24 at d = 1, every other cell 1/24: C2's raw p is 0.039 (<= alpha) and its Holm p 0.196 (> alpha).
    The family-wise rule says NOT SEPARATED (operator ruling s3: the number of contrasts counts)."""
    assert 0.01 < stats.stratified_exact([(9, 24, 1, 24), (1, 24, 1, 24), (1, 24, 1, 24)]) <= analyze.ALPHA
    res = analyze.analyze(_fixed_ledger({("X1", 1): 9}))
    c2 = res["contrasts"]["C2_retention"]
    assert c2["p"] <= analyze.ALPHA < c2["p_holm"]
    assert c2["verdict"].startswith("NOT SEPARATED")
    assert not any(v["verdict"].startswith("SEPARATES") for v in res["contrasts"].values())


def test_resume_counts_the_cpu_already_in_the_ledger(tmp_path, monkeypatch):
    """E4. A ledger holding one complete round whose recorded CPU already exceeds the cap: --resume must stop at the
    cap without running another round, and RUN.json must carry the ledger's CPU total."""
    monkeypatch.setattr(run_d1, "CPU_CAP_S", 10_000.0)
    rows = []
    for d in run_d1.DISTANCES:
        for arm in analyze.ARMS:
            rows.append(dict(round=0, arm=arm, d=d, cpu_s=1000.0, hit=False, discovery=False, certificate=None))
    ledger = tmp_path / "LEDGER.jsonl"
    ledger.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    assert run_d1.main(["--toy", "--out-dir", str(tmp_path), "--workers", "1", "--resume",
                        "--max-rounds-this-call", "1"]) == 0
    run = json.loads((tmp_path / "RUN.json").read_text())
    assert run["status"] == "STOPPED_AT_CPU_CAP"
    assert run["rounds_completed"] == 1 and run["cpu_s"] == 18_000.0
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 18
