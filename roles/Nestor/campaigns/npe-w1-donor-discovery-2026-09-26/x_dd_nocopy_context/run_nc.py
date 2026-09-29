"""X-DD-NOCOPY-CONTEXT (EXPLORE, MEASUREMENT / failure localization; child of X-DD-ESTABLISH). Declared
before running. Theory-aware by date.

X-DD-ESTABLISH (SIGNAL): of 25 stalled donor runs, 20 (80%) are NO_COPY -- the first competent donor
makes zero P-11 causal births before it is lost, although many stay alive for 100-260 epochs;
established donors make their first causal birth within 0-22 epochs. The donor passes the FRESH-START
assay (blank partner, fresh registers) but does not copy in the world. In the world three things differ:
its carried register state, a live partner genome that also executes, and its tape side / order.
Question: which in-world context blocks copying by a fresh-start-competent donor?

Sample: every NO_COPY run and every ESTABLISHED run of X-DD-ESTABLISH (dense VM, ATOMIC runner), replayed
to the 20-epoch check where D0 was first found (the check's epoch and D0 size must equal the record).
There: the donor = the first D0 organism; its carried state (regs, fz, fc); 16 live partners sampled with
a fixed RNG, each with its own carried state.
Evaluation (the world's copy criterion re-executed by p11.interact exactly as world._pair_epoch runs it):
a COPY at one (state, partner, side) = the donor's partner half satisfies the predecessor criterion on
the REAL interaction AND the P-11 randomized-victim assay passes, with the donor on that side.
Conditions: state OWN vs FRESH x partner REAL (16 sampled) vs BLANK (zero bytes, fresh state) x side
0 (runs first) vs 1 (runs second). Rate = share of (partner, side) pairs that COPY.
Per donor, with b = rate(FRESH, BLANK): PARTNER if rate(FRESH, REAL) < 0.25 b; else STATE if
rate(OWN, REAL) < 0.25 b; else NONE (the donor copies in its real context at >= a quarter of its own
blank baseline -- the failure is not context). BLANK uses 10 assay seeds x 2 sides = 20 trials.
Control: rate(FRESH, BLANK) >= 0.10 per trial under the world criterion; donors failing it are reported
and EXCLUDED from labels (the ruler cannot see their blocking); INVALID if more than 50% fail.
REAL uses 16 partners x 2 seeds x 2 sides = 64 trials; BLANK 20 seeds x 2 sides = 40 trials.
PRE-LAUNCH REPAIR (smoke, no outcome data used): the first draft used 1 BLANK trial per side (2 trials)
with an absolute 0.5 control and absolute 0.1 label bars; the smoke's ESTABLISHED donor then failed the
control at 0/2 although the screen found it competent -- an underpowered ruler. Repair 2 (second smoke):
under the world criterion (predecessor acceptance on the real interaction AND P-11) per-trial blank rates
were 0.05-0.15, so trials were raised to 40/64, the control set to 0.10, and control failures excluded
from labels (INVALID above 50%) instead of invalidating the run at 20%.
INVALID if any replay does not reproduce the recorded D0 epoch and size, or if the FRESH/BLANK control
fails for more than 50% of donors.
Classification: SIGNAL if one of PARTNER / STATE labels >= 70% of NO_COPY donors AND < 30% of
ESTABLISHED donors; CLEAN_NULL if NONE labels >= 70% of NO_COPY donors; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import collections
import json
import multiprocessing as mp
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parent
DE = HERE.parent / "x_dd_establish"
for p in (DE, HERE.parent / "x_dd_dense_copy", HERE.parent / "x_donor_discovery",
          HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
NP = 16
KB = 20          # BLANK repetitions (distinct assay seeds): 40 trials (smoke repairs 1-2)
KR = 2           # seeds per REAL partner: 16 x 2 x 2 sides = 64 trials
CTRL = 0.10
REL = 0.25


class Snap(Exception):
    pass


def plan():
    out = []
    for p in sorted((DE / "results").glob("*.json")):
        r = json.loads(p.read_text())
        if r["status"] in ("NO_COPY", "ESTABLISHED"):
            out.append((r["status"], r["cell"], r["seed"], r["d0_epoch"], r["d0_size"]))
    return out


def copies(world, r, g_d, st_d, g_p, st_p, side, tag):
    """The world's criterion for 'the partner half became a causal copy of the donor'."""
    import p11
    from constants import C
    n = r.L
    ga, gb = (g_d, g_p) if side == 0 else (g_p, g_d)
    sa, sb = (st_d, st_p) if side == 0 else (st_p, st_d)
    t = bytearray(world._pow2(2 * n))
    t[0:len(ga)] = ga
    t[n:n + len(gb)] = gb
    tl = len(t)
    kw = dict(n=n, tape_len=tl, ga=ga, gb=gb, st_a=sa, st_b=sb, budget=r.t["slice"],
              ops_mask=r._ops_mask(), cmr=r.copy_mut)
    tape, prov, lit, wo = p11.interact(world.z8, rng=random.Random(p11.event_seed(tag, "real")), **kw)
    vs = 1 - side
    v0 = 0 if vs == 0 else n
    new = bytes(tape[v0:v0 + n])
    old = bytes((g_p + bytes(n))[:n])
    donor = bytes((g_d + bytes(n))[:n])
    acc = p11.predecessor_accepts(p11.fidelity(donor, new), p11.fidelity(old, new), wo[side], n)
    if not acc:
        return False
    return p11.assay(world.z8, victim_side=vs, seed=tag, **kw)["pass"]


