"""X-DD-ESTABLISH (EXPLORE, MEASUREMENT / failure localization; child of X-DD-DENSE-COPY). Declared before
running. Theory-aware by date.

X-DD-DENSE-COPY: with one-byte block-copy encodings a fresh-start-competent donor (L2) appears in 49/96
random populations, but only 23 of those 49 reach runaway heredity. In the 26 that stall, the competent
genome is usually single (peak count 1 in 17/26) and gone within ~2 checkpoints of 100 epochs.
Question: when the first competent donor appears, where does establishment fail?
  NO_COPY            - the donor set is lost before its causal lineage makes any P-11 causal birth;
  INCOMPETENT_COPIES - causal births happen, but no lineage member (other than the donors themselves)
                       is ever found COMPETENT;
  LOST_COMPETENT     - competent lineage members arise, and the competent lineage still goes extinct.

Sample: the 49 DENSE_COPY runs of X-DD-DENSE-COPY with L2, replayed exactly (same cell, seed, dense VM,
ATOMIC runner); world depth must equal the record. Screening every 20 epochs (from epoch 20) with the
parent's COMPETENT criterion, cached per distinct genome (deterministic assay seeds keyed on the genome
bytes, so a genome's verdict is the same wherever it appears).
D0 = the live organisms whose genome is COMPETENT at the first 20-epoch check where any is.
Lineage L = D0 plus every organism born by a P-11 causal birth from a member of L (X-SWAP-ORIGIN hook).
Per run: epochs from D0 to the first causal birth from L; total causal births from L; whether any
non-D0 member of L is found COMPETENT at a later check; the last check with a live competent member of L.
A run is ESTABLISHED if it reaches world causal depth >= 20 (the parent's L4); otherwise STALLED and
assigned NO_COPY / INCOMPETENT_COPIES / LOST_COMPETENT as above.
INVALID if any replay depth differs from its record, or if more than 20% of runs are NO_D0 (this screen,
seeded per genome, never finds a COMPETENT genome although the parent's screen did: ruler disagreement);
NO_D0 runs are excluded from the failure modes (repair found by the pre-launch smoke: a run with no D0
would otherwise have been labelled NO_COPY).
Classification (over STALLED runs): SIGNAL if one failure mode holds for >= 70%; CLEAN_NULL if none
reaches 40%; WEAK_SIGNAL otherwise. The same statistics are reported for ESTABLISHED runs.
"""
from __future__ import annotations

import collections
import hashlib
import json
import multiprocessing as mp
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "x_dd_dense_copy"
DD = HERE.parent / "x_donor_discovery"
for p in (DC, DD, HERE.parent.parent / "c9x-explore-2026-09-24" / "x_donor_swap",
          HERE.parent.parent / "z80atlas-verify-2026-09-22"):
    sys.path.insert(0, str(p))
EVERY = 20


def plan():
    out = []
    for p in sorted((DC / "results").glob("DENSE_COPY_*.json")):
        r = json.loads(p.read_text())
        if any(c["L2"] > 0 for c in r["checkpoints"]):
            out.append((r["cell"], r["seed"], r["depth"]))
    return out


def competent(world, r, g, cache):
    if g in cache:
        return cache[g]
    import run_dd
    tag = ("X-DD-ESTABLISH", hashlib.sha256(g).hexdigest()[:16])
    h, _ = run_dd.assay_one(world, r, g, tag + (1,), run_dd.K1)
    ok = False
    if h:
        h2, _ = run_dd.assay_one(world, r, g, tag + (2,), run_dd.K2)
        ok = h2 / run_dd.K2 >= 0.5
    cache[g] = ok
    return ok


