"""Witness programs for the C-013-T011 edits. Each prints ONE JSON object; run_edits.py runs it once under the
original file and once under the mutant and records both. Development lineages / toy budgets only.

    <venv python> rso/reach/challenge/D1/witnesses.py W1|W2|W3|W4
"""
import json
import pathlib
import shutil
import sys
import tempfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def W1():
    from rso.reach import certify
    from rso.reach._proto import org
    c = certify.certify(org.builder_min())
    st = org.lookup_store(certify.P.seed, certify.TRAIN0, certify.P.K, certify.P.R, certify.P.S)
    lk = certify.certify(org.lookup(), store0=st)
    return dict(target_status=c["status"], target_selection_probe=c["selection_probe"], target_select_lives=c["select_lives"],
                lookup_train0_status=lk["status"], lookup_train0_selection_probe=lk["selection_probe"])


def W2():
    from rso.reach import certify
    from rso.reach.challenge.D1.cases_d1 import family
    return {name: dict(status=certify.certify(prog)["status"]) for name, prog in family().items()}


def W3():
    from rso.reach import analyze, stats
    from rso.reach.challenge.D1.cases_d1 import synthetic_ledger
    chosen = None
    for k in range(5, 14):
        p = stats.stratified_exact([(k, 24, 1, 24), (1, 24, 1, 24), (1, 24, 1, 24)])
        if 0.0101 < p < 0.05:
            chosen = (k, p)
            break
    assert chosen, "no k with raw p in (0.0101, 0.05)"
    k, p = chosen
    res = analyze.analyze(synthetic_ledger({("X1", 1): k}))
    c2 = res["contrasts"]["C2_retention"]
    return dict(X1_d1=k, raw_p_precomputed=p, C2=c2, any_other_separates=any(v["verdict"].startswith("SEPARATES")
                                                                            for n, v in res["contrasts"].items() if n != "C2_retention"))


def W4():
    from rso.reach import run_d1
    out = pathlib.Path(tempfile.mkdtemp(prefix="pallas_w4_"))
    try:
        run_d1.TOY_ROUNDS = 3
        run_d1.CPU_CAP_S = 10 ** 9
        rc1 = run_d1.main(["--toy", "--out-dir", str(out), "--workers", "1", "--max-rounds-this-call", "1"])
        rows = [json.loads(x) for x in (out / "LEDGER.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        c0 = sum(r["cpu_s"] for r in rows)
        s1 = json.loads((out / "RUN.json").read_text())["status"]
        run_d1.CPU_CAP_S = 1.5 * c0
        rc2 = run_d1.main(["--toy", "--out-dir", str(out), "--workers", "1", "--resume", "--max-rounds-this-call", "1"])
        m2 = json.loads((out / "RUN.json").read_text())
        s2, n2, cpu2 = m2["status"], m2["rounds_completed"], m2["cpu_s"]
        try:
            rc3 = run_d1.main(["--toy", "--out-dir", str(out), "--workers", "1", "--resume"])
            s3 = json.loads((out / "RUN.json").read_text())["status"]
            n3 = json.loads((out / "RUN.json").read_text())["rounds_completed"]
            refused = False
        except SystemExit as e:
            rc3, s3, n3, refused = None, "REFUSED: " + str(e), n2, True
        return dict(call1=dict(rc=rc1, status=s1, round0_cpu_s=round(c0, 2)), cap_s=round(1.5 * c0, 2),
                    call2=dict(rc=rc2, status=s2, rounds=n2, cpu_s_recorded=cpu2),
                    call3=dict(rc=rc3, status=s3, rounds=n3, refused=refused))
    finally:
        shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    print(json.dumps({"W1": W1, "W2": W2, "W3": W3, "W4": W4}[sys.argv[1]](), sort_keys=True, default=str))
