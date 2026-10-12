"""Witness programs for the C-016-T040 edits. Each prints ONE JSON object; run_edits.py runs it once under the original
file and once under the mutant (fresh -B subprocess each, caches purged) and records both. Challenge seeds only
(subjects_c.CH0 + WITNESS_OFF ..), disjoint from the scored cases' seeds.

    python -B rso/ensorain/challenge/witnesses.py W1|W2|W3|W4|W5
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rso.ensorain import analysis, assay, subjects as S      # noqa: E402
from rso.ensorain.challenge import subjects_c as C           # noqa: E402
from rso.ensorain.challenge.cases import synth_rows          # noqa: E402

W0 = C.CH0 + C.WITNESS_OFF


def _v(v):
    return dict(verdict=v["verdict"], G_PRE=v["G_PRE"], G_R5=v["G_R5"], pre=v["pre_competent_lives"],
                K1=[v["K1"]["wins"], v["K1"]["losses"], v["K1"]["ties"], str(v["K1"]["p"])],
                K2=[v["K2"]["wins"], v["K2"]["losses"], v["K2"]["ties"], str(v["K2"]["p"])],
                holm={k: str(x) for k, x in v["holm"].items()})


def W1():
    """Holm: K1 raw p = P(X >= 26 | 40, 1/2) = .0403 <= .05, Holm-adjusted .081 > .05; K2 all ties (p = 1)."""
    rows = synth_rows(40, k1_wins=26, k2_wins=0)
    for r in rows:                                   # 14 losses on K1: frozen beats full on the remaining seeds
        if r["arm"] == "frozen" and r["seed"] >= 1026:
            r["c_late"] = 90
    return _v(analysis.verdicts(rows, 40)["synth"])


def W2():
    """G_PRE read from the full arm (original) vs the frozen arm (mutant) for learns_pre at 12 seeds."""
    rows = assay.run({"learns_pre": C.learns_pre()}, assay.ARMS, [W0 + i for i in range(12)])
    v = analysis.verdicts(rows, 12)["learns_pre"]
    frozen_pre = sum(1 for r in rows if r["arm"] == "frozen" and 2 * r["c_pre"] > r["n_pre"])
    return dict(_v(v), frozen_arm_pre_competent_lives=frozen_pre)


def W3():
    """The window split of one reference life."""
    r = assay.life(S.reference(), "full", W0)
    return {k: r[k] for k in ("sw", "c_pre", "n_pre", "c_early", "n_early", "c_late", "n_late")}


def W4():
    """Which control carries K1: jitter at 40 seeds."""
    rows = assay.run({"jitter": C.jitter()}, assay.ARMS, [W0 + 100 + i for i in range(40)])
    return _v(analysis.verdicts(rows, 40)["jitter"])


def W5():
    """The gate threshold: 205 pre-competent lives of 400 (binomial k_pos = 217; simple majority = 201)."""
    rows = synth_rows(400, pre_ok=205, k2_wins=300)
    return _v(analysis.verdicts(rows, 400)["synth"])


if __name__ == "__main__":
    print(json.dumps(globals()[sys.argv[1]](), sort_keys=True))
