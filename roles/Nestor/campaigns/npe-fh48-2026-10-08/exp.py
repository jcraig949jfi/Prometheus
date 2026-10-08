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


# --------------------------------------------------------------------------- 2. X-DIR-QUAL
# X-DIR-QUAL (EXPLORE, parents X-GATE-HARM, X-LOSS-AUTOPSY): does selection on COPY DIRECTION (competence decides who runs
#   first = who copies onto whom) maintain a transmitted task function, at a FIXED, competence-blind interaction rate?
#   Single coordinate: order = DIR (higher-u organism on side 0, q = 1) vs RANDOM, at CONST p in {0.15, 1.0}; CT_UA plant.
#   Negatives under DIR at p = 0.15: CT_U (reads, does not use; u = 0 -> no ordering advantage) and COPY_ONLY.
#   p = 0.15 arms run 2000 epochs, p = 1.0 arms 300 epochs: both ~300 interactions per organism (X-LOSS-GATE showed
#   p = 1.0 costs ~10x per epoch). Seeds 44_100_000 + s (paired across arms within a plant).
#   Endpoint (persistence, not peak): among established runs, final CS >= 0.10 (MAINTAINED), and last epoch with CS > 0.
#   Classification (declared): SIGNAL if DIR maintains (final CS >= 0.10) in >= 50% of established CT_UA runs at some p
#   while its RANDOM partner at that p maintains in <= 1 run AND both negatives have final CS = 0 in all runs;
#   WEAK_SIGNAL if DIR's median last-CS>0 epoch exceeds RANDOM's by >= 2x at some p without maintenance;
#   CLEAN_NULL otherwise. INVALID if a negative arm ends with CS >= 0.10 in any run.
SEEDS_D = [44_100_000 + s for s in range(12)]
declare("X-DIR-QUAL",
        jobs=[(arm, s, dict(gate="CONST", p_const=p, order=o, epochs=ep)) for s in SEEDS_D
              for arm, p, o, ep in (("DIR015", 0.15, "DIR", 2000), ("RND015", 0.15, "RANDOM", 2000),
                                    ("DIR100", 1.0, "DIR", 300), ("RND100", 1.0, "RANDOM", 300))]
        + [(arm, s, dict(gate="CONST", p_const=0.15, order="DIR", plant=pl)) for s in SEEDS_D[:6]
           for arm, pl in (("NEG_CTU_DIR015", "CT_U"), ("NEG_COPY_DIR015", "COPY_ONLY"))])


if __name__ == "__main__":
    name = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    e = EXPS[name]
    fh.pool_run(name, e["jobs"], HERE / "runs" / name, w)