def job(args):
    cell, seed, recorded = args
    import world
    import run_dc
    import run_dd
    import run_ds
    world.z8 = run_dc.dense_z8()
    spec = run_dd.CELLS[cell]
    a = run_ds.cells()[spec]
    cache = {}
    st = {"d0_epoch": None, "d0_size": 0, "lineage": set(), "d0": set(), "births": 0, "first_birth": None,
          "competent_nonD0_epochs": [], "last_competent_member": None, "checks": []}

    class De(run_ds.runner_cls(world)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            if st["d0_epoch"] is not None and causal and parent in st["lineage"]:
                st["lineage"].add(child)
                st["births"] += 1
                if st["first_birth"] is None:
                    st["first_birth"] = self.epoch
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

        def step(self):
            super().step()
            if self.epoch % EVERY:
                return
            alive = [o for o in self.orgs if o.alive]
            comp = [o for o in alive if competent(world, self, bytes(self._genome(o)), cache)]
            if st["d0_epoch"] is None:
                if comp:
                    st["d0_epoch"] = self.epoch
                    st["d0"] = {o.oid for o in comp}
                    st["lineage"] = set(st["d0"])
                    st["d0_size"] = len(comp)
                return
            live_l = [o for o in alive if o.oid in st["lineage"]]
            comp_l = [o for o in live_l if o in comp]
            if any(o.oid not in st["d0"] for o in comp_l):
                st["competent_nonD0_epochs"].append(self.epoch)
            if comp_l:
                st["last_competent_member"] = self.epoch
            st["checks"].append((self.epoch, len(live_l), len(comp_l), len(comp)))

    r = De(dict(a["cell"], atlas_axis="NONE"), seed, tier=a["tier"])
    out = r.run()
    depth = out["max_causal_replication_depth"]
    if st["d0_epoch"] is None:
        status = "NO_D0"                      # this screen never found the parent's donor
    elif depth >= 20:
        status = "ESTABLISHED"
    elif st["births"] == 0:
        status = "NO_COPY"
    elif not st["competent_nonD0_epochs"]:
        status = "INCOMPETENT_COPIES"
    else:
        status = "LOST_COMPETENT"
    rec = {"cell": cell, "seed": seed, "depth": depth, "recorded_depth": recorded, "status": status,
           "d0_epoch": st["d0_epoch"], "d0_size": st["d0_size"], "lineage_births": st["births"],
           "first_birth_epoch": st["first_birth"], "competent_nonD0_first": (st["competent_nonD0_epochs"] or [None])[0],
           "last_competent_member": st["last_competent_member"], "genomes_assayed": len(cache),
           "checks": st["checks"][:60]}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%s_%d.json" % (cell, seed))).write_text(json.dumps(rec))
    return rec


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(10, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if "%s_%d" % (t[0], t[1]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [(r["cell"], r["seed"]) for r in res if r["depth"] != r["recorded_depth"]]
    nod0 = [r for r in res if r["status"] == "NO_D0"]
    stalled = [r for r in res if r["status"] not in ("ESTABLISHED", "NO_D0")]
    cnt = collections.Counter(r["status"] for r in stalled)
    top = max(cnt.values()) / len(stalled) if stalled else 0.0
    cls = ("INVALID" if mism or len(res) != len(todo) or len(nod0) > 0.2 * len(res) else "SIGNAL" if top >= 0.7 else
           "CLEAN_NULL" if top < 0.4 else "WEAK_SIGNAL")
    est = [r for r in res if r["status"] == "ESTABLISHED"]
    summ = {"classification": cls, "replay_mismatches": mism, "n": len(res), "established": len(est), "no_d0": len(nod0),
            "stalled_modes": dict(cnt), "top_mode_share": round(top, 4),
            "established_first_birth_lag": sorted((r["first_birth_epoch"] - r["d0_epoch"]) for r in est if r["first_birth_epoch"] is not None),
            "stalled_first_birth_lag": sorted((r["first_birth_epoch"] - r["d0_epoch"]) for r in stalled if r["first_birth_epoch"] is not None),
            "d0_size": {"established": sorted(r["d0_size"] for r in est), "stalled": sorted(r["d0_size"] for r in stalled)},
            "d0_epoch": {"established": sorted(r["d0_epoch"] for r in est), "stalled": sorted(r["d0_epoch"] for r in stalled)}}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
