"""Experiment registry for the NPE-48h window. Each experiment is declared HERE (question, arms, seeds, epochs,
classification rule) and committed BEFORE it runs; results land in runs/<EXP>/.

    python -B exp.py <EXP> [workers]
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fh  # noqa: E402

EXPS = {}


def declare(name, **kw):
    EXPS[name] = kw


# --------------------------------------------------------------------------- 1. X-LOSS-AUTOPSY + X-GATE-HARM
# One batch serves two declared nodes (shared runs).
# X-LOSS-AUTOPSY (EXPLORE, parent X-TASK-GATE-V2): what causal event destroys the transmitted task function while copying
#   stays intact? Read from the exact per-interaction ledger: loss classes (LOST_INPLACE / LOST_OVERWRITE /
#   LOST_COPY_ERR / LOST_COPY_MUT), transmission fidelity P(child comp | comp donor) for P-11 and LABEL births and for the
#   tape copy before the world's mutation, per-interaction and per-epoch hazards, loss byte positions vs the CT_UA map
#   (copier 0-6, task routine 7-49, padding 50-63), exposure of competent vs non-competent halves.
#   TG_REPLAY re-runs the six XTG-v2 production seeds (EQ-1: identical dynamics) for 400 epochs with the ledger.
# X-GATE-HARM (EXPLORE, parent X-TASK-GATE-V2): is the symmetric TG gate beneficial, neutral or harmful to competence?
#   Same CT_UA plant + backgrounds (paired seeds) under TG, SHUF (rate-matched, competence-blind), CONST p=0.15 (floor,
#   competence-blind), CONST p=1.0 (everyone interacts). Endpoint: competence persistence among ESTABLISHED runs
#   (depth >= 20): last epoch with CS > 0, CS AUC over the run, CS_peak; mechanism: per-interaction loss hazard of
#   competent halves vs exposure (interactions per competent half-epoch).
#   Classification (declared): HARMFUL if median last-epoch-CS>0 (established runs) of TG is < that of SHUF AND < CONST015
#   with TG's per-competent-half-epoch exposure higher; BENEFICIAL if TG's is > both; NEUTRAL otherwise.
#   All arms are expected to lose competence; the question is speed and why.
SEEDS_A = [44_000_000 + s for s in range(12)]
REPLAY = [43_000_000 + s for s in range(6)]
declare("X-LOSS-GATE",
        jobs=[("TG_REPLAY", s, dict(epochs=400)) for s in REPLAY]
        + [(arm, s, dict(epochs=1000, **cfg)) for s in SEEDS_A for arm, cfg in
           (("TG", {}), ("SHUF", dict(gate="SHUF")), ("C015", dict(gate="CONST", p_const=0.15)),
            ("C100", dict(gate="CONST", p_const=1.0)))])


if __name__ == "__main__":
    name = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    e = EXPS[name]
    fh.pool_run(name, e["jobs"], HERE / "runs" / name, w)
