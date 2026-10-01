"""W2-35 s2: does ATOMIC write-back (the runner behind every anc0_share / L_share verdict) let a rotated 7ae3 frame
persist? Read-only replay of C-CORE runaway seeds (7ae3 cell, ATOMIC runner of X-DONOR-SWAP, untagged, as X-CERT-BREAK
replays them) for EMAX epochs. Counts halves entering a rotated frame (rot >= 16, s != 0) TRANSIENTLY (after the VM,
before the ATOMIC restore) and FINALLY (after restore), plus a 5-epoch alive census by (anc==0, frame class).
python -B s2_atomic.py EMAX SEED [SEED...] -> s2_atomic.json"""
import json, sys, types, collections, time
sys.dont_write_bytecode = True
from frames import world, ARM, IMP, frame, HERE, W2
sys.path.insert(0, str(W2.parent / "campaigns" / "c9x-explore-2026-09-24" / "x_donor_swap"))
import run_ds  # noqa: E402
from s1_scan import fclass  # noqa: E402


class Stop(Exception):
    pass


def run(seed, EMAX):
    cnt = collections.Counter()
    census = {}

    class Probe(world.Runner):
        def _pair_interact(self, i, a, b):
            pre = [(o.oid, fclass(frame(self._genome(o)))) for o in (a, b)]
            super()._pair_interact(i, a, b)
            for (oid, c0), o in zip(pre, (a, b)):
                c = fclass(frame(self._genome(o)))
                if c.startswith("ROT") and c != c0:
                    cnt["transient_enter_rot" + ("_promoted" if o.oid != oid else "")] += 1
    shim = types.SimpleNamespace(Runner=Probe, _mutated_orig=world._mutated_orig)

    class Final(run_ds.runner_cls(shim)):
        def _pair_interact(self, i, a, b):
            pre = [fclass(frame(self._genome(o))) for o in (a, b)]
            super()._pair_interact(i, a, b)
            for c0, o in zip(pre, (a, b)):
                c = fclass(frame(self._genome(o)))
                if c.startswith("ROT") and c != c0:
                    cnt["final_enter_rot"] += 1

        def step(self):
            out = super().step()
            if self.epoch % 5 == 0:
                c = collections.Counter()
                for o in self.orgs:
                    if o.alive:
                        c["%s|%s" % ("anc0" if o.anc == 0 else "other", fclass(frame(self._genome(o))))] += 1
                census[self.epoch] = dict(c)
            if self.epoch >= EMAX:
                raise Stop
            return out
    r = Final(dict(ARM["cell"], atlas_axis="NONE"), seed, tier=ARM["tier"], implant="ACTUAL_GENOME", implant_bytes=IMP)
    try:
        r.run()
    except Stop:
        pass
    return {"seed": seed, "epochs": r.epoch, "counts": dict(cnt), "census_last": census.get(max(census)) if census else None,
            "rot_alive_max": max((sum(v for k, v in c.items() if "ROT" in k) for c in census.values()), default=0)}


if __name__ == "__main__":
    t0 = time.process_time()
    E = int(sys.argv[1])
    res = [run(int(s), E) for s in sys.argv[2:]]
    for x in res:
        print(x, flush=True)
    (HERE / "s2_atomic.json").write_text(json.dumps({"runs": res, "cpu_s": round(time.process_time() - t0, 1)}, indent=1))