def job(args):
    status, cell, seed, d0_epoch, d0_size = args
    import world
    import run_dc
    import run_dd
    import run_ds
    import run_de
    world.z8 = run_dc.dense_z8()
    a = run_ds.cells()[run_dd.CELLS[cell]]
    cache, snap = {}, {}

    class Nc(run_ds.runner_cls(world)):
        def step(self):
            super().step()
            if self.epoch % run_de.EVERY:
                return
            alive = [o for o in self.orgs if o.alive]
            comp = [o for o in alive if run_de.competent(world, self, bytes(self._genome(o)), cache)]
            if comp:
                d = comp[0]
                rng = random.Random(seed * 7 + 1)
                others = [o for o in alive if o is not d]
                parts = rng.sample(others, min(NP, len(others)))
                st = lambda o: (None if o.regs is None else list(o.regs), o.fz, o.fc)
                snap.update(epoch=self.epoch, size=len(comp), g=bytes(self._genome(d)), st=st(d),
                            parts=[(bytes(self._genome(o)), st(o)) for o in parts], r=self)
                raise Snap()

    r = Nc(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    try:
        r.run()
    except Snap:
        pass
    ok_replay = snap.get("epoch") == d0_epoch and snap.get("size") == d0_size
    rates = {}
    if snap:
        n = r.L
        fresh = (None, 0, 0)
        for sname, st_d in (("OWN", snap["st"]), ("FRESH", fresh)):
            for pname in ("REAL", "BLANK"):
                hits = tot = 0
                plist = snap["parts"] * KR if pname == "REAL" else [(bytes(n), fresh)] * KB
                for j, (gp, sp) in enumerate(plist):
                    for side in (0, 1):
                        tot += 1
                        hits += copies(world, r, snap["g"], st_d, gp, sp if pname == "REAL" else fresh, side,
                                       ("X-DD-NOCOPY-CONTEXT", cell, seed, sname, pname, j, side))
                rates["%s_%s" % (sname, pname)] = round(hits / tot, 4)
    b = rates.get("FRESH_BLANK", 0.0)
    if not rates:
        label = None
    elif rates["FRESH_REAL"] < REL * b:
        label = "PARTNER"
    elif rates["OWN_REAL"] < REL * b:
        label = "STATE"
    else:
        label = "NONE"
    rec = {"status": status, "cell": cell, "seed": seed, "d0_epoch": d0_epoch, "replay_ok": ok_replay,
           "rates": rates, "label": label, "control_ok": bool(rates) and rates["FRESH_BLANK"] >= CTRL,
           "donor_hex": snap["g"].hex() if snap else None}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d" % (t[1], t[2]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    bad_replay = [(r["cell"], r["seed"]) for r in res if not r["replay_ok"]]
    ctrl_fail = sum(not r["control_ok"] for r in res)
    nc = [r for r in res if r["status"] == "NO_COPY" and r["control_ok"]]
    es = [r for r in res if r["status"] == "ESTABLISHED" and r["control_ok"]]
    cn = collections.Counter(r["label"] for r in nc)
    ce = collections.Counter(r["label"] for r in es)
    lab = None
    for L in ("PARTNER", "STATE"):
        if nc and cn[L] >= 0.7 * len(nc) and (not es or ce[L] < 0.3 * len(es)):
            lab = L
    cls = ("INVALID" if bad_replay or len(res) != len(todo) or ctrl_fail > 0.5 * len(res) else
           "SIGNAL" if lab else "CLEAN_NULL" if nc and cn["NONE"] >= 0.7 * len(nc) else "WEAK_SIGNAL")

    def mean(rows, k):
        v = [r["rates"][k] for r in rows if r["rates"]]
        return round(sum(v) / len(v), 4) if v else None
    summ = {"classification": cls, "signal_label": lab, "bad_replay": bad_replay, "control_failures": ctrl_fail,
            "labels_NO_COPY": dict(cn), "labels_ESTABLISHED": dict(ce),
            "mean_rates": {g: {k: mean(rows, k) for k in ("OWN_REAL", "FRESH_REAL", "OWN_BLANK", "FRESH_BLANK")}
                           for g, rows in (("NO_COPY", nc), ("ESTABLISHED", es))}}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
