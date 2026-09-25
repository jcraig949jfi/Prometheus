"""C9-H1R (CONFIRM lane; HARNESS repair of C9 H1, INVALID under C9-D16). Frozen with this file.

C9-D16: world.Runner stored output_gate / cue_cost but never passed them into the task
spec, so C9's four H1 arms were one experiment run four times (identical to the last
decimal). REPAIR: `_task_spec` builds the spec WITH the intervention. Nothing else changes:
H1's cell, arms, tier, readout (final held-out competence, held_max_final), statistic
(M = gate main effect, I = cost interaction) and threshold (|M|, |I| >= 0.15, from the
hash-covered constants) are exactly C9's preregistered H1 (PREREGISTRATION rev D). Seeds
are FRESH: 9_120_000 + s, s < 60 (C9 used 9_100_000 + s).

GATE BEFORE ANY RUN (fail-on-old-code): an organism that emits its answer BEFORE reading
the cue must have its answer suppressed under GATED+VM, so its competence under the gated
spec must differ from the ungated one on the REPAIRED runner, and must NOT differ on the
unrepaired (C9) runner - otherwise the test could not tell them apart. Also: every H1 arm's
runner exposes the intended gate/cost on the spec the organisms are validated against.

    python run_h1r.py -> GATE.json, RESULTS.json, VERDICT.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SEED0 = 9_120_000


def repaired_runner():
    import tasks
    import world

    class H1Runner(world.Runner):
        def _task_spec(self):
            s = tasks.spec_from_cell(self.cell, n_episodes=self.t["val_episodes"], budget=140)
            return tasks.TaskSpec(transform=s.transform, read_order=s.read_order, bridge=s.bridge,
                                  n_episodes=s.n_episodes, budget=s.budget, neutral=s.neutral,
                                  output_gate=self.output_gate, cue_cost=self.cue_cost)
    return H1Runner


def gate():
    import manifest as M
    import tasks
    import world
    import z8
    cell = M.h1_bundles(1)[0]["arms"][0]["cell"]
    early, _ = z8.asm("LD A,0x42\nOUT\nHALT")          # answers before reading anything
    R = repaired_runner()

    def comp(Runner, gate_, cost):
        r = Runner(cell, 1, tier="S", max_epochs=1, output_gate=gate_, cue_cost=cost)
        spec = r._env_spec_for(type("O", (), {"niche": 0})())
        res = tasks.competence(early + bytes(24), spec, seed=5, held_seed=6)
        return spec.output_gate, spec.cue_cost, res["answered"]
    rep_on, rep_off = comp(R, "GATED", "VM"), comp(R, "UNRESTRICTED", "VM")
    old_on, old_off = comp(world.Runner, "GATED", "VM"), comp(world.Runner, "UNRESTRICTED", "VM")
    arms_ok = all(repaired_runner()(cell, 1, tier="S", max_epochs=1, output_gate=g, cue_cost=c).spec.output_gate == g
                  for g, c in (("GATED", "VM"), ("UNRESTRICTED", "FREE"), ("GATED", "FREE")))
    out = {"repaired_gated": rep_on, "repaired_ungated": rep_off, "old_gated": old_on, "old_ungated": old_off,
           "repaired_distinguishes": rep_on[2] != rep_off[2], "old_cannot": old_on[2] == old_off[2],
           "arms_carry_intervention": arms_ok}
    out["pass"] = out["repaired_distinguishes"] and out["old_cannot"] and arms_ok
    return out


def job(arm):
    R = repaired_runner()
    s = R(arm["cell"], arm["seed"], tier=arm["tier"], **arm["kwargs"]).run()
    return {"seed": arm["seed"], "arm": arm["arm"], "held_max_final": s["held_max_final"],
            "crossed_ever": s["crossed_ever"], "crossed_at_final": s["crossed_at_final"]}


def main():
    g = gate()
    (HERE / "GATE.json").write_text(json.dumps(g, indent=1, default=str))
    print("gate:", json.dumps(g, default=str))
    if not g["pass"]:
        print("GATE FAILED - not running")
        return 1
    import manifest as M
    import hypotheses as HY
    bundles = M.h1_bundles(60)
    arms = []
    for s, b in enumerate(bundles):
        for a in b["arms"]:
            arms.append(dict(a, seed=SEED0 + s))
    with mp.Pool(6, maxtasksperchild=4) as pool:
        res = pool.map(job, arms)
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1))
    by = {}
    for r in res:
        by.setdefault(r["seed"], {})[r["arm"]] = r
    verdict = HY.h1([{"results": v} for v in by.values()])
    (HERE / "VERDICT.json").write_text(json.dumps(verdict, indent=1))
    print(json.dumps(verdict, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
