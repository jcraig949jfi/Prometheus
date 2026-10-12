"""Witness programs for the C-016-T042 re-run of the T040 edits under v1.1.0 (six-arm schema). Each prints ONE JSON
object; run_edits_r2.py runs it once under the original file and once under the mutant (fresh -B subprocess each,
caches purged). R2 seeds only (subjects_r2.R2_0 + WITNESS_OFF ..).

    python -B rso/ensorain/challenge/R2/witnesses_r2.py W1|W2|W3|W4|W5
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rso.ensorain import analysis, assay, subjects as S            # noqa: E402
from rso.ensorain.challenge import subjects_c as C                 # noqa: E402
from rso.ensorain.challenge.R2 import subjects_r2 as R             # noqa: E402
from rso.ensorain.challenge.R2.cases_r2 import synth_rows6         # noqa: E402

W0 = R.R2_0 + R.WITNESS_OFF


def _v(v):
    return dict(verdict=v["verdict"], G_PRE=v["G_PRE"], G_R5=v["G_R5"], pre=v["pre_competent_lives"],
                K1=[v["K1"]["wins"], v["K1"]["losses"], v["K1"]["ties"], str(v["K1"]["p"])],
                K1n=[v["K1_noise"]["wins"], v["K1_noise"]["losses"], v["K1_noise"]["ties"], str(v["K1_noise"]["p"])],
                K2=[v["K2"]["wins"], v["K2"]["losses"], v["K2"]["ties"], str(v["K2"]["p"])],
                holm={k: str(x) for k, x in v["holm"].items()})


def W1():
    """Holm (E1): K1f and K1n both 26:14 of 40 (raw p .0403 <= .05, Holm .081 > .05); K2 all ties."""
    rows = synth_rows6(40, k1_wins=26, k2_wins=0)
    for r in rows:                                   # 14 losses: the control revised where full is not
        if r["arm"] in ("frozen", "noise") and r["seed"] >= 1026:
            r["c_late"] = 90
        if r["arm"] == "full" and r["seed"] >= 1026:
            r["c_late"] = 0
    return _v(analysis.verdicts(rows, 40)["synth"])


def W2():
    """G_PRE arm (E2): learns_pre at 12 seeds; the frozen arm acts -s (0 pre-competent lives)."""
    rows = assay.run({"learns_pre": C.learns_pre()}, assay.ARMS, [W0 + i for i in range(12)])
    v = analysis.verdicts(rows, 12)["learns_pre"]
    frozen_pre = sum(1 for r in rows if r["arm"] == "frozen" and 2 * r["c_pre"] > r["n_pre"])
    return dict(_v(v), frozen_arm_pre_competent_lives=frozen_pre)


def W3():
    """Window (E3): the split of one reference life."""
    r = assay.life(S.reference(), "full", W0)
    return {k: r[k] for k in ("sw", "c_pre", "n_pre", "c_early", "n_early", "c_late", "n_late")}


def W4():
    """Control assignment (E4), synthetic: the frozen arm revises on every seed, the shuffle arm on none; original K1
    (vs frozen) ties -> NOT_SHOWN; mutant K1 (vs shuffle) 40:0 -> NOT_HISTORY_DEPENDENT."""
    rows = synth_rows6(40, frozen_revised=True, k2_wins=40)
    return _v(analysis.verdicts(rows, 40)["synth"])


def W5():
    """Gate threshold (E6): 205 pre-competent lives of 400 (k_pos 217; simple majority 201)."""
    rows = synth_rows6(400, pre_ok=205, k2_wins=300)
    return _v(analysis.verdicts(rows, 400)["synth"])


if __name__ == "__main__":
    print(json.dumps(globals()[sys.argv[1]](), sort_keys=True))
