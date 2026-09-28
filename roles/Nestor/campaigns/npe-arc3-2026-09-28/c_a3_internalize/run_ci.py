"""C-A3-INTERNALIZE (CONFIRM lane, fresh and frozen). Parents: X-A3-SFLINEAGE (SIGNAL), X-A3-ENDOSTATE-R (WEAK_SIGNAL),
X-A3-FORENSIC-16000006. Theory-aware by date.

NOTHING HERE MAY CHANGE AFTER COMMIT: cells, seeds, world, rulers, event definition, rule, allocation, controls.

Exploratory evidence: in the default CARRIED world (dense VM, random populations), lineages whose first donors are NOT state-free
(not competent from random entry registers) come to consist of state-free genomes by descent -- 3 independent lineages (7ae3
16000006, 7ae3 16000021, ffa6 16000030) of 5 examined; mechanism shown in one (the copier fixes its own destination). The runs were
selected post hoc from existing data.
Claim under test (independent recurrence): in fresh evolutionary runs, a lineage founded only by non-state-free donors repeatedly
comes to carry state-free competent genomes descended from those founders -- endogenous internalization of register initialization.

Design: random populations (no implant), dense VM, ATOMIC runner, default CARRIED register world, cells 7ae3 and ffa6, FRESH seeds
27_000_000 + s, s < 72, per cell: 144 runs, 2000 epochs. X-A3-SFLINEAGE's instrument, unchanged:
  D0 = live organisms COMPETENT (zero-state cached screen, run_de.competent) at the first 20-epoch check with any; each distinct D0
       genome measured for STATE_FREE;
  STATE_FREE = X-A3-FAIR fair_assay rate >= 0.5 over 20 seeds from BOTH fixed random entry states R1 and R2;
  L = D0 + every accepted replication whose parent is in L (a member overwritten by a non-L source leaves L);
  every 100 epochs: for each distinct live competent genome, STATE_FREE and whether an organism carrying it is in L.
EVENT (per run): every D0 genome NOT state-free AND at the last checkpoint with >= 1 state-free competent genome, >= 80% of the
state-free competent genomes are in L AND L holds >= 50% of the live population there.
CONFIRMED iff EVENTS >= 4 (independent recurrence in at least 4 fresh runs). NOT_CONFIRMED otherwise.
Frozen controls: reset_axis.selftest (CARRIED is the identity); the instrument reproduces X-A3-SFLINEAGE's per-run verdict on 7ae3
16000006 (a replay check run before launch: EVENT must be true there).
Eligibility (before freezing): in the exploratory data 3 EVENTS were found among the 96 X-DD-DENSE-COPY DENSE_COPY runs (by
examining the 13 measurable runaway runs); at that rate the expected count in 144 fresh runs is ~4.5 (Poisson P(>= 4) ~ 0.66). The rule is a recurrence bar,
not an effect size; a NOT_CONFIRMED at this power is not evidence of absence.
Secondary, never decisive: runs with D0 all not state-free that end state-free by REPLACEMENT (L share < 50%); per-cell counts.

    python run_ci.py -> VERDICT.json
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W1 = ROOT / "npe-w1-donor-discovery-2026-09-26"
SFL = HERE.parent / "x_a3_sflineage"
for p in (SFL, HERE.parent / "x_a3_fair", W1 / "x_dd_establish", W1 / "x_dd_dense_copy", W1 / "x_donor_discovery",
          ROOT / "c9x-explore-2026-09-24" / "x_donor_swap", ROOT / "z80atlas-verify-2026-09-22", ROOT.parent / "lib"):
    sys.path.insert(0, str(p))
N = 72
SEED0 = 27_000_000


def event(rec):
    last = next((c for c in reversed(rec["checkpoints"]) if c["free"] > 0), None)
    d0_not = bool(rec["d0_free"]) and not any(rec["d0_free"])
    ok = d0_not and last is not None and last["free_in_L"] >= 0.8 * last["free"] and last["L_share"] >= 0.5
    repl = d0_not and last is not None and last["L_share"] < 0.5
    return ok, repl


def _run(run_sfl, cell, seed):
    """X-A3-SFLINEAGE's instrument (run_sfl.job body) without the recorded-depth lookup."""
    import world
    import run_dc
    import run_dd
    import run_de
    import run_ds
    import run_fair
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cc, sfc = {}, {}
    S = {"d0": None, "d0_free": None, "L": set(), "cps": []}

    def sf(self, g):
        if g not in sfc:
            sfc[g] = all(run_fair.fair_assay(world, self, g, e, "SFL" + g.hex(), 20) >= 0.5 for e in ("R1", "R2"))
        return sfc[g]

    class Ln(run_ds.runner_cls(world)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if S["d0"] is not None:
                if parent in S["L"]:
                    S["L"].add(child)
                else:
                    S["L"].discard(child)
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            super().step()
            alive = [o for o in self.orgs if o.alive]
            if S["d0"] is None and self.epoch % 20 == 0:
                comp = [o for o in alive if run_de.competent(world, self, bytes(self._genome(o)), cc)]
                if comp:
                    S["d0"] = self.epoch
                    S["L"] = {o.oid for o in comp}
                    S["d0_free"] = [sf(self, g) for g in sorted({bytes(self._genome(o)) for o in comp})]
            if S["d0"] is not None and self.epoch % 100 == 0:
                inL = {}
                for o in alive:
                    g = bytes(self._genome(o))
                    inL[g] = inL.get(g, False) or (o.oid in S["L"])
                rows = [(sf(self, g), l) for g, l in inL.items() if run_de.competent(world, self, g, cc)]
                S["cps"].append({"epoch": self.epoch, "L_share": round(sum(o.oid in S["L"] for o in alive) / len(alive), 4),
                                 "competent": len(rows), "free": sum(f for f, _ in rows), "free_in_L": sum(f and l for f, l in rows)})

    r = Ln(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    rec = {"cell": cell, "seed": seed, "depth": out["max_causal_replication_depth"], "d0_epoch": S["d0"],
           "d0_free": S["d0_free"], "checkpoints": S["cps"]}
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def jobs():
    return [(c, SEED0 + s) for s in range(N) for c in ("7ae3", "ffa6")]


def precheck():
    import world
    import run_dc
    import run_ds
    import reset_axis
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()["7ae3f9c1437c8000-s54765-tL-a0"]
    ok, st = reset_axis.selftest(world, run_ds.runner_cls(world), dict(a["cell"], atlas_axis="NONE"), a["tier"])
    ref = json.loads((SFL / "results" / "7ae3_16000006.json").read_text())
    return {"reset_axis_ok": ok, "reset_axis": st, "reference_event_16000006": event(ref)[0]}


def main():
    (HERE / "results").mkdir(parents=True, exist_ok=True)
    pc = precheck()
    (HERE / "PRECHECK.json").write_text(json.dumps(pc, indent=1))
    done = {p.stem for p in (HERE / "results").glob("*.json")}
    import run_sfl                                         # noqa: F401 (import check)
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(_job, [t for t in jobs() if "%s_%d" % t not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    assert len(res) == len(jobs()), len(res)
    ev = [r for r in res if event(r)[0]]
    rp = [r for r in res if event(r)[1]]
    controls_ok = pc["reset_axis_ok"] and pc["reference_event_16000006"]
    verdict = "INVALID" if not controls_ok else "CONFIRMED" if len(ev) >= 4 else "NOT_CONFIRMED"
    v = {"verdict": verdict, "controls": pc, "events": len(ev), "event_runs": [(r["cell"], r["seed"]) for r in ev],
         "n_runs": len(res), "runs_with_donor": sum(r["d0_epoch"] is not None for r in res),
         "runs_d0_all_not_free": sum(bool(r["d0_free"]) and not any(r["d0_free"]) for r in res),
         "replacement_runs": len(rp), "runaway": sum(r["depth"] >= 20 for r in res),
         "per_cell_events": {c: sum(1 for r in ev if r["cell"] == c) for c in ("7ae3", "ffa6")}}
    (HERE / "VERDICT.json").write_text(json.dumps(v, indent=1))
    print(json.dumps(v, indent=1))


def _job(args):
    import run_sfl
    return _run(run_sfl, *args)


if __name__ == "__main__":
    main()
