"""trace one background oid's interactions (replay, read-only)."""
import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
C9 = HERE.parents[1] / "campaigns" / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
import world
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"
man = json.loads((C9 / "MANIFEST_FROZEN.json").read_text())
b = next(b for b in man["bundles"] if b["hypothesis_id"] == "H2" and b["specimen"] == SPEC)
arm = next(a for a in b["arms"] if a["arm"] == "B_reimplant_actual")
imp = bytes.fromhex(arm["kwargs"]["implant_hex"])
class Stop(Exception): pass
SEED, TGT, E = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
F = world._fidelity
class R(world.Runner):
    def _pair_interact(self, i, a, b):
        pre = [(o.oid, o.anc, self._genome(o)) for o in (a, b)]
        super()._pair_interact(i, a, b)
        for s, (oid, anc, g) in enumerate(pre):
            if oid == TGT:
                po = pre[1 - s]
                o = (a, b)[s]
                print("e%d side%d partner oid %d anc %d | fid(self,imp) %.2f->%.2f | fid(partner,imp) %.2f | new oid %d" %
                      (self.epoch, s, po[0], po[1], F(g, imp), F(self._genome(o), imp), F(po[2], imp), o.oid))
    def step(self):
        super().step()
        if self.epoch >= E: raise Stop
r = R(dict(arm["cell"], atlas_axis="NONE"), SEED, tier=arm["tier"], implant="ACTUAL_GENOME", implant_bytes=imp)
try: r.run()
except Stop: pass
